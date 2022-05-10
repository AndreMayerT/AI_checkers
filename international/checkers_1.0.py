import time

import pygame
import random
import sys
from itertools import combinations

WIDTH = 800
ROWS = 10

RED = pygame.image.load('red.png')
GREEN = pygame.image.load('green.png')

REDKING = pygame.image.load('redKing.png')
GREENKING = pygame.image.load('greenKing.png')

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (235, 168, 52)
BLUE = (76, 252, 241)

pygame.init()
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption('Checkers')

priorMoves = []
possible_jump = False

def get_actions_value(current_position, grid, type):
    positions = generatePotentialMovesAI(current_position, grid, type)
    actions = {}
    pieces = []
    for i in range(8):
        for j in range(8):
            if grid[i][j].piece:
                if grid[i][j].piece.team == 'G':
                    pieces.append((i, j))

    for position in positions:
        if not type:
            if abs(position[0] - current_position[0]) > 1 or abs(position[1] - current_position[1]) > 1:
                actions[position] = 1
            elif position[0] == 7:
                actions[position] = 1

            elif abs(position[0] - current_position[0]) > 1 or abs(position[1] - current_position[1]) > 1 and \
                    position[0] == 7:
                actions[position] = 2
            else:
                actions[position] = 0
            for piece in pieces:
                if abs(position[0] - piece[0]) == 1 and abs(position[1] - piece[1]) == 1:
                    actions[position] = -1
                    if abs(position[0] - current_position[0]) > 1 or abs(position[1] - current_position[1]) > 1:
                        actions[position] = 1
                    if position[0] == 7:
                        actions[position] = 1
        else:
            if abs(position[0] - current_position[0]) > 1 or abs(position[1] - current_position[1]) > 1:
                actions[position] = 1
            else:
                actions[position] = 0
            for piece in pieces:
                if abs(position[0] - piece[0]) == 1 and abs(position[1] - piece[1]) == 1:
                    actions[position] = -1
                    if abs(position[0] - current_position[0]) > 1 or abs(position[1] - current_position[1]) > 1:
                        actions[position] = 1
    return actions


def alpha_beta(piece_value, sequence, grid, type):
    new_actions = get_actions_value(sequence[-1], grid, type)

    positions = list(new_actions.keys())
    values = list(new_actions.values())
    if 1 not in values:
        return piece_value, sequence
    if len(positions) < 1:
        return piece_value, sequence
    if type == 'KING':
        print(positions)
    if type == 'KING' and len(positions) < 2:
        return piece_value, sequence

    for i in range(len(values)):
        if values[i] == 2:
            piece_value += 2
            sequence.append(positions[i])
            piece_value, sequence = alpha_beta(piece_value, sequence, grid, type)
        if values[i] == 1:
            piece_value += 1
            sequence.append(positions[i])
            piece_value, sequence = alpha_beta(piece_value, sequence, grid, type)
            return piece_value, sequence


def action_search(grid):
    pieces = []
    piece_value = 0
    max_value = 0
    best_sequence = []
    default_moves = []
    safe_moves = []
    for i in range(8):
        for j in range(8):
            if grid[i][j].piece:
                if grid[i][j].piece.team == 'R':
                    pieces.append((i, j))

    for piece in pieces:
        piece_type = grid[piece[0]][piece[1]].piece.type
        default_action = get_actions_value(piece, grid, piece_type)
        pos = list(default_action.keys())
        values = list(default_action.values())
        piece_value, sequence = alpha_beta(piece_value, [piece], grid, piece_type)
        if len(default_action) > 0:
            default_moves.append([piece, pos[0]])
            if values[0] > -1:
                safe_moves.append([piece, pos[0]])
        if piece_value > max_value:
            best_sequence = sequence
            max_value = piece_value
        piece_value = 0

    if len(default_moves) == 0:
        print("The AI lost!!")
        print("### CONGRATULATIONS ###")
        quit()

    random_choice_default = random.randint(0, len(default_moves) - 1)
    if best_sequence:
        return best_sequence
    elif len(safe_moves) > 0:
        random_choice_safe = random.randint(0, len(safe_moves) - 1)
        return safe_moves[random_choice_safe]
    else:
        return default_moves[random_choice_default]


