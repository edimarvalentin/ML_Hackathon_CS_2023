import arcade
import random
import math

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
SPACESHIP_SPEED = 0.01
GRAVITATIONAL_FORCE = 5


class Spaceship:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity_x = 0
        self.velocity_y = 0
        self.angle = 0

    def draw(self):
        arcade.draw_rectangle_filled(
            self.x, self.y, 20, 20, arcade.color.BLUE, self.angle)

    def move(self, net_force, angle):
        self.velocity_x += net_force * math.cos(math.radians(angle))
        self.velocity_y += net_force * math.sin(math.radians(angle))
        self.x += self.velocity_x
        self.y += self.velocity_y

    def apply_gravity(self, planet):
        dx = planet.x - self.x
        dy = planet.y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        force = GRAVITATIONAL_FORCE * planet.size / distance**2
        angle = math.degrees(math.atan2(dy, dx))
        self.move(force, angle)

    def collides_with(self, planet):
        dx = planet.x - self.x
        dy = planet.y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        return distance <= planet.size + 15


class Planet:
    def __init__(self, x, y, size, is_green):
        self.x = x
        self.y = y
        self.size = size
        self.is_green = is_green

    def draw(self):
        color = arcade.color.GREEN if self.is_green else arcade.color.WHITE
        arcade.draw_circle_filled(self.x, self.y, self.size, color)


class Game(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.BLACK)
        self.planets = []
        self.green_planet_index = random.randint(0, 4)
        for i in range(5):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            size = random.randint(10, 20)
            is_green = i == self.green_planet_index
            self.planets.append(Planet(x, y, size, is_green))
        self.spaceship = Spaceship(50, SCREEN_HEIGHT//2)

    def setup(self):
        pass

    def on_update(self, delta_time):
        for planet in self.planets:
            if planet.is_green and self.spaceship.collides_with(planet):
                arcade.draw_text("Congratulations!", SCREEN_WIDTH/2, SCREEN_HEIGHT/2,
                                 arcade.color.WHITE, font_size=50, anchor_x="center")
            self.spaceship.apply_gravity(planet)
        if self.spaceship.x < 0 or self.spaceship.x > SCREEN_WIDTH or self.spaceship.y < 0 or self.spaceship.y > SCREEN_HEIGHT:
            arcade.close_window()
        self.spaceship.move(SPACESHIP_SPEED, self.spaceship.angle)

    def on_draw(self):
        arcade.start_render()
        for planet in self.planets:
            planet.draw()
        self.spaceship.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.spaceship.angle = 180
        elif key == arcade.key.RIGHT:
            self.spaceship.angle = 0
        elif key == arcade.key.UP:
            self.spaceship.angle = 90
        elif key == arcade.key.DOWN:
            self.spaceship.angle = 270


def main():
    game = Game(SCREEN_WIDTH, SCREEN_HEIGHT, "Spaceship Game")
    game.setup()
    arcade.run()


if __name__ == '__main__':
    main()
