import glfw
from OpenGL.GL import *


def display():
    glClear(GL_COLOR_BUFFER_BIT)  # 背景を実際に塗る

    # glBegin(GL_TRIANGLES)
    # glBegin(GL_TRIANGLE_FAN)

    # GL_TRIANGLES: 3点を組にして三角形
    glColor3f(0.8, 0.0, 0.8)
    glBegin(GL_TRIANGLES)
    glVertex2f(0.0, 0.0)
    glVertex2f(0.2, 0.3)
    glVertex2f(-0.2, 0.3)
    glEnd()

    glColor3f(0.8, 0.0, 0.8)
    glBegin(GL_TRIANGLES)
    glVertex2f(0.0, 0.6)
    glVertex2f(0.2, 0.3)
    glVertex2f(-0.2, 0.3)
    glEnd()

    ####

    glColor3f(0.8, 0.0, 0.8)
    glBegin(GL_TRIANGLES)
    glVertex2f(0.0, -0.0)
    glVertex2f(0.2, -0.3)
    glVertex2f(-0.2, -0.3)
    glEnd()

    glColor3f(0.8, 0.0, 0.8)
    glBegin(GL_TRIANGLES)
    glVertex2f(0.0, -0.6)
    glVertex2f(0.2, -0.3)
    glVertex2f(-0.2, -0.3)
    glEnd()

    ###
    glColor3f(0.8, 0.0, 0.8)
    glBegin(GL_TRIANGLES)
    glVertex2f(0.0, 0.0)
    glVertex2f(0.3, 0.2)
    glVertex2f(0.3, -0.2)
    glEnd()

    glColor3f(0.8, 0.0, 0.8)
    glBegin(GL_TRIANGLES)
    glVertex2f(0.6, 0.0)
    glVertex2f(0.3, 0.2)
    glVertex2f(0.3, -0.2)
    glEnd()

    glColor3f(0.8, 0.0, 0.8)
    glBegin(GL_TRIANGLES)
    glVertex2f(-0.0, 0.0)
    glVertex2f(-0.3, 0.2)
    glVertex2f(-0.3, -0.2)
    glEnd()

    glColor3f(0.8, 0.0, 0.8)
    glBegin(GL_TRIANGLES)
    glVertex2f(-0.6, 0.0)
    glVertex2f(-0.3, 0.2)
    glVertex2f(-0.3, -0.2)
    glEnd()


def init():
    glClearColor(1.0, 1.0, 1.0, 1.0)  # 背景塗るとしたらこの色であると宣言しているだけ


def main():
    glfw.init()
    window = glfw.create_window(512, 512, "Create Window", None, None)
    glfw.make_context_current(window)
    init()
    while not glfw.window_should_close(window):
        display()
        glfw.swap_buffers(window)
        glfw.poll_events()
    glfw.destroy_window(window)
    glfw.terminate()


# main
if __name__ == "__main__":
    main()