class Node:
    def __init__(self, row, col, width):
        self.row = row
        self.col = col
        self.x = int(row * width)
        self.y = int(col * width)
        self.colour = BLACK
        self.piece = None

    def draw(self, WIN):
        pygame.draw.rect(WIN, self.colour, (self.x, self.y, WIDTH / ROWS, WIDTH / ROWS))
        if self.piece:
            WIN.blit(self.piece.image, (self.x, self.y))


def update_display(win, grid, rows, width):
    for row in grid:
        for spot in row:
            spot.draw(win)
    draw_grid(win, rows, width)
    pygame.display.update()


def make_grid(rows, width):
    grid = []
    gap = width // rows
    count = 0
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(j, i, gap)
            if abs(i - j) % 2 == 0:
                node.colour = WHITE
            if node.colour == BLACK and i < 4:
                node.piece = Piece('R')
            elif node.colour == BLACK and i > 5:
                node.piece = Piece('G')
            count += 1
            grid[i].append(node)
    return grid


def draw_grid(win, rows, width):
    gap = width // ROWS
    for i in range(rows):
        pygame.draw.line(win, BLACK, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, BLACK, (j * gap, 0), (j * gap, width))


class Piece:
    def __init__(self, team):
        self.team = team
        self.image = RED if self.team == 'R' else GREEN
        self.type = 'KING'

    def draw(self, x, y):
        WIN.blit(self.image, (x, y))


def getNode(grid, rows, width):
    gap = width // rows
    RowX, RowY = pygame.mouse.get_pos()
    Row = RowX // gap
    Col = RowY // gap
    return (Col, Row)


def resetColours(grid, node):
    positions = generatePotentialMoves(node, grid)
    positions.append(node)

    for colouredNodes in positions:
        nodeX, nodeY = colouredNodes
        grid[nodeX][nodeY].colour = WHITE if abs(nodeX - nodeY) % 2 == 0 else BLACK


def HighlightpotentialMoves(piecePosition, grid):
    positions = generatePotentialMoves(piecePosition, grid)
    for position in positions:
        Column, Row = position
        grid[Column][Row].colour = BLUE


def opposite(team):
    return "R" if team == "G" else "G"


def generatePotentialMoves(nodePosition, grid):
    positions = []
    column, row = nodePosition
    global possible_jump
    if grid[column][row].piece:
        if grid[column][row].piece.type == 'KING':
            vectors = [[1, -1], [1, 1], [-1, -1], [-1, 1]]
            for i in range(len(vectors)):
                count = 0
                diagonal = nodePosition
                column_direction, row_direction = vectors[i]
                for square in range(10):
                    diagonal = (diagonal[0] + column_direction, diagonal[1] + row_direction)
                    if diagonal[0] > 9 or diagonal[0] < 0 or diagonal[1] > 9 or diagonal[1] < 0:
                        break

                    if grid[diagonal[0]][diagonal[1]].piece:
                        if grid[diagonal[0]][diagonal[1]].piece.team == 'G':
                            break
                        if grid[diagonal[0]][diagonal[1]].piece.team == 'R':
                            if count == 1:
                                break
                            else:
                                count = 1
                    if not grid[diagonal[0]][diagonal[1]].piece:
                        positions.append(diagonal)
                        count = 0
        else:
            movement_vectors = [[-1, -1], [-1, 1]]
            jump_vectors = [[1, -1], [1, 1], [-1, -1], [-1, 1]]

            for vector in jump_vectors:
                diagonal = (nodePosition[0] + vector[0], nodePosition[1] + vector[1])
                if diagonal[0] > 9 or diagonal[0] < 0 or diagonal[1] > 9 or diagonal[1] < 0:
                    continue

                if grid[diagonal[0]][diagonal[1]].piece and grid[diagonal[0]][diagonal[1]].piece.team == 'R':
                    diagonal = (diagonal[0] + vector[0], diagonal[1] + vector[1])
                    if diagonal[0] > 9 or diagonal[0] < 0 or diagonal[1] > 9 or diagonal[1] < 0:
                        continue

                    if not grid[diagonal[0]][diagonal[1]].piece:
                        possible_jump = True
                        positions.append(diagonal)

            if not possible_jump:
                for vector in movement_vectors:
                    diagonal = (nodePosition[0] + vector[0], nodePosition[1] + vector[1])
                    if diagonal[0] > 9 or diagonal[0] < 0 or diagonal[1] > 9 or diagonal[1] < 0:
                        continue

                    if grid[diagonal[0]][diagonal[1]].piece:
                        continue
                    else:
                        positions.append(diagonal)

    return positions


