`timescale 1ns / 1ps

// REGU は汎用レジスタ GR0～GR7 と フラグレジスタ
// GR0 ～ GR7 は GR[0] ～ GR[7] (レジスタ配列はクセが強いので使うときは注意)
// フラグは FLAG_REGISTER、MSB側から順に OF, SF, ZF
// 制御用の専用レジスタ PR, SP, IR, MAR, MDR は CNTU ににある

module REGU(
        input [15:0] DATA_TO_REGU,
        output [15:0] DATA_FROM_REGU_A,
        output [15:0] DATA_FROM_REGU_B,
        input WRITE_ENABLE_GR,    // CNTU からの制御信号
        input [2:0] SELECT_GR_IN,
        input [2:0] SELECT_GR_OUTA,
        input [2:0] SELECT_GR_OUTB,
        input [2:0] FLAG_TO_REGU,    // ALU, SHIFTU からのフラグ値、演算結果
        output [2:0] FLAG_FROM_REGU, // CNTU へのフラグ値、分岐用
        input WRITE_ENABLE_FLAG,     // CNTU からの制御信号
        input CLK
    );
    
    reg [15:0] GR [0:7];    // レジスタファイル
            // メモリもこんな感じで作れるが、
            // 巨大なメモリを作りたいときはIPコアを使った方が良いらしい
    
    reg [2:0] FLAG_REGISTER;    // フラグレジスタ、MSB側から順に OF, SF, ZF
    wire OF;
    wire SF;
    wire ZF;
    
    assign {OF, SF, ZF} = FLAG_REGISTER;    // 本当はいらないんだけどシミュレーション時参照用に
    
    always @(posedge CLK) begin
        if(WRITE_ENABLE_GR) begin
            GR[SELECT_GR_IN] <= DATA_TO_REGU;
        end
    end
    
    assign DATA_FROM_REGU_A = GR[SELECT_GR_OUTA];
    assign DATA_FROM_REGU_B = GR[SELECT_GR_OUTB];
    
    always @(posedge CLK) begin
        if(WRITE_ENABLE_FLAG) begin
            FLAG_REGISTER <= FLAG_TO_REGU;
        end
    end
    assign FLAG_FROM_REGU = FLAG_REGISTER;
endmodule
