import pygame
from pygame.locals import *
import math
import random
from lxml import etree
import os

pygame.init()
clock = pygame.time.Clock()
# создание списка всех видов движений
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

# создание списка всех видов персонажей
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
        elif stat.tag == "sp_attack":
            sp_attack = int(stat.text)
        elif stat.tag == "sp_defense":
            sp_defense = int(stat.text)
    base_characters[character.get("name")] = {"base_hp": base_hp, "base_attack": base_attack,
                                              "base_defense": base_defense, "base_speed": base_speed,
                                              "base_shield": base_shield, "evolution": evolution, "ev_lvl": ev_lvl,
                                              "type": type, "base_sp_defense": sp_defense, "base_sp_attack": sp_attack}
potion_buttons_name = ["Attack+", "Defense+", "HP+", "Return"]
# создание шаблонов для цвета
black = (0, 0, 0)
gold = (218, 165, 32)
grey = (200, 200, 200)
green = (0, 200, 0)
red = (200, 0, 0)
white = (255, 255, 255)


# класс для движений
class Move:

    def __init__(self, name):
        self.name = name
        self.type = all_moves[name]["type"]
        self.category = all_moves[name]["category"]
        self.power = all_moves[name]["power"]
        self.accuracy = all_moves[name]["accuracy"]
        self.pp = all_moves[name]["pp"]
        self.cur_pp = self.pp


class Map:

    def __init__(self, background, music=0):
        self.music = music
        self.background = background

    def set_map(self):
        game.blit(bg_images[self.background], (0, 0))
        pygame.display.update()
        pygame.mixer.music.load(os.getcwd() + "\\music\\" + self.music + ".mp3")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

    def set(self):
        game.blit(bg_images[self.background], (0, 0))


# класс персонажа(игрового и npc)

