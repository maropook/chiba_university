import numpy as np


def simplex(c, A, b, sense="max", verbose=False):
    """
    タブロー単体法による線形計画問題ソルバー

    対象クラス: maximize c^T x  s.t. Ax <= b, x >= 0, b >= 0
    (sense="min" の場合は目的関数の符号を反転して最大化に帰着)

    Parameters
    ----------
    c : array-like, shape (n,)
    A : array-like, shape (m, n)
    b : array-like, shape (m,)  b >= 0 を仮定
    sense : "max" or "min"
    verbose : bool  True なら各反復のタブローを出力

    Returns
    -------
    dict with keys:
        status         : "optimal" or "unbounded"
        x              : 主問題の最適解 (n,)
        objective      : 最適値
        y              : 双対最適解 (m,)  最終タブローz行から読み取り
        num_iterations : ピボット回数
        basis          : 最終基底の変数添字リスト
        slack          : 各制約のスラック値 (m,)
    """
    c = np.array(c, dtype=float)
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)

    m, n = A.shape
    EPS = 1e-9

    # --- タブロー構築 ---
    # 行: [z行] + [制約m行]
    # 列: [x_1..x_n | s_1..s_m | RHS]
    T = np.zeros((m + 1, n + m + 1))

    # 制約行: Ax + Is = b
    T[1:, :n] = A
    T[1:, n:n + m] = np.eye(m)
    T[1:, -1] = b

    # z行: max → z - c^T x = 0  ⟹ z行係数は -c
    #       min → 符号反転して max に帰着
    if sense == "max":
        T[0, :n] = -c
    else:
        T[0, :n] = c

    # 初期基底: スラック変数
    basis = list(range(n, n + m))
    num_iterations = 0

    def var_name(idx):
        return f"x{idx + 1}" if idx < n else f"s{idx - n + 1}"

    def print_tableau(iteration):
        col_labels = [f"x{i+1}" for i in range(n)] + \
                     [f"s{i+1}" for i in range(m)] + ["RHS"]
        row_labels = ["z"] + [var_name(b) for b in basis]
        col_w = 10
        header = f"{'':>6} | " + " | ".join(f"{v:>{col_w}}" for v in col_labels)
        print(f"\n=== Iteration {iteration} ===")
        print(header)
        print("-" * len(header))
        for i, row in enumerate(T):
            vals = " | ".join(f"{v:>{col_w}.4f}" for v in row)
            print(f"{row_labels[i]:>6} | {vals}")

    # --- メインループ ---
    while True:
        if verbose:
            print_tableau(num_iterations)

        # ステップ1: 入る変数の選択（Dantzig 規則）
        z_row = T[0, :-1]
        entering_col = int(np.argmin(z_row))

        # 停止条件: 被約費用がすべて >= 0
        if z_row[entering_col] >= -EPS:
            if verbose:
                print("\n→ 最適: z行の全係数 >= 0, 停止")
            status = "optimal"
            break

        if verbose:
            print(f"\n入る変数: {var_name(entering_col)} (被約費用 {z_row[entering_col]:.4f})")

        # ステップ2: 出る変数の選択（最小比検定）
        ratios = np.full(m, np.inf)
        for i in range(m):
            coef = T[i + 1, entering_col]
            if coef > EPS:
                ratios[i] = T[i + 1, -1] / coef

        leaving_idx = int(np.argmin(ratios))

        # 非有界判定
        if np.isinf(ratios[leaving_idx]):
            status = "unbounded"
            if verbose:
                print("→ 非有界: 全比率が inf")
            return {"status": status}

        leaving_row = leaving_idx + 1
        pivot = T[leaving_row, entering_col]

        if verbose:
            print(f"出る変数: {var_name(basis[leaving_idx])} "
                  f"(比率 {ratios[leaving_idx]:.4f}, ピボット要素 {pivot:.4f})")

        # ステップ3: ピボット操作（行基本変形）
        basis[leaving_idx] = entering_col
        T[leaving_row, :] /= pivot                        # ピボット行を正規化
        for i in range(m + 1):
            if i != leaving_row:
                T[i, :] -= T[i, entering_col] * T[leaving_row, :]  # 他の行を消去

        num_iterations += 1

    # --- 解の抽出 ---
    x = np.zeros(n)
    slack = np.zeros(m)
    for i, b_idx in enumerate(basis):
        if b_idx < n:
            x[b_idx] = T[i + 1, -1]
        else:
            slack[b_idx - n] = T[i + 1, -1]

    objective = T[0, -1]
    y = T[0, n:n + m].copy()   # 双対解: z行のスラック変数位置の係数

    return {
        "status": status,
        "x": x,
        "objective": objective,
        "y": y,
        "num_iterations": num_iterations,
        "basis": basis,
        "slack": slack,
    }


# =============================================================================
# 課題1 — 実装の検証（2変数・手計算との照合）
# =============================================================================
def task1():
    print("=" * 60)
    print("課題1: 実装の検証")
    print("max z = 2x1 + 3x2  s.t. x1+x2<=4, x1+3x2<=6, x>=0")
    print("既知解: x*=(3,1), z*=9, y*=(3/2,1/2), 2回ピボット")
    print("=" * 60)

    c = [2, 3]
    A = [[1, 1], [1, 3]]
    b = [4, 6]

    res = simplex(c, A, b, sense="max", verbose=True)

    print("\n--- 結果 ---")
    print(f"status        : {res['status']}")
    print(f"x*            : {res['x']}")
    print(f"z*            : {res['objective']}")
    print(f"y* (双対解)   : {res['y']}")
    print(f"反復回数      : {res['num_iterations']}")
    print(f"スラック       : {res['slack']}")
    print(f"バインディング : "
          f"{['s' + str(i+1) for i, s in enumerate(res['slack']) if abs(s) < 1e-9]}")

    print("\n【手計算との照合】")
    assert np.allclose(res['x'], [3, 1], atol=1e-6), "x* が不一致"
    assert np.isclose(res['objective'], 9, atol=1e-6), "z* が不一致"
    assert np.allclose(res['y'], [1.5, 0.5], atol=1e-6), "y* が不一致"
    assert res['num_iterations'] == 2, "反復回数が不一致"
    print("✓ 全項目一致")


