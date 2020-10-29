import pygame, sys, random, os

dir_path = os.path.dirname(os.path.realpath(__file__))

# Initialize pygame
pygame.mixer.pre_init(frequency = 44100, size = 16, channels = 1, buffer = 512)
pygame.init()
screen = pygame.display.set_mode((576, 1024))
pygame.display.set_caption('Flocky Bird')
pygame.display.set_icon(pygame.image.load(dir_path + '/flappy_icon.ico').convert_alpha())
clock = pygame.time.Clock()


class Bird:
    img_upflap = pygame.transform.scale2x(pygame.image.load(dir_path + '/assets/bluebird-upflap.png').convert_alpha())
    img_midflap = pygame.transform.scale2x(pygame.image.load(dir_path + '/assets/bluebird-midflap.png').convert_alpha())
    img_downflap = pygame.transform.scale2x(pygame.image.load(dir_path + '/assets/bluebird-downflap.png').convert_alpha())

    flap_sound = pygame.mixer.Sound(dir_path + '/sound/wing.wav')
    death_sound = pygame.mixer.Sound(dir_path + '/sound/hit.wav')

    def __init__(self):
        self.frames = [Bird.img_downflap, Bird.img_midflap, Bird.img_upflap]
        self.index = 0
        self.surface = self.frames[self.index]
        self.rect = self.surface.get_rect(center = (100, 512))
        self.movement = 0
        self.active = False
        self.score = 0
        self.high_score = 0

    def animation(self):
        self.surface = self.frames[self.index]
        self.rect = self.surface.get_rect(center = (100, self.rect.centery))
        if self.index < 2:
            self.index += 1

        else:
            self.index = 0


    def rotate(self):
        return pygame.transform.rotozoom(self.surface, -self.movement * 3, 1)

    def check_collision(self, pipes):
        for pipe in pipes:
            if self.rect.colliderect(pipe.pipe_top) or self.rect.colliderect(pipe.pipe_bottom):
                self.death_sound.play()
                return True

        if self.rect.top <= -100 or self.rect.bottom >= 900:
            return True

        return False

    def flap(self):
        self.flap_sound.play()
        self.movement = 0
        self.movement -= 8

    def reset(self):
        self.active = True
        self.rect.center = (100, 512)
        self.movement = 0
        self.score = 0


class Pipe:
    pipe_surface = pygame.transform.scale2x(pygame.image.load(dir_path + '/assets/pipe-green.png').convert())
    score_surface = pygame.transform.scale2x(pygame.image.load(dir_path + '/assets/score_line.png').convert_alpha())
    pipe_list = []

    def __init__(self):
        self.pipe_pos = random.randint(400, 800)
        self.pipe_top = Pipe.pipe_surface.get_rect(midbottom = (700, self.pipe_pos - 250))
        self.pipe_bottom = Pipe.pipe_surface.get_rect(midtop = (700, self.pipe_pos))
        self.score_rect = pygame.Rect(700, self.pipe_pos - 300, 1, 200)
        self.collected_score = []

    @classmethod
    def create_pipe(cls): 
        Pipe.pipe_list.append(Pipe())

    @classmethod
    def move_pipes(cls):
        for pipe in Pipe.pipe_list:
            pipe.pipe_top.centerx -= 5
            pipe.pipe_bottom.centerx -= 5
            pipe.score_rect.centerx -= 5

        Pipe.draw_pipes()

    @classmethod
    def draw_pipes(cls):
        for pipe in Pipe.pipe_list:
            screen.blit(Pipe.pipe_surface, pipe.pipe_bottom)
            screen.blit(pygame.transform.flip(Pipe.pipe_surface, False, True), pipe.pipe_top)
            screen.blit(Pipe.score_surface, pipe.score_rect)
        
        if len(cls.pipe_list) > 3:
            del cls.pipe_list[0]
            

