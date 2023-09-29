import pygame
from pygame.locals import *
import random

pygame.init()

clock = pygame.time.Clock()
fps = 60

# constants
IMG_NUMBER = 3
FONT = pygame.font.SysFont("Bauhaus 93", 60)
WHITE = (255, 255, 255)


screen_width = 864
screen_height = 936

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Flappy Bird")

ground_scroll = 0
scroll_speed = 4
pipe_gap = 200
is_flying = False
game_over = False
pipe_frequency = 1500
last_pipe = pygame.time.get_ticks()
score = 0
pass_pipe = False

bg = pygame.image.load("img/bg.png")
ground_img = pygame.image.load("img/ground.png")
button_img = pygame.image.load("img/restart.png")


def draw_text(text, font, text_color, x, y):
    image = font.render(text, True, text_color)
    screen.blit(image, (x, y))


def reset_game():
    pipe_group.empty()
    flappy_bird.rect.x = 100
    flappy_bird.rect.y = int(screen_height / 2)
    score = 0
    flappy_bird.image = pygame.transform.rotate(
        flappy_bird.images[flappy_bird.index], 180
    )
    return score


class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y, img_number):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.img_number = img_number
        for i in range(1, self.img_number + 1):
            img = pygame.image.load(f"img/bird{i}.png")
            self.images.append(img)
        self.index = 0
        self.counter = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.velocity = 0
        self.clicked = False

    def update(self):
        if is_flying:
            if self.rect.bottom < 768:
                self.velocity += 0.5
                self.rect.y += int(self.velocity)
        if game_over is False:
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                self.velocity = -10
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False
            self.counter += 1
            flap_cooldown = 3
            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                self.index %= self.img_number
            self.image = self.images[self.index]
            self.image = pygame.transform.rotate(
                self.images[self.index], (-3) * self.velocity
            )
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)


class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position: bool):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/pipe.png")
        self.rect = self.image.get_rect()
        if position:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        elif not position:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()


class Button:
    def __init__(self, image, x, y):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        is_pressed = False
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed()[0] == 1:
                is_pressed = True
        screen.blit(self.image, (self.rect.x, self.rect.y))
        return is_pressed


bird_group = pygame.sprite.Group()
flappy_bird = Bird(100, int(screen_height / 2), IMG_NUMBER)
bird_group.add(flappy_bird)

pipe_group = pygame.sprite.Group()

restart_button = Button(button_img, screen_width // 2 - 50, screen_height // 2 - 100)

run = True
while run:
    clock.tick(fps)

    screen.blit(bg, (0, 0))

    bird_group.draw(screen)
    bird_group.update()

    pipe_group.draw(screen)

    screen.blit(ground_img, (ground_scroll, 768))

    if len(pipe_group) > 0:
        if (
            bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left
            and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right
            and pass_pipe is False
        ):
            pass_pipe = True
        if pass_pipe is True:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                pass_pipe = False

    draw_text(str(score), FONT, WHITE, int(screen_width / 2), 20)

    if (
        pygame.sprite.groupcollide(bird_group, pipe_group, False, False)
        or flappy_bird.rect.top < 0
    ):
        game_over = True

    if flappy_bird.rect.bottom >= 768:
        game_over = True
        is_flying = False

    if not game_over and is_flying:
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            pipe_height = random.randint(-200, 200)
            top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, True)
            bottom_pipe = Pipe(
                screen_width, int(screen_height / 2) + pipe_height, False
            )
            pipe_group.add(top_pipe, bottom_pipe)

            last_pipe = time_now

        ground_scroll -= scroll_speed
        if ground_scroll < -35:
            ground_scroll = 0
        pipe_group.update()

    if game_over:
        if restart_button.draw() is True:
            game_over = False
            score = reset_game()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and is_flying is False
            and game_over is False
        ):
            is_flying = True

    pygame.display.update()

pygame.quit()
