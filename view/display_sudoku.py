import pygame

class DisplaySudoku:
    def __init__(self):
        self.setup_game()
        self.start_game()
        pass
    
    def events_hendler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        pass
    
    def setup_game(self):
        pygame.init()
        self.screen = pygame.display.set_mode((600, 600))
        pygame.display.set_caption("Sudoku Solver")
    
    def display_board(board, screen):
        pass
    
    def start_game(self):
        self.events_hendler()        
        clock = pygame.time.Clock()
        running = True
        while running:
            print("1 frame")
            self.events_hendler()
            self.screen.fill("white")
            pygame.display.flip()
            clock.tick(60)
        
    