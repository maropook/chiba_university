import glfw
from OpenGL.GL import *
from OpenGL.GLU import *

# 3次元図形の頂点とエッジの定義（上記「3」のデータをここに配置）
vertex = [
    (0.0, 0.0, 0.0),
    (1.0, 0.0, 0.0),
    (1.0, 1.0, 0.0),
    (0.0, 1.0, 0.0),
    (0.0, 0.0, 1.0),
    (1.0, 0.0, 1.0),
    (1.0, 1.0, 1.0),
    (0.0, 1.0, 1.0),
]
edge = [
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 0),
    (4, 5),
    (5, 6),
    (6, 7),
    (7, 4),
    (0, 4),
    (1, 5),
    (2, 6),
    (3, 7),
]


def display():
    glClear(GL_COLOR_BUFFER_BIT)
    # モデルビュー変換行列の設定
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    # 視点を(3,4,5)におき、注視点は原点、y軸方向がカメラの上向き
    gluLookAt(3.0, 4.0, 5.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

    # 図形の描画(黒)
    glColor3d(0.0, 0.0, 0.0)
    glBegin(GL_LINES)
    for i in range(12):
        glVertex3fv(vertex[edge[i][0]])
        glVertex3fv(vertex[edge[i][1]])
    glEnd()


def perspective(width, height):
    # 透視変換行列の設定
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    # 画角30度、アスペクト比、前方面1.0、後方面100.0
    gluPerspective(30.0, width / height, 1.0, 100.0)
    # モデルビュー変換行列の設定に戻しておく
    glMatrixMode(GL_MODELVIEW)


def resize(window, width, height):
    perspective(width, height)


def init():
    glClearColor(1.0, 1.0, 1.0, 1.0)
    perspective(512, 512)


def main():
    if glfw.init():
        window = glfw.create_window(512, 512, "Hello OpenGL", None, None)
        if not window:
            glfw.terminate()
            return
        glfw.make_context_current(window)
        init()

        # リサイズコールバックの設定
        glfw.set_framebuffer_size_callback(window, resize)

        while not glfw.window_should_close(window):
            display()
            glfw.swap_buffers(window)
            glfw.poll_events()

        glfw.destroy_window(window)
        glfw.terminate()


if __name__ == "__main__":
    main()
