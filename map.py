import random
import pygame
import numpy
import math

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHT_GREY = (180, 180, 190)
DARK_GREY = (50, 50, 50)
YELLOW = (210, 220, 0)
GREEN = (0, 255, 0)
DARK_RED = (200, 0, 0)
LIGHT_GREEN = (144, 238, 144)


class Mapper:
    def __init__(self, SCREEN):
        self.connections_list = []
        self.starting_point = [random.randrange(5, 7), random.randrange(3, 5)]
        self.currnode = self.starting_point
        self.circle_diam = 20
        self.circle_line_width = 2
        self.line_width = 4
        self.grid_line_width = 1
        self.w, self.h = 8, 15
        self.margin = 120
        self.fill_percent = 0.4
        self.diagonal_percent = 0

        # pygame.init()
        self.screen = SCREEN
        # self.done = False
        self.clock = pygame.time.Clock()
        # self.paused = False
        # self.stopped = False
        self.done = False
        self.boss_count = 0

        self.nodelist = numpy.zeros((self.h, self.w))
        self.nodetypes = numpy.zeros((self.h, self.w))

    def addnode(self, coordinates):
        self.nodelist[coordinates[0]][coordinates[1]] = 1
        # nodetypes[coordinates[0]][coordinates[1]] = type

    def one_away(self, coordinates):
        # Given a set of coordinates, return all the nodes that immediately
        # surround it.
        diag_chance = self.diagonal_percent
        check_list = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if random.random() < diag_chance or i * j == 0:
                    if [i, j] != [0, 0] and 0 <= coordinates[0] + i < self.h and 0 <= coordinates[
                        1] + j < self.w:  # not self, not off the edge
                        check_list.append([coordinates[0] + i, coordinates[1] + j])
        return check_list

    def empty_nodes(self):
        # take every non-empty node in nodelist, check all the surrounding empty
        # nodes, and return the coords of a non-empty node with the highest
        # number of empty surrounding nodes

        coord_dict = {}
        nonzero = numpy.transpose(numpy.nonzero(self.nodelist))
        for entry in nonzero:
            counter = 0
            for i in self.one_away(entry):
                if self.nodelist[i[0]][i[1]] == 0:
                    counter += 1
            coord_dict[tuple(entry)] = counter
        for k, v in list(coord_dict.items()):
            if v < max(coord_dict.values()):
                del coord_dict[k]
        return random.choice(list(coord_dict.keys()))

    def connection_check(self, coords1, coords2):
        if [coords1, coords2] in self.connections_list or [coords2, coords1] in self.connections_list:
            return True
        else:
            return False

    def cross_check(self, coords1, coords2):
        if abs((coords1[0] - coords2[0]) * (coords1[1] - coords2[1])) == 1:  # diagonal
            swapped_one = [coords1[0], coords2[1]]
            swapped_two = [coords2[0], coords1[1]]
            if self.connection_check(swapped_one, swapped_two):
                return True
        return False

    def connect_new_nodes(self):
        while True:
            selected_node = list(self.empty_nodes())
            selected_one_away = random.choice(self.one_away(selected_node))
            if not self.connection_check(selected_node, selected_one_away):  # prevents redundant nodes
                if not self.cross_check(selected_node, selected_one_away):  # prevents crossed nodes
                    self.addnode(selected_one_away)
                    self.connections_list.append([selected_node, selected_one_away])
                    break

    def rotate(self, origin, point, angle):
        # Rotate a point counterclockwise by a given angle around a given
        # origin, then rounds the result.
        # The angle should be given in degrees.

        angle = math.radians(angle)
        ox, oy = origin
        px, py = point
        qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
        qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
        return [round(qx), round(qy)]

    def one_connection_nodes(self):
        # Take a list of non-empty nodes and check each node to see if it has exactly one connection.
        # If it does, return the center node and the edge node for each of the one-connection nodes.

        nonzero = numpy.transpose(numpy.nonzero(self.nodelist))
        temp_list = []
        for entry in nonzero:
            connect_nodes = self.one_away(entry, 1)
            connection_count = 0
            for node in connect_nodes:
                if self.connection_check(node, entry.tolist()):
                    connection_count += 1
                    last_check = node
            if connection_count == 1:
                temp_list.append([entry.tolist(), last_check])
        return temp_list

    def connect_existing_nodes(self):
        # Find each node that has only one connection.  - done
        # Find the coordinates of the node it's connected to. - done
        # Find the coordinates for the node in the exact opposite direction and
        #  see if there's a node there.
        # If so, connect them and move on.
        # If not, find the coordinates for the two nodes 45 degrees
        # (one segment away) from the previous check.
        # If one of them has a node, connect it.
        # If they both have nodes, randomly select one and connect it.
        # Do the same thing again, at 90-degree angles (2 segments) from the
        # initial check.
        # Don't go any further than 90 degrees.

        nonzero = numpy.transpose(numpy.nonzero(self.nodelist)).tolist()
        for node_pair in self.one_connection_nodes():
            opposite = self.rotate(node_pair[0], node_pair[1], 180)
            cw1 = self.rotate(node_pair[0], node_pair[1], 135)  # no idea which of these are clockwise/counterclockwise.
            ccw1 = self.rotate(node_pair[0], node_pair[1], 225)
            cw2 = self.rotate(node_pair[0], node_pair[1], 90)
            ccw2 = self.rotate(node_pair[0], node_pair[1], 270)
            if opposite in nonzero:
                if not self.cross_check(node_pair[0], opposite):
                    self.connections_list.append([node_pair[0], opposite])
            elif cw1 in nonzero and ccw1 in nonzero:
                chosen = random.choice([cw1, ccw1])
                if not self.cross_check(node_pair[0], chosen):
                    self.connections_list.append([node_pair[0], chosen])
            elif cw1 in nonzero:
                if not self.cross_check(node_pair[0], cw1):
                    self.connections_list.append([node_pair[0], cw1])
            elif ccw1 in nonzero:
                if not self.cross_check(node_pair[0], ccw1):
                    self.connections_list.append([node_pair[0], ccw1])
            elif cw2 in nonzero and ccw2 in nonzero:
                chosen = random.choice([cw2, ccw2])
                if not self.cross_check(node_pair[0], chosen):
                    self.connections_list.append([node_pair[0], chosen])
            elif cw2 in nonzero:
                if not self.cross_check(node_pair[0], cw2):
                    self.connections_list.append([node_pair[0], cw2])
            elif ccw2 in nonzero:
                if not self.cross_check(node_pair[0], ccw2):
                    self.connections_list.append([node_pair[0], ccw2])

    def convert_to_screen(self, coordinate):
        return (coordinate + 1) * self.margin

    def createtypes(self):
        # 0:not defined; 1: default; 2:start; 3:loot; 4:boss; 5:done.
        for row in range(self.w):
            for column in range(self.h):
                if self.nodelist[column][row] == 1:
                    if self.nodetypes[column][row] == 0:
                        self.nodetypes[column][row] = numpy.random.choice((1, 3, 4), p=[0.55, 0.25, 0.20])
                        if self.nodetypes[column][row] == 4:
                            self.boss_count += 1

    def drawcircle(self, column, row, nodecol=BLACK, ringcol=WHITE):
        nodetype = self.nodetypes[column][row]
        if nodetype == 2:
            nodecol = GREEN  # START/CURRENT
        elif nodetype == 3:
            nodecol = YELLOW  # LOOT
        elif nodetype == 4:
            nodecol = DARK_RED  # BOSS
        elif nodetype == 5:
            nodecol = LIGHT_GREEN

        pygame.draw.circle(self.screen, nodecol,
                           [self.convert_to_screen(column), self.convert_to_screen(row)], self.circle_diam,
                           0)
        pygame.draw.circle(self.screen, ringcol,
                           [self.convert_to_screen(column), self.convert_to_screen(row)], self.circle_diam,
                           self.circle_line_width)

    def drawcircles(self):
        for row in range(self.w):
            for column in range(self.h):
                if self.nodelist[column][row] == 1:
                    self.drawcircle(column, row)

    def drawlines(self):
        for connection in self.connections_list:
            pygame.draw.line(self.screen, LIGHT_GREY, [self.convert_to_screen(connection[0][0]),
                                                       self.convert_to_screen(connection[0][1])],
                             [self.convert_to_screen(connection[1][0]),
                              self.convert_to_screen(connection[1][1])], self.line_width)

    def drawgrid(self):
        for i in range(1, self.h + 1):
            pygame.draw.line(self.screen, DARK_GREY, (i * self.margin, self.margin),
                             (i * self.margin, self.w * self.margin), self.grid_line_width)
        for j in range(1, self.w + 1):
            pygame.draw.line(self.screen, DARK_GREY, (self.margin, j * self.margin),
                             (self.h * self.margin, j * self.margin), self.grid_line_width)

    def drawall(self):
        self.screen.fill(BLACK)
        self.drawgrid()
        self.drawlines()
        self.drawcircles()
        # pygame.display.flip()

    def generate(self):
        self.addnode(self.starting_point)
        self.nodetypes[self.starting_point[0]][self.starting_point[1]] = 2
        self.done = False
        # drawn = 0
        while not self.done:
            self.connect_new_nodes()
            self.createtypes()
            # self.drawall()
            # drawn += 1
            if sum(sum(self.nodelist)) > self.w * self.h * self.fill_percent:
                self.done = True
        # print(self.currnode)
        # print(self.nodelist)
