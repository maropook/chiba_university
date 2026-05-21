import glfw
from OpenGL.GL import *


def display():
    print("display is called")
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
