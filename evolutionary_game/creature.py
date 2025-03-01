import pyxel
import random
import math
from creature_data import CreatureData

class Creature:
    def __init__(self, x, y, level=0):
        self.x = x
        self.y = y
        self.level = level
        self.energy = 0
        self.stats = {k: CreatureData.get(level, k) for k in CreatureData.BASE_DATA[level]}
        self.alive = True
        self.vx = 0
        self.vy = 0
        self.reproduction_cooldown = 0

    def attack(self, target, damage):
        target.stats["hp"] -= damage
        if target.stats["hp"] <= 0:
            target.alive = False
            return True
        return False

    def update(self, creatures, foods):
        self.stats["lifetime"] -= 1
        if self.stats["lifetime"] <= 0:
            self.alive = False
            return

        if self.reproduction_cooldown > 0:
            self.reproduction_cooldown -= 1

        # 動き
        speed = self.stats["speed"]
        detection_range = self.stats["detection_range"]
        attack_power = self.stats["attack_power"]
        if self.level == 0:
            pass
        else:
            target_level = self.level - 1 if self.level > 0 else 0
            targets = ([c for c in creatures if c.level == target_level and c.alive] + 
                       [f for f in foods if f.alive])
            target = min(targets, key=lambda t: self.distance(t), default=None) if targets else None
            if target:
                angle = math.atan2(target.y - self.y, target.x - self.x)
                self.vx = math.cos(angle) * speed
                self.vy = math.sin(angle) * speed
            else:
                self.vx = random.uniform(-speed, speed)
                self.vy = random.uniform(-speed, speed)

        self.x += self.vx
        self.y += self.vy
        if self.x < 0 or self.x > 256: self.vx = -self.vx; self.x = max(0, min(256, self.x))
        if self.y < 0 or self.y > 256: self.vy = -self.vy; self.y = max(0, min(256, self.y))

        # 攻撃処理
        energy_per_food = self.stats["energy_per_food"]
        hunger_threshold = self.stats["hunger_threshold"]
        if self.level == 0:
            self.energy += energy_per_food
            for f in foods:
                if self.distance(f) < detection_range and f.alive:
                    self.energy += f.energy
                    f.alive = False
        else:
            ate_something = False
            for c in creatures:
                if (c.level == self.level - 1 and self.distance(c) < detection_range and c.alive):
                    if self.attack(c, attack_power):
                        self.energy += energy_per_food
                    ate_something = True
                    break
            for f in foods:
                if self.distance(f) < detection_range and f.alive:
                    if attack_power > 0:
                        f.energy -= attack_power
                        if f.energy <= 0:
                            f.alive = False
                            self.energy += energy_per_food
                    else:
                        self.energy += f.energy
                        f.alive = False
                    ate_something = True
                    break
            if not ate_something and self.energy < hunger_threshold:
                for c in creatures:
                    if (c.level == self.level and c != self and 
                        self.distance(c) < detection_range and c.alive):
                        if self.attack(c, attack_power):
                            self.energy += energy_per_food // 2
                        break
            nearby_allies = [c for c in creatures if c.level == self.level - 1 and 
                            self.distance(c) < detection_range and c.alive]
            if nearby_allies:
                total_damage = sum(CreatureData.get(c.level, "attack_power") for c in nearby_allies)
                if self.attack(self, total_damage):
                    pass

        # 進化（ランダム強化）
        evolution_energy = self.stats["evolution_energy"]
        evolution_chance = self.stats["evolution_chance"]
        random_evolution_chance = self.stats["random_evolution_chance"]
        if self.alive and ((self.energy >= evolution_energy and random.random() < evolution_chance) or 
            (random.random() < random_evolution_chance)):
            if self.level < 3:
                self.level += 1
                self.energy = 0
                self.stats = {k: CreatureData.get(self.level, k) for k in CreatureData.BASE_DATA[self.level]}
                options = ["attack_power", "hp", "speed", "detection_range", "lifetime"]
                chosen_stat = random.choice(options)
                self.stats[chosen_stat] *= 1.2

        # 繁殖
        if self.level > 0 and self.reproduction_cooldown == 0 and self.alive:
            reproduction_energy = self.stats["reproduction_energy"]
            reproduction_chance = self.stats["reproduction_chance"]
            if self.energy >= reproduction_energy and random.random() < reproduction_chance:
                self.energy -= reproduction_energy // 2
                self.reproduction_cooldown = self.stats["reproduction_cooldown"]
                creatures.append(Creature(self.x + random.randint(-5, 5), 
                                        self.y + random.randint(-5, 5), 
                                        self.level))

    def draw(self):
        if self.level == 0:
            pyxel.circ(self.x, self.y, 2, 11)  
        elif self.level == 1:
            pyxel.tri(self.x, self.y, self.x+3, self.y-4, self.x+6, self.y, 12)  
        elif self.level == 2:
            pyxel.rect(self.x, self.y, 4, 4, 8)  
        elif self.level == 3:
            pyxel.circ(self.x, self.y, 4, 14)   

    def distance(self, other):
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5