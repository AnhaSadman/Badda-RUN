import math
import time
import random
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
from OpenGL.GLU import *

#WORLD 

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


#PLAYER MODEL

# scales the whole player model down so it looks right next to the city (original height ~270 units)
PLAYER_SCALE = 0.15


def draw_player(player_pos, player_angle, first_person, game_over):
    px, py, pz = player_pos

    # base dimensions, scaled by PLAYER_SCALE below rather than hardcoded small
    body_width = 80
    body_depth = 40
    body_height = 120

    head_radius = 35

    leg_height = 80
    leg_top_radius = 15
    leg_bottom_radius = 5

    arm_radius = 10
    arm_length = 55

    gun_length = 100

    GREEN = (0, 0.35, 0.05)
    BLUE = (0, 0, 1)
    SKIN = (1, 0.75, 0.55)
    BLACK = (0.05, 0.05, 0.05)
    RED = (1, 0, 0)
    GRAY = (0.5, 0.5, 0.5)

    glPushMatrix()

    # move to the player's world position
    glTranslatef(px, py, pz)

    # lie the model down when the game is over, otherwise face the movement angle
    if game_over:
        glRotatef(90, 1, 0, 0)
    else:
        glRotatef(player_angle, 0, 0, 1)

    # everything drawn below this line is scaled down to PLAYER_SCALE
    glScalef(PLAYER_SCALE, PLAYER_SCALE, PLAYER_SCALE)

    # body
    glColor3f(*GREEN)
    glPushMatrix()
    glTranslatef(0, 0, leg_height + body_height / 2)
    glScalef(body_width, body_depth, body_height)
    glutSolidCube(1)
    glPopMatrix()

    # head, hidden in first person so it doesn't block the view
    if not first_person:
        glColor3f(*BLACK)
        glPushMatrix()
        glTranslatef(0, 0, leg_height + body_height + head_radius)
        gluSphere(gluNewQuadric(), head_radius, 12, 8)
        glPopMatrix()

    # eyes
    if not first_person:
        glColor3f(*RED)
        for x in (-12, 12):
            glPushMatrix()
            glTranslatef(x, head_radius - 5, leg_height + body_height + head_radius + 5)
            gluSphere(gluNewQuadric(), 6, 8, 6)
            glPopMatrix()

    # legs
    glColor3f(*BLUE)
    for x in (-25, 25):
        glPushMatrix()
        glTranslatef(x, 0, leg_height / 2)
        gluCylinder(gluNewQuadric(), leg_top_radius, leg_bottom_radius, leg_height, 10, 6)
        glPopMatrix()

    # arms
    glColor3f(*SKIN)

    glPushMatrix()
    glTranslatef(-18, 25, leg_height + body_height - 40)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), arm_radius, arm_radius, arm_length, 10, 6)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(18, 25, leg_height + body_height - 40)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), arm_radius, arm_radius, arm_length, 10, 6)
    glPopMatrix()

    # gun
    glColor3f(*GRAY)
    glPushMatrix()
    glTranslatef(0, 100, leg_height + body_height - 40)
    glScalef(20, gun_length, 20)
    glutSolidCube(1)
    glPopMatrix()

    glPopMatrix()


#GAME MAIN

# camera
camera_radius = 120
camera_angle = 0
camera_height = 85
first_person = False
fovY = 120

# screen
screen_width = 0
screen_height = 0

# game stats
player_life_remaining = 5
game_score = 0
player_bullet_missed = 0

# player
player_pos = [200, 100, 0]
player_angle = 0
player_speed = 8
rotation_speed = 5
PLAYER_LIMIT = MAP_SIZE - 30

# bullets
bullets = []
bullet_speed = 1000
bullet_size = 2

# enemies
enemies = []
MAX_ENEMIES = 5
enemy_speed = 20
enemy_body_radius = 35
enemy_head_radius = 20
enemy_spawn_distance = 250

# game state
game_over = False
game_paused = False
last_time = time.perf_counter()
game_menu_open = False
menu_buttons = {}

# cheat mode
cheat_mode = False
cheat_rotation_speed = 120
cheat_shoot_interval = 0.15
cheat_shoot_timer = 0
gun_follow = True
locked_camera_angle = 0

# car
car_x = 160
car_y = 150
car_z = 0
car_angle = 0
car_speed = 0
car_max_speed = 20
car_acceleration = 0.5
car_friction = 0.3
car_turn_speed = 3

