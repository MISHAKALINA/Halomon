import pygame
from pygame.locals import *
import time
import math
import random
from lxml import etree
import os

pygame.init()
#создание списка всех видов движений
all_moves = []
file = os.getcwd() + "\\moves.xml"
moves = etree.parse(file)
moves = etree.tostring(moves)
moves = etree.fromstring(moves)
for move in moves:
    all_moves.append(move.get("name"))
#создание списка всех имён
all_names = []
file = os.getcwd() + "\\stats.xml"
names = etree.parse(file)
names = etree.tostring(names)
names = etree.fromstring(names)
for name in names:
    all_names.append(name.get("name"))
#создание шаблонов для цвета
black = (0, 0, 0)
gold = (218, 165, 32)
grey = (200, 200, 200)
green = (0, 200, 0)
red = (200, 0, 0)
white = (255, 255, 255)

#класс для движений
class Move:

    def __init__(self, name):
        self.name = name
        file = os.getcwd() + "\\moves.xml"
        moves = etree.parse(file)
        moves = etree.tostring(moves)
        moves = etree.fromstring(moves)
        for move in moves:
            if move.get("name") == name:
                for stat in move:
                    if stat.tag == "type":
                        self.type = stat.text
                    elif stat.tag == "category":
                        self.category = stat.text
                    elif stat.tag == "power":
                        self.power = int(stat.text)
                    elif stat.tag == "accuracy":
                        self.accuracy = int(stat.text)
                    elif stat.tag == "pp":
                        self.pp = int(stat.text)
                break

