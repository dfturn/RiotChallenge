from __future__ import division
import json
import bisect
import astar

class Position:
    def __init__(self, grid, x, y, scaled=False):
        self.grid = grid
        
        if not scaled:
            self.x = x
            self.y = y
            
            self.scaledX = Position.scaleX(self.x)
            self.scaledY = Position.scaleY(self.y)
            if (self.scaledX, self.scaledY) in grid.walls:
                neighbors = my_grid.neighbors((self.scaledX, self.scaledY))
                neighbors = filter(my_grid.passable, neighbors)
                if neighbors:
                    self.scaledX, self.scaledY = neighbors[0] # TODO: If we're running into walls a lot look at this again
        else:
            self.x = Position.scaleX(x, False)
            self.y = Position.scaleY(y, False)
            
            self.scaledX = x
            self.scaledY = y
    
    @staticmethod
    def scale(val, src, dst):
        """
        Scale the given value from the scale of src to the scale of dst.
        """
        return int(((val - src[0]) / (src[1]-src[0])) * (dst[1]-dst[0]) + dst[0])
        
    @staticmethod
    def scaleX(val, to=True):
        # If to==True then we're scaling down to the 64x64 map
        
        source_Xrange = (-120, 14870)
        dest_range = (0,64)
        if to:
            return Position.scale(val, source_Xrange, dest_range)
        else:
            return Position.scale(val, dest_range, source_Xrange)
        
    @staticmethod
    def scaleY(val, to=True):
        source_Yrange = (-120, 14980)
        dest_range = (0,64)
        if to:
            return 64-Position.scale(val, source_Yrange, dest_range)
        else:
            return Position.scale(64-val, dest_range, source_Yrange)

class PlayerLocation:
    def __init__(self, grid, ts, pos=None, x=None, y=None, scaled=False):
        self.time = ts
        if pos:
            self.pos = Position(grid, pos["x"], pos["y"], scaled)
        else:
            self.pos = Position(grid, x, y, scaled)
        
    def __repr__(self):
        return "({0},{1}) at {2}".format(self.pos.x, self.pos.y, self.time)

class Ward:
    def __init__(self, ts, type, duration):
        self.time = ts
        self.type = type
        self.duration = duration
        
        # To be estimated later from the estimated player position (lol)
        self.x = None
        self.y = None
        
my_grid = astar.read_grid("C:\\git_stuff\\riot_challenge\\map.txt")        

with open("example_match.json") as json_data:
    data = json.loads(json_data.read())

pos_data = { int(pid) : [PlayerLocation(my_grid, 0, d["position"])] for pid, d in data["timeline"]["frames"][0]["participantFrames"].iteritems() }

wards = {}
wards_destroyed = { 0 : [] }

levels = { pid : 1 for pid in range(1,11) }

towers = {100 : set([(5846, 6396), (5048, 4812), (981, 10441), (10504, 1029), (6919, 1483), (1512, 6699), \
                    (3651, 3696), (1169, 4287), (4281, 1253), (1748, 2270), (2177, 1807)]),
          200 : set([(4318, 13875), (8955, 8510), (7943, 13411), (10481, 13650), (9767, 10113), (11134, 11207), \
                    (4505, 13866), (8226, 13327), (10572, 13624), (12612, 13052), (13084, 12611)])}
                    

