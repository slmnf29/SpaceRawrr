import sys
import random
import pygame
import pygame.image
import struct
from pygame.locals import *

pygame.init()

'''IMAGE'''
#INISIALISASI ASSETS GAMBAR
player_ship = 'assets\\img\\playership.png'
enemy_ship = 'assets\\img\\enemyship.png'
ufo_ship = 'assets\\img\\ufo.png'
player_bullet = 'assets\\img\\playerbullet.png'
enemy_bullet = 'assets\\img\\enemybullet.png'
ufo_bullet = enemy_bullet
heart = 'assets\\img\\heart.png'

'''SOUND'''
#INISIALISASI ASSETS SUARA
laser_sound = pygame.mixer.Sound("assets\\backsound\\pewpew.mp3")
explosion_sfx = pygame.mixer.Sound("assets\\backsound\\loud-explosion.wav")
game_over_sfx = pygame.mixer.Sound("assets\\backsound\\dark_souls_game_over.wav")
menu_sound = pygame.mixer.Sound("assets\\backsound\\cyberfunk.mp3")

ingame_sound = pygame.mixer.music.load("assets\\backsound\\epicsong.mp3")

#INISIALISASI pygame.mixer
pygame.mixer.init()

#set pygame.display
screen = pygame.display.set_mode((0,0), FULLSCREEN)
s_width, s_height = screen.get_size()

clock = pygame.time.Clock()
FPS = 60

#sprite = objek yang dipake di pygame
#sprite.Group() = sekumpulan objek yang dijadiin satu
background_group = pygame.sprite.Group()
particle_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
ufo_group = pygame.sprite.Group()
sprite_group = pygame.sprite.Group()
playerbullet_group = pygame.sprite.Group()
enemybullet_group = pygame.sprite.Group()
ufobullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()

#menyembunyikan cursor mouse
pygame.mouse.set_visible(False)

#class background ingame
class Background(pygame.sprite.Sprite):
    def __init__(self, x, y):
        #deklarasi partikel rect di background
        super().__init__()
        self.image = pygame.Surface([x,y])
        self.image.fill("white")
        self.image.set_colorkey('black')
        self.rect = self.image.get_rect()

    def update(self):
        #buat gerakin rect
        self.rect.y += 1
        self.rect.x += 1
        if self.rect.y > s_height:
            self.rect.y = random.randrange(-10, 0)
            self.rect.x = random.randrange(-400, s_width)

class Particle(Background):
    def __init__(self, x, y):
        #deklarasi partikel paling depan
        super().__init__(x, y)
        self.rect.x = random.randrange(0, s_width)
        self.rect.y = random.randrange(0, s_height)
        self.image.fill('grey')
        self.velocity = random.randint(3, 6)

    def update(self):
        #buat gerakin partikel
        self.rect.y += self.velocity
        if self.rect.y > s_height:
            self.rect.y = random.randrange(0, s_height)
            self.rect.x = random.randrange(0, s_width)

class Player(pygame.sprite.Sprite):
    def __init__(self, img):
        #inisialisasi player
        super().__init__()
        self.image = pygame.image.load(img)
        self.h_image = self.image.get_height()
        self.w_image = self.image.get_width()
        self.image.set_colorkey("black")
        self.rect = self.image.get_rect()
        self.hit_count = 0
        self.hit_max = 3
        self.alive = True
        self.count_to_live = 0
        self.activate_bullet = True
        self.alpha_duration = 0

    def update(self):
        #buat gerakin player
        if self.alive:
            #kalo hidup gerak
            self.image.set_alpha(80)
            self.alpha_duration += 1
            if self.alpha_duration > 170:
                self.image.set_alpha(255)
            mouse = pygame.mouse.get_pos()
            self.rect.x = mouse[0]
            self.rect.y = mouse[1]
        else:
            #kalo mati objek hilang, kasih efek meledak,
            #tunggu beberapa detik, player hidup lagi
            explosion = Explosion(self.rect.x + 20, self.rect.y + 35)
            self.rect.y = s_height + 200
            explosion_group.add(explosion)
            sprite_group.add(explosion)
            self.count_to_live += 1
            if self.count_to_live > 100:  
                self.count_to_live = 0
                self.alive = True
                self.alpha_duration = 0
                self.activate_bullet = True

    def shoot(self):
        #agar player dapat menembaki enemy / ufo
        if self.activate_bullet:
            #kalo peluru boleh keluar, maka keluarin peluru
            mouse = pygame.mouse.get_pos()
            bullet = PlayerBullet(player_bullet)
            bullet.rect.x = mouse[0] + 23
            bullet.rect.y = mouse[1]
            playerbullet_group.add(bullet)
            sprite_group.add(bullet)
            pygame.mixer.Sound.play(laser_sound)

    def dead(self):
        #untuk mengidentifikasi apakah player hidup atau mati
        self.alive = False
        self.activate_bullet = False
        pygame.mixer.Sound.play(explosion_sfx)
             
