import sys

import pygame


class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('ninja game')
        self.screen = pygame.display.set_mode((640, 480))

        self.display = pygame.Surface((320, 240))
        
        self.clock = pygame.time.Clock()
        
        self.fps = 75
        self.dt = 1
        
        self.games_objects = []
        
    def run(self):
        
        while True:

            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.movement[0] = True
                    if event.key == pygame.K_DOWN:
                        self.movement[1] = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP:
                        self.movement[0] = False
                    if event.key == pygame.K_DOWN:
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
        self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
        
        self.display.fill((14, 219, 248))
        
        for game_object in self.games_objects:
            game_object.render(self.display)
        
        

Game().run()