#steering
steering_wheel_angle = 0
STEER_MAX = 33
STEER_STEP = 6

# pressed_keys is shared by on-foot movement and car movement
player_in_car = False
pressed_keys = set()

# ===================== JUMP + RUN =====================

jumping = False
jump_velocity = 0.0

JUMP_HEIGHT = 40.0
JUMP_GRAVITY = 400.0
JUMP_VELOCITY = (2.0 * JUMP_GRAVITY * JUMP_HEIGHT) ** 0.5

RUN_SPEED = player_speed * 2

def start_jump():
    global jumping
    global jump_velocity

    if player_in_car:
        return

    if game_over or game_paused:
        return

    if not jumping and player_pos[2] <= 0:
        jumping = True
        jump_velocity = JUMP_VELOCITY
        
def update_jump(delta_time):
    global jumping
    global jump_velocity

    if not jumping:
        return

    jump_velocity -= JUMP_GRAVITY * delta_time
    player_pos[2] += jump_velocity * delta_time

    if player_pos[2] <= 0:
        player_pos[2] = 0
        jump_velocity = 0
        jumping = False


def initialize():
    global screen_width, screen_height
    screen_width = glutGet(GLUT_SCREEN_WIDTH)
    screen_height = glutGet(GLUT_SCREEN_HEIGHT)
    if screen_width == 0:
        screen_width = 1280
    if screen_height == 0:
        screen_height = 720


def draw_car_body():
    glBegin(GL_QUADS)

    glVertex3f(-17, -30, 10); glVertex3f(17, -30, 10)
    glVertex3f(20, 25, 8); glVertex3f(-20, 25, 8)

    glVertex3f(-17, -30, 4); glVertex3f(-17, -30, 10)
    glVertex3f(-20, 25, 8); glVertex3f(-20, 25, 4)

    glVertex3f(17, -30, 4); glVertex3f(20, 25, 4)
    glVertex3f(20, 25, 8); glVertex3f(17, -30, 10)

    glVertex3f(-20, 25, 4); glVertex3f(20, 25, 4)
    glVertex3f(16, 34, 6); glVertex3f(-16, 34, 6)

    glVertex3f(-17, -30, 4); glVertex3f(17, -30, 4)
    glVertex3f(17, -30, 10); glVertex3f(-17, -30, 10)

    glEnd()


