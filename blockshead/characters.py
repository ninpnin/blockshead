import pygame
import random
import numpy as np
from .physics import check_collision
from .objects import Direction
from .objects import Pistol, Blood, Uzi, Shotgun, DevilAttack, Healthbox, Fakewall
import math
import logging

class Blockshead(object):
    def __init__(self, game_config):
        self.images = {}
        self.images[Direction.UP] = pygame.image.load("images/blockshead/bhup.png")
        self.images[Direction.DOWN] = pygame.image.load("images/blockshead/bhdown.png")
        self.images[Direction.LEFT] = pygame.image.load("images/blockshead/bhleft.png")
        self.images[Direction.RIGHT] = pygame.image.load("images/blockshead/bhright.png")
        self.width = 70
        self.height = self.width
        
        self.x = random.randrange(self.width, game_config.width - self.width)
        self.y = random.randrange(self.height, game_config.height - self.height)
        self.direction = Direction.UP
        self.x_vel = 0
        self.y_vel = 0
        self.health = game_config.max_health # +5 health is added at the beginning of every level
        self.weapon = "pistol"
        self.ammo_dict = {"pistol": "Infinite"}
        self.pause = False
        self.bonus_score = 0
        self.pistol_range = 150 # the range of the pistol in pixels
        self.mine_count = 0 # how many mines are left
        self.bullet_images = []
        self.cooldown = 0
        self.speed = game_config.blockshead_speed
    
    def ammo(self):
        return self.ammo_dict.get(self.weapon, 0)
    
    def get_image(self):            
        return self.images[self.direction]

    def _check_collisions(self, game_state):
        for zombie in game_state.zombies + game_state.fakewalls:
            if check_collision(self, zombie):
                return True
        return False

    def move(self, game_config, game_state):
        # game area boundaries
        if (self.x >= game_config.width) and self.x_vel > 0:
            self.x_vel = 0
        elif self.x <= 0 and self.x_vel < 0:
            self.x_vel = 0

        if (self.y >= game_config.height) and self.y_vel > 0:
            self.y_vel = 0
        elif self.y <= 0 and self.y_vel < 0:
            self.y_vel = 0

        speed = math.sqrt(self.x_vel ** 2 + self.y_vel ** 2)
        if speed < 1.0:
            speed = 1.0
        speed = self.speed / speed
        next_x = self.x + self.x_vel * speed
        next_y = self.y + self.y_vel * speed
        
        old_x, old_y = self.x, self.y
        self.x = next_x
        self.y = next_y
        if self._check_collisions(game_state):
            self.x, self.y = old_x, old_y

        self.cooldown = max(0, self.cooldown - 1)

    def get_coordinates(self):
        return int(self.x), int(self.y)
    
    def fire_gun(self, window, game_config, game_state):
        """Fires whichever weapon that blockshead is using at the moment"""
        self.bonus_score = 0
        if self.cooldown == 0:
            shot = None
            if self.weapon == "pistol":
                shot = Pistol(game_config, game_state)
                self.cooldown = 30
            elif self.ammo() > 0:
                if self.weapon == "uzi":
                    shot = Uzi(game_config, game_state)
                    self.cooldown = 12
                    self.ammo_dict["uzi"] = max(0, self.ammo() - 1)
                elif self.weapon == "shotgun":
                    shot = Shotgun(window, game_state)
                    self.ammo_dict["shotgun"] = max(0, self.ammo() - 1)
                    self.cooldown = 45
                elif self.weapon == "fireball":
                    #shot = Fireball(window, game_config, game_state)
                    self.cooldown = 45
                elif self.weapon == "fake walls":
                    xvel, yvel = self.direction.value
                    coords = self.x - xvel * self.width + 1, self.y - yvel * (self.height+10) + 1
                    wall = Fakewall(game_config, init_coords=coords)
                    collisions = False
                    for zombie in game_state.zombies + game_state.devils + game_state.fakewalls:
                        if check_collision(wall, zombie):
                            collisions = True
                    if not collisions:
                        logging.info("fakewall added")
                        game_state.fakewalls.append(wall)
                        self.ammo_dict["fake walls"] = max(0, self.ammo() - 1)
                        self.cooldown = 15
                    else:    
                        logging.debug("fakewall not possible here")
                
                # Automatically change to pistol if out of ammo
                if self.ammo() == 0:
                    self.weapon = "pistol"
            else:
                logging.info("Out of ammo")

            return shot

    def injure(self, damage, game_state):
        self.health -= damage

