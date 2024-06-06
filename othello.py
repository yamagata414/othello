import numpy as np
import matplotlib.pyplot as plt
import random

empty = 0         # 何もない状態
white = -1
black = 1         # 黒の面
wall = 2


# 2進数で考える
upper = 2 ** 0           # 1    上
upper_right = 2 ** 1     # 2    右上
right = 2 ** 2           # 4    右
lower_right = 2 ** 3     # 8    右下
lower = 2 ** 4           # 16   下
lower_left = 2 ** 5      # 32   左下
left = 2 ** 6            # 64   左
upper_left = 2 ** 7      # 128  左上

board_size = 8           # 盤面のサイズ

player_color = [black, white]


class Board:
    def __init__(self):    # 盤面の基盤をつくる

        self.RawBoard = np.zeros((board_size + 2, board_size + 2), dtype=int)

        self.RawBoard[0, :] = wall
        self.RawBoard[:, 0] = wall
        self.RawBoard[board_size + 1, :] = wall
        self.RawBoard[:, board_size + 1] = wall

        self.RawBoard[4, 4] = white
        self.RawBoard[5, 5] = white
        self.RawBoard[4, 5] = black
        self.RawBoard[5, 4] = black

        self.turns = 0

        self.CurrentColor = black

        # ひっくり返せる相手の石がある方向の情報が入っている配列
        self.board_direction = np.zeros(
            (board_size + 2, board_size + 2), dtype=int)
        # 石が置けるか置けないかの情報が入っている配列
        self.position = np.zeros((board_size + 2, board_size + 2), dtype=int)
        self.controller = np.zeros((board_size + 2, board_size + 2), dtype=int)

        self.ref_direction_position()

    def ref_flip_disc(self, x, y):                 # 石を置いたのを反映(相手の石をひっくり返す)
        self.RawBoard[x, y] = self.CurrentColor
        direction = self.board_direction[x, y]

        if direction & upper:  # ひっくり返す
            y_y = y - 1
            while self.RawBoard[x, y_y] == -self.CurrentColor:
                self.RawBoard[x, y_y] = self.CurrentColor
                y_y -= 1

        if direction & upper_right:  # 〇& ✕==
            x_x = x + 1
            y_y = y - 1
            while self.RawBoard[x_x, y_y] == -self.CurrentColor:
                self.RawBoard[x_x, y_y] = self.CurrentColor
                x_x += 1
                y_y -= 1

        if direction & right:
            x_x = x + 1
            while self.RawBoard[x_x, y] == -self.CurrentColor:
                self.RawBoard[x_x, y] = self.CurrentColor
                x_x += 1

        if direction & lower_right:
            x_x = x + 1
            y_y = y + 1
            while self.RawBoard[x_x, y_y] == -self.CurrentColor:
                self.RawBoard[x_x, y_y] = self.CurrentColor
                x_x += 1
                y_y += 1

        if direction & lower:
            y_y = y + 1
            while self.RawBoard[x, y_y] == -self.CurrentColor:
                self.RawBoard[x, y_y] = self.CurrentColor
                y_y += 1

        if direction & lower_left:
            x_x = x - 1
            y_y = y + 1
            while self.RawBoard[x_x, y_y] == -self.CurrentColor:
                self.RawBoard[x_x, y_y] = self.CurrentColor
                x_x -= 1
                y_y += 1

        if direction & left:
            x_x = x - 1
            while self.RawBoard[x_x, y] == -self.CurrentColor:
                self.RawBoard[x_x, y] = self.CurrentColor
                x_x -= 1

        if direction & upper_left:
            x_x = x - 1
            y_y = y - 1
            while self.RawBoard[x_x, y_y] == -self.CurrentColor:
                self.RawBoard[x_x, y_y] = self.CurrentColor
                x_x -= 1
                y_y -= 1

    def set_disc(self, x, y):  # 石を置く
        if x < 1 or board_size < x:
            return False
        if y < 1 or board_size < y:
            return False          # おけないところだと、falseを返す
        if self.position[x, y] == 0:
            return False

        self.ref_flip_disc(x, y)
        self.turns += 1
        self.CurrentColor = -self.CurrentColor
        self.ref_direction_position()

        return True  # おけるところならtrueを返す

    def set_disc_2(self, x, y):  # 石を置けるかどうかの判定（CPULv１用）
        if x < 1 or board_size < x:
            return False
        if y < 1 or board_size < y:
            return False  # おけないところだと、falseを返す
        if self.position[x, y] == 0:
            return False

        self.ref_direction_position()
        return True  # おけるところならtrueを返す

    def check(self, x, y, color):  # 相手の石のある方向をシラベル
        direction = 0
        if self.RawBoard[x, y] != empty:
            return direction

        if self.RawBoard[x, y - 1] == -color:   # 上に相手の石
            x_x = x
            y_y = y - 2  # 修正前 y_y=y-1
            while self.RawBoard[x_x, y_y] == -color:  # 自分の色ではないとさらに上に行く
                y_y -= 1
            if self.RawBoard[x_x, y_y] == color:       # 自分の色を見つけると、終わり
                # |:or        direction=upperだと、1つしか決められない |を使うと、すべての方向の情報が分かる（2進数の桁が違うから）
                direction = direction | upper

        if self.RawBoard[x + 1, y - 1] == -color:  # 右上に相手の石
            x_x = x + 2
            y_y = y - 2
            while self.RawBoard[x_x, y_y] == -color:
                x_x += 1
                y_y -= 1
            if self.RawBoard[x_x, y_y] == color:
                direction = direction | upper_right

        if self.RawBoard[x + 1, y] == -color:  # 右に相手の石
            x_x = x + 2
            y_y = y
            while self.RawBoard[x_x, y_y] == -color:
                x_x += 1
            if self.RawBoard[x_x, y_y] == color:
                direction = direction | right

        if self.RawBoard[x + 1, y + 1] == -color:       # 右下に相手の石
            x_x = x + 2
            y_y = y + 2
            while self.RawBoard[x_x, y_y] == -color:
                x_x += 1
                y_y += 1
            if self.RawBoard[x_x, y_y] == color:
                direction = direction | lower_right

        if self.RawBoard[x, y + 1] == -color:           # 下に相手の石
            x_x = x
            y_y = y + 2
            while self.RawBoard[x_x, y_y] == -color:
                y_y += 1
            if self.RawBoard[x, y_y] == color:
                direction = direction | lower

        if self.RawBoard[x - 1, y + 1] == -color:       # 左下に相手の石
            x_x = x - 2
            y_y = y + 2
            while self.RawBoard[x_x, y_y] == -color:
                x_x -= 1
                y_y += 1
            if self.RawBoard[x_x, y_y] == color:
                direction = direction | lower_left

        if self.RawBoard[x - 1, y] == -color:           # 左に相手の石
            x_x = x - 2
            y_y = y
            while self.RawBoard[x_x, y] == -color:
                x_x -= 1
            if self.RawBoard[x_x, y] == color:
                direction = direction | left

        if self.RawBoard[x - 1, y - 1] == -color:       # 左上に相手の石
            x_x = x - 2
            y_y = y - 2
            while self.RawBoard[x_x, y_y] == -color:
                x_x -= 1
                y_y -= 1
            if self.RawBoard[x_x, y_y] == color:
                direction = direction | upper_left

        return direction  # これが０だと置ける場所がない

    def ref_direction_position(self):  # 自分のおける場所かつ、相手の石のある方向を表示
        self.position[:, :] = False  # 最初はすべてのマスがfalseの状態
        for x in range(1, board_size+1):  # シラベル
            for y in range(1, board_size+1):
                direction = self.check(x, y, self.CurrentColor)
                self.board_direction[x, y] = direction

                if direction != 0:
                    # directionが0以外（相手の石がどこかの方向に隣接している）だと、trueへ変わる
                    self.position[x, y] = True

    def display(self):  # RawBoardを記号に変更
        for y in range(1, board_size + 1):
            for x in range(1, board_size + 1):
                shape = self.RawBoard[x, y]
                if shape == white:
                    print('○', end="")
                if shape == black:
                    print('●', end="")
                if shape == empty:
                    print('□', end="")
                if shape == wall:
                    print('', end="")
            print()

    def end_game(self):  # ゲームが終了する場面の場合、Trueを返す
        # any関数：positionに一つでもtrue（置ける場所）があれば、ゲームは終わらない
        if self.position[:, :].any() == True:
            return False

        for y in range(1, board_size + 1):
            for x in range(1, board_size + 1):
                if self.check(x, y, - self.CurrentColor) != 0:  # 一つでも置ける場所があればゲームは終わらない（相手）
                    return False

        return True  # 自分と相手が置けないのでゲーム終わり

    def skip(self):  # パスしなければならない場面なら、Trueを返す
        if self.position[:, :].any() == True:  # 自分が置ける場所があると、falseでパス不可能
            return False
        if self.end_game() == True:  # 自分も相手も置けないと、falseでパス不可能
            return False
