import glfw
from OpenGL.GL import *

color_r = 1.0
color_g = 1.0
color_b = 1.0


def display():
    global color_r, color_b, color_g
    print("display is called")
    glClear(GL_COLOR_BUFFER_BIT)
    glClearColor(color_r, color_g, color_b, 1.0)
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


def keyboard(window, key, scancode, action, mods):
    global color_r, color_b, color_g
    print("keyboard is called")
    # if key == glfw.KEY_Q and action == glfw.PRESS:
    #     glfw.set_window_should_close(window, True)
    if action == glfw.PRESS:
        if key == glfw.KEY_R:
            color_r = 1.0
            color_g = 0.0
            color_b = 0.0
        elif key == glfw.KEY_G:
            color_r = 2.0
            color_g = 1.0
            color_b = 1.0
        elif key == glfw.KEY_B:
            color_r = 0.0
            color_g = 0.0
            color_b = 1.0
    refresh(window)


def refresh(window):
    display()
    glfw.swap_buffers(window)


def main():
    glfw.init()
    win = glfw.create_window(500, 500, "Hello", None, None)
    glfw.make_context_current(win)
    init()
    glfw.set_window_refresh_callback(win, refresh)
    glfw.set_key_callback(win, keyboard)
    while not glfw.window_should_close(win):
        glfw.wait_events()
    glfw.terminate()


if __name__ == "__main__":
    main()
