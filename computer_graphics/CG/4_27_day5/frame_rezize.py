import glfw
from OpenGL.GL import *


def resize(window, width, height):
    print(f"resize (w, h) = {width}, {height}")
    # ウィンドウのアスペクト比
    aspect = width / height
    # ウィンドウ全体をビューポートにする
    glViewport(0, 0, width, height)
    # 

    # 変換行列の初期化
    glLoadIdentity()
    # アスペクト比を保つ

    glOrtho(-aspect, aspect, -1.0, 1.0, -1.0, 1.0)
    #どこをカメラに映し出すか, 横幅は固定してしまってる


def display():
    glClear(GL_COLOR_BUFFER_BIT)
    glColor3d(0.0, 0.6, 0.2)
    glBegin(GL_POLYGON)
    glVertex2f(-0.9, -0.9)
    glVertex2f(0.9, -0.9)
    glVertex2f(0.9, 0.9)
    glVertex2f(-0.9, 0.9)
    glEnd()


def init():
    glClearColor(1.0, 1.0, 1.0, 1.0)


def main():
    glfw.init()
    window = glfw.create_window(500, 500, "Hello", None, None)
    glfw.make_context_current(window)
    init()

    # フレームバッファのサイズが変わったときに呼び出されるコールバック関数を登録する
    glfw.set_framebuffer_size_callback(window, resize)
    # 起動直後に一度呼んで投影行列を初期化する
    resize(window, *glfw.get_framebuffer_size(window))

    while not glfw.window_should_close(window):
        display()
        glfw.swap_buffers(window)
        glfw.poll_events()
    glfw.terminate()


if __name__ == "__main__":
    main()
