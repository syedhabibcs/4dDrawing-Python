from OpenGL.GL import *
from OpenGL.GLUT import *
import numpy as np
import math
import sys

def draw():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # clear the screen
    glLoadIdentity()  # reset position
    refresh2d()  # set mode to 2d
    glTranslatef(_width / 2, _height / 2, 0)
    glScalef(100, 100, 1)

    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    for (poly, I_V) in _polygonToDrawInfo:
        if I_V[0] >= 0:
            glColor3f(I_V[0]+0.2, I_V[0]+0.1, I_V[0]/2)
            glBegin(GL_POLYGON)
            for v in poly:
                glVertex2f(v[0], v[1])
            glEnd()

    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    for (poly, I_V) in _polygonToDrawInfo:
        if I_V[0] >= 0:
            glColor3f(0, 1, 1)
            glBegin(GL_POLYGON)
            for v in poly:
                glVertex2f(v[0], v[1])
            glEnd()

    glutSwapBuffers()


def init(window_title):
    glutInit()  # initialize glut
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
    glutInitWindowSize(_width, _height)  # set window size
    glutInitWindowPosition(0, 0)  # set window position
    glutCreateWindow(b":)")  # create window with title
    glutSetWindowTitle(window_title)
    glutDisplayFunc(draw)  # set draw function callback
    glutKeyboardFunc(key_pressed)
    glutIdleFunc(draw)  # draw all the time
    glutMainLoop()


def key_pressed(*args):
    global _polygonToDrawInfo

    # If escape is pressed, kill everything.
    if args[0] == b'\x1b':
        writeOutput()
        sys.exit()

    elif args[0] == b'w':
        radianDegree = math.radians(_rotateSpeed)
        ry = [[math.cos(radianDegree), 0, -math.sin(radianDegree), 0], [0, 1, 0, 0],
              [math.sin(radianDegree), 0, math.cos(radianDegree), 0], [0, 0, 0, 1]]
        for c in range(len(_cords)):
            _cords[c] = np.matmul(_cords[c], ry)

    elif args[0] == b's':
        radianDegree = math.radians(-_rotateSpeed)
        ry = [[math.cos(radianDegree), 0, -math.sin(radianDegree), 0], [0, 1, 0, 0],
              [math.sin(radianDegree), 0, math.cos(radianDegree), 0], [0, 0, 0, 1]]
        for c in range(len(_cords)):
            _cords[c] = np.matmul(_cords[c], ry)

    elif args[0] == b'a':
        radianDegree = math.radians(-_rotateSpeed)
        rx = [[1, 0, 0, 0], [0, math.cos(radianDegree), -math.sin(radianDegree), 0],
              [0, math.sin(radianDegree), math.cos(radianDegree), 0], [0, 0, 0, 1]]
        for c in range(len(_cords)):
            _cords[c] = np.matmul(_cords[c], rx)

    elif args[0] == b'd':
        radianDegree = math.radians(_rotateSpeed)
        rx = [[1, 0, 0, 0], [0, math.cos(radianDegree), -math.sin(radianDegree), 0],
              [0, math.sin(radianDegree), math.cos(radianDegree), 0], [0, 0, 0, 1]]
        for c in range(len(_cords)):
                _cords[c] = np.matmul(_cords[c], rx)

    _polygonToDrawInfo = calculate2d_points()


def writeOutput():
    file = open("output.txt", 'w')  # create a file
    file.write(_title)   # write object type

    for c in range(len(_cells)):
        file.write('-{:d}\n'.format(c+1))  # write cell number
        for v in _cells[c]:  # write vertex and adjacent
            file.write('-{:d} {:d} {:d} {:d}\n'.format(v[0] + 1, v[1] + 1, v[2] + 1, v[3] + 1))

    file.write('0\n')

    for v in range(len(_cords)):
        file.write('-{:d} {:6f} {:6f} {:6f} {:6f}\n'.format(v + 1, _cords[v][0], _cords[v][1], _cords[v][2], _cords[v][3]))

    file.write("0\n")
    file.close()


