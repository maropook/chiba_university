import glfw
from OpenGL.GL import *


def display():
    pass


def main():
    glfw.init()
    window = glfw.create_window(512, 512, "Create Window", None, None)
    glfw.make_context_current(window)

    # glfw.set_window_pos(window, 400, 100)  # 実行時の表示ウィンドウ位置
    # glfw.set_window_size(window, 200, 200)  # ウィンドウサイズ

    while not glfw.window_should_close(window):
        display()
        glfw.swap_buffers(window)
        glfw.poll_events()
    glfw.destroy_window(window)
    glfw.terminate()


# main
if __name__ == "__main__":
    main()
