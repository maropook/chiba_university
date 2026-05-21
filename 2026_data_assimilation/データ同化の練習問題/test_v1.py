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
# ANS:


# Q2. F=8 のとき何が起きるか？
# ANS:


# Q3. RK4 はオイラー法と比べて何が違うか？
# ANS:


# Q4. RK4 の更新式を書いてください（k1~k4 を使って）
# ANS:
#   k1 =
#   k2 =
#   k3 =
#   k4 =
#   x_new =


# Q5. 以下の RK4 コードの ??? を埋めてください
def lorenz96(x, F=8.0):
    N = len(x)
    dxdt = np.zeros(N)
    for i in range(N):
        dxdt[i] = (x[(i+1)%N] - x[(i-2)%N]) * x[(i-1)%N] - x[i] + F
    return dxdt

def rk4(x, dt, F=8.0):
    k1 = lorenz96(x, F)
    k2 = lorenz96(???, F)                              # Q5a
    k3 = lorenz96(???, F)                              # Q5b
    k4 = lorenz96(???, F)                              # Q5c
    return x + (dt / ???) * (k1 + ???*k2 + ???*k3 + k4)  # Q5d, Q5e, Q5f


# ======================================================
# 【Task 2】 誤差倍増時間
# ======================================================

# Q6. 誤差倍増時間とは何か？
# ANS:


# Q7. データ同化コミュニティで誤差を評価する指標は？
# ANS:


# Q8. RMSE の計算式を書いてください
# ANS:


# Q9. 0.2 MTU = 1日 とする妥当性をどのように確認するか？
# ANS:


# Q10. 以下の誤差倍増時間を求めるコードの ??? を埋めてください
def error_doubling_time(mean_rmse, t_values):
    initial_rmse = mean_rmse[0]
    idx_double = np.where(??? >= ??? * initial_rmse)[0][0]  # Q10a, Q10b
    return t_values[idx_double]


# ======================================================
# 【Task 3】 真値生成・観測データ
# ======================================================

# Q11. スピンアップとは何のために行うか？
# ANS:


# Q12. 観測データはどのように作るか？
# ANS:


# Q13. 以下の観測データ生成コードの ??? を埋めてください
def make_obs(truth, seed=42):
    rng = np.random.???(seed=seed)          # Q13a: 乱数生成器
    noise = rng.???(size=truth.shape)       # Q13b: N(0,1) ノイズ生成
    obs = ???                               # Q13c: 観測データ
    return obs


# ======================================================
# 【Task 4】 カルマンフィルタ
# ======================================================

# Q14. カルマンフィルタの予報ステップの式を3つ書いてください
# ANS:
#   xb =
#   Pb =
#   Pb =  （インフレーション後）


# Q15. カルマンフィルタの解析ステップの式を3つ書いてください
# ANS:
#   K  =
#   xa =
#   Pa =


# Q16. カルマンゲイン K において H と H.T がある理由を説明してください
# ANS:


# Q17. 共分散インフレーションが必要な理由は？
# ANS:


# Q18. 3D-Var と KF の違いを説明してください
# ANS:


# Q19. RMSE と sqrt(tr(Pa)/N) を比較する意味は？
# ANS:


# Q20. 以下の EKF サイクルの ??? を埋めてください
def EKF_cycle(xa, Pa, y_obs, dt, F, H, R, inflation):
    N = len(xa)
    M = tangent_linear_matrix(xa, dt)

    xb = rk4(xa, dt, F)

    Pb = M @ ??? @ M.T                      # Q20a
    Pb = (??? + inflation) * Pb             # Q20b

    S = H @ Pb @ ??? + R                    # Q20c
    K = Pb @ ??? @ np.linalg.inv(S)         # Q20d

    xa_new = xb + K @ (??? - H @ xb)        # Q20e
    Pa_new = (np.eye(N) - K @ ???) @ Pb     # Q20f

    return xa_new, Pa_new, xb, Pb


# Q21. H = np.eye(N) のとき、H が実質意味をなさない理由は？
# ANS:


# Q22. TLM の M[j,j] = 1 - dt となる理由を説明してください
# ANS:


# Q23. inflation=0 のとき最初は収束するのに、その後真値を追えなくなり、
#      また収束するように見えるのはなぜか？
# ANS:


# Q24. 以下の TLM の ??? を埋めてください（L96 の偏微分）
def tangent_linear_matrix(x, dt):
    N = len(x)
    M = np.zeros((N, N))
    for j in range(N):
        prev2 = (j - 2) % N
        prev1 = (j - 1) % N
        next1 = (j + 1) % N
        M[j, prev2] = ???                   # Q24a: ∂f_j/∂X_{j-2} × dt
        M[j, prev1] = ???                   # Q24b: ∂f_j/∂X_{j-1} × dt
        M[j, j]     = ???                   # Q24c: 1 + ∂f_j/∂X_j × dt
        M[j, next1] = ???                   # Q24d: ∂f_j/∂X_{j+1} × dt
    return M