class Enemy(Player):
    def __init__(self, img):
        #inisialisasi enemy
        super().__init__(img)
        self.rect.y = random.randrange(-1000,  -1 * (self.h_image))
        self.rect.x = random.randrange(0, s_width - self.w_image)
        self.move_y = 1
        self.move_x = 0
        self.hit_max = 2
        screen.blit(self.image, (self.rect.x, self.rect.y))

    def update(self):
        #buat gerakin enemy
        self.rect.y += self.move_y
        if self.rect.y > s_height:
            self.rect.x = random.randrange(0, s_width - self.w_image)
            self.rect.y = random.randrange(-1000, -1 * (self.h_image))
        self.shoot()

    def shoot(self):
        #agar enemy dapat menembak
        bullet_freq = 200
        if not(self.rect.y % bullet_freq) and self.rect.y < int(s_height * 0.3):
            enemybullet = EnemyBullet(enemy_bullet)
            enemybullet.rect.x = self.rect.x + 16
            enemybullet.rect.y = self.rect.y + 10
            enemybullet_group.add(enemybullet)
            sprite_group.add(enemybullet)

class Ufo(Enemy):
    def __init__(self, img):
        #inilisialisasi ufo
        super().__init__(img)
        self.rect.x = -600
        self.rect.y = 200
        self.move_x = 2
        self.move_y = 0
        self.hit_max = 12
        self.using_skill = False
    
    def update(self):
        #buat gerakin ufo
        if random.randrange(1, 1500) == 1:
            #agar suatu saat ufo dapat menggunakan skillnya
            #secara random
            self.using_skill = True
        
        if self.using_skill:
             #kalau diijinin pake skill, maka gunakan skill
             self.skill()
        else:
            #kalau tidak maka ufo hanya bergerak dan menembak
            self.rect.x += self.move_x
            if self.rect.x > s_width + 200 and self.move_x > 0:
                self.move_x *= -1
            elif self.rect.x < -200 and self.move_x < 0:
                self.move_x *= -1
            self.shoot()

    def shoot(self):
        #agar ufo dapat menembak
        bullet_freq = 150
        if not(self.rect.x % bullet_freq):
            ufobullet = EnemyBullet(ufo_bullet)
            ufobullet.rect.x = self.rect.x + 50
            ufobullet.rect.y = self.rect.y + 70
            ufobullet_group.add(ufobullet)
            sprite_group.add(ufobullet)

    def skill(self):
        #skill ufo berupa mengejar player dan menabraknya
        target_pos = pygame.mouse.get_pos()
        self.move_y = 5
        if target_pos[0] < self.rect.x:
            self.move_x = -8
        elif target_pos[0] > self.rect.x + 100:
            self.move_x = 8
        else:
            self.move_x = 0
        self.rect.y += self.move_y
        self.rect.x += self.move_x
        if self.rect.y > s_height or self.rect.x < 0:
            self.using_skill = False
            self.rect.x = -600
            self.rect.y = 200
            self.move_x = 2
            self.move_y = 0
            self.hit_max = 12

class PlayerBullet(pygame.sprite.Sprite):
    #untuk inilisialisasi peluru player
    def __init__(self, img):
        super().__init__()
        self.image = pygame.image.load(img)
        self.rect = self.image.get_rect()
        self.image.set_colorkey('black')

    def update(self):
        self.rect.y -= 10
        if self.rect.y < 0:
            self.kill()

class EnemyBullet(PlayerBullet):
    #untuk inilisialisasi peluru enemy
    def __init__(self, img):
        super().__init__(img)
        self.image.set_colorkey("white")
    
    def update(self):
        self.rect.y += 3
        if self.rect.y > s_height:
            self.kill()

class UfoBullet(EnemyBullet):
    #untuk inilisialisasi peluru ufo
    def __init__(self, img):
        super().__init__(img)

