import gym
from gym import spaces
import arcade
from arcade import get_window
import random
import math
import numpy as np
import pyglet

from SpaceGame import Game

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
SPACESHIP_SPEED = 0.01
GRAVITATIONAL_FORCE = 5


class SpaceshipGameEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        super(SpaceshipGameEnv, self).__init__()

        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(
            low=0, high=1200, shape=(25,), dtype=np.float32)

        self.game = Game(SCREEN_WIDTH, SCREEN_HEIGHT, "Spaceship Game")

        self.game.setup()

    def calculate_reward(self, done, done_reward):
        if done:
            return done_reward

        # Compute the distance to the target planet
        target_planet = self.game.planets[self.game.green_planet_index]
        distance_to_target = np.sqrt(
            (self.game.spaceship.x - target_planet.x) ** 2 + (self.game.spaceship.y - target_planet.y) ** 2)

        # Compute the velocity of the spaceship
        velocity = np.sqrt(self.game.spaceship.velocity_x **
                           2 + self.game.spaceship.velocity_y ** 2)

        # Reward for getting closer to the target planet and having a smaller velocity
        reward = -0.01 * distance_to_target - 0.01 * velocity

        return reward

    def step(self, action):
        self.game.action(action)
        done_reward, done = self.game.on_update(1 / 60)
        obs = self.get_observation()
        reward = self.calculate_reward(done, done_reward)

        return obs, reward, done, {}

    def get_observation(self):
        planets_data = []
        for planet in self.game.planets:
            planets_data.extend(
                [planet.x, planet.y, planet.size, planet.is_green])
        spaceship_data = [self.game.spaceship.x,
                          self.game.spaceship.y, self.game.spaceship.angle, self.game.spaceship.velocity_x, self.game.spaceship.velocity_y]
        return np.array(spaceship_data + planets_data)

    def reset(self):
        self.game.reset()
        print("Game Reset")
        return self.get_observation()

    def render(self, mode='human'):

        if mode == 'human':

            arcade.start_render()
            self.game.on_draw()
            arcade.finish_render()

        elif mode == 'rgb_array':
            return self.game.get_frame()
        else:
            raise NotImplementedError(
                "Render mode not supported: {}".format(mode))

    def close(self):
        if self.game:
            self.game.close()
            self.game = None
