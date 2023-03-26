import torch
import random
import numpy as np

from collections import deque

from Model import Linear_QNet, QTrainer

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001


class Agent:

    def __init__(self):
        self.n_games = 0
        self.epsilon = 0  # control the randomness
        self.gamma = 0.9  # discount rate
        # Elements will be removed from the left if exceeded
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(16, 256, 4)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_state(self, game):

        spaceship = game.get_spaceship()

        destination = None

        obstacle = spaceship.pulling_planet

        for planet in game.planets:
            if (planet.is_green):
                destination = planet

        state = [

            # up
            (spaceship.velocity_y < 0),
            # down
            (spaceship.velocity_y > 0),
            # left
            (spaceship.velocity_x < 0),
            # right
            (spaceship.velocity_x > 0),

            # Danger - Right Wall collision
            (spaceship.velocity_x > 0 and spaceship.x > game.get_screen_width() - 5),
            # Danger - Up wall collision
            (spaceship.velocity_y < 0 and spaceship.y < 5),
            # Danger - Left wall collision
            (spaceship.velocity_x < 0 and spaceship.x < 5),
            # Danger - Down Wall collision
            (spaceship.velocity_y > 0 and spaceship.x > game.get_screen_height() - 5),

            #destination is up
            (destination.y < spaceship.y),
            #destination is down
            (destination.y > spaceship.y),
            #destination is right
            (destination.x > spaceship.x),
            #destination is left
            (destination.x < spaceship.x),

            #obstacle is up
            (obstacle is not None and obstacle.y < spaceship.y),
            #obstacle is down
            (obstacle is not None and obstacle.y > spaceship.y),
            #obstacle is right
            (obstacle is not None and obstacle.x > spaceship.x),
            #obstacle is left
            (obstacle is not None and obstacle.x < spaceship.x)
        ]
        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # random moves at first
        self.epsilon = 80 - self.n_games
        final_move = [0, 0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 3)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move



