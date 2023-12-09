import pygame
from pygame.locals import *
import math
import random
from lxml import etree
import os

pygame.init()
#создание списка всех видов движений
all_moves = {}
file = os.getcwd() + "\\moves.xml"
moves = etree.parse(file)
moves = etree.tostring(moves)
moves = etree.fromstring(moves)
for move in moves:
    for stat in move:
        if stat.tag == "type":
            type = stat.text
        elif stat.tag == "category":
            category = stat.text
        elif stat.tag == "power":
            power = int(stat.text)
        elif stat.tag == "accuracy":
            accuracy = int(stat.text)
        elif stat.tag == "pp":
            pp = int(stat.text)
    all_moves[move.get("name")] = {"type": type, "category": category, "power": power, "accuracy": accuracy, "pp": pp}

#создание списка всех видов персонажей
file = os.getcwd() + "\\stats.xml"
characters = etree.parse(file)
characters = etree.tostring(characters)
characters = etree.fromstring(characters)
base_characters = {}
for character in characters:
    for stat in character:
        if stat.tag == "hp":
            base_hp = int(stat.text)
        elif stat.tag == "attack":
            base_attack = int(stat.text)
        elif stat.tag == "defense":
            base_defense = int(stat.text)
        elif stat.tag == "speed":
            base_speed = int(stat.text)
        elif stat.tag == "shield":
            base_shield = int(stat.text)
        elif stat.tag == "evolution":
            evolution = stat.text
        elif stat.tag == "ev_lvl":
            ev_lvl = int(stat.text)
        elif stat.tag == "type":
            type = stat.text
    base_characters[character.get("name")] = {"base_hp": base_hp, "base_attack":base_attack, "base_defense":base_defense, "base_speed": base_speed, "base_shield": base_shield, "evolution": evolution, "ev_lvl": ev_lvl, "type": type}

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
        self.type = all_moves[name]["type"]
        self.category = all_moves[name]["category"]
        self.power = all_moves[name]["power"]
        self.accuracy = all_moves[name]["accuracy"]
        self.pp = all_moves[name]["pp"]
        self.cur_pp = self.pp

#класс персонажа(игрового и npc)

class Character(pygame.sprite.Sprite):

    def __init__(self, name, level, x, y, moves=random.sample(list(all_moves.keys()), 4)):

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
        self.max_hp = math.floor(((2 * base_characters[name]["base_hp"] + self.IV_hp * self.level) / 100) + self.level + 10)
        self.current_hp = self.max_hp
        self.attack = math.floor(0.01 * (2 * base_characters[name]["base_attack"] + self.IV_attack * self.level) + 5)
        self.defense = math.floor(0.01 * (2 * base_characters[name]["base_defense"] + self.IV_defense * self.level) + 5)
        self.speed = math.floor(0.01 * (2 * base_characters[name]["base_speed"] + self.IV_speed * self.level) + 5)
        self.max_shield = int(self.max_hp * (base_characters[name]["base_shield"] / 100))
        self.current_shield = self.max_shield
        self.evolution = base_characters[name]["evolution"]
        self.ev_lvl = base_characters[name]["ev_lvl"]
        self.size = 250
        self.image = ch_images[name]
        self.hp_x = 0
        self.hp_y = 0
        self.type = base_characters[name]["type"]
        self.flag_shield = 1

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
            bar = (self.hp_x + 70 + bar_scale * i, self.hp_y + 27, bar_scale, 7)
            pygame.draw.rect(game, red, bar)
        for i in range(self.current_hp):
            bar = (self.hp_x + 70 + bar_scale * i, self.hp_y + 27, bar_scale, 7)
            pygame.draw.rect(game, green, bar)
        pygame.draw.rect(game, black, (self.hp_x + 70, self.hp_y + 27, bar_scale * self.max_hp, 7), 1)

        if self.max_shield != 0:
            bar_scale = 75 // self.max_shield
            for i in range(self.max_shield):
                bar = (self.hp_x + 70 + bar_scale * i, self.hp_y + 20, bar_scale, 5)
                pygame.draw.rect(game, grey, bar)
            for i in range(self.current_shield):
                bar = (self.hp_x + 70 + bar_scale * i, self.hp_y + 20, bar_scale, 5)
                pygame.draw.rect(game, (128, 166, 255), bar)
            pygame.draw.rect(game, black, (self.hp_x + 70, self.hp_y + 20, bar_scale * self.max_shield, 5), 1)

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
        pygame.time.wait(2000)
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
game = pygame.display.set_mode((game_width, game_height))
pygame_icon = pygame.image.load(os.getcwd() + "\\icon.jpeg")
pygame.display.set_icon(pygame_icon)
pygame.display.set_caption('Halomon')
bg_images = {}
for i in os.listdir(os.getcwd() + "\\backgrounds"): #преобразование всх задников
    bg_img = pygame.image.load(os.getcwd() + "\\backgrounds\\" + i).convert_alpha()
    bg_img = pygame.transform.scale(bg_img, (game_width, game_height))
    bg_images[i[:i.find(".")]] = bg_img
