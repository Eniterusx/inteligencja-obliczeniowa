# Simple pygame code!
import pygame
from enum import Enum
import random

PIXEL_SIZE = 6
BLOCK_SIZE = PIXEL_SIZE*6
BULLET_SIZE = PIXEL_SIZE*2
from PIL import Image



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

    def draw_hp(tank1, tank2):
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
    
class State:
    def __init__(self, tank1, init_map, tank2=None, spawners=[]):
        self.tank1 = tank1
        self.tank2 = tank2
        self.bullets = []
        self.map = init_map
        self.spawners = spawners
        self.spawn_cooldown = 60
        self.tank_bots = []
        self.points = 0

    def draw(self, screen):         
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
        Utils.draw_hp(self.tank1, self.tank2)

    def game_tick(self):
        if self.tank2 is None:
            for tank_bot in self.tank_bots:
                if tank_bot.health == 0:
                    self.tank_bots.remove(tank_bot)
                    self.points += 1
                    continue
                tank_bot.move()
                tank_bot.shoot()
                tank_bot.decrease_cooldown()
        for bullet in self.bullets:
            bullet.move()
            for obstacle in self.map:
                if obstacle.shootable:
                    continue
                if Utils.check_collision(bullet, obstacle):
                    self.bullets.remove(bullet)
                    if obstacle.destructible:
                        obstacle.hp -= 1
                        if obstacle.hp == 0:
                            self.map.remove(obstacle)
                    break
            if Utils.check_collision(bullet, self.tank1):
                self.tank1.health -= 1
                self.bullets.remove(bullet)
            if self.tank2 is not None:
                if Utils.check_collision(bullet, self.tank2):
                    self.tank2.health -= 1
                    self.bullets.remove(bullet)
            else:
                if not bullet.is_from_bot:
                    for tank_bot in self.tank_bots:
                        if Utils.check_collision(bullet, tank_bot):
                            tank_bot.health -= 1
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
            if tank1.health == 0:
                print("Player 2 wins!")
                exit()
            if self.tank2.health == 0:
                print("Player 1 wins!")
                exit()
            self.tank1.decrease_cooldown()
            self.tank2.decrease_cooldown()
        else:
            if tank1.health == 0:
                print("You lose!")
                print(f"Final score: {self.points}")
                exit()
            tank1.decrease_cooldown()

            if len(self.tank_bots) < 12 and self.spawn_cooldown == 0:
                spawner = random.choice(self.spawners)
                # check if there's any tank on the spawner
                while any(Utils.check_collision(spawner, tank) for tank in self.tank_bots + [self.tank1]):
                    spawner = random.choice(self.spawners)
                self.tank_bots.append(spawner.spawn())
                self.spawn_cooldown = 120
        if self.spawn_cooldown > 0:
            self.spawn_cooldown -= 1

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

    def move(self, direction: Direction):
        dx, dy = direction.value
        self.direction = direction.value
        new_x = min(max(0, self.x + dx), MAP_SIZE_X)
        new_y = min(max(0, self.y + dy), MAP_SIZE_Y)
        old_rect = self.rect
        self.rect = pygame.Rect(new_x, new_y, BLOCK_SIZE, BLOCK_SIZE)
        global game_state
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

    def shoot(self):
        if self.reload_time > 0:
            return
        self.reload_time = 80
        global game_state
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

    def move(self):
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
        global game_state
        for obstacle in game_state.map + [game_state.tank1] + [game_state.tank2] + game_state.tank_bots:
            if obstacle is None or obstacle == self:
                continue
            if Utils.check_collision(self, obstacle):
                self.rect = old_rect
                return
        self.x = new_x
        self.y = new_y

    def shoot(self):
        if self.reload_time > 0:
            return
        self.reload_time = 70 
        global game_state
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


pygame.init() # intialize the library


# Create the map
init_map, tank1, obj2 = Utils.init_map("survival.txt")
screen = pygame.display.set_mode([MAP_SIZE_X, MAP_SIZE_Y])

if isinstance(obj2, Tank):
    game_state = State(tank1, init_map, tank2=obj2)
else:
    game_state = State(tank1, init_map, spawners=obj2)

clock = pygame.time.Clock()

# Run until the user asks to quit
running = True
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    handle_key_presses(game_state)
        
    
    game_state.game_tick()

    game_state.draw(screen)

    # Flip the display
    pygame.display.flip()

# Quit the program
pygame.quit()