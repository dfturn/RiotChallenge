import astar
from itertools import permutations
import pickle
import os

class CachedPaths:
    def __init__(self, grid):
        self.pickle_file = "caches/paths.bin"
        self.grid = grid
        
        if os.path.exists(self.pickle_file):
            with open(self.pickle_file, 'rb') as f:
                self.dict = pickle.load(f)
        else:
            self.dict = {}
            
    def getPath(self, start, end):
        if (start, end) in self.dict:
            path = self.dict[(start, end)]
        else:
            came_from, cost_so_far = astar.a_star_search(self.grid, start, end)
            path = [end]
            e = end
            try: 
                while( e != start ):
                    e = came_from[e]
                    path.append(e)
                path.append(start)
            except KeyError:
                #Some paths may be impossible
                path = [end, start]
            finally:
                path.reverse()

            self.dict[(start, end)] = path

        return path
        
    def pickle(self):
        with open(self.pickle_file, 'wb') as f:
            pickle.dump(self.dict, f)