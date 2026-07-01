import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

vertex = np.array([
    (0.0, 0.0, 0.0),  # A (0)
    (1.0, 0.0, 0.0),  # B (1)
    (1.0, 1.0, 0.0),  # C (2)
    (0.0, 1.0, 0.0),  # D (3)
    (0.0, 0.0, 1.0),  # E (4)
    (1.0, 0.0, 1.0),  # F (5)
    (1.0, 1.0, 1.0),  # G (6)
    (0.0, 1.0, 1.0),  # H (7)
])

face = np.array([
    [3, 2, 1, 0],  # D-C-B-A
    [2, 6, 5, 1],  # C-G-F-B
    [6, 7, 4, 5],  # G-H-E-F
    [7, 3, 0, 4],  # H-D-A-E
    [0, 1, 5, 4],  # A-B-F-E
    [7, 6, 2, 3],  # H-G-C-D
])

face_colors = [
    (1.0, 0.0, 0.0),  # 赤
    (0.0, 1.0, 0.0),  # 緑
    (0.0, 0.0, 1.0),  # 青
    (1.0, 1.0, 0.0),  # 黄
    (1.0, 0.0, 1.0),  # マゼンタ
    (0.0, 1.0, 1.0),  # シアン
]

r = 0


def perspective(width, height):
    if height == 0:
        height = 1
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(30.0, width / height, 1.0, 100.0)
    glMatrixMode(GL_MODELVIEW)


def resize(window, width, height):
    perspective(width, height)


def display():
    global r
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(3.0, 4.0, 5.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)
    glRotatef(float(r), 0.0, 1.0, 0.0)

    for i in range(6):
        glColor3fv(face_colors[i])
        glBegin(GL_QUADS)
        for idx in face[i]:
            glVertex3fv(vertex[idx])
        glEnd()

    r = (r + 1) % 360


def init():
    glClearColor(0.2, 0.2, 0.2, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    perspective(512, 512)


def main():
    glfw.init()
    glfw.window_hint(glfw.SAMPLES, 4)
    window = glfw.create_window(512, 512, "Day8 - Cube with Depth Buffer", None, None)
    glfw.make_context_current(window)
    glfw.set_framebuffer_size_callback(window, resize)
    init()

    while not glfw.window_should_close(window):
        display()
        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.destroy_window(window)
    glfw.terminate()


if __name__ == "__main__":
    main()
