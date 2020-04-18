import tkinter as tk
from pathfinding import *
import time

class PathfindingGUI:

    def __init__(self, rectanglesCount=20, rectPixelWidth=25, padding=10):
        self.rectanglesCount = rectanglesCount
        self.rectPixelWidth = rectPixelWidth
        self.padding = padding
        self.windowSize = 10 * 2 + rectanglesCount * rectPixelWidth

        self.rectangles = [[0 for x in range(rectanglesCount)] for y in range(rectanglesCount)] # initialize rectangle array which gets filled later
        self.clicked = [] # all marked rectangles (none at the beginning)
        
        self.create_gui() # create root & canvas to draw on; adds rectangles

        self.start = self.get_rectangle(0, 0) # where the algorithm should start
        self.start.setStartType()

        self.stop = self.get_rectangle(rectanglesCount - 1, rectanglesCount - 1) # where the algorithm should stop
        self.stop.setStopType()

        self._pick_mode('solid') # solid marker is enabled by default

    def create_gui(self):
        self.root = tk.Tk()
        self.root.title('Pathfinding: Visualization Program (github.com/philipp-riddle)')


        self.frame = tk.Frame(self.root)
        self.frame.pack(side=tk.TOP)

        self.pick_canvas = tk.Canvas(self.frame, width=200, height=51)
        self.pick_canvas.pack(side=tk.LEFT)

        self.pick_start = self.pick_canvas.create_rectangle(0, 0, 32, 32, outline='black', fill='blue', tags="pick_start")
        self.pick_canvas.tag_bind('pick_start', "<Button-1>", self._click_pick_start)

        self.pick_stop = self.pick_canvas.create_rectangle(60, 0, 92, 32, outline='black', fill='violet', tags="pick_stop")
        self.pick_canvas.tag_bind('pick_stop', "<Button-1>", self._click_pick_stop)

        self.pick_solid = self.pick_canvas.create_rectangle(120, 0, 152, 32, outline='black', fill='red', tags="pick_solid")
        self.pick_canvas.tag_bind('pick_solid', "<Button-1>", self._click_pick_solid)

        self.pick_mode = 'solid'

        self.button = tk.Button(self.frame, text='STEP', command=self._clicked_step_pathfinding, highlightbackground='#3E4149')
        self.button.pack(fill=tk.BOTH, side=tk.RIGHT)

        self.button = tk.Button(self.frame, text='FINISH', command=self._clicked_finish_pathfinding, bg='red', highlightbackground='#3E4149')
        self.button.pack(fill=tk.BOTH, side=tk.RIGHT)

        self.canvas = tk.Canvas(self.root, width=self.windowSize, height=self.windowSize)
        self.create_rectangles() # add rectangles to screen
        self.canvas.pack()

    def reloadAlgo(self):
        tileMesh = self.create_tile_mesh()
        self.algo = Dijkstras(tileMesh, start=PathfindingTile(start=True, x=self.start.gridX, y=self.start.gridY), stop=PathfindingTile(stop=True, x=self.stop.gridX, y=self.stop.gridY), gui=self)

    # opens the GUI window and reloads the tiles if any tiles were added by the user before opening the GUI
    def open(self):
        self.reloadAlgo()
        self.root.mainloop()

    def _click_pick_start(self, *args):
        self._pick_mode('start')
        return 0

    def _click_pick_stop(self, *args):
        self._pick_mode('stop')
        return 0

    def _click_pick_solid(self, *args):
        self._pick_mode('solid')
        return 0

    def _pick_mode(self, mode):
        self.pick_mode = mode
        modes = ['start', 'stop', 'solid']

        for mode in modes:
            width = 5 if self.pick_mode == mode else 1
            self.pick_canvas.itemconfig(getattr(self, 'pick_' + mode), width=width)

    def create_rectangles(self):
        for x in range(self.rectanglesCount):
          for y in range(self.rectanglesCount):
            topLeftX = self.padding + x * self.rectPixelWidth
            topLeftY = self.padding + y * self.rectPixelWidth
            bottomRightX = topLeftX + self.rectPixelWidth
            bottomRightY = topLeftY + self.rectPixelWidth

            tagName = "rect" + str(x) + "." + str(y)

            rect = GridRectangle(self, x, y, topLeftX, topLeftY, bottomRightX, bottomRightY, tagName, onClick=self._clicked_rectangle)
            rect.draw()

            self.rectangles[x][y] = rect

    def _clicked_finish_pathfinding(self):
        self.reset_tiles()
        path = self.algo.step()

        while self.algo.running:
            path = self.algo.step()

        if path is not None:
            self.visualize_path(path) 

    # user clicked on "STEP"
    def _clicked_step_pathfinding(self):
        path = self.algo.step()

        if path is not None:
            self.visualize_path(path)

    def visualize_path(self, path):
        for tile in path: # color path
            tile = self.get_rectangle(tile.x, tile.y)

            if self.start != tile and self.stop != tile:
                tile.setColor('#8A2BE2')

    # click on a rectangle - check the mode
    def _clicked_rectangle(self, event):
        rect = self._get_rectangle_from_coordinates(event.x, event.y)

        if rect is None or self.start == rect or self.stop == rect: # should not override start/stop node
            return

        if self.pick_mode == 'start': # select start node
            self.start.setType('white', None) # reset type
            rect.setStartType()
            self.start = rect

        elif self.pick_mode == 'stop': # select stop node
            self.stop.setType('white', None) # reset type
            rect.setStopType()
            self.stop = rect

        elif self.pick_mode == 'solid': # select solid block
            color = ''

            if rect.isClicked: # remove 'clicked' status / rect is not solid anymore
                color = 'white'
                rect.setIsClicked(False)
                self.clicked.remove(rect)
            else:
                color = 'red'
                rect.setIsClicked(True)
                self.clicked.append(rect)
            
            rect.color = color
            rect.setColor(color)
        
        self.reloadAlgo() # reload the mesh to the solid walls can be detected
        self.reset_tiles() # reset the tile colors to start a new "round"
  
    """ 
    this function gets the rectangle x and y index from the coordinates
    this rectangle instance gets used to change the color
    """
    def _get_rectangle_from_coordinates(self, x, y):
        rectX = (x - self.padding) // self.rectPixelWidth
        rectY = (y - self.padding) // self.rectPixelWidth

        return self.get_rectangle(rectX, rectY)

    def get_rectangle(self, indexX, indexY):
        try:
            return self.rectangles[indexX][indexY]
        except IndexError:
            return None

    # create a "mesh" which can be used by the pathfinding algorithm implementations
    def create_tile_mesh(self):
        tiles = [[0 for x in range(self.rectanglesCount)] for y in range(self.rectanglesCount)] # prepare tiles array

        for x in range(self.rectanglesCount):
          for y in range(self.rectanglesCount):
              rect = self.get_rectangle(x, y)
              start = True if rect.type == 'start' else False
              stop = True if rect.type == 'stop' else False
              solid = rect.isClicked

              tiles[x][y] = PathfindingTile(start, stop, solid, x=x, y=y)

        return tiles

    # resets the tiles - removes colors!
    def reset_tiles(self):
        for x in range(self.rectanglesCount):
          for y in range(self.rectanglesCount):
              tile = self.get_rectangle(x, y)
              if not tile.isClicked:
                  tile.reset()


