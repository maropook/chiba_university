# 課題8：球体がバウンドするプログラム

import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

RADIUS = 0.5

pos = np.array([0.0, 3.0, 0.0])
vel = np.array([0.0, 0.0, 0.0])
g = np.array([0.0, -9.8, 0.0]) 
restitution = 0.8               
time = 0.0


def from_spherical(r, theta, phi):
    x = r * np.sin(theta) * np.cos(phi)
    y = r * np.cos(theta)
    z = r * np.sin(theta) * np.sin(phi)
    return np.array([x, y, z])


def drawSphere(radius):
    glBegin(GL_QUADS)
    for i in range(8):
        for j in range(16):
            theta = i / 8.0 * np.pi
            phi = j / 16.0 * 2.0 * np.pi
            dtheta = 1.0 / 8.0 * np.pi
            dphi = 1.0 / 16.0 * 2.0 * np.pi
            v0 = from_spherical(radius, theta, phi)
            v1 = from_spherical(radius, theta + dtheta, phi)
            v2 = from_spherical(radius, theta + dtheta, phi + dphi)
            v3 = from_spherical(radius, theta, phi + dphi)
            glVertex3fv(v0)
            glVertex3fv(v1)
            glVertex3fv(v2)
            glVertex3fv(v3)
    glEnd()


def drawWireSphere(radius):
    for i in range(8):
        for j in range(16):
            theta = i / 8.0 * np.pi
            phi = j / 16.0 * 2.0 * np.pi
            dtheta = 1.0 / 8.0 * np.pi
            dphi = 1.0 / 16.0 * 2.0 * np.pi
            v0 = from_spherical(radius, theta, phi)
            v1 = from_spherical(radius, theta + dtheta, phi)
            v2 = from_spherical(radius, theta + dtheta, phi + dphi)
            v3 = from_spherical(radius, theta, phi + dphi)
            glBegin(GL_LINE_LOOP)
            glVertex3fv(v0)
            glVertex3fv(v1)
            glVertex3fv(v2)
            glVertex3fv(v3)
            glEnd()


def drawPlaneY(size):
    glBegin(GL_QUADS)
    for i in range(size):
        for j in range(size):
            x = i - 0.5 * size
            z = j - 0.5 * size
            if (i + j) % 2 == 0:
                glColor3f(1, 1, 1)
            else:
                glColor3f(0.2, 0.2, 0.2)
            glVertex3f(x, 0, z)
            glVertex3f(x + 1, 0, z)
            glVertex3f(x + 1, 0, z + 1)
            glVertex3f(x, 0, z + 1)
    glEnd()


def drawAxis():
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
    global time, pos, vel

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(5.0, 5.0, 8.0, 0.0, 1.5, 0.0, 0.0, 1.0, 0.0)

    dt = 0.01
    time += dt

    # 速度と位置をオイラー法で更新する
    vel = vel + dt * g
    pos = pos + dt * vel

    # 床との衝突判定
    if pos[1] < RADIUS:
        pos[1] = RADIUS
        vel[1] = -vel[1] * restitution 

    # 球を描画
    glPushMatrix()
    glTranslatef(pos[0], pos[1], pos[2])
    glColor3f(0.8, 0.5, 0.2)
    drawSphere(RADIUS)
    glColor3f(1.0, 0.8, 0.4)
    drawWireSphere(RADIUS)
    glPopMatrix()

    drawPlaneY(10)
    drawAxis()


def init():
    glClearColor(0.15, 0.15, 0.2, 1.0)
    glEnable(GL_DEPTH_TEST)
    perspective(512, 512)


def main():
    glfw.init()
    glfw.window_hint(glfw.SAMPLES, 4)
    window = glfw.create_window(512, 512, "第8回宿題", None, None)
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
