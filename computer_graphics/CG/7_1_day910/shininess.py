import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

shininess = 32.0


def from_spherical(r, theta, phi):
    x = r * np.sin(theta) * np.cos(phi)
    y = r * np.cos(theta)
    z = r * np.sin(theta) * np.sin(phi)
    return np.array([x, y, z])


def drawSphere(radius, tdiv=32, pdiv=64):
    glBegin(GL_QUADS)
    for i in range(tdiv):
        for j in range(pdiv):
            theta = i / tdiv * np.pi
            phi = j / pdiv * 2.0 * np.pi
            dtheta = 1.0 / tdiv * np.pi
            dphi = 1.0 / pdiv * 2.0 * np.pi
            v0 = from_spherical(radius, theta, phi)
            v1 = from_spherical(radius, theta + dtheta, phi)
            v2 = from_spherical(radius, theta + dtheta, phi + dphi)
            v3 = from_spherical(radius, theta, phi + dphi)
            # 球の法線 = 位置ベクトル / 半径
            glNormal3fv(v0 / radius)
            glVertex3fv(v0)
            glNormal3fv(v1 / radius)
            glVertex3fv(v1)
            glNormal3fv(v2 / radius)
            glVertex3fv(v2)
            glNormal3fv(v3 / radius)
            glVertex3fv(v3)
    glEnd()


def drawAxis():
    lighting_on = glGetBooleanv(GL_LIGHTING)
    glDisable(GL_LIGHTING)
    glBegin(GL_LINES)
    glColor3f(1, 0, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(1, 0, 0)
    glColor3f(0, 1, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 1, 0)
    glColor3f(0, 0, 1)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, 1)
    glEnd()
    if lighting_on:
        glEnable(GL_LIGHTING)


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
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(3.0, 4.0, 5.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

    lpos = np.array([3, 3, 3, 1], dtype=np.float32)
    glLightfv(GL_LIGHT0, GL_POSITION, lpos)

    matRed = np.array([1, 0, 0, 1], dtype=np.float32)
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, matRed)
    matWhite = np.array([1, 1, 1, 1], dtype=np.float32)
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, matWhite)
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, shininess)

    drawSphere(0.5)
    drawAxis()


def key_callback(window, key, scancode, action, mods):
    global shininess
    if action in (glfw.PRESS, glfw.REPEAT):
        if key == glfw.KEY_UP:
            shininess = min(128.0, shininess + 8.0)
            print(f"Shininess: {shininess:.1f}")
        elif key == glfw.KEY_DOWN:
            shininess = max(0.0, shininess - 8.0)
            print(f"Shininess: {shininess:.1f}")


def init():
    glClearColor(0.2, 0.2, 0.2, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    perspective(512, 512)


def main():
    glfw.init()
    glfw.window_hint(glfw.SAMPLES, 4)
    window = glfw.create_window(512, 512, "Shininess Control - Up/Down Arrow", None, None)
    glfw.make_context_current(window)
    glfw.set_framebuffer_size_callback(window, resize)
    glfw.set_key_callback(window, key_callback)
    init()

    while not glfw.window_should_close(window):
        display()
        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.destroy_window(window)
    glfw.terminate()


if __name__ == "__main__":
    main()
