import pygame
import sys
from settings import *
from level import Level

class Game:
    def __init__(self):
        pygame.init()
        self.fullscreen = False
        self.screen = pygame.display.set_mode((1100, 700), pygame.RESIZABLE)

        logo_img = pygame.image.load('logo_1.ico')
        pygame.display.set_icon(logo_img)
        pygame.display.set_caption('Legends Of The Adventure')
        self.clock = pygame.time.Clock()
        self.level = Level()

        main_sound = pygame.mixer.Sound('../audio/music.ogg')
        main_sound.set_volume(0.7)
        main_sound.play(loops = -1)

        self.fading_image = pygame.image.load("logo_2.png")
        self.fading_image = pygame.transform.scale(self.fading_image, self.screen.get_size())


        self.run_fading_effect()

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((1100, 700), pygame.RESIZABLE)

    def exit_fullscreen(self):
        if self.fullscreen:
            self.toggle_fullscreen()

    def run_fading_effect(self):
        for alpha in range(255, 0, -5):
            self.screen.fill('#71ddee')
            self.fading_image.set_alpha(alpha)
            self.screen.blit(self.fading_image, (0, 0))
            pygame.display.flip()
            pygame.time.delay(60)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:
                        self.level.toggle_menu()
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # Fullscreen
                elif event.type == pygame.VIDEORESIZE:
                    if not self.fullscreen:
                        self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        self.toggle_fullscreen()
                    elif event.key == pygame.K_ESCAPE:
                        self.exit_fullscreen()

            self.screen.fill('#71ddee')
            self.level.run()
            pygame.display.update()
            self.clock.tick(FPS)

if __name__ == '__main__':
    game = Game()
    game.run()