class Explosion(pygame.sprite.Sprite):
    #untuk inilisialisasi bentuk ledakan
    def __init__(self, x, y):
        super().__init__()
        #export gambar satu-per-satu
        self.img_list = []
        for i in range(1,6):
            img = pygame.image.load(f"assets\\img\\exp{i}.png").convert()
            img.set_colorkey("black")
            img = pygame.transform.scale(img, (120, 120))
            self.img_list.append(img)

        self.index = 0
        self.image = self.img_list[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.count_delay = 0
        self.delay = 8

    def update(self):
        #untuk menganimasikan ledakan
        self.count_delay += 1
        if self.count_delay >= self.delay:
            if self.index < len(self.img_list) - 1:
                self.count_delay = 0
                self.index += 1
                self.image = self.img_list[self.index]
        if self.index >= len(self.img_list) - 1:
            if self.count_delay >= self.delay:
                self.kill()

class Game:
    def __init__(self):
        self.score = 0
        self.high_score = 200
        self.init_create = True
        self.start_screen()

    def read_bin_file(self, nama_file):
        #Membaca file highscore yang berformaat bin
        try:
            file = open(nama_file, "rb")
        except FileNotFoundError:
            file = open(nama_file, "wb")
            data = struct.pack("i", 0)
            file.write(data)
            file.close()
            file = open(nama_file, "rb")
        data_int = file.read()
        data_int = struct.unpack("i", data_int)[0]
        file.close()
        return data_int

    def write_bin_file(self, nama_file, data_int):
        #menulis file highscore yang berformaat bin
        file = open(nama_file, "wb")
        data = struct.pack("i", data_int)
        file.write(data)
        file.close()

    def start_text(self):
        #mengidentifikasi teks yang ingin ditampilkan pada menu awal
        font = pygame.font.Font("assets\\font\\RollboxSemiBoldItalic-51Vez.ttf", 40)
        text_1 = font.render("SPACE RAWRRR", True, "green")
        text_rect = text_1.get_rect(center=(s_width/2, s_height/2))
        screen.blit(text_1, text_rect)
        
        font = pygame.font.Font("assets\\font\\RollboxSemiBoldItalic-51Vez.ttf", 25)
        text_2 = font.render("PRESS ENTER TO PLAY", True, "white")
        text_rect = text_2.get_rect(center=(s_width/2, s_height/2 + 25))
        screen.blit(text_2, (text_rect[0], text_rect[1] + 10))

    def start_screen(self):
        #menata kalimat yang ingin ditampilkan pada menu awal
        background_group.empty()
        particle_group.empty()
        player_group.empty()
        enemy_group.empty()
        ufo_group.empty()
        sprite_group.empty()
        playerbullet_group.empty()
        enemybullet_group.empty()
        ufobullet_group.empty()
        explosion_group.empty()
        pygame.mixer.Sound.play(menu_sound)
        self.score = 0
        while True:
            screen.fill("black")
            self.start_text()
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    elif event.key == K_RETURN:
                        self.run_game()

            pygame.display.update()

    def pause_text(self):
        #mengidentifikasi teks yang ingin ditampilkan pada menu pause
        font = pygame.font.Font("assets\\font\\RollboxSemiBoldItalic-51Vez.ttf", 50)
        text_1 = font.render("PAUSE", True, "green")
        text_rect = text_1.get_rect(center=(s_width/2, s_height/2))
        screen.blit(text_1, text_rect)

    def pause_screen(self):
        #menata teks yang ingin ditampilkan pada menu pause
        self.init_create = False
        self.pause_text()
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    elif event.key == K_SPACE:
                        self.run_game()

            pygame.display.update()

    def game_over_text(self):
        #menginilisialisasikan teks yang ingin ditampilkan pada menu game over
        font = pygame.font.Font("assets\\font\\RollboxSemiBoldItalic-51Vez.ttf", 50)
        text_1 = font.render("DUARRR, GAME OVERR", True, "red")
        text_rect = text_1.get_rect(center=(s_width/2, s_height/2))
        screen.blit(text_1, text_rect)

        font = pygame.font.Font("assets\\font\\RollboxSemiBoldItalic-51Vez.ttf", 25)
        text_2 = font.render("PRESS ESCAPE TO RETURN TO MENU", True, "white")
        text_rect = text_2.get_rect(center=(s_width/2, s_height/2 + 25))
        screen.blit(text_2, (text_rect[0], text_rect[1] + 10))

    def game_over_screen(self):
        #menata teks yang ingin ditampilkan pada menu game over
        pygame.mixer.music.stop()
        pygame.mixer.Sound.play(game_over_sfx)
        while True:
            screen.fill("black")
            self.game_over_text()
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.start_screen()

            pygame.display.update()
    
    def create_background(self):
        #mencetek partikel pada background sebanyak 20 buah dan
        #memasukkan partikel ke dalam group
        for i in range(20):
            x = random.randint(1,5)
            background_image = Background(x, x)
            background_image.rect.x = random.randrange(0, s_width)        
            background_image.rect.y = random.randrange(0, s_height)        
            background_group.add(background_image)
            sprite_group.add(background_image)

    def create_particle(self):
        #mencetak partikel pada layer terdepan sebanyak 100 buah
        #dan memasukkan partikel-partikel ke dalam group
        for i in range(100):
            x = 1
            y = random.randint(1, 6)
            particle = Particle(x, y)
            particle_group.add(particle)
            sprite_group.add(particle)

    def create_player(self):
        #mencetak objek player dan memasukkan ke dalam group
        self.player = Player(player_ship)
        player_group.add(self.player)
        sprite_group.add(self.player)

    def create_enemy(self):
        #mencetak dan memasukkan objek enemy ke group
        for i in range(10):
            self.enemy = Enemy(enemy_ship)
            enemy_group.add(self.enemy)
            sprite_group.add(self.enemy)

    def create_ufo(self):
        #mencetak dan memasukkan objek ufo ke dalam group
        for i in range(1):
            self.ufo = Ufo(ufo_ship)
            ufo_group.add(self.ufo)
            sprite_group.add(self.ufo)

    def playerbullet_hits_enemy(self):
        #menyimpulkan kondisi apabila peluru player mengenai enemy
        hits = pygame.sprite.groupcollide(enemy_group, playerbullet_group, False, True)
        for enemy_hit, bullet_hit in hits.items():
            enemy_hit.hit_count += 1
            if enemy_hit.hit_count > enemy_hit.hit_max:
                self.score += 10
                expl_x = enemy_hit.rect.x + 16
                expl_y = enemy_hit.rect.y + 30
                explosion = Explosion(expl_x, expl_y)
                explosion_group.add(explosion)
                sprite_group.add(explosion)
                pygame.mixer.Sound.play(explosion_sfx)
                
                enemy_hit.rect.x = random.randrange(0, s_width)
                enemy_hit.rect.y = random.randrange(-3000, -100)
                enemy_hit.hit_count = 0

    def playerbullet_hits_ufo(self):
        #menyimpulkan kondisi apabila peluru player mengenai ufo
        hits = pygame.sprite.groupcollide(ufo_group, playerbullet_group, False, True)
        for ufo_hit, bullet_hit in hits.items():
            ufo_hit.hit_count += 1
            if ufo_hit.hit_count >= ufo_hit.hit_max:
                self.score += 30
                expl_x = ufo_hit.rect.x + 50
                expl_y = ufo_hit.rect.y + 45
                explosion = Explosion(expl_x, expl_y)
                explosion_group.add(explosion)
                sprite_group.add(explosion)
                pygame.mixer.Sound.play(explosion_sfx)

                ufo_hit.rect.x = -600
                ufo_hit.rect.y = 200
                ufo_hit.hit_count = 0

    def enemybullet_hits_player(self):
        #menyimpulkan kondisi apabila peluru enemy mengenai player
        if self.player.image.get_alpha() == 255:
            hits = pygame.sprite.spritecollide(self.player, enemybullet_group, True)
            if hits :
                self.player.hit_count += 1
                self.player.dead()
                if self.player.hit_count > self.player.hit_max:
                    self.player.hit_count = 0
                    if self.score > self.high_score:
                        self.write_bin_file("assets\\hs.bin", self.score)
                    self.game_over_screen()
    
    def ufobullet_hits_player(self):
        #menyimpulkan kondisi apabila peluru ufo mengenai player
        if self.player.image.get_alpha() == 255:
            hits = pygame.sprite.spritecollide(self.player, ufobullet_group, True)
            if hits:
                self.player.hit_count += 1
                self.player.dead()
                if self.player.hit_count > self.player.hit_max:
                    self.player.hit_count = 0
                    if self.score > self.high_score:
                        self.write_bin_file("assets\\hs.bin", self.score)
                    self.game_over_screen()

    def player_enemy_crash(self):
        #menyimpulkan kondisi apabila player crash dengan enemy
        if self.player.image.get_alpha() == 255:
            hits = pygame.sprite.spritecollide(self.player, enemy_group, False)
            for enemy_hit in hits:
                self.score += 10
                expl_x = enemy_hit.rect.x + 16
                expl_y = enemy_hit.rect.y + 30
                explosion = Explosion(expl_x, expl_y)
                explosion_group.add(explosion)
                enemy_hit.rect.x = random.randrange(0, s_width)
                enemy_hit.rect.y = random.randrange(-3000, -100)

                self.player.hit_count += 1
                self.player.dead()
                sprite_group.add(explosion)
                if self.player.hit_count > self.player.hit_max:
                    self.player.hit_count = 0
                    if self.score > self.high_score:
                        self.write_bin_file("assets\\hs.bin", self.score)
                    self.game_over_screen()
    
    def player_ufo_crash(self):
        ##menyimpulkan kondisi apabila player crash dengan ufo
        if self.player.image.get_alpha() == 255:
            hits = pygame.sprite.spritecollide(self.player, ufo_group, False)
            for ufo_hit in hits:
                self.score += 30
                expl_x = ufo_hit.rect.x + 50
                expl_y = ufo_hit.rect.y + 45
                explosion = Explosion(expl_x, expl_y)
                explosion_group.add(explosion)
                sprite_group.add(explosion)
                ufo_hit.rect.x = -600
                ufo_hit.rect.y = 200
                ufo_hit.hit_count = 0

                self.player.hit_count += 1
                self.player.dead()
                sprite_group.add(explosion)
                if self.player.hit_count > self.player.hit_max:
                    self.player.hit_count = 0
                    if self.score > self.high_score:
                        self.write_bin_file("assets\\hs.bin", self.score)
                    self.game_over_screen()

    def create_lives_list(self):
        #mencetak health bar pada dekat pesawat
        self.live_img = pygame.image.load(heart)
        self.live_img = pygame.transform.scale(self.live_img, (20,20))
        live_img_rect = pygame.mouse.get_pos()
        n = 75
        for i in range(self.player.hit_max - self.player.hit_count):
            screen.blit(self.live_img, (live_img_rect[0] + n, live_img_rect[1] + 30))
            n+= 30

    def create_score(self):
        #mencetak skor pada dekat pesawat
        score = self.score
        font = pygame.font.Font("assets\\font\\RollboxSemiBoldItalic-51Vez.ttf", 18)
        text = font.render(str(score), True, 'green')
        text.set_alpha(220)
        text_rect = pygame.mouse.get_pos()
        screen.blit(text, (text_rect[0] + 75, text_rect[1] + 10))

    def create_high_score(self):
        font = pygame.font.Font("assets\\font\\RollboxSemiBoldItalic-51Vez.ttf", 23)
        text = font.render(f"HIGH SCORE : {self.high_score}", True, 'green')
        text.set_alpha(220)
        screen.blit(text, (10,10))

    def run_update(self):
        #mencetak semua objek dalam group sprite_group
        sprite_group.draw(screen)
        sprite_group.update()

    def run_game(self):
        if self.init_create:
            #apabila game baru mulai, maka semua perintah fungsi
            #pendeklarasian di jalankan, dan menata backsound
            pygame.mixer.Sound.stop(menu_sound)
            pygame.mixer.music.play(-1)
            self.create_background()
            self.create_particle()
            self.create_player()
            self.create_enemy()
            self.create_ufo()
            self.high_score = self.read_bin_file("assets\\hs.bin")
        while True:
            #mengupdate hasil yang terjadi pada tiap objek
            screen.fill("black")
            self.run_update()
            self.playerbullet_hits_enemy()
            self.playerbullet_hits_ufo()
            self.enemybullet_hits_player()
            self.ufobullet_hits_player()
            self.player_enemy_crash()
            self.player_ufo_crash()
            self.create_lives_list()
            self.create_score()
            self.create_high_score()

            #mengidentifikasi key yang dipencet user
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == MOUSEBUTTONDOWN:
                    self.player.shoot()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == K_SPACE:
                        self.pause_screen()
            pygame.display.update()
            clock.tick(FPS)

def main():
    #fungsi main
    game = Game()

if __name__ == "__main__":
    #menjalankan fungsi main secara otomatis
    main()