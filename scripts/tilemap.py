import pygame
import json
import copy
import random
from scripts.particle import Particle

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
        
    def extract(self, id_pairs, keep=False):
        matches = []
        for tile in self.offgrid_tiles.copy():
            if (tile['type'], tile['variant']) in id_pairs:
                matches.append(tile.copy())
                if not keep:
                    self.offgrid_tiles.remove(tile)
        
        for loc in self.tilemap.copy():
            tile = self.tilemap[loc]
            if (tile['type'], tile['variant']) in id_pairs:
                matches.append(tile.copy())
                matches[-1]['pos'] = matches[-1]['pos'].copy()
                matches[-1]['pos'][0] *= self.tile_size
                matches[-1]['pos'][1] *= self.tile_size
                if not keep:
                    del self.tilemap[loc]

        return matches

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
            tile['pos'] = (tile['pos'][0] // self.tile_size, tile['pos'][1] // self.tile_size)
                
                
        total_tiles = list(self.tilemap.values()) + offgrid_tiles
        for tile in total_tiles:            
            chunk_coordinates = (tile['pos'][0] // self.chunk_size, tile['pos'][1] // self.chunk_size)
            chunk_loc = str(int(chunk_coordinates[0])) + ";" + str(int(chunk_coordinates[1]))
            if chunk_loc not in self.chunks_map:
                self.chunks_map[chunk_loc] = []
            self.chunks_map[chunk_loc].append(tile)
        
        return self.chunks_map
    
    '''    
    def chunk_mapping(self):
        self.chunks_map = {}
        offgrid_tiles = copy.deepcopy(self.offgrid_tiles)

        # Convertir les positions des tuiles offgrid en coordonnées de grille
        for tile in offgrid_tiles:
            tile['pos'] = (tile['pos'][0] // self.tile_size, tile['pos'][1] // self.tile_size)
                
        # Combiner toutes les tuiles
        total_tiles = list(self.tilemap.values()) + offgrid_tiles
        for tile in total_tiles:
            # Calculer les coordonnées du chunk pour chaque tuile
            chunk_coordinates = (tile['pos'][0] // self.chunk_size, tile['pos'][1] // self.chunk_size)
            chunk_loc = str(int(chunk_coordinates[0])) + ";" + str(int(chunk_coordinates[1]))
            
            # Si le chunk n'existe pas, créez un nouvel objet Chunk
            if chunk_loc not in self.chunks_map:
                self.chunks_map[chunk_loc] = Chunk( self.game, chunk_coordinates, self.chunk_size, self.tile_size)
            
            # Ajouter la tuile à l'objet Chunk correspondant
            self.chunks_map[chunk_loc].add_tile(tile['pos'], tile)
        
        return self.chunks_map
    '''

    def chunks_around(self, pos):
        chunks_around = {}
        chunk_loc = (pos[0] // self.tile_size // self.chunk_size, pos[1] // self.tile_size // self.chunk_size)
        for offset in NEIGHBORS_OFFSETS:
            check_loc = str(chunk_loc[0] + offset[0]) + ";" + str(chunk_loc[1] + offset[1])
            if check_loc in self.chunks_map:
                chunk = self.chunks_map[check_loc]
                if check_loc not in chunks_around:  # Vérifie si le chunk n'est pas déjà dans la liste
                    chunks_around[check_loc] = chunk
        return chunks_around


    def solid_check(self, pos):
        tile_loc = str(int(pos[0] // self.tile_size)) + ";" + str(int(pos[1] // self.tile_size))
        if tile_loc in self.tilemap:
            if self.tilemap[tile_loc]['type'] in PHYSICS_TILES:
                return self.tilemap[tile_loc]
            
    def tiles_around(self, pos):
        tiles = []
        tiles_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        for offset in NEIGHBORS_OFFSETS:
            check_loc = str(tiles_loc[0] + offset[0]) + ";" + str(tiles_loc[1] + offset[1])
            if check_loc in self.tilemap:
                tiles.append(self.tilemap[check_loc])
        return tiles 

    def physics_rects_around(self, pos):
        rects = []
        
        for tile in self.tiles_around(pos):
            if tile['type'] in PHYSICS_TILES:
                rects.append(pygame.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size))

        return rects
    
    def render(self, surf, offset=(0, 0)):
                
        for tile in self.offgrid_tiles:
            surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1]))
            
        for x in range(offset[0] // self.tile_size, (offset[0] + surf.get_width()) // self.tile_size + 1):
            for y in range(offset[1] // self.tile_size, (offset[1] + surf.get_height()) // self.tile_size + 1):
                loc = str(x) + ';' + str(y)
                if loc in self.tilemap:
                    tile = self.tilemap[loc]
                    surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))
    
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


class Chunk:
    
    def __init__(self, game, loc, tiles, entities_list = [], size=16):
        self.game = game
        self.size = size
        self.tiles = tiles
        self.entities = entities_list
        self.leaf_spawners = []
        self.loc = loc
    
    
    def get_loc(self):
        return self.loc

    
    def add_tile(self, loc, tile):
        tile_loc = str(loc[0]) + ";" + str(loc[1])
        if tile_loc not in self.tiles:
            self.tiles[tile_loc] = tile
    
    def add_entity(self, entity):
        if entity not in self.entities:
            self.entities.append(entity)
    
    def add_leaf_spawners(self, leaf_spawners):
        if leaf_spawners not in self.leaf_spawners:
            self.leaf_spawners.append(leaf_spawners)
    
    def clear_entity(self):
        self.entities = []
    
    def update(self):
        for entity in self.entities:
            entity.update(self.game.tilemap)
            
        for rect in self.leaf_spawners:
            if random.random() * 49999 < rect.width * rect.height:
                pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                self.particles.append(Particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20)))
        
    
    def render(self, surf, offset=(0, 0)):
        for tile in self.tiles:
            surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tilemap.tile_size - offset[0], tile['pos'][1] * self.tilemap.tile_size - offset[1]))
        
        for entity in self.entities:
            entity.render(surf, offset)

    def __str__(self) -> str:
        return f"chunk : {self.loc} | tiles: {len(self.tiles)} | entities: {len(self.entities)}"
    