def generatePotentialMovesAI(nodePosition, grid, type):
    checker = lambda x, y: x + y >= 0 and x + y < 10
    positions = []
    column, row = nodePosition

    vectors = [[1, -1], [1, 1]]

    if type == 'KING':
        vectors = [[1, -1], [1, 1], [-1, -1], [-1, 1]]
    for vector in vectors:
        columnVector, rowVector = vector
        if checker(columnVector, column) and checker(rowVector, row):
            # grid[(column+columnVector)][(row+rowVector)].colour=ORANGE
            if not grid[(column + columnVector)][(row + rowVector)].piece:
                print(column + columnVector, row + rowVector)
                positions.append((column + columnVector, row + rowVector))
            elif grid[column + columnVector][row + rowVector].piece and \
                    grid[column + columnVector][row + rowVector].piece.team == 'G':
                if checker((2 * columnVector), column) and checker((2 * rowVector), row) \
                        and not grid[(2 * columnVector) + column][(2 * rowVector) + row].piece:
                    print(2 * columnVector + column, 2 * rowVector + row)
                    positions.append((2 * columnVector + column, 2 * rowVector + row))
                    break
    # print(positions[0][0])
    return positions


def highlight(ClickedNode, Grid, OldHighlight):
    Column, Row = ClickedNode
    Grid[Column][Row].colour = ORANGE
    if OldHighlight:
        resetColours(Grid, OldHighlight)
    HighlightpotentialMoves(ClickedNode, Grid)
    return (Column, Row)


def move(grid, piecePosition, newPosition):
    resetColours(grid, piecePosition)
    newColumn, newRow = newPosition
    oldColumn, oldRow = piecePosition
    diagonal = piecePosition
    column_direction = 0
    row_direction = 0

    piece = grid[oldColumn][oldRow].piece
    grid[newColumn][newRow].piece = piece
    grid[oldColumn][oldRow].piece = None

    if grid[newColumn][newRow].piece.type == 'KING':
        if oldColumn - newColumn > 0:
            # pra cima e direita
            if oldRow - newRow < 0:
                column_direction = -1
                row_direction = 1
            # pra cima e esquerda
            if oldRow - newRow > 0:
                column_direction = -1
                row_direction = -1
        else:
            # pra baixo e direita
            if oldRow - newRow < 0:
                column_direction = 1
                row_direction = 1
            # pra baixo e esquerda
            if oldRow - newRow > 0:
                column_direction = 1
                row_direction = -1

        for i in range(0, abs(oldColumn - newColumn)):
            diagonal = (diagonal[0] + column_direction, diagonal[1] + row_direction)
            print(diagonal)
            if grid[diagonal[0]][diagonal[1]].piece and grid[diagonal[0]][diagonal[1]].piece.team == 'R':
                grid[diagonal[0]][diagonal[1]].piece = None
    print('end of move')
    if newColumn == 0:
        grid[newColumn][newRow].piece.type = 'KING'
        grid[newColumn][newRow].piece.image = GREENKING
    if abs(newColumn - oldColumn) == 2 or abs(newRow - oldRow) == 2:
        grid[int((newColumn + oldColumn) / 2)][int((newRow + oldRow) / 2)].piece = None
        return grid[newColumn][newRow].piece.team
    return opposite(grid[newColumn][newRow].piece.team)


