import math
import time
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
from OpenGL.GLU import *
import random
import world
from draw_player import draw_player

# Camera

camera_radius = 120
camera_angle = 0
camera_height = 85

first_person = False
fovY = 120


# Game Map
screen_width = 0
screen_height = 0


# Game Stats

player_life_remaining = 5
game_score = 0
player_bullet_missed = 0


# Player
player_pos = [100, 150, 0]
player_angle = 0
player_speed = 8
rotation_speed = 5
PLAYER_LIMIT = world.MAP_SIZE - 30


# Bullets
bullets = []
bullet_speed = 300
bullet_size = 2


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

    angle = math.radians(
        player_angle
    )

    # ========================================================
    # SAME PLAYER FORWARD DIRECTION
    # ========================================================

    forward_x = -math.sin(angle)
    forward_y = math.cos(angle)


    # ========================================================
    # SMALL PLAYER / SMALL GUN
    # ========================================================
    #
    # Original gun muzzle distance:
    # approximately 100
    #
    # Player scale:
    # 0.15
    #
    # New muzzle distance:
    # 100 * 0.15 = 15
    #
    # The bullet therefore starts at the actual scaled gun
    # muzzle instead of 100 units away from the tiny player.
    # ========================================================

    gun_muzzle_distance = 15

    start_x = (
        player_pos[0] +
        forward_x *
        gun_muzzle_distance
    )

    start_y = (
        player_pos[1] +
        forward_y *
        gun_muzzle_distance
    )


    # Original muzzle height:
    # 160
    #
    # Scaled:
    # 160 * 0.15 = 24

    start_z = 24


    bullets.append({

        "x": start_x,
        "y": start_y,
        "z": start_z,

        "dx": forward_x,
        "dy": forward_y,

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
            abs(bullet["x"]) > world.MAP_SIZE or
            abs(bullet["y"]) > world.MAP_SIZE
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

        player_pos = [100, 150, 0]
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

    # ========================================================
    # PROJECTION
    # ========================================================

    glMatrixMode(GL_PROJECTION)

    glLoadIdentity()

    aspect_ratio = screen_width / screen_height

    gluPerspective(
        fovY,
        aspect_ratio,
        0.1,
        5000
    )

    glMatrixMode(GL_MODELVIEW)

    glLoadIdentity()


    # ========================================================
    # FPP
    # ========================================================

    if first_person:

        # ----------------------------------------------------
        # PLAYER FORWARD DIRECTION
        # ----------------------------------------------------
        #
        # KEEP YOUR WORKING A3 CONVENTION.
        # ----------------------------------------------------

        angle = math.radians(
            player_angle
        )

        forward_x = -math.sin(angle)
        forward_y = math.cos(angle)


        # ----------------------------------------------------
        # CAMERA POSITION
        # ----------------------------------------------------

        eye_x = (
            player_pos[0] +
            forward_x * 5
        )

        eye_y = (
            player_pos[1] +
            forward_y * 5
        )

        # Player is now approximately 40 units tall.
        # Put the camera near the head.

        eye_z = 32


        # ----------------------------------------------------
        # CAMERA LOOK DIRECTION
        # ----------------------------------------------------

        if cheat_mode and gun_follow:

            # Existing cheat + FPP gun-follow behavior.

            camera_direction_angle = player_angle

        elif cheat_mode and not gun_follow:

            # Existing locked-camera behavior.

            camera_direction_angle = locked_camera_angle

        else:

            # Normal FPP follows player.

            camera_direction_angle = player_angle


        camera_direction = math.radians(
            camera_direction_angle
        )


        look_x_direction = (
            -math.sin(camera_direction)
        )

        look_y_direction = (
            math.cos(camera_direction)
        )


        look_x = (
            eye_x +
            look_x_direction * 500
        )

        look_y = (
            eye_y +
            look_y_direction * 500
        )

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
#TPP
    else:

        angle = math.radians(player_angle)

        forward_x = -math.sin(angle)
        forward_y = math.cos(angle)

        # Opposite of player's forward direction
        backward_x = -forward_x
        backward_y = -forward_y

        # Distance behind player
        tpp_distance = 40

        cam_x = (
            player_pos[0] +
            backward_x * tpp_distance
        )

        cam_y = (
            player_pos[1] +
            backward_y * tpp_distance
        )

        # Camera height
        cam_z = 50

        # Look slightly above player's feet
        target_x = player_pos[0]
        target_y = player_pos[1]
        target_z = 22

        gluLookAt(
            cam_x,
            cam_y,
            cam_z,

            target_x,
            target_y,
            target_z,

            0,
            0,
            1
        )
        
        
def show_status():
    draw_text(10, screen_height - 30, f"Player life Remaining: {player_life_remaining}")
    draw_text(10, screen_height - 60, f"Game Score: {game_score}")
    draw_text(10, screen_height - 90, f"Player Bullet Missed: {player_bullet_missed}")
    
    
 

def showScreen():

    #SKY
    glClearColor(
        0.22,
        0.42,
        0.72,
        1.0
    )

    glClear(
        GL_COLOR_BUFFER_BIT |
        GL_DEPTH_BUFFER_BIT
    )

    glLoadIdentity()


    # Use current monitor/window size

    glViewport(
        0,
        0,
        screen_width,
        screen_height
    )


    # Camera

    setupCamera()

    world.world_player_x = player_pos[0]
    world.world_player_y = player_pos[1]

    world.drawWORLD()

    show_status()

    draw_player(
        player_pos,
        player_angle,
        first_person,
        game_over
    )

    draw_bullets()

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