class ChunksManager:
    
    def __init__(self, game, tilemap, chunk_size=16):
        self.game = game
        self.player = self.game.player
        self.tilemap = tilemap
        self.chunk_size = chunk_size
        self.chunks = {}
        self.loaded_chunks = self.chunks_around()
        self.player_chunk = self.get_chunk(self.player.rect().center)
    
    def set_chunks(self, chunks):
        for chunk in chunks.copy():
            self.chunks[chunk]= Chunk(self.game, chunk, chunks[chunk])
        self.load_chunks()
    
    def add_entity(self, entity):
        entity_chunk = self.get_chunk(entity.rect().center)
        if entity_chunk:
            entity_chunk.add_entity(entity)
    
    def add_leaf_spawners(self, leaf_spawners):
        leaf_spawners_chunk = self.get_chunk(leaf_spawners.rect().center)
        if leaf_spawners_chunk:
            leaf_spawners_chunk.add_leaf_spawners(leaf_spawners)
    
    def clear_entity(self):
        for chunk in self.chunks:
            self.chunks[chunk].clear_entity()
            
    def add_chunk(self, chunk):
        self.chunks[chunk.get_loc()] = chunk

    def get_chunk(self, pos):
        chunk_loc = str(pos[0] // self.tilemap.tile_size //self.chunk_size) + ";" + str(pos[1]// self.tilemap.tile_size //self.chunk_size)
        if chunk_loc in self.chunks:
            return self.chunks[chunk_loc]
    
    def chunks_around(self):
        pos = self.player.rect().center
        chunks_around = {}
        tile_size = self.tilemap.tile_size
        chunk_loc = (pos[0] // tile_size // self.chunk_size, pos[1] // tile_size // self.chunk_size)
        for offset in NEIGHBORS_OFFSETS:
            check_loc = str(chunk_loc[0] + offset[0]) + ";" + str(chunk_loc[1] + offset[1])
            if check_loc in self.chunks:
                chunk = self.chunks[check_loc]
                if check_loc not in chunks_around:  # Vérifie si le chunk n'est pas déjà dans la liste
                    chunks_around[check_loc] = chunk
        return chunks_around
    
    def load_chunks(self):
        current_player_chunk = self.get_chunk(self.player.rect().center)
        if current_player_chunk != self.player_chunk:
            self.player_chunk = current_player_chunk
            self.loaded_chunks = self.chunks_around()
    
    def update(self):
        self.load_chunks()
        for chunk in self.loaded_chunks:
            print(self.loaded_chunks[chunk])
            self.loaded_chunks[chunk].update()
            
    def render(self, surf, offset=(0, 0)):
        for chunk in self.chunks:
            chunk.render(surf, offset)