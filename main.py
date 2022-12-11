import cv2
import numpy as np
import time
import pyautogui as ptg
import chess
import chess.engine
import asyncio
from mss import mss
from glob import glob

'''
Made by Ryan Lee In Zer

This script is specifically designed for https://lichess.org, on Windows 10

PLEASE DO NOT USE THIS SCRIPT FOR RATED GAMES

This script is made for the purpose purely for coding practice and learning image processing,
I do not condone using this script for malicious purposes such as cheating and/or gaining more rating.
I am not responsible for any consequences led by the usage of this script.
I encourage the usage of this bot to play against another bot.
'''

# bounding area of the chess board (top left x, top left y, bottom right x, bottom right y)
board_bbox = ()#BBOX GO HERE
length = int((board_bbox[2] - board_bbox[0])/8) 
sct = mss()

'''
black pieces = lowercase
white pieces = uppercase

(according to chess library)
'''

piece_map = {
    'black_bishop': 'b',
    'black_king': 'k',
    'black_knight': 'n',
    'black_pawn': 'p',
    'black_queen': 'q',
    'black_rook': 'r',
    'white_bishop': 'B',
    'white_king': 'K',
    'white_knight': 'N',
    'white_pawn': 'P',
    'white_queen': 'Q',
    'white_rook': 'R'
}

# append piece images along with piece name
chess_piece_templates = []
for filename in glob('piece_templates/*.png'):
    piece_name = filename[16:-6]
    chess_piece_templates.append(
        [piece_name, cv2.imread(filename, 0)])

# capture the part of the screen (predefined) where there is a chess
def capture_image():
    img = sct.grab(monitor=board_bbox)
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
    return img

# determine which colour you are playing as
def playing_color():
    # image -> turn gray -> set threshold for white color -> count how many white pixels
    image = sct.grab(monitor=(board_bbox[0], board_bbox[1] +
                           length*6, board_bbox[0]+length, board_bbox[1]+length*7))
    image = cv2.cvtColor(np.array(image),cv2.COLOR_BGR2GRAY)
    ret,thresh=cv2.threshold(image,235,255,cv2.THRESH_BINARY)
    white_pixels = np.count_nonzero(thresh)

    if white_pixels > 500:
        return 'white'
    else:
        return 'black'

# get the board position based on input image
def check_grid_cells(image):
    string = ''
    # check each individual box on 8 x 8 chess board
    for y in range(8):
        blank_count = 0
        for x in range(8):
            confirm_chess_piece = ''
            cropped = image[y*length:y*length+length, x*length:x*length+length]

            highest_confidence = 0

            for chess_piece, template in chess_piece_templates:
                res = cv2.matchTemplate(cropped, template, cv2.TM_CCOEFF_NORMED)

                confidence = cv2.minMaxLoc(res)[1] #finding the confidence

                # make most confident piece as the final confirmed piece
                if confidence > highest_confidence:
                    highest_confidence = confidence 
                    confirm_chess_piece = chess_piece
            
            if highest_confidence < 0.4:
                blank_count += 1
            else:
                if blank_count >= 1:
                    string += str(blank_count)
                    blank_count = 0
                string += piece_map[confirm_chess_piece]
        if blank_count >= 1:
            string += str(blank_count)
            blank_count = 0
        if y != 7:
            string += '/'
    return string

# move mouse to the left side of the screen to start (not top left or else it will trigger FAIL SAFE)
def waiting_to_start():
    while 1:
        if ptg.position()[0] <= 10:
            break
    print('alright let\'s go')

# controls mouse to make move on board (lichess)
def play_move(player_color, before, after, is_pawn):
    before_column = before[0]
    before_row = before[1]

    after_column = after[0]
    after_row = after[1]

    rows = ['8', '7', '6', '5', '4', '3', '2', '1']
    columns = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

    if player_color == "black":
        rows = rows[::-1]
        columns = columns[::-1]

    before_x_index = columns.index(before_column)
    before_y_index = rows.index(before_row)

    after_x_index = columns.index(after_column)
    after_y_index = rows.index(after_row)

    before_x = board_bbox[0] + length//2 + length * before_x_index
    before_y = board_bbox[1] + length//2 + length * before_y_index

    after_x = board_bbox[0] + length//2 + length * after_x_index
    after_y = board_bbox[1] + length//2 + length * after_y_index

    ptg.moveTo(before_x, before_y)
    time.sleep(0.2)
    ptg.dragTo(after_x, after_y, 0.1, button='left')
    if ((after_row == '8' and before_row == '7') or (after_row == '1' and before_row == '2')) and abs(before_x_index - after_x_index) <= 1:
        if is_pawn:
            ptg.click()

# main logic
width = int(board_bbox[2]-board_bbox[0]) #set width
height = int(board_bbox[3]-board_bbox[1]) #set height
# writer= cv2.VideoWriter('basicvideo.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 20, (785,785))

async def main():
    transport, engine = await chess.engine.popen_uci("stockfish_14_x64_avx2.exe")
    original_board = None

    waiting_to_start()

    play_as = playing_color()
    play_as = 'white'

    print(play_as)

    board_image = capture_image()

    # cv2.imwrite('board.png', board_image)

    # generate the board into chess library readable format
    ascii_board = check_grid_cells(board_image)

    while ascii_board == 'RNBKQBNR/PPPPPPPP/8/8/8/8/pppppppp/rnbkqbnr':  # waiting for white to make move first
        board_image = capture_image()
        ascii_board = check_grid_cells(board_image)

    # to make it readable for chess library
    ascii_board += f' {play_as[0]} KQkq'
    board = chess.Board(ascii_board)

    print(board)

    if play_as == 'black':  # flip perspective when playing as black
        board.apply_transform(chess.flip_vertical)
        board.apply_transform(chess.flip_horizontal)

    while not board.is_game_over():
        try:
            # result = await engine.play(board, chess.engine.Limit(depth=18))
            result = await engine.play(board, chess.engine.Limit(time=0.05))
            ai_move = str(result.move) # extract the move in string format

            before_pos = ai_move[:2]
            after_pos = ai_move[2:]

            # check if piece is pawn, for promotion
            # promoting pawns should be dragged and clicked to promote
            # normal pieces would only be dragged
            before_piece = board.piece_at(chess.parse_square(before_pos))
            is_pawn = str(before_piece).lower() == 'p'

            play_move(play_as, before_pos, after_pos, is_pawn)

            board.push(result.move)
            board_copy = board # create copy to identify if opponent made a move

            # if black, flip the board so coordinates line up correctly
            if play_as == 'black':
                board_copy.apply_transform(chess.flip_vertical)
                board_copy.apply_transform(chess.flip_horizontal)

            original_board = str(board_copy)
            # time.sleep(2)

            board_image = capture_image()

            ascii_board = check_grid_cells(board_image)
            ascii_board += f' {play_as[0]} KQkq'

            if board.is_game_over(): #if game is over, break
                break

            # waiting for opponent to make move
            while str(chess.Board(ascii_board)) == original_board:
                board_image = capture_image()
                
                ascii_board = check_grid_cells(board_image)
                ascii_board += f' {play_as[0]} KQkq'
            print(str(chess.Board(ascii_board)))
            print()
            print(original_board)
            print()

            board = chess.Board(ascii_board)
            if play_as == 'black':
                board.apply_transform(chess.flip_vertical)
                board.apply_transform(chess.flip_horizontal)
        except Exception as e:
            print(e)
            break
    await engine.quit()
    # writer.release()


if __name__ == '__main__':
    asyncio.set_event_loop_policy(chess.engine.EventLoopPolicy())
    asyncio.run(main())
