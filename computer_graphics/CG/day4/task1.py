import numpy as np  # 追加
from OpenGL.GL import *
import glfw


def display():
    glClear(GL_COLOR_BUFFER_BIT)
    glColor3f(0.0, 0.6, 0.2)
    v = np.array([[0.0, 0.0],
    [0.0, 0.5],
    [1.0, 0.0]], dtype=np.float32)

    glBegin(GL_TRIANGLES)
    for i in range(3):
        x = v[i][0]
        y = v[i][1]
        # rotation
        theta = 30.0 / 180.0 * np.pi
        # TODO1: x', y'を計算する
        # x_dash = ...
        # y_dash = ...
        # TODO2: OpenGLに座標を渡す
        # glVertex2f(x_dash, y_dash)
    glEnd()


def init():
    glClearColor(1.0, 1.0, 1.0, 1.0)


def refresh(window):
    display()
    glfw.swap_buffers(window)


def main():
    glfw.init()
    win = glfw.create_window(500, 500, "Hello", None, None)
    glfw.make_context_current(win)
    init()
    glfw.set_window_refresh_callback(win, refresh)
    while not glfw.window_should_close(win):
        glfw.wait_events()
    glfw.terminate()


if __name__ == "__main__":
    main()
