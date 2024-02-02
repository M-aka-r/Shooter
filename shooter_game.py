import sys
import os

from pygame import *
from random import randint

win_width, win_height = 700, 500
window = display.set_mode((win_width, win_height))
display.set_caption("Shooter 2D")

clock = time.Clock()

fps = 60 # ? 1 секунда = 60 тиков
game_run = True
game_finished = False

# ! Створення звуків
mixer.init()
mixer.music.load("dream.mp3")
mixer.music.play(-1)
mixer.music.set_volume(0.2)

fire_sound = mixer.Sound("fire.ogg")
fire_sound.set_volume(0.05)

pop_sound = mixer.Sound("popadanie.mp3")
pop_sound.set_volume(0.15)

pop2_sound = mixer.Sound("popadaniea.mp3")
pop2_sound.set_volume(0.15)

health_sound = mixer.Sound("health.mp3")
health_sound.set_volume(0.15)

win_sound = mixer.Sound("win.mp3")
win_sound.set_volume(1)

gameover_sound = mixer.Sound("game_over.mp3")
gameover_sound.set_volume(1)




# ! Створення шрифтів
font.init()
stats_font = font.Font("code.ttf", 32)
main_font = font.Font("code.ttf", 72)

# ! Створюю текст поразки та перемоги
win_text = main_font.render("You win!", True, (50, 200, 0))
lose_text = main_font.render("You lose!", True, (200, 50, 0))
hp_font = font.SysFont("code.ttf", 18)

class GameSprite(sprite.Sprite):
    def __init__(self, img, x, y, w, h, speed):
        super().__init__()
        
        self.image = transform.scale(
            image.load(img),
            (w, h)
        )
        
        self.speed = speed
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))  
        
class Player(GameSprite):
    fire_delay = fps * 0.15
    fire_timer = fire_delay
    can_fire = True
    health = 4


    def update(self):
        
        hp_txt = hp_font.render(f"HP: {self.health - 1}", True, (0, 200, 0))

        if not self.can_fire:
            if self.fire_timer > 0:
                self.fire_timer -= 1
            else:
                self.fire_timer = self.fire_delay
                self.can_fire = True
        
        keys = key.get_pressed()
        if keys[K_a] or keys[K_LEFT]:
            if self.rect.x > 0:
                self.rect.x -= self.speed
        if keys[K_d] or keys[K_RIGHT]:
            if self.rect.x < win_width - self.image.get_width():
                self.rect.x += self.speed
        if keys[K_SPACE]:
            if self.can_fire:
                self.fire()
                self.can_fire = False

        window.blit(hp_txt, (self.rect.x + self.image.get_width() / 2 - hp_txt.get_width() / 2, self.rect.y + 100))        
    def fire(self):
        new_bullet = Bullet("bullet.png", self.rect.centerx - 7.5, self.rect.y, 15, 25, 5)
        bullet_group.add(new_bullet)
        fire_sound.play()
    
class Enemy(GameSprite):
    health = 1
    

    def update(self):
        global lost

        hp_txt = hp_font.render(f"HP: {self.health + 1}", True, (200, 40, 40))
        
        if self.rect.y >= win_height:
            lost += 1
            self.kill()
         
        elif sprite.collide_rect(self, player):
            player.health -= 1
            pop2_sound.play()
            self.kill()
        else:
            self.rect.y += self.speed

        window.blit(hp_txt, (self.rect.x + self.image.get_width() / 2 - hp_txt.get_width() / 2, self.rect.y - 25))    
class Bullet(GameSprite):
    def update(self):
        global kills

        if self.rect.y <= 0:
            self.kill()
            
        enemy = sprite.spritecollide(self, enemys_group, False) # ! Список ворогів, з якими зіткнулись

        if enemy: # ! Якщо зіткнулись з ворогом
            enemy = enemy[0] # ! Отримуємо ворога, з яким зіткнулись
            if enemy.health <= 0: # ! Якщо у ворога нема ХП
                kills += 1 
                pop_sound.play()
                enemy.kill()
            else: # ! Якщо у ворога є ХП
                enemy.health -= 1
                self.kill() # ! В будь якому разі виділяємо кулю

        self.rect.y -= self.speed
