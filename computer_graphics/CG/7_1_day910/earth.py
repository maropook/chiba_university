import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from PIL import Image


# 極座標からXYZ座標へ変換する
def from_spherical(r, theta, phi):
    x = r * np.sin(theta) * np.cos(phi)
    y = r * np.cos(theta)
    z = r * np.sin(theta) * np.sin(phi)
    return np.array([x, y, z])


# 画像を読み込む
def initTextureFromFile(filename):
    img = Image.open(filename)
    # 上下を反転する
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    width, height = img.size
    data = img.tobytes()

    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)

    glTexImage2D(
        GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, data
    )
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)


def drawSphere(radius):
    stacks = 80
    slices = 160

    glBegin(GL_QUADS)
    for i in range(stacks):
        for j in range(slices):
            theta = i / float(stacks) * np.pi
            phi = j / float(slices) * 2.0 * np.pi
            dtheta = 1.0 / float(stacks) * np.pi
            dphi = 1.0 / float(slices) * 2.0 * np.pi

            v0 = from_spherical(radius, theta, phi)
            v1 = from_spherical(radius, theta + dtheta, phi)
            v2 = from_spherical(radius, theta + dtheta, phi + dphi)
            v3 = from_spherical(radius, theta, phi + dphi)

            # 頂点0
            glTexCoord2f(1.0 / (2.0 * np.pi) * phi, 1.0 / np.pi * theta)
            glVertex3fv(v0)

            # 頂点1
            glTexCoord2f(1.0 / (2.0 * np.pi) * phi, 1.0 / np.pi * (theta + dtheta))
            glVertex3fv(v1)

            # 頂点2
            glTexCoord2f(
                1.0 / (2.0 * np.pi) * (phi + dphi), 1.0 / np.pi * (theta + dtheta)
            )
            glVertex3fv(v2)

            # 頂点3
            glTexCoord2f(1.0 / (2.0 * np.pi) * (phi + dphi), 1.0 / np.pi * theta)
            glVertex3fv(v3)
    glEnd()


def resize(window, width, height):
    if height == 0:
        height = 1
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(30.0, width / height, 1.0, 100.0)
    glMatrixMode(GL_MODELVIEW)


def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    gluLookAt(0.0, 2.0, 3.5, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

    # 描画色を白にする
    glColor3f(1.0, 1.0, 1.0)

    drawSphere(0.6)


def init():
    glClearColor(0.2, 0.2, 0.2, 1.0)
    glEnable(GL_DEPTH_TEST)

    glEnable(GL_TEXTURE_2D)
    initTextureFromFile("earth.png")


def main():
    if not glfw.init():
        return

    window = glfw.create_window(512, 512, "Earth", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.set_framebuffer_size_callback(window, resize)

    init()

    width, height = glfw.get_framebuffer_size(window)
    resize(window, width, height)

    while not glfw.window_should_close(window):
        display()
        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.destroy_window(window)
    glfw.terminate()


if __name__ == "__main__":
    main()
