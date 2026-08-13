import math
import time
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
from OpenGL.GLU import *
import random

# Camera

camera_radius = 700
camera_angle = 90
camera_height = 500
first_person = False
fovY = 120


# Game Map

GRID_LENGTH = 700
GRID_SIZE = 15


# Game Stats

player_life_remaining = 5
game_score = 0
player_bullet_missed = 0


# Player
player_pos = [0, 0, 0]
player_angle = 0
player_speed = 30
rotation_speed = 10
PLAYER_LIMIT = GRID_LENGTH - 80


# Bullets
bullets = []
bullet_speed = 1000
bullet_size = 10

# Game State
game_over = False
game_paused = False
last_time = time.perf_counter()






def shoot(is_cheat=False):

    global bullets

    angle = math.radians(player_angle)

    # Same direction as player movement and gun
    forward_x = -math.sin(angle)
    forward_y = math.cos(angle)

    # Start at the gun muzzle
    start_x = (
        player_pos[0] +
        forward_x * 100
    )

    start_y = (
        player_pos[1] +
        forward_y * 100
    )

    start_z = 160

    bullets.append({
        "x": start_x,
        "y": start_y,
        "z": start_z,

        "dx": forward_x,
        "dy": forward_y,

        # Remember whether this is a cheat bullet
        "cheat": is_cheat
    })

       
def draw_bullets():

    for bullet in bullets:

        glColor3f(1, 1, 0)

        glPushMatrix()

        glTranslatef(
            bullet["x"],
            bullet["y"],
            bullet["z"]
        )

        glScalef(
            bullet_size,
            bullet_size,
            bullet_size
        )

        glutSolidCube(1)

        glPopMatrix()


   

def update_bullets(delta_time):

    global bullets
    global enemies
    global player_bullet_missed
    global game_over
    global game_score

    remaining_bullets = []


    for bullet in bullets:

        #  MOVE BULLET 

        bullet["x"] += (
            bullet["dx"] *
            bullet_speed *
            delta_time
        )

        bullet["y"] += (
            bullet["dy"] *
            bullet_speed *
            delta_time
        )



        #  BULLET LEFT GRID 

        if (
            abs(bullet["x"]) > GRID_LENGTH or
            abs(bullet["y"]) > GRID_LENGTH
        ):

            # ONLY normal bullets count as misses
            if not bullet.get("cheat", False):

                player_bullet_missed += 1

                if player_bullet_missed >= 10:

                    game_over = True


            # Cheat bullets simply disappear
            continue


        # Bullet is still alive
        remaining_bullets.append(bullet)


    bullets = remaining_bullets
    
            

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1,1,1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    # Set up an orthographic projection that matches window coordinates
    gluOrtho2D(0, 1000, 0, 800)  # left, right, bottom, top

    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Draw text at (x, y) in screen coordinates
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    # Restore original projection and modelview matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def CANVAS():

    #FLOOR GRID

    cell_size = (GRID_LENGTH * 2) / GRID_SIZE

    glBegin(GL_QUADS)

    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):

            x1 = -GRID_LENGTH + i * cell_size
            y1 = -GRID_LENGTH + j * cell_size

            x2 = x1 + cell_size
            y2 = y1 + cell_size


            # Checkerboard color
            if (i + j) % 2 == 0:
                glColor3f(0.8, 0.8, 0.8)
            else:
                glColor3f(0.3, 0.3, 0.3)


            glVertex3f(x1, y1, 0)
            glVertex3f(x2, y1, 0)
            glVertex3f(x2, y2, 0)
            glVertex3f(x1, y2, 0)

    glEnd()



    #BOUNDARY WALLS

    height = 150
    thickness = 20


    # Front wall
    glColor3f(1,0,0)

    glPushMatrix()
    glTranslatef(0, -GRID_LENGTH, height/2)
    glScalef(GRID_LENGTH*2, thickness, height)
    glutSolidCube(1)
    glPopMatrix()



    # Back wall
    glColor3f(0,1,0)

    glPushMatrix()
    glTranslatef(0, GRID_LENGTH, height/2)
    glScalef(GRID_LENGTH*2, thickness, height)
    glutSolidCube(1)
    glPopMatrix()



    # Left wall
    glColor3f(0,0,1)

    glPushMatrix()
    glTranslatef(GRID_LENGTH,0,height/2)
    glScalef(thickness, GRID_LENGTH*2, height)
    glutSolidCube(1)
    glPopMatrix()



    # Right wall
    glColor3f(1,0,1)

    glPushMatrix()
    glTranslatef(-GRID_LENGTH,0,height/2)
    glScalef(thickness, GRID_LENGTH*2, height)
    glutSolidCube(1)
    glPopMatrix()
    
    

