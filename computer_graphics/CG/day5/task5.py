import glfw
from OpenGL.GL import *
from OpenGL.GLU import *

vertex = [
    (0.0, 0.0, 0.0),
    (1.0, 0.0, 0.0),
    (1.0, 1.0, 0.0),
    (0.0, 1.0, 0.0),
    (0.0, 0.0, 1.0),
    (1.0, 0.0, 1.0),
    (1.0, 1.0, 1.0),
    (0.0, 1.0, 1.0),
]

edge = [
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 0),
    (4, 5),
    (5, 6),
    (6, 7),
    (7, 4),
    (0, 4),
    (1, 5),
    (2, 6),
    (3, 7),
]

tx = 0.0
ty = 0.0
tz = 0.0
angele_x = 0.0
angle_y = 0.0
scale = 0.5


def perspective(width, height):
    # 割る方が0にならないようにする
    if height == 0:
        height = 1
    # 透視変換行列の設定
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(30.0, width / height, 1.0, 100.0)
    # モデルビュー変換行列の設定
    glMatrixMode(GL_MODELVIEW)


def display():
    glClear(GL_COLOR_BUFFER_BIT)
    # モデルビュー変換行列の設定
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(3.0, 4.0, 5.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

    # 平行移動・回転・拡大縮小する
    glTranslatef(tx, ty, tz)
    glRotatef(angele_x, 1.0, 0.0, 0.0)
    glRotatef(angle_y, 0.0, 1.0, 0.0)
    glScalef(scale, scale, scale)

    # 立方体を描画する
    glColor3d(0.0, 0.0, 0.0)
    glBegin(GL_LINES)
    for i in range(12):
        glVertex3fv(vertex[edge[i][0]])
        glVertex3fv(vertex[edge[i][1]])
    glEnd()


def keyboard(window, key, scancode, action, mods):
    global tx, ty, tz, angele_x, angle_y, scale
    if action not in (glfw.PRESS, glfw.REPEAT):
        return

    # 平行移動
    if key == glfw.KEY_LEFT:
        tx -= 0.05
    if key == glfw.KEY_RIGHT:
        tx += 0.05
    if key == glfw.KEY_UP:
        ty += 0.05
    if key == glfw.KEY_DOWN:
        ty -= 0.05
    if key == glfw.KEY_W:
        tz += 0.05
    if key == glfw.KEY_S:
        tz -= 0.05

    # 平行移動
    if key == glfw.KEY_A:
        angle_y -= 5.0
    if key == glfw.KEY_D:
        angle_y += 5.0
    if key == glfw.KEY_R:
        angele_x += 5.0
    if key == glfw.KEY_F:
        angele_x -= 5.0

    # 拡大縮小
    if key == glfw.KEY_Z:
        scale += 0.05
    if key == glfw.KEY_X:
        scale = max(0.05, scale - 0.05)

    refresh(window)


def refresh(window):
    display()
    glfw.swap_buffers(window)


def init():
    glClearColor(1.0, 1.0, 1.0, 1.0)
    perspective(512, 512)


def main():
    glfw.init()
    window = glfw.create_window(512, 512, "課題5", None, None)
    glfw.make_context_current(window)
    init()
    glfw.set_key_callback(window, keyboard)

    while not glfw.window_should_close(window):
        display()
        glfw.swap_buffers(window)
        glfw.poll_events()
    glfw.destroy_window(window)
    glfw.terminate()


if __name__ == "__main__":
    main()
