

class Particle:

    def __init__(self, game, p_type, pos, velocity=[0, 0], frame=0):
        self.game = game
        self.type = p_type
        self.pos = list(pos)
        self.velocity = list(velocity)
        self.animation = self.game.assets['particle/' + p_type].copy()
        self.animation.frame = frame

    def update(self):
        kill = False
        if self.animation.is_done:
            kill = True

        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]

        self.animation.update()
        return kill

    def render(self, surf, offset=(0, 0)):
        img = self.animation.img()
        adjusted_x = self.pos[0] - offset[0] - img.get_width() // 2
        adjusted_y = self.pos[1] - offset[1] - img.get_height() // 2

        if (adjusted_x + img.get_width() > 0 and adjusted_x < surf.get_width() and
            adjusted_y + img.get_height() > 0 and adjusted_y < surf.get_height()):
            surf.blit(img, (adjusted_x, adjusted_y))