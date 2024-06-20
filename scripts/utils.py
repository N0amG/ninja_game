import pygame
import os

BASE_IMG_PATH = 'data/images/'


def load_image(path):
    try:
        img = pygame.image.load(BASE_IMG_PATH + path).convert()
        img.set_colorkey((0, 0, 0))
        return img
    except:
        print("Error loading image: " + path)
        return None

def load_image_switched_colorkey(path, list_of_colors_tuple):
    try:
        img = pygame.image.load(BASE_IMG_PATH + path).convert()
        img.set_colorkey((0, 0, 0))
        pixel_array = pygame.PixelArray(img)
        for old_color, new_color in list_of_colors_tuple:
            pixel_array.replace(old_color, new_color)

        del pixel_array
        return img
    except:
        print("Error loading image: " + path)
        return None
    
def load_images_switched_colorkey(path, list_of_colors_tuple):
    images = []

    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
        full_path = path + '/' + img_name
        if full_path.endswith('.png'):
            images.append(load_image_switched_colorkey(full_path, list_of_colors_tuple))
    return images

def load_images(path):
    images = []

    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
        full_path = path + '/' + img_name
        if full_path.endswith('.png'):
            images.append(load_image(full_path))
    return images


class Animation:
    
    def __init__(self, images, img_dur = 5, loop = True ) -> None:
        self.images = images
        self.img_dur = img_dur
        self.loop = loop
        self.is_done = False
        self.frame = 0
    
    def copy(self):
        return Animation(self.images, self.img_dur, self.loop)
    
    def img(self):
        return self.images[int(self.frame/self.img_dur)]
    
    def update(self):
        if self.loop:
            self.frame = (self.frame + 1) % (len(self.images) * self.img_dur)
        else:
            self.frame = min(self.frame + 1, len(self.images) * self.img_dur)
            if self.frame >= len(self.images) * self.img_dur -1:
                self.is_done = True
        