class Character(pygame.sprite.Sprite):

    def __init__(self, name, level, x, y, moves=random.sample(list(all_moves.keys()), 3)):

        pygame.sprite.Sprite.__init__(self)

        self.name = name
        self.level = level
        self.x = x
        self.y = y
        self.moves = []
        self.favorite_weapon = {}
        for i in moves:
            move = Move(i)
            self.moves.append(move)
            self.favorite_weapon[move.name] = 0
        self.medkit = 2
        self.poition_of_attack = 2
        self.poition_of_defense = 2
        self.IV_hp = random.randint(0, 31)
        self.IV_attack = random.randint(0, 31)
        self.IV_defense = random.randint(0, 31)
        self.IV_sp_attack = random.randint(0, 31)
        self.IV_sp_defense = random.randint(0, 31)
        self.IV_speed = random.randint(0, 31)
        self.max_hp = math.floor(
            ((2 * base_characters[name]["base_hp"] + self.IV_hp * self.level) / 100) + self.level + 10)
        self.current_hp = self.max_hp
        self.attack = math.floor(0.01 * (2 * base_characters[name]["base_attack"] + self.IV_attack * self.level) + 5)
        self.current_attack = self.attack
        self.defense = math.floor(0.01 * (2 * base_characters[name]["base_defense"] + self.IV_defense * self.level) + 5)
        self.current_defense = self.defense
        self.sp_attack = math.floor(
            0.01 * (2 * base_characters[name]["base_sp_attack"] + self.IV_sp_attack * self.level) + 5)
        self.current_sp_attack = self.sp_attack
        self.sp_defense = math.floor(
            0.01 * (2 * base_characters[name]["base_sp_defense"] + self.IV_sp_defense * self.level) + 5)
        self.current_sp_defense = self.sp_defense
        self.speed = math.floor(0.01 * (2 * base_characters[name]["base_speed"] + self.IV_speed * self.level) + 5)
        self.current_speed = self.speed
        self.max_shield = int(self.max_hp * (base_characters[name]["base_shield"] / 100))
        self.current_shield = self.max_shield
        self.evolution = base_characters[name]["evolution"]
        self.ev_lvl = base_characters[name]["ev_lvl"]
        self.size = 250
        self.image = ch_images[name]
        self.hp_x = 0
        self.hp_y = 0
        self.type = base_characters[name]["type"]
        if self.evolution != "no":
            self.evolution_image = ch_images[self.evolution]
        self.all_damage = 0

    def flip(self):
        self.image = pygame.transform.flip(self.image, True, False)  # изменение ориентации спрайта

    def set_sprite(self):  # приведение спрайта к нудному размеру
        scale = self.size / self.image.get_width()
        new_width = self.image.get_width() * scale
        new_height = self.image.get_height() * scale
        self.image = pygame.transform.scale(self.image, (new_width, new_height))

    def draw(self, ev=0, alpha=255):  # вывод спрайта
        if ev == 0:
            sprite = self.image.copy()
        elif ev == 1:
            sprite = self.evolution_image.copy()
        transparency = (255, 255, 255, alpha)
        sprite.fill(transparency, None, pygame.BLEND_RGBA_MULT)
        game.blit(sprite, (self.x, self.y))

    def get_rect(self):
        return Rect(self.x, self.y, self.image.get_width(), self.image.get_height())

    def draw_hp(self):  # вывод здоровья и щита и доп информации

        pygame.draw.rect(game, white, (self.hp_x, self.hp_y, 150, 45))
        pygame.draw.rect(game, black, (self.hp_x, self.hp_y, 150, 45), 2)

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
        text_rect.y = self.hp_y + 33
        game.blit(text, text_rect)

        bar_scale = self.current_hp / self.max_hp
        pygame.draw.rect(game, red, (self.hp_x + 70, self.hp_y + 33, 75, 7))
        pygame.draw.rect(game, green, (self.hp_x + 70, self.hp_y + 33, 75 * bar_scale, 7))
        pygame.draw.rect(game, black, (self.hp_x + 70, self.hp_y + 33, 75, 7), 1)
        if self.max_shield > 0:
            font = pygame.font.Font(pygame.font.get_default_font(), 10)
            text = font.render(f"Shield:{self.current_shield}/{self.max_shield}", True, (0, 0, 0, 0))
            text_rect = text.get_rect()
            text_rect.x = self.hp_x + 5
            text_rect.y = self.hp_y + 21
            game.blit(text, text_rect)

            bar_scale = self.current_shield / self.max_shield
            pygame.draw.rect(game, grey, (self.hp_x + 70, self.hp_y + 26, 75, 5))
            pygame.draw.rect(game, (128, 166, 255), (self.hp_x + 70, self.hp_y + 26, 75 * bar_scale, 5))
            pygame.draw.rect(game, black, (self.hp_x + 70, self.hp_y + 26, 75, 5), 1)

    def use_medkit(self, tumblr=2):  # функция лечения
        heal_sound.play()
        if tumblr == 2:
            self.current_hp += 30
            if self.current_hp > self.max_hp:
                self.current_hp = self.max_hp
            self.medkit -= 1
        elif tumblr == 0:
            self.current_attack += 5
            self.poition_of_attack -= 1
        elif tumblr == 1:
            self.current_defense += 5
            self.poition_of_defense -= 1

    def take_damage(self, damage):  # урон

        if self.current_shield > 0:
            self.current_shield -= damage
            if self.current_shield < 0:
                self.current_shield = 0

        else:
            self.current_hp -= damage
            if self.current_hp < 0:
                self.current_hp = 0

    def perform_attack(self, other, move):  # выполнение движения
        if move.accuracy + (self.attack + self.speed) / (other.defense + other.speed) <= random.randint(1, 100):
            display_message(f'{self.name} used {move.name}')
            sounds[move.name].play()
            pygame.time.wait(2000)
            if other.current_shield != other.max_shield:  # восстановление щита противника
                other.current_shield = other.max_shield
            display_message(f'{self.name} miss')
            pygame.time.wait(2000)
            return 0
        damage = (2 * self.level + 10) / 250 * self.current_attack / other.current_defense * move.power
        if "explosive" in move.type:
            damage = (2 * self.level + 10) / 250 * self.current_sp_attack / other.current_sp_defense * move.power
        if "plasma" in move.type and other.current_shield > 0:
            damage *= 1.5
        elif "physical" in move.type and other.current_shield == 0:
            damage *= 1.5

        random_num = random.randint(1, 10000)
        if random_num <= 625:
            damage *= 1.5
        damage = math.floor(damage)
        display_message(f'{self.name} used {move.name}')
        sounds[move.name].play()
        alpha = 255
        while alpha < 255:
            game.blit(bg_images["pre battle" + type_of_map], (0, 0))
            transparency = (255, 255, 255, alpha)
            other.draw()
            other.draw_hp()
            self.draw()
            self.draw_hp()
            sprite = damage_image.copy()
            sprite.fill(transparency, None, pygame.BLEND_RGBA_MULT)
            game.blit(sprite, (other.x+50, other.y+50))
            display_message(f'{self.name} used {move.name}')
            alpha += 2
            pygame.display.update()
        alpha = 255
        while alpha > 2:
            game.blit(bg_images["pre battle" + type_of_map], (0, 0))
            transparency = (255, 255, 255, alpha)
            other.draw()
            other.draw_hp()
            self.draw()
            self.draw_hp()
            sprite = damage_image.copy()
            sprite.fill(transparency, None, pygame.BLEND_RGBA_MULT)
            game.blit(sprite, (other.x+50, other.y+50))
            display_message(f'{self.name} used {move.name}')
            alpha -= 2
            pygame.display.update()
        display_message(f"{other.name} take {damage} {move.category} damage")
        other.take_damage(damage)
        pygame.time.wait(2000)
        game.blit(bg_images["pre battle"+type_of_map], (0, 0))
        other.draw()
        self.draw()
        self.draw_hp()
        other.draw_hp()
        self.all_damage += damage
        self.favorite_weapon[move.name] += 1


