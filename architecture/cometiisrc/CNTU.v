`timescale 1ns / 1ps

// CNTU は CPU の制御部

module CNTU(
        input [15:0] DATA_TO_CNTU_A,
        input [15:0] DATA_TO_CNTU_B,
        output reg [15:0] DATA_FROM_CNTU_B,
        output reg [15:0] DATA_FROM_CNTU_C,
        output [7:0] OP_CODE_HIGH,    // ALU, SHIFTU への制御信号
        input [2:0] FLAG_FROM_REGU,   // REGU から フラグ値、分岐命令に使う
        output reg WRITE_ENABLE_GR,   // REGU への制御信号
        output reg WRITE_ENABLE_FLAG,
        output [2:0] SELECT_GR_IN,
        output [2:0] SELECT_GR_OUTA,
        output [2:0] SELECT_GR_OUTB,
        output reg SELECT_FROM_CNTU_B, // BUSU への制御信号
        output reg SELECT_FROM_CNTU_C,
        output reg SELECT_FROM_ALU,
        output reg SELECT_FROM_SHIFTU,
        output [15:0] ADDR_TO_MEMORY,  // メモリから/への各種信号
        input [15:0] DATA_FROM_MEMORY,
        output [15:0] DATA_TO_MEMORY,
        output reg REQUEST_WRITE_TO_MEMORY,
        input START,    // 外部装置からの制御信号
        output BUSY,    // 外部装置への制御信号
        output DONE,
        input CLK
    );
    
    // parameter は C言語で言うところの define 文
    // 状態 STATE の値を定義する
    parameter STATE_READY            = 8'h00; // 実行開始前の状態
    // フェッチサイクル
    parameter STATE_FETCH_1ST        = 8'h01; // (MAR <= PR++)、メモリ読み出し要求
    parameter STATE_FETCH_2ND        = 8'h02; // メモリ応答待ち
    parameter STATE_FETCH_3RD        = 8'h03; // MDR <= メモリ
    parameter STATE_FETCH_4TH        = 8'h04; // IR <= MDR、
    // 実行サイクル
    parameter STATE_DECODING         = 8'h08; // IRを見ながらデコーダ1でデコード
    parameter STATE_LOAD_OPERAND_1ST = 8'h0c; // 第2オペランドの読み出し (MAR <= PR++)、メモリ読み出し要求
    parameter STATE_LOAD_OPERAND_2ND = 8'h0d; // 第2オペランドの読み出し メモリ応答待ち
    parameter STATE_LOAD_OPERAND_3RD = 8'h0e; // 第2オペランドの読み出し MDR <= メモリ、デコーダ2でデコード
    
    parameter STATE_STORE_1ST        = 8'h10; // ST命令 MAR <= MDR + GR、MDR <= GR、メモリ書き込み要求
    parameter STATE_STORE_2ND        = 8'h11; // ST命令 メモリ処理待ち
    parameter STATE_LOAD_ADDRESS_1ST = 8'h18; // LAD命令 MAR <= MDR + GR
    parameter STATE_LOAD_ADDRESS_2ND = 8'h19; // LAD命令 GR <= MAR
    parameter STATE_CALC_REG         = 8'h28; // LD命令、演算命令 GR <= ALU ( GR, GR )
    parameter STATE_CALC_MEM_1ST     = 8'h20; // LD命令、演算命令 MAR <= MDR + GR、メモリ読み出し要求
    parameter STATE_CALC_MEM_2ND     = 8'h21; // LD命令、メモリ応答待ち
    parameter STATE_CALC_MEM_3RD     = 8'h22; // LD命令、演算命令 MDR <= メモリ
    parameter STATE_CALC_MEM_4TH     = 8'h23; // LD命令、演算命令 GR <= ALU ( GR, MDR )
    parameter STATE_SHIFT_1ST        = 8'h50; // シフト命令 MAR <= MDR + GR
    parameter STATE_SHIFT_2ND        = 8'h51; // シフト命令 SHIFTU <= ( GR, MAR )
    parameter STATE_SHIFT_3RD        = 8'h52; // シフト命令 GR <= SHIFTU
    parameter STATE_JUMP_1ST         = 8'h60; // 分岐命令 MAR <= MDR + GR フラグが条件を満たさないとこの状態まで来ない
    parameter STATE_JUMP_2ND         = 8'h61; // 分岐命令 PR <= MAR
    parameter STATE_PUSH_1ST         = 8'h70; // PUSH命令 MAR <= MDR + GR 
    parameter STATE_PUSH_2ND         = 8'h71; // PUSH命令 MDR <= MAR、MAR <= --SP、メモリ書き込み要求
    parameter STATE_PUSH_3RD         = 8'h72; // メモリ処理待ち
    parameter STATE_POP_1ST          = 8'h78; // POP命令、MAR <= SP++、メモリ読み出し供給
    parameter STATE_POP_2ND          = 8'h79; // メモリ応答待ち
    parameter STATE_POP_3RD          = 8'h7a; // POP命令、MDR <= メモリ
    parameter STATE_POP_4TH          = 8'h7b; // POP命令、GR <= MDR
    
    parameter STATE_CALL_1ST         = 8'h80; // CALL命令 MAR <= MDR + GR, MDR <= PR
    parameter STATE_CALL_2ND         = 8'h81; // CALL命令 PR <= MAR, MAR <= --SP、メモリ書き込み要求
    parameter STATE_CALL_3RD         = 8'h82; // メモリ処理待ち
    parameter STATE_RET_1ST          = 8'h88; // RET命令 MAR <= SP++、メモリ読み出し供給
    parameter STATE_RET_2ND          = 8'h89; // RET命令 メモリ応答待ち
    parameter STATE_RET_3RD          = 8'h8a; // RET命令 MDR <= メモリ
    parameter STATE_RET_4TH          = 8'h8b; // RET命令 PC <= MDR
    parameter STATE_HALT             = 8'hff; // 実行終了後の状態
    
    // 順序回路は有限オートマトン、状態を STATE に記憶
    reg [7:0] STATE = STATE_READY;
    reg [7:0] DECODER1_OUT;    // デコーダ1の出力用
    reg [7:0] DECODER2_OUT;    // デコーダ2の出力用
    reg SATISFY_JUMP_CONDITION;  // 分岐条件判定
    wire SATISFY_HALT_CONDITION; // プログラム終了
    
    // 各種専用レジスタ
    reg [15:0] PR = 0;
    reg [15:0] SP = 16'hffff;
    reg [15:0] MAR = 0;
    reg [15:0] MDR;
    reg [15:0] IR = 0;
    
    wire [15:0] EFFECTIVE_ADDRESS; // 実効アドレス演算用
    
    // デコーダ1、出力 DECODER1_OUT は次状態
    // 2ワード命令は第2オペランドを読み出すための共通の状態に移る
    // 第2オペランド読み出し後に、デコーダ2で再度デコードを行う
    // LD命令, 加減算命令, 論理演算命令は ALU での演算が違うだけで制御は同じ
    // LD命令実行時は INB = ALU( INA, INB ) のような計算を行う
    
    always @(*) begin
        casex(IR[15:8])
            8'b00000000: DECODER1_OUT <= STATE_FETCH_1ST;        // NOP
            8'b0001x0xx: DECODER1_OUT <= STATE_LOAD_OPERAND_1ST; // LD/ST/LAD GR,adr,GR
            8'b0001x1xx: DECODER1_OUT <= STATE_CALC_REG;         // LD GR,GR
            8'b001xx0xx: DECODER1_OUT <= STATE_LOAD_OPERAND_1ST; // 演算 GR,adr,GR
            8'b001xx1xx: DECODER1_OUT <= STATE_CALC_REG;         // 演算 GR,GR
            8'b0100x0xx: DECODER1_OUT <= STATE_LOAD_OPERAND_1ST; // 比較 GR,adr,GR
            8'b0100x1xx: DECODER1_OUT <= STATE_CALC_REG;         // 比較 GR,adr,GR
            8'b0101xxxx: DECODER1_OUT <= STATE_LOAD_OPERAND_1ST; // シフト GR,adr,GR
            8'b0110xxxx: DECODER1_OUT <= STATE_LOAD_OPERAND_1ST; // 分岐 adr,GR
            8'b0111xxx0: DECODER1_OUT <= STATE_LOAD_OPERAND_1ST; // PUSH adr,GR
            8'b0111xxx1: DECODER1_OUT <= STATE_POP_1ST;          // POP GR
            8'b1000xxx0: DECODER1_OUT <= STATE_LOAD_OPERAND_1ST; // CALL adr,GR
            8'b1000xxx1: DECODER1_OUT <= SATISFY_HALT_CONDITION ? STATE_HALT : STATE_RET_1ST;
                                                                 // RET
            default:     DECODER1_OUT <= 8'bx;
        endcase
    end
    assign SATISFY_HALT_CONDITION = (SP == 16'hffff);
        // スタックが空の状態で RET すると HALT
    
    // デコーダ2
    always @(*) begin
        casex(IR[15:8])
            8'b00010000: DECODER2_OUT <= STATE_CALC_MEM_1ST;     // LD GR,adr,GR
            8'b00010001: DECODER2_OUT <= STATE_STORE_1ST;        // ST GR,adr,GR
            8'b00010010: DECODER2_OUT <= STATE_LOAD_ADDRESS_1ST; // LAD GR,adr,GR
            8'b001xxxxx: DECODER2_OUT <= STATE_CALC_MEM_1ST;     // 演算 GR,adr,GR
            8'b0100xxxx: DECODER2_OUT <= STATE_CALC_MEM_1ST;     // 比較 GR,adr,GR
            8'b0101xxxx: DECODER2_OUT <= STATE_SHIFT_1ST;        // シフト GR,adr,GR
            8'b0110xxxx: DECODER2_OUT <= SATISFY_JUMP_CONDITION ? STATE_JUMP_1ST : STATE_FETCH_1ST;
                                                                 // 分岐 adr,GR
            8'b0111xxxx: DECODER2_OUT <= STATE_PUSH_1ST;         // PUSH adr,GR
            8'b1000xxxx: DECODER2_OUT <= STATE_CALL_1ST;         // CALL adr,GR
            default:     DECODER2_OUT <= 8'bx;
        endcase
    end
    
    // 分岐条件、SATISFY_JUMP_CONDITION=1 ならジャンプ
    always @(*) begin    
        casex ({IR[11:8], FLAG_FROM_REGU})    // case 文、数値中の '_' は無視される
                // フラグは MSB 側から順に OF, SF, ZF
            7'b0001_x1x: SATISFY_JUMP_CONDITION <= 1;    // JMI, SF=1
            7'b0010_xx0: SATISFY_JUMP_CONDITION <= 1;    // JNZ, ZF=0
            7'b0011_xx1: SATISFY_JUMP_CONDITION <= 1;    // JZE, ZF=1
            7'b0100_xxx: SATISFY_JUMP_CONDITION <= 1;    // JUMP
            7'b0101_x00: SATISFY_JUMP_CONDITION <= 1;    // JPL, SF=0 && ZF=0
            7'b0110_1xx: SATISFY_JUMP_CONDITION <= 1;    // JOV, SF=0 && ZF=0
            default: SATISFY_JUMP_CONDITION <= 0;
        endcase
    end
    
    // 次の状態を決める状態遷移関数(と状態を記憶するFF部)
    // IP のメモリはレイテンシが 常に1クロックと決まっているので
    // メモリ応答待ち、処理待ちでも 1クロック待つ
    
    always @(posedge CLK) begin
        case(STATE)
            STATE_READY:            STATE <= START ? STATE_FETCH_1ST : STATE_READY;
            STATE_FETCH_1ST:        STATE <= STATE_FETCH_2ND;
            STATE_FETCH_2ND:        STATE <= STATE_FETCH_3RD;
            STATE_FETCH_3RD:        STATE <= STATE_FETCH_4TH;
            STATE_FETCH_4TH:        STATE <= STATE_DECODING;
            STATE_DECODING:         STATE <= DECODER1_OUT;
            STATE_LOAD_OPERAND_1ST: STATE <= STATE_LOAD_OPERAND_2ND;
            STATE_LOAD_OPERAND_2ND: STATE <= STATE_LOAD_OPERAND_3RD;
            STATE_LOAD_OPERAND_3RD: STATE <= DECODER2_OUT;
            STATE_STORE_1ST:        STATE <= STATE_STORE_2ND;
            STATE_STORE_2ND:        STATE <= STATE_FETCH_1ST;
            STATE_LOAD_ADDRESS_1ST: STATE <= STATE_LOAD_ADDRESS_2ND;
            STATE_LOAD_ADDRESS_2ND: STATE <= STATE_FETCH_1ST;
            STATE_CALC_REG:         STATE <= STATE_FETCH_1ST;
            STATE_CALC_MEM_1ST:     STATE <= STATE_CALC_MEM_2ND;
            STATE_CALC_MEM_2ND:     STATE <= STATE_CALC_MEM_3RD;
            STATE_CALC_MEM_3RD:     STATE <= STATE_CALC_MEM_4TH;
            STATE_CALC_MEM_4TH:     STATE <= STATE_FETCH_1ST;
            STATE_SHIFT_1ST:        STATE <= STATE_SHIFT_2ND;
            STATE_SHIFT_2ND:        STATE <= STATE_SHIFT_3RD;
            STATE_SHIFT_3RD:        STATE <= STATE_FETCH_1ST;
            STATE_JUMP_1ST:         STATE <= STATE_JUMP_2ND;
            STATE_JUMP_2ND:         STATE <= STATE_FETCH_1ST;
            STATE_PUSH_1ST:         STATE <= STATE_PUSH_2ND;
            STATE_PUSH_2ND:         STATE <= STATE_PUSH_3RD;
            STATE_PUSH_3RD:         STATE <= STATE_FETCH_1ST;
            STATE_POP_1ST:          STATE <= STATE_POP_2ND;
            STATE_POP_2ND:          STATE <= STATE_POP_3RD;
            STATE_POP_3RD:          STATE <= STATE_POP_4TH;
            STATE_POP_4TH:          STATE <= STATE_FETCH_1ST;
            STATE_CALL_1ST:         STATE <= STATE_CALL_2ND;
            STATE_CALL_2ND:         STATE <= STATE_CALL_3RD;
            STATE_CALL_3RD:         STATE <= STATE_FETCH_1ST;
            STATE_RET_1ST:          STATE <= STATE_RET_2ND;
            STATE_RET_2ND:          STATE <= STATE_RET_3RD;
            STATE_RET_3RD:          STATE <= STATE_RET_4TH;
            STATE_RET_4TH:          STATE <= STATE_FETCH_1ST;
            default:                STATE <= STATE_HALT;
        endcase
    end
    
    assign DONE = (STATE == STATE_HALT);
    assign BUSY = ~((STATE == STATE_READY) | DONE);
    
    // 現在の状態によって専用レジスタ値を更新する
    
    always @(posedge CLK) begin
        case(STATE)
            STATE_FETCH_1ST:        PR <= PR+1;
            STATE_LOAD_OPERAND_1ST: PR <= PR+1;
            STATE_JUMP_2ND:         PR <= MAR;
            STATE_CALL_2ND:         PR <= MAR;
            STATE_RET_4TH:          PR <= MDR;
            default:                PR <= PR;
        endcase
    end
    
    always @(posedge CLK) begin
        case(STATE)
            STATE_PUSH_2ND:         SP <= SP-1;
            STATE_POP_1ST:          SP <= SP+1;
            STATE_CALL_2ND:         SP <= SP-1;
            STATE_RET_1ST:          SP <= SP+1;
            default:                SP <= SP;
        endcase
    end
    
    always @(posedge CLK) begin
        case(STATE)
            STATE_FETCH_4TH:        IR <= MDR;
            default:                IR <= IR;
        endcase
    end
    
    // メモリ関連 (MAR, MDR, メモリへの制御信号)
    
    // 実効アドレスを求めるための加算器 LD, r,addr,x の addr + x
    // INB には 汎用レジスタ x の値が来ている
    // GR0 が選択されているときは x は GR0 の値ではなく値 0
    
    assign EFFECTIVE_ADDRESS = MDR + ((SELECT_GR_OUTB == 0) ? 0 : DATA_TO_CNTU_B);
    always @(posedge CLK) begin
        case(STATE)
            STATE_FETCH_1ST:        MAR <= PR;
            STATE_LOAD_OPERAND_1ST: MAR <= PR;
            STATE_STORE_1ST:        MAR <= EFFECTIVE_ADDRESS;
            STATE_LOAD_ADDRESS_1ST: MAR <= EFFECTIVE_ADDRESS;
            STATE_CALC_MEM_1ST:     MAR <= EFFECTIVE_ADDRESS;
            STATE_SHIFT_1ST:        MAR <= EFFECTIVE_ADDRESS;
            STATE_JUMP_1ST:         MAR <= EFFECTIVE_ADDRESS;
            STATE_PUSH_1ST:         MAR <= EFFECTIVE_ADDRESS;
            STATE_PUSH_2ND:         MAR <= SP-1;
            STATE_POP_1ST:          MAR <= SP;
            STATE_CALL_1ST:         MAR <= EFFECTIVE_ADDRESS;
            STATE_CALL_2ND:         MAR <= SP-1;
            STATE_RET_1ST:          MAR <= SP;
            default:                MAR <= MAR;
        endcase
    end
    assign ADDR_TO_MEMORY = MAR;
    
    always @(posedge CLK) begin
        case(STATE)
            STATE_FETCH_3RD:        MDR <= DATA_FROM_MEMORY;
            STATE_LOAD_OPERAND_3RD: MDR <= DATA_FROM_MEMORY;
            STATE_STORE_1ST:        MDR <= DATA_TO_CNTU_A; // 汎用レジスタ値
            STATE_CALC_MEM_3RD:     MDR <= DATA_FROM_MEMORY;
            STATE_PUSH_2ND:         MDR <= MAR;
            STATE_POP_3RD:          MDR <= DATA_FROM_MEMORY;
            STATE_CALL_1ST:         MDR <= PR;
            STATE_RET_3RD:          MDR <= DATA_FROM_MEMORY;
            default:                MDR <= MDR;
        endcase
    end
    assign DATA_TO_MEMORY = MDR;
    
    // メモリへの書き込み要求
    always @(posedge CLK) begin
        case(STATE)
            STATE_STORE_1ST:        REQUEST_WRITE_TO_MEMORY <= 1;
            STATE_PUSH_2ND:         REQUEST_WRITE_TO_MEMORY <= 1;
            STATE_CALL_2ND:         REQUEST_WRITE_TO_MEMORY <= 1;
            default:                REQUEST_WRITE_TO_MEMORY <= 0;
        endcase
    end
    
    // メモリへの読み出し請求は行わない
    // IP のメモリはわざわざ要求しなくても、常時値を出力し続けてくれる
    
    // 制御部として各部品に指示(イネーブル信号)を出していく
    // 制御信号ではクロック同期を取らないので、ここでは組み合わせ回路を作る
    // タイミング関連は熟練者でもよく間違えるので、落ち着いて考えよう
    
    // REGU (汎用レジスタ) への制御
    // 汎用レジスタ GR 更新指示
    
    // IR の上位4桁 が 4 のときは比較命令であり、
    // GR への書き出しを指示しない
    
    always @(*) begin
        case(STATE)
            STATE_LOAD_ADDRESS_2ND: WRITE_ENABLE_GR <= 1;
            STATE_CALC_REG:         WRITE_ENABLE_GR <= (IR[15:12] != 4'b0100);
            STATE_CALC_MEM_4TH:     WRITE_ENABLE_GR <= (IR[15:12] != 4'b0100);
            STATE_SHIFT_3RD:        WRITE_ENABLE_GR <= 1;
            STATE_POP_4TH:          WRITE_ENABLE_GR <= 1;
            default:                WRITE_ENABLE_GR <= 0;
        endcase
    end
    
    // フラグレジスタ更新指示
    always @(*) begin
        case(STATE)
            STATE_CALC_REG:         WRITE_ENABLE_FLAG <= 1;
            STATE_CALC_MEM_4TH:     WRITE_ENABLE_FLAG <= 1;
            STATE_SHIFT_3RD:        WRITE_ENABLE_FLAG <= 1;
            default:                WRITE_ENABLE_FLAG <= 0;
        endcase
    end
    
    // LD 命令、演算命令、比較命令では MDR の値を
    // シフト命令では MAR の値を ALU, SHIFTU に入力させる必要があり、
    // これらの値を DATA_FROM_CNTU_B に出力する
    
    always @(*) begin
        case(STATE)
            STATE_SHIFT_2ND:        DATA_FROM_CNTU_B <= MAR;
            STATE_CALC_MEM_4TH:     DATA_FROM_CNTU_B <= MDR;
            default:                DATA_FROM_CNTU_B <= 16'bx;
        endcase
    end
    
    // BUSU には DATA_FROM_CNTU_B の値を使うよう指示する
    
    always @(*) begin
        case(STATE)
            STATE_SHIFT_2ND:        SELECT_FROM_CNTU_B <= 1;
            STATE_CALC_MEM_4TH:     SELECT_FROM_CNTU_B <= 1;
            default:                SELECT_FROM_CNTU_B <= 0;
        endcase
    end
    
    // LAD 命令、POP 命令では MAR, MDR の値を REGU に入力させる必要があり、
    // これらの値を DATA_FROM_CNTU_C に出力する
    
    always @(*) begin
        case(STATE)
            STATE_LOAD_ADDRESS_2ND: DATA_FROM_CNTU_C <= MAR;
            STATE_POP_4TH:          DATA_FROM_CNTU_C <= MDR;
            default:                DATA_FROM_CNTU_C <= 16'bx;
        endcase
    end
    
    always @(*) begin
        case(STATE)
            STATE_LOAD_ADDRESS_2ND: SELECT_FROM_CNTU_C <= 1;
            STATE_POP_4TH:          SELECT_FROM_CNTU_C <= 1;
            default:                SELECT_FROM_CNTU_C <= 0;
        endcase
    end
    
    // ALU, SHIFTU どちらの出力を使うか選択する
    
    always @(*) begin
        case(STATE)
            STATE_CALC_REG:         SELECT_FROM_ALU <= 1;
            STATE_CALC_MEM_4TH:     SELECT_FROM_ALU <= 1;
            default:                SELECT_FROM_ALU <= 0;
        endcase
    end
    
    always @(*) begin
        case(STATE)
            STATE_SHIFT_3RD:        SELECT_FROM_SHIFTU <= 1;
            default:                SELECT_FROM_SHIFTU <= 0;
        endcase
    end
    
    // REGU への指示、汎用レジスタ GR0～7 の選択
    // ニモニック表の r/r1, r/r2 列が IR[6:4], IR[2:0] に相当する
    
    assign SELECT_GR_IN = IR[6:4];
    assign SELECT_GR_OUTA = IR[6:4];
    assign SELECT_GR_OUTB = IR[2:0];
    
    // ALU, SHIFTU への指示、行う演算の選択
    // IR に入っているオペコードの上位8ビットをそのまま送る
    
    assign OP_CODE_HIGH = IR[15:8];
    
    // 手続きブロック (always 文) は
    // 更新する (代入文の左辺にくる) reg型変数毎に作っていくのがセオリー
endmodule
