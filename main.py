import pygame
import os
import random
pygame.font.init()

WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mario in Space")

# Load images
DRAGON = pygame.image.load(os.path.join("assets", "dragon.png"))
TURTLE = pygame.image.load(os.path.join("assets", "turtle.png"))
MONSTER = pygame.image.load(os.path.join("assets", "monster.png"))

# Player
MARIO = pygame.image.load(os.path.join("assets", "mario.png"))

# Blasters
DRAGON_BLAST = pygame.image.load(os.path.join("assets", "fireball.png"))
TURTLE_BLAST = pygame.image.load(os.path.join("assets", "turtle_blast.png"))
MONSTER_BLAST = pygame.image.load(os.path.join("assets", "monster_blast.png"))
MARIO_BLAST = pygame.image.load(os.path.join("assets", "mario_blast.png"))
# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))


class Blaster:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (height >= self.y >= 0)

    def collision(self, obj):
        return collide(obj, self)


class Character:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.character_img = None
        self.blaster_img = None
        self.blasters = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.character_img, (self.x, self.y))
        for blaster in self.blasters:
            blaster.draw(window)

    def move_blasters(self, vel, obj):
        self.cooldown()
        for blaster in self.blasters:
            blaster.move(vel)
            if blaster.off_screen(HEIGHT):
                self.blasters.remove(blaster)
            elif blaster.collision(obj):
                obj.health -= 10
                self.blasters.remove(blaster)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            blaster = Blaster(self.x, self.y, self.blaster_img)
            self.blasters.append(blaster)
            self.cool_down_counter = 1

    def get_width(self):
        return self.character_img.get_width()

    def get_height(self):
        return self.character_img.get_height()


class Player(Character):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.character_img = MARIO
        self.blaster_img = MARIO_BLAST
        self.mask = pygame.mask.from_surface(self.character_img)
        self.max_health = health

    def move_blasters(self, vel, objs):
        self.cooldown()
        for blaster in self.blasters:
            blaster.move(vel)
            if blaster.off_screen(HEIGHT):
                self.blasters.remove(blaster)
            else:
                for obj in objs:
                    if blaster.collision(obj):
                        objs.remove(obj)
                        if blaster in self.blasters:
                            self.blasters.remove(blaster)


class Enemy(Character):
    COLOR_MAP = {
        "red": (DRAGON, DRAGON_BLAST),
        "green": (TURTLE, TURTLE_BLAST),
        "blue": (MONSTER, MONSTER_BLAST)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.character_img, self.blaster_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.character_img)

    def move(self, vel):
        self.y += vel


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None


def main():
    run = True
    fps = 60
    level = 0
    lives = 5

    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)

    enemies = []
    wave_length = 1
    enemy_velocity = 1
    player_velocity = 5
    blaster_velocity = 4

    player = Player(300, 650)

    clock = pygame.time.Clock()

    lost = False
    lost_display_mesagae_sec = 0

    def redraw_window():
        WIN.blit(BG, (0, 0))
        # draw text
        lives_label = main_font.render(f"Lives: {lives}", False, (255, 255, 255))
        level_label = main_font.render(f"level:{level}", False, (255, 255, 255))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy_people in enemies:
            enemy_people.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("You need some milk!!", False, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()

    while run:
        clock.tick(fps)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_display_mesagae_sec += 1

        if lost:
            if lost_display_mesagae_sec > fps * 5:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500,
                                                                                -100),
                              random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and player.x + player_velocity > player_velocity:
            player.x -= player_velocity
        if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and player.x + player_velocity + player.get_width() < WIDTH:
            player.x += player_velocity
        if (keys[pygame.K_w] or keys[pygame.K_UP]) and player.y + player_velocity + player.get_height() > 100:
            player.y -= player_velocity
        if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and player.y + player_velocity + player.get_height() < HEIGHT:
            player.y += player_velocity
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_velocity)
            enemy.move_blasters(blaster_velocity, player)

            if random.randrange(0, 120) == 1:
                enemy.shoot()
            if enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)
        player.move_blasters(-blaster_velocity, enemies)


main()
