import arcade
import random
import pyglet
import math
import numpy as np

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
        return distance <= (planet.size + 15 + (20 if planet.is_green else 0))


class Planet:
    def __init__(self, x, y, size, is_green):
        self.x = x
        self.y = y
        self.size = size
        self.is_green = is_green

    def draw(self):
        color = arcade.color.GREEN if self.is_green else arcade.color.WHITE
        arcade.draw_circle_filled(self.x, self.y, self.size, color)
        if self.is_green:
            arcade.draw_circle_outline(self.x, self.y, self.size + 20, color)


class Game(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        self.is_running = True

        self.push_handlers(on_key_press=self.on_key_press)
        # print(self.get_event_handlers)

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
                print("you won!!!")
                self.is_running = False
                return (100, True)
            self.spaceship.apply_gravity(planet)
        if self.spaceship.x < 0 or self.spaceship.x > SCREEN_WIDTH or self.spaceship.y < 0 or self.spaceship.y > SCREEN_HEIGHT:
            self.is_running = False
            return (-100, True)
        self.spaceship.move(SPACESHIP_SPEED, self.spaceship.angle)
        return (0, False)

    def on_draw(self):
        if self.is_running:
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
        print("Key pressed:", key)

    def action(self, action):
        if action == 0:
            self.spaceship.angle = 180
        elif action == 1:
            self.spaceship.angle = 0
        elif action == 2:
            self.spaceship.angle = 90
        elif action == 3:
            self.spaceship.angle = 270

    def run(self):
        # Set up the game loop
        while True:
            # Call the update() method with the time since the last frame
            self.on_update(1/60)

            if self.is_running:

                # Clear the screen
                arcade.start_render()

                # Call the on_draw() method to draw the game objects
                self.on_draw()

                # Swap buffers to display the rendered frame
                arcade.finish_render()

                # Sleep to enforce the desired frame rate
                arcade.pause(1/60)
            else:
                self.close()

    def reset(self):
        self.is_running = True
        self.planets = []
        self.green_planet_index = random.randint(0, 4)
        for i in range(5):
            x = random.randint(200, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            size = random.randint(10, 20)
            is_green = i == self.green_planet_index
            self.planets.append(Planet(x, y, size, is_green))
        self.spaceship = Spaceship(50, SCREEN_HEIGHT // 2)

    def get_frame(self):
        arcade.start_render()
        self.on_draw()
        arcade.finish_render()

        buffer = pyglet.image.get_buffer_manager().get_color_buffer()
        image_data = buffer.get_image_data()
        arr = np.frombuffer(image_data.data, dtype=np.uint8)
        arr = arr.reshape(buffer.height, buffer.width, 4)
        return arr[::-1]


def main():
    game = Game(SCREEN_WIDTH, SCREEN_HEIGHT, "Spaceship Game")
    game.setup()
    # arcade.run()
    game.run()


if __name__ == '__main__':
    main()
