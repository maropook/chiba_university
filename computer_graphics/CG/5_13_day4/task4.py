import glfw
from OpenGL.GL import *
import numpy as np

tx = 0.0  # 平行移動
ty = 0.0  # 平行移動
angle = 0.0  # 回転角
scale = 1.0  # 拡大縮小率

# 花びら
PETALS = [
    # 上
    [(0.0, 0.0), (0.2, 0.3), (-0.2, 0.3)],
    [(0.0, 0.6), (0.2, 0.3), (-0.2, 0.3)],
    # 下
    [(0.0, 0.0), (0.2, -0.3), (-0.2, -0.3)],
    [(0.0, -0.6), (0.2, -0.3), (-0.2, -0.3)],
    # 右
    [(0.0, 0.0), (0.3, 0.2), (0.3, -0.2)],
    [(0.6, 0.0), (0.3, 0.2), (0.3, -0.2)],
    # 左
    [(0.0, 0.0), (-0.3, 0.2), (-0.3, -0.2)],
    [(-0.6, 0.0), (-0.3, 0.2), (-0.3, -0.2)],
]


def get_transfored_matrix():
    # 変換行列を返す関数
    theta = angle / 180.0 * np.pi
    T = np.array([[1, 0, tx], [0, 1, ty], [0, 0, 1]], dtype=np.float32)
    R = np.array(
        [
            [np.cos(theta), -np.sin(theta), 0],
            [np.sin(theta), np.cos(theta), 0],
            [0, 0, 1],
        ],
        dtype=np.float32,
    )
    S = np.array([[scale, 0, 0], [0, scale, 0], [0, 0, 1]], dtype=np.float32)
    return T @ R @ S


def apply_transform(A, x, y):
    # x', y' を x*Aから取り出す関数
    p = A @ np.array([x, y, 1], dtype=np.float32)
    return p[0], p[1]


def display():
    glClearColor(1.0, 1.0, 1.0, 1.0)
    glClear(GL_COLOR_BUFFER_BIT)
    A = get_transfored_matrix()
    # 花びらをすべて表示
    glColor3f(0.8, 0.0, 0.8)
    for petal in PETALS:
        glBegin(GL_TRIANGLES)
        for x, y in petal:
            x_dash, y_dash = apply_transform(A, x, y)
            glVertex2f(x_dash, y_dash)
        glEnd()

    glFlush()


def keyboard(window, key, scancode, action, mods):
    """キー操作で変換状態を更新する"""
    global tx, ty, angle, scale
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

    # 回転
    if key == glfw.KEY_R:
        angle += 10.0
    if key == glfw.KEY_E:
        angle -= 10.0

    # 拡大縮小
    if key == glfw.KEY_Z:
        scale += 0.1
    if key == glfw.KEY_X:
        scale = max(0.1, scale - 0.1)

    refresh(window)


def refresh(window):
    display()
    glfw.swap_buffers(window)


def main():
    if not glfw.init():
        raise Exception("GLFW初期化失敗")

    window = glfw.create_window(512, 512, "Flower Transform", None, None)
    glfw.make_context_current(window)
    glClearColor(0.1, 0.1, 0.1, 1.0)
    glfw.set_window_refresh_callback(window, refresh)
    glfw.set_key_callback(window, keyboard)
    while not glfw.window_should_close(window):
        glfw.wait_events()
    glfw.terminate()


if __name__ == "__main__":
    main()
