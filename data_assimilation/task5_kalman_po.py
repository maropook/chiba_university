"""
Task 5: Lorenz-96 モデルに対する EnKF-PO（Perturbed Observations 法）

[予報ステップ]
  X^b(:,i) = M(X^a(:,i))                        (全メンバーをモデル積分)
  Z^b       = (X^b - x^b_mean) / sqrt(m-1)      (偏差行列)
  Z^b      *= (1 + delta)                         (インフレーション)

[解析ステップ (PO法)]
  P^b_loc   = L * (Z^b Z^{b,T})                  (局所化 Schur 積)
  K         = P^b_loc H^T (H P^b_loc H^T + R)^{-1}  (カルマンゲイン)
  eps(:,i)  ~ N(0, R), 平均ゼロ補正              (観測摂動)
  X^a(:,i)  = X^b(:,i) + K (y^o + eps(:,i) - H X^b(:,i))

局所化: Gaspari-Cohn 5次多項式（周期境界）
"""

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

matplotlib.rcParams["font.family"] = "Hiragino Sans"


# ==============================================================
# Lorenz-96 モデル
# ==============================================================
def lorenz96(x, F=8.0):
    N = len(x)
    dxdt = np.zeros(N)
    for i in range(N):
        dxdt[i] = (x[(i + 1) % N] - x[(i - 2) % N]) * x[(i - 1) % N] - x[i] + F
    return dxdt


def rk4(x, dt, F=8.0):
    k1 = lorenz96(x, F)
    k2 = lorenz96(x + 0.5 * dt * k1, F)
    k3 = lorenz96(x + 0.5 * dt * k2, F)
    k4 = lorenz96(x + dt * k3, F)
    return x + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)


# ==============================================================
# データ生成（task4_2.py と同一設定）
# ==============================================================
N = 40
F = 8.0
dt = 0.01
SIX_HOURS = 0.05
save_every = int(SIX_HOURS / dt)      # 5 steps
steps_per_year = int(73.0 / dt)       # 7300 steps
n_obs = steps_per_year // save_every  # 1460 points

x = F * np.ones(N)
x[0] += 0.01

truth = np.zeros((n_obs, N))
step = 0
save_idx = 0
for t in range(steps_per_year * 2):
    x = rk4(x, dt, F)
    step += 1
    if step > steps_per_year and (step - steps_per_year) % save_every == 0:
        truth[save_idx] = x
        save_idx += 1

print(f"truth shape: {truth.shape}")

rng = np.random.Generator(np.random.MT19937(seed=42))
noise = rng.normal(0.0, 1.0, size=truth.shape)
obs = truth + noise
print(f"obs shape:   {obs.shape}")

H = np.eye(N)
R = np.eye(N)


# ==============================================================
# Gaspari-Cohn 局所化
# ==============================================================
def gaspari_cohn(z):
    """Gaspari-Cohn 5次多項式 (z = dist / c)"""
    if z < 0:
        raise ValueError("z must be non-negative")
    if z >= 2.0:
        return 0.0
    if z <= 1.0:
        return (-(z ** 5) / 4 + (z ** 4) / 2 + (5 * z ** 3) / 8
                - (5 * z ** 2) / 3 + 1.0)
    else:
        return ((z ** 5) / 12 - (z ** 4) / 2 + (5 * z ** 3) / 8
                + (5 * z ** 2) / 3 - 5 * z + 4 - (2 / 3) / z)


def build_localization_matrix(N, c):
    """N×N の Gaspari-Cohn 局所化行列（周期境界）"""
    L = np.zeros((N, N))
    for i in range(N):
        for j in range(N):
            dist = min(abs(i - j), N - abs(i - j))
            L[i, j] = gaspari_cohn(dist / c)
    return L


