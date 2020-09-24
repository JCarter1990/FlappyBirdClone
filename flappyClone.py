import pygame, sys, random, os

dir_path = os.path.dirname(os.path.realpath(__file__))

# Initialize pygame
pygame.mixer.pre_init(frequency = 44100, size = 16, channels = 1, buffer = 512)
pygame.init()
screen = pygame.display.set_mode((576, 1024))
clock = pygame.time.Clock()
game_font = pygame.font.Font(dir_path + '/04B_19.ttf', 40)

# Load images
bg_surface = pygame.transform.scale2x(pygame.image.load(dir_path + '/assets/background-day.png').convert())
floor_surface = pygame.transform.scale2x(pygame.image.load(dir_path + '/assets/base.png').convert())
game_over_surface = pygame.transform.scale2x(pygame.image.load(dir_path + '/assets/message.png').convert_alpha())

# Load sounds
flap_sound = pygame.mixer.Sound(dir_path + '/sound/wing.wav')
death_sound = pygame.mixer.Sound(dir_path + '/sound/hit.wav')
score_sound = pygame.mixer.Sound(dir_path + '/sound/point.wav')

# Rect setup
game_over_rect = game_over_surface.get_rect(center = (288, 512))

# User events
BIRDFLAP = pygame.USEREVENT + 1
pygame.time.set_timer(BIRDFLAP, 200)
SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE, 1200)

# Game Variables
fall_speed = 0.25
game_active = False
score = 0
high_score = 0
floor_x_pos = 0


class Bird:
    img_upflap = pygame.transform.scale2x(pygame.image.load(dir_path + '/assets/bluebird-upflap.png').convert_alpha())
    img_midflap = pygame.transform.scale2x(pygame.image.load(dir_path + '/assets/bluebird-midflap.png').convert_alpha())
    img_downflap = pygame.transform.scale2x(pygame.image.load(dir_path + '/assets/bluebird-downflap.png').convert_alpha())

    def __init__(self):
        self.frames = [Bird.img_downflap, Bird.img_midflap, Bird.img_upflap]
        self.index = 0
        self.surface = self.frames[self.index]
        self.rect = self.surface.get_rect(center = (100, 512))
        self.movement = 0

    def animation(self):
        self.surface = self.frames[self.index]
        self.rect = self.surface.get_rect(center = (100, self.rect.centery))

    def rotate(self):
        return pygame.transform.rotozoom(self.surface, -self.movement * 3, 1)

    def check_collision(self, pipes):
        for pipe in pipes:
            if self.rect.colliderect(pipe.pipe_top) or self.rect.colliderect(pipe.pipe_bottom):
                death_sound.play()
                return False

        if self.rect.top <= -100 or self.rect.bottom >= 900:
            return False

        return True


class Pipe:
    pipe_surface = pygame.transform.scale2x(pygame.image.load(dir_path + '/assets/pipe-green.png').convert())
    score_surface = pygame.transform.scale2x(pygame.image.load(dir_path + '/assets/score_line.png').convert_alpha())
    pipe_list = []
    pipe_height = [400, 600, 800]

    def __init__(self):
        self.pipe_pos = random.choice(Pipe.pipe_height)
        self.pipe_top = Pipe.pipe_surface.get_rect(midbottom = (700, self.pipe_pos - 300))
        self.pipe_bottom = Pipe.pipe_surface.get_rect(midtop = (700, self.pipe_pos))
        self.score_rect = pygame.Rect(700, self.pipe_pos - 300, 1, 150)
        self.collect_score = False

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

def draw_floor():
    screen.blit(floor_surface, (floor_x_pos, 900))
    screen.blit(floor_surface, (floor_x_pos + 576, 900))

def score_display(game_state):
    if game_state == 'main_game':
        score_surface = game_font.render(str(int(score)), True, (255, 255, 255))
        score_rect = score_surface.get_rect(center = (288, 100))
        screen.blit(score_surface, score_rect)

    if game_state == 'game_over':
        score_surface = game_font.render(f'Score: {int(score)}', True, (255, 255, 255))
        score_rect = score_surface.get_rect(center = (288, 100))
        screen.blit(score_surface, score_rect)

        high_score_surface = game_font.render(f'High Score: {int(high_score)}', True, (255, 255, 255))
        high_score_rect = high_score_surface.get_rect(center = (288, 850))
        screen.blit(high_score_surface, high_score_rect)

def update_score(score, high_score):
    if score > high_score:
        high_score = score

    return high_score

bird1 = Bird()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_active:
                flap_sound.play()
                bird1.movement = 0
                bird1.movement -= 8

            elif event.key == pygame.K_SPACE and game_active == False:
                game_active = True
                Pipe.pipe_list.clear()
                bird1.rect.center = (100, 512)
                bird1.movement = 0
                score = 0

        if event.type == SPAWNPIPE:
            Pipe.create_pipe()

        if event.type == BIRDFLAP:
            if bird1.index < 2:
                bird1.index += 1

            else:
                bird1.index = 0

            bird1.animation()

    screen.blit(bg_surface, (0, 0))

    if game_active:
        bird1.movement += fall_speed
        bird1.rect.centery += int(bird1.movement)
        screen.blit(bird1.rotate(), bird1.rect)
        game_active = bird1.check_collision(Pipe.pipe_list)
        Pipe.move_pipes()

        for pipe in Pipe.pipe_list:
            if bird1.rect.colliderect(pipe.score_rect) and pipe.collect_score == False:
                pipe.collect_score = True
                score += 1
                score_sound.play()
            else:
                pass

        score_display('main_game')

    else:
        screen.blit(game_over_surface, game_over_rect)
        high_score = update_score(score, high_score)
        score_display('game_over')

    floor_x_pos -= 1
    draw_floor()

    if floor_x_pos <= -576:
        floor_x_pos = 0

    pygame.display.update()
    clock.tick(120)