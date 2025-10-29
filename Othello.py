import copy
import time
import pygame
import sys

# Initialize pygame
pygame.init()

# Window dimensions
WIDTH, HEIGHT = 600, 600
BOARD_SIZE = 520
MARGIN = (WIDTH - BOARD_SIZE) // 2  # Space for labels
# Colors
GREEN = (0, 100, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY_BLACK = (0, 70, 0)
LIGHT_GRAY = (90, 150,90)
BLUE = (0, 0, 255)

# Board constants
ROWS, COLS = 8, 8
CELL_SIZE = BOARD_SIZE // COLS

# Create window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Othello")
font = pygame.font.Font(None, 150)
small_font = pygame.font.Font(None, 35)

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect(center=(x, y))
    surface.blit(textobj, textrect)

pygame.font.init()
font = pygame.font.SysFont("arial", 20, bold=True)
font1 = pygame.font.SysFont("arialblack", 80)
small_fontfont = pygame.font.SysFont("arialblack", 35)
def minmax(board, depth, maximizingPlayer):
    
    if depth == 0:
        return evaluate_board(board),None
    if maximizingPlayer:
        best_value = float('-inf')
        best_move = None
        moves = get_valid_moves(WHITE,board)
        if not moves:  # no valid moves
            return evaluate_board(board), None
        for i,(move,flips) in enumerate(moves.items()):
            new_board = apply_move(board,move,WHITE,flips)
            value, _ = minmax(new_board, depth - 1, False)
            if value > best_value:
                best_value = value
                best_move = move
        
        return best_value,best_move

    else:
        best_value = float('inf')
        best_move = None
        moves = get_valid_moves(BLACK,board)
        if not moves:  # no valid moves
            return evaluate_board(board), None
        for i,(move,flips) in enumerate(moves.items()):
            new_board = apply_move(board,move,BLACK,flips)
            value, _ = minmax(new_board,depth - 1, True)
            if value < best_value:
                best_value = value
                best_move = move

        return best_value,best_move

selected_cell = None 
def draw_board():

    screen.fill(WHITE)
    
    # Draw green board in the center
    board_rect = pygame.Rect(MARGIN, MARGIN, BOARD_SIZE, BOARD_SIZE)
    pygame.draw.rect(screen, GREEN, board_rect)

    # Draw grid lines
    for i in range(ROWS + 1):
        # Horizontal lines
        pygame.draw.line(screen, BLACK, 
                         (MARGIN, MARGIN + i * CELL_SIZE), 
                         (MARGIN + BOARD_SIZE, MARGIN + i * CELL_SIZE), 2)
        # Vertical lines
        pygame.draw.line(screen, BLACK, 
                         (MARGIN + i * CELL_SIZE, MARGIN), 
                         (MARGIN + i * CELL_SIZE, MARGIN + BOARD_SIZE), 2)

    # Draw labels (A–H for columns, 1–8 for rows)
    for i in range(COLS):
        # Column labels (top)
        letter = chr(65 + i)  
        text = font.render(letter, True, BLACK)
        text_rect = text.get_rect(center=(MARGIN + i * CELL_SIZE + CELL_SIZE / 2, MARGIN - 15))
        screen.blit(text, text_rect)

        # Column labels (bottom)
        text_rect = text.get_rect(center=(MARGIN + i * CELL_SIZE + CELL_SIZE / 2, MARGIN + BOARD_SIZE + 15))
        screen.blit(text, text_rect)

    for i in range(ROWS):
        # Row labels (left)
        number = str(i + 1)
        text = font.render(number, True, BLACK)
        text_rect = text.get_rect(center=(MARGIN - 15, MARGIN + i * CELL_SIZE + CELL_SIZE / 2))
        screen.blit(text, text_rect)

        # Row labels (right)
        text_rect = text.get_rect(center=(MARGIN + BOARD_SIZE + 15, MARGIN + i * CELL_SIZE + CELL_SIZE / 2))
        screen.blit(text, text_rect)
clicked_cells = [(3,3,WHITE),(4,4,WHITE),(4,3,BLACK),(3,4,BLACK)]


def highlight_cell(row,col,color):
     x = MARGIN + col * CELL_SIZE + CELL_SIZE // 2
     y = MARGIN + row * CELL_SIZE + CELL_SIZE // 2
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


def draw_center_text(text, color, font_size, y_offset=0, shadow=True):
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y_offset))

    if shadow:
        shadow_surface = font.render(text, True, (0, 0, 0))  # black shadow
        shadow_rect = text_rect.copy()
        shadow_rect.x += 3
        shadow_rect.y += 3
        screen.blit(shadow_surface, shadow_rect)
    screen.blit(text_surface, text_rect)

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

