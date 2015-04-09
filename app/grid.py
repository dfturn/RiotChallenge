# Code adapted from http://www.redblobgames.com/pathfinding/
# Copyright 2014 Red Blob Games <redblobgames@gmail.com>

# License: Apache v2.0 <http://www.apache.org/licenses/LICENSE-2.0.html>

class SquareGrid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.walls = set()
    
    def in_bounds(self, id):
        (x, y) = id
        return 0 <= x < self.width and 0 <= y < self.height
    
    def passable(self, id):
        return id not in self.walls
    
    def neighbors(self, id):
        (x, y) = id
        results = [(x+1, y), (x, y-1), (x-1, y), (x, y+1), (x+1,y+1), (x+1,y-1), (x-1, y-1), (x-1, y+1)] # include diagonals
        if (x + y) % 2 == 0: results.reverse() # aesthetics
        results = filter(self.in_bounds, results)
        if id not in self.walls:
            results = filter(self.passable, results)
        return results
        
    def cost(self, a, b):
        if abs(a[0]-b[0])+abs(a[1]-b[1]) == 2: # diagonals cost more
            return 14
        return 10