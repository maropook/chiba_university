`timescale 1ns / 1ps

// ALU は算術演算、ビット論理演算を行う組み合わせ回路
// フラグを変化させるため、LD命令でも ALU を通す
// OP_CODE_HIGH (オペコード上位) から演算種を決め
// DATA_TO_ALU_A, B から入力される値から演算し、演算結果を DATA_FROM_ALU に常時出力している

module ALU(
        input [15:0] DATA_TO_ALU_A,
        input [15:0] DATA_TO_ALU_B,
        output reg [15:0] DATA_FROM_ALU,
        output [2:0] FLAG_FROM_ALU,    // REGU へのフラグ値
        input [7:0] OP_CODE_HIGH       // CNTU からの制御信号
    );
    
    wire [15:0] ADDER_INB;
    wire [15:0] ADDER_OUT;
    reg IS_SUBTRACT;
    wire CARRY_14;
    wire CARRY_MSB;
    wire OVERFLOW_SIGNED;
    reg OF;
    reg SF;
    wire ZF;
    
    // 減算を行うときは IS_SUBTRACT = 1 加算なら 0
    always @(*) begin    
        casex(OP_CODE_HIGH)    // 条件に x を書きたいときは case ではなく casex
            8'b0010xxx0: IS_SUBTRACT <= 1'b0;    // ADD?命令
            8'b0010xxx1: IS_SUBTRACT <= 1'b1;    // SUB?命令
            8'b0100xxxx: IS_SUBTRACT <= 1'b1;    // CP?命令
            default: IS_SUBTRACT <= 1'bx;    // 0 でも 1 でもよければ不定値 x
                // case文には必ず default を書く
                // 書かないと不要なラッチが生成されることがある
        endcase
    end
    
    // ここから加減算器 A +/- B の結果を ADDER_OUT に出力
    // MSBでのキャリーを CARRY_MSB、1桁下を CARRY_14 に出力
    assign ADDER_INB = IS_SUBTRACT ? ~DATA_TO_ALU_B : DATA_TO_ALU_B;
    assign {CARRY_14, ADDER_OUT[14:0]} = DATA_TO_ALU_A[14:0] + ADDER_INB[14:0] + IS_SUBTRACT;
    assign {CARRY_MSB, ADDER_OUT[15]} = DATA_TO_ALU_A[15] + ADDER_INB[15] + CARRY_14;
    assign OVERFLOW_SIGNED = CARRY_MSB ^ CARRY_14; 
            // 符号あり加減算でオーバーフローが起きたとき OVERFLOW_SIGNED = 1
    // ここまで加減算器
    
    always @(*) begin
        casex(OP_CODE_HIGH)
            8'b0001xxxx: DATA_FROM_ALU <= DATA_TO_ALU_B;    // LD命令 (ST, LAD は ALU を使わない)
            8'b0010xxxx: DATA_FROM_ALU <= ADDER_OUT;        // 加減算命令
            8'b0011xx00: DATA_FROM_ALU <= DATA_TO_ALU_A & DATA_TO_ALU_B;    // AND 命令
            8'b0011xx01: DATA_FROM_ALU <= DATA_TO_ALU_A | DATA_TO_ALU_B;    // OR 命令
            8'b0011xx10: DATA_FROM_ALU <= DATA_TO_ALU_A ^ DATA_TO_ALU_B;    // XOR 命令
            8'b0100xxxx: DATA_FROM_ALU <= ADDER_OUT;        // 比較命令
            default: DATA_FROM_ALU <= 16'bx;
        endcase
    end
    
    assign ZF = (DATA_FROM_ALU == 0);    // 演算結果が 0 ならゼロフラグをオン
    
    always @(*) begin
        casex(OP_CODE_HIGH)
            8'b0001xxxx: SF <= DATA_FROM_ALU[15]; // LD命令
            8'b0010xxxx: SF <= DATA_FROM_ALU[15]; // ADD?, SUB? 命令
            8'b0011xxxx: SF <= DATA_FROM_ALU[15]; // AND / OR / XOR
            8'b0100xxx0: SF <= DATA_FROM_ALU[15] ^ OVERFLOW_SIGNED; // CPA 命令
            8'b0100xxx1: SF <= ~CARRY_MSB;        // CPL 命令
            default: SF <= 1'bx;
        endcase
    end
    
    always @(*) begin
        casex(OP_CODE_HIGH)
            8'b0001xxxx: OF <= 1'b0;              // LD命令
            8'b0010xx00: OF <= OVERFLOW_SIGNED;   // ADDA 命令
            8'b0010xx01: OF <= OVERFLOW_SIGNED;   // SUBA 命令
            8'b0010xx10: OF <= CARRY_MSB;         // ADDL 命令
            8'b0010xx11: OF <= ~CARRY_MSB;        // SUBL 命令
            8'b0011xxxx: OF <= 1'b0;              // AND / OR / XOR
            8'b0100xxxx: OF <= 1'b0;              // CP? 命令
            default: OF <= 1'bx;
        endcase
    end
    
    assign FLAG_FROM_ALU = {OF, SF, ZF};
endmodule
