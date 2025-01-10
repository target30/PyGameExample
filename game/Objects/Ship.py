import pygame


class Ship():
    """Класс для управления кораблём"""

    def __init__(self, ai_game):
        """Инициализируем корабль и задаём начальную позицию"""
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.screen_rect = ai_game.screen.get_rect()

        # Загружаем изображение корабля и получаем прямоугольник
        self.image = pygame.image.load('images/ship.bmp')
        self.image = pygame.transform.scale(
            self.image, (ai_game.settings.screen_width / 20,
                         ai_game.settings.screen_height / 10))
        self.rect = self.image.get_rect()

        # Каждый новый корабль появляется у нижнего края экрана
        self.rect.midbottom = self.screen_rect.midbottom

        self.x = float(self.rect.x)

        #Флаг перемещения
        self.moving_right = False
        self.moving_left = False


    def update(self):
        """Обновляет позицию корабля с учётом флага"""
        if self.moving_right:
            self.x += self.settings.ship_speed
        if self.moving_left:
            self.x -= self.settings.ship_speed

        #Обновление атрибута rect на основании self.x
        self.rect.x = self.x

    def blitme(self):
        """Рисует корабль в текущей позиции"""
        self.screen.blit(self.image, self.rect)
