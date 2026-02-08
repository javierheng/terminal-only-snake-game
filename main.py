import curses
import random
import time


SNAKE_CHAR = "O"
HEAD_CHAR = "@"
FOOD_CHAR = "*"
WALL_CHAR = "#"

INITIAL_SPEED = 0.12
SPEEDUP_PER_FOOD = 0.003
MIN_SPEED = 0.05
MIN_HEIGHT = 15
MIN_WIDTH = 30


def clamp(n, low, high):
    return max(low, min(high, n))


def place_food(rng, height, width, snake_set):
    while True:
        y = rng.randint(1, height - 2)
        x = rng.randint(1, width - 2)
        if (y, x) not in snake_set:
            return (y, x)


def draw_border(stdscr, height, width):
    for x in range(width):
        try:
            stdscr.addch(0, x, WALL_CHAR)
            stdscr.addch(height - 1, x, WALL_CHAR)
        except curses.error:
            return
    for y in range(height):
        try:
            stdscr.addch(y, 0, WALL_CHAR)
            stdscr.addch(y, width - 1, WALL_CHAR)
        except curses.error:
            return


def run_game(stdscr):
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    stdscr.nodelay(True)
    stdscr.timeout(0)
    stdscr.keypad(True)

    rng = random.Random()
    while True:
        height, width = stdscr.getmaxyx()
        if height >= MIN_HEIGHT and width >= MIN_WIDTH:
            break
        stdscr.erase()
        msg = f" Window too small: need at least {MIN_WIDTH}x{MIN_HEIGHT} "
        stdscr.addstr(height // 2, clamp((width - len(msg)) // 2, 0, max(0, width - 1)), msg)
        stdscr.refresh()
        time.sleep(0.1)

    start_y = height // 2
    start_x = width // 2
    snake = [(start_y, start_x), (start_y, start_x - 1), (start_y, start_x - 2)]
    snake_set = set(snake)
    direction = (0, 1)
    pending_direction = direction
    food = place_food(rng, height, width, snake_set)

    score = 0
    speed = INITIAL_SPEED
    last_tick = time.time()
    game_over = False

    last_height = height
    last_width = width
    while True:
        height, width = stdscr.getmaxyx()
        if height < MIN_HEIGHT or width < MIN_WIDTH:
            stdscr.erase()
            msg = f" Window too small: need at least {MIN_WIDTH}x{MIN_HEIGHT} "
            stdscr.addstr(height // 2, clamp((width - len(msg)) // 2, 0, max(0, width - 1)), msg)
            stdscr.refresh()
            time.sleep(0.1)
            continue
        if height != last_height or width != last_width:
            start_y = height // 2
            start_x = width // 2
            snake = [(start_y, start_x), (start_y, start_x - 1), (start_y, start_x - 2)]
            snake_set = set(snake)
            direction = (0, 1)
            pending_direction = direction
            food = place_food(rng, height, width, snake_set)
            score = 0
            speed = INITIAL_SPEED
            game_over = False
            last_height = height
            last_width = width

        stdscr.erase()
        draw_border(stdscr, height, width)

        stdscr.addch(food[0], food[1], FOOD_CHAR)
        for i, (y, x) in enumerate(snake):
            stdscr.addch(y, x, HEAD_CHAR if i == 0 else SNAKE_CHAR)

        status = f" Score: {score}  Speed: {speed:.2f}  (Q to quit) "
        stdscr.addstr(0, clamp((width - len(status)) // 2, 1, width - len(status) - 2), status)

        if game_over:
            msg = " GAME OVER - Press R to restart or Q to quit "
            stdscr.addstr(height // 2, clamp((width - len(msg)) // 2, 1, width - len(msg) - 2), msg)

        stdscr.refresh()

        key = stdscr.getch()
        if key in (ord("q"), ord("Q")):
            return
        if game_over:
            if key in (ord("r"), ord("R")):
                return "restart"
            time.sleep(0.05)
            continue

        if key in (curses.KEY_UP, ord("w"), ord("W")):
            pending_direction = (-1, 0)
        elif key in (curses.KEY_DOWN, ord("s"), ord("S")):
            pending_direction = (1, 0)
        elif key in (curses.KEY_LEFT, ord("a"), ord("A")):
            pending_direction = (0, -1)
        elif key in (curses.KEY_RIGHT, ord("d"), ord("D")):
            pending_direction = (0, 1)

        # Prevent reversing into itself
        if (pending_direction[0] != -direction[0]) or (pending_direction[1] != -direction[1]):
            direction = pending_direction

        now = time.time()
        if now - last_tick < speed:
            time.sleep(0.005)
            continue
        last_tick = now

        head_y, head_x = snake[0]
        new_head = (head_y + direction[0], head_x + direction[1])

        # Wall collision
        if new_head[0] <= 0 or new_head[0] >= height - 1 or new_head[1] <= 0 or new_head[1] >= width - 1:
            game_over = True
            continue

        will_grow = new_head == food

        # Self collision (allow moving into tail if it will move away)
        tail = snake[-1]
        if new_head in snake_set and (will_grow or new_head != tail):
            game_over = True
            continue

        snake.insert(0, new_head)
        snake_set.add(new_head)

        if will_grow:
            score += 1
            speed = max(MIN_SPEED, speed - SPEEDUP_PER_FOOD)
            food = place_food(rng, height, width, snake_set)
        else:
            tail = snake.pop()
            snake_set.remove(tail)


def main():
    while True:
        result = curses.wrapper(run_game)
        if result != "restart":
            break


if __name__ == "__main__":
    main()
