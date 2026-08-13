from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *


def drawWORLD(GRID_LENGTH, GRID_SIZE):

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
