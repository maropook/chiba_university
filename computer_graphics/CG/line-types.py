import glfw
from OpenGL.GL import *
from OpenGL.GLU import *


def display():
    glClear(GL_COLOR_BUFFER_BIT)

    # GL_POINTS: 点を打つ
    glPointSize(8.0)
    glColor3f(1.0, 0.0, 0.0)
    glBegin(GL_POINTS)
    glVertex2f(-0.9, 0.8)
    glVertex2f(-0.8, 0.9)
    glVertex2f(-0.7, 0.8)
    glEnd()

    # GL_LINES: 2点を対にして直線を結ぶ
    glColor3f(0.0, 1.0, 0.0)
    glBegin(GL_LINES)
    glVertex2f(-0.6, 0.9)
    glVertex2f(-0.3, 0.7)
    glVertex2f(-0.2, 0.9)
    glVertex2f(0.0, 0.7)
    glEnd()

    # GL_LINE_STRIP: 折れ線
    glColor3f(0.0, 0.0, 1.0)
    glBegin(GL_LINE_STRIP)
    glVertex2f(0.1, 0.7)
    glVertex2f(0.3, 0.9)
    glVertex2f(0.5, 0.7)
    glVertex2f(0.7, 0.9)
    glVertex2f(0.9, 0.7)
    glEnd()

    # GL_LINE_LOOP: 折れ線（始点と終点も結ばれる）
    glColor3f(1.0, 0.5, 0.0)
    glBegin(GL_LINE_LOOP)
    glVertex2f(-0.9, 0.3)
    glVertex2f(-0.7, 0.5)
    glVertex2f(-0.5, 0.3)
    glVertex2f(-0.7, 0.1)
    glEnd()

    # GL_TRIANGLES: 3点を組にして三角形
    glColor3f(0.8, 0.0, 0.8)
    glBegin(GL_TRIANGLES)
    glVertex2f(-0.3, 0.1)
    glVertex2f(-0.1, 0.5)
    glVertex2f(0.1, 0.1)
    glEnd()

    # GL_QUADS: 4点を組にして四角形
    glColor3f(0.0, 0.8, 0.8)
    glBegin(GL_QUADS)
    glVertex2f(0.2, 0.1)
    glVertex2f(0.5, 0.1)
    glVertex2f(0.5, 0.5)
    glVertex2f(0.2, 0.5)
    glEnd()

    # GL_TRIANGLE_STRIP: 帯状に三角形
    glColor3f(1.0, 1.0, 0.0)
    glBegin(GL_TRIANGLE_STRIP)
    glVertex2f(-0.9, -0.5)
    glVertex2f(-0.9, -0.2)
    glVertex2f(-0.7, -0.5)
    glVertex2f(-0.7, -0.2)
    glVertex2f(-0.5, -0.5)
    glVertex2f(-0.5, -0.2)
    glEnd()

    # GL_QUAD_STRIP: 帯状に四角形
    glColor3f(0.5, 1.0, 0.5)
    glBegin(GL_QUAD_STRIP)
    glVertex2f(-0.3, -0.5)
    glVertex2f(-0.3, -0.2)
    glVertex2f(-0.1, -0.5)
    glVertex2f(-0.1, -0.2)
    glVertex2f(0.1, -0.5)
    glVertex2f(0.1, -0.2)
    glEnd()

    # GL_TRIANGLE_FAN: 扇状に三角形
    glColor3f(0.5, 0.5, 1.0)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(0.5, -0.35)  # 中心点
    glVertex2f(0.7, -0.2)
    glVertex2f(0.9, -0.3)
    glVertex2f(0.9, -0.5)
    glVertex2f(0.7, -0.5)
    glEnd()

    # GL_POLYGON: 凸多角形（六角形）
    glColor3f(1.0, 0.3, 0.3)
    glBegin(GL_POLYGON)
    glVertex2f(-0.1, -0.7)
    glVertex2f(0.1, -0.7)
    glVertex2f(0.2, -0.85)
    glVertex2f(0.1, -1.0)
    glVertex2f(-0.1, -1.0)
    glVertex2f(-0.2, -0.85)
    glEnd()

    glFlush()


def refresh(window):
    display()
    glfw.swap_buffers(window)


def main():
    if not glfw.init():
        raise Exception("GLFW初期化失敗")
    win = glfw.create_window(700, 700, "GL Primitives", None, None)
    glfw.make_context_current(win)
    glClearColor(0.1, 0.1, 0.1, 1.0)
    glfw.set_window_refresh_callback(win, refresh)
    while not glfw.window_should_close(win):
        glfw.wait_events()
    glfw.terminate()


if __name__ == "__main__":
    main()