def draw_car():
    glPushMatrix()
    glTranslatef(car_x, car_y, car_z)
    glRotatef(car_angle, 0, 0, 1)

    glColor3f(0.82, 0.02, 0.07)
    draw_car_body()

    # hood
    glPushMatrix()
    glColor3f(0.95, 0.04, 0.08)
    glTranslatef(0, 20, 10)
    glRotatef(-7, 1, 0, 0)
    glScalef(30, 25, 3)
    glutSolidCube(1)
    glPopMatrix()
    
    if not (first_person and player_in_car):
        # cabin
        glPushMatrix()
        glColor3f(0.06, 0.08, 0.12)
        glTranslatef(0, -6, 16)
        glScalef(25, 27, 10)
        glutSolidCube(1)
        glPopMatrix()
        
        # windshield
        glPushMatrix()
        glColor3f(0.18, 0.55, 0.75)
        glTranslatef(0, 7.8, 20)
        glRotatef(28, 1, 0, 0)
        glScalef(22, 0.5, 7)
        glutSolidCube(1)
        glPopMatrix()


    # roof
    glPushMatrix()
    glColor3f(0.04, 0.05, 0.08)
    glTranslatef(0, -7, 23)
    glScalef(19, 14, 2)
    glutSolidCube(1)
    glPopMatrix()

    # rear glass
    glPushMatrix()
    glColor3f(0.15, 0.45, 0.65)
    glTranslatef(0, -18, 19)
    glRotatef(-28, 1, 0, 0)
    glScalef(20, 3, 8)
    glutSolidCube(1)
    glPopMatrix()

    # wheels and rims
    q = gluNewQuadric()
    for wx in (-18, 18):
        for wy in (-20, 20):
            glPushMatrix()
            glColor3f(0.03, 0.03, 0.03)
            glTranslatef(wx, wy, 6)
            glRotatef(90, 0, 1, 0)
            gluCylinder(q, 6, 6, 3, 16, 3)
            glPopMatrix()

            glPushMatrix()
            glColor3f(0.7, 0.7, 0.72)
            glTranslatef(wx * (18.2 / 18), wy, 6)
            glRotatef(90, 0, 1, 0)
            gluDisk(gluNewQuadric(), 0, 3.5, 12, 1)
            glPopMatrix()

    # headlights
    for lx in (-10, 10):
        glPushMatrix()
        glColor3f(1.0, 0.95, 0.75)
        glTranslatef(lx, 32, 8)
        glScalef(8, 2, 3)
        glutSolidCube(1)
        glPopMatrix()

    # tail lights
    
    for lx in (-10, 10):
        draw_cube(lx, -30.3, 8, 8 + 1.5, 2, 3 + 1.5, (0.03, 0.03, 0.03))
        draw_cube(lx, -30.6, 8, 8, 2, 3, (1.0, 0.02, 0.02))
    
    for lx in (-10, 10):
        glPushMatrix()
        glColor3f(1.0, 0.02, 0.02)
        glTranslatef(lx, -30.5, 8)
        glScalef(8, 2, 3)
        glutSolidCube(1)
        glPopMatrix()

    # side skirts
    for sx in (-20, 20):
        glPushMatrix()
        glColor3f(0.04, 0.04, 0.05)
        glTranslatef(sx, -1, 4)
        glScalef(2, 45, 3)
        glutSolidCube(1)
        glPopMatrix()

    # spoiler stands
    for sx in (-10, 10):
        glPushMatrix()
        glColor3f(0.04, 0.04, 0.05)
        glTranslatef(sx, -27, 15)
        glScalef(2, 2, 9)
        glutSolidCube(1)
        glPopMatrix()

    # spoiler wing
    glPushMatrix()
    glColor3f(0.04, 0.04, 0.05)
    glTranslatef(0, -28, 19)
    glScalef(28, 5, 2)
    glutSolidCube(1)
    glPopMatrix()
    
    if first_person and player_in_car:
        glDisable(GL_DEPTH_TEST)
        draw_steering_wheel(steering_wheel_angle)
        glEnable(GL_DEPTH_TEST)

    glPopMatrix()

def draw_steering_wheel(angle_deg):
    glPushMatrix()
    glTranslatef(0, 14, 13)          # wheel position, lower z = lower wheel
    glRotatef(angle_deg, 0, 1, 0)    # steering spin, about the forward axis

    glColor3f(0.05, 0.05, 0.05)
    radius = 6
    tube = 0.9
    segments = 20
    q = gluNewQuadric()

    # points around the rim, in the wheel's local xz plane
    points = []
    for i in range(segments + 1):
        a = 2 * math.pi * i / segments
        points.append((math.sin(a) * radius, 0, math.cos(a) * radius))

    for i in range(segments):
        x1, y1, z1 = points[i]
        x2, y2, z2 = points[i + 1]
        dx, dz = x2 - x1, z2 - z1
        length = math.hypot(dx, dz)
        seg_angle = math.degrees(math.atan2(dx, dz))

        # short tube segment from point i to point i+1
        glPushMatrix()
        glTranslatef(x1, y1, z1)
        glRotatef(seg_angle, 0, 1, 0)
        gluCylinder(q, tube, tube, length, 10, 1)
        glPopMatrix()

        # sphere at the joint rounds the corner and hides the seam
        glPushMatrix()
        glTranslatef(x1, y1, z1)
        gluSphere(q, tube, 10, 10)
        glPopMatrix()

    # spokes
    for a_deg in (0, 120, 240):
        a = math.radians(a_deg)
        x = math.sin(a) * 3
        z = math.cos(a) * 3
        draw_cube(x, 0, z, 1, 1.5, 1, (0.05, 0.05, 0.05))

    # hub
    draw_cube(0, 0, 0, 3, 2, 3, (0.05, 0.05, 0.05))
    
    # hands gripping the rim, simple cylinders that spin with the wheel
    glColor3f(0.85, 0.65, 0.5)
    for side in (-1, 1):
        hx = side * radius * 0.85
        hz = -radius * 0.3
        glPushMatrix()
        glTranslatef(hx, -1, hz)
        glRotatef(90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 1.8, 1.8, 5, 8, 2)
        glPopMatrix()
    
    glPopMatrix()

