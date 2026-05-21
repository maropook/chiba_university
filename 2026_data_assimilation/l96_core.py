"""
Lorenz 96 モデルの共有コアモジュール。
各タスクからインポートして使用する。
"""

import numpy as np

# y = x^2等も時間変化について考えることもしたかったら一つの式でxとtを使って表すのは難しい
# 時間によって変わる変化量を当て込める(それがないと一定の変化量)


def lorenz96(x, F):
    """Lorenz 96 モデルの右辺（時間微分）を返す。
    dX_j/dt = (X_{j+1} - X_{j-2}) * X_{j-1} - X_j + F
    """
    N = len(x)
    dxdt = np.zeros(N)
    for i in range(N):
        x_prev2 = x[(i - 2) % N]  # out of indexを防ぐ
        x_prev1 = x[(i - 1) % N]
        x_next1 = x[(i + 1) % N]
        dxdt[i] = (x_next1 - x_prev2) * x_prev1 - x[i] + F
        # (x_next1 - x_prev2) * x_prev1は全体で見たら0だからFが必要
        # (x_next1 - x_prev2) * x_prev1は
        # カオス的な挙動を生み出すための非線形項とx[i]で
        # Fは基準の変化量、カオスになりやすい
        # 現実の大気に似せて作った人工的なモデルで、「こういう式にしたらカオス的な挙動が出た」という感じ
        # 現在の風速をマイナスするのは、周り何もなかったら動かなくなる(逆の方向に加速度が動く)
    return dxdt


def rk4_step(x, dt, F):
    """4次ルンゲ・クッタ法による1ステップ更新。"""
    k1 = lorenz96(x, F)
    k2 = lorenz96(x + 0.5 * dt * k1, F)  # 中間地点を調べるため0.5
    k3 = lorenz96(x + 0.5 * dt * k2, F)  # 中間地点を調べるため0.5
    k4 = lorenz96(x + dt * k3, F)
    return x + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
    # 先に進めるが、dtを細かく切ったり


# 今の地点だけでなく、少し先の地点での変化速度も使って精度を上げる


def euler_step(x, dt, F):
    """前進オイラー法による1ステップ更新。"""
    return x + dt * lorenz96(x, F)


def rk2_step(x, dt, F):
    """2次ルンゲ・クッタ法（修正オイラー法）による1ステップ更新。"""
    k1 = lorenz96(x, F)
    k2 = lorenz96(x + dt * k1, F)
    return x + (dt / 2.0) * (k1 + k2)


def simulate(scheme, x0, dt, num_steps, F):
    """指定したスキームで L96 を num_steps ステップ積分する。"""
    N = len(x0)
    traj = np.zeros((num_steps + 1, N))
    traj[0] = x0.copy()
    x = x0.copy()
    # xは今の状態だけ記録しているが、trajは全履歴を積み重ねた行列である
    # step数状態を進めていく 初期値+stepの結果がtrajに入ってくる
    for i in range(num_steps):
        x = scheme(x, dt, F)
        traj[i + 1] = x
    return traj


def initial_condition(F, N, perturb_idx=19, perturb=0.01):
    """平衡状態 X_j = F からわずかにずらした初期条件を返す。"""
    x0 = F * np.ones(N)
    x0[perturb_idx] += perturb
    return x0  # 40の1次元配列であり、f,f,f,f,f,f+0.01, fというような物が入る


def simulate(scheme, x0, dt, num_steps, F):
    N = len(x0)
    traj = np.zeros(1 + steps, N)
    traj[0] = x0
    x = x0.copy()
    for i in range(num_steps):
        x = scheme(x, dt, F)
        traj[i + 1] = x
    return traj
