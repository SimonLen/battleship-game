from random import randint


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Выстрел за пределы игрового поля!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку!"


class BoardWrongShipException(BoardException):
    pass


class Dot:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot({self.x}, {self.y})"


class Ship:
    def __init__(self, lenght: int, bow, direction: int):
        self.lenght = lenght
        self.bow = bow
        self.direction = direction  # 0 - horizontal; 1 - vertical
        self.lives = lenght

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.lenght):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.direction == 1:
                cur_x += i
            elif self.direction == 0:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hid: bool = False, size: int = 6):
        self.hid = hid
        self.size = size
        self.count = 0
        self.field = [["O"] * size for _ in range(size)]
        self.busy = []
        self.ships = []

    def __str__(self):
        res = "   | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n {i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "O")

        return res

    def out(self, d):
        return not (0 <= d.x < self.size and 0 <= d.y < self.size)

    def contour(self, ship, verb: bool = False):
        near = [
            (-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)
        ]

        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d):
        if self.out(d):
            raise BoardOutException

        if d in self.busy:
            raise BoardUsedException

        self.busy.append(d)

        for ship in self.ships:
            if ship.shooten(d):
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def turn(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class User(Player):
    def ask(self):
        while True:
            turn = input("Введите координаты выстрела: ").split()

            if len(turn) != 2:
                print("Введите 2 координаты")
                continue

            x, y = turn

            if not (x.isdigit()) or not (y.isdigit()):
                print("Введите числа!")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size: int = 6):
        self.size = size
        self.lens = [3, 2, 2, 1, 1, 1, 1]
        player = self.random_board()
        computer = self.random_board()
        computer.hid = True

        self.ai = AI(computer, player)
        self.us = User(player, computer)

    @staticmethod
    def greet():
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def start(self):
        self.greet()
        self.loop()

    def fill_board(self):
        board = Board(size=self.size)
        attempts = 0
        for lenght in self.lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(lenght, Dot(randint(0, self.size), randint(0, self.size)), randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.fill_board()
        return board

    def show_boards(self):
        print("-" * 20)
        print("Поле игрока:")
        print(self.us.board)
        print("-" * 20)
        print("Поле компьютера:")
        print(self.ai.board)
        print("-" * 20)

    def loop(self):
        num = 0
        while True:
            self.show_boards()
            if num % 2 == 0:
                print("Ходит игрок!")
                repeat = self.us.turn()
            else:
                print("Ходит компьютер!")
                repeat = self.ai.turn()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                self.show_boards()
                print("-" * 20)
                print("Игрок выиграл!")
                break

            if self.us.board.count == 7:
                self.show_boards()
                print("-" * 20)
                print("Компьютер выиграл!")
                break

            num += 1


g = Game()
g.start()
