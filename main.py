from collections import defaultdict
import random

import pygame


WIDTH = 900
HEIGHT = 600
CELL = 10

TICK = 0.2
DENSITY = 0.25

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRID_LINE = (30, 30, 30)


class Game:
    def __init__(self):
        pygame.init()

        self.width, self.height = WIDTH, HEIGHT
        self.cell = CELL
        self.rows = self.height // self.cell
        self.cols = self.width // self.cell

        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = True

        self.tick = TICK
        self.timer = 0

        self.grid = self.empty_grid()
        self.saved_grid = self.grid.copy()
        self.grid_overlay = self.make_grid_overlay()

        self.font = pygame.font.SysFont(None, 24)
        self.info_text = self.font.render(
            "Space - pause/play  C - clear  R - randomize  F - step forward  S - save grid  L - load grid",
            True,
            (255, 255, 255)
        )
        self.info_rect = self.info_text.get_rect(center=(self.width//2, self.height-30))
        self.paused_text = self.font.render(
            "Paused - click to edit cell",
            True,
            (255, 255, 255)
        )
        self.paused_rect = self.paused_text.get_rect(center=(self.width//2, self.height-60))

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
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False
            elif event.key == pygame.K_SPACE:
                self.paused = not self.paused
                self.timer = 0
            elif event.key == pygame.K_c:
                # Clear grid
                self.grid = self.empty_grid()
            elif event.key == pygame.K_r:
                # Random grid
                self.grid = self.random_grid(DENSITY)
            elif event.key == pygame.K_s:
                # Save grid
                self.saved_grid = self.grid.copy()
            elif event.key == pygame.K_l:
                # Load saved grid
                self.grid = self.saved_grid.copy()
            elif self.paused and event.key == pygame.K_f:
                # Step forward
                self.step()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.paused and event.button == 1:
                self.toggle_cell(event.pos)

    def update(self, dt):
        if self.paused:
            return

        self.timer += dt

        while self.timer >= self.tick:
            self.step()
            self.timer -= self.tick

    def step(self):
        counts = defaultdict(int)

        for i, j in self.grid:
            for ni in range(-1, 2):
                for nj in range(-1, 2):
                    if ni == 0 and nj == 0:
                        continue
                    if 0 <= i+ni < self.rows and 0 <= j+nj < self.cols:
                        counts[(i+ni, j+nj)] += 1

        new = self.empty_grid()

        for cell, n in counts.items():
            alive = cell in self.grid
            if (n == 3 or (alive and n == 2)):
                new.add(cell)

        self.grid = new

    def draw(self):
        self.screen.fill(BLACK)

        self.draw_grid()
        self.draw_grid_lines()
        self.screen.blit(self.info_text, self.info_rect)

        if self.paused:
            self.screen.blit(self.paused_text, self.paused_rect)

        pygame.display.flip()

    def draw_grid(self):
        for i, j in self.grid:
            y = i * self.cell
            x = j * self.cell
            pygame.draw.rect(
                self.screen, 
                WHITE,
                (x, y, self.cell, self.cell)
            )
    
    def draw_grid_lines(self):
        self.screen.blit(self.grid_overlay, (0, 0))

    def empty_grid(self):
        return set()

    def random_grid(self, density):
        alive = set()

        for i in range(self.rows):
            for j in range(self.cols):
                if random.random() < density:
                    alive.add((i, j))

        return alive

    def make_grid_overlay(self):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        for i in range(self.rows + 1):
            y = i * self.cell
            pygame.draw.line(overlay, GRID_LINE, (0, y), (self.width, y), 1)

        for j in range(self.cols + 1):
            x = j * self.cell
            pygame.draw.line(overlay, GRID_LINE, (x, 0), (x, self.height), 1)

        return overlay

    def toggle_cell(self, pos):
        pos = (pos[1] // self.cell, pos[0] // self.cell)
        if pos in self.grid:
            self.grid.remove(pos)
        else:
            self.grid.add(pos)


if __name__ == "__main__":
    Game().run()