def update_car():
    global car_x, car_y, car_speed, car_angle

    if not player_in_car:
        return

    if b'w' in pressed_keys:
        car_speed = min(car_speed + car_acceleration, car_max_speed)
    elif b's' in pressed_keys:
        car_speed = max(car_speed - car_acceleration, -car_max_speed / 2)
    else:
        if car_speed > 0:
            car_speed = max(car_speed - car_friction, 0.0)
        elif car_speed < 0:
            car_speed = min(car_speed + car_friction, 0.0)

    if abs(car_speed) > 0.1:
        turn_dir = 1 if car_speed > 0 else -1
        if b'a' in pressed_keys:
            car_angle += car_turn_speed * turn_dir
        if b'd' in pressed_keys:
            car_angle -= car_turn_speed * turn_dir

    angle_rad = math.radians(car_angle)
    forward_x = -math.sin(angle_rad)
    forward_y = math.cos(angle_rad)

    new_cx = car_x + forward_x * car_speed
    new_cy = car_y + forward_y * car_speed

    limit = MAP_SIZE - 50

    # move on the x axis only if it stays in bounds and doesn't land inside a building
    test_cx = new_cx
    if abs(test_cx) > limit:
        test_cx = max(-limit, min(test_cx, limit))
        car_speed = 0
    if is_colliding(test_cx, car_y, CAR_RADIUS):
        car_speed = 0
    else:
        car_x = test_cx

    # move on the y axis the same way, so the car slides along a wall instead of clipping through it
    test_cy = new_cy
    if abs(test_cy) > limit:
        test_cy = max(-limit, min(test_cy, limit))
        car_speed = 0
    if is_colliding(car_x, test_cy, CAR_RADIUS):
        car_speed = 0
    else:
        car_y = test_cy

    # keep player glued to car
    if player_in_car:
        player_pos[0] = car_x
        player_pos[1] = car_y


def shoot(is_cheat=False):
    angle = math.radians(player_angle)
    forward_x = -math.sin(angle)
    forward_y = math.cos(angle)

    gun_muzzle_distance = 15
    bullets.append({
        "x": player_pos[0] + forward_x * gun_muzzle_distance,
        "y": player_pos[1] + forward_y * gun_muzzle_distance,
        "z": 24,
        "dx": forward_x,
        "dy": forward_y,
        "cheat": is_cheat,
    })


def draw_bullets():
    glColor3f(1, 1, 0)
    for bullet in bullets:
        glPushMatrix()
        glTranslatef(bullet["x"], bullet["y"], bullet["z"])
        glScalef(bullet_size, bullet_size, bullet_size)
        glutSolidCube(1)
        glPopMatrix()


def update_bullets(delta_time):
    global bullets, enemies, player_bullet_missed, game_over, game_score

    remaining = []
    for bullet in bullets:
        bullet["x"] += bullet["dx"] * bullet_speed * delta_time
        bullet["y"] += bullet["dy"] * bullet_speed * delta_time

        hit = False
        # iterate over a snapshot so removing during the loop is safe
        for enemy in list(enemies):
            dx = bullet["x"] - enemy["x"]
            dy = bullet["y"] - enemy["y"]
            if math.hypot(dx, dy) < enemy_body_radius + bullet_size:
                game_score += 1
                if enemy in enemies:
                    enemies.remove(enemy)
                hit = True
                break

        if hit:
            continue

        # a bullet also stops if it hits a building instead of flying through it
        if is_colliding(bullet["x"], bullet["y"], bullet_size):
            continue

        if abs(bullet["x"]) > MAP_SIZE or abs(bullet["y"]) > MAP_SIZE:
            if not bullet.get("cheat", False):
                player_bullet_missed += 1
                if player_bullet_missed >= 10:
                    game_over = True
            continue

        remaining.append(bullet)

    bullets = remaining


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    if screen_width == 0 or screen_height == 0:
        return
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, screen_width, 0, screen_height)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def show_status():
    draw_text(10, screen_height - 30, f"Lives: {player_life_remaining}")
    draw_text(10, screen_height - 60, f"Score: {game_score}")
    draw_text(10, screen_height - 90, f"Missed: {player_bullet_missed}")
    if player_in_car:
        draw_text(10, screen_height - 120, f"IN CAR  speed={car_speed:.1f}")
    if game_over:
        cx = screen_width // 2 - 80
        cy = screen_height // 2
        draw_text(cx, cy, "GAME OVER - press R to restart")
    if game_paused:
        cx = screen_width // 2 - 40
        cy = screen_height // 2
        draw_text(cx, cy, "PAUSED")