class Zombie(object):
    def __init__(self, window, game_config, init_coords=None):
        self.direction = Direction.UP
        self.images = {}
        for direction in Direction:
            # 8 different devil images
            self.images[direction] = pygame.image.load(f"images/zombies/z{direction.name.lower()}.png")

        # pick a random starting point on the right side of the field. Zombies start on the left half.
        self.radius = 35
        self.width = 2 * self.radius
        self.height = 2 * self.radius

        if init_coords is None:
            self.x = random.randrange(self.radius, game_config.width // 20)
            self.y = random.randrange(self.radius, game_config.height - self.radius)
        else:
            self.x, self.y = init_coords
        
        # Rolling average location
        self.x_average, self.y_average = self.x, self.y

        self.speed = game_config.zombie_speed
        self.health = 50
        self.cooldown = 0
        self.injury_cooldown = 0
        self.multiplier = 0.5
        self.angles = [0, 45, -45, 90, -90]

        # Randomize movement on enemy level
        if random.choice([True, False, False]):
            self.angles = [20] + self.angles
        elif random.choice([True, False]):
            self.angles = [-20] + self.angles
    
    def _check_collisions(self, game_state, game_config=None):
        if game_config is not None:
            if self.x >= game_config.width or self.x < 0:
                return True
            if self.y >= game_config.height or self.y < 0:
                return True

        for zombie in game_state.zombies + game_state.devils + game_state.fakewalls + [game_state.blockshead]:
            if zombie is self:
                continue
            if check_collision(self, zombie):
                return True
        return False

    def move(self, window, game_config, game_state):
        target = game_state.blockshead
        
        self.x_average = self.x_average * 0.9 + self.x * 0.1
        self.y_average = self.y_average * 0.9 + self.y * 0.1
        self.stuck = math.sqrt((self.x_average -self.x) ** 2 + (self.y_average - self.y) ** 2) <= 3
        if self.cooldown > 0:
            self.cooldown -= 1
            return
        if self.injury_cooldown > 0:
            self.injury_cooldown -= 1
            return

        diff = np.array([self.x - target.x, self.y - target.y])
        diff = diff / np.linalg.norm(diff) * self.speed
        
        dotprod, best_diff = -100.0, Direction.UP.value
        for d in Direction:
            d_val = d.value / np.linalg.norm(d.value)
            matching = np.dot(d_val, diff)
            if matching >= dotprod:
                dotprod = matching
                best_diff = d_val
                
        diff = best_diff * self.speed
        
        old_x, old_y = self.x, self.y
        for angle in self.angles:
            theta = np.radians(angle)
            c, s = np.cos(theta), np.sin(theta)
            R = np.array(((c, -s), (s, c)))
            direction = R @ diff
            next_x = self.x - direction[0]
            next_y = self.y - direction[1]

            self.x = next_x
            self.y = next_y
            collisions = self._check_collisions(game_state, game_config)
            if collisions:
                self.x, self.y = old_x, old_y
            else:
                # Calculate which direction is the best aligned with where the zombie ends up going
                dirs = [(d_prime, d_prime.value / np.linalg.norm(d_prime.value)) for d_prime in Direction]
                dirs_dots = [(d_prime, np.dot(-direction, d_prime_val)) for d_prime, d_prime_val in dirs]
                self.direction = max(dirs_dots, key=lambda t: t[1])[0]

                # Exit loop if no collisions are found
                break
                    
        # Cooldown period for shooting
        if self.cooldown > 0:
            self.cooldown -= 1
        if self.injury_cooldown > 0:
            self.injury_cooldown -= 1

    def get_coordinates(self):
        return int(self.x), int(self.y)

    def get_image(self):            
        return self.images[self.direction]

    def contact(self, game_state):
        bh = game_state.blockshead
        # Only attack walls if they are directly in the way of blockshead
        bh_diff = np.array([bh.x - self.x, bh.y - self.y])
        bh_diff = bh_diff / np.linalg.norm(bh_diff)
        
        targets = [game_state.blockshead]
        if self.stuck:
            targets += game_state.fakewalls
        for target in targets:
            target_diff = np.array([target.x - self.x, target.y - self.y])
            target_diff = target_diff / np.linalg.norm(target_diff)
            cosine = np.dot(target_diff, bh_diff)
            
            # Note that the cosine is always 1.0 if target == blockshead
            if not cosine >= 0.95:
                continue

            horizontal = abs(target.x - self.x) < target.width // 2 + self.radius + 2
            vertical = abs(target.y - self.y) < target.height // 2 + self.radius + 2
            
            if horizontal and vertical and self.cooldown == 0:
                target.injure(1, game_state)
                self.cooldown = 20
                break
    
    def injure(self, damage, game_state, direction=None):
        self.health -= damage
        self.injury_cooldown = 11
        if direction is not None:
            old_x, old_y = self.x, self.y
            self.x += direction.value[0] * 5
            self.y += direction.value[1] * 5
            collisions = self._check_collisions(game_state)
            if collisions:
                self.x, self.y = old_x, old_y

        if self.health <= 1:
            blood_mark = Blood(self.x, self.y)
            game_state.blood_marks.append(blood_mark)
            game_state.score += int(5 * game_state.multiplier)
            game_state.multiplier += self.multiplier

class Devil(object):
    def __init__(self, window, game_config):
        self.direction = Direction.UP
        self.images = {}
        for direction in Direction:
            # 8 different devil images
            self.images[direction] = pygame.image.load(f"images/devils/d{direction.name.lower()}.png")

        # pick a random starting point on the right side of the field. Zombies start on the left half.
        self.radius = 35
        self.width = 2 * self.radius
        self.height = 2 * self.radius
        
        self.x = random.randrange(self.radius, game_config.width // 4)
        self.y = random.randrange(self.radius, game_config.height - self.radius)
        self.x_average = self.x
        self.y_average = self.y
        
        self.speed = game_config.devil_speed
        self.health = 150
        self.cooldown = 0
        self.injury_cooldown = 0
        self.multiplier = 0.5
        self.angles = [0, 30, -30, 60, -60, 90, -90, 110, -110, 130, -130]

        # Randomize movement on enemy level
        if random.choice([True, False, False]):
            self.angles = [20] + self.angles
        elif random.choice([True, False]):
            self.angles = [-20] + self.angles
    
    def _check_collisions(self, game_state, game_config=None):
        if game_config is not None:
            if self.x >= game_config.width or self.x < 0:
                return True
            if self.y >= game_config.height or self.y < 0:
                return True

        for zombie in game_state.zombies + game_state.devils + game_state.fakewalls + [game_state.blockshead]:
            if zombie is self:
                continue
            if check_collision(self, zombie):
                return True
        return False

    def move(self, window, game_config, game_state):
        target = game_state.blockshead
        if self.cooldown > 0:
            self.cooldown -= 1
        if self.injury_cooldown > 0:
            self.injury_cooldown -= 1
            return

        diff = np.array([self.x - target.x, self.y - target.y])
        diff = diff / np.linalg.norm(diff) * self.speed
        
        old_x, old_y = self.x, self.y
        for angle in self.angles:
            theta = np.radians(angle)
            c, s = np.cos(theta), np.sin(theta)
            R = np.array(((c, -s), (s, c)))
            direction = R @ diff
            self.x = self.x - direction[0]
            self.y = self.y - direction[1]

            collisions = self._check_collisions(game_state, game_config)
            if collisions:
                self.x, self.y = old_x, old_y
            else:
                break
                    
        # Cooldown period for shooting
        if self.cooldown > 0:
            self.cooldown -= 1
        if self.injury_cooldown > 0:
            self.injury_cooldown -= 1
            
        self.x_average = self.x_average * 0.9 + self.x * 0.1
        self.y_average = self.y_average * 0.9 + self.y * 0.1

    def get_coordinates(self):
        return int(self.x), int(self.y)

    def get_image(self):            
        return self.images[self.direction]

    def contact(self, game_state):
        target = game_state.blockshead
        horizontal = abs(target.x - self.x) < target.width // 2 + self.radius + 2
        vertical = abs(target.y - self.y) < target.height // 2 + self.radius + 2
        if horizontal and vertical and self.cooldown == 0 and self.injury_cooldown == 0:
            target.injure(1, game_state)
            self.cooldown = 20
        elif self.cooldown == 0 and self.injury_cooldown == 0:
            logging.debug("Devil attack")
            attack = DevilAttack(self, game_state)
            game_state.shots.append(attack)
            self.cooldown = 300
            self.injury_cooldown = 70
    
    def injure(self, damage, game_state, direction=None):
        self.health -= damage
        self.injury_cooldown = 11
        if direction is not None:
            old_x, old_y = self.x, self.y
            self.x += direction.value[0] * 5
            self.y += direction.value[1] * 5
            collisions = self._check_collisions(game_state)
            if collisions:
                self.x, self.y = old_x, old_y

        if self.health <= 1:
            blood_mark = Blood(self.x, self.y)
            healthbox = Healthbox(game_state, self.x, self.y)
            game_state.blood_marks.append(blood_mark)
            game_state.healthboxes.append(healthbox)
            game_state.score += int(5 * game_state.multiplier)
            game_state.multiplier += self.multiplier
