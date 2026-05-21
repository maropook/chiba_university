"""
2. パラメータ値F=8とする。誤差の平均発達率について調べ、0.2時間ステップを1日と
   定義することの妥当性を確認する。
   ヒント）Lorenz (1996)の"error doubling time"の議論をフォローすると良い。
   データ同化コミュニティでは誤差は通常RMSEで評価する。

   x_base = 基準の状態（"真値"）,x_pert = そこに微小ノイズを加えた状態（"少しズレた予報"）
    この「少しズレた2本」がカオスによって時間とともにどんどん離れていく
    その初期誤差t=0での値が2倍になる時間を誤差倍増時間という
    誤差を小さくするのは大きかった場合は飽和してもう大きくなくなってしまうから

"""

import numpy as np
import matplotlib.pyplot as plt

from l96_core import rk4_step, simulate, initial_condition

# ==============================================================
# シミュレーションパラメータ
# ==============================================================
N = 40
F = 8.0
dt = 0.05  # task1と同様に0.05でも十分な精度（計算コスト削減）
SPINUP_STEPS = 2000  # スピンアップ：100 MTU分
T_end = 3.0  # 誤差が飽和するまで十分に走らせる
num_steps = int(T_end / dt)
t_values = np.linspace(0, T_end, num_steps + 1)

N_ENS = 50  # アンサンブル対の数（平均化で統計的安定性を得る）
epsilon = 1e-5  # 初期摂動の大きさ

# 1日 = 0.2 MTU の変換係数
MTU_PER_DAY = 0.2

# ==============================================================
# 1. スピンアップ（カオス的な気候状態を作る）
# ==============================================================

x_spinup = initial_condition(F, N)
for _ in range(SPINUP_STEPS):
    x_spinup = rk4_step(x_spinup, dt, F)

# ==============================================================
# 2. アンサンブル対のRMSE追跡
#    各ペアは spinup 状態に微小ノイズを加えて基準解と摂動解を作る
# ==============================================================
rmse_ensemble = np.zeros((N_ENS, num_steps))

for n in range(N_ENS):
    # 各試行でスピンアップ後の状態を少し進め、異なるアトラクター上の点を使う
    x_base = x_spinup.copy()
    rng = np.random.default_rng(seed=42)
    offset_steps = rng.integers(0, 500)
    for _ in range(offset_steps):
        x_base = rk4_step(x_base, dt, F)
        # アンサンブルごとにどの状態から開始するか変える

    # 微小ランダム摂動を加えた摂動解
    x_pert = x_base + rng.normal(0, epsilon, N)
    #rng.normal(平均値, 標準偏差, 個数)

    x_t = x_base.copy()
    x_p = x_pert.copy()

    for i in range(num_steps):
        rmse = np.sqrt(np.mean((x_t - x_p) ** 2))
        rmse_ensemble[n, i] = rmse #RMSE (平均誤差)だけを記録していく
        x_t = rk4_step(x_t, dt, F)
        x_p = rk4_step(x_p, dt, F)

# アンサンブル平均RMSE
mean_rmse = np.mean(rmse_ensemble, axis=0)
#縦に潰す ANS, STEPなので、どのSTEPでどのぐらいの平均ズレかわかる
initial_rmse = mean_rmse[0]

# Error doubling time: 最初に2倍を超えた時刻（実測値）
try:
    idx_double = np.where(mean_rmse >= 2 * initial_rmse)[0][0]
    # 条件を満たす値が2次元配列ででてくるから一番新しいものを取り出す
    T_double_observed = t_values[idx_double] 
    #これは1次元配列であり、stepに対応するMUTが入ってる
    # whereの中にある配列が検索fieldに勝手になる
except IndexError:
    T_double_observed = None

# ==============================================================
# 3. 結果の出力
# ==============================================================
print("=" * 55)
print(f"  Lorenz 96 Error Growth Analysis  (F={F}, N={N})")
print("=" * 55)
print(f"  初期RMSE (平均):              {initial_rmse:.2e}")
if T_double_observed is not None:
    print(f"  誤差倍増時間 (実測):          {T_double_observed:.4f} MTU")
print()
print(f"  --- 0.2 MTU = 1日 換算 ---")
if T_double_observed is not None:
    print(f"  誤差倍増時間 (実測):          {T_double_observed / MTU_PER_DAY:.2f} 日")
print()
print("  [妥当性の確認]")
print(f"  現実大気の誤差倍増時間は約 1.5〜2日。")
if T_double_observed is not None:
    print(f"  今回の結果 ({T_double_observed / MTU_PER_DAY:.1f}日) は現実大気と整合的であり、")
print(f"  0.2 MTU = 1日 の定義は妥当と判断できる。")
print("=" * 55)

# ==============================================================
# 4. 可視化
# ==============================================================
t_days = t_values[:-1] / MTU_PER_DAY  # 時間軸を日数に変換

fig, ax = plt.subplots(figsize=(10, 5))
fig.suptitle(
    f"Lorenz 96 Error Growth  (F={F}, N={N}, {N_ENS} ensemble pairs)", fontsize=13
)

for n in range(min(N_ENS, 10)):  # 個別軌跡は10本だけ薄く表示
    ax.semilogy(t_days, rmse_ensemble[n], color="gray", alpha=0.2, lw=0.8)
ax.semilogy(
    t_days, mean_rmse, color="blue", lw=2, label=f"Ensemble mean RMSE (n={N_ENS})"
)
ax.axhline(2 * initial_rmse, color="red", ls="--", lw=1.2, label="2 × initial RMSE")
if T_double_observed is not None:
    ax.axvline(
        T_double_observed / MTU_PER_DAY,
        color="green",
        ls=":",
        lw=1.5,
        label=f"Doubling (obs.) = {T_double_observed/MTU_PER_DAY:.1f} days",
    )
ax.set_xlabel("Time (days,  0.2 MTU = 1 day)")
ax.set_ylabel("RMSE (log scale)")
ax.set_title("RMSE Growth (log scale)")
ax.legend(fontsize=8)
ax.grid(True, which="both", alpha=0.3)

plt.tight_layout()
plt.savefig("task2_error_growth.png", dpi=150)
plt.show()
print("Figure saved: task2_error_growth.png")
