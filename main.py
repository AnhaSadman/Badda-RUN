import math
import time
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
from OpenGL.GLU import *
import random
from world import drawWORLD
from draw_player import draw_player

# Camera

camera_radius = 700
camera_angle = 90
camera_height = 500
first_person = False
fovY = 120


# Game Map

GRID_LENGTH = 700
GRID_SIZE = 15

screen_width = 0
screen_height = 0


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


# Enemies
enemies = []
MAX_ENEMIES = 5
enemy_speed = 20
enemy_body_radius = 35
enemy_head_radius = 20
enemy_spawn_distance = 250


# Game State
game_over = False
game_paused = False
last_time = time.perf_counter()


# Cheat Mode
cheat_mode = False
cheat_rotation_speed = 120
cheat_shoot_interval = 0.15
cheat_shoot_timer = 0
gun_follow = True
locked_camera_angle = 0


def initialize():
    global screen_width, screen_height
    screen_width = glutGet(GLUT_SCREEN_WIDTH)
    screen_height = glutGet(GLUT_SCREEN_HEIGHT)

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


        bullet_hit = False


        #  CHECK ENEMY COLLISION 

        for enemy in enemies:

            dx = bullet["x"] - enemy["x"]
            dy = bullet["y"] - enemy["y"]

            distance = math.sqrt(
                dx * dx +
                dy * dy
            )


            if distance < enemy_body_radius + bullet_size:

                game_score += 1

                enemies.remove(enemy)

                bullet_hit = True

                break


        # Bullet killed an enemy
        if bullet_hit:
            continue


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
    gluOrtho2D(
        0,
        screen_width,
        0,
        screen_height
    )  # left, right, bottom, top

    
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
        enemies.clear()

        first_person = False

        camera_angle = 90
        camera_height = 500

        # Reset cheat mode

        cheat_mode = False

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

    aspect_ratio = screen_width / screen_height
    gluPerspective(fovY, aspect_ratio, 0.1, 3000)

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
    
    
 

def showScreen():
    # Clear color and depth buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()  # Reset modelview matrix
    glViewport(0, 0, screen_width, screen_height)  # Set viewport size

    setupCamera()  # Configure camera perspective

    # Draw the grid (game floor)
    drawWORLD(GRID_LENGTH, GRID_SIZE)
    show_status()
    draw_player(player_pos,player_angle,first_person,game_over)
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
    initialize()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)  # Double buffering, RGB color, depth test
    glutInitWindowSize(screen_width, screen_height)
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