class Asteroid(GameSprite):
    def update(self):
        global lost
        
        if self.rect.y >= win_height:
            self.kill()
        elif sprite.collide_rect(self, player):
            player.health -= 1
            pop2_sound.play()
            self.kill()
        else:
            self.rect.y += self.speed
class Health(GameSprite):
    def update(self):
        global lost
        
        if self.rect.y >= win_height:
            self.kill()
        elif sprite.collide_rect(self, player):
            player.health += 1
            health_sound.play()
            self.kill()
        else:
            self.rect.y += self.speed

class HealthL(GameSprite):
    def update(self):
        global lost
        global kills

        if self.rect.y >= win_height:
            self.kill()
        elif sprite.collide_rect(self, player):
            health_sound.play()
            self.kill()
            if lost != 0:
                lost -= 1
        else:
            self.rect.y += self.speed
# ! Для таймера спавна ворогів
enemy_respawn_delay = fps * 1 # ? між спавном ворогів чекаємо 2 секунди
enemy_respawn_timer = enemy_respawn_delay # ? таймер

health_respawn_delay = fps * 6.5
health_respawn_timer = health_respawn_delay

healthl_respawn_delay = fps * 11
healthl_respawn_timer = healthl_respawn_delay

asteroid_respawn_delay = fps * 2 # ? між спавном ворогів чекаємо 2 секунди
asteroid_respawn_timer = asteroid_respawn_delay
# ! Змінні для лічильників
lost, kills = 0, 0

# ! Створення спрайтів
background = GameSprite("background.png", 0, 0, win_width, win_height, 0)
player = Player("korablik.png", win_width / 2.2, win_height - 120, 70, 100, 12)

# ! Створення груп спрайтів
enemys_group = sprite.Group()
bullet_group = sprite.Group()
asteroid_group = sprite.Group()
health_group = sprite.Group()
healthl_group = sprite.Group()
while game_run:
    
    for ev in event.get():
        if ev.type == QUIT:
            game_run = False
            
    if not game_finished:
        
        kills_text = stats_font.render(f"Kills: {kills}/40", True, (0, 200, 220))
        lost_text = stats_font.render(f"Losts: {lost}/5", True, (0, 200, 220))
        
        if enemy_respawn_timer > 0:
            enemy_respawn_timer -= 1
        else:
            new_enemy = Enemy("ufo.png", randint(0, win_width - 72), -72, 52, 44, randint(3, 5))
            new_enemy.health = randint(0, 2)
            enemys_group.add(new_enemy)
            enemy_respawn_timer = enemy_respawn_delay
            
        if asteroid_respawn_timer > 0:
            asteroid_respawn_timer -= 1
        else:
            new_asteroid = Asteroid("asteroidd.png", randint(0, win_width - 72), -72, 100, 80, randint(4, 6))
            asteroid_group.add(new_asteroid)
            asteroid_respawn_timer = asteroid_respawn_delay

        if health_respawn_timer > 0:
            health_respawn_timer -= 1
        else:
            new_health = Health("health.png", randint(0, win_width - 72), -72, 80, 60, randint(2, 3))
            health_group.add(new_health)
            health_respawn_timer = health_respawn_delay

        if healthl_respawn_timer > 0:
            healthl_respawn_timer -= 1
        else:
            new_healthl = HealthL("healthl.png", randint(0, win_width - 72), -72, 80, 60, randint(2, 3))
            healthl_group.add(new_healthl)
            healthl_respawn_timer = healthl_respawn_delay


        background.reset()
        
        player.reset()
        enemys_group.draw(window)
        bullet_group.draw(window)
        asteroid_group.draw(window)
        health_group.draw(window)
        healthl_group.draw(window)
        player.update()
        health_group.update()
        healthl_group.update()
        enemys_group.update()
        bullet_group.update()
        asteroid_group.update()

        window.blit(kills_text, (5, 5))
        window.blit(lost_text, (5, 38))
        
        if kills >= 40:
            mixer.stop()
            win_sound.play()
            window.blit(win_text, (win_width / 2 - win_text.get_width() / 2, win_height / 2 - win_text.get_height() / 2))

            game_finished = True
            
        if lost >= 5 or player.health <= 0:
            gameover_sound.play()
            window.blit(lose_text, (win_width / 2 - lose_text.get_width() / 2, win_height / 2 - lose_text.get_height() / 2))
            game_finished = True

        display.update()
    
    clock.tick(fps)