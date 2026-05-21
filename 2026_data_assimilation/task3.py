"""
Task 3: L96 真値生成・観測データ作成・可視化

- L96 を 2 年分積分（前半 1 年はスピンアップとして捨てる）
- 後半 1 年を 6 時間毎に保存 → 真値
- Mersenne Twister 法で分散 1 の正規分布乱数生成 → ノイズ
- 真値 + ノイズ → 観測データ
- 可視化: 真値と観測データを重ねた時系列 + 乱数のヒストグラム

時間スケール: 1 MTU ≈ 5 日 (Lorenz & Emanuel 1998)
  1 年 = 73 MTU,  6 時間 = 0.05 MTU,  dt = 0.05 → 毎 step 保存
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib

matplotlib.rcParams["font.family"] = "Hiragino Sans"
from scipy.stats import norm

from l96_core import rk4_step, initial_condition

# ==============================================================
# パラメータ
# ==============================================================
N = 40
F = 8
dt = 0.05  # 1ステップ = 6時間 = 0.05 MTU

ONE_YEAR_MTU = 73.0  # 1 年 [MTU]
SIX_HOURS_MTU = 0.05  # 6 時間 [MTU]

spinup_steps = int(ONE_YEAR_MTU / dt)  # = 1460 steps
truth_steps = int(ONE_YEAR_MTU / dt)   # = 1460 steps
n_obs = truth_steps                    # 毎ステップ保存 → 1460 時点

# ==============================================================
# 2 年積分（前半スピンアップ、後半を真値として保存）
# ==============================================================
x = initial_condition(F, N)

# スピンアップ（前半 1 年）
for _ in range(spinup_steps):
    x = rk4_step(x, dt, F)

# 後半 1 年: 6 時間毎に保存
truth = np.zeros((n_obs, N))
t_save = np.arange(n_obs) * SIX_HOURS_MTU  # 保存時刻 [MTU]
# n_obsで連番を作成しているので保存した時刻をたくさん作ってる

for step in range(truth_steps):
    truth[step] = x
    x = rk4_step(x, dt, F)

np.save("task3_truth.npy", truth)
print(f"真値保存完了: task3_truth.npy  shape={truth.shape}")

# ==============================================================
# 乱数生成 (Mersenne Twister / MT19937 ベース)
# ==============================================================
rng = np.random.default_rng(seed=42)  # default_rng は MT19937 を使用
# ランダムな数字をたくさん作ってる
noise = rng.standard_normal(size=(n_obs, N))  # 平均 0, 分散 1
# sizeで２次元配列にしている、standard_normalは標準正規分布ということ

# ==============================================================
# 観測データ
# ==============================================================
obs = truth + noise
np.save("task3_obs.npy", obs)
print(f"観測データ保存完了: task3_obs.npy  shape={obs.shape}")

# ==============================================================
# 可視化
# ==============================================================
fig, axes = plt.subplots(2, 1, figsize=(12, 9))
fig.suptitle("L96 Task 3: 真値・観測データ・乱数確認", fontsize=14)

# --- 上段: X_1 の時系列（真値 vs 観測データ）---
ax = axes[0]
ax.plot(t_save, truth[:, 0], color="steelblue", lw=1.2, label="真値 $X_1$")
ax.scatter(t_save, obs[:, 0], color="tomato", s=6, alpha=0.6, label="観測データ $X_1$")
ax.set_xlabel("Time (MTU)")
ax.set_ylabel("$X_1$")
ax.set_title("後半 1 年の真値と観測データ（X₁, 6 時間毎）")
ax.legend(loc="upper right")
ax.grid(True, alpha=0.3)

# --- 下段: 乱数ヒストグラム（正規分布確認）---
ax = axes[1]
noise_flat = noise.flatten()
ax.hist(
    noise_flat,
    bins=100,
    density=True,
    color="steelblue",
    alpha=0.7,
    label="乱数ヒストグラム",
)
x_range = np.linspace(-4, 4, 300)
ax.plot(x_range, norm.pdf(x_range, 0, 1), color="red", lw=2, label="N(0,1) 理論 PDF")
ax.set_xlabel("値")
ax.set_ylabel("確率密度")
ax.set_title(
    f"生成乱数のヒストグラム  (n={noise_flat.size:,},  "
    f"mean={noise_flat.mean():.4f},  std={noise_flat.std():.4f})"
)
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("task3_result.png", dpi=150)
plt.show()
print("図保存完了: task3_result.png")

# --- 真値のみ ---
fig, ax = plt.subplots(figsize=(12, 4))
ax.plot(t_save, truth[:, 0], color="steelblue", lw=1.2)
ax.set_xlabel("Time (MTU)")
ax.set_ylabel("$X_1$")
ax.set_title("真値 $X_1$（後半 1 年, 6 時間毎）")
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("task3_truth_plot.png", dpi=150)
plt.show()
print("図保存完了: task3_truth_plot.png")