def draw_pause_menu():
    # semi-transparent full screen overlay with Restart / Resume / Exit buttons
    if screen_width == 0 or screen_height == 0:
        return

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, screen_width, 0, screen_height)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glDisable(GL_DEPTH_TEST)
    glLoadIdentity()

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # dim the whole screen
    glColor4f(0, 0, 0, 0.65)
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(screen_width, 0)
    glVertex2f(screen_width, screen_height)
    glVertex2f(0, screen_height)
    glEnd()

    # three stacked buttons, centered on screen
    btn_w, btn_h, gap = 220, 50, 20
    cx = screen_width / 2
    cy = screen_height / 2
    labels = ["Restart", "Resume", "Exit"]
    menu_buttons.clear()

    for i, label in enumerate(labels):
        top = cy + (1 - i) * (btn_h + gap)
        bottom = top - btn_h
        left = cx - btn_w / 2
        right = cx + btn_w / 2

        glColor4f(0.15, 0.15, 0.18, 0.9)
        glBegin(GL_QUADS)
        glVertex2f(left, bottom)
        glVertex2f(right, bottom)
        glVertex2f(right, top)
        glVertex2f(left, top)
        glEnd()

        menu_buttons[label] = (left, bottom, right, top)

    glDisable(GL_BLEND)
    glEnable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

    # labels drawn after popping, draw_text sets up its own ortho each call
    for label, (left, bottom, right, top) in menu_buttons.items():
        text_x = left + btn_w / 2 - len(label) * 5
        text_y = bottom + btn_h / 2 - 6
        draw_text(text_x, text_y, label)


def handle_menu_click(label):
    # runs when a menu button is clicked
    global game_menu_open
    if label == "Restart":
        RestartGame()
        game_menu_open = False
    elif label == "Resume":
        game_menu_open = False
    elif label == "Exit":
        glutLeaveMainLoop()

def _forward_from_angle(deg):
    rad = math.radians(deg)
    return -math.sin(rad), math.cos(rad)


def setupCamera():
    global camera_radius, camera_angle, camera_height

    if screen_height == 0:
        return

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, screen_width / screen_height, 0.1, 5000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if first_person:
        # first person works for both on-foot and in-car
        if player_in_car:
            cam_angle_rad = math.radians(car_angle)
            fx = -math.sin(cam_angle_rad)
            fy = math.cos(cam_angle_rad)

            eye_x = car_x + fx * 5
            eye_y = car_y + fy * 5
            eye_z = car_z + 22

            look_dir = car_angle
        else:
            fx, fy = _forward_from_angle(player_angle)
            eye_x = player_pos[0] + fx * 5
            eye_y = player_pos[1] + fy * 5
            eye_z = 32

            if cheat_mode and not gun_follow:
                look_dir = locked_camera_angle
            else:
                look_dir = player_angle

        lx, ly = _forward_from_angle(look_dir)
        gluLookAt(
            eye_x, eye_y, eye_z,
            eye_x + lx * 500, eye_y + ly * 500, eye_z,
            0, 0, 1,
        )

    else:
        # third person follows the car when in car, the player when on foot
        if player_in_car:
            pivot_x, pivot_y = car_x, car_y
            follow_angle = car_angle
        else:
            pivot_x, pivot_y = player_pos[0], player_pos[1]
            follow_angle = player_angle

        fx, fy = _forward_from_angle(follow_angle)

        tpp_distance = 80
        cam_x = pivot_x - fx * tpp_distance
        cam_y = pivot_y - fy * tpp_distance
        cam_z = 60

        gluLookAt(
            cam_x, cam_y, cam_z,
            pivot_x, pivot_y, 20,
            0, 0, 1,
        )

