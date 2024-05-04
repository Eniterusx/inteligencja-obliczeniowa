# Simple pygame code!
import pygame
from enum import Enum
import random

PIXEL_SIZE = 6
BLOCK_SIZE = PIXEL_SIZE*6
BULLET_SIZE = PIXEL_SIZE*2
from PIL import Image

pygame.init()

MAP_SIZE_X = 0
MAP_SIZE_Y = 0

class Direction(Enum):
    UP = (0, -PIXEL_SIZE)
    DOWN = (0, PIXEL_SIZE)
    LEFT = (-PIXEL_SIZE, 0)
    RIGHT = (PIXEL_SIZE, 0)

class Utils:
    def init_map(map_name):
        # open txt file with map
        # read character by character, if the character is "#" then create an obstacle, if it is "-" then do nothing, if it is "1" then create a tank 1, if it is "2" then create a tank 2, if it is "\n" then go to the next line
        # return the list of obstacles

        with open(map_name, 'r') as file:
            global MAP_SIZE_X
            global MAP_SIZE_Y
            MAP_SIZE_X = (len(file.readline())-1) * BLOCK_SIZE
            MAP_SIZE_Y = (sum(1 for line in file)+2) * BLOCK_SIZE
            file.seek(0)
            map = []
            tank2 = None
            spawners = []
            for y, line in enumerate(file):
                for x, char in enumerate(line):
                    if char == '#':
                        map.append(Obstacle(x * BLOCK_SIZE, y * BLOCK_SIZE))
                    elif char == '@':
                        map.append(Obstacle(x * BLOCK_SIZE, y * BLOCK_SIZE, shootable=True, color=(0, 0, 255)))
                    elif char == '*':
                        map.append(Obstacle(x * BLOCK_SIZE, y * BLOCK_SIZE, destructible=True, color=(128, 0, 128)))
                    elif char == '1':
                        tank1 = Tank(x * BLOCK_SIZE//PIXEL_SIZE, y * BLOCK_SIZE//PIXEL_SIZE, (255, 0, 0))
                    elif char == '2':
                        tank2 = Tank(x * BLOCK_SIZE//PIXEL_SIZE, y * BLOCK_SIZE//PIXEL_SIZE, (0, 255, 0))
                    elif char == '3':
                        spawners += [TankBotSpawner(x * BLOCK_SIZE, y * BLOCK_SIZE, (0, 255, 0))]
        if tank2 is None:
            return map, tank1, spawners
        return map, tank1, tank2            

    def draw_hp(screen, tank1, tank2, game_state):
        font = pygame.font.Font(None, 36)

        text_surface_tank1 = font.render(f'Tank 1 HP: {tank1.health}', True, (0, 255, 0))
        text_rect_tank1 = text_surface_tank1.get_rect()
        text_rect_tank1.bottomleft = (PIXEL_SIZE*2, MAP_SIZE_Y-PIXEL_SIZE)
        screen.blit(text_surface_tank1, text_rect_tank1)

        if tank2 is not None:
            text_surface_tank2 = font.render(f'Tank 2 HP: {tank2.health}', True, (0, 255, 0))
            text_rect_tank2 = text_surface_tank2.get_rect()
            text_rect_tank2.bottomright = (MAP_SIZE_X-PIXEL_SIZE*2, MAP_SIZE_Y-PIXEL_SIZE)
            screen.blit(text_surface_tank2, text_rect_tank2) 
        else:
            text_surface_points = font.render(f'Points: {game_state.points}', True, (0, 255, 0))
            text_rect_points = text_surface_points.get_rect()
            text_rect_points.bottomright = (MAP_SIZE_X-PIXEL_SIZE*2, MAP_SIZE_Y-PIXEL_SIZE)
            screen.blit(text_surface_points, text_rect_points)
            

    def check_collision(object1, object2):
        return object1.rect.colliderect(object2.rect)
    
    def check_nearby_objects(tank, objects):
        rect_up = pygame.Rect(tank.x, tank.y - PIXEL_SIZE, BLOCK_SIZE, BLOCK_SIZE)
        rect_down = pygame.Rect(tank.x, tank.y + PIXEL_SIZE, BLOCK_SIZE, BLOCK_SIZE)
        rect_left = pygame.Rect(tank.x - PIXEL_SIZE, tank.y, BLOCK_SIZE, BLOCK_SIZE)
        rect_right = pygame.Rect(tank.x + PIXEL_SIZE, tank.y, BLOCK_SIZE, BLOCK_SIZE)

        nearby_objects = [0, 0, 0, 0]
        for object in objects:
            if rect_up.colliderect(object.rect):
                nearby_objects[0] = 1
            if rect_down.colliderect(object.rect):
                nearby_objects[1] = 1
            if rect_left.colliderect(object.rect):
                nearby_objects[2] = 1
            if rect_right.colliderect(object.rect):
                nearby_objects[3] = 1
        return nearby_objects
    
    def check_nearby_bullets(tank, bullets):
        rect_up = pygame.Rect(tank.x, tank.y - BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
        rect_2_up = pygame.Rect(tank.x, tank.y - 2*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
        rect_down = pygame.Rect(tank.x, tank.y + BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
        rect_2_down = pygame.Rect(tank.x, tank.y + 2*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
        rect_left = pygame.Rect(tank.x - BLOCK_SIZE, tank.y, BLOCK_SIZE, BLOCK_SIZE)
        rect_2_left = pygame.Rect(tank.x - 2*BLOCK_SIZE, tank.y, BLOCK_SIZE, BLOCK_SIZE)
        rect_right = pygame.Rect(tank.x + BLOCK_SIZE, tank.y, BLOCK_SIZE, BLOCK_SIZE)
        rect_2_right = pygame.Rect(tank.x + 2*BLOCK_SIZE, tank.y, BLOCK_SIZE, BLOCK_SIZE)

        nearby_bullets = [0, 0, 0, 0]
        for bullet in bullets:
            if rect_up.colliderect(bullet.rect) or rect_2_up.colliderect(bullet.rect):
                nearby_bullets[0] = 1
            if rect_down.colliderect(bullet.rect) or rect_2_down.colliderect(bullet.rect):
                nearby_bullets[1] = 1
            if rect_left.colliderect(bullet.rect) or rect_2_left.colliderect(bullet.rect):
                nearby_bullets[2] = 1
            if rect_right.colliderect(bullet.rect) or rect_2_right.colliderect(bullet.rect):
                nearby_bullets[3] = 1
        return nearby_bullets

    def get_distance(object1, object2):
        return ((object1.x - object2.x)**2 + (object1.y - object2.y)**2)**0.5

class State:
    def __init__(self, tank1, init_map, tank2=None, spawners=[]):
        self.tank1 = tank1
        self.tank2 = tank2
        self.bullets = []
        self.map = init_map
        self.spawners = spawners
        self.spawn_cooldown = 60
        self.tank_bots = [self.spawn_bot_on_start()]
        self.points = 0
        self.max_enemies = 5

    def spawn_bot_on_start(self):
        spawner = random.choice(self.spawners)
        return spawner.spawn()

    def draw(self, screen, game_state):         
        screen.fill((80, 80, 80))
        self.tank1.draw(screen)
        if self.tank2 is not None:
            self.tank2.draw(screen)
        else:
            # for spawner in self.spawners:
                # spawner.draw(screen)
            for tank_bot in self.tank_bots:
                tank_bot.draw(screen)
        for obstacle in self.map:
            obstacle.draw(screen)
        
        for bullet in self.bullets:
            bullet.draw(screen)
        Utils.draw_hp(screen, self.tank1, self.tank2, game_state)

    def game_tick(self, game_state):
        points = 0
        took_damage = False
        if self.tank2 is None:
            for tank_bot in self.tank_bots:
                if tank_bot.health == 0:
                    self.tank_bots.remove(tank_bot)
                    self.points += 1
                    points += 1
                    continue
                tank_bot.move(game_state)
                tank_bot.shoot(game_state)
                tank_bot.decrease_cooldown()
        for bullet in self.bullets:
            bullet.move()
            for obstacle in self.map:
                if obstacle.shootable:
                    continue
                if Utils.check_collision(bullet, obstacle):
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    if obstacle.destructible:
                        obstacle.hp -= 1
                        if obstacle.hp == 0:
                            self.map.remove(obstacle)
                    break
            if Utils.check_collision(bullet, self.tank1):
                self.tank1.health -= 1
                if bullet in self.bullets:
                    self.bullets.remove(bullet)
                    took_damage = True
            if self.tank2 is not None:
                if Utils.check_collision(bullet, self.tank2):
                    self.tank2.health -= 1
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
            else:
                if not bullet.is_from_bot:
                    for tank_bot in self.tank_bots:
                        if Utils.check_collision(bullet, tank_bot):
                            tank_bot.health -= 1
                            if bullet in self.bullets:
                                self.bullets.remove(bullet)
                            break
        for bullet1 in self.bullets:
            for bullet2 in self.bullets:
                if bullet1 == bullet2:
                    continue
                if Utils.check_collision(bullet1, bullet2):
                    self.bullets.remove(bullet1)
                    self.bullets.remove(bullet2)
        self.bullets = [bullet for bullet in self.bullets if 0 <= bullet.x <= MAP_SIZE_X and 0 <= bullet.y <= MAP_SIZE_Y]
        if self.tank2 is not None:
            if self.tank1.health == 0:
                # print("Player 2 wins!")
                return True, took_damage, points
            if self.tank2.health == 0:
                # print("Player 1 wins!")
                return True, took_damage, points
            self.tank1.decrease_cooldown()
            self.tank2.decrease_cooldown()
        else:
            if self.tank1.health == 0:
                # print("You lose!")
                # print(f"Final score: {self.points}")
                return True, took_damage, points
            self.tank1.decrease_cooldown()
        
            if len(self.tank_bots) < self.max_enemies and self.spawn_cooldown == 0 or len(self.tank_bots) == 0:
                spawner = random.choice(self.spawners)
                # check if there's any tank on the spawner
                while any(Utils.check_collision(spawner, tank) for tank in self.tank_bots + [self.tank1]):
                    spawner = random.choice(self.spawners)
                self.tank_bots.append(spawner.spawn())
                self.spawn_cooldown = 120
        if self.spawn_cooldown > 0:
            self.spawn_cooldown -= 1
        return False, took_damage, points

class Tank:
    def __init__(self, x, y, color):
        # positon
        self.x = x * PIXEL_SIZE
        self.y = y * PIXEL_SIZE

        # movement
        self.move_cooldown = 0
        self.direction = (0, PIXEL_SIZE)
        
        # shooting
        self.reload_time = 0
        
        # hp
        self.health = 3

        # skin
        self.color = color

        self.rect = pygame.Rect(self.x, self.y, BLOCK_SIZE, BLOCK_SIZE)

    def move(self, direction: Direction, game_state):
        dx, dy = direction.value
        self.direction = direction.value
        new_x = min(max(0, self.x + dx), MAP_SIZE_X)
        new_y = min(max(0, self.y + dy), MAP_SIZE_Y)
        old_rect = self.rect
        self.rect = pygame.Rect(new_x, new_y, BLOCK_SIZE, BLOCK_SIZE)
        for obstacle in game_state.map + [game_state.tank1] + [game_state.tank2] + game_state.tank_bots:
            if obstacle is None or obstacle == self:
                continue
            if Utils.check_collision(self, obstacle):
                self.rect = old_rect
                return
        if self.move_cooldown > 0:
            return
        self.move_cooldown = 3
        self.x = new_x
        self.y = new_y

    def shoot(self, game_state):
        if self.reload_time > 0:
            return
        self.reload_time = 80
        # it just works, don't ask me how
        bullet_x = self.x + (BLOCK_SIZE ) // 2 - BULLET_SIZE // 2 + self.direction[0]//PIXEL_SIZE * BLOCK_SIZE
        bullet_y = self.y + (BLOCK_SIZE) // 2 - BULLET_SIZE // 2 + self.direction[1]//PIXEL_SIZE * BLOCK_SIZE
        game_state.bullets.append(Bullet(bullet_x, bullet_y, self.direction))

    def decrease_cooldown(self):
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
        if self.reload_time > 0:
            self.reload_time -= 1

    def draw(self, screen):
        if self.color == (255, 0, 0):
            i = 1
        elif self.color == (0, 255, 0):
            i = 2
        else:
            i = 3
        # pygame.draw.rect(screen, self.color, (self.x, self.y, BLOCK_SIZE, BLOCK_SIZE))
        match self.direction:
            case Direction.LEFT.value:
                img = pygame.image.load(f"lab4/assets/tank{i}_90.png")
            case Direction.RIGHT.value:
                img = pygame.image.load(f"lab4/assets/tank{i}_270.png")
            case Direction.UP.value:
                img = pygame.image.load(f"lab4/assets/tank{i}_0.png")
            case Direction.DOWN.value:
                img = pygame.image.load(f"lab4/assets/tank{i}_180.png")
        screen.blit(img, (self.x, self.y))

class TankBot(Tank):
    def __init__(self, x, y, color):
        super().__init__(x//PIXEL_SIZE, y//PIXEL_SIZE, color)
        self.turn_cooldown = 25
        self.health = 1

    def move(self, game_state):
        if self.move_cooldown > 0:
            return
        if self.turn_cooldown == 0:
            direction = random.choice(list(Direction)).value
            self.turn_cooldown = 25
        else:
            direction = self.direction
        self.move_cooldown = 5
        self.direction = direction
        dx, dy = self.direction
        new_x = min(max(0, self.x + dx), MAP_SIZE_X)
        new_y = min(max(0, self.y + dy), MAP_SIZE_Y)
        old_rect = self.rect
        self.rect = pygame.Rect(new_x, new_y, BLOCK_SIZE, BLOCK_SIZE)
        for obstacle in game_state.map + [game_state.tank1] + [game_state.tank2] + game_state.tank_bots:
            if obstacle is None or obstacle == self:
                continue
            if Utils.check_collision(self, obstacle):
                self.rect = old_rect
                return
        self.x = new_x
        self.y = new_y

    def shoot(self, game_state):
        if self.reload_time > 0:
            return
        self.reload_time = 180 
        # it just works, don't ask me how
        bullet_x = self.x + (BLOCK_SIZE ) // 2 - BULLET_SIZE // 2 + self.direction[0]//PIXEL_SIZE * BLOCK_SIZE
        bullet_y = self.y + (BLOCK_SIZE) // 2 - BULLET_SIZE // 2 + self.direction[1]//PIXEL_SIZE * BLOCK_SIZE
        game_state.bullets.append(Bullet(bullet_x, bullet_y, self.direction, is_from_bot=True))

    def decrease_cooldown(self):
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
        if self.reload_time > 0:
            self.reload_time -= 1
        if self.turn_cooldown > 0:
            self.turn_cooldown -= 1

class TankBotSpawner:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.rect = pygame.Rect(self.x, self.y, BLOCK_SIZE, BLOCK_SIZE)

    def spawn(self):
        return TankBot(self.x, self.y, self.color)        
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, BLOCK_SIZE, BLOCK_SIZE))

class Bullet:
    def __init__(self, start_x, start_y, direction, is_from_bot=False, velocity=1):
        self.x = start_x
        self.y = start_y
        self.direction = direction
        self.velocity = velocity
        self.is_from_bot = is_from_bot
        self.rect = pygame.Rect(self.x, self.y, BULLET_SIZE, BULLET_SIZE)
        
    def draw(self, screen):
        img = pygame.image.load("lab4/assets/bullet.png")
        screen.blit(img, (self.x, self.y))
        
    def move(self):
        dx, dy = self.direction
        self.x += dx * self.velocity
        self.y += dy * self.velocity
        self.rect = pygame.Rect(self.x, self.y, BULLET_SIZE, BULLET_SIZE)

class Obstacle:
    def __init__(self, x, y, shootable=False, destructible=False, color=(0, 0, 0)):
        self.x = x
        self.y = y
        self.shootable = shootable
        self.destructible = destructible
        self.hp = 3
        self.color = color
        self.rect = pygame.Rect(self.x, self.y, BLOCK_SIZE, BLOCK_SIZE)

    def draw(self, screen):
        if self.destructible:
            self.color = (255, 64*self.hp, 0)
        pygame.draw.rect(screen, self.color, (self.x, self.y, BLOCK_SIZE, BLOCK_SIZE))

def handle_key_presses(game_state: State):
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        game_state.tank1.move(Direction.UP)
    elif keys[pygame.K_s]:
        game_state.tank1.move(Direction.DOWN)
    elif keys[pygame.K_a]:
        game_state.tank1.move(Direction.LEFT)
    elif keys[pygame.K_d]:
        game_state.tank1.move(Direction.RIGHT)
    if keys[pygame.K_SPACE]:
        game_state.tank1.shoot()

    if game_state.tank2 is not None:
        if keys[pygame.K_UP]:
            game_state.tank2.move(Direction.UP)
        elif keys[pygame.K_DOWN]:
            game_state.tank2.move(Direction.DOWN)
        elif keys[pygame.K_LEFT]:
            game_state.tank2.move(Direction.LEFT)
        elif keys[pygame.K_RIGHT]:
            game_state.tank2.move(Direction.RIGHT)
        if keys[pygame.K_RCTRL]:
            game_state.tank2.shoot()

def handle_key_presses_AI(game_state: State, action):
    if action[0] == 1:
        game_state.tank1.move(Direction.UP, game_state)
    if action[1] == 1:
        game_state.tank1.move(Direction.DOWN, game_state)
    if action[2] == 1:
        game_state.tank1.move(Direction.LEFT, game_state)
    if action[3] == 1:
        game_state.tank1.move(Direction.RIGHT, game_state)
    if action[4] == 1:
        game_state.tank1.shoot(game_state)

class TankGame:
    def __init__(self, map_name, FPS=60):
        self.map_name = map_name
        init_map, tank1, spawners = Utils.init_map(map_name)
        self.game_state = State(tank1, init_map, spawners=spawners)
        self.screen = pygame.display.set_mode([MAP_SIZE_X, MAP_SIZE_Y])
        self.clock = pygame.time.Clock()
        self.FPS = FPS
        self.frame_iteration = 0
        self.cooldown = 0
        self.human_mode = True

    def reset(self):
        init_map, tank1, spawners = Utils.init_map(self.map_name)
        self.game_state = State(tank1, init_map, spawners=spawners)
        self.frame_iteration = 0
        self.game_state.tank_bots = [self.game_state.spawn_bot_on_start()]

    def play_step(self, action):
        self.clock.tick(self.FPS)
        self.frame_iteration += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_h] and self.cooldown == 0:
            self.human_mode = not self.human_mode
            self.cooldown = 10
        if self.cooldown > 0:
            self.cooldown -= 1
        reward = 0
        handle_key_presses_AI(self.game_state, action)
        is_over, took_damage, points = self.game_state.game_tick(self.game_state)
        if took_damage:
            reward -= 5
            if is_over:
                return reward, is_over, self.game_state.points
        if points > 0:
            reward += 1
        if self.frame_iteration > 1500*(self.game_state.points+1):
            reward -= 10
            return reward, True, self.game_state.points
        if action[4] == 1 and 0 < self.game_state.tank1.reload_time < 79:
            reward -= 1
        if self.human_mode:
            self.game_state.draw(self.screen, self.game_state)
            pygame.display.flip()
        return reward, is_over, self.game_state.points