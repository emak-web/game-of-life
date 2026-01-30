from collections import defaultdict
import random

import pygame


WIDTH = 900
HEIGHT = 600
CELL = 10
MIN_CELL = 2
MAX_CELL = 100

TICK = 0.2
DENSITY = 0.25

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRID_LINE = (30, 30, 30)


class Game:
    def __init__(self):
        pygame.init()

        self.width, self.height = WIDTH, HEIGHT
        self.cell_f = CELL
        self.cell = int(round(self.cell_f))
        self.rows = self.height // self.cell
        self.cols = self.width // self.cell
        self.origin = (5, 5)

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Game of life")
        self.clock = pygame.time.Clock()
        self.running = True

        self.paused = True
        self.display_grid = True
        self.dragging = False
        self.lmb_down = False
        self.drag_start_pos = (0, 0)
        self.drag_threshold = self.cell

        self.tick = TICK
        self.timer = 0

        self.grid = self.empty_grid()
        self.saved_grid = self.grid.copy()
        self.grid_overlay = self.make_grid_overlay()

        self.font = pygame.font.SysFont(None, 24)
        self.info_text = self.font.render(
            "Space - pause/play  C - clear  R - randomize  F - step forward  S - save grid  L - load grid  G - toggle grid lines",
            True,
            WHITE
        )
        self.info_rect = self.info_text.get_rect(center=(self.width//2, self.height-30))
        self.paused_text = self.font.render(
            "Paused - click to edit cell",
            True,
            WHITE
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
            elif event.key == pygame.K_g:
                # Toggle grid lines
                self.display_grid = not self.display_grid
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.lmb_down = True
                self.dragging = False
                self.drag_start_pos = event.pos

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if self.paused and not self.dragging:
                    self.toggle_cell(event.pos)

                self.lmb_down = False
                self.dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self.lmb_down:
                if not self.dragging:
                    dx = event.pos[0] - self.drag_start_pos[0]
                    dy = event.pos[1] - self.drag_start_pos[1]

                    if dx**2 + dy**2 >= self.drag_threshold**2:
                        self.dragging = True

                if self.dragging:
                    dx, dy = event.rel
                    self.origin = (self.origin[0] + dx, self.origin[1] + dy)

        elif event.type == pygame.MOUSEWHEEL:
            if event.y > 0:
                self.zoom_at(pygame.mouse.get_pos(), 1)
            elif event.y < 0:
                self.zoom_at(pygame.mouse.get_pos(), -1)

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

        if self.display_grid:
            self.draw_grid_lines()

        self.screen.blit(self.info_text, self.info_rect)

        if self.paused:
            self.screen.blit(self.paused_text, self.paused_rect)

        pygame.display.flip()

    def draw_grid(self):
        for i, j in self.grid:
            y = self.origin[1] + i * self.cell
            x = self.origin[0] + j * self.cell

            if x < -self.cell or x > self.width:
                continue
            if y < -self.cell or y > self.height:
                continue

            pygame.draw.rect(
                self.screen, 
                WHITE,
                (x, y, self.cell, self.cell)
            )
    
    def draw_grid_lines(self):
        self.screen.blit(self.grid_overlay, (self.origin[0] % self.cell - self.cell, self.origin[1] % self.cell - self.cell))

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
        overlay = pygame.Surface((self.width+2*self.cell, self.height+2*self.cell), pygame.SRCALPHA)
        ow, oh = overlay.get_width(), overlay.get_height()

        for y in range(0, oh + 1, self.cell):
            pygame.draw.line(overlay, GRID_LINE, (0, y), (ow, y), 1)

        for x in range(0, ow + 1, self.cell):
            pygame.draw.line(overlay, GRID_LINE, (x, 0), (x, oh), 1)

        return overlay

    def toggle_cell(self, pos):
        pos = ((pos[1]-self.origin[1]) // self.cell, (pos[0]-self.origin[0]) // self.cell)
        if pos in self.grid:
            self.grid.remove(pos)
        else:
            self.grid.add(pos)

    def zoom_at(self, mouse_pos, delta):
        if not (MIN_CELL <= self.cell + delta <= MAX_CELL):
            return

        mx, my = mouse_pos
        wx = (mx - self.origin[0]) / self.cell
        wy = (my - self.origin[1]) / self.cell

        self.cell += delta

        self.origin = (
            mx - wx * self.cell,
            my - wy * self.cell
        )
        self.origin = (int(self.origin[0]), int(self.origin[1]))

        self.rows = self.height // self.cell
        self.cols = self.width // self.cell
        self.grid_overlay = self.make_grid_overlay()


if __name__ == "__main__":
    Game().run()
