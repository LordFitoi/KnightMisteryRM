import pygame, sys, math, pytmx
from pytmx.util_pygame import load_pygame
from pygame.locals import *

# Global Variables;
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
PIXEL_PER_METER = 10
FRICTION = 1.35
GRAVITY = 9.8
BOUNCY = 0.65
TILE_SIZE = 16

class RigidBody:
    def __init__(self, size, coords, mass=1):
        self.rect = pygame.Rect(coords[0], coords[1], size[0], size[1])
        self.color_rect = (200,0,50)
        self.mass = mass
        self.speed = [0,0]
        self.gravity = 0
        self.label = "Nothing"
        self.last_position = [self.rect.centerx, self.rect.centery]

    def separate_from_other(self, other):
        if self.rect.colliderect(other.rect):
            width = other.rect.width+self.rect.width
            height = other.rect.height+self.rect.height
            delta = float(height)/float(width)
            distance_h = other.rect.centerx-self.last_position[0]
            distance_v = other.rect.centery-self.last_position[1]
            direction = "None"; alpha = 2
            if distance_v < 0: alpha = -2
            if abs(distance_v) > (abs(distance_h)*delta-alpha):
                if distance_v > 0: self.rect.bottom = other.rect.top; direction = "Down"
                else: self.rect.top = other.rect.bottom; direction = "Up"
            else:
                if distance_h > 0: self.rect.right = other.rect.left; direction = "Right"
                else: self.rect.left = other.rect.right; direction = "Left"
            return [direction, other]
        return False

    def get_speed_from_collide (self, speed, other):
        delta_speed = (self.mass*speed[0]+other.mass*speed[1]+BOUNCY*(speed[0]-speed[1]))/(self.mass+other.mass)
        speed = delta_speed
        return speed

    def set_gravity(self, speed):
        self.gravity = speed

    def add_speed(self, speed):
        self.rect.centerx += int(speed[0])
        self.rect.centery += int(speed[1])

    def is_colliding(self, object_list, type):
        collision = []
        for objectA in object_list:
            if objectA.label == type:
                collide_data = self.separate_from_other(objectA)
                if collide_data != False:
                    if collide_data[0] == "Down":
                        self.speed[1] = self.get_speed_from_collide((self.speed[1],objectA.speed[1]), objectA)
                        self.speed[0] = self.speed[0]/FRICTION

                    if collide_data[0] == "Right" or collide_data[0] == "Left":
                        self.speed[0] = self.get_speed_from_collide((self.speed[1],objectA.speed[0]), objectA)
                    collision.append(collide_data)
        return collision

    def move_and_collide(self, object_list, type, speed):
        self.last_position = [self.rect.centerx, self.rect.centery]
        self.add_speed((0,speed[1]))
        self.add_speed((speed[0],0))
        collision = self.is_colliding(object_list, type)
        return collision

    def draw(self, surface):
        pygame.draw.rect(surface,self.color_rect,self.rect)

    def update(self, is_moving=True):
        self.speed[1]+=self.gravity/PIXEL_PER_METER
        if is_moving: self.add_speed((self.speed[0], self.speed[1]))

class Block(RigidBody):
    def __init__(self, size, coords, mass=1000):
        RigidBody.__init__(self, size, coords, mass)
        self.color_rect = (20,20,20)
        self.label = "Block"

class Box(Block):
    def __init__(self, coords):
        Block.__init__(self, (32,32), coords, mass=70)
        self.color_rect = (170,70,20)
        self.label = "Box"
        self.set_gravity(GRAVITY)

    def update(self, object_list):
        Block.update(self, False)
        self.move_and_collide(object_list,"Block",(self.speed[0], self.speed[1]))

