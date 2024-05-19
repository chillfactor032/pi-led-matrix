import board
import neopixel

class LedMatrix():

    def __init__(self, height, width, pin=board.D18):
        self.ORDER = neopixel.GRB
        self.pin = pin
        self.height = height
        self.width = width
        self.num_pixels = self.height*self.width
        self.pixels = neopixel.NeoPixel(
            self.pin, 
            self.num_pixels, 
            brightness=0.2, 
            auto_write=False, 
            pixel_order=self.ORDER)
        self.index_map = LedMatrix.gen_index_map(self.height, self.width)
    
    def clear(self):
        self.pixels.fill((0,0,0))

    def update(self):
        self.pixels.show()

    def set_pixel(self, x, y, color):
        self.pixels[self.index_map[x][y]] = color
    
    @staticmethod
    def gen_index_map(h, w):
        grid_offset = 0
        grid_h = 16
        grid_w = 16
        grid_len = grid_h*grid_w
        map = []
        for y in range(h):
            row = []
            for x in range(w):
                if x < 16 and y < 16:
                    grid_offset = grid_len*0
                elif x < 16 and y >= 16:
                    grid_offset = grid_len*1
                elif x > 16 and y >= 16:
                    grid_offset = grid_len*2
                elif x < 16 and y < 16:
                    grid_offset = grid_len*3
                tx = x % 16
                ty = y % 16
                offset = ty
                if tx % 2 > 0:
                    offset = (grid_h-1)-ty
                index = grid_offset + (tx * grid_w) + offset
                row.append(index)
            map.append(row)
        return map
