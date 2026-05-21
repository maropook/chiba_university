`timescale 1ns/1ps
module testbench;
    reg START;
    reg CLK;
    wire BUSY;
    wire DONE;

    design_1_wrapper UUT (.BUSY(BUSY), .CLK(CLK), .DONE(DONE), .START(START));

    always begin
        CLK <= 0; #4
        CLK <= 1; #4
        ;
    end
    initial begin
        START <= 0; #122  // リセット GSR がオフになるまで待つ
        START <= 1; #200000  // 50000ns実行
        $finish;
    end
endmodule
