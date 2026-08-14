from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random

MAP_SIZE=1000
ROAD_WIDTH=100
SIDEWALK_WIDTH=22
BLOCK_SPACING=300

buildings=[]
building_colors=[
    (0.78,0.68,0.62),
    (0.64,0.70,0.74),
    (0.76,0.62,0.52),
    (0.58,0.65,0.69),
    (0.82,0.78,0.68),
    (0.68,0.57,0.52),
    (0.74,0.72,0.64)
]

interactive_zones={
    "gas_station":(-300,-300,120,120),
    "safe_house":(300,300,120,120)
}

random.seed(8)

# Buildings
for road_x in range(-MAP_SIZE,MAP_SIZE,BLOCK_SPACING):
    for road_y in range(-MAP_SIZE,MAP_SIZE,BLOCK_SPACING):
        x=road_x+BLOCK_SPACING/2
        y=road_y+BLOCK_SPACING/2
        bw=random.randint(110,140)
        bh=random.randint(110,140)
        h=random.randint(140,320)
        r,g,b=random.choice(building_colors)
        buildings.append((x,y,bw,bh,r,g,b,h))

def draw_cube(x,y,z,sx,sy,sz,color):
    glPushMatrix()
    glColor3f(*color)
    glTranslatef(x,y,z)
    glScalef(sx,sy,sz)
    glutSolidCube(1)
    glPopMatrix()

def draw_ground():
    # Grass
    glColor3f(0.28,0.48,0.25)
    glBegin(GL_QUADS)
    glVertex3f(-MAP_SIZE,-MAP_SIZE,-2)
    glVertex3f(MAP_SIZE,-MAP_SIZE,-2)
    glVertex3f(MAP_SIZE,MAP_SIZE,-2)
    glVertex3f(-MAP_SIZE,MAP_SIZE,-2)
    glEnd()

    # Sidewalks
    glColor3f(0.72,0.71,0.67)
    for i in range(-MAP_SIZE,MAP_SIZE+1,BLOCK_SPACING):
        glBegin(GL_QUADS)

        glVertex3f(i-ROAD_WIDTH/2-SIDEWALK_WIDTH,-MAP_SIZE,1)
        glVertex3f(i-ROAD_WIDTH/2,-MAP_SIZE,1)
        glVertex3f(i-ROAD_WIDTH/2,MAP_SIZE,1)
        glVertex3f(i-ROAD_WIDTH/2-SIDEWALK_WIDTH,MAP_SIZE,1)

        glVertex3f(i+ROAD_WIDTH/2,-MAP_SIZE,1)
        glVertex3f(i+ROAD_WIDTH/2+SIDEWALK_WIDTH,-MAP_SIZE,1)
        glVertex3f(i+ROAD_WIDTH/2+SIDEWALK_WIDTH,MAP_SIZE,1)
        glVertex3f(i+ROAD_WIDTH/2,MAP_SIZE,1)

        glVertex3f(-MAP_SIZE,i-ROAD_WIDTH/2-SIDEWALK_WIDTH,1)
        glVertex3f(MAP_SIZE,i-ROAD_WIDTH/2-SIDEWALK_WIDTH,1)
        glVertex3f(MAP_SIZE,i-ROAD_WIDTH/2,1)
        glVertex3f(-MAP_SIZE,i-ROAD_WIDTH/2,1)

        glVertex3f(-MAP_SIZE,i+ROAD_WIDTH/2,1)
        glVertex3f(MAP_SIZE,i+ROAD_WIDTH/2,1)
        glVertex3f(MAP_SIZE,i+ROAD_WIDTH/2+SIDEWALK_WIDTH,1)
        glVertex3f(-MAP_SIZE,i+ROAD_WIDTH/2+SIDEWALK_WIDTH,1)

        glEnd()

    # Roads
    glColor3f(0.09,0.10,0.12)
    glBegin(GL_QUADS)
    for i in range(-MAP_SIZE,MAP_SIZE+1,BLOCK_SPACING):
        glVertex3f(i-ROAD_WIDTH/2,-MAP_SIZE,2)
        glVertex3f(i+ROAD_WIDTH/2,-MAP_SIZE,2)
        glVertex3f(i+ROAD_WIDTH/2,MAP_SIZE,2)
        glVertex3f(i-ROAD_WIDTH/2,MAP_SIZE,2)

        glVertex3f(-MAP_SIZE,i-ROAD_WIDTH/2,2)
        glVertex3f(MAP_SIZE,i-ROAD_WIDTH/2,2)
        glVertex3f(MAP_SIZE,i+ROAD_WIDTH/2,2)
        glVertex3f(-MAP_SIZE,i+ROAD_WIDTH/2,2)
    glEnd()

    draw_road_lines()

