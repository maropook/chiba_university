"""
Task 4: 6時間サイクルのデータ同化システム (Extended Kalman Filter)

KF の式:
  [予報ステップ]
    xb    = M(xa)                            (非線形モデル積分)
    Pb    = M * Pa * M^T                     (予報誤差共分散の時間発展)
    Pb    = (1 + δ) * Pb                    (共分散インフレーション, δ≥0)

  [解析ステップ]
    K     = Pb H^T (H Pb H^T + R)^{-1}      (カルマンゲイン)
    xa    = xb + K (y - H xb)               (解析値)
    Pa    = (I - K H) Pb                    (解析誤差共分散)

  dtは変化率に対してどれぐらいかけるかで基準がMTUである
"""

import numpy as np
import matplotlib.pyplot as plt

from l96_core import rk4_step

# ==============================================================
# パラメータ
# ==============================================================
N = 40
F = 8
dt = 0.05  # 1ステップ = 6時間 = 0.05 MTU

# ==============================================================
# task3 の結果を読み込む
# ==============================================================
truth = np.load("task3_truth.npy")  # (1460, 40)
obs = np.load("task3_obs.npy")  # (1460, 40)


# ==============================================================
# Tangent Linear Matrix (to create matrix point)
# δx(t+dt) = M δx(t)
# ==============================================================
def tangent_linear_matrix(x, dt):
    # xもこれだけ変化するってことは誤差も同時にこれだけ変化するでしょって事
    N = len(x)
    M = np.zeros((N, N))

    for j in range(N):
        # すべての位置に対して、prev2, prev1, next, currの偏微分を計算
        prev2 = (j - 2) % N
        prev1 = (j - 1) % N
        next1 = (j + 1) % N

        M[j, prev2] = -x[prev1] * dt  # lorenzの式を偏微分していく
        M[j, prev1] = (x[next1] - x[prev2]) * dt
        M[j, j] = 1.0 - dt  # 誤差はそのまま引き継がれる -dtはブレーキで減った分
        # X(t+dt) = (X(t) + -X(x)*dt) = 1 - dt
        M[j, next1] = x[prev1] * dt
    # 線形にして、簡易的なモデルを作ってる、M[J,K]はK番目の変数がJ番目の変数の誤差にどう影響するか
    # ここには現在の誤差が入ってくるMε*Mεすると、次の時間での誤差共分散を出すことができる
    return M


# ==============================================================
# KF cycle
# ==============================================================
# Hは20*40, H.Tは40*20, Pb:40×40
def EKF_cycle(xa, Pa, y_obs, dt, F, H, R, inflation, const_Pf=None):
    # 1. tangent linear matrix (M)
    M = tangent_linear_matrix(xa, dt)
    # Mがなかったら何100パターンのxのペアをためさsないといけない
    # 2. prediction forecast state (xb)
    xb = rk4_step(xa, dt, F)
    # 3. prediction covariance (Pb)
    if const_Pf is not None:
        Pb = const_Pf  # 3D-Var: P^f を定数に固定（時間発展させない）
    else:
        Pb = M @ Pa @ M.T
        # Pa = εε　であり、Mεとすると誤差がどの様に変化するかわかる
        Pb = (1 + inflation) * Pb
        # 線形にすることで甘く見積もってしまうので少し大きくする
    # 4. Kalman Gain 観測値をどれぐらい信じるか
    S = H @ Pb @ H.T + R
    #  (20×40)@(40×40)@(40×20) + (20×20) = 20×20
    K = Pb @ H.T @ np.linalg.inv(S)
    #  (40×40)@(40×20)@(20×20)
    # 5. analysis
    xa_new = xb + K @ (y_obs - H @ xb)
    # y_obs - H @ xb: (20×1) - (20×40)@(40×1) = 20×1
    # (40×1) + (40×20)@(20×1) = 40×1
    # 6. analysis covariance
    I = np.eye(len(xa))
    Pa_new = (I - K @ H) @ Pb
    # PbからPaを作成する、観測の誤差も予測の誤差もいい感じに含まれてる
    return xa_new, Pa_new, xb, Pb, K


# ==============================================================
# main
# ==============================================================
H = np.eye(N)
R = np.eye(N)

inflation_values = [0.0, 0.03, 0.05, 0.055, 0.06, 0.08]
result = {}

