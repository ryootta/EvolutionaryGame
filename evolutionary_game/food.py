import pyxel

class Food:
    def __init__(self, x, y, energy=5):
        self.x = x
        self.y = y
        self.energy = energy  # 初期エネルギー（hp的な役割に）
        self.lifetime = 100
        self.alive = True

    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.alive = False

    def draw(self):
        pyxel.circ(self.x, self.y, 1, 6)