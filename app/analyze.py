from __future__ import division
import json
import astar
from cached_paths import CachedPaths
import numpy as np
import common_data as cd
import os
from scipy.spatial import ConvexHull
from scipy.spatial.distance import euclidean
from scipy.sparse import coo_matrix, csgraph

dir = os.path.dirname(__file__)
my_grid = astar.read_grid(os.path.join(dir, "../map.txt"))
    
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
                    self.scaledX, self.scaledY = neighbors[0] # If we're running into walls a lot look at this again
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
        
class TowerDestroyed:
    def __init__(self, ts, pos):
        self.x = pos["x"]
        self.y = pos["y"]
        self.time = ts
    
TEAM1 = 100
TEAM2 = 200
def get_opposing_team(team_id):
    if team_id == TEAM1:
        return TEAM2
    return TEAM1
    
# Since OpenShift won't install scipy 0.15 use this to get the proper convex hull from the simplices
# From https://gist.github.com/pv/5492551
def ordered_hull_idx_2d(hull):
    n = hull.simplices.shape[0]
    
    # determine order of edges in the convex hull
    v = coo_matrix((np.ones(2*n), (np.repeat(np.arange(n), 2), hull.neighbors.ravel())))
    facet_order = csgraph.depth_first_order(v, 0, return_predecessors=False)
    facet_vidx = hull.simplices[facet_order]
    
    # pick one vertex for each edge, based on which direction the walk went
    m = hull.neighbors[facet_order][:-1] == facet_order[1:,None]
    i = np.arange(n)
    j = np.r_[np.where(m)[1], 0] 
    
    ordered_vertex_idx = facet_vidx[i, j]
    
    # sanity check
    assert np.all(np.unique(ordered_vertex_idx) == np.unique(hull.simplices.ravel()))
 
    return ordered_vertex_idx
    
