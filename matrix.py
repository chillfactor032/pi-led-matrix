import os
import threading
import board
import neopixel
import requests
from io import BytesIO
from PIL import Image, GifImagePlugin
GifImagePlugin.LOADING_STRATEGY = GifImagePlugin.LoadingStrategy.RGB_ALWAYS

_USER_AGENT_STRING = ' '.join([
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'AppleWebKit/537.36 (KHTML, like Gecko)',
    'Chrome/86.0.4240.75',
    'Safari/537.36'])

class LedMatrix():

    def __init__(self, height, width, **kwargs):
        self.ORDER = neopixel.GRB
        self.pin = kwargs.get("pin", board.D18)
        self.height = height
        self.width = width
        self.num_pixels = self.height*self.width
        self.pixels = neopixel.NeoPixel(
            self.pin, 
            self.num_pixels, 
            brightness=kwargs.get("brightness", 0.2), 
            auto_write=False, 
            pixel_order=self.ORDER)
        self.index_map = LedMatrix.gen_index_map(self.height, self.width)
        self.gif_thread = None
        self._gif_stop = False
    
    def show_img(self, url):
        self.stop_gif()
        img = self.fetch_img(url)
        if img is None:
            return
        if img.format != "GIF":
            img.thumbnail((self.width, self.height))
        else:
            self.gif_thread = threading.Thread(target=self.show_gif, args=(img,))
            self.gif_thread.start()
            return
        img_pixels = self.fetch_img_pixels(img)
        self.set_img_pixels(img_pixels)
        self.update()

    def set_img_pixels(self, img_pixels):
        if img_pixels is None: return
        for x in range(len(img_pixels[0])):
            for y in range(len(img_pixels)):
                self.set_pixel(x, y, img_pixels[x][y])

    def fetch_img(self, img_url):
        img = None
        if img_url[0:4] == "http":
            # Naive way to tell if this is a url vs a local file
            resp = requests.get(img_url, headers={"User-Agent": _USER_AGENT_STRING})
            resp.raise_for_status()
            img = Image.open(BytesIO(resp.content))
        else:
            if not os.path.isfile(img_url):
                raise FileNotFoundError("Image File Does Not Exist")
            img = Image.open(img_url)
        return img

    def fetch_img_pixels(self, img):
        thumb_w, thumb_h = img.size
        if thumb_h != self.height or thumb_w != self.width:
            return None
        pixels = []
        for x in range(self.width):
            row = []
            for y in range(self.height):
                if y >= thumb_h or x >= thumb_w:
                    color = (0, 0, 0)
                    continue
                else:
                    color = img.getpixel((x, y))
                if type(color) is int:
                    color = (color, color, color)
                else:
                    if len(color) >= 4 and color[3] == 0:
                        # If transparent, set color to black
                        color = (0, 0, 0)
                    color = (color[0], color[1], color[2])
                row.append(color)
            pixels.append(row)
        return pixels

    def stop_gif(self):
        print("Stop Gif")
        self._gif_stop = False
        if self.gif_thread is not None:
            print("Joining thread")
            self.gif_thread.join()
            print("Join Done")

    def show_gif(self, gif_img):
        self._gif_stop = True
        imgs = []
        delay_ms = gif_img.info.get("duration", 40)
        try:
            while True:
                frame = Image.new("RGBA", gif_img.size)
                frame.paste(gif_img, (0,0), gif_img.convert('RGBA'))
                frame.thumbnail((self.width, self.height))
                imgs.append(self.fetch_img_pixels(frame))
                gif_img.seek(gif_img.tell() + 1)
        except EOFError:
            pass
        while self._gif_stop:
            for img in imgs:
                self.set_img_pixels(img)
                self.update()

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
        for x in range(w):
            row = []
            for y in range(h):
                if x < 16 and y < 16:
                    grid_offset = grid_len*0
                elif x < 16 and y >= 16:
                    grid_offset = grid_len*1
                elif x >= 16 and y >= 16:
                    grid_offset = grid_len*2
                elif x >= 16 and y < 16:
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