# ==============================================================
# EnKF-PO サイクル
# ==============================================================
def EnKF_PO_cycle(Xb, y_obs, H, R, L, inflation, rng_obj):
    """
    Xb      : (N, m) 予報アンサンブル
    y_obs   : (p,)  観測ベクトル
    L       : (N, N) 局所化行列
    returns : Xa (N, m), xb_mean (N,), Pb_samp (N, N)
    """
    m = Xb.shape[1]
    p = y_obs.shape[0]

    xb_mean = Xb.mean(axis=1)
    Zb = (Xb - xb_mean[:, None]) / np.sqrt(m - 1)
    Zb = Zb * (1.0 + inflation)

    Pb_samp = Zb @ Zb.T
    Pb_loc = L * Pb_samp

    PHT = Pb_loc @ H.T
    S = H @ Pb_loc @ H.T + R
    K = PHT @ np.linalg.inv(S)

    eps = rng_obj.multivariate_normal(np.zeros(p), R, size=m).T
    eps -= eps.mean(axis=1, keepdims=True)

    innov = y_obs[:, None] + eps - H @ Xb
    Xa = Xb + K @ innov

    return Xa, xb_mean, Pb_samp


# ==============================================================
# EnKF-PO メインループ
# ==============================================================
def run_enkf_po(m=20, inflation=0.05, L=None):
    """
    m         : アンサンブルメンバー数
    inflation : 偏差インフレーション率 delta
    L         : (N,N) 局所化行列。None のとき c=5 の GC 行列を使用
    """
    rng_ens = np.random.Generator(np.random.MT19937(seed=0))
    if L is None:
        L = build_localization_matrix(N, 5.0)

    Xa = truth[0][:, None] + rng_ens.normal(0.0, 1.0, size=(N, m))

    rmse_b_list, rmse_a_list, spread_list = [], [], []

    for t in range(1, n_obs):
        Xb = np.zeros_like(Xa)
        for i in range(m):
            xi = Xa[:, i].copy()
            for _ in range(save_every):
                xi = rk4(xi, dt, F)
            Xb[:, i] = xi

        Xa, xb_mean, Pb_samp = EnKF_PO_cycle(
            Xb, obs[t], H, R, L, inflation, rng_ens
        )
        xa_mean = Xa.mean(axis=1)

        rmse_b_list.append(np.sqrt(np.mean((xb_mean - truth[t]) ** 2)))
        rmse_a_list.append(np.sqrt(np.mean((xa_mean - truth[t]) ** 2)))
        spread_list.append(np.sqrt(np.trace(Pb_samp) / N))

    return {
        "forecast_rmse":      np.array(rmse_b_list),
        "analysis_rmse":      np.array(rmse_a_list),
        "spread":             np.array(spread_list),
        "mean_forecast_rmse": np.mean(rmse_b_list),
        "mean_analysis_rmse": np.mean(rmse_a_list),
        "mean_spread":        np.mean(spread_list),
    }


# ==============================================================
# EKF 関数（task4_2.py と同一ロジック）
# ==============================================================
def tangent_linear_matrix(x, dt):
    n = len(x)
    M = np.zeros((n, n))
    for j in range(n):
        p2 = (j - 2) % n
        p1 = (j - 1) % n
        n1 = (j + 1) % n
        M[j, p2] = -x[p1] * dt
        M[j, p1] = (x[n1] - x[p2]) * dt
        M[j, j]  = 1.0 - dt
        M[j, n1] = x[p1] * dt
    return M


def run_ekf(inflation=0.05):
    dt_ekf = SIX_HOURS  # 0.05 MTU（6時間を1ステップで積分）
    xa = obs[0].copy()
    Pa = 10 * np.eye(N)
    rmse_b_list, rmse_a_list = [], []

    for t in range(1, n_obs):
        M = tangent_linear_matrix(xa, dt_ekf)

        xb = rk4(xa, dt_ekf, F)  # 1ステップで6時間積分

        Pb = (1 + inflation) * (M @ Pa @ M.T)
        S = H @ Pb @ H.T + R
        K = Pb @ H.T @ np.linalg.inv(S)

        xa_new = xb + K @ (obs[t] - H @ xb)
        Pa_new = (np.eye(N) - K @ H) @ Pb

        rmse_b_list.append(np.sqrt(np.mean((xb - truth[t]) ** 2)))
        rmse_a_list.append(np.sqrt(np.mean((xa_new - truth[t]) ** 2)))

        xa = xa_new
        Pa = Pa_new

    return {
        "forecast_rmse":      np.array(rmse_b_list),
        "analysis_rmse":      np.array(rmse_a_list),
        "mean_forecast_rmse": np.mean(rmse_b_list),
        "mean_analysis_rmse": np.mean(rmse_a_list),
    }


# ==============================================================
# 実験パラメータ（EKF と EnKF-PO で共通）
# ==============================================================
m = 20
inflation = 0.05

