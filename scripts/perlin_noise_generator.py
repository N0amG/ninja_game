import noise
from pygame import PixelArray, Surface
import random
from  PIL import Image

import pygame, os

BASE_IMG_PATH = 'data/images/'

# Ajoutez ces deux lignes avant la boucle for

ground = (0, 200, 0)

air = (255, 255, 255)



def set_color(pixel_array, x, y, value, air, ground):
    if value < 0.1:
        pixel_array[x, y] = air
    elif value < 1:
        pixel_array[x, y] = ground


def perlin_noise_map(shape = (32, 32), scale = 5.0, octaves = 3, persistence = 0.5, lacunarity = 1.0):
    x_offset = random.random() * 100
    y_offset = random.random() * 100
    

    scale = 5.0
    octaves = 3
    persistence = 0.5
    lacunarity = 1.0



    pixel_array = PixelArray(Surface(shape))
    
    image = Image.new('RGB', shape)
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
            set_color(pixel_array, x, y, value, air, ground)
    
    image.save('data/images/og_noise.png') # Save the black and white noise
    save_pixel_array_as_png(pixel_array) # Save the colored noise
    return pixel_array

def save_pixel_array_as_png(pixel_array, path = 'data/images/noise.png'):
        # Créer une surface à partir du PixelArray
        surface = pygame.Surface(pixel_array.shape)
        pygame.surfarray.blit_array(surface, pixel_array)

        # Sauvegarder la surface en tant que fichier image
        pygame.image.save(surface, 'temp.png')

        # Ouvrir le fichier image avec PIL
        img = Image.open('temp.png')

        # Sauvegarder l'image avec PIL
        img.save(path)

        # Supprimer le fichier temporaire
        os.remove('temp.png')
if __name__ == "__main__":
    perlin_noise_map()