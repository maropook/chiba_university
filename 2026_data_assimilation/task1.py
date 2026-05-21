"""
1. L96 を 4 次の Runge-Kutta 法を用いて実装する。
パラメータ値 F を色々と変え、F=8 の時にカオスとなることを確認する。

ここでは、Runge-Kutta はライブラリを用いずに自分でコーディングする事。
また、オイラー法など、他の積分スキームと比較してみる。
ヒント）まずは、原著論文 Lorenz and Emanuel (1998) の Fig. 1 を再現する。
"""

"""
オイラー法ではそのばその場でやっていくだけなので、だんだんズレていく
ルンゲ・クッタ法では、そのばその場ではありつつ、4点ほどの傾きも使用するのでより正確であってる？


RK4のほうが絶対いいよねということを
"""

import numpy as np
import matplotlib.pyplot as plt

from l96_core import rk4_step, euler_step, rk2_step, simulate, initial_condition

# ==============================================================
# モデル・シミュレーションパラメータ
# ==============================================================
N = 40  # 格子点数（変数の次元）
dt = 0.01  # 時間刻み（無次元時間）
T_end = 20.0  # 積分時間
num_steps = int(T_end / dt)
t_values = np.linspace(0, T_end, num_steps + 1)


# ==============================================================
# 1. 複数の F 値でカオス性の確認（RK4）
# ==============================================================
F_values = [1, 4, 8, 16]

fig, axes = plt.subplots(len(F_values), 1, figsize=(12, 10), sharex=True)
fig.suptitle("Lorenz 96: Time series of $X_1$ for various F (RK4)", fontsize=14)

for ax, F in zip(axes, F_values):
    x0 = initial_condition(F, N)
    traj = simulate(rk4_step, x0, dt, num_steps, F)
    ax.plot(t_values, traj[:, 0], lw=0.8)
    ax.set_ylabel(f"$X_1$\n(F={F})", fontsize=11)
    ax.grid(True, alpha=0.3)

axes[-1].set_xlabel("Time (MTU)")
plt.tight_layout()
plt.savefig("task1_F_comparison.png", dpi=150)
plt.show()
print("Figure 1 saved: task1_F_comparison.png")


# ==============================================================
# 2. Lorenz & Emanuel (1998) Fig. 1 の再現
#    F=8, N=40 での Hovmöller 図（時空間図）
# ==============================================================
F = 8
x0 = initial_condition(F, N)
traj_rk4 = simulate(rk4_step, x0, dt, num_steps, F)

fig, ax = plt.subplots(figsize=(12, 6))
im = ax.imshow(
    traj_rk4.T,
    aspect="auto",
    origin="lower",
    extent=[t_values[0], t_values[-1], 1, N],
    cmap="RdBu_r",
    vmin=-10,
    vmax=10,
)
plt.colorbar(im, ax=ax, label="$X_j$")
ax.set_xlabel("Time (MTU)")
ax.set_ylabel("Site index $j$")
ax.set_title(
    f"Lorenz 96 Hovmöller Diagram  (F={F}, N={N}, RK4)\n"
    "Reproduction of Lorenz & Emanuel (1998) Fig. 1"
)
plt.tight_layout()
plt.savefig("task1_hovmoller.png", dpi=150)
plt.show()
print("Figure 2 saved: task1_hovmoller.png")


# ==============================================================
# 3. 積分スキームの比較（F=8）
#    RK4 vs オイラー法 vs 2次 RK（修正オイラー法）
# ==============================================================
F = 8
x0 = initial_condition(F, N)
T_cmp = 5.0
num_steps_cmp = int(T_cmp / dt)
t_cmp = np.linspace(0, T_cmp, num_steps_cmp + 1)

traj_rk4_cmp = simulate(rk4_step, x0, dt, num_steps_cmp, F)
traj_rk2_cmp = simulate(rk2_step, x0, dt, num_steps_cmp, F)
traj_eul_cmp = simulate(euler_step, x0, dt, num_steps_cmp, F)


# RK4 を参照解として RMSE を計算
def rmse(a, ref):
    return np.sqrt(np.mean((a - ref) ** 2, axis=1))


# root mean squre error, 横が1の2次元がこれ
#  rmse(error, true):
# return np.sqrt(np.mean((error - true)**2 , axis = 1))