for inflation in inflation_values:
    xa = obs[0].copy()
    Pa = 10 * np.eye(N)

    xb_save = []
    xa_save = []
    pb_save = []
    pa_save = []
    spread_a_list = []
    rmse_b_list = []
    rmse_a_list = []

    for t in range(1, truth.shape[0]):
        xa, Pa, xb, Pb, K = EKF_cycle(xa, Pa, obs[t], dt, F, H, R, inflation)

        xb_save.append(xb.copy())
        xa_save.append(xa.copy())
        pb_save.append(Pb.copy())
        pa_save.append(Pa.copy())
        spread_a = np.sqrt(np.trace(Pa) / N)  # 対角成分の平均を標準偏差みたいにする
        # 自身でズレてるかどうかの評価, RMSEは客観的な評価
        # 解析誤差共分散、自分で spread = np.sqrt(np.trace(Pa)/N)
        # infrationがないときは、spreadとRMSEのさが大きくなる。spreadが楽観的になるということ？
        spread_a_list.append(spread_a)

        rmse_b_ = np.sqrt(np.mean((xb - truth[t]) ** 2))
        rmse_b_list.append(rmse_b_)

        rmse_a_ = np.sqrt(np.mean((xa - truth[t]) ** 2))
        rmse_a_list.append(rmse_a_)

    result[inflation] = {
        "forecast": np.array(xb_save),
        "analysis": np.array(xa_save),
        "Pb": np.array(pb_save),
        "Pa": np.array(pa_save),
        "analysis_spread": np.array(spread_a_list),
        "mean_analysis_spread": np.mean(spread_a_list),
        "forecast_rmse": np.array(rmse_b_list),
        "analysis_rmse": np.array(rmse_a_list),
        "mean_forecast_rmse": np.mean(rmse_b_list),
        "mean_analysis_rmse": np.mean(rmse_a_list),
    }

# ==============================================================
# 3D-Var: 最適 inflation (0.055) の定常 P^f を定数として固定
# ==============================================================
OPTIMAL_INFLATION = 0.055
Pf_const = result[OPTIMAL_INFLATION]["Pb"][-1].copy()  # 定常状態の P^f

xa = obs[0].copy()
Pa = 10 * np.eye(N)

xb_save_3dv = []
xa_save_3dv = []
pa_save_3dv = []
spread_3dv = []
rmse_b_3dv = []
rmse_a_3dv = []

for t in range(1, truth.shape[0]):
    xa, Pa, xb, Pb, K = EKF_cycle(
        xa, Pa, obs[t], dt, F, H, R, inflation=0.0, const_Pf=Pf_const
    )
    xb_save_3dv.append(xb.copy())
    xa_save_3dv.append(xa.copy())
    pa_save_3dv.append(Pa.copy())
    spread_3dv.append(np.sqrt(np.trace(Pa) / N))
    rmse_b_3dv.append(np.sqrt(np.mean((xb - truth[t]) ** 2)))
    rmse_a_3dv.append(np.sqrt(np.mean((xa - truth[t]) ** 2)))

result["3dvar"] = {
    "forecast": np.array(xb_save_3dv),
    "analysis": np.array(xa_save_3dv),
    "Pa": np.array(pa_save_3dv),
    "analysis_spread": np.array(spread_3dv),
    "mean_analysis_spread": np.mean(spread_3dv),
    "forecast_rmse": np.array(rmse_b_3dv),
    "analysis_rmse": np.array(rmse_a_3dv),
    "mean_forecast_rmse": np.mean(rmse_b_3dv),
    "mean_analysis_rmse": np.mean(rmse_a_3dv),
}
print(
    f"[3D-Var] Analysis RMSE={result['3dvar']['mean_analysis_rmse']:.4f}  "
    f"Spread={result['3dvar']['mean_analysis_spread']:.4f}"
)

# ==============================================================
# 可視化
# ==============================================================
time_days = np.arange(1, truth.shape[0]) / 4.0
var = 0
start_day = 200
end_day = 300
mask = (time_days >= start_day) & (time_days <= end_day)

fig, axes = plt.subplots(
    len(inflation_values), 1, figsize=(10, 3 * len(inflation_values)), sharex=True
)
fig.suptitle(
    f"Truth, Observation, Forecast, Analysis  (x_{var}, day {start_day}–{end_day})",
    fontsize=13,
)

