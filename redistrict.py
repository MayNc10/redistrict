import random
from copy import deepcopy

RED_SYM = 'R'
BLUE_SYM = 'B'
GREEN_SYM = 'G'

def get_free_neighbors(coord, board, width, height):
    x = coord[0]
    y = coord[1]
    free_list = []
    if (x > 0 and board[x - 1][y] == None):
        free_list.append((x - 1, y))
    if (x < width - 1 and board[x + 1][y] == None):
        free_list.append((x + 1, y))
    if (y > 0 and board[x][y - 1] == None):
        free_list.append((x, y - 1))
    if (y < height - 1 and board[x][y + 1] == None):
        free_list.append((x, y + 1))
    return free_list

def find_points_tarjan(idx, visited, disc, low, time, parent, isCV, board):
    visited[idx] = True
    time[0] += 1
    disc[idx] = low[idx] = time[0]
    children = 0
    coord = (idx // height, idx % height)
    for other in get_free_neighbors(coord, board, width, height):
        o_idx = other[0] * height + other[1]
        if not visited[o_idx]:
            children += 1
            find_points_tarjan(o_idx, visited, disc, low, time, idx, isCV, board)
            low[idx] = min(low[idx], low[o_idx])
            if parent != -1 and low[o_idx] >= disc[idx]:
                isCV[idx] = True
        elif o_idx != parent:
            low[idx] = min(low[idx], disc[o_idx])
    if parent == -1 and children > 1:
        isCV[idx] = True

# from https://www.geeksforgeeks.org/articulation-points-or-cut-vertices-in-a-graph/
def get_free_cut_verticies(board, width, height):
    disc = [None for _ in range (width * height)]
    low = [None for _ in range (width * height)]
    visited = [False for _ in range (width * height)]
    isCV = [False for _ in range (width * height)]
    time = [0]

    for idx in range(width * height):
        if not visited[idx] and board[idx // height][idx % height] is None:
            find_points_tarjan(idx, visited, disc, low, time, -1, isCV, board)
    result = [(idx / height, idx % height) for idx in range(width * height) if isCV[idx]]
    return result

def get_free_cut_verticies_naive(board, width, height):
    def dfs(idx, board, width, height, visited):
        visited[idx] = True
        for neighbor in get_free_neighbors((idx // height, idx % height), board, width, height):
            if not visited[neighbor[0] * height + neighbor[1]]:
                dfs(neighbor[0] * height + neighbor[1], board, width, height, visited)

    res = []
    for idx in range(width * height):
        visited = [False for _ in range(width * height)]
        visited[idx] = True
        comp = 0
        for o_coord in get_free_neighbors((idx // height, idx % height), board, width, height):
            o_idx = o_coord[0] * height + o_coord[1]
            if comp > 1:
                break
            if not visited[o_idx]:
                comp += 1
                dfs(o_idx, board, width, height, visited)
        if comp > 1:
            res.append((idx // height, idx % height))
    return res


# x,y addressing 
def make_board(width, height):
    n = width * height
    board = [[ None for y in range(height)] for x in range(width)]
    num_red = random.randrange(1, n - 2)
    num_blue = random.randrange(1, n - 1 - num_red)
    num_green = n - num_blue - num_red
    if (num_red + num_blue + num_green != n):
        print("Bug in generating districts")
    
    # generate red
    red_arr = [(random.randrange(width), random.randrange(height))]
    board[red_arr[0][0]][red_arr[0][1]] = RED_SYM
    num_red -= 1
    while num_red > 0:
        #print_board_with_cv(board, width, height)
        cut_verticies = get_free_cut_verticies_naive(board, width, height)
        free_list_nested = [get_free_neighbors(coord, board, width, height) for coord in red_arr]
        free_list = [x for xs in free_list_nested for x in xs if x not in cut_verticies]
        next = free_list[random.randrange(len(free_list))]
        red_arr.append(next)
        board[next[0]][next[1]] = RED_SYM
        num_red -= 1
    # generate blue
    free_list_nested_r = [get_free_neighbors(coord, board, width, height) for coord in red_arr]
    cut_verticies_r = get_free_cut_verticies_naive(board, width, height)
    free_list_r = [x for xs in free_list_nested_r for x in xs if x not in cut_verticies_r]
    blue_arr = [free_list_r[random.randrange(len(free_list_r))]]
    board[blue_arr[0][0]][blue_arr[0][1]] = BLUE_SYM
    num_blue -= 1
    while num_blue > 0:
        #print_board_with_cv(board, width, height)
        cut_verticies = get_free_cut_verticies_naive(board, width, height)
        free_list_nested = [get_free_neighbors(coord, board, width, height) for coord in blue_arr]
        free_list = [x for xs in free_list_nested for x in xs if x not in cut_verticies]
        if len(free_list) == 0:
            #print_board_with_cv(board, width, height)
            #print("Can't claim any squares!")
            #print("Num left: ", num_blue)
            #print("Free verticies with cvs:", [x for xs in free_list_nested for x in xs])
            # find free sections    
            q = [[(x, y)] for x in range(width) for y in range(height) if board[x][y] == None and (x, y) not in cut_verticies]
            s = lambda x: len(x)
            failed = False
            while len(q) > 0:
                c_list = q.pop(0)
                print("In group bfs, smallest path is ", len(c_list))
                print("num blue: ", num_blue)
                print_board_with_cv(board, width, height)
                print("path: ")
                for coord in c_list:
                    print(coord[0], ", ", coord[1], "(", board[coord[0]][coord[1]], ")")
                print()
                if len(c_list) - 1 > num_blue:
                    failed = True
                    break
                if board[c_list[-1][0]][c_list[-1][1]] == BLUE_SYM:
                    # found free
                    for coord in c_list[:-1]:
                        board[coord[0]][coord[1]] = BLUE_SYM
                        num_blue -= 1
                    break
                x = c_list[-1][0]
                y = c_list[-1][1]
                # todo optimize
                if (x > 0 and ((x - 1, y) in cut_verticies or (x-1, y) in blue_arr) ):
                    nl = deepcopy(c_list)
                    nl.append((x - 1, y))
                    q.append(nl)
                if (x < width - 1 and ((x + 1, y) in cut_verticies or (x+1,y) in blue_arr) ):
                    nl = deepcopy(c_list)
                    nl.append((x + 1, y))
                    q.append(nl)
                if (y > 0 and ((x, y - 1) in cut_verticies or (x, y-1) in blue_arr)):
                    nl = deepcopy(c_list)
                    nl.append((x, y - 1))
                    q.append(nl)
                if (y < height - 1 and ((x, y + 1) in cut_verticies or (x,y+1) in blue_arr)):
                    nl = deepcopy(c_list)
                    nl.append((x, y + 1))
                    q.append(nl)
                
                q.sort(key=s)
            if failed:
                print("BFS for free group failed!")
                return None
            #else:
                #print("BFS Succeeded!")
        else:
            next = free_list[random.randrange(len(free_list))]
            blue_arr.append(next)
            board[next[0]][next[1]] = BLUE_SYM
            num_blue -= 1

    for x in range(width):
        for y in range(height):
            if board[x][y] is None:
                board[x][y] = GREEN_SYM
    
    return board

def check_board(board, width, height):
    syms = [RED_SYM, BLUE_SYM, GREEN_SYM]
    if len(board) != width:
        return False
    for x in range(width):
        if len(board[x]) != height:
            return False
        for y in range(height):
            if board[x][y] not in syms:
                return False

    def check_color(board, width, height, color):
        coord = None
        for x in range(width):
            for y in range(height):
                if board[x][y] == color:
                    coord = (x, y)
                    break
            if coord is not None:
                break
        if coord is None:
            return False
        # dfs
        def dfs(board, width, height, color,x, y):
            board[x][y] = None
            if x > 0 and board[x - 1][y] == color:
                dfs(board, width, height, color, x - 1, y)
            if x < width - 1 and board[x+1][y] == color:
                dfs(board, width, height, color, x+1, y)
            if y > 0 and board[x][y-1] == color:
                dfs(board, width, height, color, x, y-1)
            if y < height - 1 and board[x][y+1] == color:
                dfs(board, width, height, color, x, y+1)
        dfs(board, width, height, color, coord[0], coord[1])
        for x in range(width):
            for y in range(height):
                if board[x][y] == color:
                    return False
        return True
    
    return (check_color(deepcopy(board), width, height, RED_SYM) and check_color(deepcopy(board), width, height, BLUE_SYM) and check_color(deepcopy(board), width, height, GREEN_SYM))

#inclusive on both ends
def gen_benchmark(min_size, max_size, runs_per):
    total = (max_size - min_size + 1) * runs_per
    steps = 0
    fails = 0
    for size in range(min_size, max_size + 1):
        for run in range(runs_per):
            print(">>> ", steps / total * 100, "%")
            board = make_board(size, size)
            if board is None:
                fails += 1
            elif not check_board(board, size, size):
                fails += 1
            steps += 1
    print("Total error rate: ", (fails / total) * 100.0, "%")

def print_board(board, width, height):
    for y in range(height):
        for x in range(width):
            if (board[x][y] is None):
                print("_", end=" ")
            else:
                print(board[x][y], end=" ")
        print("\n")
    print("\n")

def print_board_with_cv(board, width, height):
    cut_verticies = get_free_cut_verticies_naive(board, width, height)
    for y in range(height):
        for x in range(width):
            if (x, y) in cut_verticies:
                print("C", end=" ")
            elif (board[x][y] is None):
                print("_", end=" ")
            else:
                print(board[x][y], end=" ")
        print("\n")
    print("\n")

width = 5
height = 5
#board = make_board(width, height)
#print_board(board, width, height)
#print(check_board(board, width, height))
gen_benchmark(5, 100, 1000)
