`timescale 1ns / 1ps

// SHIFTU はシフト演算を行う回路
// OP_CODE_HIGH (オペコード上位) からシフト種を決め
// DATA_TO_SHIFTU_A から入力される値を ～B 回シフトし、
// 結果を DATA_FROM_SHIFTU に出力すればよい
// フラグは3ビットバスでまとめて扱う

module SHIFTU(
        input [15:0] DATA_TO_SHIFTU_A,
        input [15:0] DATA_TO_SHIFTU_B,
        output reg [15:0] DATA_FROM_SHIFTU,
        output [2:0] FLAG_FROM_SHIFTU,    // REGU へのフラグ値
        input [7:0] OP_CODE_HIGH,          // CNTU からの制御信号
        input CLK
    );
    
    reg OF;
    wire ZF;
    wire SF;
    
    wire [16:0] SLL_W0, SLL_W1, SLL_W2, SLL_W3, SLL_W4, SLL_W5;
    wire [16:0] SRL_W0, SRL_W1, SRL_W2, SRL_W3, SRL_W4, SRL_W5;
    wire [16:0] SRA_W0, SRA_W1, SRA_W2, SRA_W3, SRA_W4, SRA_W5;
    
    // バレルシフタの計算時間は長く、ALU と同様に作ると計算が間に合わない
    // そこで、入力線 DATA_TO_SHIFTU_A と信号線 SHIFT_COUNT にフリップフロップを挿入し
    // SHIFTU を経由するパスの長さを2分割することで
    // フリップフロップ間の計算時間を 8 ns 以下に抑える

    reg [15:0] DATA_TO_SHIFTU_A_REG;
    reg [4:0] SHIFT_COUNT;
    
    always @(posedge CLK) begin
        DATA_TO_SHIFTU_A_REG <= DATA_TO_SHIFTU_A;
    end
    
    always @(posedge CLK) begin
        SHIFT_COUNT <= (DATA_TO_SHIFTU_B[15:5] != 0) ? 5'b11111 : DATA_TO_SHIFTU_B; 
            // 17 を越えるシフト回数は意味がないので、シフト回数を減らす
    end
    
    // SLA, SRA, SLL, SRL 各命令毎にバレルシフタを作る
    
    assign SLL_W0 = {1'd0, DATA_TO_SHIFTU_A_REG[15:0]};
        // SLL_W? の最上位ビットは OF 用、残る 16ビットがシフト結果
    assign SLL_W1 = SHIFT_COUNT[0] ? {SLL_W0[15:0], 1'd0} : SLL_W0;
        // SHIFT_COUNT の最下位ビットが 1 なら 1 ビット左シフト
    assign SLL_W2 = SHIFT_COUNT[1] ? {SLL_W1[14:0], 2'd0} : SLL_W1;
        // SHIFT_COUNT の下から1ビット目が 1 なら 2 ビット左シフト
    assign SLL_W3 = SHIFT_COUNT[2] ? {SLL_W2[12:0], 4'd0} : SLL_W2;
        // SHIFT_COUNT の下から2ビット目が 1 なら 4 ビット左シフト
    assign SLL_W4 = SHIFT_COUNT[3] ? {SLL_W3[8:0],  8'd0} : SLL_W3;
        // SHIFT_COUNT の下から3ビット目が 1 なら 8 ビット左シフト
    assign SLL_W5 = SHIFT_COUNT[4] ? {SLL_W4[0],   16'd0} : SLL_W4;
        // SHIFT_COUNT の下から4ビット目が 1 なら16 ビット左シフト
    
    assign SRL_W0 = {DATA_TO_SHIFTU_A_REG[15:0], 1'd0};
        // SRL_W? の最下位ビットは OF 用、残る 16ビットがシフト結果
        // 後は左シフトと同じようにバレルシフト
    assign SRL_W1 = SHIFT_COUNT[0] ? {1'd0, SRL_W0[16:1]} : SRL_W0;
    assign SRL_W2 = SHIFT_COUNT[1] ? {2'd0, SRL_W1[16:2]} : SRL_W1;
    assign SRL_W3 = SHIFT_COUNT[2] ? {4'd0, SRL_W2[16:4]} : SRL_W2;
    assign SRL_W4 = SHIFT_COUNT[3] ? {8'd0, SRL_W3[16:8]} : SRL_W3;
    assign SRL_W5 = SHIFT_COUNT[4] ? {16'd0, SRL_W4[16]}  : SRL_W4;
    
    assign SRA_W0 = {DATA_TO_SHIFTU_A_REG[15:0], 1'b0};
    assign SRA_W1 = SHIFT_COUNT[0] ? {SRA_W0[16],       SRA_W0[16:1]} : SRA_W0;
    assign SRA_W2 = SHIFT_COUNT[1] ? {{2{SRA_W1[16]}},  SRA_W1[16:2]} : SRA_W1;
    assign SRA_W3 = SHIFT_COUNT[2] ? {{4{SRA_W2[16]}},  SRA_W2[16:4]} : SRA_W2;
    assign SRA_W4 = SHIFT_COUNT[3] ? {{8{SRA_W3[16]}},  SRA_W3[16:8]} : SRA_W3;
    assign SRA_W5 = SHIFT_COUNT[4] ? {{16{SRA_W4[16]}}, SRA_W4[16]}   : SRA_W4;
        // 算術右シフトでは、シフト後の余白を 0 でなく、符号ビットで埋める
    
    always @(*) begin
        case(OP_CODE_HIGH)
            8'h52: begin {OF, DATA_FROM_SHIFTU} <= SLL_W5; end    // SLL 命令
            8'h53: begin {DATA_FROM_SHIFTU, OF} <= SRL_W5; end    // SRL 命令
            8'h51: begin {DATA_FROM_SHIFTU, OF} <= SRA_W5; end    // SRA 命令
            8'h50: begin    // SLA 命令
                    OF <= SLL_W5[15];
                    DATA_FROM_SHIFTU <= {DATA_TO_SHIFTU_A_REG[15], SLL_W5[14:0]};
                    // SLL 用のバレルシフタを再利用
                end
            default: begin
                    OF <= 1'bx;
                    DATA_FROM_SHIFTU <= 16'bx;
                end
        endcase
    end
    assign ZF = (DATA_FROM_SHIFTU == 0);    // 演算結果が 0 ならゼロフラグをオン
    assign SF = DATA_FROM_SHIFTU[15];    // 演算結果の MSB が 1 ならサインフラグをオン
    
    assign FLAG_FROM_SHIFTU = {OF, SF, ZF};
endmodule
