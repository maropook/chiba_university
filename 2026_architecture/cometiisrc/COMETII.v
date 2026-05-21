`timescale 1ns / 1ps

// COMET II 本体
// 制御ユニット CNTU と演算ユニット ALU, SHIFTU を持つ

module COMETII(
        input START,
        output BUSY,
        output DONE,
        output [15:0] ADDR_TO_MEMORY,
        input [15:0] DATA_FROM_MEMORY,
        output [15:0] DATA_TO_MEMORY,
        output REQUEST_WRITE_TO_MEMORY,
        input CLK
    );
    
    wire [15:0] DATA_TO_CNTU_A;
    wire [15:0] DATA_TO_CNTU_B;
    wire [15:0] DATA_FROM_CNTU_B;
    wire [15:0] DATA_FROM_CNTU_C;
    wire SELECT_FROM_CNTU_B;
    wire SELECT_FROM_CNTU_C;
    wire SELECT_FROM_ALU;
    wire SELECT_FROM_SHIFTU;
    
    reg [15:0] DATA_TO_REGU;
    wire [15:0] DATA_FROM_REGU_A;
    wire [15:0] DATA_FROM_REGU_B;
    wire WRITE_ENABLE_GR;
    wire [2:0] SELECT_GR_IN;
    wire [2:0] SELECT_GR_OUTA;
    wire [2:0] SELECT_GR_OUTB;
    reg [2:0] FLAG_TO_REGU;
    wire [2:0] FLAG_FROM_REGU;
    wire WRITE_ENABLE_FLAG;
    
    wire [15:0] DATA_TO_ALU_A;
    wire [15:0] DATA_TO_ALU_B;
    wire [15:0] DATA_FROM_ALU;
    wire [2:0] FLAG_FROM_ALU;
    wire [7:0] OP_CODE_HIGH;
    
    wire [15:0] DATA_TO_SHIFTU_A;
    wire [15:0] DATA_TO_SHIFTU_B;
    wire [15:0] DATA_FROM_SHIFTU;
    wire [2:0] FLAG_FROM_SHIFTU;
    
    CNTU CNTU_0 (
        .DATA_TO_CNTU_A(DATA_TO_CNTU_A),
        .DATA_TO_CNTU_B(DATA_TO_CNTU_B),
        .DATA_FROM_CNTU_B(DATA_FROM_CNTU_B),
        .DATA_FROM_CNTU_C(DATA_FROM_CNTU_C),
        .OP_CODE_HIGH(OP_CODE_HIGH),
        .FLAG_FROM_REGU(FLAG_FROM_REGU),
        .WRITE_ENABLE_GR(WRITE_ENABLE_GR),
        .WRITE_ENABLE_FLAG(WRITE_ENABLE_FLAG),
        .SELECT_GR_IN(SELECT_GR_IN),
        .SELECT_GR_OUTA(SELECT_GR_OUTA),
        .SELECT_GR_OUTB(SELECT_GR_OUTB),
        .SELECT_FROM_CNTU_B(SELECT_FROM_CNTU_B),
        .SELECT_FROM_CNTU_C(SELECT_FROM_CNTU_C),
        .SELECT_FROM_ALU(SELECT_FROM_ALU),
        .SELECT_FROM_SHIFTU(SELECT_FROM_SHIFTU),
        .ADDR_TO_MEMORY(ADDR_TO_MEMORY),
        .DATA_FROM_MEMORY(DATA_FROM_MEMORY),
        .DATA_TO_MEMORY(DATA_TO_MEMORY),
        .REQUEST_WRITE_TO_MEMORY(REQUEST_WRITE_TO_MEMORY),
        .START(START),
        .BUSY(BUSY),
        .DONE(DONE),
        .CLK(CLK)
    );
    
    REGU REGU_0 (
        .DATA_TO_REGU(DATA_TO_REGU),
        .DATA_FROM_REGU_A(DATA_FROM_REGU_A),
        .DATA_FROM_REGU_B(DATA_FROM_REGU_B),
        .WRITE_ENABLE_GR(WRITE_ENABLE_GR),
        .SELECT_GR_IN(SELECT_GR_IN),
        .SELECT_GR_OUTA(SELECT_GR_OUTA),
        .SELECT_GR_OUTB(SELECT_GR_OUTB),
        .FLAG_TO_REGU(FLAG_TO_REGU),
        .FLAG_FROM_REGU(FLAG_FROM_REGU),
        .WRITE_ENABLE_FLAG(WRITE_ENABLE_FLAG),
        .CLK(CLK)
    );
    
    ALU ALU_0 (
        .DATA_TO_ALU_A(DATA_TO_ALU_A),
        .DATA_TO_ALU_B(DATA_TO_ALU_B),
        .DATA_FROM_ALU(DATA_FROM_ALU),
        .FLAG_FROM_ALU(FLAG_FROM_ALU),
        .OP_CODE_HIGH(OP_CODE_HIGH)
    );
    
    SHIFTU SHIFTU_0 (
        .DATA_TO_SHIFTU_A(DATA_TO_SHIFTU_A),
        .DATA_TO_SHIFTU_B(DATA_TO_SHIFTU_B),
        .DATA_FROM_SHIFTU(DATA_FROM_SHIFTU),
        .FLAG_FROM_SHIFTU(FLAG_FROM_SHIFTU),
        .OP_CODE_HIGH(OP_CODE_HIGH),
        .CLK(CLK)
    );
    
    // 本来ならば、各ユニットの入出力を共通の内部バス(信号線)につなげ、
    // イネーブル信号とスリーステートバッファを使って制御しているが、
    // スリーステートバッファの使用はバグの巣窟である。
    // そこでここではスリーステートバッファの使用を避け、セレクタを使う。
        
    assign DATA_TO_CNTU_A   = DATA_FROM_REGU_A;
    assign DATA_TO_ALU_A    = DATA_FROM_REGU_A;
    assign DATA_TO_SHIFTU_A = DATA_FROM_REGU_A;
    
    assign DATA_TO_CNTU_B   = DATA_FROM_REGU_B;
    assign DATA_TO_ALU_B    = SELECT_FROM_CNTU_B ? DATA_FROM_CNTU_B : DATA_FROM_REGU_B;
    assign DATA_TO_SHIFTU_B = DATA_TO_ALU_B;
    
    always @(*) begin
       case({SELECT_FROM_CNTU_C, SELECT_FROM_ALU, SELECT_FROM_SHIFTU})
           3'b100:
            begin
                DATA_TO_REGU <= DATA_FROM_CNTU_C;
                FLAG_TO_REGU <= 3'bx;
            end
        3'b010:
            begin
                DATA_TO_REGU <= DATA_FROM_ALU;
                FLAG_TO_REGU <= FLAG_FROM_ALU;
            end
        3'b001:
            begin
                DATA_TO_REGU <= DATA_FROM_SHIFTU;
                FLAG_TO_REGU <= FLAG_FROM_SHIFTU;
            end
        default:
            begin
                DATA_TO_REGU <= 16'bx;
                FLAG_TO_REGU <= 3'bx;
            end
       endcase
    end
endmodule