def keyboardListener(key, x, y):
    global cheat_shoot_timer
    global player_pos
    global player_angle
    global game_over
    global player_bullet_missed
    global game_score
    global bullets
    global enemies
    global first_person
    global camera_height
    global camera_angle
    global cheat_mode
    global game_paused
    global gun_follow
    global locked_camera_angle
    global player_life_remaining
    
    #  RESTART 

    if key == b'r' or key == b'R':

        player_pos = [0, 0, 0]
        player_angle = 0
        player_life_remaining = 5
        game_over = False
        player_bullet_missed = 0
        game_score = 0

        bullets.clear()

        first_person = False

        camera_angle = 90
        camera_height = 500


        # Reset automatic gun following

        gun_follow = True
        locked_camera_angle = 0



        return

    #  PAUSE 

    if key == b' ':

        if not game_over:

            game_paused = not game_paused

        return

    #  CHEAT MODE 

    if key == b'c' or key == b'C':

        cheat_mode = not cheat_mode

        return
    
    # Automatic Gun Following

    if key == b'v' or key == b'V':

        # V only works in cheat mode + first-person mode
        if cheat_mode and first_person:

            if gun_follow:

                # Turn gun following OFF
                # Save the current camera direction
                locked_camera_angle = player_angle

                gun_follow = False

            else:

                # Turn gun following ON
                gun_follow = True

        return


    #  GAME OVER 

    if game_over:
        return
    
    
    #  PAUSED 

    if game_paused:
        return


    #  NORMAL ROTATION 

    if key == b'a':

        player_angle += rotation_speed


    if key == b'd':

        player_angle -= rotation_speed


    # Keep angle between 0 and 360

    if player_angle >= 360:
        player_angle -= 360


    if player_angle < 0:
        player_angle += 360


    #  NORMAL MOVEMENT 

    angle = math.radians(player_angle)

    forward_x = -math.sin(angle)
    forward_y = math.cos(angle)


    new_x = player_pos[0]
    new_y = player_pos[1]


    if key == b'w':

        new_x += forward_x * player_speed
        new_y += forward_y * player_speed


    if key == b's':

        new_x -= forward_x * player_speed
        new_y -= forward_y * player_speed


    #  BOUNDARY 

    if abs(new_x) < PLAYER_LIMIT:

        player_pos[0] = new_x


    if abs(new_y) < PLAYER_LIMIT:

        player_pos[1] = new_y       

def specialKeyListener(key,x,y):

    global camera_height
    global camera_angle


    if first_person:
        return


    if key == GLUT_KEY_UP:

        camera_height += 20


    if key == GLUT_KEY_DOWN:

        camera_height -= 20


    if key == GLUT_KEY_LEFT:

        camera_angle += 3


    if key == GLUT_KEY_RIGHT:

        camera_angle -= 3


def mouseListener(button, state, x, y):

    global first_person

    #  GAME OVER 

    if game_over:
        return


    #  LEFT CLICK 

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:

        if not game_paused:

            shoot()


    #  RIGHT CLICK 

    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:

        if not game_paused:

            first_person = not first_person

def setupCamera():

    global camera_radius
    global camera_angle
    global camera_height
    global first_person

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    gluPerspective(fovY,1.25,0.1,3000)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


    if first_person:

        #  FIRST PERSON CAMERA 

        # Camera position always stays with the player

        angle = math.radians(player_angle)

        forward_x = -math.sin(angle)
        forward_y = math.cos(angle)

        eye_x = player_pos[0] + forward_x * 35
        eye_y = player_pos[1] + forward_y * 35
        eye_z = 215
        
        #  CAMERA LOOK DIRECTION 

        if cheat_mode and gun_follow:

            # Camera follows the gun
            camera_direction_angle = player_angle

        elif cheat_mode and not gun_follow:

            # Camera stays locked
            camera_direction_angle = locked_camera_angle

        else:

            # Normal FPP camera follows player
            camera_direction_angle = player_angle


        camera_direction = math.radians(
            camera_direction_angle
        )

        look_x_direction = -math.sin(camera_direction)
        look_y_direction = math.cos(camera_direction)


        look_x = eye_x + look_x_direction * 500
        look_y = eye_y + look_y_direction * 500
        look_z = eye_z
        
        gluLookAt(
            eye_x,
            eye_y,
            eye_z,

            look_x,
            look_y,
            look_z,

            0,
            0,
            1
        )


    else:

        angle = math.radians(camera_angle)

        cam_x = camera_radius * math.cos(angle)
        cam_y = camera_radius * math.sin(angle)

        gluLookAt(

            cam_x,
            cam_y,
            camera_height,

            0,
            0,
            0,

            0,
            0,
            1
        )