for ax, inflation in zip(axes, inflation_values):
    xb_save = result[inflation]["forecast"]
    xa_save = result[inflation]["analysis"]

    ax.plot(time_days[mask], truth[1:, var][mask], label="Truth", color="red")
    ax.scatter(
        time_days[mask], obs[1:, var][mask], label="Observation", s=5, alpha=0.25
    )
    ax.plot(time_days[mask], xb_save[:, var][mask], label="Forecast", color="steelblue")
    ax.plot(time_days[mask], xa_save[:, var][mask], label="Analysis", color="black")
    ax.set_ylabel(f"x_{var}")
    ax.set_title(f"inflation={inflation}")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(True)

axes[-1].set_xlabel("Time [days]")
plt.tight_layout()
plt.show()

colors = {
    0.0: "black",
    0.03: "blue",
    0.05: "green",
    0.055: "red",
    0.06: "purple",
    0.08: "brown",
}

plt.figure(figsize=(8, 4))
start_day = 1
end_day = 300
mask = (time_days >= start_day) & (time_days <= end_day)

for inflation in inflation_values:
    rmse = result[inflation]["analysis_rmse"]
    plt.plot(
        time_days[mask],
        rmse[mask],
        label=f"inflation={inflation:.3f}",
        color=colors[inflation],
        linewidth=0.7,
    )

plt.xlim(0, 300)
plt.ylim(0, 7)
plt.ylabel("ave RMSE")
plt.title("Analysis RMSE for different inflation values")
plt.legend()
plt.grid(True)
plt.show()

plt.figure(figsize=(8, 4))
mask = (time_days >= 250) & (time_days <= 300)

for inflation in inflation_values:
    rmse = result[inflation]["analysis_rmse"]
    plt.plot(
        time_days[mask],
        rmse[mask],
        label=f"inflation={inflation:.3f}",
        color=colors[inflation],
        linewidth=1,
    )

plt.xlim(250, 300)
plt.ylim(0, 1)
plt.xlabel("time (day)")
plt.ylabel("ave RMSE")
plt.title("Analysis RMSE (zoomed: day 250–300)")
plt.legend()
plt.grid(True)
plt.show()

plot_inflations = [0.0, 0.03, 0.055, 0.08]
plot_days = [1, 10, 300]

fig, axes = plt.subplots(len(plot_days), len(plot_inflations), figsize=(14, 17))

vmin = -0.3
vmax = 0.3

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

infls = [0.0, 0.03, 0.05, 0.055, 0.06, 0.08]
means = [result[i]["mean_analysis_rmse"] for i in infls]

plt.figure(figsize=(6, 4))
plt.plot(infls, means, marker="o")
plt.xlabel("Inflation δ")
plt.ylabel("Mean Analysis RMSE")
plt.title("Optimization of inflation parameter")
plt.grid(True)
plt.show()

# RMSE plot (最後の inflation の結果)
last_inflation = inflation_values[-1]
rmse_b_list = result[last_inflation]["forecast_rmse"]
rmse_a_list = result[last_inflation]["analysis_rmse"]
time_days_rmse = np.arange(len(rmse_a_list)) / 4.0

plt.figure(figsize=(12, 4))
plt.plot(time_days_rmse, rmse_b_list, label="Forecast RMSE")
plt.plot(time_days_rmse, rmse_a_list, label="Analysis RMSE")
plt.xlabel("Time [days]")
plt.ylabel("RMSE")
plt.title("EKF RMSE")
plt.legend()
plt.grid(True)
plt.show()

# ==============================================================
# RMSE vs sqrt(tr(P^a)) 比較
# EKF (optimal inflation) vs 3D-Var
# RMSE  = 真値との実際の誤差
# spread = フィルタ自身の誤差推定 sqrt(tr(Pa)/N)
# 一致していれば最適、spread << RMSE なら過信（発散の兆候）
# ==============================================================
opt_inf = OPTIMAL_INFLATION
rmse_ekf = result[opt_inf]["analysis_rmse"]
spread_ekf = result[opt_inf]["analysis_spread"]
rmse_3dv = result["3dvar"]["analysis_rmse"]
spread_3dv = result["3dvar"]["analysis_spread"]
t_ax = np.arange(len(rmse_ekf)) / 4.0

fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
fig.suptitle(
    "RMSE vs $\\sqrt{\\mathrm{tr}(P^a)/N}$ (実誤差 vs フィルタ自己推定)", fontsize=13
)

