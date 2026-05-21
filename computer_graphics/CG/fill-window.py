import glfw
from OpenGL.GL import *


def display():
    glClear(GL_COLOR_BUFFER_BIT)  # 背景を実際に塗る


def init():
    glClearColor(0.0, 0.0, 1.0, 1.0)  # 背景塗るとしたらこの色であると宣言しているだけ


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
