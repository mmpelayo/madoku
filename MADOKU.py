
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
import random
import pandas as pd

grid_size = 3
mathdoku_grid = np.zeros((grid_size, grid_size), dtype=int)
undo_stack = []
redo_stack = []
answer = []

row_input = widgets.IntSlider(value=0, min=0, max=grid_size-1, description="Row")
col_input = widgets.IntSlider(value=0, min=0, max=grid_size-1, description="Col")
value_input = widgets.IntSlider(value=1, min=1, max=grid_size, description="Value")

button_update = widgets.Button(description="Update", button_style='success')
button_undo = widgets.Button(description="Undo", button_style='info')
button_redo = widgets.Button(description="Redo", button_style='info')
button_reset = widgets.Button(description="Reset", button_style='warning')
button_validate = widgets.Button(description="Validate", button_style='primary')
button_hint = widgets.Button(description="Hint", button_style='info')
button_new_game = widgets.Button(description="New Game", button_style='danger')

# Apply styles to buttons (padding, border, and width)
for button in [button_update, button_undo, button_redo, button_reset, button_validate, button_hint, button_new_game]:
    button.layout.width = '120px'
    button.layout.height = '40px'
    button.layout.border_radius = '10px'
    button.layout.font_size = '14px'

# Display buttons in a row with spacing
button_box = widgets.HBox([button_update, button_undo, button_redo, button_reset, button_validate, button_hint, button_new_game],
                          layout=widgets.Layout(justify_content='center', padding='10px'))

def get_adjacent_cells(cell, used_cells):
    r, c = cell
    candidates = [(r+1, c), (r, c+1), (r-1, c), (r, c-1)]
    return [(nr, nc) for nr, nc in candidates if 0 <= nr < grid_size and 0 <= nc < grid_size and (nr, nc) not in used_cells]

def generate_cages():
    used_cells = set()
    cages = []
    all_cells = [(r, c) for r in range(grid_size) for c in range(grid_size)]
    while len(used_cells) < grid_size * grid_size:
        start_cell = random.choice([cell for cell in all_cells if cell not in used_cells])
        cage_cells = [start_cell]
        used_cells.add(start_cell)
        cage_size = min(random.choice([2, 3]), grid_size * grid_size - len(used_cells))

        while len(cage_cells) < cage_size:
            adjacent = get_adjacent_cells(random.choice(cage_cells), used_cells)
            if not adjacent:
                break
            next_cell = random.choice(adjacent)
            cage_cells.append(next_cell)
            used_cells.add(next_cell)

        operation = '=' if len(cage_cells) == 1 else '+'
        target_value = sum(random.choices(range(1, grid_size + 1), k=len(cage_cells)))
        cages.append((target_value, operation, cage_cells))
    return cages

cages = generate_cages()

def validate_cages(grid, cages):
    for target_value, operation, cage_cells in cages:
        numbers = [grid[r][c] for r, c in cage_cells]
        if operation == '+' and sum(numbers) != target_value:
            return False
        elif operation == '=' and numbers[0] != target_value:
            return False
    return True

def is_valid(grid, row, col, num):
    return num not in grid[row] and num not in [grid[i][col] for i in range(len(grid))]

def solve_mathdoku(grid, cages, row=0, col=0):
    if row == grid_size:
        return validate_cages(grid, cages)

    next_row, next_col = (row, col + 1) if col + 1 < grid_size else (row + 1, 0)

    for num in range(1, grid_size + 1):
        if is_valid(grid, row, col, num):
            #answer.append((row, col, num))
            answer = np.copy(grid)
            grid[row][col] = num
            if solve_mathdoku(grid, cages, next_row, next_col):
                return True
            grid[row][col] = 0
    return False

# Generate a solvable Mathdoku grid
while not solve_mathdoku(mathdoku_grid, cages):
    mathdoku_grid = np.zeros((grid_size, grid_size), dtype=int)
    cages = generate_cages()

colors = list(mcolors.TABLEAU_COLORS.values())
random.shuffle(colors)
cage_colors = {i: colors[i % len(colors)] for i in range(len(cages))}

answer = mathdoku_grid #to save correct answer sa board

