import pygame
import random
import csv
import os
from collections import deque

cellsize = 8
gridcol = 100
gridrow = 100
hud_height = 18

winwidth = cellsize*gridcol
winheight = cellsize*gridrow + hud_height

cells_to_place = 22
spread = 5
stale_window = 6
max_period = 30  # detect oscillators up to this period
tick_ms = 1
csv_path = "conway_runs.csv"

def make_seed_grid():
    grid = [[0 for c in range(gridcol)] for r in range(gridrow)]
    cr, cc = gridrow // 2, gridcol // 2
    placed = 0
    while placed < cells_to_place:
        dr = random.randint(-spread, spread)
        dc = random.randint(-spread, spread)
        if grid[cr + dr][cc + dc] == 0:
            grid[cr + dr][cc + dc] = 1
            placed += 1
    return grid


pygame.init()
screen = pygame.display.set_mode((winwidth, winheight))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, hud_height)

def count_neighbors(grid, r, c):
    total = 0
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr = r + dr
            nc = c + dc
            if 0 <= nr < gridrow and 0 <= nc < gridcol:
                total += grid[nr][nc]
    return total

def next_generation(grid):
    new_grid = [[0 for c in range(gridcol)] for r in range(gridrow)]
    for r in range(gridrow):
        for c in range(gridcol):
            neighbors = count_neighbors(grid, r, c)
            cell = grid[r][c]
            if cell == 1 and (neighbors == 2 or neighbors == 3):
                new_grid[r][c] = 1
            elif cell == 0 and neighbors == 3:
                new_grid[r][c] = 1
    return new_grid

def draw_grid(screen, grid, generation, resets, max_gen):
    screen.fill((0, 0, 0))
    for r in range(gridrow):
        for c in range(gridcol):
            if grid[r][c] == 1:
                rect = (c*cellsize, r*cellsize + hud_height, cellsize, cellsize)
                pygame.draw.rect(screen, (255, 255, 255), rect)
    pygame.draw.rect(screen, (20, 20, 20), (0, 0, winwidth, hud_height))
    gen_text = font.render(f"Generations = {generation}", True, (255, 255, 255))
    max_text = font.render(f"Max = {max_gen}", True, (255, 255, 255))
    reset_text = font.render(f"Resets = {resets}", True, (255, 255, 255))
    screen.blit(gen_text, (4, 1))
    screen.blit(max_text, ((winwidth - max_text.get_width()) // 2, 1))
    screen.blit(reset_text, (winwidth - reset_text.get_width() - 4, 1))
    pygame.display.flip()

def live_cells(grid):
    cells = []
    for r in range(gridrow):
        for c in range(gridcol):
            if grid[r][c] == 1:
                cells.append((r, c))
    return cells

def grid_state(grid):
    return tuple(tuple(row) for row in grid)

def init_csv():
    if not os.path.exists(csv_path):
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["iteration", "generation", "live_count", "live_cells"])

def log_generation(iteration, generation, cells):
    cells_str = ";".join(f"{r},{c}" for r, c in cells)
    with open(csv_path, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([iteration, generation, len(cells), cells_str])

init_csv()

running = True
iteration = 1
generation = 0
resets = 0
max_gen = 0
state_history = deque(maxlen=max_period)

grid = make_seed_grid()
log_generation(iteration, generation, live_cells(grid))
state_history.append(grid_state(grid))

last_tick = pygame.time.get_ticks()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    now = pygame.time.get_ticks()
    if now - last_tick >= tick_ms:
        grid = next_generation(grid)
        generation += 1
        if generation > max_gen:
            max_gen = generation
        cells = live_cells(grid)
        log_generation(iteration, generation, cells)

        state = grid_state(grid)
        # oscillator: current state matches any state seen within the last
        # max_period generations (catches periods 1..max_period)
        stale = state in state_history
        state_history.append(state)
        dead = len(cells) == 0

        if stale or dead:
            resets += 1
            iteration += 1
            generation = 0
            grid = make_seed_grid()
            state_history.clear()
            log_generation(iteration, generation, live_cells(grid))
            state_history.append(grid_state(grid))

        last_tick = now

    draw_grid(screen, grid, generation, resets, max_gen)
    clock.tick(60)

pygame.quit()
