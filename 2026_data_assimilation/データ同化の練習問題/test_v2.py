"""
========================================================
 データ同化 Task 1~4  確認テスト（第2回）
 答えを # ANS: の後に書いてください
 コード穴埋めは ??? を正しいコードに書き換えてください
========================================================
"""

import numpy as np

# ======================================================
# 【Task 1】 Lorenz 96 モデルと数値積分
# ======================================================

# Q1. L96 の方程式を数式で書いてください
# ANS: 


# Q2. F の値を変えると何が変わるか？F=8 のとき何が起きるか？
# ANS:


# Q3. オイラー法の更新式を書いてください
# ANS:


# Q4. オイラー法と比べた RK4 の利点と欠点を書いてください
# ANS:
#   利点:
#   欠点:


# Q5. 以下の lorenz96 関数の ??? を埋めてください
def lorenz96(x, F=8.0):
    N = len(x)
    dxdt = np.zeros(N)
    for i in range(N):
        dxdt[i] = (x[???] - x[???]) * x[???] - x[i] + F
        #              Q5a       Q5b       Q5c
    return dxdt


# Q6. 以下の RK4 関数の ??? を埋めてください
def rk4(x, dt, F=8.0):
    k1 = lorenz96(x, F)
    k2 = lorenz96(???, F)                          # Q6a
    k3 = lorenz96(???, F)                          # Q6b
    k4 = lorenz96(???, F)                          # Q6c
    return x + (??? / 6.0) * (k1 + ???*k2 + ???*k3 + k4)  # Q6d, Q6e, Q6f


# ======================================================
# 【Task 2】 誤差倍増時間
# ======================================================

# Q7. 誤差倍増時間の定義を書いてください
# ANS:


# Q8. RMSE の計算式をコードで書いてください（x_true, x_pred を使って）
# ANS:
#   rmse =


# Q9. 0.2 MTU = 1日 の妥当性をどのように確認するか？
#     現実大気の誤差倍増時間も含めて答えてください
# ANS:


# Q10. アンサンブル対を使って RMSE を計算する理由は何か？
# ANS:


# Q11. 以下のコードの ??? を埋めてください
#      （base と pert の2軌道を積分して RMSE を記録する）
def compute_error_growth(x_base, x_pert, dt, F, num_steps):
    rmse_list = []
    for i in range(num_steps):
        rmse = np.sqrt(np.mean((??? - ???) ** 2))  # Q11a, Q11b
        rmse_list.append(rmse)
        x_base = rk4(x_base, dt, F)
        x_pert = rk4(???, dt, F)                   # Q11c
    return np.array(rmse_list)


# ======================================================
# 【Task 3】 真値生成・観測データ
# ======================================================

# Q12. スピンアップとは何か？なぜ必要か？
# ANS:


# Q13. 観測誤差の分布は何を仮定しているか？その式は？
# ANS:


# Q14. 真値と観測データのサイズはなぜ同じなのか？
# ANS:


# Q15. 以下の真値・観測データ生成コードの ??? を埋めてください
def generate_truth_obs(N=40, F=8.0, dt=0.05, seed=42):
    steps_per_year = int(73.0 / dt)

    x = F * np.ones(N)
    x[N // 4] += 0.01

    # スピンアップ
    for _ in range(???):          # Q15a: スピンアップのステップ数
        x = rk4(x, dt, F)

    # 真値保存
    truth = np.zeros((steps_per_year, N))
    for t in range(steps_per_year):
        truth[t] = x
        x = rk4(x, dt, F)

    # 観測データ
    rng = np.random.???(seed=seed)          # Q15b: 乱数生成器
    noise = rng.???(size=truth.shape)       # Q15c: N(0,1) ノイズ
    obs = ???                               # Q15d: 観測データ

    return truth, obs


# ======================================================
# 【Task 4】 カルマンフィルタ
# ======================================================

# Q16. 以下の各変数が何を意味するか答えてください
# xa  : ANS:
# xb  : ANS:
# Pa  : ANS:
# Pb  : ANS:
# K   : ANS:
# H   : ANS:
# R   : ANS:


# Q17. カルマンフィルタの予報・解析ステップの式を全て書いてください
# ANS:
#   [予報]
#   xb =
#   Pb =
#   Pb =  （インフレーション後）
#
#   [解析]
#   K  =
#   xa =
#   Pa =


# Q18. H=I（単位行列）のとき K の式はどう簡略化されるか？
# ANS:


# Q19. 以下の EKF サイクルの ??? を全て埋めてください
def EKF_cycle(xa, Pa, y_obs, dt, F, H, R, inflation):
    N = len(xa)
    M = tangent_linear_matrix(xa, dt)

    # 予報
    xb = rk4(xa, dt, F)
    Pb = M @ ??? @ M.T                      # Q19a
    Pb = (1 + ???) * Pb                     # Q19b

    # カルマンゲイン
    S = H @ Pb @ ??? + R                    # Q19c
    K = Pb @ ??? @ np.linalg.inv(S)         # Q19d

    # 解析
    xa_new = xb + K @ (??? - H @ xb)        # Q19e
    Pa_new = (np.eye(N) - K @ ???) @ Pb     # Q19f

    return xa_new, Pa_new, xb, Pb


# Q20. 以下の TLM の ??? を埋めてください（L96 の偏微分）
def tangent_linear_matrix(x, dt):
    N = len(x)
    M = np.zeros((N, N))
    for j in range(N):
        prev2 = (j - 2) % N
        prev1 = (j - 1) % N
        next1 = (j + 1) % N
        M[j, prev2] = ???                   # Q20a: ∂f_j/∂X_{j-2} * dt
        M[j, prev1] = ???                   # Q20b: ∂f_j/∂X_{j-1} * dt
        M[j, j]     = ???                   # Q20c: 1 + ∂f_j/∂X_j * dt
        M[j, next1] = ???                   # Q20d: ∂f_j/∂X_{j+1} * dt
    return M


# Q21. TLM がオイラー近似である理由と、その影響を答えてください
# ANS:


# Q22. 共分散インフレーションが必要な理由を、Pb・K・xa の流れで説明してください
# ANS:


# Q23. 3D-Var と KF を比較して、それぞれの利点・欠点を答えてください
# ANS:
#   3D-Var 利点:
#   3D-Var 欠点:
#   KF    利点:
#   KF    欠点:


# Q24. RMSE と sqrt(tr(Pa)/N) を比較したとき
#      以下の各状況はフィルタにとって何を意味するか？
#
#   RMSE ≈ sqrt(tr(Pa)/N) : ANS:
#   RMSE >> sqrt(tr(Pa)/N) : ANS:
#   RMSE << sqrt(tr(Pa)/N) : ANS:


# Q25. inflation=0 のとき、発散→再収束のように見える現象を
#      Pa・K・RMSE の変化を使って説明してください
# ANS:
