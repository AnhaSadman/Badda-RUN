from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *


# ============================================================
# PLAYER SCALE
# ============================================================

# Original player height was approximately 270 units.
#
# 270 * 0.15 = approximately 40 units.
#
# This makes the player small relative to the city.

PLAYER_SCALE = 0.15


# ============================================================
# PLAYER
# ============================================================

def draw_player(
    player_pos,
    player_angle,
    first_person,
    game_over
):

    px, py, pz = player_pos


    # ========================================================
    # ORIGINAL PLAYER DIMENSIONS
    # ========================================================
    #
    # We KEEP the original dimensions.
    #
    # PLAYER_SCALE scales the complete model afterward.
    #
    # This preserves the proportions of your A3 player.
    # ========================================================

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


    # ========================================================
    # COLORS
    # ========================================================

    GREEN = (
        0,
        0.35,
        0.05
    )

    BLUE = (
        0,
        0,
        1
    )

    SKIN = (
        1,
        0.75,
        0.55
    )

    BLACK = (
        0.05,
        0.05,
        0.05
    )

    RED = (
        1,
        0,
        0
    )

    GRAY = (
        0.5,
        0.5,
        0.5
    )


    # ========================================================
    # PLAYER TRANSFORM
    # ========================================================

    glPushMatrix()

    # Player world position

    glTranslatef(
        px,
        py,
        pz
    )


    # Player rotation

    if game_over:

        glRotatef(
            90,
            1,
            0,
            0
        )

    else:

        glRotatef(
            player_angle,
            0,
            0,
            1
        )


    # ========================================================
    # SCALE ENTIRE PLAYER
    # ========================================================
    #
    # This is the important change.
    #
    # Everything below automatically becomes 15% of its
    # original size:
    #
    # body
    # head
    # legs
    # arms
    # gun
    #
    # Player height:
    #
    # approximately 270 -> approximately 40 units
    # ========================================================

    glScalef(
        PLAYER_SCALE,
        PLAYER_SCALE,
        PLAYER_SCALE
    )


    # ========================================================
    # BODY
    # ========================================================

    glColor3f(
        *GREEN
    )

    glPushMatrix()

    glTranslatef(
        0,
        0,
        leg_height +
        body_height / 2
    )

    glScalef(
        body_width,
        body_depth,
        body_height
    )

    glutSolidCube(1)

    glPopMatrix()


    # ========================================================
    # HEAD
    # ========================================================

    if not first_person:

        glColor3f(
            *BLACK
        )

        glPushMatrix()

        glTranslatef(
            0,
            0,
            leg_height +
            body_height +
            head_radius
        )

        gluSphere(
            gluNewQuadric(),
            head_radius,
            12,
            8
        )

        glPopMatrix()


    # ========================================================
    # EYES
    # ========================================================

    if not first_person:

        glColor3f(
            *RED
        )

        for x in (
            -12,
            12
        ):

            glPushMatrix()

            glTranslatef(
                x,
                head_radius - 5,
                leg_height +
                body_height +
                head_radius +
                5
            )

            gluSphere(
                gluNewQuadric(),
                6,
                8,
                6
            )

            glPopMatrix()


    # ========================================================
    # LEGS
    # ========================================================

    glColor3f(
        *BLUE
    )

    for x in (
        -25,
        25
    ):

        glPushMatrix()

        glTranslatef(
            x,
            0,
            leg_height / 2
        )

        gluCylinder(
            gluNewQuadric(),
            leg_top_radius,
            leg_bottom_radius,
            leg_height,
            10,
            6
        )

        glPopMatrix()


    # ========================================================
    # ARMS
    # ========================================================

    glColor3f(
        *SKIN
    )


    # Left arm

    glPushMatrix()

    glTranslatef(
        -18,
        25,
        leg_height +
        body_height -
        40
    )

    glRotatef(
        -90,
        1,
        0,
        0
    )

    gluCylinder(
        gluNewQuadric(),
        arm_radius,
        arm_radius,
        arm_length,
        10,
        6
    )

    glPopMatrix()


    # Right arm

    glPushMatrix()

    glTranslatef(
        18,
        25,
        leg_height +
        body_height -
        40
    )

    glRotatef(
        -90,
        1,
        0,
        0
    )

    gluCylinder(
        gluNewQuadric(),
        arm_radius,
        arm_radius,
        arm_length,
        10,
        6
    )

    glPopMatrix()


    # ========================================================
    # GUN
    # ========================================================

    glColor3f(
        *GRAY
    )

    glPushMatrix()

    glTranslatef(
        0,
        100,
        leg_height +
        body_height -
        40
    )

    glScalef(
        20,
        gun_length,
        20
    )

    glutSolidCube(1)

    glPopMatrix()


    # ========================================================
    # RESTORE TRANSFORM
    # ========================================================

    glPopMatrix()