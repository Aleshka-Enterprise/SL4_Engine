import pygame

class DISPLAY:
    WIDTH = 1500
    HEIGHT = 800

class KEYS:
    RIGHT = (pygame.K_RIGHT, pygame.K_d)
    LEFT = (pygame.K_LEFT, pygame.K_a)
    JUMP = (pygame.K_SPACE, pygame.K_w, pygame.K_UP)
    RUN = (pygame.K_LSHIFT,)
    SIT = (pygame.K_s, pygame.K_DOWN)
    ATTACK = (pygame.K_z,)
    INTERACT = (pygame.K_e,)
    DROP = (pygame.K_q,)
    MENU = (pygame.K_ESCAPE,)

DEBUG = False
FPS = 60