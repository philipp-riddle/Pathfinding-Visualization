from tkinter import *

class PathfindingGUI:

    def __init__(self, rectanglesCount=5, rectPixelWidth=50, padding=10):
        self.rectanglesCount = rectanglesCount
        self.rectPixelWidth = rectPixelWidth
        self.padding = padding
        self.windowSize = 10 * 2 + rectanglesCount * rectPixelWidth

        self.rectangles = [[0 for x in range(rectanglesCount)] for y in range(rectanglesCount)] # initialize rectangle array which gets filled later
        self.clicked = [] # all marked rectangles (none at the beginning)
        
        self.create_gui() # create root & canvas to draw on; adds rectangles

    def create_gui(self):
        self.root = Tk()
        self.root.geometry(str(self.windowSize) + "x" + str(self.windowSize))
        self.canvas = Canvas(self.root, width=self.windowSize, height=self.windowSize)

        self.create_rectangles() # add rectangles to screen
        self.canvas.pack()

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
        
        self.canvas.itemconfig(rect.id, fill=color)
  
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

class GridRectangle:

    def __init__(self, gui, gridX, gridY, x1, y1, x2, y2, tag=None, color='white', onClick=None):
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

        self.id = None # the unique ID of the component

    def draw(self):
        self.id = self.gui.canvas.create_rectangle(self.x1, self.y1, self.x2, self.y2, fill=self.color, outline='black', tags=self.tag)

        if self.onClick is not None:
            self.gui.canvas.tag_bind(self.tag,"<Button-1>",self.onClick)

    def setIsClicked(self, isClicked):
        self.isClicked = isClicked