def draw_minimap():
    if screen_width==0 or screen_height==0:
        return

    # Follow player or car
    if player_in_car:
        px,py=car_x,car_y
    else:
        px,py=player_pos[0],player_pos[1]

    map_size=220
    margin=20
    bottom_offset=60
    minimap_range=500

    # Bottom-left minimap
    glViewport(margin,margin+bottom_offset,map_size,map_size)

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(-minimap_range,minimap_range,-minimap_range,minimap_range,0.1,3000)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    gluLookAt(px,py,1200,px,py,0,0,1,0)

    # Background
    glDisable(GL_DEPTH_TEST)
    glColor3f(0.05,0.05,0.06)
    glBegin(GL_QUADS)
    glVertex3f(px-minimap_range,py-minimap_range,-5)
    glVertex3f(px+minimap_range,py-minimap_range,-5)
    glVertex3f(px+minimap_range,py+minimap_range,-5)
    glVertex3f(px-minimap_range,py+minimap_range,-5)
    glEnd()
    glEnable(GL_DEPTH_TEST)

    # Ground and roads
    draw_ground()

    # Minimap road lines
    glDisable(GL_DEPTH_TEST)
    glColor3f(1,0.9,0.1)

    for road in range(-MAP_SIZE,MAP_SIZE+1,BLOCK_SPACING):
        for p in range(-MAP_SIZE,MAP_SIZE,80):
            glBegin(GL_QUADS)

            glVertex3f(road-3,p,15)
            glVertex3f(road+3,p,15)
            glVertex3f(road+3,p+38,15)
            glVertex3f(road-3,p+38,15)

            glVertex3f(p,road-3,15)
            glVertex3f(p+38,road-3,15)
            glVertex3f(p+38,road+3,15)
            glVertex3f(p,road+3,15)

            glEnd()

    glEnable(GL_DEPTH_TEST)

    # Buildings
    for bx,by,bw,bh,r,g,b,h in buildings:
        glColor3f(r,g,b)
        glBegin(GL_QUADS)
        glVertex3f(bx-bw/2,by-bh/2,5)
        glVertex3f(bx+bw/2,by-bh/2,5)
        glVertex3f(bx+bw/2,by+bh/2,5)
        glVertex3f(bx-bw/2,by+bh/2,5)
        glEnd()

    # Gas station marker
    
    gx,gy,gw,gh=interactive_zones["gas_station"]

    glColor3f(1,0.15,0.15)
    glBegin(GL_QUADS)
    glVertex3f(gx-35,gy-22,12)
    glVertex3f(gx+35,gy-22,12)
    glVertex3f(gx+35,gy+22,12)
    glVertex3f(gx-35,gy+22,12)
    glEnd()

    # Safe house marker
    sx,sy,sw,sh=interactive_zones["safe_house"]

    glColor3f(0.1,1,0.25)
    glBegin(GL_QUADS)
    glVertex3f(sx-35,sy-22,12)
    glVertex3f(sx+35,sy-22,12)
    glVertex3f(sx+35,sy+22,12)
    glVertex3f(sx-35,sy+22,12)
    glEnd()
        
    
    # Car/player marker
    if player_in_car:
        glPushMatrix()
        glTranslatef(px,py,20)
        glRotatef(car_angle,0,0,1)

        glColor3f(1,0,0)
        glBegin(GL_QUADS)
        glVertex3f(-10,-16,0)
        glVertex3f(10,-16,0)
        glVertex3f(10,16,0)
        glVertex3f(-10,16,0)
        glEnd()

        glColor3f(0.1,0.1,0.1)
        glBegin(GL_QUADS)
        glVertex3f(-7,-5,1)
        glVertex3f(7,-5,1)
        glVertex3f(7,7,1)
        glVertex3f(-7,7,1)
        glEnd()

        glPopMatrix()

    else:
        glPushMatrix()
        glTranslatef(px,py,20)
        glRotatef(player_angle,0,0,1)

        # Player marker
        glColor3f(0,0.8,1)
        glBegin(GL_TRIANGLES)
        glVertex3f(0,25,0)
        glVertex3f(-17,-16,0)
        glVertex3f(17,-16,0)
        glEnd()

        glPopMatrix()

    # Restore minimap matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    # Full screen
    glViewport(0,0,screen_width,screen_height)

    # Border projection
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0,screen_width,0,screen_height)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glDisable(GL_DEPTH_TEST)

    x1=margin
    y1=margin+bottom_offset
    x2=margin+map_size
    y2=margin+bottom_offset+map_size

    # Outer black border
    glColor3f(0,0,0)
    glLineWidth(8)
    glBegin(GL_LINE_LOOP)
    glVertex2f(x1-4,y1-4)
    glVertex2f(x2+4,y1-4)
    glVertex2f(x2+4,y2+4)
    glVertex2f(x1-4,y2+4)
    glEnd()

    # Inner white border
    glColor3f(1,1,1)
    glLineWidth(3)
    glBegin(GL_LINE_LOOP)
    glVertex2f(x1,y1)
    glVertex2f(x2,y1)
    glVertex2f(x2,y2)
    glVertex2f(x1,y2)
    glEnd()

    glLineWidth(1)
    glEnable(GL_DEPTH_TEST)

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def showScreen():
    glClearColor(0.22,0.42,0.72,1.0)
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # Main view
    if screen_width>0 and screen_height>0:
        glViewport(0,0,screen_width,screen_height)

    setupCamera()
    drawWORLD()

    if not player_in_car:
        draw_player(player_pos,player_angle,first_person,game_over)

    draw_car()
    draw_bullets()
    
    if game_menu_open:
        draw_pause_menu()

    # Minimap
    draw_minimap()

    # HUD
    glViewport(0,0,screen_width,screen_height)
    show_status()

    glutSwapBuffers()



