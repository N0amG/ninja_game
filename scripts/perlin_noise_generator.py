import noise
from PIL import Image
import random

BASE_IMG_PATH = 'data/images/'

# Ajoutez ces deux lignes avant la boucle for
x_offset = random.random() * 100
y_offset = random.random() * 100


shape = (128, 128)

scale = 20.0
octaves = 3
persistence = 5
lacunarity = 1


ground = (140, 140, 140)

air = (255, 255, 255)

image_filepath = BASE_IMG_PATH + "noise.png"

image = Image.new('RGB', shape)

def set_color(x, y, image, value):

    if value < 0.2:
        image.putpixel((x, y), air)

    elif value < 1:
        image.putpixel((x, y), ground)

def perlin_noise_map():
    for x in range(shape[0]):
        for y in range(shape[1]):
            value = noise.pnoise2(x/scale + x_offset, 
                                y/scale + y_offset, 
                                octaves=octaves, 
                                persistence=persistence, 
                                lacunarity=lacunarity, 
                                repeatx=1024, 
                                repeaty=1024, 
                                base=0)
            
            image.putpixel((x, y), (int((value + 1) * 128), int((value + 1) * 128), int((value + 1) * 128)))
            set_color(x, y, image, value)
    image.save(image_filepath)

    print(image)
    
    
if __name__ == "__main__":
    perlin_noise_map()