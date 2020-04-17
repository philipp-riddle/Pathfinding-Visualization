from tkinter import *
from pathfinding import *

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

        self.reloadAlgo()

    def create_gui(self):
        self.root = Tk()
        self.root.title('Pathfinding: Visualization Program (github.com/philipp-riddle)')
        # self.root.geometry(str(self.windowSize) + "x" + str(self.windowSize))
        self.canvas = Canvas(self.root, width=self.windowSize, height=self.windowSize)

        self.button = Button(self.root, text='STEP', command=self._clicked_pathfinding, highlightbackground='#3E4149')
        self.button.pack()

        self.create_rectangles() # add rectangles to screen
        self.canvas.pack()

    def reloadAlgo(self):
        tileMesh = self.create_tile_mesh()
        self.algo = Dijkstras(tileMesh, start=PathfindingTile(start=True, x=self.start.gridX, y=self.start.gridY), stop=PathfindingTile(stop=True, x=self.stop.gridX, y=self.stop.gridY), gui=self)

    def open(self):
        self.root.mainloop()

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

    def _clicked_pathfinding(self):
        path = self.algo.step()

        if path is not None:
            print("FOUND IT!")
            for tile in path: # color path
                self.get_rectangle(tile.x, tile.y).setColor('#8A2BE2')

    def _clicked_rectangle(self, event):
        rect = self._get_rectangle_from_coordinates(event.x, event.y)

        if rect is None:
            print('click was out of bounds. ignore the event...')
            return

        color = ''

        if rect.isClicked:
            color = 'white'
            rect.setIsClicked(False)
            self.clicked.remove(rect)
        else:
            color = 'red'
            rect.setIsClicked(True)
            self.clicked.append(rect)
        
        rect.setColor(color)
        self.reloadAlgo() # reload the mesh to the solid walls can be detected
        self.reset_tiles()
  
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

    def setColor(self, color, ignoreLock=False):
        if not self._lockedColor():
            self.gui.canvas.itemconfig(self.id, fill=color)

    def setType(self, color, type):
        self.setColor(color)
        self.type = type

    def setStartType(self, color='blue'):
        self.setType(color, 'start')

    def setStopType(self, color='violet'):
        self.setType(color, 'stop')

    def reset(self):
        self.setColor(self.color)

    def _lockedColor(self):
        return self.type == 'start' or self.type == 'stop'