def display_message(message):  # вывод сообщения и рамки к нему
    pygame.draw.rect(game, white, (0, 370, 500, 130))
    pygame.draw.rect(game, (0, 0, 0, 0), (0, 370, 500, 130), 3)

    font = pygame.font.Font(pygame.font.get_default_font(), 20)
    text = font.render(message, True, (0, 0, 0, 0))
    text_rect = text.get_rect()
    text_rect.x = 20
    text_rect.y = 400
    game.blit(text, text_rect)

    pygame.display.update()


def create_button(width, height, left, top, text_cx, text_cy, label):  # создание кнопки

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
pygame_icon = pygame.image.load(os.getcwd() + "\\icon.png")
pygame.display.set_icon(pygame_icon)
pygame.display.set_caption('Halomon')
bg_images = {}
maps = {}
damage_image = pygame.image.load(os.getcwd() + "\\damage.png").convert_alpha()
damage_image = pygame.transform.scale(damage_image, (150, 150))

for i in os.listdir(os.getcwd() + "\\backgrounds"):  # преобразование всх задников
    bg_img = pygame.image.load(os.getcwd() + "\\backgrounds\\" + i).convert_alpha()
    bg_img = pygame.transform.scale(bg_img, (game_width, game_height))
    bg_images[i[:i.find(".")]] = bg_img
    if i[:i.find(".")] + ".mp3" in os.listdir(os.getcwd() + "\\music"):
        maps[i[:i.find(".")]] = Map(i[:i.find(".")], i[:i.find(".")])
ch_images = {}
for i in os.listdir(os.getcwd() + "\\characters"):  # преобразование всх задников
    ch_img = pygame.image.load(os.getcwd() + "\\characters\\" + i).convert_alpha()
    ch_img = pygame.transform.scale(ch_img, (250, 250))
    ch_images[i[:i.find(".")]] = ch_img
sounds = {}
for i in os.listdir(os.getcwd() + "\\weapons sound"):
    sound = pygame.mixer.Sound(os.getcwd() + "\\weapons sound\\" + i)
    sounds[i[:i.find(".")]] = sound
openning = {}
for i in os.listdir(os.getcwd() + "\\introduction sound"):
    op = pygame.mixer.Sound(os.getcwd() + "\\introduction sound\\" + i)
    openning[i[:i.find(".")]] = op
heal_sound = pygame.mixer.Sound(os.getcwd() + "\\potion.mp3")

