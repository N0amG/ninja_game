import pygame
try:
    from scripts.perlin_noise_generator import perlin_noise_map, ground, air
    from scripts.tilemap import Tilemap
except ImportError:
    from perlin_noise_generator import perlin_noise_map, ground, air
    from tilemap import Tilemap
from PIL import Image
import random
import os


AUTOTILE_CLEANER = {
    tuple(sorted([(0, -1) ,(0, 1)])),
    tuple(sorted([(0, 1)])),
    tuple(sorted([(0, -1)])),
    tuple(sorted([(-1, 0), (1, 0)])),
}


class MapGenerator:

    
    def __init__(self, game, world_type, map_size = (32, 32), spawn_rate = 0.3):
        self.game = game
        self.world_type = world_type
        self.spawn_rate = spawn_rate
        self.regions = []
        self.noise_array = self.create_noise_map(map_size)
        self.save_pixel_array_as_png(self.noise_array)
        self.tilemap = Tilemap(game)
        self.turn_noise_map_into_tilemap()
        self.map_decoration()
        
        self.tile_list = list(game.assets)

        self.put_spawner_tile()

    def create_noise_map(self, map_size):
        pixel_array = perlin_noise_map(shape = map_size)
        
        pixel_array = self.noise_cleaner(pixel_array)

        ground_color_value = self.rgb_to_int(ground)
        
        self.regions = self.find_color_regions(pixel_array, ground_color_value)

        pixel_array = self.add_color_2_randomly(pixel_array, self.regions)
        
        pixel_array = self.map_cleaner(pixel_array)
        
        self.regions.extend(self.find_color_regions(pixel_array, self.ground2_color))
        return pixel_array
        
    def find_color_regions(self, pixel_array, target_color):
        visited = set()
        regions = []
        for x in range(pixel_array.shape[0]):
            for y in range(pixel_array.shape[1]):
                if (x, y) not in visited and pixel_array[x, y] == target_color:
                    region = []
                    stack = [(x, y)]
                    while stack:
                        px, py = stack.pop()
                        if (px, py) not in visited:
                            visited.add((px, py))
                            region.append((px, py))

                            # Vérifiez les pixels voisins
                            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                                nx, ny = px + dx, py + dy
                                if (0 <= nx < pixel_array.shape[0] and 0 <= ny < pixel_array.shape[1] and
                                    pixel_array[nx, ny] == target_color):
                                    stack.append((nx, ny))

                    regions.append(region)
        return regions
    
    def noise_cleaner(self, pixel_array, tolerance = 8):
        new_color_value = self.rgb_to_int(air)

        old_color_value = self.rgb_to_int(ground)        
        regions = self.find_color_regions(pixel_array, old_color_value)
        
        for region in regions:
            if len(region) < tolerance:
                for x, y in region:
                    pixel_array[x, y] = new_color_value

        return pixel_array

    def map_cleaner(self, pixel_array):
        width, height = pixel_array.shape
        for i in range(3):
            for y in range(height):
                for x in range(width):
                    pixel = pixel_array[x, y]
                    neighbors = set()
                    for shift in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                        check_x = x + shift[0]
                        check_y = y + shift[1]
                        if 0 <= check_x < width and 0 <= check_y < height:
                            if pixel_array[check_x, check_y] == pixel:
                                neighbors.add(shift)

                    neighbors = tuple(sorted(neighbors))
                    if neighbors in AUTOTILE_CLEANER or len(neighbors) <= 1:
                        pixel_array[x, y] = self.rgb_to_int(air)

        return pixel_array

    def map_decoration(self):
        for loc in self.tilemap.tilemap.copy():
            if self.tilemap.tilemap[loc]['type'] in ['grass', 'stone'] and self.tilemap.tilemap[loc]['variant'] == 1:
                if self.tilemap.tilemap[loc]['type'] == 'grass': chance = 0.75
                else : chance = 0.3
                if random.random() < chance:
                    if self.tilemap.tilemap[loc]['type'] == 'grass':
                        type = random.choices(['decor', 'large_decor'], weights=[0.5, 0.5], k=1)[0]
                        variant = random.choice([0, 1, 2]) if type == "large_decor" else random.choices([0, 1, 2, 3], weights=[0.3, 0.3, 0.3, 0.1], k=1)[0]
                    else:
                        type = random.choices(['decor', 'large_decor'], weights=[0.4, 0.6], k=1)[0]
                        variant = 0 if type == "large_decor" else 3
                    loc = tuple(loc.split(';'))
                    loc = (int(loc[0]), int(loc[1]) -1)
                    if type == "large_decor" and variant == 2: # tree
                        loc = (int(loc[0]), int(loc[1]) -3)
                        margin = random.choice([0, 1, 2])
                        if margin == 0: margin = 1.25
                        elif margin == 1: margin = 2
                        else: margin = 2.75
                        loc = (loc[0] * self.tilemap.tile_size- self.tilemap.tile_size//2, loc[1] * self.tilemap.tile_size + self.tilemap.tile_size*1.25)
                    
                    elif type == "large_decor" and variant == 1: # bush;
                        margin = random.random() *2
                        loc = (loc[0] * self.tilemap.tile_size - self.tilemap.tile_size//2, loc[1] * self.tilemap.tile_size + self.tilemap.tile_size/(3-margin))
                    
                    elif type == "large_decor" and variant == 0: # rock
                        loc = (loc[0] * self.tilemap.tile_size, loc[1] * self.tilemap.tile_size + self.tilemap.tile_size/2.25)
                    
                    if type == "decor":
                        self.tilemap.add_tile(loc, type, offgrid=False, variant= variant)
                    else:
                        self.tilemap.add_tile(loc, type, offgrid=True, variant= variant)
        self.tilemap.save('data/maps/perlin_noise_map.json')

    def extract_regions(self, pixel_array, regions):
        for i in range (len(regions)//2):
            region = random.choice(regions)
            for x, y in region:
                pixel_array[x, y] = self.rgb_to_int((140, 140, 140))
        
        return pixel_array
    
    def add_color_2_randomly(self, pixel_array, regions):
        self.ground2_color = self.rgb_to_int((140, 140, 140))
        for i in range (len(regions)//2):
            region = random.choice(regions)
            for x, y in region:
                pixel_array[x, y] = self.ground2_color
        
        return pixel_array
        
    def rgb_to_int(self, rgb : tuple):
        r, g, b = rgb
        return r * 65536 + g * 256 + b
    
    def turn_noise_map_into_tilemap(self):
        for x in range(self.noise_array.shape[0]):
            for y in range(self.noise_array.shape[1]):
                color = self.noise_array[x, y]
                if color == self.rgb_to_int(ground):
                    self.tilemap.add_tile((x, y), "grass")
                elif color == self.rgb_to_int((140, 140, 140)):
                    self.tilemap.add_tile((x, y), "stone")

        self.tilemap.autotile()
        
        self.tilemap.save('data/maps/perlin_noise_map.json')

    def put_spawner_tile(self, spawn_type = ["player", "enemy"]):
                    
            self.regions.sort(key = lambda x: len(x), reverse = True)
            self.regions = [list(item) for item in set(tuple(row) for row in self.regions)]
            if self.regions != [[]]:
                if 'player' in spawn_type:
                    surface_tiles = []
                    surface_tiles2 = []
                    index = len(self.regions)//2
                    player_region = self.regions[index]  # Get the player region without removing it
        
                    for loc in player_region:
                        check_loc = f"{loc[0]};{loc[1]}"
                        if check_loc in self.tilemap.tilemap:
                            if self.tilemap.tilemap[f"{loc[0]};{loc[1]}"]['variant'] == 1:
                                surface_tiles.append(loc)
                            elif self.tilemap.tilemap[f"{loc[0]};{loc[1]}"]['variant'] in (0, 2):
                                surface_tiles2.append(loc)
                    if len(surface_tiles) == 0:
                        surface_tiles = surface_tiles2[:]
                            
                    surface_tiles.sort(key = lambda x: x[0])
        
                    player_spawn_tile = surface_tiles[len(surface_tiles)//2]
                    player_pos = player_spawn_tile
                    player_spawn_tile = (player_spawn_tile[0] * self.tilemap.tile_size, (player_spawn_tile[1] -1) * self.tilemap.tile_size)
                    self.tilemap.add_tile(player_spawn_tile, "spawners", offgrid = True, variant = 0)
                    
                    
                if 'enemy' in spawn_type:
                    enemy_regions = [region for region in self.regions if region != player_region]  # Exclude the player region
                    for region in enemy_regions:
                        surface_tiles = []
                        for loc in region:
                            check_loc = f"{loc[0]};{loc[1]}"
                            if check_loc in self.tilemap.tilemap and self.tilemap.tilemap[f"{loc[0]};{loc[1]}"]['variant'] == 1:
                                surface_tiles.append(loc)
                        
                        if len(surface_tiles) > 0:
                            spawned = 0
                            max_spawn = len(surface_tiles) // 3
                            for loc in surface_tiles:
                                if ((player_pos[0] - loc[0]) ** 2 + (player_pos[1] - loc[1]) ** 2) ** 0.5 > 5:
                                    if random.random() <= self.spawn_rate and spawned < max_spawn:
                                        self.tilemap.add_tile((loc[0] * self.tilemap.tile_size, (loc[1]-1) * self.tilemap.tile_size), "spawners", offgrid = True, variant = 1)
                                        
                    self.tilemap.save('data/maps/perlin_noise_map.json')
        
    def save_pixel_array_as_png(self, pixel_array, path = 'data/images/noise.png'):
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
    map = MapGenerator(None, "forest")
