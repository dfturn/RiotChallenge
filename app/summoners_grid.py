from grid import *
from PIL import Image

# This created an original rough 64x64 map which I had to manually adjust a tiny bit
# No longer needed but kept just in case
def create_map():
    im = Image.open("minimap_64.png")
    im.save("test.jpeg", "JPEG")
    pix = im.load()
    
    ranges = [((15, 130), (20, 90), (20, 63)), \
                ((110, 140), (110, 120), (60, 70))]

    width, height = im.size #Get the width and hight of the image for iterating over
    
    diagram = SquareGrid(width, height)
    for r in range(0,height):
        for c in range(0,width):
            for ra in ranges:
                if colorIn(pix[r,c], ra):
                    diagram.walls.add((r,c))
                    
    return diagram

    
    
    
    