for frame in data["timeline"]["frames"]:
    if "events" in frame:
        for e in frame["events"]:
            if e["eventType"] == "CHAMPION_KILL" or \
               e["eventType"] == "BUILDING_KILL" or \
               e["eventType"] == "ELITE_MONSTER_KILL": # TODO: Add in "back" handling -- when they buy items it's a teleport

                loc = PlayerLocation(my_grid, e["timestamp"], e["position"])
                
                if "victimId" in e and e["victimId"] != 0:
                    pos_data[e["victimId"]].append(loc)
                    
                    respawn_time = levels[e["victimId"]] * 2.5 + 5
                    mins = e["timestamp"] / 60000
                    if( mins > 25 ):
                        respawn_time += mins - 25
                    respawn_loc = PlayerLocation(my_grid, e["timestamp"] + respawn_time, e["position"])
                    pos_data[e["victimId"]].append(respawn_loc)
                if "killerId" in e and e["killerId"] != 0:
                    pos_data[e["killerId"]].append(loc)
                
                if "assistingParticipantIds" in e:
                    for p in e["assistingParticipantIds"]:
                        pos_data[p].append(loc)
            elif e["eventType"] == "WARD_PLACED":
                pid = e["creatorId"]
                if pid not in wards:
                    wards[pid] = []
                
                duration = 3 * 60 * 1000
                if e["wardType"] == "YELLOW_TRINKET" and levels[pid] < 9:
                    duration /= 3
                    
                wards[pid].append(Ward(e["timestamp"], e["wardType"], duration))
            elif e["eventType"] == "WARD_KILL":
                pid = e["killerId"]
                if pid not in wards_destroyed:
                    wards_destroyed[pid] = []
                wards_destroyed[pid].append(e["timestamp"])
            elif e["eventType"] == "ITEM_PURCHASED":
                pid = e["participantId"]
                if pos_data[pid][-1].time <= e["timestamp"]: # Make sure they're not dead
                    pos_data[pid].append(PlayerLocation(my_grid, e["timestamp"], x=pos_data[pid][0].pos.x, y=pos_data[pid][0].pos.y))
                    
            else:
                if "position" in e:
                    print(e)
                    
    for pid, d in frame["participantFrames"].iteritems():
        if "position" in d:
            pos_data[int(pid)].append(PlayerLocation(my_grid, frame["timestamp"], d["position"]))
            levels[pid] = d["level"]

            
            
for pid, wlist in wards.iteritems():
    for w in wlist:
        pass
            
            

wall_locs = []
for pid in range(1,11):
    #scaled_locs = [(scaleX(p.x), scaleY(p.y), p.time) for p in pos_data[pid]]

    full_path = []
    for i in range(len(pos_data[pid])-1):
        start = (pos_data[pid][i].pos.scaledX, pos_data[pid][i].pos.scaledY)
        end = (pos_data[pid][i+1].pos.scaledX, pos_data[pid][i+1].pos.scaledY)
        path = [end]
        
        if end not in my_grid.walls:

                
            came_from, cost_so_far = astar.a_star_search(my_grid, start, end)
            #print came_from
            while( end != start ):
                if end not in came_from:
                    print start, end, [Position.scaleX(start[0], False), Position.scaleY(start[1], False), \
                            Position.scaleX(end[0], False), Position.scaleY(end[1], False)], ","
                    break
                
                end = came_from[end]
                path.append(end)
        else:
            wall_locs.append(end)
            #print str(pid) + " going to wall: " + str(end) # TODO: remove debug
        path.append(start)
        
        time_inc = (pos_data[pid][i+1].time - pos_data[pid][i].time)/(len(path)-1)
        time_start = pos_data[pid][i].time
        while path:
            node = path.pop()
            full_path.append((node[0], node[1], time_start))
            time_start += time_inc
            
    pos_data[pid] = [PlayerLocation(my_grid, p[2], x=p[0], y=p[1], scaled=True) for p in full_path]
        
#print 

# Prints where we ran into walls
#print [[Position.scaleX(w[0], False), Position.scaleY(w[1], False)] for w in wall_locs]

# Prints all our estimated locations for all players
for pid, locs in pos_data.iteritems():
   pass #print [[l.pos.x, l.pos.y] for l in locs]
        
        

diffs = []
for pid, ws in wards.iteritems():
    #print pid, len(ws)
    for w in ws:
        # TODO: Improve this, perhaps look at nearby bushes
        loc = min(pos_data[pid], key=lambda x:abs(x.time-w.time))
        # Prints estimated ward locations
        w.x = loc.pos.x
        w.y = loc.pos.y
        #print [loc.pos.x, loc.pos.y], ","
        diffs.append(abs(min(pos_data[pid], key=lambda x:abs(x.time-w.time)).time - w.time))
        
#print diffs



from scipy.spatial import ConvexHull
import numpy
print 
#print {(pid, pid) for pid, wlist in wards.iteritems() for w in wlist if pid in range(1,6)}
points = numpy.array(list(towers[100] | {(w.x, w.y) for pid, wlist in wards.iteritems() for w in wlist if pid in range(1,6)}))
#print points
hull = ConvexHull(points)
import matplotlib.pyplot as plt
plt.plot(points[:,0], points[:,1], 'o')
for simplex in hull.simplices:
    plt.plot(points[simplex,0], points[simplex,1], 'k-')
#plt.show()