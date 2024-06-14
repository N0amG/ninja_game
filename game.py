import sys

from scripts.utils import load_image, load_images, Animation
from scripts.entities import PhysicsEntity
from scripts.tilemap import Tilemap

import pygame


class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('ninja game')
        self.screen = pygame.display.set_mode((1080, 720), pygame.RESIZABLE)
        
        self.screen = pygame.display.set_mode((self.screen.get_size()[0]//2, self.screen.get_size()[1]//2), pygame.RESIZABLE)
        
        self.aspect_ratio = self.screen.get_width() / self.screen.get_height()
        
        self.display = pygame.Surface((self.screen.get_width()//1.75, self.screen.get_height()//1.75))
        
        self.display_original_size = self.display.get_size()
        
        self.clock = pygame.time.Clock()
                
        # Initialisation des manettes
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]

        self.assets = {
            "player": load_image('entities/player.png'),
            "player/idle": Animation(load_images('entities/player/idle'), 8),
            "decor": load_images('tiles/decor'),
            "grass": load_images('tiles/grass'),
            "large_decor": load_images('tiles/large_decor'),
            "stone": load_images('tiles/stone')
        }
        
        self.fps = 75
        self.dt = 1

        self.movement = [False, False]

        self.player = PhysicsEntity(self, 'player', (165, 40), (14, 18))

        self.tilemap = Tilemap(self, tile_size=16)

        self.games_objects = [self.player]


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

          
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    elif event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    elif event.key == pygame.K_UP:
                        self.player.jump()
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    elif event.key == pygame.K_RIGHT:
                        self.movement[1] = False

                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0:
                        self.player.jump()
                elif event.type == pygame.JOYBUTTONUP:
                    pass
                
                elif event.type == pygame.JOYAXISMOTION:
                    if event.axis == 0:
                        if event.value < -0.3:
                            self.movement[0] = True
                        elif event.value > 0.3:
                            self.movement[1] = True
                        elif -0.3 < event.value < 0.3:
                            self.movement = [False, False]
                                                
                elif event.type == pygame.JOYHATMOTION:
                    pass
                
            self.update()
            self.render()
            
            pygame.display.update()
            self.clock.tick(self.fps)
            self.dt = 1 / (self.clock.get_fps() +1)


    def update(self):
        
        self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
        
    def render(self):
        # Remplissez self.screen avec du noir
        self.screen.fill((0, 0, 0))
    
        # Dessinez vos objets de jeu sur self.display
        self.display.fill((14, 219, 248))
        
        self.tilemap.render(self.display)

        self.player.render(self.display)

        
        
        # Calculez la nouvelle taille de la copie de self.display tout en conservant le rapport d'aspect
        screen_width, screen_height = self.screen.get_size()
        if screen_width / screen_height > self.aspect_ratio:
            new_width = int(screen_height * self.aspect_ratio)
            new_height = screen_height
        else:
            new_width = screen_width
            new_height = int(screen_width / self.aspect_ratio)

        # Créez une copie redimensionnée de self.display
        scaled_display = pygame.transform.scale(self.display, (new_width, new_height))
    
        # Dessinez la copie redimensionnée de self.display au centre de self.screen
        display_rect = scaled_display.get_rect(center=self.screen.get_rect().center)
        self.screen.blit(scaled_display, display_rect)
    
        pygame.display.flip()
        
        

Game().run()