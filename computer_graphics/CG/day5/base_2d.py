import glfw
from OpenGL.GL import *


def display():
    glClear(GL_COLOR_BUFFER_BIT)
    glColor3f(0.0, 0.6, 0.2)
    glBegin(GL_POLYGON)
    glVertex2f(-0.9, -0.9)
    glVertex2f(0.9, -0.9)
    glVertex2f(0.9, 0.9)
    glVertex2f(-0.9, 0.9)
    glEnd()
    glFlush()


def init():
    glClearColor(1.0, 1.0, 1.0, 1.0)


def main():
    glfw.init()
    win = glfw.create_window(500, 500, "Hello", None, None)
    glfw.make_context_current(win)
    init()
    glOrtho(-2, 2, -2, 2, -1.0, 1.0)
    while not glfw.window_should_close(win):
        display()
        glfw.swap_buffers(win)
        glfw.poll_events()
    glfw.terminate()


if __name__ == "__main__":
    main()
