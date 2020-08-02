import pygame as pg
from enum import auto, Enum
from random import randint
import pickle


class States(Enum):
    MENU = auto()
    RUNNING = auto()
    ENDGAME = auto()
    PAUSE = auto()


class Game:
    def __init__(self):
        pg.init()
        SCREEN_WIDTH = 360*2
        SCREEN_HEIGHT = 780
        self._size = (SCREEN_WIDTH, SCREEN_HEIGHT)
        self._screen = pg.display.set_mode(self._size)
        self._clock = pg.time.Clock()
        pg.display.set_caption("Tetris")
        # GAME DATA
        self._running = False
        self._state = States.MENU
        #####
        self._kinds = [None for _ in range(7)]
        self._kinds[0] = ['.X..',
                          '.X..',
                          '.X..',
                          '.X..']
        self._kinds[1] = ['....',
                          '.XX.',
                          '.XX.',
                          '....']
        self._kinds[2] = ['.X..',
                          '.X..',
                          '.XX.',
                          '....']
        self._kinds[3] = ['..X.',
                          '..X.',
                          '.XX.',
                          '....']
        self._kinds[4] = ['....',
                          '..X.',
                          '.XX.',
                          '.X..']
        self._kinds[5] = ['....',
                          '.X..',
                          '.XX.',
                          '..X.']
        self._kinds[6] = ['.X..',
                          '.XX.',
                          '.X..',
                          '....']
        #####
        self._start_up()
        self._logo = pg.transform.scale(
            pg.image.load('./assets/logo.png'), (180, 120))

    def _start_up(self):
        self._board = [[0 for j in range(12)] for i in range(26)]
        for i in range(26):
            self._board[i][0] = 1  # SOLID BLOCK = 1
            self._board[i][11] = 1
        for i in range(12):
            self._board[25][i] = 1
        self._current_piece_color = (
            randint(50, 255), randint(50, 255), randint(50, 255))
        self._current_piece_type = 0  # 0-6
        self._current_piece_i = 0  # 0-24
        self._current_piece_j = 4  # 1-10
        self._current_piece_rotation = 0  # 0-3
        self._tick_count = 0
        self._points = 0
        self._next_pieces = [[randint(0, 6), (
            randint(50, 255), randint(50, 255), randint(50, 255))] for i in range(3)]

    def _main_loop(self):
        self._running = True
        while self._running:
            self._main_event_handler()
            self._main_logic_handler()
            self._main_draw()
            self._tick_count += 1
            self._clock.tick(120)
            pg.display.update()
        pg.quit()

    def _main_event_handler(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self._running = False
                return
            if self._state == States.MENU:
                if event.type == pg.KEYDOWN:
                    key_pressed = event.key
                    if key_pressed == pg.K_SPACE:
                        self._start_up()
                        self._save()
                        self._state = States.RUNNING
                    if key_pressed == pg.K_c:
                        self._start_up()
                        self._load_save()
                        self._state = States.RUNNING
                    if key_pressed == pg.K_ESCAPE:
                        self._running = False
                return
            elif self._state == States.RUNNING:
                if event.type == pg.KEYDOWN:
                    key_pressed = event.key
                    if key_pressed == pg.K_LEFT:
                        self._move_piece_left_right(-1)
                    if key_pressed == pg.K_RIGHT:
                        self._move_piece_left_right(+1)
                    if key_pressed == pg.K_DOWN:
                        self._move_piece_down()
                    if key_pressed == pg.K_SPACE:
                        self._quick_drop()
                    if key_pressed == pg.K_r:
                        self._rotate()
                    if key_pressed == pg.K_ESCAPE:
                        self._state = States.PAUSE
                return
            elif self._state == States.PAUSE:
                if event.type == pg.KEYDOWN:
                    key_pressed = event.key
                    if key_pressed == pg.K_m:
                        self._save()
                        self._state = States.MENU
                    if key_pressed == pg.K_ESCAPE:
                        self._state = States.RUNNING
                return
            elif self._state == States.ENDGAME:
                if event.type == pg.KEYDOWN:
                    key_pressed = event.key
                    if key_pressed == pg.K_SPACE:
                        self._start_up()
                        self._state = States.RUNNING
                    if key_pressed == pg.K_m:
                        self._state = States.MENU
                return

    def _quick_drop(self):
        while not self._collision_checker(self._current_piece_i, self._current_piece_j, self._current_piece_rotation):
            self._current_piece_i += 1
        self._current_piece_i -= 1
        self._touch_down()

    def _rotate(self):
        nextRot = (self._current_piece_rotation + 1) % 4
        if not self._collision_checker(self._current_piece_i, self._current_piece_j, nextRot):
            self._current_piece_rotation = (
                self._current_piece_rotation + 1) % 4

    def _move_piece_left_right(self, logic):
        self._current_piece_j += logic if not self._collision_checker(
            self._current_piece_i, self._current_piece_j+logic, self._current_piece_rotation) else 0

    def _move_piece_down(self):
        self._current_piece_i += 1 if not self._collision_checker(
            self._current_piece_i+1, self._current_piece_j, self._current_piece_rotation) else 0

    def _line_finished(self):
        # CHECK FOR FULL LINE
        i = 0
        while i < 25:
            empty = 0
            for j in range(1, 11):
                if self._board[24-i][j] == 0:
                    empty += 1
            if empty == 0:
                # COMPLETE LINE
                self._points += 100
                self._board.pop(24-i)
                a = [0 for _ in range(12)]
                a[0] = 1
                a[11] = 1
                self._board.insert(0, a)
                i -= 1
            if empty == 10:
                break
            i += 1

    def _touch_down(self):
        # CONVERT ALL PIECE TO SOLID
        for i in range(4):
            for j in range(4):
                cell = self.posAt(
                    i, j, self._current_piece_rotation, self._current_piece_type)
                if cell == 'X':
                    self._board[self._current_piece_i +
                                i][self._current_piece_j+j] = self._current_piece_color
        # RESET PIECE
        self._current_piece_color = self._next_pieces[0][1]
        self._current_piece_rotation = 0
        self._current_piece_type = self._next_pieces[0][0]
        self._current_piece_i = 0
        self._current_piece_j = 4
        self._next_pieces.pop(0)
        self._next_pieces.append(
            [randint(0, 6), (randint(50, 255), randint(50, 255), randint(50, 255))])
        # CHECK FOR LINE
        self._line_finished()
        # CHECK FOR GAME OVER
        if self._collision_checker(0, 4, 0):
            self._state = States.ENDGAME

    def _main_logic_handler(self):
        if self._state == States.RUNNING:
            if self._tick_count >= 40:
                self._tick_count = 0
                self._move_piece_down()
                if self._collision_checker(self._current_piece_i+1, self._current_piece_j, self._current_piece_rotation):
                    # PIECE TOUCH DOWN
                    self._touch_down()
        return

    def _main_draw(self):
        self._screen.fill((0, 0, 0))
        self._draw_board()
        self._draw_piece()
        self._draw_next_pieces()
        if self._state == States.MENU:
            overLay = pg.Surface(self._size, pg.SRCALPHA)
            overLay.fill((0, 0, 0, 200))
            self._screen.blit(overLay, (0, 0))
            font = pg.font.SysFont('Ariel', 100)
            text = font.render(
                'Menu', False, (255, 255, 255))
            self._screen.blit(text, (50, 300))
            font = pg.font.SysFont('Ariel', 50)
            text = font.render(
                'Press Space to Start New Game', False, (255, 255, 255))
            self._screen.blit(text, (50, 390))
            text = font.render(
                'Press C to Continue Last Game', False, (255, 255, 255))
            self._screen.blit(text, (50, 450))
            text = font.render(
                'Press Esc to Exit', False, (255, 255, 255))
            self._screen.blit(text, (50, 510))
            self._screen.blit(self._logo, (50, 150))
            return
        elif self._state == States.RUNNING:
            font = pg.font.SysFont('Ariel', 70)
            text = font.render(
                f'Score: {self._points}', False, (255, 255, 255))
            self._screen.blit(text, (400, 50))
            return
        elif self._state == States.PAUSE:
            overLay = pg.Surface(self._size, pg.SRCALPHA)
            overLay.fill((0, 0, 0, 200))
            self._screen.blit(overLay, (0, 0))
            font = pg.font.SysFont('Ariel', 100)
            text = font.render(
                'Paused', False, (255, 255, 255))
            self._screen.blit(text, (50, 300))
            font = pg.font.SysFont('Ariel', 50)
            text = font.render(
                'Press Esc to continue', False, (255, 255, 255))
            self._screen.blit(text, (50, 390))
            text = font.render(
                'Press M to Save and Return to Menu', False, (255, 255, 255))
            self._screen.blit(text, (50, 450))
            return
        elif self._state == States.ENDGAME:
            overLay = pg.Surface(self._size, pg.SRCALPHA)
            overLay.fill((0, 0, 0, 200))
            self._screen.blit(overLay, (0, 0))
            font = pg.font.SysFont('Ariel', 100)
            text = font.render(
                'Game Over', False, (255, 255, 255))
            self._screen.blit(text, (50, 300))
            font = pg.font.SysFont('Ariel', 50)
            text = font.render(
                f'Your Score: {self._points}', False, (255, 255, 255))
            self._screen.blit(text, (50, 390))
            text = font.render(
                'Press Space to restart', False, (255, 255, 255))
            self._screen.blit(text, (50, 450))
            text = font.render(
                'Press M to return to Menu', False, (255, 255, 255))
            self._screen.blit(text, (50, 510))
            return

    def _draw_piece(self):
        for i in range(4):
            for j in range(4):
                cell = self.posAt(
                    i, j, self._current_piece_rotation, self._current_piece_type)
                if cell == 'X':
                    rect_to_draw = pg.Rect(
                        30*(j+self._current_piece_j), 30*(i+self._current_piece_i), 30, 30)
                    pg.draw.rect(
                        self._screen, self._current_piece_color, rect_to_draw)

    def _draw_next_pieces(self):
        for _ in range(len(self._next_pieces)):
            for i in range(4):
                for j in range(4):
                    cell = self.posAt(
                        i, j, 0, self._next_pieces[_][0])
                    if cell == 'X':
                        rect_to_draw = pg.Rect(
                            400 + 30*j, 200 + 30*i + 150*_, 30, 30)
                        pg.draw.rect(
                            self._screen, self._next_pieces[_][1], rect_to_draw)

    def _draw_board(self):
        for i in range(26):
            for j in range(12):
                cell = self._board[i][j]
                rect_to_draw = pg.Rect(30*j, 30*i, 30, 30)
                if cell == 1:  # SOLID BLOCK
                    pg.draw.rect(self._screen, (255, 255, 255), rect_to_draw)
                elif cell != 0:
                    pg.draw.rect(self._screen, cell, rect_to_draw)
    # HELPER

    def posAt(self, pi, pj, rotation, kind):
        if rotation == 0:
            return self._kinds[kind][pi][pj]
        elif rotation == 1:
            return self._kinds[kind][pj][3-pi]
        elif rotation == 2:
            return self._kinds[kind][3-pi][3-pj]
        elif rotation == 3:
            return self._kinds[kind][3-pj][pi]

    def _collision_checker(self, pos_i, pos_j, rotation):
        for i in range(4):
            for j in range(4):
                cell = self.posAt(i, j, rotation,
                                  self._current_piece_type)
                if cell == 'X' and self._board[pos_i + i][pos_j + j] != 0:
                    return True  # COLLIDE
        return False  # NOT COLLIDE

    def _save(self):
        with open('saved_state.pkl', 'wb') as f:
            state = [self._board, self._current_piece_color,
                     self._current_piece_type, self._points, self._next_pieces]
            pickle.dump(state, f)

    def _load_save(self):
        with open('saved_state.pkl', 'rb') as f:
            state = pickle.load(f)
            self._board = state[0]
            self._current_piece_color = state[1]
            self._current_piece_type = state[2]
            self._points = state[3]
            self._next_pieces = state[4]


game = Game()
game._main_loop()
