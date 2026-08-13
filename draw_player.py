from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

def draw_player(player_pos,player_angle,first_person,game_over):
    px,py,pz=player_pos

    # Dimensions
    body_width=80
    body_depth=40
    body_height=120
    head_radius=35
    leg_height=80
    leg_top_radius=15
    leg_bottom_radius=5
    arm_radius=10
    arm_length=55
    gun_length=100

    # Colors
    GREEN=(0,0.35,0.05)
    BLUE=(0,0,1)
    SKIN=(1,0.75,0.55)
    BLACK=(0.05,0.05,0.05)
    RED=(1,0,0)
    GRAY=(0.5,0.5,0.5)

    glPushMatrix()
    glTranslatef(px,py,pz)

    if game_over:
        glRotatef(90,1,0,0)
    else:
        glRotatef(player_angle,0,0,1)

    # Body
    glColor3f(*GREEN)
    glPushMatrix()
    glTranslatef(0,0,leg_height+body_height/2)
    glScalef(body_width,body_depth,body_height)
    glutSolidCube(1)
    glPopMatrix()

    # Head
    if not first_person:
        glColor3f(*BLACK)
        glPushMatrix()
        glTranslatef(0,0,leg_height+body_height+head_radius)
        gluSphere(gluNewQuadric(),head_radius,20,20)
        glPopMatrix()

    # Eyes
    if not first_person:
        glColor3f(*RED)
        for x in (-12,12):
            glPushMatrix()
            glTranslatef(x,head_radius-5,leg_height+body_height+head_radius+5)
            gluSphere(gluNewQuadric(),6,15,15)
            glPopMatrix()

    # Legs
    glColor3f(*BLUE)
    for x in (-25,25):
        glPushMatrix()
        glTranslatef(x,0,leg_height/2)
        gluCylinder(gluNewQuadric(),leg_top_radius,leg_bottom_radius,leg_height,20,20)
        glPopMatrix()

    # Arms
    glColor3f(*SKIN)

    glPushMatrix()
    glTranslatef(-18,25,leg_height+body_height-40)
    glRotatef(-90,1,0,0)
    gluCylinder(gluNewQuadric(),arm_radius,arm_radius,arm_length,15,15)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(18,25,leg_height+body_height-40)
    glRotatef(-90,1,0,0)
    gluCylinder(gluNewQuadric(),arm_radius,arm_radius,arm_length,15,15)
    glPopMatrix()

    # Gun
    glColor3f(*GRAY)
    glPushMatrix()
    glTranslatef(0,100,leg_height+body_height-40)
    glScalef(20,gun_length,20)
    glutSolidCube(1)
    glPopMatrix()

    glPopMatrix()