def refresh2d():
    glViewport(0, 0, _width, _height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, _width, 0.0, _height, 0.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def readfile(filename):
    cellsRotationSystem = []
    vertexCords = []
    input_file = open(filename, "r")
    title = input_file.readline();
    v, c, f, e = input_file.readline().strip().split();
    v, c, f, e = int(v), int(c), int(f), int(e)
    for i in range(c):
        line = input_file.readline()  # cell number
        assert ((-int(line.strip())) - 1 == i)
        currCell = []
        line = input_file.readline().strip()
        while line is not "0":
            line = line.split()
            currRotation = [(-int(line[0])) - 1]

            for j in range(1, len(line), 2):
                currRotation.append(int(line[j]) - 1)
            line = input_file.readline().strip()
            currCell.append(currRotation)
        cellsRotationSystem.append(currCell)

    assert (input_file.readline().strip() == "0")

    for i in range(v):
        line = input_file.readline().strip().split()
        currCord = []
        for j in range(1, len(line)):
            currCord.append(float(line[j]))
        vertexCords.append(currCord)
    input_file.close()
    return title, cellsRotationSystem, vertexCords


def construct_face(i, j, cell):  # i=vertex and j=adjacent vertex
    completed = False;
    x = i
    y = j
    face = [x]
    while not completed:
        face.append(y)
        # find x in the rotation of y
        currZPos = len(cell)
        for k in range(len(cell)):
            if cell[k][0] == y:
                currZPos = k

        z = cell[currZPos].index(x) - 1
        if z == 0:
            z = -1
        x = y
        y = cell[currZPos][z]
        if y == i:
            completed = True
    return face


def project_face4d(face, cords):
    polygon = []

    for corner in face:
        corner_vertex = list(cords[corner])
        corner_vertex.append(1)

        projectedPoint = np.subtract(corner_vertex, np.multiply(_Q, (np.dot(corner_vertex, _E) / np.dot(_Q, _E))))
        projectedPoint = np.divide(projectedPoint, projectedPoint[-1])
        polygon.append(projectedPoint[:3])

    return polygon


def project_face3d(face):
    polygon = []

    for corner in face:
        corner_vertex = list(corner)
        corner_vertex.append(1)

        Q = np.subtract(corner_vertex, np.multiply(_view, (np.dot(corner_vertex, _screen) / np.dot(_view, _screen))))
        Q = np.divide(Q, Q[-1])
        polygon.append((Q[1], Q[2]))

    return polygon


def calculate_intensity_and_distance(face_cords):
    first_vector = np.subtract(face_cords[1], face_cords[0])
    second_vector = np.subtract(face_cords[-1], face_cords[0])
    normal = np.cross(first_vector, second_vector)
    unit_normal = np.divide(normal, np.dot(normal, normal))

    # calculate centre
    centre = [0, 0, 0]
    for f in face_cords:
        centre[0] += f[0]
        centre[1] += f[1]
        centre[2] += f[2]
    centre = np.divide(centre, len(face_cords))
    light_minus_centre = np.subtract(_lightSource, centre)
    u = np.divide(light_minus_centre, np.dot(light_minus_centre, light_minus_centre))

    # calculate distance to v
    vector_to_view = np.subtract(np.divide(_view, _view[-1])[:-1], centre)

    return np.dot(u, unit_normal), np.dot(vector_to_view, vector_to_view)  # (intensity, distance)


def calculate2d_points():
    projectedFaces3d = []   # [ (face, (intensity, distance)) ]
    for c in range(len(_cells)):
        # project C into Σ from point Q
        # - Make faces from rotation system
        # - Project each vertex of face to E from Q

        currCellFaces = []
        traversedEdges = []
        projectedFaces4d = []

        # - Make faces from rotation system
        for v in range(len(_cells[c])):  # for each vertex in cell
            for av in range(1, len(_cells[c][v])):  # for each adjacent vertex
                if not ((_cells[c][v][0], _cells[c][v][av]) in traversedEdges):
                    # Construct the face
                    currFace = construct_face(_cells[c][v][0], _cells[c][v][av], _cells[c])
                    for tv in range(-1, len(currFace) - 1):  # add the traversed edges
                        traversedEdges.append((currFace[tv], currFace[tv + 1]))
                    currCellFaces.append(currFace)

        # - Project each vertex of face to E from Q (4d to 3d)
        for f in currCellFaces:
            projectedFaces4d.append(project_face4d(f, _cords))

        # Project from 3d to 2d
        for f in projectedFaces4d:
            projectedFaces3d.append((project_face3d(f), calculate_intensity_and_distance(f)))

    # [(cords, (intensity, distance))]
    projectedFaces3d = sorted(projectedFaces3d, key=lambda x: x[1][1])
    projectedFaces3d.reverse()

    return projectedFaces3d


def main():
    
    if len(sys.argv) != 2:
        print("Expecting only input filename")
        sys.exit()

    # global variables
    global _fileName, _rotateSpeed, _width, _height
    global _title, _cells, _cords, _E, _Q
    global _view, _screen, _lightSource, _polygonToDrawInfo

    _fileName = sys.argv[1]

    _rotateSpeed = 4
    _width, _height = 700, 700  # window size
    _title, _cells, _cords = readfile(_fileName)

    # _cells : [v, adjacentV, adjacentV, adjacentV]
    # _cords : [cordsV1, cordsV2, ...]

    # 4D cords
    _E = (0, 0, 0, 1, 0)  # 3d sub-space
    _Q = (0, 0, 0, 20, 1)  # Projection point
    # 3D cords
    _view = [100, 0, 0, 1]  # choose a viewpoint V in E
    _screen = [1, 0, 0, 10]  # choose a viewing screen screen in E  (the w=10 term here manages the depth)
    _lightSource = [5, 0, 0]

    _polygonToDrawInfo = calculate2d_points()
    init(_title)

if __name__ == '__main__':
    main()