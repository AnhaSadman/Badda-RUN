from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random

MAP_SIZE = 1000
ROAD_WIDTH = 100
SIDEWALK_WIDTH = 22
BLOCK_SPACING = 300

# radius used for player-vs-building collision checks
PLAYER_RADIUS = 14
# radius used for car-vs-building collision checks
CAR_RADIUS = 24

buildings = []
building_colors = [
    (0.78, 0.68, 0.62),
    (0.64, 0.70, 0.74),
    (0.76, 0.62, 0.52),
    (0.58, 0.65, 0.69),
    (0.82, 0.78, 0.68),
    (0.68, 0.57, 0.52),
    (0.74, 0.72, 0.64)
]

interactive_zones = {
    "gas_station": (-300, -300, 120, 120),
    "safe_house": (300, 300, 120, 120)
}

random.seed(8)

# generate a building for every city block
for road_x in range(-MAP_SIZE, MAP_SIZE, BLOCK_SPACING):
    for road_y in range(-MAP_SIZE, MAP_SIZE, BLOCK_SPACING):
        x = road_x + BLOCK_SPACING / 2
        y = road_y + BLOCK_SPACING / 2
        bw = random.randint(110, 140)
        bh = random.randint(110, 140)
        h = random.randint(140, 320)
        r, g, b = random.choice(building_colors)
        buildings.append((x, y, bw, bh, r, g, b, h))


def get_solid_boxes():
    # returns every axis-aligned solid box in the world as (x, y, width, height)
    boxes = [(bx, by, bw, bh) for bx, by, bw, bh, r, g, b, h in buildings]

    gx, gy, gw, gh = interactive_zones["gas_station"]
    boxes.append((gx, gy + 25, 70, 36))

    sx, sy, sw, sh = interactive_zones["safe_house"]
    boxes.append((sx, sy, 86, 71))

    return boxes


def is_colliding(x, y, radius):
    # circle-vs-rectangle test against every solid box, used to block movement through walls
    for bx, by, bw, bh in get_solid_boxes():
        half_w = bw / 2
        half_h = bh / 2
        closest_x = max(bx - half_w, min(x, bx + half_w))
        closest_y = max(by - half_h, min(y, by + half_h))
        dx = x - closest_x
        dy = y - closest_y
        if dx * dx + dy * dy < radius * radius:
            return True
    return False


def draw_cube(x, y, z, sx, sy, sz, color):
    glPushMatrix()
    glColor3f(*color)
    glTranslatef(x, y, z)
    glScalef(sx, sy, sz)
    glutSolidCube(1)
    glPopMatrix()


def draw_ground():
    # grass
    glColor3f(0.28, 0.48, 0.25)
    glBegin(GL_QUADS)
    glVertex3f(-MAP_SIZE, -MAP_SIZE, -2)
    glVertex3f(MAP_SIZE, -MAP_SIZE, -2)
    glVertex3f(MAP_SIZE, MAP_SIZE, -2)
    glVertex3f(-MAP_SIZE, MAP_SIZE, -2)
    glEnd()

    # sidewalks
    glColor3f(0.72, 0.71, 0.67)
    for i in range(-MAP_SIZE, MAP_SIZE + 1, BLOCK_SPACING):
        glBegin(GL_QUADS)

        glVertex3f(i - ROAD_WIDTH / 2 - SIDEWALK_WIDTH, -MAP_SIZE, 1)
        glVertex3f(i - ROAD_WIDTH / 2, -MAP_SIZE, 1)
        glVertex3f(i - ROAD_WIDTH / 2, MAP_SIZE, 1)
        glVertex3f(i - ROAD_WIDTH / 2 - SIDEWALK_WIDTH, MAP_SIZE, 1)

        glVertex3f(i + ROAD_WIDTH / 2, -MAP_SIZE, 1)
        glVertex3f(i + ROAD_WIDTH / 2 + SIDEWALK_WIDTH, -MAP_SIZE, 1)
        glVertex3f(i + ROAD_WIDTH / 2 + SIDEWALK_WIDTH, MAP_SIZE, 1)
        glVertex3f(i + ROAD_WIDTH / 2, MAP_SIZE, 1)

        glVertex3f(-MAP_SIZE, i - ROAD_WIDTH / 2 - SIDEWALK_WIDTH, 1)
        glVertex3f(MAP_SIZE, i - ROAD_WIDTH / 2 - SIDEWALK_WIDTH, 1)
        glVertex3f(MAP_SIZE, i - ROAD_WIDTH / 2, 1)
        glVertex3f(-MAP_SIZE, i - ROAD_WIDTH / 2, 1)

        glVertex3f(-MAP_SIZE, i + ROAD_WIDTH / 2, 1)
        glVertex3f(MAP_SIZE, i + ROAD_WIDTH / 2, 1)
        glVertex3f(MAP_SIZE, i + ROAD_WIDTH / 2 + SIDEWALK_WIDTH, 1)
        glVertex3f(-MAP_SIZE, i + ROAD_WIDTH / 2 + SIDEWALK_WIDTH, 1)

        glEnd()

    # roads
    glColor3f(0.09, 0.10, 0.12)
    glBegin(GL_QUADS)
    for i in range(-MAP_SIZE, MAP_SIZE + 1, BLOCK_SPACING):
        glVertex3f(i - ROAD_WIDTH / 2, -MAP_SIZE, 2)
        glVertex3f(i + ROAD_WIDTH / 2, -MAP_SIZE, 2)
        glVertex3f(i + ROAD_WIDTH / 2, MAP_SIZE, 2)
        glVertex3f(i - ROAD_WIDTH / 2, MAP_SIZE, 2)

        glVertex3f(-MAP_SIZE, i - ROAD_WIDTH / 2, 2)
        glVertex3f(MAP_SIZE, i - ROAD_WIDTH / 2, 2)
        glVertex3f(MAP_SIZE, i + ROAD_WIDTH / 2, 2)
        glVertex3f(-MAP_SIZE, i + ROAD_WIDTH / 2, 2)
    glEnd()

    draw_road_lines()


