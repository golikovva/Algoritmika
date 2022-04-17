from pygame import *
from random import randint
from math import sin, sqrt
init()
class GameSrite(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, player_speed, size):
        super().__init__()
        self.image = transform.scale(image.load(player_image), size)
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y
        self.speed = player_speed
        self.mask = mask.from_surface(self.image)
        self.hp = 3
        self.buffs = []
        self.inner_start_time = time.get_ticks()+randint(1000, 5000)
        self.current_time = 0
    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSrite):
    reload_time = 500
    level = 0
    def update(self):
        if 'lvlup' in self.buffs:
            self.buffs.remove('lvlup')
            self.lvlup()
        keys_pressed = key.get_pressed()
        if keys_pressed[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed*(min(self.level, 3)+1)
        if keys_pressed[K_RIGHT] and self.rect.x < 630:
            self.rect.x += self.speed*(min(self.level,3)+1)
        # if keys_pressed[K_UP] and self.rect.y > 5:
        #     self.rect.y -= self.speed
        # if keys_pressed[K_DOWN] and self.rect.y < 430:
        #     self.rect.y += self.speed
    def lvlup(self):
        self.level += 1
        self.reload_time = max(self.reload_time-50, 100)
    def fire(self):
        bullet = Bullet('thumb.png', self.rect.centerx, self.rect.top, 12, (randint(5, 15), randint(10, 30)))
        bullets.add(bullet)
        if 'triple' in self.buffs:
            left_bullet = Bullet('thumb.png', self.rect.left, self.rect.top, 12, (5, 20), (-1, 2))
            right_bullet = Bullet('thumb.png', self.rect.right, self.rect.top, 12, (5, 20), (1, 2))
            bullets.add(left_bullet)
            bullets.add(right_bullet)

class Enemy(GameSrite):
    # start_time = 0
    
    def __init__(self, player_image, player_x, player_y, player_speed, size, complex_move):
        super().__init__(player_image, player_x, player_y, player_speed, size)
        self.complex_move = complex_move
        self.min_speed = 1
        self.max_speed = 4
        self.health = 3
    def to_start(self):
        self.inner_start_time = time.get_ticks()+randint(1000, 5000)
        # self.rect.y = -70.0
        self.rect.x = randint(0, 630)
        self.speed = randint(self.min_speed, self.max_speed)
    def update(self):
        global lost
        if self.rect.y < 500:
            # print(float(self.speed)*time_past)
            self.current_time = time.get_ticks()-self.inner_start_time
            # self.rect.y += float(self.speed)
            self.rect.y = self.current_time*0.03*self.speed
            if self.complex_move:
                self.rect.x += sin((time.get_ticks()-self.inner_start_time)/200)*5
        else:
            self.inner_start_time = time.get_ticks()+randint(1000, 5000)
            self.rect.y = -70.0
            self.rect.x = randint(0, 630)
            self.speed = randint(self.min_speed, self.max_speed)
            lost += 1
class Bullet(GameSrite):
    def __init__(self, bullet_image, x, y, speed, size, direction=(0, 1), damage=1):
        super().__init__(bullet_image, x, y, speed, size)
        module = sqrt(direction[0]**2 + direction[1]**2)
        self.dir = [direction[0]/module, direction[1]/module]
        self.damage = damage

    def update(self):
        if self.rect.y > 0:
            self.rect.x += self.speed*self.dir[0]
            self.rect.y -= self.speed*self.dir[1]
        else:
            self.kill()
class Buff(GameSrite):
    buff_number = 2
    def __init__(self, player_image, player_x, player_y, player_speed, size, buff):
        super().__init__(player_image, player_x, player_y, player_speed, size)
        self.buff = buff
    def update(self):
        if self.rect.y < 500:
            self.current_time = time.get_ticks()-self.inner_start_time
            self.rect.y = self.current_time*0.03*self.speed
        else:
            self.kill()
    def create_buff():
        b = randint(1,Buff.buff_number)
        if b == 1:
            buff = Buff('Flight_Bonus.png8', randint(0, 630), -70, 2, (40, 40), 'triple')
        if b == 2:
            buff = Buff('Coin.png8', randint(0, 630), -70, 2, (40, 40), 'lvlup')
        buffs.add(buff)
    def give_buff(self, player):
        if self.buff not in player.buffs:
            player.buffs.append(self.buff)
def try_buff():
    if randint(1, 1000) > 998:
        Buff.create_buff()

#создай окно игры
window = display.set_mode((700, 500))
display.set_caption("Лабиринт")
mixer.init()
# mixer.music.load('jungles.ogg')
# mixer.music.play()
volume = 0.5
game_time = time.get_ticks()

background = transform.scale(image.load("background.jpg"), (700, 500))
hero = Player('sprite1.png', 100, 430, 3, (60, 80))
# счетчики
lost = 0
killed = 0

buffs = sprite.Group()
bullets = sprite.Group()
monsters = sprite.Group()
enemy_number = 5

for i in range(enemy_number):
    monster = Enemy('mario.png', randint(0, 630), randint(-150, 0), randint(1, 4), (70, 70), randint(0, 1))
    monsters.add(monster)

clock = time.Clock()
FPS = 40
font.init()
font1 = font.SysFont('Arial', 30)
font2 = font.SysFont('Arial', 70)
lose = font2.render('YOU LOSE!', True, (251, 215, 0))
win = font2.render('YOU WIN!', True, (251, 215, 0))

game = True
finish = False
bullet_reload = 0 
while game:
    frame_time = clock.tick(FPS)
    # frame_time /=16
    if finish != True:
        window.blit(background, (0,0))
        passed_text = font1.render("Пропущено: " + str(lost), True, (255, 255, 255))
        killed_text = font1.render("До следующего уровня: " + str(10-killed), True, (255, 255, 255))
        level_text = font1.render("Уровень: " + str(hero.level), True, (255, 255, 255))
        window.blit(passed_text, (0, 10))
        window.blit(killed_text, (0, 40))
        window.blit(level_text, (0, 70))
        try_buff()
        monsters.update()
        monsters.draw(window)
        hero.update()
        hero.reset()
        bullets.update()
        bullets.draw(window)
        buffs.update()
        buffs.draw(window)
        sprite_list = sprite.spritecollide(hero, monsters, False, sprite.collide_mask)
        if sprite_list:
            finish = True
            window.blit(lose, (250, 240))

        buff_list = sprite.spritecollide(hero, buffs, True)
        for b in buff_list:
            b.give_buff(hero)

        killed_monsters = sprite.groupcollide(monsters, bullets, False, True)
        for m in killed_monsters:
            # monster = Enemy('mario.png', randint(0, 630), -200, 3, (70, 70))
            # monsters.add(monster)
            m.hp -= 1
            if m.hp <=0:
                m.to_start()
                m.hp = 3
                killed +=1
            if killed >= 10:
                hero.lvlup()
                new_monster = Enemy('mario.png', randint(0, 630), randint(-150, 0), randint(1, 4), (70, 70), randint(0, 1))
                monsters.add(new_monster)
                killed = 0


        bullet_reload += frame_time
        keys_pressed = key.get_pressed()
        if keys_pressed[K_SPACE] and bullet_reload > hero.reload_time:
            hero.fire()
            bullet_reload = 0
    for e in event.get():
        if e.type == QUIT:
            game = False
    keys_pressed = key.get_pressed()
    if keys_pressed[K_KP_MINUS] and volume >= 0.1:
        volume -= 0.1
        print(volume)
    if keys_pressed[K_KP_PLUS] and volume <= 0.9:
        volume += 0.1
        print(volume)
    mixer.music.set_volume(volume)

    display.update()
    
