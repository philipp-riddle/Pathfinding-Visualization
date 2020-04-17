import time

class Dijkstras:

    def __init__(self, tiles, start, stop, gui):
        self.tiles = tiles
        self.leftToVisit = len(self.tiles) * len(self.tiles[0]) - 1 # subtract the start node
        self.startNode = start
        self.stopNode = stop
        self.gui = gui
        # self.visited = [[0 for x in range(len(tiles))] for y in range(len(tiles[0]))] # to support non-square tile meshes => len(tiles[0])

        self.frontierNodes = [self.startNode] # the tiles that are currently exploring - initialize with startNode

    # returns None if no path could be found
    def start(self):
        return self._checkTile(self.startNode) # recursive algorithm

    def _checkTile(self, tile):
        path = None

        while (path is None):
            frontiers = self.frontierNodes.copy()
            self.frontierNodes = [] # reset frontiers so the for loop below is not an endless loop

            for node in frontiers:
                if node.x != self.startNode.x and node.y != self.startNode.y:
                    self.gui.get_rectangle(node.x, node.y).setColor('gray') # set prior frontier to color gray
                print("Exploring nodes around ", node.x, ':', node.y)
                self.explore_nodes_around(node) # generate frontier nodes
            path = self.check_frontier_nodes()

            if path is not None:
                return path
            
            print("Left to visit: ", self.leftToVisit)
            time.sleep(1)
        


        return None

    def step(self):

        if len(self.frontierNodes) == 0: # empty 
            print("Could not find path!")
            return

        frontiers = self.frontierNodes.copy()
        self.frontierNodes = [] # reset frontiers so the for loop below is not an endless loop

        for node in frontiers:
            self.explore_nodes_around(node) # generate frontier nodes
            
        path = self.check_frontier_nodes()

        if path is not None:
            return path
        
        print("Left to visit: ", self.leftToVisit)

    # this function explores the nodes around a tile
    def explore_nodes_around(self, tile):
        # create a "square" around the current node and takes care of boundaries
        for x in range(max(0, tile.x - 1), min(len(self.tiles), tile.x + 2)):
            for y in range(max(0, tile.y - 1), min(len(self.tiles[0]), tile.y + 2)):
                t = self.tiles[x][y]

                if (tile.x == x and tile.y == y) or t.visited(): # the tile itself or if the tile was already visited => skip it
                    # print((tile.x == x and tile.y == y), ", ", t.visited)
                    continue

                if t.solid: # tile is a solid block, skip it
                    print(t.x, ":", t.y, " is solid; skip it")
                    t.distance = -2 # set it to a number which signalizes that the tile has been visited
                    continue

                distance = self.calculate_distance_between(tile, t)
                # print(tile.x, ":", tile.y, " => ", t.x, ":", t.y, "; distance = ", distance)

                if t.distance > distance or t.distance == -1: # shorter path detected; override the previous tile plus distance
                    t.previous = tile
                    t.distance = distance + t.distance if t.distance != -1 else distance # override infinity setting

                if t in self.frontierNodes: # only got better path - do nothing further
                    continue

                # print(x, ", ", y, ": ", t.distance)
                self.leftToVisit -= 1
                self.gui.get_rectangle(x, y).setColor('yellow')
                if t not in self.frontierNodes:
                    self.frontierNodes.append(t)

        if tile.x != self.startNode.x or tile.y != self.startNode.y: # color the frontier node gray unless it's the start node
            self.gui.get_rectangle(tile.x, tile.y).setColor('gray')

    # check frontier nodes if the stop node has been hit - do this after exploration to ensure we pick the best path
    def check_frontier_nodes(self):
        for node in self.frontierNodes:
            if node.stop: # node is stop node
                return self.get_path(node)

        return None

    def get_path(self, tile):
        tiles = [tile]

        while(tile.previous is not None):
            tile = tile.previous
            tiles.append(tile)

        return tiles

    # two cases: direct neighbours or diagonal neighbours
    def calculate_distance_between(self, tile1, tile2):
        absX = abs(tile1.x - tile2.x)
        absY = abs(tile1.y - tile2.y)

        if (absX == 0 and absY == 1) or (absX == 1 and absY == 0): # direct
            return 1
        
        if absX == 1 and absY == 1: # diagonal
            return 1.4 # ~ square root of 2

        return 0

class PathfindingTile:
    def __init__(self, start=False, stop=False, solid=False, x=0, y=0):
        self.start = start
        self.stop = stop
        self.solid = solid
        self.x = x
        self.y = y

        # Dijkstra's related
        self.distance = 0 if start else -1 # every tile except start has the distance of infinity (or -1 in this case)
        self.previous = None

    def visited(self):
        return self.distance != -1 # if distance has been set - should be infinity if not discovered yet
    # def __eq__(self, value):
    #     return self.x == value.x and self.y == value.y