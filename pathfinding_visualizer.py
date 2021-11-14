import tkinter as tk
import time
import sys
from collections import deque
from queue import PriorityQueue
from tkinter import messagebox


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
options = ["Breadth-First-Pathfinding", "Depth-First-Pathfinding", "Dijkstra-Pathfinding", "A*-Pathfinding"]
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
    elif variable.get() == options[2]:
        dijkstra_shortest_path(adjacency_list_weighted, start, end)
    elif variable.get() == options[3]:
        a_star_shortest_path(adjacency_list_weighted, start, end)


click_count = 0
def adjust_start_end(event):
    global click_count, start, end
    click_count += 1
    if click_count == 1:
        canvas.create_rectangle(start[0], start[1], start[0] + TILE_SIZE, start[1] + TILE_SIZE, fill="white")
        start = (event.x // TILE_SIZE * TILE_SIZE, event.y // TILE_SIZE * TILE_SIZE)
        canvas.create_rectangle(start[0], start[1], start[0] + TILE_SIZE, start[1] + TILE_SIZE, fill="green")
        canvas.unbind("<B1-Motion>")
    elif click_count == 2:
        canvas.create_rectangle(end[0], end[1], end[0] + TILE_SIZE, end[1] + TILE_SIZE, fill="white")
        end = (event.x // TILE_SIZE * TILE_SIZE, event.y // TILE_SIZE * TILE_SIZE)
        canvas.create_rectangle(end[0], end[1], end[0] + TILE_SIZE, end[1] + TILE_SIZE, fill="red")
        click_count = 0
        canvas.unbind("<Button-1>")
        canvas.after(200, lambda: [canvas.bind("<B1-Motion>", draw_barrier), canvas.bind("<Button-1>", draw_barrier)])


def erase_start_end():
    canvas.create_rectangle(start[0], start[1], start[0] + TILE_SIZE, start[1] + TILE_SIZE, fill="white")
    canvas.create_rectangle(end[0], end[1], end[0] + TILE_SIZE, end[1] + TILE_SIZE, fill="white")


start_algorithm_btn = tk.Button(root, text="Start Algorithm", command=get_algorithm)
start_algorithm_btn.pack(side=tk.LEFT, padx=10)

clear_graph_btn = tk.Button(root, text="Clear Graph", command=lambda: [canvas.delete("all"), canvas.update(), create_start_and_end_tile(), draw_grid(), draw_border(), redraw_all_barriers()])
clear_graph_btn.pack(side=tk.LEFT, padx=10)

clear_board_btn = tk.Button(root, text="Clear Board", command=lambda: [canvas.delete("all"), canvas.update(), create_start_and_end_tile(), draw_grid(), draw_border(), reset_barrier()])
clear_board_btn.pack(side=tk.LEFT, padx=10)

set_start_end_btn = tk.Button(root, text="Set New Start & End", command=lambda: [canvas.bind("<Button-1>", adjust_start_end), erase_start_end()])
set_start_end_btn.pack(side=tk.LEFT, padx=10)


# Message that is shown when the target node is blocked off with barriers
def show_message():
    messagebox.showinfo("Not reachable", "Target could not be reached. You probably blocked it off with barriers.")


# Create start and end point
def create_start_and_end_tile():
    canvas.create_rectangle(start[0], start[1], start[0] + TILE_SIZE, start[1] + TILE_SIZE, fill="green")
    canvas.create_rectangle(end[0], end[1], end[0] + TILE_SIZE, end[1] + TILE_SIZE, fill="red")

create_start_and_end_tile()

# Reset barrier/border
def reset_barrier():
    global barrier_set
    barrier_set = set()

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


def redraw_all_barriers():
    for barrier in barrier_set:
        canvas.create_rectangle(barrier[0], barrier[1], barrier[0] + TILE_SIZE, barrier[1] + TILE_SIZE, fill="black")


def remove_barrier(e):
    x = e.x
    y = e.y
    x = (x // TILE_SIZE) * TILE_SIZE
    y = (y // TILE_SIZE) * TILE_SIZE
    global barrier_set
    if (x, y) in barrier_set:
        barrier_set.remove((x, y))
        canvas.create_rectangle(x, y, x+TILE_SIZE, y+TILE_SIZE, fill="white")


def is_inbounds(x, y):
    return x >= 0 and x <= (CANVAS_WIDTH - TILE_SIZE)  and y >= 0 and y <= (CANVAS_HEIGHT - TILE_SIZE) 


class Node:
    def __init__(self, x, y, state, weight) -> None:
        self.x = x
        self.y = y
        self.state = state # barrier, unvisited, currently visited, start/end...
        self.weight = weight
        self.neighbors = []


# Set nodes in grid
# (x-coordinate, y-coordinate, state) with state = barrier, start, end, currently visited...
grid = [[Node(x, y, "neutral", 1) for x in range(0, CANVAS_WIDTH, TILE_SIZE)] for y in range(0, CANVAS_HEIGHT, TILE_SIZE)]


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


def draw_grid():
    for y in range(0, CANVAS_HEIGHT, TILE_SIZE):
        canvas.create_line(0, y, CANVAS_WIDTH, y)
    for x in range(0, CANVAS_WIDTH, TILE_SIZE):
        canvas.create_line(x, 0, x, CANVAS_HEIGHT)
            

draw_grid()


# Fills out the specified tile if it's not the start or end point
def draw_spot(start, end, current):
    if current != start and current != end:
        canvas.create_rectangle(current[0], current[1], current[0] + TILE_SIZE, current[1] + TILE_SIZE, fill="orange")
        time.sleep(0.01)
        canvas.update()


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


def reconstruct_path(start, end, predecessors, current):
    path = deque()
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


def breadth_first_shortest_path(adjacency_list, start, end):
    visited = set([start])
    queue = deque([[start]])
    predecessors = {}
    while len(queue) > 0:
        [node] = queue.popleft()
        draw_spot(start, end, node)
        if node == end:
            reconstruct_path(start, end , predecessors, node)
            return
        for neighbor in adjacency_list[node]:
            if neighbor not in visited and neighbor not in barrier_set and neighbor not in border_set:
                predecessors[neighbor] = node
                visited.add(neighbor)
                queue.append([neighbor])
    show_message()
    return


def depth_first_algorithm(adjacency_list, start, end):
    visited = set()
    stack = [start]
    predecessors = {}
    while len(stack) > 0:
        current = stack.pop()
        if current != start:
            visited.add(current)
        if current == end: 
            reconstruct_path(start, end, predecessors, current)
            return
        draw_spot(start, end, current)
        for neighbor in adjacency_list[current]:
            if neighbor not in visited and neighbor not in barrier_set and neighbor not in border_set:
                predecessors[neighbor] = current
                stack.append(neighbor)
    show_message()
    return


# Creates weighted adjacency list for Dijkstra and A* algorithm (weighted pathfinding algorithms)
def create_weighted_adjacency_list(adjacency_list):
    adjacency_list_weighted = {}
    for node, neighbors in adjacency_list.items():
        adjacency_list_weighted[node] = dict()
        for neighbor in neighbors:
            adjacency_list_weighted[node][neighbor] = 1 # adjust node weight here
    return adjacency_list_weighted


adjacency_list_weighted = create_weighted_adjacency_list(adjacency_list)


def dijkstra_shortest_path(adjacency_list_weighted, start, end):
    visited = set()
    predecessors = {}
    dist = {}
    for key in adjacency_list_weighted.keys():
        dist[key] = sys.maxsize
    dist[start] = 0
    prio_queue = PriorityQueue()
    prio_queue.put((0, start))
    while not prio_queue.empty():
        min_val, current = prio_queue.get()
        visited.add(current)
        if dist[current] < min_val: continue
        for neighbor in adjacency_list_weighted[current]:
            if neighbor in visited or neighbor in border_set or neighbor in barrier_set: continue
            new_dist = min_val + adjacency_list_weighted[current][neighbor]
            if new_dist < dist[neighbor]:
                predecessors[neighbor] = current
                dist[neighbor] = new_dist
                prio_queue.put((dist[neighbor], neighbor))
        draw_spot(start, end, current)
        if current == end:
            reconstruct_path(start, end, predecessors, current)
            return
    show_message()
    return


# Finds shortest path the quickest way in a weighted graph using a heuristic
# function to make essentially educated guesses about the distance between
# the current node and the end node
def a_star_shortest_path(adjacency_list_weighted, start, end):
    open_set = PriorityQueue()  # set of discovered nodes that may need to be reexpanded
    open_set.put((0, start))
    predecessors = {}
    g_score = {}    # g_score[n] stores the cost of the cheapest path from start to node n currently known ("dist" in Dijkstra's algorithm)
    f_score = {}    # f_score[n] = g_score[n] + heuristics[n], heuristics is the educated guess about the distance (here the Manhattan Distance is used for that)
    for key in adjacency_list_weighted.keys():
        g_score[key] = sys.maxsize  # initializes every node with a max value due to the distance/weight currently unknown (like in Dijkstra's algorithm)
        f_score[key] = sys.maxsize
    g_score[start] = 0
    f_score[start] = heuristics(start, end)
    while not open_set.empty():
        min_val, current = open_set.get()
        if current == end:
            reconstruct_path(start, end, predecessors, current)
            return
        for neighbor in adjacency_list_weighted[current]:
            # d(current, neighbor) is the weight of the edge from current to neighbor
            # temp_g_score is the distance from start to the neighbor through current
            if neighbor in open_set.queue or neighbor in border_set or neighbor in barrier_set: continue
            temp_g_score = g_score[current] + 1 # d(current, neighbor) = 1 here
            if temp_g_score < g_score[neighbor]:
                # The path here is better than any previous one, so it gets tracked
                predecessors[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = g_score[neighbor] + heuristics(neighbor, end)
                if neighbor not in open_set.queue:
                    open_set.put((f_score[neighbor], neighbor))
        draw_spot(start, end, current)
    show_message()
    return


# Heuristics function used for the A* pathfinding algorithm
# Here the Manhattan Distance is used
def heuristics(start, end):
    return abs(start[0]//TILE_SIZE - end[0]//TILE_SIZE) + abs(start[1]//TILE_SIZE - end[1]//TILE_SIZE)


canvas.bind("<B1-Motion>", draw_barrier)
canvas.bind("<Button-1>", draw_barrier)
canvas.bind("<B3-Motion>", remove_barrier)
canvas.bind("<Button-3>", remove_barrier)
root.mainloop()