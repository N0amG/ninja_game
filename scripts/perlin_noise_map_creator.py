import pygame
from perlin_noise_generator import perlin_noise_map

from PIL import Image



def create_noise_map():
    return perlin_noise_map()


map = create_noise_map()

print(map)