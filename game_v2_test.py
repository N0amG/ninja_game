import sys
import os

import random
import math

from scripts.utils import load_image, load_images, Animation, load_image_switched_colorkey, load_images_switched_colorkey
from scripts.entities import Player, Enemy
from scripts.tilemap_v2_test import Tilemap, ChunksManager
from scripts.clouds import Clouds
from scripts.particle import Particle
from scripts.sparks import Spark
#from scripts.perlin_noise_map_creator import MapGenerator

SCREEN_SIZE = 1
RENDER_SCALE = 3.5 # 1.75 pour screen size de 2

import pygame

def rgb(r, g, b):
    return (r, g, b)

class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('ninja game')
        self.screen = pygame.display.set_mode((1080, 720), pygame.RESIZABLE)
        
        self.screen = pygame.display.set_mode((self.screen.get_size()[0]//SCREEN_SIZE, self.screen.get_size()[1]//SCREEN_SIZE), pygame.RESIZABLE)
                
        self.display = pygame.Surface((self.screen.get_width()//RENDER_SCALE, self.screen.get_height()//RENDER_SCALE), pygame.SRCALPHA)
        
        self.display_2 = pygame.Surface(self.display.get_size(), pygame.SRCALPHA)
        
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
            "enemy/idle": Animation(load_images('entities/enemy/idle'), 8),
            "enemy/run": Animation(load_images('entities/enemy/run')),
            "gun": load_image('gun.png'),
            "projectile" : load_image('projectile.png'),
        }
        
        self.autumn_color_list = [
            
                    (rgb(70, 33, 31),   rgb(70, 33, 31)), #1
                    (rgb(98, 53, 48),   rgb(98, 53, 48)), #2
                    (rgb(148, 85, 66),  rgb(148, 85, 66)), #3
                    (rgb(15, 39, 56),   rgb(191, 64, 12)), #4
                    (rgb(26, 69, 59),   rgb(230, 74, 25)), #5
                    (rgb(46, 106, 66),  rgb(255, 112, 67)), #6
                    (rgb(80, 155, 75),  rgb(255, 202, 40)), #7
                    (rgb(123, 207, 92), rgb(255, 167, 38)), #8
                    
                ]
        
        self.winter_color_list = [
            
                    (rgb(70, 33, 31),   rgb(70, 33, 31)), #1
                    (rgb(98, 53, 48),   rgb(98, 53, 48)), #2
                    (rgb(148, 85, 66),  rgb(148, 85, 66)), #3
                    (rgb(15, 39, 56),   rgb(144, 164, 174)), #4
                    (rgb(26, 69, 59),   rgb(143, 214, 223)), #5
                    (rgb(46, 106, 66),  rgb(191, 230, 235)), #6
                    (rgb(80, 155, 75),  rgb(238, 238, 238)), #7
                    (rgb(123, 207, 92), rgb(255, 255, 255)), #8
                    
                ]
        
        self.death_color_list = [
            
                    (rgb(70, 33, 31),   rgb(38, 50, 56)), #1
                    (rgb(98, 53, 48),   rgb(55, 71, 79)), #2
                    (rgb(148, 85, 66),  rgb(81, 101, 110)), #3
                    (rgb(15, 39, 56),   rgb(26, 8, 8)), #4
                    (rgb(26, 69, 59),   rgb(55, 0, 0)), #5
                    (rgb(46, 106, 66),  rgb(101, 2, 2)), #6
                    (rgb(80, 155, 75),  rgb(154, 14, 14)), #7
                    (rgb(123, 207, 92), rgb(229, 11, 11)), #8
                    
                    # Background
                    (rgb(19, 178, 242), rgb(49, 0, 0)),
                    (rgb(14, 219, 248), rgb(104, 5, 5)),
                    (rgb(65, 243, 252), rgb(214, 0, 0)),
                    
                    # Clouds
                    (rgb(163, 172, 190), rgb(27, 28, 29)),
                    (rgb(219, 224, 231), rgb(47, 48, 49)),
                    
                    # Rocks
                    (rgb(57, 58, 86), rgb(20, 0, 0)),
                    (rgb(78, 83, 113), rgb(46, 4, 4)),
                    (rgb(103, 112, 139), rgb(61, 18, 18)),
                    (rgb(164, 172, 190), rgb(75, 15, 15)),
                ]

        self.sfx = {
            "jump": pygame.mixer.Sound('data/sfx/jump.wav'),
            "dash": pygame.mixer.Sound('data/sfx/dash.wav'),
            "hit": pygame.mixer.Sound('data/sfx/hit.wav'),
            "shoot" : pygame.mixer.Sound('data/sfx/shoot.wav'),
            "ambience" : pygame.mixer.Sound('data/sfx/ambience.wav')
        }
        
        self.sfx['ambience'].set_volume(0.2)
        self.sfx['dash'].set_volume(0.3)
        self.sfx['hit'].set_volume(0.8)
        self.sfx['shoot'].set_volume(0.4)
        self.sfx['jump'].set_volume(0.7)
        
        self.clouds = Clouds(self.assets['clouds'])
        
        self.movement = [False, False]
        self.id = 0
        
        self.player = Player(self, (250, 50), self.id)

        self.scroll = [0, 0]
        self.scroll[0] = self.player.rect().centerx - self.display.get_width() / 2
        self.scroll[1] = self.player.rect().centery - self.display.get_height() / 2

        self.tilemap = Tilemap(self, tile_size=16)
        
        self.score = 0
        
        self.level = 0
        self.world = 0
        
        self.load_level(self.level)
        
    
    def score_update(self, score = 0):
        self.score = max(0, self.score + score)
        font = pygame.font.Font(None, 35)
        score_render = font.render(str(self.score), True, (255, 255, 255))
        return self.score, score_render
    
    def switch_assets_color(self, color_list):
        
        self.assets["grass"] = load_images_switched_colorkey('tiles/grass', color_list)
        
        self.assets["large_decor"] = load_images_switched_colorkey('tiles/large_decor', color_list)
        
        self.assets["decor"] = load_images_switched_colorkey('tiles/decor', color_list)
        
        self.assets["particle/leaf"] = Animation(load_images_switched_colorkey('particles/leaf', color_list), img_dur=20, loop=False)
        
        if color_list == self.death_color_list:
            self.assets['background'] = load_image_switched_colorkey('background.png', color_list)
            self.assets['clouds'] = load_images_switched_colorkey('clouds', color_list)
            self.clouds = Clouds(self.assets['clouds'])
        
    def load_level(self, map_id):
        
        self.tiles_display = pygame.Surface((self.display.get_width(), self.display.get_height()), pygame.SRCALPHA)
        self.tiles_display.fill((0, 0, 0, 0))
        
        self.tiles_display_2 = pygame.Surface(self.tiles_display.get_size(), pygame.SRCALPHA)
        self.tiles_display_2.fill((0, 0, 0, 0))
        '''
        self.tiles_mask = pygame.mask.from_surface(self.tiles_display)
        self.tiles_mask = self.tiles_mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))
        for offset in [(0,-1), (0, 1), (-1, 0), (1,0)]:
            self.tiles_display_2.blit(self.tiles_mask, offset)
        '''
        
        self.score_update(50) if self.level != 0 else None
        if map_id % 3 == 0:
            self.world += 1 if map_id != 0 else 0
            self.score_update(100) if self.world != 0 else None
            
            if self.world == 1:
                
                self.switch_assets_color(self.winter_color_list)

        try:
            self.tilemap.load('data/maps/' + str(map_id) + '.json')
        except:
            self.level = 0
            self.tilemap.load('data/maps/' + str(self.level) + '.json')
        #self.tilemap.load('data/maps/perlin_noise_map.json')
        
        if self.tilemap.chunksManager.respawn_pos:
            self.player.pos = self.tilemap.chunksManager.respawn_pos
        
        self.enemies = []
        self.leaf_spawners = []
        
        self.id = 0
        self.tilemap.chunksManager.reset()
        
        self.projectiles = []
        self.particles = []
        self.sparks = []
        self.player = Player(self, self.player.pos, self.id)
        self.tilemap.chunksManager.set_player(self.player)
        
        self.scroll = [0, 0]
        self.scroll[0] = self.player.rect().centerx - self.display.get_width() / 2
        self.scroll[1] = self.player.rect().centery - self.display.get_height() / 2
        
        self.debug = True
        
        self.dead = 0
        self.screenshake = 0
        
        self.transition = -30
    
    def run(self):
        
        pygame.mixer.music.load('data/music.wav')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        
        self.sfx['ambience'].play(-1)
        
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
                        if self.player.jump():
                            self.sfx['jump'].play()
                    elif event.key == pygame.K_c:
                        self.debug= not self.debug
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_q:
                        self.movement[0] = False
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = False

                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0:
                        if self.player.jump():
                            self.sfx['jump'].play()
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
        self.screenshake = max(0, self.screenshake - 1)
        
        if self.dead:
            self.dead += 1
            if self.dead > 150:
                self.transition = min(30, self.transition+1)
            
            if self.dead > 200:
                self.load_level(self.level)

        if not self.dead:
            self.player.update(self.tilemap.chunksManager, (self.movement[1] - self.movement[0], 0))

        # [ [x, y], direction, timer]
        for projectile in self.projectiles.copy():
            projectile[0][0] += projectile[1]
            projectile[2] += 1
            
            if self.tilemap.chunksManager.solid_check(projectile[0]):
                self.projectiles.remove(projectile)
                for i in range(4):
                    self.sparks.append(Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0), 2 + random.random()))
            if projectile[2] > 360:
                self.projectiles.remove(projectile)
            
            elif abs(self.player.dashing) < 50:
                if self.player.rect().collidepoint(projectile[0]) and not self.dead:
                    self.projectiles.remove(projectile)
                    for i in range(30):
                        angle = random.random() * math.pi * 2
                        speed = random.random() * 5
                        self.sparks.append(Spark(self.player.rect().center, angle, random.random() + 2))
                        self.particles.append(Particle(self, 'particle', self.player.rect().center, [math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
                    self.dead += 1
                    self.score_update(-25)
                    self.screenshake = max(64, self.screenshake)
                    self.sfx['hit'].play()
                    
        self.clouds.update()
        

        self.tilemap.chunksManager.update()

        for sparks in self.sparks.copy():
            kill = sparks.update()
            if kill:
                self.sparks.remove(sparks)

        for particle in self.particles.copy():
            kill = particle.update()
            if particle.type == 'leaf':
                particle.pos[0] += math.sin(particle.animation.frame * 0.035) *0.3
            if kill:
                self.particles.remove(particle)
        
        
        # transition de niveau pass pour l'instant
        if not len(self.enemies):
            self.transition += 1
            if self.transition > 30:
                self.level = min(self.level + 1, len(os.listdir('data/maps')) -1)
                self.load_level(self.level)
        
        if self.transition < 0:
            self.transition += 1

    
    
    def render(self):
        # Remplissez self.screen avec du noir
        self.screen.fill((0, 0, 0))
        self.screen.blit(pygame.transform.scale(self.assets['background'], self.screen.get_size()), (0, 0))
        
        self.display.fill((0, 0, 0, 0))
        self.display_2.fill((0, 0, 0, 0))
        self.display = pygame.transform.scale(self.display, (self.screen.get_width()//RENDER_SCALE, self.screen.get_height()//RENDER_SCALE))
        self.display_2 = pygame.transform.scale(self.display_2, self.display.get_size())
        
        # Dessinez vos objets de jeu sur self.display
        
        self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 20
        self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 20
        render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

        compteur = [0, 0, 0, 0, 0, 0] # [tiles, enemy, leafs, projectiles, sparks, particles]
        
        self.clouds.render(self.display_2, offset=render_scroll)
        
        #compteur = [x+y for x, y in zip(compteur, self.tilemap.chunksManager.render(self.display, offset=render_scroll))]
        self.tilemap.chunksManager.render(self.display, offset=render_scroll)
        if not self.dead:
            self.player.render(self.display, offset=render_scroll)
        
        
        img = self.assets['projectile']
        
        for projectile in self.projectiles:
            self.display.blit(img, (projectile[0][0] - img.get_width()/2- render_scroll[0], projectile[0][1] - img.get_height()/2 - render_scroll[1]))
            compteur[3] += 1
            
        
        for sparks in self.sparks:
            sparks.render(self.display, offset=render_scroll)
            compteur[4] += 1
        
        score, score_render = self.score_update()
        self.display.blit(score_render, (2, 2))
        
        display_mask = pygame.mask.from_surface(self.display)
        display_sillhouette = display_mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))
        for offset in [(0,-1), (0, 1), (-1, 0), (1,0)]:
            self.display_2.blit(display_sillhouette, offset)
        
        
        for particle in self.particles:
            x, y = particle.pos  # Assurez-vous que particle.pos existe et contient la position
            # Convertir la position de la particule en tenant compte de l'offset de rendu
            x -= render_scroll[0]
            y -= render_scroll[1]
            # Vérifier si la particule est dans la zone visible de l'écran avant de la rendre
            if 0 <= x < self.display.get_width() and 0 <= y < self.display.get_height():
                particle.render(self.display, offset=render_scroll)
                compteur[5] += 1
        
        #print(compteur)

                
        # transitions
        if self.transition:
            transition_surf = pygame.Surface(self.display.get_size())
            pygame.draw.circle(transition_surf, (255, 255, 255), (self.display.get_width()//2, self.display.get_height()//2), (30 - abs(self.transition))*8)
            transition_surf.set_colorkey((255, 255, 255))
            self.display.blit(transition_surf, (0, 0))

        # Redimensionnez self.display à la taille de self.screen
        self.display = pygame.transform.scale(self.display, self.screen.get_size())
        self.display_2 = pygame.transform.scale(self.display_2, self.display.get_size())
        
        # Dessinez la copie redimensionnée de self.display au centre de self.screen
        screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2, random.random() * self.screenshake - self.screenshake / 2)
        #display_rect = scaled_display.get_rect(center=tuple(a + b for a, b in zip(self.screen.get_rect().center, screenshake_offset)))
        

        self.screen.blit(self.display_2, screenshake_offset)
        self.screen.blit(self.display, screenshake_offset)


        # Créez un objet de police pour dessiner le texte
        font = pygame.font.Font(None, 35)  # Utilisez None pour la police par défaut de pygame, et 24 pour la taille

        # Créez le texte des FPS minimum
        fps_text = font.render(f"FPS: {int(self.clock.get_fps())}", True, (255, 255, 255))
        
        
        #self.tilemap.chunksManager.displayed_tiles_number_render(compteur[0], self.screen, offset)
        
        
        # Obtenez la taille de l'écran pour positionner le texte en haut à droite
        screen_width, screen_height = self.screen.get_size()

        # Positionnez le texte en haut à droite, avec une petite marge
        text_x = screen_width - fps_text.get_width() - 10
        text_y = 10

        self.screen.blit(fps_text, (text_x, text_y))

        # Dessinez le texte sur self.screen
        if self.debug:
            self.tilemap.chunksManager.chunks_grid_render(self.display_2, offset)


        pygame.display.flip()


def clean():
    for folder in os.listdir('scripts'):
        if folder == "__pycache__":
            for file in os.listdir('scripts/__pycache__/'):
                os.remove('scripts/__pycache__/' + file)
            os.rmdir('scripts/__pycache__/')
clean()

Game().run()


