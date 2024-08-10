import pygame
import json
import copy
import math
import random
from scripts.particle import Particle
from scripts.entities import Enemy

NEIGHBORS_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (0, 0)]

PHYSICS_TILES = {'grass', 'stone'}

AUTOTILE_TYPES = {'grass', 'stone'}

AUTOTILE_MAP = {
    tuple(sorted([(1, 0), (0, 1)])): 0,
    tuple(sorted([(1, 0)])): 0,
    tuple(sorted([(-1, 0), (1, 0)])): 1,
    tuple(sorted([(0, 1)])): 1,
    tuple(sorted([(1, 0), (0, 1), (-1, 0)])): 1,
    tuple(sorted([(-1, 0), (0, 1)])): 2,
    tuple(sorted([(-1, 0)])): 2,
    tuple(sorted([(-1, 0), (0, -1), (0, 1)])): 3,
    tuple(sorted([(-1, 0), (0, -1)])): 4,
    tuple(sorted([(-1, 0), (0, -1), (1, 0)])): 5,
    tuple(sorted([(0, -1)])): 5,
    tuple(sorted([(1, 0), (0, -1)])): 6,
    tuple(sorted([(1, 0), (0, -1), (0, 1)])): 7,
    tuple(sorted([(0, -1), (0, 1)])): 7,
    tuple(sorted([(1, 0), (-1, 0), (0, 1), (0, -1)])): 8,
}

AUTOTILE_CLEANER = {
    tuple(sorted([(0, -1) ,(0, 1)])),
    tuple(sorted([(0, 1)])),
    tuple(sorted([(0, -1)])),
}


class Tilemap:

    def __init__(self, game, chunk_size=16, tile_size = 16):

        self.game = game
        self.tile_size = tile_size
        self.chunk_size = chunk_size
        self.chunks_map = {}
        self.tilemap = {}
        self.offgrid_tiles = []
        self.chunksManager = ChunksManager(game, self, chunk_size=chunk_size)
        

    def add_tile(self, tile_coordinates, tile_type, offgrid=False, variant=0):
        tile_loc = str(tile_coordinates[0]) + ";" + str(tile_coordinates[1])
        if tile_type is None:
            if tile_loc in self.tilemap:
                del self.tilemap[tile_loc]
        else:
            if offgrid:
                self.offgrid_tiles.append({'pos': tile_coordinates, 'type': tile_type, 'variant': variant})
            else:
                self.tilemap[tile_loc] = {'pos': tile_coordinates, 'type': tile_type, 'variant': variant}

    def chunk_mapping(self):
        self.chunks_map = {}
        offgrid_tiles = copy.deepcopy(self.offgrid_tiles)

        for tile in offgrid_tiles:
            tile['pos'] = (tile['pos'][0] / self.tile_size, tile['pos'][1] / self.tile_size)
                
                
        total_tiles = offgrid_tiles + list(self.tilemap.values()) 
        for tile in total_tiles:            
            chunk_coordinates = (tile['pos'][0] // self.chunk_size, tile['pos'][1] // self.chunk_size)
            chunk_loc = str(int(chunk_coordinates[0])) + ";" + str(int(chunk_coordinates[1]))
            if chunk_loc not in self.chunks_map:
                self.chunks_map[chunk_loc] = []
            self.chunks_map[chunk_loc].append(tile)
        
        return self.chunks_map

    def tilemap_cleaner(self):
        self.tilemap = {}
        self.offgrid_tiles = []

    def save(self, path):
        f = open(path, 'w')
        json.dump({'tilemap': self.tilemap, 'tile_size' : self.tile_size, 'offgrid': self.offgrid_tiles}, f)
        f.close()
    
    def load(self, path):
        f = open(path, 'r')
        map_data = json.load(f)
        f.close()
        
        self.tilemap = map_data['tilemap']
        self.tile_size= map_data['tile_size']
        self.offgrid_tiles = map_data['offgrid']
        self.chunksManager.set_chunks(chunks=self.chunk_mapping())
        self.tilemap_cleaner()
    
    def autotile(self):
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            neighbors = set()
            for shift in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                check_loc = str(tile['pos'][0] + shift[0]) + ";" + str(tile['pos'][1] + shift[1])
                if check_loc in self.tilemap:
                    if self.tilemap[check_loc]['type'] == tile['type']:
                        neighbors.add(shift)
            neighbors = tuple(sorted(neighbors))
            if (tile['type'] in AUTOTILE_TYPES) and (neighbors in AUTOTILE_MAP):
                tile['variant'] = AUTOTILE_MAP[neighbors]

    def map_cleaner(self):
        tilemap = self.tilemap
        for loc in tilemap.copy():
            tile = tilemap[loc]
            neighbors = set()
            for shift in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                check_loc = str(tile['pos'][0] + shift[0]) + ";" + str(tile['pos'][1] + shift[1])
                if check_loc in tilemap:
                    if tilemap[check_loc]['type'] == tile['type']:
                        neighbors.add(shift)

            neighbors = tuple(sorted(neighbors))
            if (neighbors in AUTOTILE_CLEANER or len(neighbors) <=1) and tile['type'] in AUTOTILE_TYPES:
                self.add_tile(tile['pos'], tile_type = None)

class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_info, game):
        super().__init__()
        # Utilisez game.assets pour obtenir l'image en fonction du type et de la variante de la tuile
        # Assurez-vous que game.assets est structuré de manière à accéder aux images via ['type']['variant']
        self.image = game.assets[tile_info['type']][tile_info['variant']]
        
        # La position est déterminée par 'pos', qui est une liste [x, y]
        # Multipliez par la taille de la tuile pour obtenir la position en pixels
        self.rect = self.image.get_rect(topleft=(tile_info['pos'][0] * 16, tile_info['pos'][1] * 16))

