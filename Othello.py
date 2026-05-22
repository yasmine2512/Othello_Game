import copy
import time
import pygame
import sys

# Initialize pygame
pygame.init()
clock = pygame.time.Clock()
# Window dimensions
WIDTH, HEIGHT = 600, 630
BOARD_SIZE = 520
MARGIN_X = (WIDTH - BOARD_SIZE) // 2
MARGIN_Y = (HEIGHT - BOARD_SIZE) // 2
# Colors
BG = (0, 30, 30)
GREEN = (0, 100, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY_BLACK = (0, 70, 0)
LIGHT_GRAY = (90, 150,90)
BLUE = (0, 0, 255)
TEXT_COL    = (210, 210, 200)
DIM_COL     = (110, 110, 100)
BOARD_COL   = (40, 100, 60)
ACCENT      = (180, 160, 90)  

# Board constants
ROWS, COLS = 8, 8
CELL_SIZE = BOARD_SIZE // COLS
DIFFICULTY = {"Easy": 1, "Medium": 3, "Hard": 5}

# Create window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Othello")
# font = pygame.font.Font(None, 150)
small_font = pygame.font.Font(None, 35)

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect(center=(x, y))
    surface.blit(textobj, textrect)

pygame.font.init()
font = pygame.font.SysFont("arial", 20, bold=True)
# font1 = pygame.font.SysFont("arialblack", 80)
# small_fontfont = pygame.font.SysFont("arialblack", 35)
font_big   = pygame.font.SysFont("DejaVu Sans", 54, bold=True)
font_med   = pygame.font.SysFont("DejaVu Sans", 26, bold=True)
font_small = pygame.font.SysFont("DejaVu Sans", 18)
def minmax(board, depth, maximizingPlayer,alpha=float('-inf'), beta=float('inf')):
    
    if depth == 0:
        return evaluate_board(board),None
    if maximizingPlayer:
        best_value = float('-inf')
        best_move = None
        moves = get_valid_moves(WHITE,board)
        if not moves:  # no valid moves
            return evaluate_board(board), None
        for move,flips in moves.items():
            new_board = apply_move(board,move,WHITE,flips)
            value, _ = minmax(new_board, depth - 1, False,alpha,beta)
            if value > best_value: best_value, best_move = value, move
            alpha = max(alpha, value)
            if beta <= alpha: break
        
        return best_value,best_move

    else:
        best_value = float('inf')
        best_move = None
        moves = get_valid_moves(BLACK,board)
        if not moves:  # no valid moves
            return evaluate_board(board), None
        for move,flips in moves.items():
            new_board = apply_move(board,move,BLACK,flips)
            value, _ = minmax(new_board,depth - 1, True,alpha,beta)
            if value < best_value: best_value, best_move = value, move
            beta = min(beta, value)
            if beta <= alpha: break

        return best_value,best_move

def txt(text, font, color, x, y):
    s = font.render(text, True, color)
    screen.blit(s, s.get_rect(center=(x, y)))

def button(rect, label, font, hovered):
    col = (55, 55, 50) if hovered else (42, 42, 38)
    pygame.draw.rect(screen, col, rect, border_radius=4)
    pygame.draw.rect(screen, ACCENT if hovered else DIM_COL, rect, 1, border_radius=4)
    txt(label, font, TEXT_COL if hovered else DIM_COL, rect.centerx, rect.centery)


selected_cell = None 
def draw_board(board,hints,hintcol):

    screen.fill(BG)

    black_n = sum(1 for (_, _, c) in board if c == BLACK)
    white_n = sum(1 for (_, _, c) in board if c == WHITE)
    turn = "Black" if hintcol == GRAY_BLACK else "White"
    txt(f"Black  {black_n}", font_small, TEXT_COL, MARGIN_X + 50, MARGIN_Y -42)
    txt(f"{turn}'s turn", font_small, ACCENT,    WIDTH // 2,   MARGIN_Y - 42)
    txt(f"White  {white_n}", font_small, TEXT_COL, MARGIN_X + BOARD_SIZE - 50, MARGIN_Y - 42)
    board_rect = pygame.Rect(MARGIN_X, MARGIN_Y, BOARD_SIZE, BOARD_SIZE)
    pygame.draw.rect(screen, BOARD_COL, board_rect)

    for i in range(ROWS + 1):

        pygame.draw.line(screen, BLACK, 
                         (MARGIN_X, MARGIN_Y + i * CELL_SIZE), 
                         (MARGIN_X + BOARD_SIZE, MARGIN_Y + i * CELL_SIZE), 2)
        pygame.draw.line(screen, BLACK, 
                         (MARGIN_X + i * CELL_SIZE, MARGIN_Y), 
                         (MARGIN_X + i * CELL_SIZE, MARGIN_Y + BOARD_SIZE), 2)

    for i in range(COLS):
        letter = chr(65 + i)  
        text = font.render(letter, True, DIM_COL)
        text_rect = text.get_rect(center=(MARGIN_X + i * CELL_SIZE + CELL_SIZE / 2, MARGIN_Y - 15))
        screen.blit(text, text_rect)

        text_rect = text.get_rect(center=(MARGIN_X + i * CELL_SIZE + CELL_SIZE / 2, MARGIN_Y + BOARD_SIZE + 15))
        screen.blit(text, text_rect)

    for i in range(ROWS):
        number = str(i + 1)
        text = font.render(number, True, DIM_COL)
        text_rect = text.get_rect(center=(MARGIN_X - 15, MARGIN_Y + i * CELL_SIZE + CELL_SIZE / 2))
        screen.blit(text, text_rect)

        # Row labels (right)
        text_rect = text.get_rect(center=(MARGIN_X + BOARD_SIZE + 15, MARGIN_Y + i * CELL_SIZE + CELL_SIZE / 2))
        screen.blit(text, text_rect)
    # hint dots
    if(hints):
        for (r, c),col in hints.items():
            cx = MARGIN_X + c * CELL_SIZE + CELL_SIZE // 2
            cy = MARGIN_Y + r * CELL_SIZE + CELL_SIZE // 2
            pygame.draw.circle(screen, hintcol, (cx, cy), 6)

    # pieces
    for (r, c, col) in board:
        cx = MARGIN_X + c * CELL_SIZE + CELL_SIZE // 2
        cy = MARGIN_Y + r * CELL_SIZE + CELL_SIZE // 2
        rad = CELL_SIZE // 2 - 5
        pygame.draw.circle(screen, col, (cx, cy), rad)
        outline = (160, 158, 150) if col == WHITE else (55, 55, 60)
        pygame.draw.circle(screen, outline, (cx, cy), rad, 1)   

clicked_cells = [(3,3,WHITE),(4,4,WHITE),(4,3,BLACK),(3,4,BLACK)]


def highlight_cell(row,col,color):
     x = MARGIN_X + col * CELL_SIZE + CELL_SIZE // 2
     y = MARGIN_Y + row * CELL_SIZE + CELL_SIZE // 2
     pygame.draw.circle(screen, color, (x, y), CELL_SIZE // 2 - 10)

def get_piece(row, col):
    for (r, c, color) in clicked_cells:
        if r == row and c == col:
            return color
    return None 

def is_on_board(row, col):
    return 0 <= row < 8 and 0 <= col < 8


directions = [
    (-1, 0),  # up
    (1, 0),   # down
    (0, -1),  # left
    (0, 1),   # right
    (-1, -1), # up-left
    (-1, 1),  # up-right
    (1, -1),  # down-left
    (1, 1)    # down-right
]


def get_valid_moves(color, clicked_cells):
    opponent = WHITE if color == BLACK else BLACK
    valid_moves = {}  

    for (row, col, clr) in clicked_cells:
        if clr != color:
            continue  

        for dr, dc in directions:
            r, c = row + dr, col + dc
            line = []

            while 0 <= r < 8 and 0 <= c < 8:
                current = get_piece(r, c)
                if current == opponent:
                    line.append((r, c))
                    r += dr
                    c += dc
                elif current is None:
                    if len(line) > 0:
                        if (r, c) in valid_moves:
                            valid_moves[(r, c)].extend(line)
                        else:
                            valid_moves[(r, c)] = line.copy()
                    break
                else:
                    break

    return valid_moves

def apply_move(board, move, color, flips):

    new_board = copy.deepcopy(board)
    row, col = move
    new_board.append((row, col, color))
    
    for (r, c) in flips:
        for i, (row, col, clr) in enumerate(new_board):
            if row == r and col == c:
                new_board[i] = (row, col, color)
                break

    return new_board

# def evaluate_board(board):
#     white_count = sum(1 for (_, _, c) in board if c == WHITE)
#     black_count = sum(1 for (_, _, c) in board if c == BLACK)
#     return white_count - black_count  # positive if white leads

WEIGHTS = [
    [100,-20,10, 5, 5,10,-20,100],
    [-20,-50, 1, 1, 1, 1,-50,-20],
    [ 10,  1, 5, 2, 2, 5,  1, 10],
    [  5,  1, 2, 1, 1, 2,  1,  5],
    [  5,  1, 2, 1, 1, 2,  1,  5],
    [ 10,  1, 5, 2, 2, 5,  1, 10],
    [-20,-50, 1, 1, 1, 1,-50,-20],
    [100,-20,10, 5, 5,10,-20,100],
]

def evaluate_board(board):
    score = 0
    for (r, c, col) in board:
        score += WEIGHTS[r][c] if col == WHITE else -WEIGHTS[r][c]
    return score

def calc_winner(board):
    b = sum(1 for (_, _, c) in board if c == BLACK)
    w = sum(1 for (_, _, c) in board if c == WHITE)
    if b > w: return f"Black wins  {b} – {w}"
    if w > b: return f"White wins  {w} – {b}"
    return f"Draw  {b} – {b}"

def game_over_overlay(result):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))
    panel = pygame.Rect(WIDTH // 2 - 180, HEIGHT // 2 - 80, 360, 160)
    pygame.draw.rect(screen, (38, 38, 35), panel, border_radius=6)
    pygame.draw.rect(screen, DIM_COL, panel, 1, border_radius=6)
    txt("Game Over", font_med, TEXT_COL, WIDTH // 2, HEIGHT // 2 - 40)
    txt(result, font_small, DIM_COL,  WIDTH // 2, HEIGHT // 2)
    btn = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 + 28, 160, 36)
    mx, my = pygame.mouse.get_pos()
    button(btn, "Main Menu", font_small, btn.collidepoint((mx, my)))
    return btn


def player_vs_robot(depth):
    global clicked_cells
    color = BLACK 
    possible_positions = get_valid_moves(color,clicked_cells)
    game_over = False
    draw_board(clicked_cells,None,None)
    pygame.display.update()
  
    running = True
    while running:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if game_over:
                menu_btn = game_over_overlay(result)
                pygame.display.flip()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if menu_btn.collidepoint(event.pos):
                        main_menu()
                        return
                continue
            if color == BLACK:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()

                    if (MARGIN_X <= mx <= MARGIN_X + BOARD_SIZE) and (MARGIN_Y <= my <= MARGIN_Y + BOARD_SIZE):
                        col = (mx - MARGIN_X) // CELL_SIZE
                        row = (my - MARGIN_Y) // CELL_SIZE
                    
                        if not any(r == row and c == col for (r, c, _) in clicked_cells):
                            if (row, col) in possible_positions:
                                clicked_cells.append((row, col,BLACK))
                                for (r, c) in possible_positions[(row, col)]:
                                    for i, (rr, cc, cc_color) in enumerate(clicked_cells):
                                        if rr == r and cc == c:
                                            clicked_cells[i] = (rr, cc, color)
                                            break       
                                draw_board(clicked_cells,None,None)        
                                pygame.display.update() 
                                pygame.time.wait(600)   
                                color = WHITE 
                                possible_positions = get_valid_moves(color,clicked_cells)
                                if not possible_positions:
                                    color = BLACK
                                    possible_positions = get_valid_moves(color,clicked_cells)
                                    if not possible_positions:
                                        game_over = True
                                        result = calc_winner(clicked_cells)
            else:                    
                        value, move = minmax(clicked_cells,depth, True)
                        row, col = move
                        clicked_cells.append((row,col,color))
                        for (r, c) in possible_positions[(row, col)]:
                            for i, (rr, cc, cc_color) in enumerate(clicked_cells):
                                if rr == r and cc == c:
                                    clicked_cells[i] = (rr, cc, color)
                                    break
                        draw_board(clicked_cells,None,None)        
                        pygame.display.update()                   
                        color = BLACK    
                        possible_positions = get_valid_moves(color,clicked_cells) 
                        if not possible_positions:
                                    color = WHITE
                                    possible_positions = get_valid_moves(color,clicked_cells)
                                    if not possible_positions:
                                        game_over = True
                                        result = calc_winner(clicked_cells)       
 
        if color == BLACK:    
            # for (row, col),line_cell in possible_positions.items():
            #     cx = MARGIN_X + col * CELL_SIZE + CELL_SIZE // 2
            #     cy = MARGIN_Y + row * CELL_SIZE + CELL_SIZE // 2
            #     pygame.draw.circle(screen, GRAY_BLACK, (cx, cy), 6)
            draw_board(clicked_cells,possible_positions,GRAY_BLACK)

        pygame.display.flip()
        

    pygame.quit()
    sys.exit()
    

def play_1v1():
    global clicked_cells
    color = BLACK 
    possible_positions = get_valid_moves(color,clicked_cells)
    draw_board(clicked_cells,None,None)        
    pygame.display.update() 
    game_over = False
    result=""
    # Main loop
    running = True
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False 

            if game_over:
                menu_btn = game_over_overlay(result)
                pygame.display.flip()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if menu_btn.collidepoint(event.pos):
                        main_menu()
                        return
                continue
         
    # Mouse click event
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()

                # Check if click inside board
                if (MARGIN_X <= mx <= MARGIN_X + BOARD_SIZE) and (MARGIN_Y <= my <= MARGIN_Y + BOARD_SIZE):
                    col = (mx - MARGIN_X) // CELL_SIZE
                    row = (my - MARGIN_Y) // CELL_SIZE
                    
                    if not any(r == row and c == col for (r, c, _) in clicked_cells):
                        if (row, col) in possible_positions:
                            clicked_cells.append((row, col,color))
                            for (r, c) in possible_positions[(row, col)]:
                            # find that cell in clicked_cells and flip its color
                                for i, (rr, cc, cc_color) in enumerate(clicked_cells):
                                    if rr == r and cc == c:
                                        clicked_cells[i] = (rr, cc, color)
                                        break
                            c = GRAY_BLACK if color == BLACK else LIGHT_GRAY
                            draw_board(clicked_cells,possible_positions,c)        
                            pygame.display.update()         
                            pygame.time.wait(600) 
                            color = WHITE if color == BLACK else BLACK
                            possible_positions = get_valid_moves(color,clicked_cells)
                            if not possible_positions:
                                    color = WHITE if color == BLACK else BLACK
                                    possible_positions = get_valid_moves(color,clicked_cells)
                                    if not possible_positions:
                                        game_over = True
                                        result = calc_winner(clicked_cells)

            c = GRAY_BLACK if color == BLACK else LIGHT_GRAY                    
            draw_board(clicked_cells,possible_positions,c)
            for (row, col,clr) in clicked_cells:
                highlight_cell(row, col,clr)
       
        pygame.display.flip()
    pygame.quit()
    sys.exit()

def main_menu(): 
    global clicked_cells
    clicked_cells = [(3,3,WHITE),(4,4,WHITE),(4,3,BLACK),(3,4,BLACK)]
    cx = WIDTH // 2
    bw, bh = 220, 44
    btns = [
        ("1 vs 1",    pygame.Rect(cx - bw//2, 280, bw, bh)),
        ("vs Robot",  pygame.Rect(cx - bw//2, 340, bw, bh)),
        ("Quit",      pygame.Rect(cx - bw//2, 400, bw, bh)),
    ]
    while True:
        screen.fill(BG)
        txt("OTHELLO", font_big, TEXT_COL, cx, 160)
        pygame.draw.line(screen, DIM_COL, (cx - 100, 195), (cx + 100, 195), 1)

        mx, my = pygame.mouse.get_pos()
        for label, r in btns:
            button(r, label, font_med, r.collidepoint((mx, my)))

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                if btns[0][1].collidepoint((mx, my)): play_1v1()
                if btns[1][1].collidepoint((mx, my)): difficulty_menu()
                if btns[2][1].collidepoint((mx, my)): pygame.quit(); sys.exit()

        pygame.display.flip()
        clock.tick(60)


def difficulty_menu():
    cx = WIDTH // 2
    bw, bh = 220, 44
    diff_btns = [
        ("Easy",   pygame.Rect(cx - bw//2, 280, bw, bh)),
        ("Medium", pygame.Rect(cx - bw//2, 340, bw, bh)),
        ("Hard",   pygame.Rect(cx - bw//2, 400, bw, bh)),
    ]
    while True:
        screen.fill(BG)
        txt("Difficulty", font_big, TEXT_COL, cx, 160)
        pygame.draw.line(screen, DIM_COL, (cx - 100, 195), (cx + 100, 195), 1)

        mx, my = pygame.mouse.get_pos()
        hover_lbl = None
        for label, r in diff_btns:
            hov = r.collidepoint((mx, my))
            if hov: hover_lbl = label
            button(r, label, font_med, hov)


        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                for label, r in diff_btns:
                    if r.collidepoint((mx, my)):
                        player_vs_robot(DIFFICULTY[label]); return
                # if back.collidepoint((mx, my)): return

        pygame.display.flip()
        clock.tick(60)


main_menu()