def draw_road_lines():
    # Dashed center lines
    glColor3f(0.92,0.82,0.28)
    for road in range(-MAP_SIZE,MAP_SIZE+1,BLOCK_SPACING):
        for p in range(-MAP_SIZE,MAP_SIZE,80):
            glBegin(GL_QUADS)
            glVertex3f(road-2,p,2.4)
            glVertex3f(road+2,p,2.4)
            glVertex3f(road+2,p+38,2.4)
            glVertex3f(road-2,p+38,2.4)

            glVertex3f(p,road-2,2.4)
            glVertex3f(p+38,road-2,2.4)
            glVertex3f(p+38,road+2,2.4)
            glVertex3f(p,road+2,2.4)
            glEnd()

def draw_building_windows(bx,by,bw,bh,h):
    ww=18
    wh=22
    gap=35
    vgap=40
    border=5
    cols_x=max(2,int(bw//gap))
    cols_y=max(2,int(bh//gap))
    floors=max(2,int(h//vgap))
    start_x=bx-((cols_x-1)*gap)/2

    for floor in range(1,floors):
        z=floor*vgap
        for column in range(cols_x):
            wx=start_x+column*gap

            # Front
            draw_cube(wx,by-bh/2-0.8,z,ww+border,2,wh+border,(0.08,0.10,0.12))
            draw_cube(wx,by-bh/2-1.9,z,ww,2,wh,(0.30,0.67,0.88))

            # Back
            draw_cube(wx,by+bh/2+0.8,z,ww+border,2,wh+border,(0.08,0.10,0.12))
            draw_cube(wx,by+bh/2+1.9,z,ww,2,wh,(0.30,0.67,0.88))

    start_y=by-((cols_y-1)*gap)/2

    for floor in range(1,floors):
        z=floor*vgap
        for column in range(cols_y):
            wy=start_y+column*gap

            # Left
            draw_cube(bx-bw/2-0.8,wy,z,2,ww+border,wh+border,(0.08,0.10,0.12))
            draw_cube(bx-bw/2-1.9,wy,z,2,ww,wh,(0.30,0.67,0.88))

            # Right
            draw_cube(bx+bw/2+0.8,wy,z,2,ww+border,wh+border,(0.08,0.10,0.12))
            draw_cube(bx+bw/2+1.9,wy,z,2,ww,wh,(0.30,0.67,0.88))

def draw_tree(x,y):
    glPushMatrix()
    glColor3f(0.28,0.17,0.08)
    glTranslatef(x,y,2)
    gluCylinder(gluNewQuadric(),5,4,34,10,5)
    glPopMatrix()

    glPushMatrix()
    glColor3f(0.12,0.42,0.16)
    glTranslatef(x,y,45)
    gluSphere(gluNewQuadric(),18,12,10)
    glPopMatrix()

    glPushMatrix()
    glColor3f(0.16,0.50,0.20)
    glTranslatef(x,y,58)
    gluSphere(gluNewQuadric(),14,12,10)
    glPopMatrix()

def draw_street_light(x,y):
    glPushMatrix()
    glColor3f(0.18,0.20,0.22)
    glTranslatef(x,y,2)
    gluCylinder(gluNewQuadric(),2.5,2,45,8,4)
    glPopMatrix()

    draw_cube(x,y,48,4,4,7,(0.95,0.90,0.62))

def draw_street_details():
    # Trees and lamps inside block edges
    for x in range(-850,851,300):
        for y in range(-850,851,300):
            draw_tree(x+85,y+85)
            draw_street_light(x-85,y+85)

def draw_gas_station():
    zx,zy,zw,zh=interactive_zones["gas_station"]

    glPushMatrix()
    glColor3f(0.66,0.67,0.65)
    glTranslatef(zx,zy,2.5)
    glBegin(GL_QUADS)
    glVertex3f(-zw/2,-zh/2,0)
    glVertex3f(zw/2,-zh/2,0)
    glVertex3f(zw/2,zh/2,0)
    glVertex3f(-zw/2,zh/2,0)
    glEnd()
    glPopMatrix()

    draw_cube(zx,zy+25,20,70,35,40,(0.92,0.90,0.82))
    draw_cube(zx,zy+6,28,50,2,10,(0.18,0.48,0.68))

    # Canopy
    draw_cube(zx,zy-25,36,98,58,6,(0.88,0.12,0.12))
    draw_cube(zx,zy-25,39.5,98,58,2,(0.96,0.96,0.92))

    for px in (zx-35,zx+35):
        draw_cube(px,zy-25,18,6,6,36,(0.88,0.88,0.84))

    # Pumps
    for px in (zx-20,zx+20):
        draw_cube(px,zy-25,10,8,10,20,(0.86,0.12,0.12))
        draw_cube(px,zy-30.5,13,5,1,6,(0.15,0.18,0.20))

def draw_safe_house():
    zx,zy,zw,zh=interactive_zones["safe_house"]

    draw_cube(zx,zy,30,85,70,60,(0.70,0.64,0.54))
    draw_cube(zx,zy,64,95,80,8,(0.25,0.19,0.15))
    draw_cube(zx,zy-35.5,18,20,2,35,(0.20,0.12,0.07))

    # Windows
    draw_cube(zx-25,zy-35.8,34,16,2,18,(0.08,0.10,0.12))
    draw_cube(zx-25,zy-37,34,12,2,14,(0.30,0.67,0.88))
    draw_cube(zx+25,zy-35.8,34,16,2,18,(0.08,0.10,0.12))
    draw_cube(zx+25,zy-37,34,12,2,14,(0.30,0.67,0.88))

def draw_city():
    for bx,by,bw,bh,r,g,b,h in buildings:
        # Main building
        draw_cube(bx,by,h/2,bw,bh,h,(r,g,b))

        # Bottom trim
        draw_cube(bx,by,7,bw+3,bh+3,14,(r*0.72,g*0.72,b*0.72))

        # Rooftop
        draw_cube(bx,by,h+8,bw*0.45,bh*0.45,16,(r*0.72,g*0.72,b*0.72))

        # Roof cap
        draw_cube(bx,by,h+17,bw*0.50,bh*0.50,3,(0.34,0.35,0.34))

        draw_building_windows(bx,by,bw,bh,h)

        if int(h)%3==0:
            glPushMatrix()
            glColor3f(0.30,0.30,0.32)
            glTranslatef(bx,by,h+17)
            gluCylinder(gluNewQuadric(),2.5,1,42,8,4)
            glPopMatrix()

    draw_gas_station()
    draw_safe_house()
    draw_street_details()

def draw_player(player_x,player_y,player_angle,in_vehicle=False):
    if in_vehicle:
        return

    glPushMatrix()
    glTranslatef(player_x,player_y,0)
    glRotatef(player_angle,0,0,1)
    glScalef(0.30,0.30,0.30)

    # Body
    glPushMatrix()
    glColor3f(0.68,0.50,0.88)
    glTranslatef(0,0,78)
    glScalef(0.75,0.55,1.25)
    glutSolidCube(50)
    glPopMatrix()

    # Head
    glPushMatrix()
    glColor3f(0.12,0.08,0.08)
    glTranslatef(0,0,135)
    gluSphere(gluNewQuadric(),21,12,12)
    glPopMatrix()

    # Legs
    for y in (12,-12):
        glPushMatrix()
        glColor3f(0.48,0.12,0.35)
        glTranslatef(0,y,48)
        glRotatef(180,1,0,0)
        gluCylinder(gluNewQuadric(),10,7,48,10,10)
        glPopMatrix()

    # Arms
    for y in (22,-22):
        glPushMatrix()
        glColor3f(1.0,0.8,0.65)
        glTranslatef(0,y,100)
        glRotatef(180,1,0,0)
        gluCylinder(gluNewQuadric(),7,6,42,10,10)
        glPopMatrix()

    glPopMatrix()

def draw_car_body():
    glBegin(GL_QUADS)

    # Top
    glVertex3f(-17,-30,10)
    glVertex3f(17,-30,10)
    glVertex3f(20,25,8)
    glVertex3f(-20,25,8)

    # Left
    glVertex3f(-17,-30,4)
    glVertex3f(-17,-30,10)
    glVertex3f(-20,25,8)
    glVertex3f(-20,25,4)

    # Right
    glVertex3f(17,-30,4)
    glVertex3f(20,25,4)
    glVertex3f(20,25,8)
    glVertex3f(17,-30,10)

    # Front
    glVertex3f(-20,25,4)
    glVertex3f(20,25,4)
    glVertex3f(16,34,6)
    glVertex3f(-16,34,6)

    # Rear
    glVertex3f(-17,-30,4)
    glVertex3f(17,-30,4)
    glVertex3f(17,-30,10)
    glVertex3f(-17,-30,10)

    glEnd()

def draw_car(car_x,car_y,car_angle):
    glPushMatrix()
    glTranslatef(car_x,car_y,3)
    glRotatef(car_angle,0,0,1)

    # Body
    glColor3f(0.82,0.02,0.07)
    draw_car_body()

    # Hood
    glPushMatrix()
    glColor3f(0.95,0.04,0.08)
    glTranslatef(0,20,10)
    glRotatef(-7,1,0,0)
    glScalef(30,25,3)
    glutSolidCube(1)
    glPopMatrix()

    # Cabin
    glPushMatrix()
    glColor3f(0.06,0.08,0.12)
    glTranslatef(0,-6,16)
    glScalef(25,27,10)
    glutSolidCube(1)
    glPopMatrix()

    # Windshield
    glPushMatrix()
    glColor3f(0.18,0.55,0.75)
    glTranslatef(0,8,20)
    glRotatef(-28,1,0,0)
    glScalef(22,3,10)
    glutSolidCube(1)
    glPopMatrix()

    # Roof
    glPushMatrix()
    glColor3f(0.04,0.05,0.08)
    glTranslatef(0,-7,23)
    glScalef(19,14,2)
    glutSolidCube(1)
    glPopMatrix()

    # Rear glass
    glPushMatrix()
    glColor3f(0.15,0.45,0.65)
    glTranslatef(0,-18,19)
    glRotatef(28,1,0,0)
    glScalef(20,3,8)
    glutSolidCube(1)
    glPopMatrix()

    # Wheels
    for x in (-18,18):
        for y in (-20,20):
            glPushMatrix()
            glColor3f(0.03,0.03,0.03)
            glTranslatef(x,y,6)
            glRotatef(90,0,1,0)
            gluCylinder(gluNewQuadric(),6,6,3,16,3)
            glPopMatrix()

    # Rims
    for x in (-18.2,18.2):
        for y in (-20,20):
            glPushMatrix()
            glColor3f(0.7,0.7,0.72)
            glTranslatef(x,y,6)
            glRotatef(90,0,1,0)
            gluDisk(gluNewQuadric(),0,3.5,12,1)
            glPopMatrix()

    # Lights
    for x in (-10,10):
        glPushMatrix()
        glColor3f(1.0,0.95,0.75)
        glTranslatef(x,32,8)
        glScalef(8,2,3)
        glutSolidCube(1)
        glPopMatrix()

        glPushMatrix()
        glColor3f(1.0,0.02,0.02)
        glTranslatef(x,-30.5,8)
        glScalef(8,2,3)
        glutSolidCube(1)
        glPopMatrix()

    # Side skirts
    for x in (-20,20):
        glPushMatrix()
        glColor3f(0.04,0.04,0.05)
        glTranslatef(x,-1,4)
        glScalef(2,45,3)
        glutSolidCube(1)
        glPopMatrix()

    # Spoiler stands
    for x in (-10,10):
        glPushMatrix()
        glColor3f(0.04,0.04,0.05)
        glTranslatef(x,-27,15)
        glScalef(2,2,9)
        glutSolidCube(1)
        glPopMatrix()

    # Spoiler
    glPushMatrix()
    glColor3f(0.04,0.04,0.05)
    glTranslatef(0,-28,19)
    glScalef(28,5,2)
    glutSolidCube(1)
    glPopMatrix()

    glPopMatrix()

def drawWORLD():
    draw_ground()
    draw_city()