class Game:
    game_font = pygame.font.Font(dir_path + '/04B_19.ttf', 40)

    bg_surface = pygame.transform.scale2x(pygame.image.load(dir_path + '/assets/background-day.png').convert())
    floor_surface = pygame.transform.scale2x(pygame.image.load(dir_path + '/assets/base.png').convert())
    game_over_surface = pygame.transform.scale2x(pygame.image.load(dir_path + '/assets/message.png').convert_alpha())
    score_sound = pygame.mixer.Sound(dir_path + '/sound/point.wav')

    game_over_rect = game_over_surface.get_rect(center = (288, 512))

    BIRDFLAP = pygame.USEREVENT + 1
    pygame.time.set_timer(BIRDFLAP, 200)
    SPAWNPIPE = pygame.USEREVENT
    pygame.time.set_timer(SPAWNPIPE, 900)

    fall_speed = 0.20
    floor_x_pos = 0

    flock = [Bird(), Bird()]

    @classmethod
    def draw_floor(cls):
        screen.blit(cls.floor_surface, (cls.floor_x_pos, 900))
        screen.blit(cls.floor_surface, (cls.floor_x_pos + 576, 900))
        cls.floor_x_pos -= 1

        if cls.floor_x_pos <= -576:
            cls.floor_x_pos = 0

    @classmethod
    def score_display(cls, game_state):
        if game_state == 'main_game':
            score_surface = cls.game_font.render(f'P1:{cls.flock[0].score}', True, (255, 255, 255))
            score_rect = score_surface.get_rect(center = (50, 50))
            screen.blit(score_surface, score_rect)

            score_surface2 = cls.game_font.render(f'P2:{cls.flock[1].score}', True, (255, 255, 255))
            score_rect2 = score_surface.get_rect(center = (50, 100))
            screen.blit(score_surface2, score_rect2)

        if game_state == 'game_over':
            score_surface = cls.game_font.render(f'Score - P1:{cls.flock[0].score} P2:{cls.flock[1].score}', True, (255, 255, 255))
            score_rect = score_surface.get_rect(center = (288, 100))
            screen.blit(score_surface, score_rect)

            high_score_surface = cls.game_font.render(f'High Score - P1:{cls.flock[0].high_score} P2:{cls.flock[1].high_score}', True, (255, 255, 255))
            high_score_rect = high_score_surface.get_rect(center = (288, 850))
            screen.blit(high_score_surface, high_score_rect)

    @classmethod
    def update_score(cls):
        for bird in cls.flock:
            if bird.score > bird.high_score:
                bird.high_score = bird.score


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w and Game.flock[0].active:
                Game.flock[0].flap()

            if event.key == pygame.K_UP and Game.flock[1].active:
                Game.flock[1].flap()

            elif event.key == pygame.K_RETURN:
                if Game.flock[0].active == False and Game.flock[1].active == False:
                    Pipe.pipe_list.clear()
                    for bird in Game.flock:
                        bird.reset()

        if event.type == Game.SPAWNPIPE:
            Pipe.create_pipe()

        if event.type == Game.BIRDFLAP:
            for bird in Game.flock:
                bird.animation()

    screen.blit(Game.bg_surface, (0, 0))

    if not Game.flock[0].active and not Game.flock[1].active:
        screen.blit(Game.game_over_surface, Game.game_over_rect)
        Game.update_score()
        Game.score_display('game_over')

    else:
        for bird in Game.flock:
            if bird.active:
                bird.movement += Game.fall_speed
                bird.rect.centery += int(bird.movement)
                screen.blit(bird.rotate(), bird.rect)
                bird.active = not bird.check_collision(Pipe.pipe_list)

        for pipe in Pipe.pipe_list:
            for bird in Game.flock:
                if bird.rect.colliderect(pipe.score_rect) and bird not in pipe.collected_score:
                    pipe.collected_score.append(bird)
                    bird.score += 1
                    Game.score_sound.play()

        Pipe.move_pipes()
        Game.score_display('main_game')

    Game.draw_floor()

    pygame.display.update()
    clock.tick(120)