ax = axes[0]
ax.plot(t_ax, rmse_ekf, color="blue", lw=1.0, label=f"RMSE  (EKF δ={opt_inf})")
ax.plot(
    t_ax, spread_ekf, color="blue", lw=1.0, ls="--", label=f"Spread (EKF δ={opt_inf})"
)
ax.set_ylabel("Error")
ax.set_title(f"EKF (inflation={opt_inf})")
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)

ax = axes[1]
ax.plot(t_ax, rmse_3dv, color="tomato", lw=1.0, label="RMSE  (3D-Var)")
ax.plot(t_ax, spread_3dv, color="tomato", lw=1.0, ls="--", label="Spread (3D-Var)")
ax.set_ylabel("Error")
ax.set_xlabel("Time [days]")
ax.set_title("3D-Var (const $P^f$)")
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

print(
    f"[EKF δ={opt_inf}]  RMSE={result[opt_inf]['mean_analysis_rmse']:.4f}  "
    f"Spread={result[opt_inf]['mean_analysis_spread']:.4f}"
)
print(
    f"[3D-Var]         RMSE={result['3dvar']['mean_analysis_rmse']:.4f}  "
    f"Spread={result['3dvar']['mean_analysis_spread']:.4f}"
)

# ==============================================================
# 棒グラフ: inflation ごとの Mean RMSE vs Mean Spread
# ==============================================================
mean_rmse_a = [result[i]["mean_analysis_rmse"] for i in inflation_values]
mean_spread_a = [result[i]["mean_analysis_spread"] for i in inflation_values]

x_pos = np.arange(len(inflation_values))
width = 0.35

plt.figure(figsize=(8, 4))
plt.bar(x_pos - width / 2, mean_rmse_a, width, label="Mean Analysis RMSE")
plt.bar(x_pos + width / 2, mean_spread_a, width, label="Mean Spread sqrt(tr(Pa)/N)")
plt.xticks(x_pos, [str(i) for i in inflation_values])
plt.xlabel("Inflation δ")
plt.ylabel("Error size")
plt.title("Mean Analysis RMSE vs Mean Spread")
plt.ylim(0, 0.5)
plt.yticks(np.arange(0, 0.51, 0.1))
plt.legend()
plt.grid(axis="y")
plt.show()

# ==============================================================
# 最適 inflation の軌道プロット（前半 25日 / 年末付近）
# ==============================================================
xb_opt = result[opt_inf]["forecast"]
xa_opt = result[opt_inf]["analysis"]
time_days = np.arange(1, truth.shape[0]) / 4.0

# 前半 25日（100ステップ）
end = 100
plt.figure(figsize=(14, 4))
plt.plot(time_days[:end], truth[1 : end + 1, var], label="Truth", linewidth=2)
plt.scatter(time_days[:end], obs[1 : end + 1, var], label="Observation", s=8, alpha=0.5)
plt.plot(time_days[:end], xb_opt[:end, var], label="Forecast", linewidth=1.2)
plt.plot(time_days[:end], xa_opt[:end, var], label="Analysis", linewidth=1.5)
plt.xlabel("Time [days]")
plt.ylabel(f"x_{var}")
plt.title(f"First 25 days  (inflation={opt_inf})")
plt.legend()
plt.grid(True)
plt.show()

# 年末付近（300–355日）
start_day = 300
end_day = 355
mask = (time_days >= start_day) & (time_days <= end_day)

plt.figure(figsize=(14, 4))
plt.plot(time_days[mask], truth[1:, var][mask], label="Truth", linewidth=2)
plt.scatter(time_days[mask], obs[1:, var][mask], label="Observation", s=8, alpha=0.4)
plt.plot(time_days[mask], xb_opt[:, var][mask], label="Forecast", linewidth=1.0)
plt.plot(time_days[mask], xa_opt[:, var][mask], label="Analysis", linewidth=1.2)
plt.xlabel("Time [days]")
plt.ylabel(f"x_{var}")
plt.title(f"Day {start_day}–{end_day}  (inflation={opt_inf})")
plt.legend()
plt.grid(True)
plt.show()

print(
    "Forecast difference mean:",
    np.mean(np.abs(xb_opt[:, var][mask] - truth[1:, var][mask])),
)
print(
    "Analysis difference mean:",
    np.mean(np.abs(xa_opt[:, var][mask] - truth[1:, var][mask])),
)
print(
    "Observation difference mean:",
    np.mean(np.abs(obs[1:, var][mask] - truth[1:, var][mask])),
)