def evaluate_board(board):
    white_count = sum(1 for (_, _, c) in board if c == WHITE)
    black_count = sum(1 for (_, _, c) in board if c == BLACK)
    return white_count - black_count  # positive if white leads

def player_vs_robot():
    global clicked_cells
    color = BLACK 
    possible_positions = get_valid_moves(color,clicked_cells)
    game_over = False
    draw_board()
    for (row, col,clr) in clicked_cells:
        highlight_cell(row, col,clr)
    pygame.display.update()
  
    running = True
    while running:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if not possible_positions:
                color = WHITE if color == BLACK else BLACK
                possible_positions = get_valid_moves(color,clicked_cells)
                if not possible_positions:
                    game_over = True
                    black_count = sum(1 for (_, _, c) in clicked_cells if c == BLACK)
                    white_count = sum(1 for (_, _, c) in clicked_cells if c == WHITE)
                    if white_count > black_count:
                        winner_text = f"White wins!  ({white_count} - {black_count})"
                    if black_count> white_count : 
                        winner_text = f"Black wins!  ({black_count} - {white_count})"
                    if black_count == white_count: 
                        winner_text = f"Draw! ({black_count} - {white_count})"   
            else:
                if color == BLACK:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mx, my = pygame.mouse.get_pos()

                        if (MARGIN <= mx <= MARGIN + BOARD_SIZE) and (MARGIN <= my <= MARGIN + BOARD_SIZE):
                            col = (mx - MARGIN) // CELL_SIZE
                            row = (my - MARGIN) // CELL_SIZE
                            selected_cell = (row, col)
                        
                            if not any(r == row and c == col for (r, c, _) in clicked_cells):
                                if (row, col) in possible_positions:
                                    clicked_cells.append((row, col,BLACK))
                                    for (r, c) in possible_positions[(row, col)]:
                                        for i, (rr, cc, cc_color) in enumerate(clicked_cells):
                                            if rr == r and cc == c:
                                                clicked_cells[i] = (rr, cc, color)
                                                break        
                                    draw_board()        
                                    for (row, col,clr) in clicked_cells:
                                        highlight_cell(row, col,clr)
                                    pygame.display.update() 
                                    pygame.time.wait(500)   
                                    color = WHITE 
                                    possible_positions = get_valid_moves(color,clicked_cells)
                else:                    
                            value, move = minmax(clicked_cells, 1, True)
                            row, col = move
                            clicked_cells.append((row,col,color))
                            for (r, c) in possible_positions[(row, col)]:
                                for i, (rr, cc, cc_color) in enumerate(clicked_cells):
                                    if rr == r and cc == c:
                                        clicked_cells[i] = (rr, cc, color)
                                        break
                            draw_board()        
                            for (row, col,clr) in clicked_cells:
                                        highlight_cell(row, col,clr) 
                            pygame.display.update()                   
                            color = BLACK    
                            possible_positions = get_valid_moves(color,clicked_cells)        

        if color == BLACK:    
            for (row, col),line_cell in possible_positions.items():
                c = GRAY_BLACK 
                highlight_cell(row, col,c)
                
        if game_over:
            draw_center_text("GAME OVER", BLUE, 80, y_offset=-40)
            draw_center_text(winner_text,BLUE, 50, y_offset=40) 
            # --- Draw Main Menu button ---
            button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 80, 200, 60)
            mx, my = pygame.mouse.get_pos()

            button_surface = pygame.Surface((200, 60), pygame.SRCALPHA)
            if button_rect.collidepoint((mx, my)):
                button_surface.fill((0, 200, 0, 180))  # brighter green, 70% opacity
            else:
                button_surface.fill((0, 150, 0, 120))  # darker green, more transparent

            # Draw button onto screen
            screen.blit(button_surface, (button_rect.x, button_rect.y))

            # Draw text centered on the button
            font = pygame.font.Font(None, 40)
            text = font.render("Main Menu", True, (255, 255, 255))
            text_rect = text.get_rect(center=button_rect.center)
            screen.blit(text, text_rect)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if button_rect.collidepoint((mx, my)):
                        main_menu()
                        return
        pygame.display.flip()
        

    pygame.quit()
    sys.exit()
    

