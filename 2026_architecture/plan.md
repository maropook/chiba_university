# 課題対応計画

## ステップ1: Vivadoセットアップ（課題2のため必須）

### ブロックデザイン作成手順
1. 新規プロジェクト作成
2. IP INTEGRATOR → Create Block Design（名前: design_1）
3. Block Memory Generator を配置・設定
   - Basic: Single Port RAM, Width=16, Depth=65536
   - Port A: Read Width=16
   - Other Options: COEファイル作成
4. COEファイルに課題1のプログラムを入力：
   ```
   memory_initialization_radix=16;
   memory_initialization_vector=1010 0005 1110 0006 8100 1234 0000;
   ```
5. cometiisrcの5ファイルをdesign sourcesに追加
6. ブロックデザインにCOMET IIを配置・配線（表1通り）
7. 入出力ポート作成（START/BUSY/DONE/CLK）
8. Validate Design → Save
9. Create HDL Wrapper → Set as Top
10. testbench.vを作成してシミュレーション実行

---

## ステップ2: 課題2（STATEの観察・CPI・MIPS）

### シミュレーション後の作業
- 波形にSTATEを追加（Scope → CNTU → STATE）
- STATEの変化を記録
- 総クロック数を数える → CPI = 総クロック ÷ 3
- MIPS = 125 ÷ CPI

### 予測値（シミュレーションで確認）
- LD: 13クロック、ST: 10クロック、RET: 9クロック
- 合計32クロック → CPI ≈ 10.67、MIPS ≈ 11.7

### STATEの変化
```
00 READY
--- LD GR1,A ---
01 FETCH_1ST
02 FETCH_2ND
03 FETCH_3RD
04 FETCH_4TH
08 DECODING
0c LOAD_OPERAND_1ST
0d LOAD_OPERAND_2ND
0e LOAD_OPERAND_3RD
20 CALC_MEM_1ST
21 CALC_MEM_2ND
22 CALC_MEM_3RD
23 CALC_MEM_4TH
--- ST GR1,B ---
01 02 03 04 08 0c 0d 0e
10 STORE_1ST
11 STORE_2ND
--- RET ---
01 02 03 04 08
88 RET_1ST
89 RET_2ND
8a RET_3RD
8b RET_4TH
ff HALT
```

---

## ステップ3: 課題4（掛け算プログラム）

### ファイル: mul.asm

### アルゴリズム：シフト加算法
```
MAIN  START
      LD   GR1,A        ; GR1 = A (#005F)
      LD   GR2,B        ; GR2 = B (#007D)
      XOR  GR0,GR0      ; GR0 = 0 (結果)

LOOP  AND  GR2,ONE      ; GR2の最下位ビット確認
      JZE  SKIP         ; 0なら加算しない
      ADDA GR0,GR1      ; 結果 += GR1

SKIP  SLL  GR1,1        ; GR1を左シフト（×2）
      SRL  GR2,1        ; GR2を右シフト
      CPA  GR2,ZERO     ; GR2が0か確認
      JZE  DONE         ; 0なら終了
      JUMP LOOP

DONE  ST   GR0,ANS      ; 結果を格納
      RET

A     DC   #005F
B     DC   #007D
ONE   DC   #0001
ZERO  DC   #0000
ANS   DS   1
      END
```

### 期待する結果
#005F × #007D = 95 × 125 = 11875 = #2E83
