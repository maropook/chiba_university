"""
========================================================
 データ同化 Task 1~4  確認テスト（第1回）
 答えを # ANS: の後に書いてください
 コード穴埋めは ??? を正しいコードに書き換えてください
========================================================
"""

import numpy as np

# ======================================================
# 【Task 1】 Lorenz 96 モデルと数値積分
# ======================================================

# Q1. L96 モデルの方程式を言葉で説明してください
# ANS: 大気のカオスな様子を表している、
# 例えばその地点の風速を表しており、
# 周辺の風速の差を考慮したり現地の強さ,そこからどう収まる方向に動くかも表すが、
# Fにより固定で変化量がある


# Q2. F=8 のとき何が起きるか？
# ANS: カオスが発生する, すべての位置の値を二乗して合計した値が一定値にならない


# Q3. RK4 はオイラー法と比べて何が違うか？
# ANS: 複数の点の傾きをバランスよく取り入れて値を予測するので制度が高い


# Q4. RK4 の更新式を書いてください（k1~k4 を使って）
# ANS:
#   k1 = Lorenz96(x, F)
#   k2 = Lorenz96(x + k1*0.5*dt, F)
#   k3 = Lorenz96(x + k2*0.5*dt, F)
#   k4 = Lorenz96(x + k3*dt, F)
#   x_new = x + (dt/6)*(k1 + k2*2 + k3*2 + k4)


# Q5. 以下の RK4 コードの ??? を埋めてください
def lorenz96(x, F=8.0):
    N = len(x)
    dxdt = np.zeros(N)
    for i in range(N):
        dxdt[i] = (x[(i + 1) % N] - x[(i - 2) % N]) * x[(i - 1) % N] - x[i] + F
    return dxdt


def rk4(x, dt, F=8.0):
    k1 = lorenz96(x, F)
    k2 = lorenz96(x + k1 * 0.5 * dt, F)  # Q5a
    k3 = lorenz96(x + k2 * 0.5 * dt, F)  # Q5b
    k4 = lorenz96(x + k3 * dt, F)  # Q5c
    return x + (dt / 6) * (k1 + 2 * k2 + 2 * k3 + k4)  # Q5d, Q5e, Q5f


# ======================================================
# 【Task 2】 誤差倍増時間
# ======================================================

# Q6. 誤差倍増時間とは何か？
# ANS: 誤差を加えたものと加えないもオンでlorenzモデルを走らせて予測する。誤差が初期の誤差の2倍となる時間


# Q7. データ同化コミュニティで誤差を評価する指標は？
# ANS: RMSE


# Q8. RMSE の計算式を書いてください
# ANS:  squrt(1/N * sum (true - false)**2)


# Q9. 0.2 MTU = 1日 とする妥当性をどのように確認するか？
# ANS: 誤差倍増時間=2日=xMTUと変換する


# Q10. 以下の誤差倍増時間を求めるコードの ??? を埋めてください
def error_doubling_time(mean_rmse, t_values):
    initial_rmse = mean_rmse[0]
    idx_double = np.where(mean_rmse >= 2 * initial_rmse)[0][0]  # Q10a, Q10b
    return t_values[idx_double]


# ======================================================
# 【Task 3】 真値生成・観測データ
# ======================================================

# Q11. スピンアップとは何のために行うか？
# ANS: アトラクターに乗るまでは捨てることで確実に特徴量が出るような環境を作る


# Q12. 観測データはどのように作るか？
# ANS: 真値データに標準正規分布に従う誤差を加える


# Q13. 以下の観測データ生成コードの ??? を埋めてください
def make_obs(truth, seed=42):
    rng = np.random.default_rng(seed=seed)  # Q13a: 乱数生成器
    noise = rng.standard_normal(size=truth.shape)  # Q13b: N(0,1) ノイズ生成
    obs = truth + noise  # Q13c: 観測データ
    return obs


# ======================================================
# 【Task 4】 カルマンフィルタ
# ======================================================

# Q14. カルマンフィルタの予報ステップの式を3つ書いてください
# ANS:
#   xb = M(xb)
#   Pb = M @ Pa @ M.T
#   Pb =  （1 + inflation） * Pb


# Q15. カルマンフィルタの解析ステップの式を3つ書いてください
# ANS:
#   K  = Pb @ H.T @ np.lingia.inv(H @ Pb @ H.T + R)
#   xa = xb + K (y_obs - H @ xb)
#   Pa = (I - K@H)@ Pb


# Q16. カルマンゲイン K において H と H.T がある理由を説明してください
# ANS: 観測の点数とモデルが予測する点数が違くその場合は行列の大きさが違うので揃える必要がある


# Q17. 共分散インフレーションが必要な理由は？
# ANS: モデルを線形にして誤差を計算するため、誤差が実際よりも小さくなってしまうから


# Q18. 3D-Var と KF の違いを説明してください
# ANS: 背景誤差分散を定数とするか、毎回計算していくか


# Q19. RMSE と sqrt(tr(Pa)/N) を比較する意味は？
# ANS: PMSEは予測値と答えの差、 sqrtはフィルタが予測した誤差であるため
# その差が小さい場合がフィルタが正しく予測できていると言える


# Q20. 以下の EKF サイクルの ??? を埋めてください
def EKF_cycle(xa, Pa, y_obs, dt, F, H, R, inflation):
    N = len(xa)
    M = tangent_linear_matrix(xa, dt)

    xb = rk4(xa, dt, F)

    Pb = M @ Pa @ M.T  # Q20a
    Pb = (1 + inflation) * Pb  # Q20b

    S = H @ Pb @ H.T + R  # Q20c
    K = Pb @ H.T @ np.linalg.inv(S)  # Q20d

    xa_new = xb + K @ (y_obs - H @ xb)  # Q20e
    Pa_new = (np.eye(N) - K @ H) @ Pb  # Q20f

    return xa_new, Pa_new, xb, Pb


# Q21. H = np.eye(N) のとき、H が実質意味をなさない理由は？
# ANS: 観測空間とモデルが出す空間の大きさが同じであり行列のサイズを変換する必要がない


# Q22. TLM の M[j,j] = 1 - dt となる理由を説明してください
# ANS: 変化率は M - M*dt = (1-dt)Mと逆算できる


# Q23. inflation=0 のとき最初は収束するのに、その後真値を追えなくなり、
#      また収束するように見えるのはなぜか？
# ANS: 収束すると言うか、値を正しく予測できない。誤差がないと思いこんでしまい、あまり観測値を取り込まなくなってしまうから


# Q24. 以下の TLM の ??? を埋めてください（L96 の偏微分）
def tangent_linear_matrix(x, dt):
    N = len(x)
    M = np.zeros((N, N))
    for j in range(N):
        # dxdt = (next1 - prev2) * prev1 - current  + F
        prev2 = (j - 2) % N
        prev1 = (j - 1) % N
        next1 = (j + 1) % N
        M[j, prev2] = -x[prev1] * dt  # Q24a: ∂f_j/∂X_{j-2} × dt
        M[j, prev1] = x[next1] - x[prev2] * dt  # Q24b: ∂f_j/∂X_{j-1} × dt
        M[j, j] = 1 - dt  # Q24c: 1 + ∂f_j/∂X_j × dt
        M[j, next1] = x[prev1] * dt  # Q24d: ∂f_j/∂X_{j+1} × dt
    return M
