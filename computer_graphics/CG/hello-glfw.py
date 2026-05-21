import glfw
from OpenGL.GL import *


def display():
    # 前フレームの色を消して、画面を塗り直す準備
    glClear(GL_COLOR_BUFFER_BIT)
    # 背景色を白に設定 (R, G, B, A)
    glClearColor(1.0, 1.0, 1.0, 1.0)
    # これから描く図形の色を緑系に設定
    glColor3f(0.0, 0.6, 0.2)

    # 多角形の描画を開始 (今回は頂点4つで四角形)
    glBegin(GL_POLYGON)
    # 図形の頂点座標を左下 -> 右下 -> 右上 -> 左上の順で指定
    glVertex2f(-0.9, -0.9)
    glVertex2f(0.9, -0.9)
    glVertex2f(0.9, 0.9)
    glVertex2f(-0.9, 0.9)
    # 図形の描画を終了
    glEnd()


def main():
    # GLFW ライブラリを初期化
    glfw.init()

    # 描画先となるウィンドウを作成 (幅, 高さ, タイトル)
    window = glfw.create_window(512, 512, "Hello OpenGL", None, None)
    # 以降の OpenGL 命令をこのウィンドウに対して有効化
    glfw.make_context_current(window)

    # ウィンドウが閉じられるまで繰り返すメインループ
    while not glfw.window_should_close(window):
        # キーボードやマウスなどのイベントを処理
        glfw.poll_events()
        display()
        # バックバッファを前面に表示 (ダブルバッファリング)
        glfw.swap_buffers(window)

    # 後片付け
    glfw.destroy_window(window)
    glfw.terminate()


if __name__ == "__main__":
    main()