class GridRectangle:

    def __init__(self, gui, gridX, gridY, x1, y1, x2, y2, tag=None, color='white', onClick=None, type=None):
        self.gui = gui
        self.gridX = gridX
        self.gridY = gridY
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.tag = tag
        self.color = color
        self.onClick = onClick
        self.isClicked = False
        self.type = type

        self.id = None # the unique ID of the component

    def draw(self):
        self.id = self.gui.canvas.create_rectangle(self.x1, self.y1, self.x2, self.y2, fill=self.color, outline='black', tags=self.tag)

        if self.onClick is not None:
            self.gui.canvas.tag_bind(self.tag, "<Button-1>", self.onClick)

    def setIsClicked(self, isClicked): # equals to an obstacle for the pathfinding algorithms
        self.isClicked = isClicked

    # function sets the color - pass ignoreLock=true if this function should not paint any start/stop points.
    def setColor(self, color, ignoreLock=True):
        if not ignoreLock and self._lockedColor:
            return
        self.gui.canvas.itemconfig(self.id, fill=color)

    def setType(self, color, type):
        self.color = color # lock color
        self.setColor(color)
        self.type = type

    def setStartType(self, color='blue'):
        self.setType(color, 'start')

    def setStopType(self, color='violet'):
        self.setType(color, 'stop')

    def reset(self):
        self.setColor(self.color)

    def _lockedColor(self):
        return self.type is not None