ch_images = {}
for i in os.listdir(os.getcwd() + "\\characters"): #преобразование всх задников
    ch_img = pygame.image.load(os.getcwd() + "\\characters\\" + i).convert_alpha()
    ch_img = pygame.transform.scale(ch_img, (250, 250))
    ch_images[i[:i.find(".")]] = ch_img


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

                opponent = Character(random.choice(list(base_characters.keys())), player.level, 250, 120)
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
                        pygame.time.wait(2000)
                        game_status = 'player move'
                    else:
                        player.use_medkit()
                        display_message(f'{player.name} used medkit')
                        if opponent.flag_shield == 0: #восстановление щита противника
                            opponent.current_shield = opponent.max_shield
                        pygame.time.wait(2000)
                        game_status = 'opponent turn'

            elif game_status == "start_menu": #обработка кнопки в меню
                if start_button.collidepoint(mouse_click):
                    character = Character("odst", 1, 0, 100, ["assault rifle", "frag grenade", "shotgun", "magnum"])
                    character.set_sprite()

                    character1 = Character("sangheili minor", 1, 250, 100,
                                           ["energy sword", "energy grenade", "needler", "energy rifle"])
                    character1.set_sprite()
                    character1.flip()
                    opponent = Character(random.choice(list(base_characters.keys())), 1, 250, 120)
                    opponent.set_sprite()
                    opponent.flip()
                    opponent.moves.append(1)
                    print(opponent.moves)
                    characters_list = [character, character1]
                    game_status = 'select'
                elif quit_button.collidepoint(mouse_click):
                    game_status = "quit"

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
        game.blit(bg_images[game_status], (0, 0))
        character.draw()
        character1.draw()
        mouse_cursor = pygame.mouse.get_pos()
        for i in characters_list:
            if i.get_rect().collidepoint(mouse_cursor):
                pygame.draw.rect(game, (0, 0, 0), i.get_rect(), 2)
        display_message("Choose your fighter")
        pygame.display.update()

    if game_status == 'pre battle':
        game.blit(bg_images[game_status], (0, 0))
        player.x, player.y = 40, 90
        opponent.x, opponent.y = 210, 0
        player.hp_x = 270
        player.hp_y = 250
        opponent.hp_x = 50
        opponent.hp_y = 30
        alpha = 0
        while alpha < 255:
            game.blit(bg_images[game_status], (0, 0))
            opponent.draw(alpha)
            display_message(f'You meet {opponent.name}!')
            alpha += 2
            pygame.display.update()
        alpha = 0
        while alpha < 255:
            game.blit(bg_images[game_status], (0, 0))
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
        player.draw()
        player.draw_hp()
        opponent.draw()
        opponent.draw_hp()
        fight_button = create_button(250, 130, 0, 370, 125, 435, 'Fight')
        medkit_button = create_button(250, 130, 250, 370, 365, 435, f'Use Medkit ({player.medkit})')
        pygame.draw.rect(game, black, (0, 370, 500, 130), 2)

        pygame.display.update()

    if game_status == 'player move':
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
        player.draw_hp()
        opponent.draw_hp()
        display_message('...')
        pygame.time.wait(2000)
        move = random.choice(opponent.moves)
        if move == 1 and opponent.medkit > 0:
            opponent.use_medkit()
            display_message(f"{opponent.name} used medkit")
            if opponent.medkit == 0:
                opponent.moves.pop(-1)
            if player.max_shield > 0:
                player.current_shield = player.max_shield
            pygame.time.wait(2000)
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
            game.blit(bg_images[game_status], (0, 0))
            display_message("Game over")
            pygame.time.wait(5000)
            game_status = "start_menu"

        if game_status == 'battleover':
            player.level += 1
            if player.level == 6:
                if player.type == "uncs":
                    game_status = "cortana"
                elif player.type == "covenant":
                    game_status = "arbiter"
            else:
                game_status = "?"
            if player.ev_lvl == player.level:
                player.name = player.evolution
                player.image = ch_images[player.name]
                player.set_sprite()
                display_message(f"{player.name} turning into {player.evolution}")

            player.attack = math.floor(0.01 * (2 * base_characters[player.name]["base_attack"] + player.IV_attack * player.level) + 5)
            player.defense = math.floor(0.01 * (2 * base_characters[player.name]["base_defense"] + player.IV_defense * player.level) + 5)
            player.speed = math.floor(0.01 * (2 * base_characters[player.name]["base_speed"] + player.IV_speed * player.level) + 5)
            player.max_hp = math.floor(((2 * base_characters[player.name]["base_hp"] + player.IV_hp * player.level) / 100) + player.level + 10)
            player.current_hp = player.max_hp
            player.max_shield = player.level + int(player.max_hp * (base_characters[player.name]["base_shield"] / 100))
            player.current_shield = player.max_shield
            player.medkit = 3
            player.flag_shield = 1
            player.draw_hp()
            opponent.draw_hp()
            player.draw()
            pygame.time.wait(5000)
            pygame.display.update()

    if game_status == "?":
        display_message('Do you want to continue(Y/N)?')

    if game_status == "cortana":
        game.blit(bg_images["menu"], (0, 0))
        cortana = Character("odst", 1, 40, 10)
        cortana.size = 400
        cortana.image = ch_images[game_status]
        cortana.set_sprite()
        cortana.draw()
        display_message(f"""Congratulations {player.name}. Simulation is over!""")
        pygame.display.update()
        pygame.time.wait(5000)
        game_status = "start_menu"

    if game_status == "arbiter":
        game.blit(bg_images["menu"], (0, 0))
        arbiter = Character("odst", 1, 40, 10)
        arbiter.size = 400
        arbiter.image = ch_images[game_status]
        arbiter.set_sprite()
        arbiter.draw()
        display_message(f"""Congratulations brother. Simulation is over!""")
        pygame.display.update()
        pygame.time.wait(5000)
        game_status = "start_menu"

    if game_status == "start_menu":
        game.blit(bg_images["menu"], (0, 0))
        font = pygame.font.Font(pygame.font.get_default_font(), 40)
        title = font.render('Halomon', True, (255, 255, 255))
        game.blit(title, (235, 30))
        start_button = create_button(150, 30, 250, 80, 325, 95, 'Finish the fight')
        quit_button = create_button(150, 30, 250, 120, 325, 135, 'Quit')
        pygame.display.update()

pygame.quit()
