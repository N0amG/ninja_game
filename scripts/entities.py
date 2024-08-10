import pygame
from scripts.particle import Particle
import math
import random
from scripts.sparks import Spark



class PhysicsEntity:
    def __init__(self, game, e_type, id, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        
        self.action = ''
        self.anim_offset = (-3, -3)
        
        self.flip = False
        self.set_action('idle')
        
        self.last_movement = [0, 0]
        
        self.id = id
    
    def __str__(self):
        return f'{self.type}, {self.id}'
    
    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()

    def update(self, chunksManager, movement=(0, 0), tag = None, dt = 1):
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        frame_movement = ((movement[0] + self.velocity[0]) * dt , (movement[1] + self.velocity[1]) * dt)
        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in chunksManager.physics_rects_around(self.pos, tag=tag):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x
        
        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in chunksManager.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y
                
        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True
            
        self.last_movement = movement

        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0

        elif not self.collisions['down']:
            self.velocity[1] = min(5 * dt, self.velocity[1] + 0.1 * dt)

                
        self.animation.update()
        
    
    def jump(self):
        self.velocity[1] = -3

    
    def render(self, surf, offset=(0 ,0)):
        #affiche l'id au dessus de leur tete
        #surf.blit(pygame.font.SysFont('arial', 15).render(str(self.id), True, (255, 255, 255)), (self.pos[0] - offset[0] -5, self.pos[1] - offset[1] - 20))
        
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))

class Enemy(PhysicsEntity):
        
        def __init__(self, game, pos, id):
            super().__init__(game, 'enemy', id, pos, (8, 15))
            self.walking = 0

        def update(self, chunksManager, movement=(0, 0), dt = 1):

            if self.walking:
                if chunksManager.solid_check((self.rect().centerx + (-7 if self.flip else 7), self.pos[1] + 23)) and not (self.collisions['right'] or self.collisions['left']):
                    movement = (movement[0] - 0.5 if self.flip else 0.5, movement[1])
                else: 
                    self.flip = not self.flip

                self.walking = max(0, self.walking - 1)

                if not self.walking:
                    dist = (self.game.player.pos[0] - self.pos[0], self.game.player.pos[1] - self.pos[1])
                    if (abs(dist[1]) < 16) and (abs(dist[0]) < 200):
                        if self.flip and dist[0] < 0:
                            self.game.projectiles.append([ [self.rect().centerx -7, self.rect().centery], -1.5, 0])
                            self.game.sfx["shoot"].play()
                            for i in range(4):
                                self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5 + math.pi, 2 + random.random()))
                        if not self.flip and dist[0] > 0:
                            self.game.projectiles.append([ [self.rect().centerx +7, self.rect().centery], 1.5, 0])
                            self.game.sfx["shoot"].play()
                            for i in range(4):
                                self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5, 2 + random.random()))
                            
            elif random.random() < 0.01:
                self.walking = random.randint(30, 120)
                self.flip = not self.flip
            
            super().update(chunksManager, movement=movement, dt = dt)
            
            if movement[0] != 0:
                self.set_action('run')
            else:
                self.set_action('idle')
            
            if abs(self.game.player.dashing) >= 50:
                if self.rect().colliderect(self.game.player.rect()):
                    
                    self.game.screenshake = max(16, self.game.screenshake)
                    self.game.sfx["hit"].play()
                    
                    for i in range(30):
                        angle = random.random() * math.pi * 2
                        speed = random.random() * 5
                        self.game.sparks.append(Spark(self.game.player.rect().center, angle, random.random() + 2))
                        self.game.particles.append(Particle(self.game, 'particle', self.game.player.rect().center, [math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
                    self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                    self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                    
                    return True
        
        def render(self, surf, offset=(0 ,0)):
            super().render(surf, offset=offset)

            x_margin = -4 - self.game.assets["gun"].get_width() if self.flip else 4
            surf.blit(pygame.transform.flip(self.game.assets['gun'], self.flip, False), (self.rect().centerx + x_margin- offset[0], self.rect().centery - offset[1]))

class Player(PhysicsEntity):
    
    def __init__(self, game, pos, id):
        super().__init__(game, 'player', id, pos, (8, 15))
        self.air_time = 0
        self.available_jump = 2
        self.jumps = self.available_jump
        self.dashing = 0
        
    def update(self, chunksManager, movement=(0, 0), dt = 1):
        
        if self.velocity[0] != 0 : 
            if (movement[0] > 0 and self.velocity[0] < 0) or (movement[0] < 0 and self.velocity[0] > 0):
                movement = (-movement[0], movement[1])

        super().update(chunksManager, movement=movement, tag="player", dt = dt)
        if self.velocity[0] != 0 : 
            if self.velocity[0] > 0: self.flip = False
            if self.velocity[0] < 0: self.flip = True
                
        self.air_time += 1 * dt
        
        if self.air_time >= 250:
            if not self.game.dead:
                self.game.sfx['hit'].play()
                self.game.screenshake = max(64, self.game.screenshake)
                self.game.score_update(-25)
            self.game.dead += 1
            
                    
        if self.collisions['down']:
            self.air_time = 0
            self.jumps = self.available_jump
        
        self.wall_slide = False
        if self.air_time > 4 and (self.collisions['right'] or self.collisions['left']):
            self.set_action('wall_slide')
            self.wall_slide = True
            self.velocity[1] = min(0.5, self.velocity[1])
            self.air_time = 5
        
        if not self.wall_slide:
            if self.air_time > 4:    
                self.set_action('jump')
            
            elif movement[0] != 0:
                self.set_action('run')
            
            else:
                self.set_action('idle')

        if abs(self.dashing) in {50, 60}:
            for i in range(20):
                angle = random.random() * math.pi * 2
                speed = random.random() * 0.5 + 0.5
                pvelocity = [math.cos(angle) * speed, math.sin(angle) * speed]
                
                self.game.particles.append(Particle(self.game, 'particle', self.rect().center, pvelocity, frame=random.randint(0, 7)))

        if self.dashing > 0:
            self.dashing = max(self.dashing - 1, 0)

        elif self.dashing < 0 :
            self.dashing = min(self.dashing + 1, 0)
        
        if abs(self.dashing) > 50:
            self.velocity[0] = abs(self.dashing) / self.dashing * 8

            if abs(self.dashing) == 51:
                self.velocity[0] *= 0.1
            pvelocity = [(abs(self.dashing) / self.dashing * random.random() *3) * dt, 0]
                
            self.game.particles.append(Particle(self.game, 'particle', self.rect().center, pvelocity, frame=random.randint(0, 7)))
            
        
        
        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
        elif self.velocity[0] < 0:
            self.velocity[0] = min(self.velocity[0] + 0.1 , 0)
            
    def jump(self):
        if not self.wall_slide:
            if self.jumps > 0:
                self.jumps -= 1
                self.air_time = 5
                super().jump()
                return True
        else:
            self.velocity[1] = -2.5
            self.velocity[0] = -3 if self.collisions["right"] else 3
            self.flip = not self.flip
            self.jumps = min(self.jumps + 1, self.available_jump-1)
            return True

    def dash(self):
        if not self.dashing:
            self.game.sfx["dash"].play()
            self.dashing = -60 if self.flip else 60

    def render(self, surf, offset=(0 ,0)):
        if abs(self.dashing) <= 50:
            super().render(surf, offset=offset)
