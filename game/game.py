import sys
import pygame
from time import  sleep

from config.settings import Settings
from Objects import Ship
from Objects import Bullet
from Objects import Alien
from Stats.game_stats import  GameStats



class AlienInvasion:
    """Класс для управления ресурсами и поведением игры"""

    def __init__(self):
        """Инициализирует игру и создаёт игровой процесс"""
        pygame.init()
        self.settings = Settings()

        # self.screen = pygame.display.set_mode(
        #     (self.settings.screen_width, self.settings.screen_height))
        self.screen = pygame.display.set_mode(
            (0,0),pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Alien Invasion")

        # Создание экземпляра для хранения игровой статистики
        self.stats = GameStats(self)

        self.ship = Ship.Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()

    def _create_fleet(self):
        """Создание флота вторжения"""
        #
        alien = Alien.Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)

        """Определение количества рядов, помещаемых на экране"""
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height -
                             (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)

        # Создание флота вторжения
        for row_number in range(number_rows):
            # Создание первого ряда пришельцев
            for alien_number in range(number_aliens_x):
                #   Создание пришельца и размещение его в ряду
                self._create_alien(alien_number,row_number)



    def _create_alien(self,alien_number, row_number):
        """Создание пришельца и размещение его в ряду"""
        alien = Alien.Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

    def _check_events(self):
        """Обрабатывает нажатия клавиш и события мыши"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)

    def _check_keydown_events(self,event):
        """Реагирует на нажатие клавищ"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()

    def _check_fleet_edges(self):
        """Реагирует на достижение пришельцем края экрана"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _ship_hit(self):
        if self.stats.ships_left > 0:
            """Обрабатывает столкновения корабля с пришельцем"""
            # Уменьшение ships_left.
            self.stats.ships_left -= 1

            # Очистка списков пришельцев и снарядов
            self.aliens.empty()
            self.bullets.empty()

            # Создание нового флота и размещения корабля в центре
            self._create_fleet()
            self.ship.center_ship()

            # Пауза
            sleep(0.5)
        else:
            self.stats.game_active = False

    def _change_fleet_direction(self):
        """Опускает весь флот и меняет направление флота"""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _fire_bullet(self):
        """Создание нового снаряда и включение его в группу bullets"""
        if len(self.bullets) < self.settings.bullet_allowed:
            new_bullet = Bullet.Bullet(self)
            self.bullets.add(new_bullet)

    def _check_keyup_events(self,event):
        """Реагирует на отпускание клавиш"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _update_screen(self):
        """Обновляет изображение на экране и отображает
         на новый экран"""
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)
        pygame.display.flip()

    def _update_bullets(self):
        """Обновляет позицию снарядов и уничтожает старые"""
        # Обновление позиции снарядов
        self.bullets.update()
        # Удаление снадов, вышедших за край экрана
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        # Проверка попаданий в пришельцев
        # При обнаружении попаданий удалить снаряд и пришельца
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens,False,True)
        if not self.aliens:
            # Уничтожение существующих снарядов и созздание нового флота
            self.bullets.empty()
            self._create_fleet()

    def _check_aliens_bottom(self):
        """Проверяет, добрались ли пришельцы до нижнешл края экрана"""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # Происходит то же, что при столкновении с кораблём
                self._ship_hit()
                break

    def _update_aliens(self):
        """ Проверяет, достиг ли флот края экрана,
            с последующим обновлением позиций всех пришельцев во флоте"""
        self._check_fleet_edges()
        self.aliens.update()

        # Проверка коллизии "пришелец - корабль"
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

    def run_game(self):
        """Запуск основного цикла игры."""

        while True:
            self._check_events()
            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()

            self._update_screen()


if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()