def moveAI(grid, piecePosition, newPosition):
    resetColours(grid, piecePosition)
    newColumn, newRow = newPosition
    oldColumn, oldRow = piecePosition

    piece = grid[oldColumn][oldRow].piece
    grid[newColumn][newRow].piece = piece
    grid[oldColumn][oldRow].piece = None

    if newColumn == 9 and grid[newColumn][newRow].piece.team == 'R':
        grid[newColumn][newRow].piece.type = 'KING'
        grid[newColumn][newRow].piece.image = REDKING
    if newColumn == 0 and grid[newColumn][newRow].piece.team == 'G':
        grid[newColumn][newRow].piece.type = 'KING'
        grid[newColumn][newRow].piece.image = GREENKING
    if abs(newColumn - oldColumn) == 2 or abs(newRow - oldRow) == 2:
        grid[int((newColumn + oldColumn) / 2)][int((newRow + oldRow) / 2)].piece = None
        return 'R'
    return 'G'


def check_end_game(grid):
    red_pieces = 0
    green_pieces = 0
    for i in range(8):
        for j in range(8):
            if grid[i][j].piece:
                if grid[i][j].piece.team == 'R':
                    red_pieces += 1
                if grid[i][j].piece.team == 'G':
                    green_pieces += 1

    if red_pieces == 0:
        print("The AI lost!!")
        print("### CONGRATULATIONS ###")
        quit()
    if green_pieces == 0:
        print("The AI won!!")
        print("###  BETTER LUCK NEXT TIME ###")
        quit()


def main(WIDTH, ROWS):
    global possible_jump
    grid = make_grid(ROWS, WIDTH)
    highlightedPiece = None
    currMove = 'G'
    AI_actions = []
    last_move = ''
    while True:
        check_end_game(grid)
        if currMove == 'R':
            time.sleep(1)
            if last_move == 'G':
                AI_actions = action_search(grid)
                currMove = moveAI(grid, AI_actions[0], AI_actions[1])
                # AI_actions.pop(0)
                del AI_actions[0]
                last_move = 'R'
            else:
                if len(AI_actions) < 2:
                    AI_actions = action_search(grid)

                currMove = moveAI(grid, AI_actions[0], AI_actions[1])
                # AI_actions = AI_actions.pop(0)
                del AI_actions[0]

            update_display(WIN, grid, ROWS, WIDTH)
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print('EXIT SUCCESSFUL')
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    clickedNode = getNode(grid, ROWS, WIDTH)

                    ClickedPositionColumn, ClickedPositionRow = clickedNode
                    # print(grid[ClickedPositionColumn][ClickedPositionRow].piece)
                    # print(grid[ClickedPositionColumn][ClickedPositionRow].piece.type)
                    if grid[ClickedPositionColumn][ClickedPositionRow].colour == BLUE:
                        if highlightedPiece:
                            pieceColumn, pieceRow = highlightedPiece
                        if currMove == grid[pieceColumn][pieceRow].piece.team:
                            resetColours(grid, highlightedPiece)
                            currMove = move(grid, highlightedPiece, clickedNode)
                            last_move = 'G'
                    elif highlightedPiece == clickedNode:
                        pass
                    else:
                        if grid[ClickedPositionColumn][ClickedPositionRow].piece:
                            if currMove == grid[ClickedPositionColumn][ClickedPositionRow].piece.team:
                                highlightedPiece = highlight(clickedNode, grid, highlightedPiece)
                                last_move = 'G'

            update_display(WIN, grid, ROWS, WIDTH)

        if last_move != currMove:
            possible_jump = False


main(WIDTH, ROWS)