def animate():
    global last_time, player_angle, cheat_shoot_timer, steering_wheel_angle

    current_time = time.perf_counter()
    delta_time = min(current_time - last_time, 0.1)
    last_time = current_time
    
    update_jump(delta_time)

    update_car()

    if game_over or game_paused or game_menu_open:
        glutPostRedisplay()
        return

    # on-foot movement, uses pressed_keys so w+a, w+d etc. all work together
    if not player_in_car:
        moving = b'w' in pressed_keys or b's' in pressed_keys

        if b'a' in pressed_keys:
            player_angle = (player_angle + rotation_speed * delta_time * 60) % 360
        if b'd' in pressed_keys:
            player_angle = (player_angle - rotation_speed * delta_time * 60) % 360

        if moving:
            fx, fy = _forward_from_angle(player_angle)
            step = player_speed * delta_time * 60

            new_x = player_pos[0]
            new_y = player_pos[1]

            if b'w' in pressed_keys:
                new_x += fx * step
                new_y += fy * step
            if b's' in pressed_keys:
                new_x -= fx * step
                new_y -= fy * step

            # move on each axis separately so the player slides along a wall instead of clipping through it
            if abs(new_x) < PLAYER_LIMIT and not is_colliding(new_x, player_pos[1], PLAYER_RADIUS):
                player_pos[0] = new_x
            if abs(new_y) < PLAYER_LIMIT and not is_colliding(player_pos[0], new_y, PLAYER_RADIUS):
                player_pos[1] = new_y
                
    # steering wheel spins toward a/d, springs back to center when released
    if b'd' in pressed_keys:
        steering_wheel_angle = min(steering_wheel_angle + STEER_STEP, STEER_MAX)
    elif b'a' in pressed_keys:
        steering_wheel_angle = max(steering_wheel_angle - STEER_STEP, -STEER_MAX)
    else:
        steering_wheel_angle *= 0.85

    if cheat_mode:
        cheat_shoot_timer += delta_time
        if cheat_shoot_timer >= cheat_shoot_interval:
            cheat_shoot_timer = 0
            player_angle = (player_angle + cheat_rotation_speed * delta_time) % 360
            shoot(is_cheat=True)

    update_bullets(delta_time)
    glutPostRedisplay()
    
def RestartGame():
    global player_pos, player_angle
    global game_over, player_bullet_missed, game_score, bullets, enemies
    global first_person, camera_height, camera_angle
    global cheat_mode, game_paused, gun_follow, locked_camera_angle
    global player_life_remaining, player_in_car
    global car_x, car_y, car_z, car_speed, car_angle
    global cheat_shoot_timer

    player_pos = [200, 100, 0]
    player_angle = 0
    player_life_remaining = 5
    game_over = False
    player_bullet_missed = 0
    game_score = 0
    bullets.clear()
    enemies.clear()
    pressed_keys.clear()
    first_person = False
    camera_angle = 0
    camera_height = 85
    cheat_mode = False
    gun_follow = True
    locked_camera_angle = 0
    cheat_shoot_timer = 0
    player_in_car = False
    car_x, car_y, car_z = 160, 150, 0
    car_angle = 0
    car_speed = 0