#класс персонажа(игрового и npc)
class Character(pygame.sprite.Sprite):

    def __init__(self, name, level, x, y, moves=random.sample(all_moves, 4)):

        pygame.sprite.Sprite.__init__(self)

        self.name = name
        self.level = level
        self.x = x
        self.y = y
        self.moves = []
        for i in range(len(moves)):
            self.moves.append(Move(moves[i]))
        self.medkit = 3
        self.IV_hp = random.randint(0, 31)
        self.IV_attack = random.randint(0, 31)
        self.IV_defense = random.randint(0, 31)
        self.IV_speed = random.randint(0, 31)
        file = os.getcwd() + "\\stats.xml"
        characters = etree.parse(file)
        characters = etree.tostring(characters)
        characters = etree.fromstring(characters)
        for character in characters:
            if character.get("name") == name:
                for stat in character:
                    if stat.tag == "hp":
                        self.max_hp = math.floor(
                            ((2 * int(stat.text) + self.IV_hp * self.level) / 100) + self.level + 10)
                        self.current_hp = self.max_hp
                        self.base_hp = int(stat.text)
                    elif stat.tag == "attack":
                        self.attack = math.floor(0.01 * (2 * int(stat.text) + self.IV_attack * self.level) + 5)
                        self.base_attack = int(stat.text)
                    elif stat.tag == "defense":
                        self.defense = math.floor(0.01 * (2 * int(stat.text) + self.IV_defense * self.level) + 5)
                        self.base_defense = int(stat.text)
                    elif stat.tag == "speed":
                        self.speed = math.floor(0.01 * (2 * int(stat.text) + self.IV_speed * self.level) + 5)
                        self.base_speed = int(stat.text)
                    elif stat.tag == "shield":
                        self.max_shield = int(stat.text)
                break #выше получение базовых статов персонажей и дальнейшая их обработка

        self.max_shield = int(self.max_hp * (self.max_shield / 100))
        self.current_shield = self.max_shield
        self.size = 250
        self.file_image = os.getcwd() + "\\characters\\" + self.name + ".png" #спрайт
        self.image = pygame.image.load(self.file_image).convert_alpha()
        self.hp_x = 0
        self.hp_y = 0
        self.flag_shield = 1

    def change_image(self):
        self.image = pygame.image.load(self.file_image).convert_alpha() #изменение для "эволюции"

    def flip(self):
        self.image = pygame.transform.flip(self.image, True, False) #изменение ориентации спрайта

    def set_sprite(self): #приведение спрайта к нудному размеру
        scale = self.size / self.image.get_width()
        new_width = self.image.get_width() * scale
        new_height = self.image.get_height() * scale
        self.image = pygame.transform.scale(self.image, (new_width, new_height))

    def draw(self, alpha=255): #вывод спрайта
        sprite = self.image.copy()
        transparency = (255, 255, 255, alpha)
        sprite.fill(transparency, None, pygame.BLEND_RGBA_MULT)
        game.blit(sprite, (self.x, self.y))

    def get_rect(self):
        return Rect(self.x, self.y, self.image.get_width(), self.image.get_height())

    def draw_hp(self): #вывод здоровья и щита и доп информации
        bar_scale = 75 // self.max_hp
        pygame.draw.rect(game, white, (self.hp_x, self.hp_y, 150, 40))
        pygame.draw.rect(game, black, (self.hp_x, self.hp_y, 150, 40), 2)

        font = pygame.font.Font(pygame.font.get_default_font(), 12)
        text = font.render(self.name, True, (0, 0, 0, 0))
        text_rect = text.get_rect()
        text_rect.x = self.hp_x + 5
        text_rect.y = self.hp_y + 5
        game.blit(text, text_rect)

        font = pygame.font.Font(pygame.font.get_default_font(), 12)
        text = font.render("Lv." + str(self.level), True, (0, 0, 0, 0))
        text_rect = text.get_rect()
        text_rect.x = self.hp_x + 110
        text_rect.y = self.hp_y + 5
        game.blit(text, text_rect)

        font = pygame.font.Font(pygame.font.get_default_font(), 10)
        text = font.render(f"HP:{self.current_hp}/{self.max_hp}", True, (0, 0, 0, 0))
        text_rect = text.get_rect()
        text_rect.x = self.hp_x + 5
        text_rect.y = self.hp_y + 25
        game.blit(text, text_rect)

        for i in range(self.max_hp):
            bar = (self.hp_x + 70 + bar_scale * i, self.hp_y + 25, bar_scale, 7)
            pygame.draw.rect(game, red, bar)
        for i in range(self.current_hp):
            bar = (self.hp_x + 70 + bar_scale * i, self.hp_y + 25, bar_scale, 7)
            pygame.draw.rect(game, green, bar)
        pygame.draw.rect(game, black, (self.hp_x + 70, self.hp_y + 25, bar_scale * self.max_hp, 7), 1)

        if self.max_shield != 0:
            bar_scale = 75 // self.max_shield
            for i in range(self.max_shield):
                bar = (self.hp_x + 70 + bar_scale * i, self.hp_y + 20, bar_scale, 3)
                pygame.draw.rect(game, red, bar)
            for i in range(self.current_shield):
                bar = (self.hp_x + 70 + bar_scale * i, self.hp_y + 20, bar_scale, 3)
                pygame.draw.rect(game, green, bar)
            pygame.draw.rect(game, (128, 166, 255), (self.hp_x + 70, self.hp_y + 20, bar_scale * self.max_shield, 3), 1)

    def use_medkit(self): #функция лечения
        self.current_hp += 30
        if self.current_hp > self.max_hp:
            self.current_hp = self.max_hp
        self.medkit -= 1

    def take_damage(self, damage): #урон

        if self.current_shield > 0:
            self.current_shield -= damage
            if self.current_shield < 0:
                self.current_shield = 0
            self.flag_shield = 0

        else:
            self.current_hp -= damage
            if self.current_hp < 0:
                self.current_hp = 0

    def perform_attack(self, other, move): #выполнение движения

        display_message(f'{self.name} used {move.name}')
        time.sleep(2)
        damage = (2 * self.level + 10) / 250 * self.attack / other.defense * move.power

        if move.type == "explosive":
            damage *= 1.5
        if move.type == "energy" and other.current_shield > 0:
            damage *= 1, 5
        elif move.type == "physical" and other.current_shield == 0:
            damage *= 1.5

        random_num = random.randint(1, 10000)
        if random_num <= 625:
            damage *= 1.5
        damage = math.floor(damage)
        other.take_damage(damage)


def display_message(message): #вывод сообщения и рамки к нему
    pygame.draw.rect(game, white, (0, 370, 500, 130))
    pygame.draw.rect(game, (0, 0, 0, 0), (0, 370, 500, 130), 3)

    font = pygame.font.Font(pygame.font.get_default_font(), 20)
    text = font.render(message, True, (0, 0, 0, 0))
    text_rect = text.get_rect()
    text_rect.x = 20
    text_rect.y = 400
    game.blit(text, text_rect)

    pygame.display.update()