class Entity(pygame.sprite.Sprite):
    def __init__(self, entity, offset=(0, 0)):
        super().__init__()
        self.image = pygame.transform.flip(entity.animation.img(), entity.flip, False)
        self.rect = entity.rect()
        self.rect.topleft = (entity.pos[0] - offset[0] + entity.anim_offset[0], entity.pos[1] - offset[1] + entity.anim_offset[1])
        
class Chunk:
    
    def __init__(self, game, loc, tiles, size=16, tile_size=16):
        self.game = game
        self.size = size
        self.tile_size = tile_size
        self.tiles = tiles # 'x;y' format
        self.entities = []
        self.leaf_spawners = []
        self.particles = []
        self.loc = loc # 'x;y' format
    
    def __str__(self) -> str:
        return f"chunk : {self.loc} | tiles: {len(self.tiles)} | entities: {len(self.entities)} | leaf_spawners: {len(self.leaf_spawners)}"
    
    def get_loc(self):
        return self.loc

        
    def solid_check(self, pos):
        tile_loc = [int(pos[0]) // self.tile_size,  int(pos[1]) // self.tile_size]
        for tile in self.tiles:
            if tile_loc == tile['pos']:
                if tile['type'] in PHYSICS_TILES:
                    return tile
    
    def add_entity(self, entity):
        if entity not in self.entities:
            self.entities.append(entity)
    
    def send_entity(self, entity, chunk):
        self.entities.remove(entity)
        chunk.add_entity(entity)
        #print(entity, "sent from", self.loc, "to", chunk.loc)
    
    def add_leaf_spawners(self, leaf_spawners):
        if leaf_spawners not in self.leaf_spawners:
            self.leaf_spawners.append(leaf_spawners)
    
    def clear_entity(self):
        self.entities = []
    
    def update(self):
        entity_list = [entity.id for entity in self.entities]
        for entity in self.entities:
            if isinstance(entity, Enemy):
                kill = entity.update(self.game.tilemap.chunksManager, (0, 0))
                entity_chunk = self.game.tilemap.chunksManager.get_chunk(entity.rect().center)
                if  entity_chunk!= self:
                    self.send_entity(entity, entity_chunk)
                    
                if kill:
                    self.entities.remove(entity)
                    self.game.enemies.remove(entity)
                    self.game.score_update(10)

        for rect in self.leaf_spawners:
            if random.random() * 49999 < rect.width * rect.height:
                pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                self.particles.append(Particle(self.game, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20)))
        
        for particle in self.particles.copy():
            kill = particle.update()
            if particle.type == 'leaf':
                particle.pos[0] += math.sin(particle.animation.frame * 0.035) *0.3
            if kill:
                self.particles.remove(particle)


    def render(self, surf, offset=(0, 0)):
        compteur = [0, 0, 0, 0, 0, 0]  # [tiles, entities, leaf_spawners, particles, total, total_rendered]
    
        marge = 32  # Définir la marge autour de l'écran
        largeur_ecran, hauteur_ecran = self.game.display.get_size()
        
    
        # Calculer la zone visible en prenant en compte l'offset et la marge
        zone_visible_x_min = offset[0] - marge
        zone_visible_x_max = offset[0] + largeur_ecran + marge
        zone_visible_y_min = offset[1] - marge
        zone_visible_y_max = offset[1] + hauteur_ecran + marge

        

        tiles_group = pygame.sprite.Group()
        
        for tile in self.tiles:
            x, y = tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size
            if tile['type'] in self.game.assets and zone_visible_x_min <= x < zone_visible_x_max and zone_visible_y_min <= y < zone_visible_y_max:
                #surf.blit(self.game.assets[tile['type']][tile['variant']], (x - offset[0], y - offset[1]))
                # Création d'une instance de Sprite pour chaque tuile visible
                tile_sprite = Tile(tile, self.game)
                tile_sprite.rect.topleft = (x - offset[0], y - offset[1])
                tiles_group.add(tile_sprite)
                compteur[0] += 1
                

        entity_group = pygame.sprite.Group()
        
        for entity in self.entities:
            if zone_visible_x_min <= entity.pos[0] < zone_visible_x_max and zone_visible_y_min <= entity.pos[1] < zone_visible_y_max:
                #entity.render(surf, offset)
                entity_sprite = Entity(entity, offset)
                entity_group.add(entity_sprite)
                compteur[1] += 1
    
        for leaf in self.particles:
            if zone_visible_x_min <= leaf.pos[0] < zone_visible_x_max and zone_visible_y_min <= leaf.pos[1] < zone_visible_y_max:
                leaf.render(surf, offset)
                compteur[2] += 1
    
        return tiles_group, entity_group
    
    def extract(self, id_pairs, keep=False):
        matches = []
        for tile in self.tiles.copy():
            if (isinstance(tile["pos"], list)): # liste = offgrid
                if (tile['type'], tile['variant']) in id_pairs:
                    matches.append(tile)
                    if not keep:
                        self.tiles.remove(tile)

            if (isinstance(tile["pos"], tuple)): # tuple = ongrid
                if (tile['type'], tile['variant']) in id_pairs:
                    matches.append(tile.copy())
                    matches[-1]['pos'] = list(matches[-1]['pos']).copy()
                    matches[-1]['pos'][0] *= self.tile_size
                    matches[-1]['pos'][1] *= self.tile_size
                    if (tile['type'] == 'spawners'and tile['variant'] == 0):
                        self.game.tilemap.chunksManager.respawn_pos = matches[-1]['pos']
                    if not keep:
                        self.tiles.remove(tile)
        
        self.game.tilemap.chunksManager.loaded_at_least_once.add(self.loc)
        return matches