fig, axes = plt.subplots(2, 1, figsize=(12, 8))

# 上段：X_1 の時系列比較
ax = axes[0]
ax.plot(t_cmp, traj_rk4_cmp[:, 0], label="RK4 (reference)", lw=1.5)
ax.plot(t_cmp, traj_rk2_cmp[:, 0], label="RK2 (Heun)", lw=1.2, ls="--")
ax.plot(t_cmp, traj_eul_cmp[:, 0], label="Euler", lw=1.0, ls=":")
ax.set_ylabel("$X_1$")
ax.set_title(f"Scheme comparison: $X_1$ time series  (F={F}, dt={dt})")
ax.legend()
ax.grid(True, alpha=0.3)

# 下段：RK4 との RMSE
ax = axes[1]
ax.semilogy(t_cmp, rmse(traj_rk2_cmp, traj_rk4_cmp), label="RK2 vs RK4", ls="--")
ax.semilogy(t_cmp, rmse(traj_eul_cmp, traj_rk4_cmp), label="Euler vs RK4", ls=":")
ax.set_xlabel("Time (MTU)")
ax.set_ylabel("RMSE (log scale)")
ax.set_title("RMSE compared to RK4 reference solution")
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("task1_scheme_comparison.png", dpi=150)
plt.show()
print("Figure 3 saved: task1_scheme_comparison.png")


# ==============================================================
# 4. エネルギー（X^2 の空間平均）の時間変化でカオス性を確認
# ==============================================================
F_chaos = [4, 8]
fig, ax = plt.subplots(figsize=(12, 4))
for F in F_chaos:
    x0 = initial_condition(F, N)
    traj = simulate(rk4_step, x0, dt, num_steps, F)
    energy = np.mean(traj**2, axis=1) #全地点を2乗して平均しているnp.mean(traj**2, axis=1)
    ax.plot(t_values, energy, label=f"F={F}")
ax.set_xlabel("Time (MTU)")
ax.set_ylabel("$\\langle X^2 \\rangle$  (spatial mean)")
ax.set_title("Lorenz 96: Spatially-averaged variance over time")
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("task1_energy.png", dpi=150)
plt.show()
print("Figure 4 saved: task1_energy.png")


"""
オイラー法ではそのばその場でやっていくだけなので、だんだんズレていく
ルンゲ・クッタ法では、そのばその場ではありつつ、4点ほどの傾きも使用するのでより正確であってる？

"""

# ==============================================================
# 5. 初期値鋭敏依存性の確認（カオスの本質）
#    x0a と x0b をわずかにずらして x1 を比較
# ==============================================================
F = 8
x0a = F * np.ones(N)
x0a[19] += 0.01  # 軌道 A
x0b = F * np.ones(N)
x0b[19] += 0.011  # 軌道 B（0.001 だけ違う）

traj_a = simulate(rk4_step, x0a, dt, num_steps, F)
traj_b = simulate(rk4_step, x0b, dt, num_steps, F)

fig, axes = plt.subplots(2, 1, figsize=(12, 7))

# 上段：x1 の時系列比較
ax = axes[0]
ax.plot(t_values, traj_a[:, 0], label="軌道 A (perturb=0.010)", lw=1.2)
ax.plot(t_values, traj_b[:, 0], label="軌道 B (perturb=0.011)", lw=1.2, ls="--")
ax.set_ylabel("$X_1$")
ax.set_title(
    f"初期値鋭敏依存性の確認  (F={F}, N={N})\n" "初期条件が 0.001 だけ違う2軌道の $X_1$"
)
ax.legend()
ax.grid(True, alpha=0.3)

# 下段：差の絶対値（対数スケール）
diff = np.abs(traj_a[:, 0] - traj_b[:, 0])
ax = axes[1]
ax.semilogy(t_values, diff, color="red", lw=1.2)
ax.set_xlabel("Time (MTU)")
ax.set_ylabel("|A - B|  (log scale)")
ax.set_title("2軌道間の差（指数的に拡大 → カオス）")
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("task1_chaos_sensitivity.png", dpi=150)
plt.show()
print("Figure 5 saved: task1_chaos_sensitivity.png")
