import random
import math

import pygame


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRID_LINE = (30, 30, 30)

TICK = 0.2

class Game:
    def __init__(self):
        pygame.init()

        self.width, self.height = 900, 600
        self.cell = 5
        self.rows = self.height // self.cell
        self.cols = self.width // self.cell

        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False

        self.tick = TICK
        self.timer = 0

        self.grid = self.random_grid()
        self.grid_overlay = self.make_grid_overlay()

    def run(self):
        while self.running:
            dt = min(self.clock.tick(60)/1000, 0.1)

            for event in pygame.event.get():
                self.handle_event(event)

            self.update(dt)
            self.draw()

        pygame.quit()

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.paused = not self.paused

    def update(self, dt):
        if self.paused:
            return

        self.timer += dt

        while self.timer >= self.tick:
            self.step()
            self.timer -= self.tick

    def step(self):
        new = self.empty_grid()

        for i in range(self.rows):
            for j in range(self.cols):
                n = self.neighbours(i, j)
                alive = self.grid[i][j] == 1
                new[i][j] = 1 if (n == 3 or (alive and n == 2)) else 0

        self.grid = new

    def draw(self):
        self.screen.fill(BLACK)
        self.draw_grid()
        self.draw_grid_lines()
        pygame.display.flip()

    def draw_grid(self):
        for i in range(self.rows):
            y = i * self.cell
            for j in range(self.cols):
                x = j * self.cell
                if self.grid[i][j]:
                    pygame.draw.rect(
                        self.screen, 
                        WHITE,
                        (x, y, self.cell, self.cell)
                    )
    
    def draw_grid_lines(self):
        self.screen.blit(self.grid_overlay, (0, 0))

    def empty_grid(self):
        return [[0] * self.cols for _ in range(self.rows)]

    def random_grid(self):
        return [[random.randint(0, 1) for _ in range(self.cols)] for _ in range(self.rows)]

    def neighbours(self, i, j):
        n = 0
        for ni in range(-1, 2):
            for nj in range(-1, 2):
                if ni == 0 and nj == 0:
                    continue
                if 0 <= i+ni < self.rows and 0 <= j+nj < self.cols:
                    if self.grid[i+ni][j+nj] == 1:
                        n += 1
        return n

    def make_grid_overlay(self):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        for i in range(self.rows + 1):
            y = i * self.cell
            pygame.draw.line(overlay, GRID_LINE, (0, y), (self.width, y), 1)

        for j in range(self.cols + 1):
            x = j * self.cell
            pygame.draw.line(overlay, GRID_LINE, (x, 0), (x, self.height), 1)

        return overlay


if __name__ == "__main__":
    Game().run()
