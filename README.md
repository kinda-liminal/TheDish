# TheDish

A self-running Conway's Game of Life that reseeds itself and logs every run.

It drops a small random seed into the middle of a 300x300 grid and lets it play out under the standard Life rules. When a run dies off or settles into a loop, it logs the result, reshuffles a fresh seed, and starts again. Every generation gets recorded, so you end up with a growing dataset of how small random seeds behave over time.

## How it works

- Seeds 22 random cells in a small box around the center of the grid
- Runs Conway's rules (B3/S23) on a bounded grid (edges count as dead, nothing wraps)
- Detects oscillators up to period 30 by checking whether the full grid state repeats
- When a run dies out or loops, it increments the reset counter and starts a new run
- Logs every generation to a CSV: run number, generation, live cell count, and the live cell coordinates

There's a small HUD across the top showing the current generation, the longest run so far, and the total number of resets.

## Running it

Requires `pygame`. I ran this on Python 3.11, since the 3.14 build I had was missing the font module.

```bash
python -m venv .venv
.venv/bin/pip install pygame
.venv/bin/python thedish.py
```

Close the window to stop.

## The data

The output CSV (`conway_runs.csv`) is gitignored on purpose. It grows quickly and it's just generated output, so running the script yourself will build your own copy.

Each row is one generation of one run:

| column | meaning |
| --- | --- |
| `iteration` | which run it is |
| `generation` | step number within that run |
| `live_count` | number of live cells |
| `live_cells` | coordinates of every live cell |

## Configuration

The knobs are all at the top of `thedish.py`:

| setting | what it does |
| --- | --- |
| `gridcol` / `gridrow` | grid dimensions |
| `cellsize` | pixels per cell (lower it if the window is bigger than your screen) |
| `cells_to_place` | number of cells in the seed |
| `spread` | how tightly the seed is clustered |
| `max_period` | longest oscillator period it will detect before calling a run stuck |
| `tick_ms` | how fast it steps |

## Notes

The grid is bounded, so gliders that would normally escape to infinity instead run into the dead edge and die. On a wrapped or infinite grid the behavior would be different.