game_status = "start_menu"
maps[game_status].set_map()
font = pygame.font.Font(pygame.font.get_default_font(), 40)
title = font.render('Halomon', True, white)
game.blit(title, (250 - title.get_width() // 2, 150))
while game_status != 'quit':
    for event in pygame.event.get():
        if event.type == QUIT:  # обработка событий
            game_status = 'quit'
        if event.type == KEYDOWN and game_status == '?':

            if event.key == K_y:  # продолжение игры

                opponent = Character(random.choice(list(base_characters.keys())), player.level, 250, 120)
                opponent.set_sprite()
                opponent.flip()
                opponent.moves.append(1)
                game_status = "pre battle"
                type_of_map = str(random.randint(0, 2))
                maps[game_status + type_of_map].set_map()


            elif event.key == K_n:  # выход из игры
                game_status = 'end of game'
                maps[game_status].set_map()
                font = pygame.font.Font(pygame.font.get_default_font(), 40)
                title = font.render('Halomon', True, white)
                game.blit(title, (250 - title.get_width() // 2, 150))

        if event.type == MOUSEBUTTONDOWN:  # обработка мыши
            mouse_click = event.pos
            if game_status == 'select':  # выбор бойца
                for i in range(len(characters_list)):
                    if characters_list[i].get_rect().collidepoint(mouse_click):
                        if i == 1:
                            player = characters_list[i]
                            player.flip()
                        else:
                            player = characters_list[i]
                        game_status = 'pre battle'
                        type_of_map = str(random.randint(0, 2))
                        maps[game_status + type_of_map].set_map()

            elif game_status == 'player turn':  # выбор действие или медицина

                if fight_button.collidepoint(mouse_click):
                    total_pp = 0
                    for i in player.moves:
                        if i != "Return":
                            total_pp += i.cur_pp
                    if total_pp > 0:
                        game_status = 'player move_attack'
                    else:
                        sounds["melee"].play()
                        alpha = 0
                        while alpha < 255:
                            game.blit(bg_images["pre battle" + type_of_map], (0, 0))
                            transparency = (255, 255, 255, alpha)
                            opponent.draw()
                            opponent.draw_hp()
                            player.draw()
                            player.draw_hp()
                            sprite = damage_image.copy()
                            sprite.fill(transparency, None, pygame.BLEND_RGBA_MULT)
                            game.blit(sprite, (opponent.x + 50, opponent.y + 50))
                            display_message("Your hand go hard")
                            alpha += 3
                            pygame.display.update()
                        alpha = 255
                        while alpha > 2:
                            game.blit(bg_images["pre battle" + type_of_map], (0, 0))
                            transparency = (255, 255, 255, alpha)
                            opponent.draw()
                            opponent.draw_hp()
                            player.draw()
                            player.draw_hp()
                            sprite = damage_image.copy()
                            sprite.fill(transparency, None, pygame.BLEND_RGBA_MULT)
                            game.blit(sprite, (opponent.x + 50, opponent.y + 50))
                            display_message("Your hand go hard")
                            alpha -= 3
                            pygame.display.update()
                        opponent.current_shield = 0
                        damage = int((2 * player.level + 10) / 250 * player.current_attack / opponent.current_defense * 70)
                        player.all_damage += damage
                        opponent.current_hp -= damage
                        if opponent.current_hp <= 0:
                            opponent.current_hp = 0
                            game_status = 'fainted'
                            opponent.draw_hp()
                        else:
                            game_status = 'opponent turn'
                            opponent.draw_hp()
                        pygame.display.update()

                if potion_button.collidepoint(mouse_click):
                    game_status = 'player move_poition'

            elif game_status == "start_menu":  # обработка кнопки в меню
                if start_button.collidepoint(mouse_click):
                    character = Character("odst", 1, 0, 100, ["assault rifle", "frag grenade", "shotgun"])
                    character.moves.append("Return")
                    character.set_sprite()
                    character1 = Character("sangheili minor", 1, 250, 100,
                                           ["energy sword", "plasma grenade", "plasma rifle"])
                    character1.moves.append("Return")
                    character1.set_sprite()
                    character1.flip()
                    opponent = Character(random.choice(list(base_characters.keys())), 1, 250, 120)
                    opponent.set_sprite()
                    opponent.flip()
                    opponent.moves.append(1)
                    characters_list = [character, character1]
                    game_status = 'select'
                    maps[game_status].set_map()

                elif quit_button.collidepoint(mouse_click):
                    game_status = "quit"

            elif game_status == "end of game":
                # обработка кнопки в меню
                if main_menu_button.collidepoint(mouse_click):
                    game_status = 'start_menu'
                    maps[game_status].set()
                    font = pygame.font.Font(pygame.font.get_default_font(), 40)
                    title = font.render('Halomon', True, white)
                    game.blit(title, (250 - title.get_width() // 2, 150))

                elif quit_from_game_button.collidepoint(mouse_click):
                    game_status = "quit"

                elif results_button.collidepoint(mouse_click):
                    game_status = "results"
                    game.blit(bg_images["start_menu"], (0, 0))
                    font = pygame.font.Font(pygame.font.get_default_font(), 40)
                    title = font.render('Results', True, white)
                    game.blit(title, (250 - title.get_width() // 2, 150))
                    font = pygame.font.Font(pygame.font.get_default_font(), 20)
                    max_val = max(player.favorite_weapon.values())
                    for i in player.favorite_weapon.keys():
                        if player.favorite_weapon[i] == max_val:
                            fav = i
                    title = font.render(f'Favorite weapon: {fav}', True, white)
                    game.blit(title, (250 - title.get_width() // 2, 200))
                    font = pygame.font.Font(pygame.font.get_default_font(), 20)
                    title = font.render(f'Damage done: {player.all_damage}', True, white)
                    game.blit(title, (250 - title.get_width() // 2, 225))

            elif game_status == "results":  # обработка кнопки в меню
                if end_of_game_button.collidepoint(mouse_click):
                    game_status = 'start_menu'
                    maps[game_status].set()
                    font = pygame.font.Font(pygame.font.get_default_font(), 40)
                    title = font.render('Halomon', True, white)
                    game.blit(title, (250 - title.get_width() // 2, 150))
                elif quit_from_results_button.collidepoint(mouse_click):
                    game_status = "quit"

            elif game_status == 'player move_attack':  # выбор действия
                for i in range(len(move_buttons)):
                    button = move_buttons[i]
                    if button.collidepoint(mouse_click) and i != 3:
                        move = player.moves[i]
                        if move.cur_pp == 0:
                            display_message("Ammo is out")
                            pygame.time.wait(2000)
                            game_status = "player turn"
                        else:
                            player.perform_attack(opponent, move)
                            move.cur_pp -= 1
                            if opponent.current_hp == 0:
                                game_status = 'fainted'
                            else:
                                game_status = 'opponent turn'
                    elif button.collidepoint(mouse_click) and i == 3:
                        game_status = "player turn"
                opponent.draw_hp()
                player.draw_hp()


            elif game_status == 'player move_poition':  # выбор действия
                for i in range(len(potion_buttons)):
                    button = potion_buttons[i]
                    if button.collidepoint(mouse_click) and i == 0 and player.poition_of_attack == 0:
                        display_message(
                            f'No left poition of {potion_buttons_name[i]}')
                        game_status = "player turn"
                        pygame.time.wait(2000)
                    elif button.collidepoint(mouse_click) and i == 1 and player.poition_of_defense == 0:
                        display_message(
                            f'No left poition of {potion_buttons_name[i]}')
                        game_status = "player turn"
                        pygame.time.wait(2000)
                    elif button.collidepoint(mouse_click) and i == 2 and player.medkit == 0:
                        display_message(
                            f'No left poition of {potion_buttons_name[i]}')
                        game_status = "player turn"
                        pygame.time.wait(2000)
                    elif button.collidepoint(mouse_click) and i != 3:
                        if button.collidepoint(mouse_click) and i==2 and player.current_hp == player.max_hp:
                            display_message("Health is maximum")
                            pygame.time.wait(2000)
                            game_status = "player turn"
                        else:
                            if opponent.current_shield != opponent.max_shield:  # восстановление щита противника
                                opponent.current_shield = opponent.max_shield
                            display_message(f'{player.name} used potion of {potion_buttons_name[i]}')
                            player.use_medkit(i)
                            game_status = 'opponent turn'
                            opponent.draw_hp()
                            player.draw_hp()
                            pygame.time.wait(2000)
                    elif button.collidepoint(mouse_click) and i == 3:
                        game_status = "player turn"

    if game_status == 'select':
        maps[game_status].set()
        character.draw()
        character1.draw()
        # окно выбора
        mouse_cursor = pygame.mouse.get_pos()
        for i in characters_list:
            if i.get_rect().collidepoint(mouse_cursor):
                pygame.draw.rect(game, (0, 0, 0), i.get_rect(), 2)
        display_message("Choose your fighter")
        pygame.display.update()

    if game_status == 'pre battle':
        player.x, player.y = 40, 90
        opponent.x, opponent.y = 210, 0
        player.hp_x = 270
        player.hp_y = 250
        opponent.hp_x = 50
        opponent.hp_y = 30
        alpha = 0
        for i in openning.keys():
            if i in opponent.name:
                openning[i].play()
        while alpha < 255:
            game.blit(bg_images[game_status + type_of_map], (0, 0))
            opponent.draw(alpha=alpha)
            display_message(f'You meet {opponent.name}!')
            alpha += 1
            pygame.display.update()
        alpha = 0
        for i in openning.keys():
            if i in player.name:
                openning[i].play()
        while alpha < 255:
            game.blit(bg_images[game_status + type_of_map], (0, 0))
            opponent.draw()
            player.draw(alpha=alpha)
            display_message(f"I go to kill you, {opponent.name}!")
            alpha += 1
            pygame.display.update()
        if player.speed >= opponent.speed:
            game_status = 'player turn'
        else:
            game_status = 'opponent turn'
        player.draw_hp()
        opponent.draw_hp()

    if game_status == "player turn":
        fight_button = create_button(250, 130, 0, 370, 125, 435, 'Fight')
        potion_button = create_button(250, 130, 250, 370, 365, 435, "Potion")
        pygame.draw.rect(game, black, (0, 370, 500, 130), 2)
        pygame.draw.rect(game, black, (0, 370, 250, 130), 2)

        pygame.display.update()

    if game_status == 'player move_attack':
        move_buttons = []
        for i in range(len(player.moves)):
            move = player.moves[i]
            button_width = 250
            button_height = 65
            left = i % 2 * button_width
            top = 370 + i // 2 * button_height
            text_center_x = left + 120
            text_center_y = top + 35
            if i != 3:
                button = create_button(button_width, button_height, left, top, text_center_x, text_center_y,
                                       f"{move.name.capitalize()} {move.cur_pp}/{move.pp}")
            else:
                button = create_button(button_width, button_height, left, top, text_center_x, text_center_y,
                                       "Return")
            move_buttons.append(button)

        pygame.draw.rect(game, black, (0, 370, 500, 130), 2)
        pygame.draw.rect(game, black, (0, 370, 250, 130), 2)
        pygame.draw.rect(game, black, (0, 370, 500, 65), 2)

        pygame.display.update()

    if game_status == 'player move_poition':
        potion_buttons = []
        for i in range(4):
            button_width = 250
            button_height = 65
            left = i % 2 * button_width
            top = 370 + i // 2 * button_height
            text_center_x = left + 120
            text_center_y = top + 35
            if i == 0:
                button = create_button(button_width, button_height, left, top, text_center_x, text_center_y,
                                       f"{potion_buttons_name[i]}({player.poition_of_attack})")
            elif i == 1:
                button = create_button(button_width, button_height, left, top, text_center_x, text_center_y,
                                       f"{potion_buttons_name[i]}({player.poition_of_defense})")
            elif i == 2:
                button = create_button(button_width, button_height, left, top, text_center_x, text_center_y,
                                       f"{potion_buttons_name[i]}({player.medkit})")
            elif i == 3:
                button = create_button(button_width, button_height, left, top, text_center_x, text_center_y,
                                       f"Return")
            potion_buttons.append(button)

        pygame.draw.rect(game, black, (0, 370, 500, 130), 2)
        pygame.draw.rect(game, black, (0, 370, 250, 130), 2)
        pygame.draw.rect(game, black, (0, 370, 500, 65), 2)

        pygame.display.update()

    if game_status == 'opponent turn':
        display_message('...')
        pygame.time.wait(2000)
        move = random.choice(opponent.moves)
        if move == 1 and opponent.medkit > 0 and opponent.current_hp != opponent.max_hp:
            opponent.use_medkit()
            display_message(f"{opponent.name} used medkit")
            if opponent.medkit == 0:
                opponent.moves.pop(-1)
            if player.max_shield > 0:
                player.current_shield = player.max_shield
            pygame.time.wait(2000)
        else:
            total_pp = 0
            if 1 in opponent.moves:
                opponent.moves.pop(opponent.moves.index(1))
            move = random.choice(opponent.moves)
            for i in opponent.moves:
                total_pp += i.cur_pp
            print(opponent.moves)
            if total_pp > 0:
                while move.cur_pp == 0:
                    move = random.choice(opponent.moves)
                    print(move)
                opponent.moves.append(1)
                opponent.perform_attack(player, move)
                move.cur_pp -= 1
            else:
                sounds["melee"].play()
                alpha = 0
                while alpha < 255:
                    game.blit(bg_images["pre battle" + type_of_map], (0, 0))
                    transparency = (255, 255, 255, alpha)
                    player.draw()
                    player.draw_hp()
                    opponent.draw()
                    opponent.draw_hp()
                    sprite = damage_image.copy()
                    sprite.fill(transparency, None, pygame.BLEND_RGBA_MULT)
                    game.blit(sprite, (player.x + 50, player.y + 50))
                    display_message("His hand go hard")
                    alpha += 3
                    pygame.display.update()
                alpha = 255
                while alpha > 2:
                    game.blit(bg_images["pre battle" + type_of_map], (0, 0))
                    transparency = (255, 255, 255, alpha)
                    player.draw()
                    player.draw_hp()
                    opponent.draw()
                    opponent.draw_hp()
                    sprite = damage_image.copy()
                    sprite.fill(transparency, None, pygame.BLEND_RGBA_MULT)
                    game.blit(sprite, (player.x + 50, player.y + 50))
                    display_message("His hand go hard")
                    alpha -= 3
                    pygame.display.update()
                player.current_shield = 0
                player.current_hp -= int(
                    (2 * opponent.level + 10) / 250 * opponent.current_attack / player.current_defense * 70)
        if player.current_hp <= 0:
            player.current_hp = 0
            game_status = 'fainted'
        else:
            game_status = 'player turn'
        player.draw_hp()
        opponent.draw_hp()
        pygame.display.update()

    if game_status == 'fainted':
        alpha = 255
        while alpha > 0:
            game.blit(bg_images["pre battle" + type_of_map], (0, 0))
            if opponent.current_hp <= 0:
                player.draw()
                opponent.draw(alpha=alpha)
                display_message(f'{opponent.name} fainted!')
            else:
                opponent.draw()
                player.draw(alpha=alpha)
                display_message(f'{player.name} fainted!')
            alpha -= 1
            pygame.display.update()
        if opponent.current_hp == 0:
            game_status = 'battleover'
        else:
            game_status = 'gameover'
        pygame.time.wait(2000)

        if game_status == 'gameover':
            game.blit(bg_images[game_status], (0, 0))
            display_message("Game over")
            pygame.time.wait(5000)
            game_status = "end of game"
            maps[game_status].set_map()

        if game_status == 'battleover':
            player.level += 1
            game_status = "?"
            if player.level == 6:
                if player.type == "uncs":
                    game_status = "cortana"
                elif player.type == "covenant":
                    game_status = "arbiter"
            elif player.ev_lvl == player.level:
                maps["evolution"].set_map()
                alpha = 255
                alpha1 = 0
                player.x = 90
                player.y = 90
                while alpha > 0:
                    game.blit(bg_images["evolution"], (0, 0))
                    player.draw(alpha=alpha)
                    player.draw(ev=1, alpha=0 + alpha1)
                    alpha -= 1
                    alpha1 += 1
                    display_message(f"{player.name} turning into {player.evolution}")
                    pygame.display.update()
                player.name = player.evolution
                player.evolution = base_characters[player.name]["evolution"]
                player.ev_lvl = base_characters[player.name]["ev_lvl"]
                player.image = ch_images[player.name]
                if player.evolution != "no":
                    player.evolution_image = ch_images[player.evolution]
                player.set_sprite()
                display_message(f"Now you are {player.name}!")
                pygame.time.wait(3000)
                player.x, player.y = 120, 90

            player.attack = math.floor(
                0.01 * (2 * base_characters[player.name]["base_attack"] + player.IV_attack * player.level) + 5)
            player.defense = math.floor(
                0.01 * (2 * base_characters[player.name]["base_defense"] + player.IV_defense * player.level) + 5)
            player.speed = math.floor(
                0.01 * (2 * base_characters[player.name]["base_speed"] + player.IV_speed * player.level) + 5)
            player.max_hp = math.floor(
                ((2 * base_characters[player.name]["base_hp"] + player.IV_hp * player.level) / 100) + player.level + 10)
            player.current_hp = player.max_hp
            player.max_shield = player.level + int(player.max_hp * (base_characters[player.name]["base_shield"] / 100))
            player.current_shield = player.max_shield
            player.sp_attack = math.floor(
                0.01 * (2 * base_characters[player.name]["base_sp_attack"] + player.IV_sp_attack * player.level) + 5)
            player.current_sp_attack = player.sp_attack
            player.sp_defense = math.floor(
                0.01 * (2 * base_characters[player.name]["base_sp_defense"] + player.IV_sp_defense * player.level) + 5)
            player.current_sp_defense = player.sp_defense
            player.medkit = 2
            player.poition_of_attack = 2
            player.poition_of_defense = 2
            player.current_attack = player.attack
            player.current_defense = player.defense
            for i in player.moves:
                if i != "Return":
                    i.cur_pp = i.pp

        if game_status != "?":
            maps["start_menu"].set_map()

    if game_status == "?":
        display_message('Do you want to continue(Y/N)?')

    if game_status == "cortana":
        cortana = Character("odst", 1, 40, 10)
        cortana.size = 400
        cortana.image = ch_images[game_status]
        cortana.set_sprite()
        cortana.draw()
        display_message(f"""Congratulations {player.name}. Simulation is over!""")
        pygame.display.update()
        pygame.time.wait(5000)
        game_status = "end of game"

    if game_status == "arbiter":
        arbiter = Character("odst", 1, 40, 10)
        arbiter.size = 400
        arbiter.image = ch_images[game_status]
        arbiter.set_sprite()
        arbiter.draw()
        display_message(f"""Congratulations brother. Simulation is over!""")
        pygame.display.update()
        pygame.time.wait(5000)
        game_status = "end of game"

    if game_status == "start_menu":
        start_button = create_button(150, 30, 175, 300, 250, 315, 'Finish the fight')
        quit_button = create_button(150, 30, 175, 340, 250, 355, 'Quit')
        pygame.display.update()

    if game_status == "end of game":
        game.blit(bg_images["start_menu"], (0, 0))
        font = pygame.font.Font(pygame.font.get_default_font(), 40)
        title = font.render('Simulation is over', True, white)
        game.blit(title, (250 - title.get_width() // 2, 150))
        main_menu_button = create_button(150, 30, 175, 300, 250, 315, 'Main menu')
        quit_from_game_button = create_button(150, 30, 175, 340, 250, 355, 'Quit')
        results_button = create_button(150, 30, 175, 380, 250, 395, 'Results')
        pygame.display.update()

    if game_status == "results":
        end_of_game_button = create_button(150, 30, 175, 300, 250, 315, 'Main menu')
        quit_from_results_button = create_button(150, 30, 175, 340, 250, 355, 'Quit')
        pygame.display.update()

    clock.tick(14)

pygame.quit()
