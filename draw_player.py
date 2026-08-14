from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

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