def analyze_match(data, granularity=5000):

    pos_data = { int(pid) : [PlayerLocation(my_grid, 0, d["position"])] for pid, d in data["timeline"]["frames"][0]["participantFrames"].iteritems() }

    wards = {}
    wards_destroyed = { 0 : [] }
    towers_destroyed = {TEAM1 : [], TEAM2 : []}

    levels = { pid : 1 for pid in range(1,11) }

    towers = {TEAM1 : set([(5846, 6396), (5048, 4812), (981, 10441), (10504, 1029), (6919, 1483), (1512, 6699), \
                        (3651, 3696), (1169, 4287), (4281, 1253), (1748, 2270), (2177, 1807), (-120, -120)]),
              TEAM2 : set([(4318, 13875), (8955, 8510), (7943, 13411), (10481, 13650), (9767, 10113), (11134, 11207), \
                        (4505, 13866), (8226, 13327), (10572, 13624), (12612, 13052), (13084, 12611), (13866, 4505), (14870, 14980)])}
                        

    for frame in data["timeline"]["frames"]:
        if "events" in frame:
            for e in frame["events"]:
                if e["eventType"] == "CHAMPION_KILL" or \
                   e["eventType"] == "BUILDING_KILL" or \
                   e["eventType"] == "ELITE_MONSTER_KILL": # TODO: Add in "back" handling -- when they buy items it's a teleport

                    if e["eventType"] == "BUILDING_KILL" and e["buildingType"] == "TOWER_BUILDING":
                        towers_destroyed[e["teamId"]].append(TowerDestroyed(e["timestamp"], e["position"]))
                   
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
                    elif e["wardType"] == "VISION_WARD":
                        duration = float("inf")
                        
                    wards[pid].append(Ward(e["timestamp"], e["wardType"], duration))
                        
                    wards_destroyed[0].append(Ward(e["timestamp"]+duration, e["wardType"], 0))
                elif e["eventType"] == "WARD_KILL":
                    pid = e["killerId"]
                    if pid not in wards_destroyed:
                        wards_destroyed[pid] = []
                        
                    wards_destroyed[pid].append(Ward(e["timestamp"], e["wardType"], 0))
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

    cached_paths = CachedPaths(my_grid)
    wall_locs = []
    for pid in range(1,11):
        full_path = []
        for i in range(len(pos_data[pid])-1):
            start = (pos_data[pid][i].pos.scaledX, pos_data[pid][i].pos.scaledY)
            end = (pos_data[pid][i+1].pos.scaledX, pos_data[pid][i+1].pos.scaledY)
            path = cached_paths.getPath(start, end)
            
            time_inc = (pos_data[pid][i+1].time - pos_data[pid][i].time)/(len(path)-1)
            time_start = pos_data[pid][i].time
            for node in path:
                full_path.append((node[0], node[1], time_start))
                time_start += time_inc
        
        interp_pos = []
        index = 0
        for t in range(0, int(full_path[-1][2]), granularity):
            while index < len(full_path) and full_path[index][2] <= t:
                index += 1
               
            a = np.array([[full_path[index-1][0], full_path[index-1][1]],
                           [full_path[index][0], full_path[index][1]]])
            rng = full_path[index][2] - full_path[index-1][2]
            w1 = (t-full_path[index][2])/rng
            w2 = 1-w1
            weights = [w1, w2]
            avg = np.append(np.average(a, 0, weights), t).tolist()

            interp_pos.append(avg)
        pos_data[pid] = [[Position.scaleX(p[0], to=False), Position.scaleY(p[1], to=False), p[2]] for p in interp_pos]

    
    
    pos_data["champs"] = {p["participantId"] : cd.CHAMPS_BY_ID["keys"][str(p["championId"])] for p in data["participants"]}

    for pid, ws in wards.iteritems():
        for w in ws:
            # TODO: Improve this, perhaps look at nearby bushes

            loc = min(pos_data[pid], key=lambda x:abs(x[2]-w.time))
            # Gets estimated ward locations
            w.x = loc[0]
            w.y = loc[1]
            
    for pid, ws in wards_destroyed.iteritems():
        if pid == 0:
            continue
            
        rng = range(1,6)
        if pid <= 5:
            rng = range(6,11)
        for w in ws:
            loc = min(pos_data[pid], key=lambda x:abs(x[2]-w.time))
            
            min_dist = float("inf")
            min_w = None
            for enemy in rng:
                for w_place in wards[enemy]:
                    if w_place.type == w.type:
                        diff = w.time - w_place.time
                        if diff >=0 and diff < w_place.duration:
                            dist = euclidean([w_place.x, w_place.y], [loc[0], loc[1]])
                            if dist < min_dist:
                                min_w = w_place
            min_w.duration = w.time - min_w.time
            
    points = {TEAM1 : [], 200 : []}
    for ts in range(0, data["matchDuration"] * 1000, granularity):
        t1_pts = set()
        for pid in range(1,6):
            for w in wards[pid]:
                if w.time < ts and w.time + w.duration > ts:
                    t1_pts.add((w.x, w.y))
                elif w.time > ts:
                    break
            
        t2_pts = set()
        for pid in range(6,11):
            for w in wards[pid]:
                if w.time < ts and w.time + w.duration > ts:
                    t2_pts.add((w.x, w.y))
                elif w.time > ts:
                    break
                    
                    
        for team, tower in towers_destroyed.iteritems():
            for t in tower:
                if t.time < ts and (t.x, t.y) in towers[get_opposing_team(team)]:
                    towers[get_opposing_team(team)].remove((t.x, t.y))
                    
        # Now create fake towers at the edges of the map
        # Find the max x and max y for team 1
        max_x = max(towers[100], key=lambda x:x[0])
        max_y = max(towers[100], key=lambda x:x[1])
        fake_towers1 = set([(max_x[0], -120), (-120, max_y[1])])
            
        # Find the min x and min y for team 2
        min_x = min(towers[200], key=lambda x:x[0])
        min_y = min(towers[200], key=lambda x:x[1])
        fake_towers2 = set([(min_x[0], 14980), (14870, min_y[1])])
    
        # Get the convex hull
        hull_test1 = np.array(list(t1_pts | towers[TEAM1] | fake_towers1))
        hull_test2 = np.array(list(t2_pts | towers[TEAM2] | fake_towers2))
        
        hull1 = ConvexHull(hull_test1)
        hull2 = ConvexHull(hull_test2)
        
        hull_idx = ordered_hull_idx_2d(hull1)
        hull_idx = np.r_[hull_idx, hull_idx[0]]
        hull_pts1 = hull_test1[hull_idx].tolist()
        
        hull_idx = ordered_hull_idx_2d(hull2)
        hull_idx = np.r_[hull_idx, hull_idx[0]]
        hull_pts2 = hull_test2[hull_idx].tolist()
        
        points[TEAM1].append(hull_pts1)
        points[TEAM2].append(hull_pts2)
       
    pos_data["hulls"] = points
    return pos_data