class ChunksManager:
    
    def __init__(self, game, tilemap, chunk_size=16):
        self.game = game
        self.player = self.game.player
        self.tilemap = tilemap
        self.chunk_size = chunk_size
        self.tile_size = self.tilemap.tile_size
        self.chunks = {}
        self.loaded_chunks = self.chunks_around()
        self.loaded_at_least_once = set(list(self.loaded_chunks.keys()))
        self.player_chunk = self.get_chunk(self.player.rect().center)
        self.respawn_pos = None

    def set_chunks(self, chunks):
        self.chunks = {}
        for chunk in chunks.copy():
            self.chunks[chunk]= Chunk(self.game, chunk, chunks[chunk])
        self.load_chunks()

    def set_player(self, player):
        self.player = player
        self.load_chunks()
    
    def add_entity(self, entity):
        entity_chunk = self.get_chunk(entity.rect().center)
        if entity_chunk != None:
            entity_chunk.add_entity(entity)
    
    def set_player_spawn_chunk(self, pos):
        self.respawn_pos = pos
    
    def add_leaf_spawners(self, leaf_spawners):
        leaf_spawners_chunk = self.get_chunk(leaf_spawners)
        if leaf_spawners_chunk:
            leaf_spawners_chunk.add_leaf_spawners(leaf_spawners)
    
    def clear_entity(self):
        for chunk in self.chunks:
            self.chunks[chunk].clear_entity()
            
    def add_chunk(self, chunk):
        self.chunks[chunk.get_loc()] = chunk

    def get_chunk(self, pos, tag=None):
        chunk_loc = str(int(pos[0]) // self.tilemap.tile_size //self.chunk_size) + ";" + str(int(pos[1])// self.tilemap.tile_size //self.chunk_size)
        if chunk_loc in self.chunks:
            return self.chunks[chunk_loc]
        else:
            if tag == "player":
                self.loaded_at_least_once.add(chunk_loc)
            return Chunk(self.game, chunk_loc, [])
    
    def tiles_around(self, pos, tag=None):
        tiles_around = []
        # Obtenir les chunks autour du joueur, y compris celui dans lequel il se trouve
        chunks = self.loaded_chunks
        for chunk in chunks:
            # Calculer la position locale de la tuile dans le chunk
            local_pos = self.get_chunk(pos, tag)
            if local_pos is not None:
                for offset in NEIGHBORS_OFFSETS:
                    check_loc = [int(pos[0]//self.tile_size + offset[0]),int(pos[1]//self.tile_size + offset[1])]
                    # Vérifier si la tuile est dans le chunk actuel
                    for tile in chunks[chunk].tiles:
                        if check_loc == tile["pos"]:
                            tiles_around.append(tile)
        #if tag == "player" : print(len(tiles_around))
        return tiles_around

    def solid_check(self, pos):
        chunk = self.get_chunk(pos)
        if chunk:
            return chunk.solid_check(pos)
    
    def extract_init(self, chunk=None):
        if chunk == None:
            self.load_chunks(is_respawn=True)
            self.game.leaf_spawners = []
            for tree in self.extract([('large_decor', 2)], keep=True):
                self.game.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))
                self.add_leaf_spawners(self.game.leaf_spawners[-1])
                
            self.game.enemies = []
            for spawner in self.extract([('spawners', 0), ('spawners', 1)]):
                if spawner['variant'] == 0:
                    self.game.player.pos = spawner['pos']
                    self.game.player.air_time = 0
                else:
                    self.game.enemies.append(Enemy(self.game, spawner['pos'],self.game.id))
                    self.game.id += 1
                    self.add_entity(self.game.enemies[-1])

        else:
            for tree in chunk.extract([('large_decor', 2)], keep=True):
                self.game.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))
                self.add_leaf_spawners(self.game.leaf_spawners[-1])
                
            for spawner in chunk.extract([('spawners', 0), ('spawners', 1)]):
                if spawner['variant'] == 0:
                    self.game.player.pos = spawner['pos']
                    self.game.player.air_time = 0
                else:
                    self.game.enemies.append(Enemy(self.game, spawner['pos'], self.game.id))
                    self.game.id += 1
                    self.add_entity(self.game.enemies[-1])
    
    def extract(self, id_pairs, keep=False, chunk=None):
        
        matches = []
        if chunk is None:
            chunks = self.loaded_chunks
            for chunk in chunks:
                matches += self.chunks[chunk].extract(id_pairs, keep)
        else:
            for chunk in chunks:
                matches += self.chunks[chunk].extract(id_pairs, keep)
        return matches
    
    def reset(self):
        self.clear_entity()
        self.loaded_at_least_once = set()
        self.load_chunks(is_respawn=True)
        self.extract_init()
        
    def physics_rects_around(self, pos, tag=None):
        rects = []
        
        for tile in self.tiles_around(pos, tag):
            if tile['type'] in PHYSICS_TILES:
                rects.append(pygame.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size))

        return rects
    
    def add_tile(self, tile):
        chunk = self.get_chunk(tile['pos'])
        chunk.add_tile(tile['pos'], tile)

    def chunks_around(self, pos=None):
        if pos is None:
            pos = list(self.player.rect().center)
            #print("player pos", pos)
            offset = self.game.scroll
            #pos[0], pos[1] = pos[0] - offset[0], pos[1] - offset[1]
            #print("player pos - offset", pos)
        chunks_around = {}
        tile_size = self.tilemap.tile_size
        chunk_loc = (pos[0] // tile_size // self.chunk_size, pos[1] // tile_size // self.chunk_size)
        for offset in NEIGHBORS_OFFSETS:
            check_loc = str(chunk_loc[0] + offset[0]) + ";" + str(chunk_loc[1] + offset[1])
            if check_loc in self.chunks:
                chunk = self.chunks[check_loc]
                if check_loc not in chunks_around:  # Vérifie si le chunk n'est pas déjà dans la liste
                    chunks_around[check_loc] = chunk
        [self.loaded_at_least_once.add(chunk) for chunk in chunks_around.keys()]
        return chunks_around
    
    def load_chunks(self, is_respawn=False):
        current_player_chunk = self.get_chunk(self.player.rect().center)
        if self.respawn_pos and is_respawn:
            current_player_chunk = self.get_chunk(self.respawn_pos)
        
        if current_player_chunk != self.player_chunk:
            self.player_chunk = current_player_chunk
            self.loaded_chunks = self.chunks_around()
    
    def update(self):
        #print(len(self.loaded_at_least_once))
        previous_loaded_chunks = self.loaded_at_least_once.copy() 
        
        self.load_chunks()
        #print(self.loaded_at_least_once)
        for chunk in self.loaded_chunks:

            self.loaded_chunks[chunk].update()

        if previous_loaded_chunks != {} and previous_loaded_chunks != self.loaded_at_least_once:
            for chunk in self.loaded_at_least_once:
                if chunk not in previous_loaded_chunks:
                    self.extract_init(self.loaded_chunks[chunk])
        
        #[print(chunk.loc, end =", ") for chunk in self.loaded_chunks.values()] ; print()
        
    def chunks_grid_render(self, surf, offset=(0, 0)):
        # Dessiner la grille des chunks
        chunk_size = self.chunk_size ** 2 # Correction : Utiliser la taille du chunk directement
        width, height = surf.get_size()  # Taille de la surface de rendu
    
        # Couleur de la grille
        grid_color = (255, 255, 255)  # Blanc semi-transparent
    
        # Initialiser la police pour dessiner le texte
        pygame.font.init()  # Initialiser le module de police si ce n'est pas déjà fait
        font = pygame.font.Font(None, 24)  # Créer une police de taille 24
    
        # Dessiner les lignes verticales et les positions des chunks
        start_x = -(offset[0] % chunk_size)
        end_x = width + (chunk_size - (offset[0] % chunk_size))
        for x in range(start_x, end_x, chunk_size):
            pygame.draw.line(surf, grid_color, (x, 0), (x, height))
            for y in range(-(offset[1] % chunk_size), height + (chunk_size - (offset[1] % chunk_size)), chunk_size):
                # Calculer la position du chunk
                chunk_x = (x + offset[0]) // chunk_size
                chunk_y = (y + offset[1]) // chunk_size

                # Créer le texte de la position du chunk
                position_text = f"({chunk_x}, {chunk_y})"
                text_surface = font.render(position_text, True, (255, 255, 255))

                # Dessiner le texte dans le coin supérieur gauche du chunk
                surf.blit(text_surface, (x + 5, y + 5))  # Ajouter une petite marge
    
        # Dessiner les lignes horizontales
        start_y = -(offset[1] % chunk_size)
        end_y = height + (chunk_size - (offset[1] % chunk_size))
        for y in range(start_y, end_y, chunk_size):
            pygame.draw.line(surf, grid_color, (0, y), (width, y))
    
    def displayed_tiles_number_render(self, tiles_number, surf, offset=(0, 0)):
        font = pygame.font.Font(None, 35)
        text_render = font.render(f"Tiles : {tiles_number}", True, (255, 255, 255))
        surf.blit(text_render, (surf.get_width() - text_render.get_width()-10, 30))
    
    def tiles_render_init(self, surf, offset=(0, 0)):
        for chunk in self.loaded_chunks:
            self.loaded_chunks[chunk].tiles_render_init(surf, offset)

    
    def render(self, surf, offset=(0, 0)):
        all_sprites = pygame.sprite.LayeredUpdates()

        for chunk in self.loaded_chunks:
            tiles_sprite, entity_sprites = self.chunks[chunk].render(surf, offset)
            for tile in tiles_sprite:
                all_sprites.add(tile, layer=0)  # Ajoute les tuiles à la couche 0
            for entity in entity_sprites:
                all_sprites.add(entity, layer=1)  # Ajoute les entités à la couche 1

        all_sprites.draw(surf)

        
        if self.game.debug:
            pass #self.displayed_tiles_number_render(len(tiles_group), self.game.screen, offset)

