import sys

import scripts.utils as utils

import pygame


class GameObject:
    def __init__(self, image_path, position):
        self.anim = utils.Animation(utils.load_images(image_path))
        self.image = utils.load_image(image_path)
        self.position = list(position)

    def update(self, movement):
        self.position[1] += movement[1] - movement[0]
        self.anim.update()

    def render(self, screen):
        screen.blit(self.anim.img(), self.position)

class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('ninja game')
        self.screen = pygame.display.set_mode((1080, 720), pygame.RESIZABLE)
        
        self.aspect_ratio = self.screen.get_width() / self.screen.get_height()
        
        self.display = pygame.Surface((self.screen.get_width()//3, self.screen.get_height()//3))
        
        self.display_original_size = self.display.get_size()
        
        self.clock = pygame.time.Clock()
        
        self.fps = 75
        self.dt = 1

        
        self.movement = [False, False]

        self.assets = {
            "player/idle": utils.Animation('entities/player/idle/')
        }
        
        self.player = GameObject('entities/player/idle', [60, 160])

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
                    if event.key == pygame.K_UP:
                        self.movement[0] = True
                    elif event.key == pygame.K_DOWN:
                        self.movement[1] = True
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP:
                        self.movement[0] = False
                    elif event.key == pygame.K_DOWN:
                        self.movement[1] = False
            
            self.update()
            self.render()
            
            pygame.display.update()
            self.clock.tick(self.fps)
            self.dt = 1 / (self.clock.get_fps() +1)
            
    def update(self):
        
        for game_object in self.games_objects:
            game_object.update(self.movement)
    
    def render(self):
        # Remplissez self.screen avec du noir
        self.screen.fill((0, 0, 0))
    
        # Dessinez vos objets de jeu sur self.display
        self.display.fill((14, 219, 248))
        for game_object in self.games_objects:
            game_object.render(self.display)
       
    
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