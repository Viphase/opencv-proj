import pygame


class PygameFacade:
    def __init__(self, screen_size: tuple[int, int], caption: str ='Noname'):
        #Pygame facade is a class that allows you 
        pygame.init()
        self.screen = pygame.display.set_mode(screen_size)
        pygame.display.set_caption(caption)
        self.clock = pygame.time.Clock()
        self.sprites = pygame.sprite.Group()
        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_clicked = False

    def create_rect(self, x: int, y: int, width: int, height: int) -> pygame.Rect:
        #This function creates a pygame rect
        return pygame.Rect(x, y, width, height)

    def load_image(self, path: str, width: int, height: int) -> pygame.Surface:
        #A function to load and scale an image
        image = pygame.image.load(path).convert_alpha()
        image = pygame.transform.smoothscale(image, (int(width), int(height)))
        return image

    def draw_image(self, image: pygame.Surface, x: int, y: int) -> None:
        #A function to draw an image on screen
        self.screen.blit(image, (x, y))

    def update_screen(self) -> None:
        #A function to update the screen
        pygame.display.flip()

    def clear_screen(self) -> None:
        #A function to clear the screen
        self.screen.fill((0, 0, 0))

    def draw_text(self, text: str, x: int, y: int, color: tuple[int, int, int] = (255, 255, 255), size=24) -> None:
        #A function to draw text on screen
        font = pygame.font.Font(None, size)
        text_surface = font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))

    def handle_events(self) -> None:
        #A function to handle events
        self.mouse_clicked = False
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_pos = pygame.mouse.get_pos()
                self.mouse_clicked = True
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        self.mouse_pos = pygame.mouse.get_pos()
