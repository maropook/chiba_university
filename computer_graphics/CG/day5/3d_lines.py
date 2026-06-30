import glfw
from OpenGL.GL import *

# 頂点データ (A～H)
vertex = [
    (0.0, 0.0, 0.0),  # A
    (1.0, 0.0, 0.0),  # B
    (1.0, 1.0, 0.0),  # C
    (0.0, 1.0, 0.0),  # D
    (0.0, 0.0, 1.0),  # E
    (1.0, 0.0, 1.0),  # F
    (1.0, 1.0, 1.0),  # G
    (0.0, 1.0, 1.0),  # H
]

# 稜線（エッジ）データ
edge = [
    (0, 1),  # ア (A-B)
    (1, 2),  # イ (B-C)
    (2, 3),  # ウ (C-D)
    (3, 0),  # エ (D-A)
    (4, 5),  # オ (E-F)
    (5, 6),  # カ (F-G)
    (6, 7),  # キ (G-H)
    (7, 4),  # ク (H-E)
    (0, 4),  # ケ (A-E)
    (1, 5),  # コ (B-F)
    (2, 6),  # サ (C-G)
    (3, 7),  # シ (D-H)
]


def display():
    glClear(GL_COLOR_BUFFER_BIT)
    # 図形の描画
    glColor3d(0.0, 0.0, 0.0)
    glBegin(GL_LINES)
    for i in range(12):
        glVertex3fv(vertex[edge[i][0]])
        glVertex3fv(vertex[edge[i][1]])
    glEnd()


def init():
    glClearColor(1.0, 1.0, 1.0, 1.0)


if __name__ == "__main__":
    glfw.init()
    window = glfw.create_window(512, 512, "Hello OpenGL", None, None)
    glfw.make_context_current(window)
    init()
    while not glfw.window_should_close(window):
        display()
        glfw.swap_buffers(window)
        glfw.poll_events()
    glfw.destroy_window(window)
    glfw.terminate()