def play_1v1():
    global clicked_cells
    color = BLACK 
    possible_positions = get_valid_moves(color,clicked_cells)
    draw_board()        
    for (row, col,clr) in clicked_cells:
        highlight_cell(row, col,clr) 
    pygame.display.update() 
    game_over = False
    # Main loop
    running = True
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
            if not possible_positions:
                color = WHITE if color == BLACK else BLACK
                possible_positions = get_valid_moves(color,clicked_cells)
                if not possible_positions:
                    game_over = True
                    black_count = sum(1 for (_, _, color) in clicked_cells if color == BLACK)
                    white_count = sum(1 for (_, _, color) in clicked_cells if color == WHITE)
                    if white_count > black_count:
                        winner_text = f"White wins!  ({white_count} - {black_count})"
                    if black_count> white_count : 
                        winner_text = f"Black wins!  ({black_count} - {white_count})"
                    if black_count == white_count: 
                        winner_text = f"Draw! ({black_count} - {white_count})"    
    # Mouse click event
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()

                # Check if click inside board
                if (MARGIN <= mx <= MARGIN + BOARD_SIZE) and (MARGIN <= my <= MARGIN + BOARD_SIZE):
                    col = (mx - MARGIN) // CELL_SIZE
                    row = (my - MARGIN) // CELL_SIZE
                    selected_cell = (row, col)
                    
                    if not any(r == row and c == col for (r, c, _) in clicked_cells):
                        if (row, col) in possible_positions:
                            clicked_cells.append((row, col,color))
                            for (r, c) in possible_positions[(row, col)]:
                            # find that cell in clicked_cells and flip its color
                                for i, (rr, cc, cc_color) in enumerate(clicked_cells):
                                    if rr == r and cc == c:
                                        clicked_cells[i] = (rr, cc, color)
                                        break
                            draw_board()        
                            for (row, col,clr) in clicked_cells:
                                        highlight_cell(row, col,clr) 
                            pygame.display.update()         
                            pygame.time.wait(500) 
                            color = WHITE if color == BLACK else BLACK
                            possible_positions = get_valid_moves(color,clicked_cells)
        draw_board()
        for (row, col,clr) in clicked_cells:
            highlight_cell(row, col,clr)
        
        for (row, col),line_cell in possible_positions.items():
            c = GRAY_BLACK if color == BLACK else LIGHT_GRAY
            highlight_cell(row, col,c)
        if game_over:
            draw_center_text("GAME OVER", BLUE, 80, y_offset=-40)
            draw_center_text(winner_text,BLUE, 50, y_offset=40) 
            # --- Draw Main Menu button ---
            button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 80, 200, 60)
            mx, my = pygame.mouse.get_pos()

            # Create a semi-transparent surface for the button
            button_surface = pygame.Surface((200, 60), pygame.SRCALPHA)

            # Check hover state
            if button_rect.collidepoint((mx, my)):
                button_surface.fill((0, 200, 0, 180))  # brighter green, 70% opacity
            else:
                button_surface.fill((0, 150, 0, 120))  # darker green, more transparent

            # Draw button onto screen
            screen.blit(button_surface, (button_rect.x, button_rect.y))

            # Draw text centered on the button
            font = pygame.font.Font(None, 40)
            text = font.render("Main Menu", True, (255, 255, 255))
            text_rect = text.get_rect(center=button_rect.center)
            screen.blit(text, text_rect)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if button_rect.collidepoint((mx, my)):
                        main_menu()
                        return

        pygame.display.flip()

    pygame.quit()
    sys.exit()
    

def main_menu():
    global clicked_cells
    clicked_cells = [(3,3,WHITE),(4,4,WHITE),(4,3,BLACK),(3,4,BLACK)]
    while True:
        screen.fill(GREEN)
        draw_text("OTHELLO", font1, BLACK, screen, WIDTH//2, 100)

        mx, my = pygame.mouse.get_pos()
        button_1v1 = pygame.Rect(200, 220, 200, 60)
        button_robot = pygame.Rect(200, 320, 200, 60)
        button_exit = pygame.Rect(200, 420, 200, 60)

        for button in [button_1v1, button_robot, button_exit]:
            color = (0, 180, 0) if button.collidepoint((mx, my)) else (0, 100, 0)
            pygame.draw.rect(screen, color, button)

        draw_text("1 vs 1", small_font, WHITE, screen, 300, 250)
        draw_text("1 vs Robot", small_font, WHITE, screen, 300, 350)
        draw_text("Exit", small_font, WHITE, screen, 300, 450)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_1v1.collidepoint((mx, my)):
                    play_1v1()
                if button_robot.collidepoint((mx, my)):
                    player_vs_robot()
                if button_exit.collidepoint((mx, my)):
                    pygame.quit(); sys.exit()

        pygame.display.flip()

main_menu()