def create_button(width, height, left, top, text_cx, text_cy, label): #создание кнопки
    # position of the mouse cursor
    mouse_cursor = pygame.mouse.get_pos()

    button = Rect(left, top, width, height)

    if button.collidepoint(mouse_cursor):
        pygame.draw.rect(game, gold, button)
    else:
        pygame.draw.rect(game, white, button)

    font = pygame.font.Font(pygame.font.get_default_font(), 16)
    text = font.render(f'{label}', True, black)
    text_rect = text.get_rect(center=(text_cx, text_cy))
    game.blit(text, text_rect)

    return button


game_width = 500
game_height = 500
size = (game_width, game_height)
game = pygame.display.set_mode(size)
pygame.display.set_caption('Battle')
bg_imges = {}
for i in os.listdir(os.getcwd() + "\\backgrounds"): #преобразование всх задников
    bg_img = pygame.image.load(os.getcwd() + "\\backgrounds\\" + i)
    bg_img = pygame.transform.scale(bg_img, (game_width, game_height))
    bg_imges[i[:i.find(".")]] = bg_img

character = Character("odst", 1, 0, 100, ["assault rifle", "frag grenade", "shotgun", "magnum"])
character.set_sprite() #создание персонажа и приведение в нужный размер спрайта

character1 = Character("sangheili minor", 1, 250, 100, ["energy sword", "energy grenade", "needler", "energy rifle"])
character1.set_sprite()
character1.flip()
opponent = Character(random.sample(all_names, 1)[0], 1, 250, 120)
opponent.set_sprite()
opponent.flip() #создание оппонента
opponent.moves.append(1)