# 自分が置けず、相手が置ける場合のみパスが発動
        self.CurrentColor = - self.CurrentColor
        self.ref_direction_position()
        return True

    def judge(self):  # ゲームの判定をする
        black_add = 0
        white_add = 0
        for y in range(1, board_size + 1):
            for x in range(1, board_size + 1):
                add = self.RawBoard[x, y]
                if add == black:
                    black_add += 1
                    continue
                elif add == white:
                    white_add += 1
                    continue
                else:
                    continue
        if black_add > white_add:
            print("Black:", black_add)
            print("White:", white_add)
            print("Black win!")
        elif black_add < white_add:
            print("White win!")
            print("Black:", black_add)
            print("White:", white_add)
        else:
            print("Draw")
            print("Black:", black_add)
            print("White:", white_add)

    def CPU(self):  # ランダム打ち
        coordinate = range(1, board_size + 1)
        while True:
            x = coordinate[random.randint(0, len(coordinate) - 1)]
            y = coordinate[random.randint(0, len(coordinate) - 1)]
            if self.set_disc(x, y) == True:
                break
            else:
                continue
        return 0

    def CPU_score(self):  # 盤面のスコアが高いところに置く
        # coordinate=range(1,board_size+1)
        x_stock = []
        y_stock = []
        count = 0
        for y in range(1, board_size + 1):
            for x in range(1, board_size + 1):
                if self.set_disc_2(x, y) == True:
                    x_stock += [x]
                    y_stock += [y]
                else:
                    continue
        for i in range(len(x_stock)):
            x_can = x_stock[i]
            y_can = y_stock[i]
            if i != 0:
                # スコアが高い場所に優先的に石をオク
                if self.controller[x_can, y_can] > self.controller[x_max, y_max]:
                    x_max = x_can
                    y_max = y_can
                    count += 1
                else:
                    continue
            else:
                x_max = x_can
                y_max = y_can
                continue
        if count == 0:
            i = random.randint(0, len(x_stock) - 1)
            x = x_stock[i]
            y = y_stock[i]
            self.set_disc(x, y)
            # print("HAPPYYYY")
            return 0  # x,y#,print(x_stock),print(y_stock)
        else:
            x = x_max
            y = y_max
            self.set_disc(x, y)
            return 0  # x,y

    def cpu_controller(self):  # CPULv1のスコアを作成（ここをいじれば、CPUをもっと強くできる(?)）
        self.controller[1, 1] = 5
        self.controller[1, board_size] = 5
        self.controller[board_size, 1] = 5
        self.controller[board_size, board_size] = 5
        if self.RawBoard[1, 1] == player_color[serect_color]:
            if self.RawBoard[1, 3] == player_color[serect_color]:
                self.controller[1, 2] = 4
                self.controller[1, 4] = -1
        if self.RawBoard[1, 1] == player_color[serect_color]:
            if self.RawBoard[3, 1] == player_color[serect_color]:
                self.controller[2, 1] = 4
                self.controller[4, 1] = -1

        if self.RawBoard[1, board_size] == player_color[serect_color]:
            if self.RawBoard[1, board_size - 2] == player_color[serect_color]:
                self.controller[1, board_size - 1] = 4
                self.controller[1, board_size - 3] = -1
        if self.RawBoard[1, board_size] == player_color[serect_color]:
            if self.RawBoard[3, board_size] == player_color[serect_color]:
                self.controller[2, board_size] = 4
                self.controller[4, board_size] = -1

        if self.RawBoard[board_size, 1] == player_color[serect_color]:
            if self.RawBoard[board_size - 2, 1] == player_color[serect_color]:
                self.controller[board_size - 1, 1] = 4
                self.controller[board_size - 3, 1] = -1
        if self.RawBoard[board_size, 1] == player_color[serect_color]:
            if self.RawBoard[board_size, 3] == player_color[serect_color]:
                self.controller[board_size, 2] = 4
                self.controller[board_size, 4] = -1

        if self.RawBoard[board_size, board_size] == player_color[serect_color]:
            if self.RawBoard[board_size, board_size - 2] == player_color[serect_color]:
                self.controller[board_size, board_size - 1] = 4
        if self.RawBoard[board_size, board_size] == player_color[serect_color]:
            if self.RawBoard[board_size - 2, board_size] == player_color[serect_color]:
                self.controller[board_size - 1, board_size] = 4


