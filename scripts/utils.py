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
            if self.frame >= len(self.images) * self.img_dur:
                self.is_done = True
        