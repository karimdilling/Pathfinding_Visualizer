import tkinter as tk
import time
from collections import deque


# Setup window
root = tk.Tk()
root.title("Pathfinding Visualizer")
root.geometry("1000x600")
root.resizable(False, False)
CANVAS_WIDTH = 1000
CANVAS_HEIGHT = 500
TILE_SIZE = 20 # Tile size of the grid
start = (280, 80)
end = (660, 160)

# Configure canvas
canvas = tk.Canvas(root, bg="white", width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
canvas.pack(side=tk.TOP)

# Put buttons in place
options = ["Breadth-First-Pathfinding", "Depth-First-Pathfinding"]
variable = tk.StringVar()
variable.set(options[0])
choose_algorithm_menu = tk.OptionMenu(root, variable, *options)
choose_algorithm_menu.pack(side=tk.LEFT, padx= 10)

# Detects which algorithm was selected
def get_algorithm():
    if variable.get() == options[0]:
        breadth_first_shortest_path(adjacency_list, start, end)
    elif variable.get() == options[1]:
        depth_first_algorithm(adjacency_list, start, end)

start_algorithm_btn = tk.Button(root, text="Start Algorithm", command=get_algorithm)
start_algorithm_btn.pack(side=tk.LEFT, padx=10)

# Create start and end point
canvas.create_rectangle(start[0], start[1], start[0] + TILE_SIZE, start[1] + TILE_SIZE, fill="green")
canvas.create_rectangle(end[0], end[1], end[0] + TILE_SIZE, end[1] + TILE_SIZE, fill="red")


barrier_set = set()

def draw_barrier(e):
    x = e.x
    y = e.y
    x = (x // TILE_SIZE) * TILE_SIZE
    y = (y // TILE_SIZE) * TILE_SIZE
    global barrier_set
    if (x, y) not in barrier_set:
        barrier_set.add((x, y))
        canvas.create_rectangle(x, y, x+TILE_SIZE, y+TILE_SIZE, fill="black")
        # print(barrier_set)

def remove_barrier(e):
    x = e.x
    y = e.y
    x = (x // TILE_SIZE) * TILE_SIZE
    y = (y // TILE_SIZE) * TILE_SIZE
    global barrier_set
    if (x, y) in barrier_set:
        barrier_set.remove((x, y))
        canvas.create_rectangle(x, y, x+TILE_SIZE, y+TILE_SIZE, fill="white")
        # print(barrier_set)


def is_inbounds(x, y):
    return x >= 0 and x <= (CANVAS_WIDTH - TILE_SIZE)  and y >= 0 and y <= (CANVAS_HEIGHT - TILE_SIZE) 


class Node:
    def __init__(self, x, y, state) -> None:
        self.x = x
        self.y = y
        self.state = state # barrier, unvisited, currently visited, start/end...
        self.neighbors = []


# Set nodes in grid
# (x-coordinate, y-coordinate, state) with state = barrier, start, end, currently visited...
grid = [[Node(x, y, "neutral") for x in range(0, CANVAS_WIDTH, TILE_SIZE)] for y in range(0, CANVAS_HEIGHT, TILE_SIZE)]


# Set neighbors of nodes
def set_neighbors(grid):
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            # All inner nodes with 4 neighbors
            if grid[i][j].y >= TILE_SIZE and grid[i][j].y <= CANVAS_HEIGHT-2*TILE_SIZE and grid[i][j].x >= TILE_SIZE and grid[i][j].x <= CANVAS_WIDTH-2*TILE_SIZE:
                grid[i][j].neighbors.extend([grid[i-1][j], grid[i+1][j], grid[i][j-1], grid[i][j+1]])
    # Top left
    grid[0][0].neighbors.extend([grid[1][0], grid[0][1]])
    # Top right
    grid[0][len(grid[0])-1].neighbors.extend([grid[1][len(grid[0])-1], grid[0][len(grid[0])-2]])
    # Bottom left
    grid[len(grid)-1][0].neighbors.extend([grid[len(grid)-1][1], grid[len(grid)-2][0]])
    # Bottom right
    grid[len(grid)-1][len(grid[0])-1].neighbors.extend([grid[len(grid)-1][len(grid[0])-2], grid[len(grid)-2][len(grid[0])-1]])
    # Top row except corners (3 neighbors each)
    for i in range(1, len(grid[0])-1): # 2nd to 2nd last
        grid[0][i].neighbors.extend([grid[0][i-1], grid[0][i+1], grid[1][i]])
    # Bottom row except corners (3 neighbors each)
        grid[len(grid)-1][i].neighbors.extend([grid[0][i-1], grid[0][i+1], grid[len(grid)-2][i]])
    # Left column without corners (3 neighbors each)
    for i in range(1, len(grid)-1):
        grid[i][0].neighbors.extend([grid[i-1][0], grid[i+1][0], grid[i][1]])
    # Right column without corners (3 neighbors each)
        grid[i][len(grid[0])-1].neighbors.extend([grid[i-1][len(grid[0])-1], grid[i+1][len(grid[0])-1], grid[i][len(grid[0])-2]])


set_neighbors(grid)

border_set = set()

# Draw border around window frame
def draw_border():
    global border_set
    for x in range(0, CANVAS_WIDTH, TILE_SIZE):
        border_set.add((x, 0))
        border_set.add((x, CANVAS_HEIGHT - TILE_SIZE))
        canvas.create_rectangle(x, 0, x + TILE_SIZE, TILE_SIZE, fill="black")
        canvas.create_rectangle(x, CANVAS_HEIGHT - TILE_SIZE, x + TILE_SIZE, CANVAS_HEIGHT, fill="black")
    for y in range(0, CANVAS_HEIGHT, TILE_SIZE):
        border_set.add((0, y))
        border_set.add((CANVAS_WIDTH - TILE_SIZE, y))
        canvas.create_rectangle(0, y, TILE_SIZE, y + TILE_SIZE, fill="black")
        canvas.create_rectangle(CANVAS_WIDTH - TILE_SIZE, y, CANVAS_WIDTH, y + TILE_SIZE, fill="black")

draw_border()

def draw_start_end():
    canvas.create_rectangle(5*TILE_SIZE, 5*TILE_SIZE, 5*TILE_SIZE+TILE_SIZE, 5*TILE_SIZE+TILE_SIZE, fill="green")   # Start point
    canvas.create_rectangle(35*TILE_SIZE, 15*TILE_SIZE, 35*TILE_SIZE+TILE_SIZE, 15*TILE_SIZE+TILE_SIZE, fill="red") # End point

def draw_spots():
    canvas.create_rectangle(grid[3][2].x, grid[3][2].y, grid[3][2].x+TILE_SIZE, grid[3][2].y+TILE_SIZE, fill="blue")
    for neighbor in grid[3][2].neighbors:
        canvas.create_rectangle(neighbor.x, neighbor.y, neighbor.x+TILE_SIZE, neighbor.y+TILE_SIZE, fill="yellow")


def draw_grid():
    for y in range(0, CANVAS_HEIGHT, TILE_SIZE):
        canvas.create_line(0, y, CANVAS_WIDTH, y)
    for x in range(0, CANVAS_WIDTH, TILE_SIZE):
        canvas.create_line(x, 0, x, CANVAS_HEIGHT)
            

# draw_start_end()
# draw_spots()
draw_grid()

# Create adjacency list that can be used by pathfinding algorithms
def get_adjacency_list(grid):
    adjacency_list = {}
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            node_key = (grid[i][j].x, grid[i][j].y)
            neighbor_list = []
            for neighbor in grid[i][j].neighbors:
                neighbor_list.append((neighbor.x, neighbor.y))
            adjacency_list[node_key] = neighbor_list
    return adjacency_list

adjacency_list = get_adjacency_list(grid)
# for node, neighbors in adjacency_list.items():
#     print(str(node) + " : " + str(neighbors))


def breadth_first_shortest_path(adjacency_list, start, end):
    visited = set([start])
    queue = deque([[start]])
    predecessors = {}
    path = deque()
    canvas.create_rectangle(start[0], start[1], start[0] + TILE_SIZE, start[1] + TILE_SIZE, fill="green")
    canvas.create_rectangle(end[0], end[1], end[0] + TILE_SIZE, end[1] + TILE_SIZE, fill="red")
    while len(queue) > 0:
        [node] = queue.popleft()
        if node == end:
            while node in predecessors:
                node = predecessors[node]
                if node != end and node != start:
                    path.appendleft(node)
                if node == start:
                    break
            for node in path:
                canvas.create_rectangle(node[0], node[1], node[0] + TILE_SIZE, node[1] + TILE_SIZE, fill="yellow")
                time.sleep(0.01)
                canvas.update()
            return
        for neighbor in adjacency_list[node]:
            if neighbor not in visited and neighbor not in barrier_set and neighbor not in border_set:
                predecessors[neighbor] = node
                visited.add(neighbor)
                queue.append([neighbor])
        if node != start:
            canvas.create_rectangle(node[0], node[1], node[0] + TILE_SIZE, node[1] + TILE_SIZE, fill="orange")
            time.sleep(0.01)
            canvas.update()


def depth_first_algorithm(adjacency_list, start, end):
    visited = set()
    stack = [start]
    predecessors = {}
    path = deque()
    while len(stack) > 0:
        current = stack.pop()
        if current != start:
            visited.add(current)
        if current == end: 
            while current in predecessors:
                current = predecessors[current]
                if current != end and current != start:
                    path.appendleft(current)
                if current == start:
                    break
            for current in path:
                canvas.create_rectangle(current[0], current[1], current[0] + TILE_SIZE, current[1] + TILE_SIZE, fill="yellow")
                time.sleep(0.01)
                canvas.update()
            return
        if current != start:
            canvas.create_rectangle(current[0], current[1], current[0] + TILE_SIZE, current[1] + TILE_SIZE, fill="orange")
            time.sleep(0.01)
            canvas.update()
        for neighbor in adjacency_list[current]:
            if neighbor not in visited and neighbor not in barrier_set and neighbor not in border_set:
                predecessors[neighbor] = current
                stack.append(neighbor)


canvas.bind("<B1-Motion>", draw_barrier)
canvas.bind("<Button-1>", draw_barrier)
canvas.bind("<B3-Motion>", remove_barrier)
canvas.bind("<Button-3>", remove_barrier)
root.mainloop()