def visualize_grid():
    clear_output(wait=True)
    display(HTML("<h2 style='text-align:center;'>MADOKU</h2>"))
    display(row_input, col_input, value_input, widgets.HBox([button_update, button_undo, button_redo, button_reset, button_validate, button_hint, button_new_game]))


    fig, ax = plt.subplots(figsize=(5, 5))
    ax.set_position([0., 0.2, 0.6, 0.6])  # [left, bottom, width, height]
    ax.set_xticks(range(grid_size + 1))
    ax.set_yticks(range(grid_size + 1))
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.grid(True, which='both', color='black', linewidth=1.5)

    # Add row and column labels
    for i in range(grid_size):
        ax.text(i + 0.5, grid_size + 0.2, str(i), ha='center', va='center', fontsize=12, fontweight='bold', color='black')
        ax.text(-0.2, grid_size - i - 0.5, str(i), ha='center', va='center', fontsize=12, fontweight='bold', color='black')

    for i, (target, op, cells) in enumerate(cages):
        color = cage_colors[i]
        for r, c in cells:
            ax.add_patch(plt.Rectangle((c, grid_size - r - 1), 1, 1, color=color, alpha=0.5))
        min_r, min_c = min(cells)
        ax.text(min_c + 0.05, grid_size - min_r - 0.15, f"{target}{op}", ha='left', va='top', fontsize=12, color='black', fontweight='bold')

    for r in range(grid_size):
        for c in range(grid_size):
            if mathdoku_grid[r, c] != 0:
                ax.text(c + 0.5, grid_size - r - 0.5, str(mathdoku_grid[r, c]),
                        ha='center', va='center', fontsize=16, color='black', fontweight='bold')

    plt.show()

def update_grid(row, col, value):
    global mathdoku_grid
    undo_stack.append(mathdoku_grid.copy())
    redo_stack.clear()
    mathdoku_grid[row, col] = value
    visualize_grid()


def undo():
    global mathdoku_grid
    if undo_stack:
        redo_stack.append(mathdoku_grid.copy())
        mathdoku_grid = undo_stack.pop()
        visualize_grid()

def redo():
    global mathdoku_grid
    if redo_stack:
        undo_stack.append(mathdoku_grid.copy())
        mathdoku_grid = redo_stack.pop()
        visualize_grid()

def reset_grid():
    global mathdoku_grid, undo_stack, redo_stack
    mathdoku_grid = np.zeros((grid_size, grid_size), dtype=int)
    undo_stack.clear()
    redo_stack.clear()
    visualize_grid()

reset_grid() #para mabura ang answer sa grid

def show_congratulations():
    fig, ax = plt.subplots(figsize=(6, 3))

    # Remove axes
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_frame_on(False)

    # Display text
    ax.text(0.5, 0.5, "🎉 Congratulations! 🎉", fontsize=20, color='purple',
            ha='center', va='center', fontweight='bold', fontstyle='italic')

    # Add confetti-like dots
    num_confetti = 30
    x_confetti = np.random.uniform(0, 1, num_confetti)
    y_confetti = np.random.uniform(0, 1, num_confetti)
    colors = [random.choice(['red', 'blue', 'green', 'orange', 'purple', 'pink']) for _ in range(num_confetti)]

    for x, y, color in zip(x_confetti, y_confetti, colors):
        ax.scatter(x, y, color=color, s=100, alpha=0.6)

    plt.show()

def validate_solution():
    for r in range(grid_size):
      for c in range(grid_size):
        if mathdoku_grid[r, c] != answer[r,c]:
            display(HTML("<p style='color:red; font-size:16px;'>❌ Incorrect. Try Again!</p>"))
            return
    display(HTML("<p style='color:green; font-size:16px;'>✅ Correct!</p>"))
    show_congratulations()

def hint():
    for r in range(grid_size):
        for c in range(grid_size):
            if mathdoku_grid[r, c] == 0:
                mathdoku_grid[r, c] = answer[r,c]
                visualize_grid()
                return
    print("No hints available!")

def new_game():
    global mathdoku_grid, cages
    mathdoku_grid = np.zeros((grid_size, grid_size), dtype=int)
    cages = generate_cages()
    cage_colors = {i: colors[i % len(colors)] for i in range(len(cages))}
    # Generate a solvable Mathdoku grid
    while not solve_mathdoku(mathdoku_grid, cages):
        mathdoku_grid = np.zeros((grid_size, grid_size), dtype=int)
        cages = generate_cages()
    reset_grid()


button_update.on_click(lambda b: update_grid(row_input.value, col_input.value, value_input.value))
button_undo.on_click(lambda b: undo())
button_redo.on_click(lambda b: redo())
button_reset.on_click(lambda b: reset_grid())
button_validate.on_click(lambda b: validate_solution())
button_hint.on_click(lambda b: hint())
button_new_game.on_click(lambda b: new_game())

display(row_input, col_input, value_input, widgets.HBox([button_update, button_undo, button_redo, button_reset, button_validate, button_hint]))
visualize_grid()