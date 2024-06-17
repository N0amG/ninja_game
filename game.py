import sys
import os

import random
import math

from scripts.utils import load_image, load_images, Animation
from scripts.entities import Player
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle

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
        
        self.fps = 75
        self.dt = 1
        
        
        # Initialisation des manettes
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]

        self.assets = {
            "background" : load_image('background.png'),
            "player": load_image('entities/player.png'),
            "player/idle": Animation(load_images('entities/player/idle'), 8),
            "player/run": Animation(load_images('entities/player/run')),
            "player/jump": Animation(load_images('entities/player/jump')),
            "player/slide" : Animation(load_images('entities/player/slide/')),
            "player/wall_slide" : Animation(load_images('entities/player/wall_slide/')),
            "particle/leaf" : Animation(load_images('particles/leaf'), img_dur=20, loop=False),
            "particle/particle": Animation(load_images('particles/particle'), 6, loop=False),
            "decor": load_images('tiles/decor'),
            "grass": load_images('tiles/grass'),
            "large_decor": load_images('tiles/large_decor'),
            "stone": load_images('tiles/stone'),
            "clouds": load_images('clouds'),
        }
        

        self.clouds = Clouds(self.assets['clouds'])
        
        self.movement = [False, False]

        self.player = Player(self, (250, 50))

        self.tilemap = Tilemap(self, tile_size=16)
        self.tilemap.load('level.json')
        
        self.games_objects = [self.player]

        self.leaf_spawners = []
        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))

        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
            else:
                print(spawner['pos'], 'enemy')


        self.particles = []

        self.scroll = [0, 0]

    def run(self):
        
        while True:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    #clean()
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.VIDEORESIZE:
                    new_width = max(self.display_original_size[0], event.w)
                    new_height = max(self.display_original_size[1], event.h)
                    self.screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.player.dash()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_q:
                        self.movement[0] = True
                    elif event.key == pygame.K_RIGHT  or event.key == pygame.K_d:
                        self.movement[1] = True
                    elif event.key == pygame.K_UP or event.key == pygame.K_SPACE:
                        self.player.jump()
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_q:
                        self.movement[0] = False
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = False

                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0:
                        self.player.jump()
                    elif event.button == 2:
                        self.player.dash()
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
        
        # Mode dev
        # ----------------
        if self.player.pos[1] > 700:
            self.player.pos[1] = -500
            self.player.pos[0] = 250
        # ----------------
        
        self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
        
        self.clouds.update()

        for rect in self.leaf_spawners:
            if random.random() * 49999 < rect.width * rect.height:
                pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                self.particles.append(Particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20)))

        for particle in self.particles.copy():
            kill = particle.update()
            if particle.type == 'leaf':
                particle.pos[0] += math.sin(particle.animation.frame * 0.035) *0.3
            if kill:
                self.particles.remove(particle)
        
    def render(self):
        # Remplissez self.screen avec du noir
        self.screen.fill((0, 0, 0))
    
        # Dessinez vos objets de jeu sur self.display
        self.display.blit(self.assets['background'], (0, 0))
        
        self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 20
        self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 20
        render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

        
        self.clouds.render(self.display, offset=render_scroll)
        
        self.tilemap.render(self.display, offset=render_scroll)
        
        self.player.render(self.display, offset=render_scroll)

        for particle in self.particles:
            particle.render(self.display, offset=render_scroll)

        
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
        #scaled_display = pygame.transform.scale(self.display, self.screen.get_size())
        
        # Dessinez la copie redimensionnée de self.display au centre de self.screen
        display_rect = scaled_display.get_rect(center=self.screen.get_rect().center)
        self.screen.blit(scaled_display, display_rect)
    
        pygame.display.flip()


def clean():
    for folder in os.listdir('scripts'):
        if folder == "__pycache__":
            for file in os.listdir('scripts/__pycache__/'):
                os.remove('scripts/__pycache__/' + file)
            os.rmdir('scripts/__pycache__/')
clean()

Game().run()


