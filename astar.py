# Code adapted from http://www.redblobgames.com/pathfinding/
# Copyright 2014 Red Blob Games <redblobgames@gmail.com>

# License: Apache v2.0 <http://www.apache.org/licenses/LICENSE-2.0.html>
from __future__ import print_function
from grid import *
from summoners_grid import *

class Graph:
    def __init__(self):
        self.edges = {}
    
    def neighbors(self, id):
        return self.edges[id]

import collections

class Queue:
    def __init__(self):
        self.elements = collections.deque()
    
    def empty(self):
        return len(self.elements) == 0
    
    def put(self, x):
        self.elements.append(x)
    
    def get(self):
        return self.elements.popleft()


def draw_tile(graph, id, style, width):
    r = "."
    if 'number' in style and id in style['number']: r = "%d" % style['number'][id]
    if 'point_to' in style and style['point_to'].get(id, None) is not None:
        (x1, y1) = id
        (x2, y2) = style['point_to'][id]
        if x2 == x1 + 1: r = "\u2192"
        if x2 == x1 - 1: r = "\u2190"
        if y2 == y1 + 1: r = "\u2193"
        if y2 == y1 - 1: r = "\u2191"
    if 'start' in style and id == style['start']: r = "A"
    if 'goal' in style and id == style['goal']: r = "Z"
    if 'path' in style and id in style['path']: r = "@"
    if id in graph.walls: r = "#" * width
    return r

def draw_grid(graph, width=2, **style):
    for y in range(graph.height):
        for x in range(graph.width):
            print("%%-%ds" % width % draw_tile(graph, (x, y), style, width), end="")
        print()

# Reads a grid from a file into code
def read_grid(filename, width=2):
    size = 0
    walls = set()
    
    with open(filename) as f:
        row = 0
        for line in f.readlines():
            if size == 0:
                size = len(line)/width
            for i in range(0, len(line), width):
                if line[i:i+width] == "#" * width:
                    walls.add((i/width, row))
            row += 1
                
    diagram = SquareGrid(size, size)
    diagram.walls = walls
    return diagram

import heapq

class PriorityQueue:
    def __init__(self):
        self.elements = []
    
    def empty(self):
        return len(self.elements) == 0
    
    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))
    
    def get(self):
        return heapq.heappop(self.elements)[1]

def heuristic(a, b):
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)

def a_star_search(graph, start, goal):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0
    
    while not frontier.empty():
        current = frontier.get()
        
        if current == goal:
            break
        
        for next in graph.neighbors(current):
            new_cost = cost_so_far[current] + graph.cost(current, next)
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(goal, next)
                frontier.put(next, priority)
                came_from[next] = current
    
    return came_from, cost_so_far

# my_grid = read_grid("C:\\git_stuff\\riot_challenge\\map.txt")
# draw_grid(my_grid)

# came_from, cost_so_far = a_star_search(diagram4, (1, 7), (7, 8))
# print (came_from)
# print (cost_so_far)

# n = (7,8)
# while( n != (1,7)):
    # print(n)
    # n=came_from[n]
# #draw_grid(diagram4, width=3, point_to=came_from, start=(1, 4), goal=(7, 8))
# print()
# draw_grid(diagram4, width=3, number=cost_so_far, start=(1, 7), goal=(7, 8))
