import pygame


import sys

from scripts.utils import load_images
from scripts.tilemap import Tilemap
from scripts.auto_map_creator import MapGenerator

RENDER_SCALE = 1.75



class Editor:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('editor')
        self.screen = pygame.display.set_mode((1080, 720), pygame.RESIZABLE)
        
        self.screen = pygame.display.set_mode((self.screen.get_size()[0]//2, self.screen.get_size()[1]//2), pygame.RESIZABLE)
        
        self.aspect_ratio = self.screen.get_width() / self.screen.get_height()
        
        self.display = pygame.Surface((self.screen.get_width()//RENDER_SCALE, self.screen.get_height()//RENDER_SCALE))
        
        self.display_original_size = self.display.get_size()
        
        self.clock = pygame.time.Clock()
        
        self.fps = 75
        self.dt = 1
        
        # Simulation joueur
        self.player = type('MyClass', (object,), {"rect": lambda: pygame.Rect(0, 0, 0, 0)})

                
        # Initialisation des manettes
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]

        self.assets = {
            "decor": load_images('tiles/decor'),
            "grass": load_images('tiles/grass'),
            "large_decor": load_images('tiles/large_decor'),
            "stone": load_images('tiles/stone'),
            "clouds": load_images('clouds'),
            "spawners": load_images('tiles/spawners'),
        }
        
        self.movement = [False, False, False, False]

        self.tilemap = Tilemap(self, tile_size=16)

        try:
            self.map_size = (64, 64)
            MapGenerator(self, 'grass', self.map_size, spawn_rate=0.5)
            self.tilemap.load('data/maps/perlin_noise_map.json')
            #self.tilemap.load('data/maps/3.json')
            #self.tilemap.load('level.json')
       
        except FileNotFoundError:
            return FileNotFoundError #self.tilemap.load('level.json')
        
        self.scroll = [0, 0]
        
        self.show_chunks_grid = False
        
        self.tile_list = list(self.assets)
        self.tile_group = 0
        self.tile_variant = 0
        
        self.clicking = False
        self.right_clicking = False
        self.shift = False
        self.left_alt = False
        
        self.ongrid = True
        self.zoom_lvl = RENDER_SCALE
        
    def run(self):
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.VIDEORESIZE:
                    new_width = max(self.display_original_size[0], event.w)
                    new_height = max(self.display_original_size[1], event.h)
                    self.screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicking = True
                    elif event.button == 3:
                        self.right_clicking = True
                    
                    if not self.shift and not self.left_alt:
                        if event.button == 4:
                            self.tile_group = (self.tile_group - 1) % len(self.tile_list)
                            self.tile_variant = 0
                        elif event.button == 5:
                            self.tile_group = (self.tile_group + 1) % len(self.tile_list)
                            self.tile_variant = 0
                    
                    elif self.shift:
                        if event.button == 4:
                            self.tile_variant = (self.tile_variant - 1) % len(self.assets[self.tile_list[self.tile_group]])
                        elif event.button == 5:
                            self.tile_variant = (self.tile_variant + 1) % len(self.assets[self.tile_list[self.tile_group]])
                    
                    if self.left_alt and not self.shift:
                        if event.button == 4:
                            self.zoom_lvl = min(3, self.zoom_lvl + 0.025)
                            self.display = pygame.transform.scale(self.display, (self.screen.get_width()//self.zoom_lvl, self.screen.get_height()//self.zoom_lvl))
                        elif event.button == 5:
                            self.zoom_lvl = max(0.25, self.zoom_lvl - 0.025)
                            self.display = pygame.transform.scale(self.display, (self.screen.get_width()//self.zoom_lvl, self.screen.get_height()//self.zoom_lvl))

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = False
                    elif event.button == 3:
                        self.right_clicking = False
                        
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_q:
                        self.movement[0] = True
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = True
                    elif event.key == pygame.K_UP or event.key == pygame.K_z:
                        self.movement[2] = True
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.movement[3] = True
                    elif event.key == pygame.K_LSHIFT:
                        self.shift = True
                    elif event.key == pygame.K_LALT:
                        self.left_alt = True
                    elif event.key == pygame.K_g:
                        self.ongrid = not self.ongrid
                    elif event.key == pygame.K_p:
                        MapGenerator(self, 'grass', self.map_size)
                        self.tilemap.load('data/maps/perlin_noise_map.json')
                    elif event.key == pygame.K_l:
                        self.tilemap.load('data/maps/perlin_noise_map.json')
                    elif event.key == pygame.K_c:
                        self.show_chunks_grid = not self.show_chunks_grid
                    elif event.key == pygame.K_o:
                        self.tilemap.save('level.json')
                    
                    elif event.key == pygame.K_t:
                        self.tilemap.autotile()

                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_q:
                        self.movement[0] = False
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = False
                    elif event.key == pygame.K_UP or event.key == pygame.K_z:
                        self.movement[2] = False
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.movement[3] = False
                    elif event.key == pygame.K_LSHIFT:
                        self.shift = False
                    elif event.key == pygame.K_LALT:
                        self.left_alt = False
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0:
                        self.clicking = True
                    if event.button == 1:
                        self.right_clicking = True
                elif event.type == pygame.JOYBUTTONUP:
                    if event.button == 0:
                        self.clicking = False
                    if event.button == 1:
                        self.right_clicking = False
                        
                elif event.type == pygame.JOYAXISMOTION:
                    if event.axis == 0:
                        if event.value < -0.3:
                            self.movement[0] = True
                        elif event.value > 0.3:
                            self.movement[1] = True
                        elif -0.3 < event.value < 0.3:
                            self.movement[0:2] = [False, False]
                    if event.axis == 1:
                        if event.value < -0.3:
                            self.movement[2] = True
                        elif event.value > 0.3:
                            self.movement[3] = True
                        elif -0.3 < event.value < 0.3:
                            self.movement[2:4] = [False, False]
                            
                elif event.type == pygame.JOYHATMOTION:
                    pass
                
            self.update()
            self.render()
            
            pygame.display.update()
            self.clock.tick(self.fps)
            self.dt = 1 / (self.clock.get_fps() +1)


    def update(self):

        self.scroll[0] += (self.movement[1] - self.movement[0]) * 2/ (self.zoom_lvl/3)
        self.scroll[1] += (self.movement[3] - self.movement[2]) * 2 / (self.zoom_lvl/3)
        
        
        
        mpos = pygame.mouse.get_pos()

        # Calculez les marges et le facteur de mise à l'échelle
        screen_width, screen_height = self.screen.get_size()
        if screen_width / screen_height > self.aspect_ratio:
            new_width = int(screen_height * self.aspect_ratio)
            margin_x = (screen_width - new_width) // 2
            margin_y = 0
            scale_factor = screen_height / self.display.get_height()
        else:
            new_height = int(screen_width / self.aspect_ratio)
            margin_x = 0
            margin_y = (screen_height - new_height) // 2
            scale_factor = screen_width / self.display.get_width()

        # Ajustez la position de la souris en fonction du facteur de mise à l'échelle et des marges
        self.mpos = ((mpos[0] / scale_factor) - margin_x/2 // self.zoom_lvl, (mpos[1] / scale_factor) - margin_y/2 // self.zoom_lvl)

        
        render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
        self.tile_pos = (int((self.mpos[0] + render_scroll[0]) // self.tilemap.tile_size), int((self.mpos[1] + render_scroll[1]) // self.tilemap.tile_size))

        if self.clicking and self.ongrid:
            self.tilemap.chunksManager.add_tile({'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': (self.mpos[0] + render_scroll[0], self.mpos[1] + render_scroll[1])})
        
        elif self.clicking and not self.ongrid:
            print([self.mpos[0] + render_scroll[0], self.mpos[1] + render_scroll[1]])
            self.tilemap.chunksManager.add_tile({'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': [self.mpos[0] + render_scroll[0], self.mpos[1] + render_scroll[1]]})
            self.clicking = False
                                              
        if self.right_clicking and self.ongrid:
            tile_loc = str(self.tile_pos[0]) + ';' + str(self.tile_pos[1])
            if tile_loc in self.tilemap.tilemap:
                del self.tilemap.tilemap[tile_loc]

        elif self.right_clicking and not self.ongrid:
            for tile in self.tilemap.offgrid_tiles.copy():
                tile_img = self.assets[tile['type']][tile['variant']]
                if pygame.Rect(tile['pos'][0] - self.scroll[0], tile['pos'][1] - self.scroll[1], tile_img.get_width(), tile_img.get_height()).collidepoint(self.mpos):
                    self.tilemap.offgrid_tiles.remove(tile)
                    break
        
    def render(self):
        # Remplissez self.screen avec du noir
        self.screen.fill((0, 0, 0))
        
        self.display.fill((0, 100, 200))
        self.display = pygame.transform.scale(self.display, (self.screen.get_width()//self.zoom_lvl, self.screen.get_height()//self.zoom_lvl))
        
        # Dessinez vos objets de jeu sur self.display
        
        render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
        
        self.tilemap.chunksManager.render(self.display, offset=render_scroll)

        if self.show_chunks_grid : self.tilemap.chunksManager.chunks_grid_render(self.display, offset=render_scroll)
        
        current_tile_img = self.assets[self.tile_list[self.tile_group]][self.tile_variant].copy()
        current_tile_img.set_alpha(128)
        
        if self.ongrid:
            self.display.blit(current_tile_img, (self.tile_pos[0] * self.tilemap.tile_size - render_scroll[0], self.tile_pos[1] * self.tilemap.tile_size - render_scroll[1]))
        else:
            self.display.blit(current_tile_img, (self.mpos[0], self.mpos[1]))

        
        # Redimensionnez self.display à la taille de self.screen
        self.display = pygame.transform.scale(self.display, self.screen.get_size())
        

        self.screen.blit(self.display, (0, 0))
    
        pygame.display.flip()
        

Editor().run()