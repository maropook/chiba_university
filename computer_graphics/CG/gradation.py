import glfw
from OpenGL.GL import *


def display():
    glClear(GL_COLOR_BUFFER_BIT)
    glBegin(GL_POLYGON)
    glColor3f(1.0, 0.0, 0.0)
    # 赤
    glVertex2f(-0.9, -0.9)
    glColor3f(0.0, 1.0, 0.0)
    # 緑
    glVertex2f(0.9, -0.9)
    glColor3f(0.0, 0.0, 1.0)
    # 青
    glVertex2f(0.9, 0.9)
    glColor3f(1.0, 1.0, 0.0)
    # 黄
    glVertex2f(-0.9, 0.9)
    glEnd()
    glFlush()


def init():
    glClearColor(1.0, 1.0, 1.0, 1.0)


glfw.init()
win = glfw.create_window(500, 500, "Hello", None, None)
glfw.make_context_current(win)
init()
while not glfw.window_should_close(win):
    display()
    glfw.swap_buffers(win)
    glfw.poll_events()
glfw.terminate()
