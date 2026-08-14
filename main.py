import math
import time
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
from OpenGL.GLU import *
import world
from draw_player import draw_player

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
player_pos = [100, 150, 0]
player_angle = 0
player_speed = 8
rotation_speed = 5
PLAYER_LIMIT = world.MAP_SIZE - 30

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

# pressed_keys is shared by on-foot movement and car movement
player_in_car = False
pressed_keys = set()


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
    glTranslatef(0, 8, 20)
    glRotatef(-28, 1, 0, 0)
    glScalef(22, 3, 10)
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
    glRotatef(28, 1, 0, 0)
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
        if b'a' in pressed_keys:
            car_angle += car_turn_speed
        if b'd' in pressed_keys:
            car_angle -= car_turn_speed

    angle_rad = math.radians(car_angle)
    forward_x = -math.sin(angle_rad)
    forward_y = math.cos(angle_rad)

    new_cx = car_x + forward_x * car_speed
    new_cy = car_y + forward_y * car_speed

    limit = world.MAP_SIZE - 50

    # move on the x axis only if it stays in bounds and doesn't land inside a building
    test_cx = new_cx
    if abs(test_cx) > limit:
        test_cx = max(-limit, min(test_cx, limit))
        car_speed = 0
    if world.is_colliding(test_cx, car_y, world.CAR_RADIUS):
        car_speed = 0
    else:
        car_x = test_cx

    # move on the y axis the same way, so the car slides along a wall instead of clipping through it
    test_cy = new_cy
    if abs(test_cy) > limit:
        test_cy = max(-limit, min(test_cy, limit))
        car_speed = 0
    if world.is_colliding(car_x, test_cy, world.CAR_RADIUS):
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
        if world.is_colliding(bullet["x"], bullet["y"], bullet_size):
            continue

        if abs(bullet["x"]) > world.MAP_SIZE or abs(bullet["y"]) > world.MAP_SIZE:
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


def showScreen():
    glClearColor(0.22, 0.42, 0.72, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    if screen_width > 0 and screen_height > 0:
        glViewport(0, 0, screen_width, screen_height)

    setupCamera()
    world.drawWORLD()
    show_status()

    if not player_in_car:
        draw_player(player_pos, player_angle, first_person, game_over)

    draw_car()
    draw_bullets()

    glutSwapBuffers()


def animate():
    global last_time, player_angle, cheat_shoot_timer

    current_time = time.perf_counter()
    delta_time = min(current_time - last_time, 0.1)
    last_time = current_time

    update_car()

    if game_over or game_paused:
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
            if abs(new_x) < PLAYER_LIMIT and not world.is_colliding(new_x, player_pos[1], world.PLAYER_RADIUS):
                player_pos[0] = new_x
            if abs(new_y) < PLAYER_LIMIT and not world.is_colliding(player_pos[0], new_y, world.PLAYER_RADIUS):
                player_pos[1] = new_y

    if cheat_mode:
        cheat_shoot_timer += delta_time
        if cheat_shoot_timer >= cheat_shoot_interval:
            cheat_shoot_timer = 0
            player_angle = (player_angle + cheat_rotation_speed * delta_time) % 360
            shoot(is_cheat=True)

    update_bullets(delta_time)
    glutPostRedisplay()


def keyboardListener(key, x, y):
    global player_pos, player_angle
    global game_over, player_bullet_missed, game_score, bullets, enemies
    global first_person, camera_height, camera_angle
    global cheat_mode, game_paused, gun_follow, locked_camera_angle
    global player_life_remaining, player_in_car
    global car_x, car_y, car_z, car_speed, car_angle
    global cheat_shoot_timer

    nk = key.lower() if isinstance(key, bytes) else key

    # restart, always available
    if nk in (b'r',):
        player_pos = [100, 150, 0]
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
        return

    # pause
    if nk == b' ':
        if not game_over:
            game_paused = not game_paused
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