def show_status():
    draw_text(10, 770, f"Player life Remaining: {player_life_remaining}")
    draw_text(10, 740, f"Game Score: {game_score}")
    draw_text(10, 710, f"Player Bullet Missed: {player_bullet_missed}")
    
    
def draw_player():

    global player_pos, player_angle
    global first_person


    px, py, pz = player_pos



    #  DIMENSIONS 

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



    #  COLORS 

    GREEN = (0,0.35,0.05)
    BLUE = (0,0,1)
    SKIN = (1,0.75,0.55)

    BLACK = (0.05,0.05,0.05)

    RED = (1,0,0)

    GRAY = (0.5,0.5,0.5)



    glPushMatrix()

    glTranslatef(
        px,
        py,
        pz
    )


    if game_over:

        # Player lies on the floor

        glRotatef(
            90,
            1,
            0,
            0
        )

    else:

        # Normal player rotation

        glRotatef(
            player_angle,
            0,
            0,
            1
        )



    #  BODY 

    glColor3f(*GREEN)

    glPushMatrix()

    glTranslatef(
        0,
        0,
        leg_height + body_height/2
    )

    glScalef(
        body_width,
        body_depth,
        body_height
    )

    glutSolidCube(1)

    glPopMatrix()



    #  HEAD 

#  HEAD 

    if not first_person:

        glColor3f(*BLACK)

        glPushMatrix()

        glTranslatef(
            0,
            0,
            leg_height + body_height + head_radius
        )

        gluSphere(
            gluNewQuadric(),
            head_radius,
            20,
            20
        )

        glPopMatrix()



    #  EYES 

    if not first_person:

        glColor3f(*RED)

        for x in [-12, 12]:

            glPushMatrix()

            glTranslatef(
                x,
                head_radius - 5,
                leg_height + body_height + head_radius + 5
            )

            gluSphere(
                gluNewQuadric(),
                6,
                15,
                15
            )

            glPopMatrix()

    #  LEGS 

    glColor3f(*BLUE)


    for x in [-25,25]:

        glPushMatrix()

        glTranslatef(
            x,
            0,
            leg_height/2
        )

        gluCylinder(
            gluNewQuadric(),
            leg_top_radius,
            leg_bottom_radius,
            leg_height,
            20,
            20
        )

        glPopMatrix()



    #  ARMS 

    glColor3f(*SKIN)



    # left arm

    glPushMatrix()

    glTranslatef(
        -18,
        25,
        leg_height+body_height-40
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
        15,
        15
    )


    glPopMatrix()



    # right arm

    glPushMatrix()

    glTranslatef(
        18,
        25,
        leg_height+body_height-40
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
        15,
        15
    )


    glPopMatrix()



    #  GUN 

    glColor3f(*GRAY)


    glPushMatrix()


    glTranslatef(
        0,
        100,
        leg_height+body_height-40
    )


    glScalef(
        20,
        gun_length,
        20
    )


    glutSolidCube(1)


    glPopMatrix()



    glPopMatrix()
    

def showScreen():
    """
    Display function to render the game scene:
    - Clears the screen and sets up the camera.
    - Draws everything of the screen
    """
    # Clear color and depth buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()  # Reset modelview matrix
    glViewport(0, 0, 1000, 800)  # Set viewport size

    setupCamera()  # Configure camera perspective

    # Draw the grid (game floor)
    CANVAS()
    show_status()
    draw_player()
    draw_bullets()

    # Swap buffers for smooth rendering (double buffering)
    glutSwapBuffers()




def animate():

    global last_time

    current_time = time.perf_counter()

    delta_time = current_time - last_time

    last_time = current_time


    # Prevent huge jumps

    if delta_time > 0.1:

        delta_time = 0.1


    if not game_over and not game_paused:

        # Bullets
        update_bullets(delta_time)

    


    glutPostRedisplay()    

# Main function to set up OpenGL window and loop
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)  # Double buffering, RGB color, depth test
    glutInitWindowSize(1000, 800)  # Window size
    glutInitWindowPosition(0, 0)  # Window position
    wind = glutCreateWindow(b"3D OpenGL Intro")  # Create the window
    glEnable(GL_DEPTH_TEST)
    glutDisplayFunc(showScreen)  # Register display function
    glutKeyboardFunc(keyboardListener)  # Register keyboard listener
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(animate)  # Register the idle function to move the bullet automatically

    glutMainLoop()  # Enter the GLUT main loop

if __name__ == "__main__":
    main()
