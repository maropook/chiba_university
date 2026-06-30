# 第4週目 課題2 レポート

## 課題内容
課題1（図17）のプログラム実行時において、CNTU 内レジスタ STATE の値がどのように変化しているか調べよ。
また、このプログラム実行時の CPI と MIPS 値を求めよ。

---

## 実験方法

### 環境構築
1. Vivado で新規プロジェクトを作成
2. IP INTEGRATOR でブロックデザインを作成
   - Block Memory Generator（16bit幅、65536深さ）を配置
   - COEファイルにて課題1の機械語をメモリ初期値として設定
3. COMET II の Verilog ソース（COMETII.v, CNTU.v, REGU.v, ALU.v, SHIFTU.v）をプロジェクトに追加
4. ブロックデザインにて COMET II とメモリを接続
5. testbench.v を作成してシミュレーション実行

### メモリ初期値（COEファイル）
```
memory_initialization_radix=16;
memory_initialization_vector=1010 0005 1110 0006 8100 1234 0000;
```

対応するプログラム：
```
#0000: #1010  LD GR1,A
#0001: #0005
#0002: #1110  ST GR1,B
#0003: #0006
#0004: #8100  RET
#0005: #1234  A DC #1234
#0006: #0000  B DS 1
```

### STATE の読み方
CNTU.v 内の parameter 文に STATE の値と状態名の対応が定義されている。
波形シミュレーションで STATE[7:0] を16進数表示にして確認した。

---

## 実験結果

### STATEの変化

波形シミュレーションより、START=1 以降の STATE の変化は以下の通りであった。

| STATE値 | 状態名 | 動作 |
|--------|--------|------|
| 00 | STATE_READY | START待機 |
| **--- LD GR1,A ---** | | |
| 01 | STATE_FETCH_1ST | MAR←PC, PC←PC+1、メモリ読み出し要求 |
| 02 | STATE_FETCH_2ND | メモリ応答待ち |
| 03 | STATE_FETCH_3RD | MDR←メモリ |
| 04 | STATE_FETCH_4TH | IR←MDR |
| 08 | STATE_DECODING | IR を解読、LD命令と判断 |
| 0c | STATE_LOAD_OPERAND_1ST | 第2語（アドレス）読み出し要求 |
| 0d | STATE_LOAD_OPERAND_2ND | メモリ応答待ち |
| 0e | STATE_LOAD_OPERAND_3RD | MDR←#0005 |
| 20 | STATE_CALC_MEM_1ST | MAR←#0005、メモリ読み出し要求 |
| 21 | STATE_CALC_MEM_2ND | メモリ応答待ち |
| 22 | STATE_CALC_MEM_3RD | MDR←#1234 |
| 23 | STATE_CALC_MEM_4TH | GR1←#1234 |
| **--- ST GR1,B ---** | | |
| 01 | STATE_FETCH_1ST | MAR←PC, PC←PC+1 |
| 02 | STATE_FETCH_2ND | メモリ応答待ち |
| 03 | STATE_FETCH_3RD | MDR←メモリ |
| 04 | STATE_FETCH_4TH | IR←MDR |
| 08 | STATE_DECODING | ST命令と判断 |
| 0c | STATE_LOAD_OPERAND_1ST | 第2語（アドレス）読み出し要求 |
| 0d | STATE_LOAD_OPERAND_2ND | メモリ応答待ち |
| 0e | STATE_LOAD_OPERAND_3RD | MDR←#0006 |
| 10 | STATE_STORE_1ST | MAR←#0006、メモリ[#0006]←GR1 |
| 11 | STATE_STORE_2ND | メモリ書き込み待ち |
| **--- RET ---** | | |
| 01 | STATE_FETCH_1ST | MAR←PC, PC←PC+1 |
| 02 | STATE_FETCH_2ND | メモリ応答待ち |
| 03 | STATE_FETCH_3RD | MDR←メモリ |
| 04 | STATE_FETCH_4TH | IR←MDR |
| 08 | STATE_DECODING | RET命令と判断、スタック空なのでHALTへ |
| ff | STATE_HALT | プログラム終了、DONE=1 |

---

## CPI と MIPS の計算

### 各命令のクロック数

| 命令 | クロック数 |
|------|-----------|
| LD GR1,A | 12 |
| ST GR1,B | 10 |
| RET | 5 |
| **合計** | **27** |

### CPI（Cycles Per Instruction）

$$CPI = \frac{総クロック数}{命令数} = \frac{27}{3} = 9.0$$

命令開始から終わるまでの総クロック数 = 27
命令数はLD ST RETと3つあるため
総クロック数÷命令数= 27÷3 = 9.0

### MIPS（Million Instructions Per Second）

クロック周波数 = 125 MHz

$$MIPS = \frac{クロック周波数(MHz)}{CPI} = \frac{125}{9.0} \approx 13.9 \text{ MIPS}$$

---

## 考察

COMET II は各命令を複数のクロックに分けて実行する。
すべての命令に共通するフェッチサイクル（01→02→03→04）に4クロックかかり、
さらに命令の種類によって異なる実行サイクルが続く。

LD命令はメモリを2回読む（命令フェッチ＋データ読み出し）ため最もクロック数が多く12クロックかかる。
ST命令はメモリへの書き込みがあるため10クロック。
RET命令はスタックが空の場合そのままHALTに遷移するため5クロックで最も少ない。


