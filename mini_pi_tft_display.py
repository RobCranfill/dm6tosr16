'''
Use PyGame for display?
'''

import os
import pygame


class tft_display():

    def __init__(self):

        self._is_running = True

        os.putenv('SDL_FBDEV', '/dev/fb1')
        # os.putenv('SDL_VIDEODRIVER', 'fbcon') # Force PyGame to PiTFT

        pygame.init()

        self._display = pygame.display.set_mode((240, 240))
        pygame.display.update()
  
        self._font = pygame.font.SysFont("monospace", 20)

        print("Created display")


    # https://stackoverflow.com/questions/20842801/how-to-display-text-in-pygame

    def text_to_screen(self, text, x, y, size = 20,
                color = (200, 0, 0), font_type = 'fonts/orecrusherexpand.ttf'):
        try:
            # text = str(text)
            # font = pygame.font.Font(font_type, size)
            text = self._font.render(str(text), True, color)
            self._display.blit(text, (int(x), int(y)))
        except Exception as e:
            print(e)
            # raise e
            
    def update(self, uptime, midi_count, status_message):

        print(f"{uptime=}\n{midi_count=}\n{status_message=}\n")

        self.text_to_screen("This is a test", 0, 0)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._is_running = False
                return

            # window_surface.blit(background, (0, 0))

        pygame.display.update()