time_days = np.arange(1, n_obs) / 4.0
mask = (time_days >= 1) & (time_days <= 300)
obs_rmse = float(np.sqrt(np.mean((obs[1:] - truth[1:]) ** 2)))


# ==============================================================
# 比較1: EKF vs EnKF-PO（同一 inflation）
# ==============================================================
print("--- 比較1: EKF vs EnKF-PO ---")
print(f"共通 inflation = {inflation},  EnKF-PO m = {m}")

ekf_result  = run_ekf(inflation=inflation)
enkf_result = run_enkf_po(m=m, inflation=inflation)  # L=None → c=5

print(f"EKF      Analysis RMSE = {ekf_result['mean_analysis_rmse']:.4f}")
print(f"EnKF-PO  Analysis RMSE = {enkf_result['mean_analysis_rmse']:.4f}")
print(f"Observation      RMSE  = {obs_rmse:.4f}")

# C1-1: Analysis RMSE 時系列
plt.figure(figsize=(10, 4))
plt.plot(time_days[mask], ekf_result["analysis_rmse"][mask],
         label=f"EKF  (inflation={inflation})", color="steelblue", linewidth=0.9)
plt.plot(time_days[mask], enkf_result["analysis_rmse"][mask],
         label=f"EnKF-PO  (inflation={inflation}, m={m})", color="tomato", linewidth=0.9)
plt.xlim(0, 300)
plt.ylim(0, 5)
plt.xlabel("Time [days]")
plt.ylabel("Analysis RMSE")
plt.title(f"比較1: EKF vs EnKF-PO  (inflation={inflation})")
plt.legend()
plt.grid(True)
plt.show()

# C1-2: Mean Analysis RMSE 棒グラフ
labels_c1 = [f"EKF\n(inflation={inflation})",
             f"EnKF-PO\n(inflation={inflation}, m={m})"]
vals_c1 = [ekf_result["mean_analysis_rmse"],
           enkf_result["mean_analysis_rmse"]]
plt.figure(figsize=(4, 4))
bars = plt.bar(labels_c1, vals_c1, color=["steelblue", "tomato"])
for bar, v in zip(bars, vals_c1):
    plt.text(bar.get_x() + bar.get_width() / 2, v + 0.01, f"{v:.3f}",
             ha="center", va="bottom", fontsize=10)
plt.ylabel("Mean Analysis RMSE")
plt.title("比較1: KF vs EnKF-PO 精度比較")
plt.grid(axis="y")
plt.tight_layout()
plt.show()


# ==============================================================
# 比較2: 局所化あり vs なし
# ==============================================================
print("\n--- 比較2: 局所化効果 ---")

loc_sigmas = [1, 3, 10, 40]
loc_colors_sigma = {1: "purple", 3: "green", 10: "orange", 40: "brown"}

L_none = np.ones((N, N))
print("  局所化なし ...")
res_no_loc = run_enkf_po(m=m, inflation=inflation, L=L_none)
print(f"    Mean Analysis RMSE = {res_no_loc['mean_analysis_rmse']:.4f}")

res_sigma = {}
for sigma in loc_sigmas:
    print(f"  σ={sigma} ...")
    L_s = build_localization_matrix(N, sigma)
    res_sigma[sigma] = run_enkf_po(m=m, inflation=inflation, L=L_s)
    print(f"    Mean Analysis RMSE = {res_sigma[sigma]['mean_analysis_rmse']:.4f}")

# C2-1: GC 局所化行列ヒートマップ（σ=1,3,10,40）
fig, axes = plt.subplots(1, 4, figsize=(14, 4))
for ax, sigma in zip(axes, loc_sigmas):
    L_s = build_localization_matrix(N, sigma)
    im = ax.imshow(L_s, cmap="viridis", vmin=0, vmax=1, origin="upper")
    ax.set_title(f"σ = {sigma}")
    ax.set_xlabel("変数インデックス")
    ax.set_ylabel("変数インデックス")
fig.colorbar(im, ax=axes[-1], shrink=0.85)
plt.suptitle("Gaspari-Cohn 局所化行列（Lorenz-96 N=40）", fontsize=12)
plt.tight_layout()
plt.show()

# C2-2: Analysis RMSE 時系列（σ別 + 局所化なし + EKF参考）
plt.figure(figsize=(10, 4))
plt.plot(time_days[mask], res_no_loc["analysis_rmse"][mask],
         label="局所化なし", color="black", linewidth=0.9)