# =============================================================================
# 課題2 — 3変数3制約（提出対象）
# =============================================================================
def task2():
    print("\n" + "=" * 60)
    print("課題2: 3変数3制約")
    print("max z = 5x1 + 4x2 + 3x3")
    print("s.t. 2x1+3x2+x3<=5, 4x1+x2+2x3<=11, 3x1+4x2+2x3<=8")
    print("=" * 60)

    c = [5, 4, 3]
    A = [[2, 3, 1], [4, 1, 2], [3, 4, 2]]
    b = [5, 11, 8]

    res = simplex(c, A, b, sense="max", verbose=True)

    n = len(c)

    print("\n--- 結果 ---")
    print(f"status        : {res['status']}")
    print(f"x*            : {res['x']}")
    print(f"z*            : {res['objective']}")
    print(f"y* (双対解)   : {res['y']}")
    print(f"反復回数      : {res['num_iterations']}")

    print("\n--- 各制約のスラック値とバインディング判定 ---")
    binding = []
    print(f"{'制約':<15} {'スラック':>10} {'判定':>12}")
    print("-" * 40)
    for i, s in enumerate(res['slack']):
        is_binding = abs(s) < 1e-9
        label = "バインディング" if is_binding else "非バインディング"
        if is_binding:
            binding.append(f"s{i+1}")
        print(f"{'s'+str(i+1):<15} {s:>10.4f} {label:>14}")

    print("\n強双対性の確認 b^T y* = c^T x*:")
    lhs = float(np.dot(b, res['y']))
    rhs = float(np.dot(c, res['x']))
    print(f"  b^T y* = {lhs:.6f}")
    print(f"  c^T x* = {rhs:.6f}")
    print(f"  一致: {np.isclose(lhs, rhs, atol=1e-6)}")

    print("\n被約費用と相補性条件の確認:")
    reduced_costs = -np.dot(res['y'], A) + np.array(c)
    print(f"  被約費用 c̄ = c - A^T y* = {reduced_costs}")
    for j in range(n):
        xj = res['x'][j]
        rc = reduced_costs[j]
        comp = xj * rc
        print(f"  x{j+1}={xj:.4f}, c̄{j+1}={rc:.4f}, "
              f"x{j+1}*c̄{j+1}={comp:.6f} (≈0: {abs(comp) < 1e-6})")

    return res


# =============================================================================
# 課題3 — 大規模LP（8製品 × 6資源）
# =============================================================================
def task3():
    print("\n" + "=" * 60)
    print("課題3: 大規模LP (8製品 × 6資源)")
    print("=" * 60)

    c = [48, 35, 27, 52, 31, 40, 23, 45]
    A = [
        [3, 2, 1, 4, 2, 3, 1, 2],  # SMT
        [2, 3, 2, 2, 1, 2, 3, 4],  # 組立
        [1, 1, 2, 2, 1, 1, 1, 2],  # 検査
        [4, 1, 0, 5, 2, 3, 0, 2],  # 部品X
        [0, 2, 3, 1, 2, 1, 4, 3],  # 部品Y
        [2, 2, 1, 3, 1, 2, 1, 2],  # 熟練工
    ]
    b = [240, 220, 150, 200, 180, 160]

    res = simplex(c, A, b, sense="max", verbose=False)

    products = ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8"]
    resources = ["SMT", "組立", "検査", "部品X", "部品Y", "熟練工"]

    print(f"\nstatus   : {res['status']}")
    print(f"z* (最適利益): {res['objective']:.2f}")
    print(f"反復回数  : {res['num_iterations']}")

    print("\n--- 最適生産量 x* ---")
    for i, xi in enumerate(res['x']):
        print(f"  {products[i]}: {xi:.4f}")

    print("\n--- 各資源のスラックとボトルネック判定 ---")
    print(f"{'資源':<8} {'利用可能':>8} {'スラック':>10} {'判定':>14}")
    print("-" * 44)
    for i, (name, bi, si) in enumerate(zip(resources, b, res['slack'])):
        label = "★ボトルネック" if abs(si) < 1e-9 else "余裕あり"
        print(f"{name:<8} {bi:>8} {si:>10.4f} {label:>14}")

    print("\n--- 影の価格 y* ---")
    print(f"{'資源':<8} {'影の価格':>10}")
    print("-" * 20)
    for name, yi in zip(resources, res['y']):
        print(f"{name:<8} {yi:>10.4f}")

    max_y_idx = int(np.argmax(res['y']))
    print(f"\n最も価値の高い資源: {resources[max_y_idx]} "
          f"(影の価格 = {res['y'][max_y_idx]:.4f})")

    print("\n強双対性の確認 b^T y* = c^T x*:")
    lhs = float(np.dot(b, res['y']))
    rhs = float(np.dot(c, res['x']))
    print(f"  b^T y* = {lhs:.6f}")
    print(f"  c^T x* = {rhs:.6f}")
    print(f"  一致: {np.isclose(lhs, rhs, atol=1e-4)}")

    return res


# =============================================================================
# メイン
# =============================================================================
if __name__ == "__main__":
    task1()
    task2()
    task3()
