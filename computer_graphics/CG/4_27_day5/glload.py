import glfw
from OpenGL.GL import *

# 3次元図形の頂点定義 (13ページ目より)
vertex = [
    (0.0, 0.0, 0.0),  # A
    (1.0, 0.0, 0.0),  # B
    (1.0, 1.0, 0.0),  # C
    (0.0, 1.0, 0.0),  # D
    (0.0, 0.0, 1.0),  # E
    (1.0, 0.0, 1.0),  # F
    (1.0, 1.0, 1.0),  # G
    (0.0, 1.0, 1.0),  # H
]

# 稜線（エッジ）の定義 (13ページ目より)
edge = [
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 0),  # ア, イ, ウ, エ
    (4, 5),
    (5, 6),
    (6, 7),
    (7, 4),  # オ, カ, キ, ク
    (0, 4),
    (1, 5),
    (2, 6),
    (3, 7),  # ケ, コ, サ, シ
]


def printMVmat():
    """現在のModelView行列の値をコンソールに表示する関数"""
    m = glGetFloatv(GL_MODELVIEW_MATRIX)
    print("Model-View Matrix:")
    for i in range(4):
        for j in range(4):
            print(f"{m[j][i]:4.2f}\t", end="")
        print()
    print()


def display():
    # 画面を白（glClearColorで設定した色）でクリア
    glClear(GL_COLOR_BUFFER_BIT)

    # 1. 行列操作のモードをModel-View（物体やカメラの配置）に指定
    glMatrixMode(GL_MODELVIEW)

    # 2. ★超重要★ 行列を単位行列にリセット（これで勝手にどこかへ飛んでいかなくなる）
    glLoadIdentity()

    # 3. モデリング変換を適用
    glScalef(0.5, 0.5, 0.5)  # 全体を0.5倍に縮小
    glTranslatef(-0.5, -0.5, 0.0)  # 左下に平行移動

    # コンソールに行列の数値をデバッグ表示
    printMVmat()

    # 4. 立方体の線画を描画
    glColor3d(0.0, 0.0, 0.0)  # 線の色を黒に指定
    glBegin(GL_LINES)
    for i in range(12):
        idx1 = edge[i][0]
        idx2 = edge[i][1]
        # 3次元の座標を指定して線を引く
        glVertex3f(vertex[idx1][0], vertex[idx1][1], vertex[idx1][2])
        glVertex3f(vertex[idx2][0], vertex[idx2][1], vertex[idx2][2])
    glEnd()


def init():
    # 背景色を白色に設定
    glClearColor(1.0, 1.0, 1.0, 1.0)


def main():
    if not glfw.init():
        return

    # 512x512の正方形のウィンドウを作成
    window = glfw.create_window(512, 512, "Hello OpenGL - Matrix Test", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    init()

    # メインループ
    while not glfw.window_should_close(window):
        display()
        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.destroy_window(window)
    glfw.terminate()


if __name__ == "__main__":
    main()
