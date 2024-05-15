import sys
import pygame

from settings import Settings

def run_game():
    #初始化游戏并创建一个屏幕对象
    pygame.init()#初始化背景设置
    ai_settings = Settings()
    screen = pygame.display.set_mode((ai_settings.screen_width,ai_settings.screen_height))#创建一个窗口
    pygame.display.set_caption("Alien Invasion")


    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:#关闭窗口为一个QUIT事件
                sys.exit()

        screen.fill(ai_settings.bg_color)#每次循环都重绘屏幕
        pygame.display.flip()#flip在每次while循环是都创建一个新的屏幕并擦去旧的屏幕，使得只有新屏幕可以见



run_game()
