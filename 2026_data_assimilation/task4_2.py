"""
Task 4_2: 6時間サイクルのデータ同化システム (Extended Kalman Filter)
task4_da の条件（自前データ生成・dt=0.05）+ task4 の改善済み可視化

KF の式:
  [予報ステップ]
    xb    = M(xa)                            (非線形モデル積分)
    Pb    = M * Pa * M^T                     (予報誤差共分散の時間発展)
    Pb    = (1 + δ) * Pb                    (共分散インフレーション, δ≥0)

  [解析ステップ]
    K     = Pb H^T (H Pb H^T + R)^{-1}      (カルマンゲイン)
    xa    = xb + K (y - H xb)               (解析値)
    Pa    = (I - K H) Pb                    (解析誤差共分散)
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

# ==============================================================
# Lorenz96 モデル
# ==============================================================
def lorenz96(x, F=8.0):
    N = len(x)
    dxdt = np.zeros(N)
    for i in range(N):
        x_prev2 = x[(i - 2) % N]
        x_prev1 = x[(i - 1) % N]
        x_next1 = x[(i + 1) % N]
        dxdt[i] = (x_next1 - x_prev2) * x_prev1 - x[i] + F
    return dxdt


# RK4
def rk4(x, dt, F=8.0):
    k1 = lorenz96(x, F)
    k2 = lorenz96(x + 0.5 * dt * k1, F)
    k3 = lorenz96(x + 0.5 * dt * k2, F)
    k4 = lorenz96(x + dt * k3, F)
    return x + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)


# ==============================================================
# データ生成（2年積分、前半1年スピンアップ）
# ==============================================================
N = 40
F = 8.0
dt = 0.01           # RK4 精度向上
SIX_HOURS = 0.05    # 6時間 = 0.05 MTU（同化サイクル間隔）
save_every = int(SIX_HOURS / dt)          # 5 steps ごとに保存
steps_per_year = int(73.0 / dt)           # 1年 = 73 MTU → 7300 steps
n_obs = steps_per_year // save_every      # 保存点数 = 1460

total_steps = steps_per_year * 2

x = F * np.ones(N)
x[0] += 0.01  # small perturbation

# 後半1年を5ステップごとに保存 → truth (1460, 40)
truth = np.zeros((n_obs, N))
step = 0
save_idx = 0
for t in range(total_steps):
    x = rk4(x, dt, F)
    step += 1
    # 前半はスピンアップとして捨て、後半1年分を保存
    if step > steps_per_year and (step - steps_per_year) % save_every == 0:
        truth[save_idx] = x
        save_idx += 1

print(f"truth shape: {truth.shape}")

# 観測データ（真値 + N(0,1) ノイズ）
rng = np.random.Generator(np.random.MT19937(seed=42))
noise = rng.normal(loc=0.0, scale=1.0, size=truth.shape)
obs = truth + noise
print(f"obs shape:   {obs.shape}")

# ノイズ確認プロット
plt.figure(figsize=(8, 3))
plt.hist(noise.flatten(), bins=100, density=True, color="steelblue", alpha=0.7, label="Histogram")
x_range = np.linspace(-4, 4, 300)
plt.plot(x_range, norm.pdf(x_range, 0, 1), color="red", lw=2, label="N(0,1) PDF")
plt.xlabel("noise")
plt.ylabel("density")
plt.title(f"Observation noise  mean={noise.mean():.4f},  std={noise.std():.4f}")
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()

# ==============================================================
# Tangent Linear Matrix  δx(t+dt) = M δx(t)
# ==============================================================
def tangent_linear_matrix(x, dt):
    N = len(x)
    M = np.zeros((N, N))
    for j in range(N):
        j_minus2 = (j - 2) % N
        j_minus1 = (j - 1) % N
        j_plus1  = (j + 1) % N
        M[j, j_minus2] = -x[j_minus1] * dt
        M[j, j_minus1] = (x[j_plus1] - x[j_minus2]) * dt
        M[j, j]        = 1.0 - dt
        M[j, j_plus1]  = x[j_minus1] * dt
    return M


# ==============================================================
# EKF cycle
# ==============================================================
def EKF_cycle(xa, Pa, y_obs, dt, F, H, R, inflation):
    # 1. tangent linear matrix (M)
    M = tangent_linear_matrix(xa, dt)

    # 2. forecast state (xb): 6時間分 = save_every ステップ積分
    xb = xa.copy()
    for _ in range(save_every):
        xb = rk4(xb, dt, F)

    # 3. forecast covariance (Pb)
    Pb = M @ Pa @ M.T
    Pb = (1 + inflation) * Pb

    # 4. Kalman Gain
    S = H @ Pb @ H.T + R
    K = Pb @ H.T @ np.linalg.inv(S)

    # 5. analysis
    xa_new = xb + K @ (y_obs - H @ xb)

    # 6. analysis covariance
    I = np.eye(len(xa))
    Pa_new = (I - K @ H) @ Pb

    return xa_new, Pa_new, xb, Pb, K


# ==============================================================
# main loop
# ==============================================================
H = np.eye(N)
R = np.eye(N)

inflation_values = [0.0, 0.03, 0.05, 0.055, 0.06, 0.08]
result = {}

for inflation in inflation_values:
    xa = obs[0].copy()
    Pa = 10 * np.eye(N)

    xb_save      = []
    xa_save      = []
    pb_save      = []
    pa_save      = []
    spread_a_list = []
    rmse_b_list  = []
    rmse_a_list  = []

    for t in range(1, truth.shape[0]):
        xa, Pa, xb, Pb, K = EKF_cycle(xa, Pa, obs[t], dt, F, H, R, inflation)

        xb_save.append(xb.copy())
        xa_save.append(xa.copy())
        pb_save.append(Pb.copy())
        pa_save.append(Pa.copy())
        spread_a_list.append(np.sqrt(np.trace(Pa) / N))
        rmse_b_list.append(np.sqrt(np.mean((xb - truth[t]) ** 2)))
        rmse_a_list.append(np.sqrt(np.mean((xa - truth[t]) ** 2)))

    result[inflation] = {
        "forecast":             np.array(xb_save),
        "analysis":             np.array(xa_save),
        "Pb":                   np.array(pb_save),
        "Pa":                   np.array(pa_save),
        "analysis_spread":      np.array(spread_a_list),
        "mean_analysis_spread": np.mean(spread_a_list),
        "forecast_rmse":        np.array(rmse_b_list),
        "analysis_rmse":        np.array(rmse_a_list),
        "mean_forecast_rmse":   np.mean(rmse_b_list),
        "mean_analysis_rmse":   np.mean(rmse_a_list),
    }

# 結果サマリ
for inflation in inflation_values:
    print(f"inflation={inflation:.3f}  "
          f"Forecast RMSE={result[inflation]['mean_forecast_rmse']:.4f}  "
          f"Analysis RMSE={result[inflation]['mean_analysis_rmse']:.4f}  "
          f"Spread={result[inflation]['mean_analysis_spread']:.4f}")

# ==============================================================
# 可視化
# ==============================================================
time_days = np.arange(1, truth.shape[0]) / 4.0
var = 0

# --- 1. inflation 比較（1つの図にサブプロット）---
start_day = 200
end_day = 300
mask = (time_days >= start_day) & (time_days <= end_day)

fig, axes = plt.subplots(len(inflation_values), 1, figsize=(10, 3 * len(inflation_values)), sharex=True)
fig.suptitle(f"Truth, Observation, Forecast, Analysis  (x_{var}, day {start_day}–{end_day})", fontsize=13)

for ax, inflation in zip(axes, inflation_values):
    xb_s = result[inflation]["forecast"]
    xa_s = result[inflation]["analysis"]
    ax.plot(time_days[mask], truth[1:, var][mask], label="Truth", color="red")
    ax.scatter(time_days[mask], obs[1:, var][mask], label="Observation", s=5, alpha=0.25)
    ax.plot(time_days[mask], xb_s[:, var][mask], label="Forecast", color="steelblue")
    ax.plot(time_days[mask], xa_s[:, var][mask], label="Analysis", color="black")
    ax.set_ylabel(f"x_{var}")
    ax.set_title(f"inflation={inflation}")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(True)

axes[-1].set_xlabel("Time [days]")
plt.tight_layout()
plt.show()

colors = {
    0.0:   "black",
    0.03:  "blue",
    0.05:  "green",
    0.055: "red",
    0.06:  "purple",
    0.08:  "brown",
}

# --- 2. Analysis RMSE 時系列（全体）---
plt.figure(figsize=(8, 4))
mask = (time_days >= 1) & (time_days <= 300)

for inflation in inflation_values:
    rmse = result[inflation]["analysis_rmse"]
    plt.plot(time_days[mask], rmse[mask], label=f"inflation={inflation:.3f}",
             color=colors[inflation], linewidth=0.7)

plt.xlim(0, 300)
plt.ylim(0, 7)
plt.ylabel("ave RMSE")
plt.title("Analysis RMSE for different inflation values")
plt.legend()
plt.grid(True)
plt.show()

# --- 3. Analysis RMSE 時系列（250–300日 拡大）---
plt.figure(figsize=(8, 4))
mask = (time_days >= 250) & (time_days <= 300)

for inflation in inflation_values:
    rmse = result[inflation]["analysis_rmse"]
    plt.plot(time_days[mask], rmse[mask], label=f"inflation={inflation:.3f}",
             color=colors[inflation], linewidth=1)

plt.xlim(250, 300)
plt.ylim(0, 1)
plt.xlabel("time (day)")
plt.ylabel("ave RMSE")
plt.title("Analysis RMSE (zoomed: day 250–300)")
plt.legend()
plt.grid(True)
plt.show()

# --- 4. 解析誤差共分散 Pa のヒートマップ ---
plot_inflations = [0.0, 0.03, 0.055, 0.08]
plot_days = [1, 10, 300]

fig, axes = plt.subplots(len(plot_days), len(plot_inflations), figsize=(14, 17))
vmin, vmax = -0.3, 0.3

for i, day in enumerate(plot_days):
    idx = int(day * 4) - 1  # 6時間ごとなので1日=4step
    for j, inflation in enumerate(plot_inflations):
        Pa = result[inflation]["Pa"][idx]
        ax = axes[i, j]
        im = ax.imshow(Pa, cmap="bwr", vmin=vmin, vmax=vmax, origin="upper")
        ax.set_title(f"Pa  infla={inflation:.2f}  day={day}")
        ax.set_xticks([0, 10, 20, 30, 39])
        ax.set_yticks([0, 10, 20, 30, 39])

cbar_ax = fig.add_axes([0.3, 0.04, 0.4, 0.025])
plt.suptitle("Analysis Error Covariance $P_t^a$", fontsize=18)
fig.subplots_adjust(bottom=0.05, top=0.90, hspace=0.45, wspace=0.25)
fig.colorbar(im, cax=cbar_ax, pad=0.12, shrink=0.5, orientation="horizontal")
plt.tight_layout()
plt.show()

# --- 5. inflation 最適化（Mean Analysis RMSE vs δ）---
infls = inflation_values
means = [result[i]["mean_analysis_rmse"] for i in infls]

plt.figure(figsize=(6, 4))
plt.plot(infls, means, marker='o')
plt.xlabel("Inflation δ")
plt.ylabel("Mean Analysis RMSE")
plt.title("Optimization of inflation parameter")
plt.grid(True)
plt.show()

# --- 6. Mean RMSE vs Spread 棒グラフ ---
mean_rmse_a  = [result[i]["mean_analysis_rmse"]   for i in inflation_values]
mean_spread_a = [result[i]["mean_analysis_spread"] for i in inflation_values]

x_pos = np.arange(len(inflation_values))
width = 0.35

plt.figure(figsize=(8, 4))
plt.bar(x_pos - width/2, mean_rmse_a,   width, label="Mean Analysis RMSE")
plt.bar(x_pos + width/2, mean_spread_a, width, label="Mean Spread sqrt(tr(Pa)/N)")
plt.xticks(x_pos, [str(i) for i in inflation_values])
plt.xlabel("Inflation δ")
plt.ylabel("Error size")
plt.title("Mean Analysis RMSE vs Mean Spread")
plt.ylim(0, 0.5)
plt.yticks(np.arange(0, 0.51, 0.1))
plt.legend()
plt.grid(axis="y")
plt.show()

# --- 7. RMSE 時系列（最後の inflation）---
last_inflation = inflation_values[-1]
rmse_b_list = result[last_inflation]["forecast_rmse"]
rmse_a_list = result[last_inflation]["analysis_rmse"]
time_days_rmse = np.arange(len(rmse_a_list)) / 4.0

plt.figure(figsize=(12, 4))
plt.plot(time_days_rmse, rmse_b_list, label="Forecast RMSE")
plt.plot(time_days_rmse, rmse_a_list, label="Analysis RMSE")
plt.xlabel("Time [days]")
plt.ylabel("RMSE")
plt.title(f"EKF RMSE  (inflation={last_inflation})")
plt.legend()
plt.grid(True)
plt.show()