characters_list = [character, character1]
flag = 0 #флаг поражения
game_status = "start_menu"
pygame.mixer.music.load(os.getcwd() + "\\music\\" + game_status + ".mp3")
pygame.mixer.music.play(-1) #запуск музыки
while game_status != 'quit':
    for event in pygame.event.get():
        if event.type == QUIT: #обработка событий
            game_status = 'quit'
        if event.type == KEYDOWN and game_status == '?':

            if event.key == K_y: #продолжение игры

                opponent = Character(random.sample(all_names, 1)[0], player.level, 250, 120)
                opponent.set_sprite()
                opponent.flip()
                opponent.moves.append(1)
                game_status = "pre battle"

            elif event.key == K_n: #выход из игры
                game_status = 'quit'

        if event.type == MOUSEBUTTONDOWN: #обработка мыши
            mouse_click = event.pos
            if game_status == 'select': #выбор бойца
                for i in range(len(characters_list)):
                    if characters_list[i].get_rect().collidepoint(mouse_click):
                        if i == 1:
                            player = characters_list[i]
                            player.flip()
                        else:
                            player = characters_list[i]
                        game_status = 'pre battle'
                        pygame.mixer.music.load(os.getcwd() + "\\music\\" + game_status + ".mp3")
                        pygame.mixer.music.play(-1)

            elif game_status == 'player turn': #выбор действие или медицина

                if fight_button.collidepoint(mouse_click):
                    game_status = 'player move'

                if medkit_button.collidepoint(mouse_click):

                    if player.medkit == 0:
                        display_message('No more medkit left')
                        time.sleep(2)
                        game_status = 'player move'
                    else:
                        player.use_medkit()
                        display_message(f'{player.name} used medkit')
                        if opponent.flag_shield == 0: #восстановление щита противника
                            opponent.current_shield = opponent.max_shield
                        time.sleep(2)
                        game_status = 'opponent turn'

            elif game_status == "start_menu": #обработка кнопки в меню
                if start_button.collidepoint(mouse_click):
                    game_status = 'select'

            elif game_status == 'player move': #выбор действия
                for i in range(len(move_buttons)):
                    button = move_buttons[i]

                    if button.collidepoint(mouse_click):
                        move = player.moves[i]
                        player.perform_attack(opponent, move)
                        if opponent.current_hp == 0:
                            game_status = 'fainted'
                        else:
                            game_status = 'opponent turn'

    if game_status == 'select': #окно выбора
        game.blit(bg_imges[game_status], (0, 0))
        character.draw()
        character1.draw()
        mouse_cursor = pygame.mouse.get_pos()
        for i in characters_list:
            if i.get_rect().collidepoint(mouse_cursor):
                pygame.draw.rect(game, (0, 0, 0), i.get_rect(), 2)
        display_message("Choose your fighter")
        pygame.display.update()

    if game_status == 'pre battle':
        game.blit(bg_imges[game_status], (0, 0))
        player.x, player.y = 40, 90
        opponent.x, opponent.y = 210, 0
        player.hp_x = 270
        player.hp_y = 250
        opponent.hp_x = 50
        opponent.hp_y = 30
        alpha = 0
        while alpha < 255:
            game.blit(bg_imges[game_status], (0, 0))
            opponent.draw(alpha)
            display_message(f'You meet {opponent.name}!')
            alpha += 2
            pygame.display.update()
        alpha = 0
        while alpha < 255:
            game.blit(bg_imges[game_status], (0, 0))
            opponent.draw()
            player.draw(alpha)
            display_message(f"I go to kill you, {opponent.name}!")
            alpha += 2

            pygame.display.update()
        if player.speed >= opponent.speed:
            game_status = 'player turn'
        else:
            game_status = 'opponent turn'
        pygame.display.update()

    if game_status == "player turn":
        game.blit(bg_imges["pre battle"], (0, 0))
        player.draw()
        player.draw_hp()
        opponent.draw()
        opponent.draw_hp()
        fight_button = create_button(250, 130, 0, 370, 125, 435, 'Fight')
        medkit_button = create_button(250, 130, 250, 370, 365, 435, f'Use Medkit ({player.medkit})')
        pygame.draw.rect(game, black, (0, 370, 500, 130), 2)

        pygame.display.update()

    if game_status == 'player move':
        game.blit(bg_imges["pre battle"], (0, 0))
        player.draw()
        opponent.draw()
        player.draw_hp()
        opponent.draw_hp()

        move_buttons = []
        for i in range(len(player.moves)):
            move = player.moves[i]
            button_width = 250
            button_height = 65
            left = i % 2 * button_width
            top = 370 + i // 2 * button_height
            text_center_x = left + 120
            text_center_y = top + 35
            button = create_button(button_width, button_height, left, top, text_center_x, text_center_y,
                                   move.name.capitalize())
            move_buttons.append(button)

        pygame.draw.rect(game, black, (0, 370, 500, 130), 3)

        pygame.display.update()

    if game_status == 'opponent turn':
        game.blit(bg_imges["pre battle"], (0, 0))
        player.draw()
        opponent.draw()
        player.draw_hp()
        opponent.draw_hp()
        display_message('...')
        time.sleep(2)
        move = random.choice(opponent.moves)
        if move == 1 and opponent.medkit > 0:
            opponent.use_medkit()
            display_message(f"{opponent.name} used medkit")
            if opponent.medkit == 0:
                opponent.moves.pop(-1)
            if player.max_shield > 0:
                player.current_shield = player.max_shield
            time.sleep(2)
        else:
            opponent.perform_attack(player, move)
        if player.current_hp == 0:
            game_status = 'fainted'
        else:
            game_status = 'player turn'
        pygame.display.update()

    if game_status == 'fainted':
        alpha = 255
        while alpha > 0:
            game.blit(bg_imges["pre battle"], (0, 0))
            player.draw_hp()
            opponent.draw_hp()
            if opponent.current_hp == 0:
                player.draw()
                opponent.draw(alpha)
                display_message(f'{opponent.name} fainted!')
                flag = 1
            else:
                player.draw(alpha)
                opponent.draw()
                display_message(f'{player.name} fainted!')
                flag = 0
            alpha -= 2

            pygame.display.update()
        if flag == 0:
            game_status = 'gameover'
        else:
            game_status = 'battleover'

        if game_status == 'gameover':
            game.blit(bg_imges[game_status], (0, 0))
            display_message("Game over")
            time.sleep(5)
            game_status = "start_menu"

        if game_status == 'battleover':
            flag_stop = 0
            flag_ev = 0
            player.level += 1
            if player.level == 6:
                if player.name == "spartan":
                    game_status = "cortana"
                else:
                    game_status = "arbiter"
                flag_stop = 1
            if player.name == "odst" and player.level == 4:
                player.file_image = os.getcwd() + "\\characters\\spartan.png"
                player.change_image()
                player.set_sprite()
                display_message(f"{player.name} turning into spartan")
                player.name = "spartan"
                flag_ev = 1
            elif player.name == "sangheili minor" and player.level == 2:
                player.file_image = os.getcwd() + "\\characters\\sangheili major.png"
                player.change_image()
                player.set_sprite()
                display_message(f"{player.name} turning into sangheili major")
                player.name = "sangheili major"
                flag_ev = 1
            elif player.name == "sangheili major" and player.level == 4:
                player.file_image = os.getcwd() + "\\characters\\sangheili general.png"
                player.change_image()
                player.set_sprite()
                display_message(f"{player.name} turning into sangheili  general")
                player.name = "sangheili general"
                flag_ev = 1
            if flag_ev == 1:
                file = os.getcwd() + "\\stats.xml"
                characters = etree.parse(file)
                characters = etree.tostring(characters)
                characters = etree.fromstring(characters)
                for character in characters:
                    if character.get("name") == player.name:
                        for stat in character:
                            if stat.tag == "hp":
                                player.base_hp = int(stat.text)
                            elif stat.tag == "attack":
                                player.base_attack = int(stat.text)
                            elif stat.tag == "defense":
                                player.base_defense = int(stat.text)
                            elif stat.tag == "speed":
                                player.base_speed = int(stat.text)
                            elif stat.tag == "shield":
                                player.max_shield = int(stat.text)
                flag_ev = 0
            player.attack = math.floor(0.01 * (2 * player.base_attack + player.IV_attack * player.level) + 5)
            player.defense = math.floor(0.01 * (2 * player.base_defense + player.IV_defense * player.level) + 5)
            player.speed = math.floor(0.01 * (2 * player.base_speed + player.IV_speed * player.level) + 5)
            player.max_hp = math.floor(
                ((2 * int(player.base_hp) + player.IV_hp * player.level) / 100) + player.level + 10)
            player.current_hp = player.max_hp
            player.max_shield = 2 + player.max_shield
            player.current_shield = player.max_shield
            player.medkit = 3
            player.flag_shield = 1
            if flag_stop == 0:
                game_status = "?"
            game.blit(bg_imges["pre battle"], (0, 0))
            player.draw_hp()
            opponent.draw_hp()
            player.draw()
            time.sleep(2)

    if game_status == "?":
        display_message('Do you want to continue(Y/N)?')

    if game_status == "cortana":
        game.blit(bg_imges["menu"], (0, 0))
        cortana = Character("odst", 1, 40, 10)
        cortana.file_image = os.getcwd() + "\\characters\\cortana.png"
        cortana.size = 400
        cortana.change_image()
        cortana.set_sprite()
        cortana.draw()
        display_message(f"""Congratulations {player.name}. Simulation is over!""")
        pygame.display.update()
        time.sleep(5)
        game_status = "start_menu"

    if game_status == "arbiter":
        game.blit(bg_imges["menu"], (0, 0))
        cortana = Character("odst", 1, 40, 10)
        cortana.file_image = os.getcwd() + "\\characters\\arbiter.png"
        cortana.size = 400
        cortana.change_image()
        cortana.set_sprite()
        cortana.draw()
        display_message(f"""Congratulations brother. Simulation is over!""")
        pygame.display.update()
        time.sleep(5)
        game_status = "start_menu"

    if game_status == "start_menu":
        game.blit(bg_imges["menu"], (0, 0))
        font = pygame.font.Font(pygame.font.get_default_font(), 40)
        title = font.render('Halomom', True, (255, 255, 255))
        game.blit(title, (240, 30))
        start_button = create_button(150, 30, 250, 100, 325, 115, 'Finish the fight')
        pygame.display.update()
        character = Character("odst", 1, 0, 100, ["assault rifle", "frag grenade", "shotgun", "magnum"])
        character.set_sprite()

        character1 = Character("sangheili minor", 1, 250, 100,
                               ["energy sword", "energy grenade", "needler", "energy rifle"])
        character1.set_sprite()
        character1.flip()
        opponent = Character(random.sample(all_names, 1)[0], 1, 250, 120)
        opponent.set_sprite()
        opponent.flip()
        opponent.moves.append(1)

        characters_list = [character, character1]

pygame.quit()
