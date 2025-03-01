import pyxel
import random
from creature import Creature
from food import Food
from creature_data import CreatureData

class Game:
    def __init__(self):
        pyxel.init(256, 256, title="Food Chain Evolution")
        self.creatures = [Creature(random.randint(0, 256), random.randint(0, 256)) for _ in range(10)]
        self.foods = []
        self.difficulty = 1.0  # 難易度係数（1.0が標準）
        self.adjust_timer = 600  # 難易度調整間隔（10秒）
        pyxel.run(self.update, self.draw)

    def adjust_difficulty(self):
        """AIによる難易度調整"""
        apex_count = sum(1 for c in self.creatures if c.level == 3 and c.alive)
        total_count = len(self.creatures)

        # 難易度計算（レベル3と生物数で調整）
        difficulty_score = (apex_count * 0.5) + (total_count / 20)  # レベル3=0.5、20匹=1.0
        self.difficulty = max(0.5, min(2.0, difficulty_score))  # 0.5〜2.0に制限

        # パラメータ調整
        for c in self.creatures:
            if c.level > 0:  # 生産者以外
                c.stats["attack_power"] = CreatureData.get(c.level, "attack_power") * self.difficulty
                c.stats["evolution_chance"] = CreatureData.get(c.level, "evolution_chance") * self.difficulty
                c.stats["reproduction_chance"] = CreatureData.get(c.level, "reproduction_chance") * (1 / self.difficulty)
            c.stats["hp"] = CreatureData.get(c.level, "hp") * (1 / self.difficulty)

    def update(self):
        self.adjust_timer -= 1
        if self.adjust_timer <= 0:
            self.adjust_difficulty()
            self.adjust_timer = 600  # 10秒ごとにリセット

        for c in self.creatures[:]:
            c.update(self.creatures, self.foods)
            if not c.alive:
                self.foods.append(Food(c.x, c.y, energy=5 + c.level * 2))
                self.creatures.remove(c)
        for f in self.foods[:]:
            f.update()
            if not f.alive:
                self.foods.remove(f)
        
        producer_count = sum(1 for c in self.creatures if c.level == 0 and c.alive)
        spawn_chance = CreatureData.get(0, "spawn_chance") * (1 / self.difficulty)
        max_population = CreatureData.get(0, "max_population")
        if producer_count < max_population and random.random() < spawn_chance:
            self.creatures.append(Creature(random.randint(0, 256), random.randint(0, 256)))

    def draw(self):
        pyxel.cls(7)
        for f in self.foods:
            f.draw()
        for c in self.creatures:
            c.draw()
        pyxel.text(10, 10, f"Difficulty: {self.difficulty:.2f}", 0)
        pyxel.text(10, 20, f"Creatures: {len(self.creatures)}", 0)
        pyxel.text(10, 30, f"Apex: {sum(1 for c in self.creatures if c.level == 3)}", 0)

if __name__ == "__main__":
    Game()