class Player(RigidBody):
    def __init__(self, coords):
        RigidBody.__init__(self, (16,28), coords, mass=20)
        self.keymap = {
            "Right" : pygame.K_RIGHT,
            "Left" : pygame.K_LEFT,
            "Down" : pygame.K_DOWN,
            "Up" : pygame.K_UP,
            "ButtonA" : pygame.K_z,
            "ButtonB" : pygame.K_x,
            "ButtonC" : pygame.K_c
        }
        self.set_gravity(GRAVITY)
        self.label = "Player"
        self.walk_speed = 3
        self.jump_speed = 7
        self.timer = {
            "Jump" : [0, 6]
        }
        self.metadata = {
            "CanJump": False,
            "Jumped": False,
            "Grabed" : [False,0]
        }

    def basic_movements(self, keyboard):
        self.metadata["Jumped"] = False
        if bool(keyboard[self.keymap["ButtonB"]]) and self.metadata["CanJump"]:
            if self.timer["Jump"][0] <= self.timer["Jump"][1]:
                self.speed[1] = -self.jump_speed
                self.timer["Jump"][0] += 1
            else:
                self.metadata["CanJump"] = False
        else:
            if self.metadata["CanJump"]: self.metadata["Jumped"] = True
            self.timer["Jump"][0] = 0
        if bool(keyboard[self.keymap["ButtonB"]]):
            self.metadata["Grabed"][0] = False
        if self.metadata["Jumped"]: self.metadata["CanJump"] = False
        walk_direction = keyboard[self.keymap["Right"]]-keyboard[self.keymap["Left"]]
        if walk_direction != 0 and self.metadata["Grabed"][0] == False:
            self.speed[0] = self.walk_speed*walk_direction

    def events(self, object_list):
        collide_data = self.move_and_collide(object_list,"Block",(self.speed[0], self.speed[1]))
        for collision in collide_data:
            if collision[0] == "Down": self.metadata["CanJump"] = True
            if collision[0] == "Right" or collision[0] == "Left":
                if abs(collision[1].rect.y-self.rect.y) <= 3 and not self.metadata["CanJump"]:

                    self.metadata["Grabed"] = [True,collision[1].rect.y]
            if collision[0] == "Up": self.speed[1] = 0; self.metadata["CanJump"] = False
        if self.metadata["Grabed"][0] == True:
            self.rect.y = self.metadata["Grabed"][1]
            self.metadata["CanJump"] = True
            self.speed[1] = 0

        for objectA in object_list:
            if objectA.label == "Box":
                if self.rect.colliderect(objectA.rect):
                    collide_data = self.separate_from_other(objectA)
                    if collide_data != False:
                        if collide_data[0] == "Down":
                            self.speed[1] = self.get_speed_from_collide((self.speed[1],objectA.speed[1]), objectA)
                            self.speed[0] = self.speed[0]/FRICTION
                            self.metadata["CanJump"] = True

                        if collide_data[0] == "Right" or collide_data[0] == "Left":
                            objectA.speed[0] = objectA.get_speed_from_collide((objectA.speed[0],self.speed[0]), self)


    def update(self, object_list):
        keyboard = pygame.key.get_pressed()
        self.basic_movements(keyboard)
        RigidBody.update(self, False)
        self.events(object_list)

class Room:
    def __init__(self, file):
        self.canvas = pygame.Surface((640,480))
        self.background_color = (150,150,150)
        self.canvas = pygame.Surface((400,400))
        self.mapdata = file
        self.object_list = []

    def build_map(self):
        self.object_list = []
        for objectA in self.mapdata.objects:
            x, y = objectA.x, objectA.y
            if objectA.type == "Block":
                width, height = objectA.width, objectA.height
                self.add_object(Block((width, height),(x, y)))

    def draw_map(self):
        for y in range(self.mapdata.height):
            for x in range(self.mapdata.width):
                tile = self.mapdata.get_tile_image(x,y,0)
                if tile != None: self.canvas.blit(tile,(x*TILE_SIZE,y*TILE_SIZE))

    def add_object(self, objectA):
        self.object_list.append(objectA)

    def remove_object(self, objectA):
        self.object_list.append(objectA)

    def room_draw(self, surface):
        self.canvas.fill(self.background_color)
        self.draw_map()
        for objectA in self.object_list:
            if objectA.label != "Block": objectA.draw(self.canvas)
        surface.blit(self.canvas,(0,0))
    def room_update(self):
        for objectA in self.object_list:
            if objectA.label != "Player" and objectA.label != "Box": objectA.update()
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
        mapfile = load_pygame("TestArea.tmx")
        room = Room(mapfile)
        room.build_map()

        room.add_object(Box((150,50)))

        room.add_object(Player((100,10)))

        while True:
            self.clock.tick(60)
            surface.fill((150,150,150))
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            room.room_update()
            self.game_draw(surface)

            pygame.display.flip()
if __name__ == "__main__": Game()
