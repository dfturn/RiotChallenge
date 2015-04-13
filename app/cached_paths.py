import astar
import os
from app import mongo

class CachedPaths:
    def __init__(self, grid):
        self.grid = grid
            
    def getPath(self, start, end):
        query = {}
        query["sx"] = start[0]
        query["sy"] = start[1]
        query["ex"] = end[0]
        query["ey"] = end[1]
        cursor = mongo.db.paths.find(query)
        
        if cursor.count() > 0:
            path = cursor[0]["path"]
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

            query["path"] = path
            mongo.db.paths.insert(query)

        return path