def keyboardListener(key, x, y):
    global player_pos, player_angle
    global player_speed
    global jumping, jump_velocity
    global game_over, player_bullet_missed, game_score, bullets, enemies
    global first_person, camera_height, camera_angle
    global cheat_mode, game_paused, gun_follow, locked_camera_angle
    global player_life_remaining, player_in_car
    global car_x, car_y, car_z, car_speed, car_angle
    global cheat_shoot_timer, game_menu_open

    nk = key.lower() if isinstance(key, bytes) else key
    
    # esc toggles the pause menu
    if key == b'\x1b':
        global game_menu_open
        game_menu_open = not game_menu_open
        return

    # block all other input while the menu is open
    if game_menu_open:
        return

    # restart, always available
    if nk in (b'r',):
        player_pos = [200, 100, 0]
        jumping = False
        jump_velocity = 0.0
        player_angle = 0
        player_life_remaining = 5
        game_over = False
        player_bullet_missed = 0
        game_score = 0
        bullets.clear()
        enemies.clear()
        pressed_keys.clear()
        first_person = False
        camera_angle = 0
        camera_height = 85
        cheat_mode = False
        gun_follow = True
        locked_camera_angle = 0
        cheat_shoot_timer = 0
        player_in_car = False
        car_x, car_y, car_z = 160, 150, 0
        car_angle = 0
        car_speed = 0
        RestartGame()
        return
    
    if nk == b' ':
        start_jump()
        return
    
    # cheat toggle
    if nk == b'c':
        cheat_mode = not cheat_mode
        return

    # gun-follow toggle, cheat + first person only
    if nk == b'v':
        if cheat_mode and first_person:
            if gun_follow:
                locked_camera_angle = player_angle
                gun_follow = False
            else:
                gun_follow = True
        return

    # car entry / exit
    if nk == b'e':
        dist = math.hypot(player_pos[0] - car_x, player_pos[1] - car_y)
        if dist < 80:
            player_in_car = not player_in_car
            if player_in_car:
                player_pos[0] = car_x
                player_pos[1] = car_y
                player_pos[2] = 0
                pressed_keys.discard(b'w')
                pressed_keys.discard(b's')
            else:
                car_speed = 0
                pressed_keys.clear()
                # step the player a little away from the car so they don't spawn stuck inside it
                angle_rad = math.radians(car_angle)
                player_pos[0] = car_x - math.sin(angle_rad) * 45
                player_pos[1] = car_y + math.cos(angle_rad) * 45
        return

    if game_over or game_paused:
        return
    
        # J = jump
    if nk == b' ':
        start_jump()
        return

    # K = run
    if nk == b'k':
        player_speed = RUN_SPEED
        return

    # wasd, added to pressed_keys so multiple keys combine
    if nk in (b'w', b'a', b's', b'd'):
        pressed_keys.add(nk)
        return

    # shoot
    if nk == b'f':
        shoot()
        return


def keyboardUpListener(key, x, y):
    nk = key.lower() if isinstance(key, bytes) else key
    
    if nk == b'k':
        global player_speed
        player_speed = 8
        return
    
    pressed_keys.discard(nk)


def specialKeyListener(key, x, y):
    global camera_height, camera_angle
    if first_person:
        return
    if key == GLUT_KEY_UP:
        camera_height += 20
    elif key == GLUT_KEY_DOWN:
        camera_height -= 20
    elif key == GLUT_KEY_LEFT:
        camera_angle += 3
    elif key == GLUT_KEY_RIGHT:
        camera_angle -= 3


def mouseListener(button, state, x, y):
    global first_person

    if game_menu_open:
        if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
            # glut gives y from the top, flip it to match our bottom-up button rects
            click_y = screen_height - y
            for label, (left, bottom, right, top) in menu_buttons.items():
                if left <= x <= right and bottom <= click_y <= top:
                    handle_menu_click(label)
                    break
        return

    if game_over:
        return
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if not game_paused:
            shoot()
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        if not game_paused:
            first_person = not first_person
            


def main():
    glutInit()
    initialize()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(screen_width, screen_height)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Mini Game")
    glEnable(GL_DEPTH_TEST)
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutKeyboardUpFunc(keyboardUpListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(animate)
    glutMainLoop()


if __name__ == "__main__":
    main()
