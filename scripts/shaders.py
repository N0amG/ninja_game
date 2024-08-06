import pygame
import moderngl
from array import array

# Initialiser Pygame et créer une fenêtre
pygame.init()
window = pygame.display.set_mode((800, 600), pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE)

display = pygame.Surface(window.get_size())

clock = pygame.time.Clock()

# Charger et redimensionner l'image
img = pygame.transform.scale(pygame.image.load("data/images/background.png").convert(), (400, 300))
img_rect = img.get_rect()

ctx = moderngl.create_context()

quad_buffer = ctx.buffer(data = array('f', [
    -1.0, 1.0, 0.0, 0.0, # topleft
    1.0, 1.0, 1.0, 0.0, # topright
    -1.0, -1.0, 0.0, 1.0, # bottomleft
    1.0, -1.0, 1.0, 1.0, # bottomright
]))

vert_shader = '''
#version 330

in vec2 vert;
in vec2 texcoord;
out vec2 uvs;

void main() {
    uvs = texcoord;
    gl_Position = vec4(vert, 0.0, 1.0);
}
'''

frag_shader = '''
#version 330

uniform sampler2D texture;

in vec2 uvs;
out vec4 fragColor;

void main() {
    fragColor = vec4(texture(texture, uvs).rgb, 1.0);
}
'''

program = ctx.program(vertex_shader=vert_shader, fragment_shader=frag_shader)
render_object = ctx.vertex_array(program, [(quad_buffer, '2f 2f', 'vert', 'texcoord')])

def surface_to_texture(ctx, surface):
    texture = ctx.texture(surface.get_size(), 4)
    texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
    texture.swizzle = 'BGRA'
    texture.write(surface.get_view('1'))
    return texture

# Boucle principale
running = True
t = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    t += 1
    # Obtenir la position de la souris
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Mettre à jour la position de l'image
    img_rect.center = (mouse_x, mouse_y)

    # Dessiner l'image
    display.fill((0, 0, 0))  # Effacer l'écran
    display.blit(img, img_rect)
    
    frame_texture = surface_to_texture(ctx, display)
    frame_texture.use(0)
    program['texture'] = 0
    render_object.render(mode = moderngl.TRIANGLE_STRIP)

    # Mettre à jour l'affichageS
    pygame.display.flip()

    frame_texture.release()
    clock.tick(60)
# Fermer Pygame
pygame.quit()