def draw_road_lines():
    # dashed center lines
    glColor3f(0.92, 0.82, 0.28)
    for road in range(-MAP_SIZE, MAP_SIZE + 1, BLOCK_SPACING):
        for p in range(-MAP_SIZE, MAP_SIZE, 80):
            glBegin(GL_QUADS)
            glVertex3f(road - 2, p, 2.4)
            glVertex3f(road + 2, p, 2.4)
            glVertex3f(road + 2, p + 38, 2.4)
            glVertex3f(road - 2, p + 38, 2.4)

            glVertex3f(p, road - 2, 2.4)
            glVertex3f(p + 38, road - 2, 2.4)
            glVertex3f(p + 38, road + 2, 2.4)
            glVertex3f(p, road + 2, 2.4)
            glEnd()


def draw_building_windows(bx, by, bw, bh, h):
    ww = 18
    wh = 22
    gap = 35
    vgap = 40
    border = 5
    cols_x = max(2, int(bw // gap))
    cols_y = max(2, int(bh // gap))
    floors = max(2, int(h // vgap))
    start_x = bx - ((cols_x - 1) * gap) / 2

    for floor in range(1, floors):
        z = floor * vgap
        for column in range(cols_x):
            wx = start_x + column * gap

            # front
            draw_cube(wx, by - bh / 2 - 0.8, z, ww + border, 2, wh + border, (0.08, 0.10, 0.12))
            draw_cube(wx, by - bh / 2 - 1.9, z, ww, 2, wh, (0.30, 0.67, 0.88))

            # back
            draw_cube(wx, by + bh / 2 + 0.8, z, ww + border, 2, wh + border, (0.08, 0.10, 0.12))
            draw_cube(wx, by + bh / 2 + 1.9, z, ww, 2, wh, (0.30, 0.67, 0.88))

    start_y = by - ((cols_y - 1) * gap) / 2

    for floor in range(1, floors):
        z = floor * vgap
        for column in range(cols_y):
            wy = start_y + column * gap

            # left
            draw_cube(bx - bw / 2 - 0.8, wy, z, 2, ww + border, wh + border, (0.08, 0.10, 0.12))
            draw_cube(bx - bw / 2 - 1.9, wy, z, 2, ww, wh, (0.30, 0.67, 0.88))

            # right
            draw_cube(bx + bw / 2 + 0.8, wy, z, 2, ww + border, wh + border, (0.08, 0.10, 0.12))
            draw_cube(bx + bw / 2 + 1.9, wy, z, 2, ww, wh, (0.30, 0.67, 0.88))


def draw_tree(x, y):
    glPushMatrix()
    glColor3f(0.28, 0.17, 0.08)
    glTranslatef(x, y, 2)
    gluCylinder(gluNewQuadric(), 5, 4, 34, 10, 5)
    glPopMatrix()

    glPushMatrix()
    glColor3f(0.12, 0.42, 0.16)
    glTranslatef(x, y, 45)
    gluSphere(gluNewQuadric(), 18, 12, 10)
    glPopMatrix()

    glPushMatrix()
    glColor3f(0.16, 0.50, 0.20)
    glTranslatef(x, y, 58)
    gluSphere(gluNewQuadric(), 14, 12, 10)
    glPopMatrix()


def draw_street_light(x, y):
    glPushMatrix()
    glColor3f(0.18, 0.20, 0.22)
    glTranslatef(x, y, 2)
    gluCylinder(gluNewQuadric(), 2.5, 2, 45, 8, 4)
    glPopMatrix()

    draw_cube(x, y, 48, 4, 4, 7, (0.95, 0.90, 0.62))


def draw_street_details():
    # trees and lamps inside block edges
    for x in range(-850, 851, 300):
        for y in range(-850, 851, 300):
            draw_tree(x + 85, y + 85)
            draw_street_light(x - 85, y + 85)


def draw_gas_station():
    zx, zy, zw, zh = interactive_zones["gas_station"]

    glPushMatrix()
    glColor3f(0.66, 0.67, 0.65)
    glTranslatef(zx, zy, 2.5)
    glBegin(GL_QUADS)
    glVertex3f(-zw / 2, -zh / 2, 0)
    glVertex3f(zw / 2, -zh / 2, 0)
    glVertex3f(zw / 2, zh / 2, 0)
    glVertex3f(-zw / 2, zh / 2, 0)
    glEnd()
    glPopMatrix()

    draw_cube(zx, zy + 25, 20, 70, 35, 40, (0.92, 0.90, 0.82))
    draw_cube(zx, zy + 6, 28, 50, 2, 10, (0.18, 0.48, 0.68))

    # canopy
    draw_cube(zx, zy - 25, 36, 98, 58, 6, (0.88, 0.12, 0.12))
    draw_cube(zx, zy - 25, 39.5, 98, 58, 2, (0.96, 0.96, 0.92))

    for px in (zx - 35, zx + 35):
        draw_cube(px, zy - 25, 18, 6, 6, 36, (0.88, 0.88, 0.84))

    # pumps
    for px in (zx - 20, zx + 20):
        draw_cube(px, zy - 25, 10, 8, 10, 20, (0.86, 0.12, 0.12))
        draw_cube(px, zy - 30.5, 13, 5, 1, 6, (0.15, 0.18, 0.20))


def draw_safe_house():
    zx, zy, zw, zh = interactive_zones["safe_house"]

    draw_cube(zx, zy, 30, 85, 70, 60, (0.70, 0.64, 0.54))
    draw_cube(zx, zy, 64, 95, 80, 8, (0.25, 0.19, 0.15))
    draw_cube(zx, zy - 35.5, 18, 20, 2, 35, (0.20, 0.12, 0.07))

    # windows
    draw_cube(zx - 25, zy - 35.8, 34, 16, 2, 18, (0.08, 0.10, 0.12))
    draw_cube(zx - 25, zy - 37, 34, 12, 2, 14, (0.30, 0.67, 0.88))
    draw_cube(zx + 25, zy - 35.8, 34, 16, 2, 18, (0.08, 0.10, 0.12))
    draw_cube(zx + 25, zy - 37, 34, 12, 2, 14, (0.30, 0.67, 0.88))


def draw_city():
    for bx, by, bw, bh, r, g, b, h in buildings:
        # main building
        draw_cube(bx, by, h / 2, bw, bh, h, (r, g, b))

        # bottom trim
        draw_cube(bx, by, 7, bw + 3, bh + 3, 14, (r * 0.72, g * 0.72, b * 0.72))

        # rooftop
        draw_cube(bx, by, h + 8, bw * 0.45, bh * 0.45, 16, (r * 0.72, g * 0.72, b * 0.72))

        # roof cap
        draw_cube(bx, by, h + 17, bw * 0.50, bh * 0.50, 3, (0.34, 0.35, 0.34))

        draw_building_windows(bx, by, bw, bh, h)

        if int(h) % 3 == 0:
            glPushMatrix()
            glColor3f(0.30, 0.30, 0.32)
            glTranslatef(bx, by, h + 17)
            gluCylinder(gluNewQuadric(), 2.5, 1, 42, 8, 4)
            glPopMatrix()

    draw_gas_station()
    draw_safe_house()
    draw_street_details()


def drawWORLD():
    draw_ground()
    draw_city()
