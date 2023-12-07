import pygame
from pygame.locals import *
import time
import math
import random
from lxml import etree
import os

pygame.init()


class Character:
    def __init__(self, name, level, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.name = name
        self.level = level
        self.x = x
        self.y = y
        file = os.getcwd() + "\\stats.xml"
        characters = etree.parse(file)
        characters = etree.tostring(characters)
        characters = etree.fromstring(characters)
        for character in characters:
            if character.get("name") == name:
                for stat in character:
                    if stat.tag == "hp":
                        self.hp = math.floor(
                            ((2 * int(stat.text) + random.randint(0, 31)) * self.level) / 100) + self.level + 10
                    elif stat.tag == "attack":
                        self.attack = math.floor(0.01 * (2 * int(stat.text) + random.randint(0, 31) * self.level) + 5)
                    elif stat.tag == "defense":
                        self.defence = math.floor(0.01 * (2 * int(stat.text) + random.randint(0, 31) * self.level) + 5)
                    elif stat.tag == "speed":
                        self.speed = math.floor(0.01 * (2 * int(stat.text) + random.randint(0, 31) * self.level) + 5)
                    elif stat.tag == "shield":
                        self.shield = int(stat.text)
                break
        self.shield = self.hp * (self.shield // 100)

        self.size = 250
        self.file_image = os.getcwd() + "\\characters\\" + self.name + ".png"
        self.image = pygame.image.load(self.file_image).convert_alpha()

    def flip(self):
        self.image = pygame.transform.flip(self.image, True, False)

    def set_sprite(self):

        scale = self.size / self.image.get_width()
        new_width = self.image.get_width() * scale
        new_height = self.image.get_height() * scale
        self.image = pygame.transform.scale(self.image, (new_width, new_height))

    def draw(self, alpha=255):

        sprite = self.image
        transparency = (255, 255, 255, alpha)
        sprite.fill(transparency, None, pygame.BLEND_RGBA_MULT)
        game.blit(sprite, (self.x, self.y))

    def get_rect(self):
        return Rect(self.x, self.y, self.image.get_width(), self.image.get_height())


white = (255, 255, 255)
game_width = 500
game_height = 500
size = (game_width, game_height)
game = pygame.display.set_mode(size)
pygame.display.set_caption('Battle')
bg_imges = {}
for i in os.listdir(os.getcwd() + "\\backgrounds"):
    bg_img = pygame.image.load(os.getcwd() + "\\backgrounds\\" + i)
    bg_img = pygame.transform.scale(bg_img, (game_width, game_height))
    bg_imges[i[:i.find(".")]] = bg_img

character = Character("odst", 1, 0, 100)
character.set_sprite()

character1 = Character("sangheili minor", 1, 250, 100)
character1.set_sprite()
character1.flip()

opponent = Character("sangheili minor", 1, 250, 100)
opponent.set_sprite()
opponent.flip()

characters_list = [character, character1]

game_status = 'select'
while game_status != 'quit':
    for event in pygame.event.get():
        if event.type == QUIT:
            game_status = 'quit'

        if event.type == MOUSEBUTTONDOWN:
            mouse_click = event.pos
            if game_status == 'select':
                for i in range(len(characters_list)):
                    if characters_list[i].get_rect().collidepoint(mouse_click):
                        player = characters_list[i]
                        game_status = 'prebattle'

    if game_status == 'select':
        game.blit(bg_imges[game_status], (0, 0))
        character.draw()
        character1.draw()
        mouse_cursor = pygame.mouse.get_pos()
        for i in characters_list:
            if i.get_rect().collidepoint(mouse_cursor):
                pygame.draw.rect(game, (0, 0, 0), i.get_rect(), 2)

        pygame.display.update()

    if game_status == 'prebattle':
        game.blit(bg_imges[game_status], (0, 0))
        player.x, player.y = 20, 200
        opponent.x, opponent.y = 210, 60
        player.draw()
        opponent.draw()
        pygame.display.update()

