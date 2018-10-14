import pygame, sys, math
from pygame.locals import *

# Global Variables;
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
PIXEL_PER_METTER = 10



class RigidBody:
    def __init__(self, size, coords, mass=1):
        self.rect = pygame.Rect(coords[0], coords[1], size[0], size[1])
        self.color_rect = (200,0,50)
        self.mass = mass
        self.speed = [0,0]
        self.gravity = 0
        self.label = "Nothing"

    def separate_from_other(self, other):
        if self.rect.colliderect(other.rect):
            width = other.rect.width+self.rect.width
            height = other.rect.height+self.rect.height
            delta = float(height)/float(width)
            distance_h = other.rect.centerx-self.rect.centerx
            distance_v = other.rect.centery-self.rect.centery
            if abs(distance_v) > (abs(distance_h)*delta-2):
                if distance_v > 0: self.rect.bottom = other.rect.top
                else: self.rect.top = other.rect.bottom
            else:
                if distance_h > 0: self.rect.right = other.rect.left
                else: self.rect.left = other.rect.right
            return True
        return False

    def get_elasticity(self, other):
        elasticity = other.mass/(self.mass+other.mass)
        return elasticity

    def set_gravity(self, speed):
        self.gravity = speed

    def add_speed(self, speed):
        self.rect.centerx += int(speed[0])
        self.rect.centery += int(speed[1])

    def draw(self, surface):
        pygame.draw.rect(surface,self.color_rect,self.rect)

    def update(self, is_moving=True):
        self.speed[1]+=self.gravity/PIXEL_PER_METTER
        if is_moving: self.add_speed((self.speed[0], self.speed[1]))

class Block(RigidBody):
    def __init__(self, size, coords):
        RigidBody.__init__(self, size, coords)
        self.mass = 200
        self.color_rect = (20,20,20)
        self.label = "Block"
class Player(RigidBody):
    def __init__(self, coords):
        RigidBody.__init__(self, (16,32), coords, mass=12)
        self.keymap = {
            "Right" : pygame.K_RIGHT,
            "Left" : pygame.K_LEFT,
            "Down" : pygame.K_DOWN,
            "Up" : pygame.K_UP,
            "ButtonA" : pygame.K_z,
            "ButtonB" : pygame.K_x,
            "ButtonC" : pygame.K_c
        }
        self.set_gravity(9.8)
        self.label = "Player"
        self.walk_speed = 5

    def is_colliding(self, object_list, speed):
        for objectA in object_list:
            if objectA.label == "Block":
                if self.separate_from_other(objectA):
                    self.speed[1] = 0

    def move_and_collide(self, object_list, speed):
        self.add_speed((0,speed[1]))
        self.add_speed((speed[0],0))
        self.is_colliding(object_list,(speed[0],0))

    def update(self, object_list):
        keyboard = pygame.key.get_pressed()
        walk_direction = keyboard[self.keymap["Right"]]-keyboard[self.keymap["Left"]]

        # if walk_direction != 0:
        self.speed[0] = self.walk_speed*walk_direction

        RigidBody.update(self, False)
        self.move_and_collide(object_list,(self.speed[0], self.speed[1]))

class Room:
    def __init__(self):
        self.canvas = pygame.Surface((640,480))
        self.background_color = (150,150,150)
        self.object_list = []

    def add_object(self, objectA):
        self.object_list.append(objectA)

    def remove_object(self, objectA):
        self.object_list.append(objectA)

    def room_draw(self, surface):
        surface.fill(self.background_color)
        for objectA in self.object_list:
            objectA.draw(surface)

    def room_update(self):
        for objectA in self.object_list:
            if objectA.label != "Player": objectA.update()
            else: objectA.update(self.object_list)

# Main Process;
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.game_loop(self.screen)

    def game_draw(self, surface):
        room.room_draw(surface)

    def game_loop(self, surface):
        global room
        room = Room()
        room.add_object(Block((200,20),(10,150)))
        room.add_object(Block((20,20),(20,140)))

        room.add_object(Player((150,10)))

        while True:
            self.clock.tick(30)
            surface.fill((150,150,150))
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            room.room_update()
            self.game_draw(surface)

            pygame.display.flip()
if __name__ == "__main__": Game()
