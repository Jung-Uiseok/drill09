import math

from pico2d import load_image, get_time
from sdl2 import SDL_KEYDOWN, SDLK_SPACE, SDLK_RIGHT, SDL_KEYUP, SDLK_LEFT, SDLK_a


def space_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE


def time_out(e):
    return e[0] == 'TIME_OUT'


def time_out_5(e):
    return e[0] == 'TIME_OUT' and e[1] == 5.0


def right_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT


def right_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT


def left_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT


def left_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT


def a_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a


def a_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_a


class Idle:
    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        if get_time() - boy.start_time > 4:
            boy.state_machine.handle_event(('TIME_OUT', 0))
        print('Idle Doing')

    @staticmethod
    def enter(boy, e):
        if boy.action == 0:
            boy.action = 2
        elif boy.action == 1:
            boy.action = 3
        boy.frame = 0
        boy.start_time = get_time()  # 경과시간
        print('Idle Entry Action')

    @staticmethod
    def exit(boy, e):
        print('Idle Exit Action')

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y)


class Sleep:
    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        print('드르렁')

    @staticmethod
    def enter(boy, e):
        boy.frame = 0
        print('눕다')

    @staticmethod
    def exit(boy, e):
        print('일어서기')

    @staticmethod
    def draw(boy):
        if boy.action == 2:
            boy.image.clip_composite_draw(boy.frame * 100, boy.action * 100, 100, 100, math.pi * 1.5, '', boy.x + 25,
                                          boy.y - 25, 100, 100)
        else:
            boy.image.clip_composite_draw(boy.frame * 100, boy.action * 100, 100, 100, math.pi / 2, '', boy.x - 25,
                                          boy.y - 25, 100, 100)


class Run:
    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        boy.x += boy.dir * 5
        pass

    @staticmethod
    def enter(boy, e):
        if right_down(e) or right_up(e):
            boy.dir, boy.action = 1, 1
        elif left_down(e) or left_up(e):
            boy.dir, boy.action = -1, 0

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y)


class AutoRun:
    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        boy.x += boy.dir * 20
        if get_time() - boy.start_time > 4:
            boy.state_machine.handle_event(('TIME_OUT', 0))
        pass

    @staticmethod
    def enter(boy, e):
        if boy.dir == 1:
            boy.action = 1
        elif boy.dir == -1:
            boy.action = 0
        boy.start_time = get_time()

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y + 35, 200, 200)
        if boy.x > 800:
            boy.dir = -1
            boy.action = 0
        elif boy.x < 0:
            boy.dir = 1
            boy.action = 1


class StateMachine:
    def __init__(self, boy):
        self.boy = boy
        self.cur_state = Idle
        self.table = {
            Sleep: {right_down: Idle, left_down: Idle, left_up: Idle, right_up: Idle, a_down: Idle, space_down: Idle},
            Idle: {right_down: Run, left_down: Run, left_up: Idle, right_up: Idle, a_down: AutoRun, a_up: AutoRun, time_out: Sleep},
            Run: {right_down: Run, left_down: Run, right_up: Idle, left_up: Idle, a_down: AutoRun, a_up: AutoRun, space_down: Idle},
            AutoRun: {left_down: Run, left_up: Idle, right_down: Run, right_up: Idle, time_out: Idle}
        }

    def handle_event(self, e):
        for check_event, next_state in self.table[self.cur_state].items():
            if check_event(e):
                self.cur_state.exit(self.boy, e)
                self.cur_state = next_state
                self.cur_state.enter(self.boy, e)
                return True
        return False

    def start(self):
        self.cur_state.enter(self.boy, ('START, 0'))

    def update(self):
        self.cur_state.do(self.boy)

    def draw(self):
        self.cur_state.draw(self.boy)


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.dir = 0
        self.action = 3
        self.image = load_image('animation_sheet.png')
        self.state_machine = StateMachine(self)
        self.state_machine.start()

    def update(self):
        # self.frame = (self.frame + 1) % 8
        self.state_machine.update()

    def handle_event(self, event):
        print(event)
        self.state_machine.handle_event(('INPUT', event))

    def draw(self):
        # self.image.clip_draw(self.frame * 100, self.action * 100, 100, 100, self.x, self.y)
        self.state_machine.draw()