# ##メインコード###

board = Board()

print("Please choose CPU level. You can enter only integer value.")
print("Lv:0")
print("Lv:1")
CPU_Lv = int(input())

print("Please choose your color. You can enter only integer value.")
print("black:0")
print("white:1")
serect_color = int(input())
print()
while True:

    board.display()
    if board.end_game() == True:
        board.display()
        print("OVER!!")
        board.judge()
        break

    if board.CurrentColor == black:
        print()
        print("Black's turns.", end="")
    else:
        print()
        print("White's turns.", end="")

    if board.skip() == True:
        print()
        print("You're pass.")
        continue

    if board.CurrentColor == player_color[serect_color]:
        try:
            print()
            print("Enter the value of x. If you want to retired, you would enter 100.")
            x = int(input())
            if x == 100:
                print()
                print("You retired.")
                print("You lose.")
                break
            try:
                print("Enter the value of y.")
                y = int(input())
                if y == 100:
                    print()
                    print("You retired.")
                    print("You lose.")
                    break
            except:
                print("The value you entered might not be right.")
                continue
        except:
            print("The value you entered might not be right.")
            continue

        if board.set_disc(x, y) != True:
            print("You can't put disc here!")
            continue
    else:
        if CPU_Lv == 0:
            board.CPU()
            print()
        elif CPU_Lv == 1:
            board.cpu_controller()
            board.CPU_score()
            print()