for sigma in loc_sigmas:
    plt.plot(time_days[mask], res_sigma[sigma]["analysis_rmse"][mask],
             label=f"σ={sigma}", color=loc_colors_sigma[sigma], linewidth=0.9)
plt.plot(time_days[mask], ekf_result["analysis_rmse"][mask],
         label="EKF  (参考)", color="steelblue", linewidth=0.9, linestyle="--")
plt.xlim(0, 300)
plt.xlabel("Time [days]")
plt.ylabel("Analysis RMSE")
plt.title(f"比較2: 局所化半径 σ の効果  (inflation={inflation}, m={m})")
plt.legend()
plt.grid(True)
plt.show()

# C2-3: Mean RMSE 棒グラフ（σ別 + 局所化なし + EKF参考）
labels_c2 = ["局所化\nなし"] + [f"σ={s}" for s in loc_sigmas] + ["EKF\n(参考)"]
vals_c2   = ([res_no_loc["mean_analysis_rmse"]]
             + [res_sigma[s]["mean_analysis_rmse"] for s in loc_sigmas]
             + [ekf_result["mean_analysis_rmse"]])
bar_colors = (["black"]
              + [loc_colors_sigma[s] for s in loc_sigmas]
              + ["steelblue"])
plt.figure(figsize=(7, 4))
bars = plt.bar(labels_c2, vals_c2, color=bar_colors)
for bar, v in zip(bars, vals_c2):
    plt.text(bar.get_x() + bar.get_width() / 2, v + 0.01, f"{v:.3f}",
             ha="center", va="bottom", fontsize=9)
plt.ylabel("Mean Analysis RMSE")
plt.title(f"比較2: 局所化半径 σ による RMSE 比較  (inflation={inflation}, m={m})")
plt.grid(axis="y")
plt.tight_layout()
plt.show()


# ==============================================================
# 比較3: アンサンブルサイズ m の影響
# ==============================================================
print("\n--- 比較3: アンサンブルサイズ m の影響 ---")

ensemble_sizes = [10, 100, 180, 500]
ens_colors = {10: "purple", 100: "green", 180: "orange", 500: "tomato"}

res_ens = {}
for m_val in ensemble_sizes:
    print(f"  m={m_val} ...")
    res_ens[m_val] = run_enkf_po(m=m_val, inflation=inflation)
    print(f"    Mean Analysis RMSE = {res_ens[m_val]['mean_analysis_rmse']:.4f}")

# C3-1: Analysis RMSE 時系列（m 別）
plt.figure(figsize=(10, 4))
for m_val in ensemble_sizes:
    plt.plot(time_days[mask], res_ens[m_val]["analysis_rmse"][mask],
             label=f"m={m_val}", color=ens_colors[m_val], linewidth=0.9)
plt.plot(time_days[mask], ekf_result["analysis_rmse"][mask],
         label="EKF  (参考)", color="steelblue", linewidth=0.9, linestyle="--")
plt.xlim(0, 300)
plt.xlabel("Time [days]")
plt.ylabel("Analysis RMSE")
plt.title(f"比較3: アンサンブルサイズ m の影響  (inflation={inflation}, σ=5)")
plt.legend()
plt.grid(True)
plt.show()

# C3-2: Mean RMSE 棒グラフ（m 別）
labels_c3 = [f"m={v}" for v in ensemble_sizes] + ["EKF\n(参考)"]
vals_c3   = [res_ens[v]["mean_analysis_rmse"] for v in ensemble_sizes] + [ekf_result["mean_analysis_rmse"]]
bar_colors_c3 = [ens_colors[v] for v in ensemble_sizes] + ["steelblue"]

plt.figure(figsize=(6, 4))
bars = plt.bar(labels_c3, vals_c3, color=bar_colors_c3)
for bar, v in zip(bars, vals_c3):
    plt.text(bar.get_x() + bar.get_width() / 2, v + 0.005, f"{v:.3f}",
             ha="center", va="bottom", fontsize=9)
plt.ylabel("Mean Analysis RMSE")
plt.title(f"比較3: m による RMSE 比較  (inflation={inflation}, σ=5)")
plt.grid(axis="y")
plt.tight_layout()
plt.show()
