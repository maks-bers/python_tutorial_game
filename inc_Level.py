import pygame
import random
import json

from inc_SpriteSheet import SpriteSheet
from inc_Sprite import Sprite

''' Level

    This replaces the orignal "Terrain" class

    Handles all level effects, such as background, ceiling, ground and everything else

    
    script = dict
    { milliseconds : "COMMAND"}

    * ceiling and ground can come in from offscreen
    * c/g can scroll (different speeds)
    * command: load different sprite for objects (or just kill object and make a new one?)

    * darkness
    * background image
    * stars

    Terrain ceiling/ground:
        There will be collision checking against the player and the enemies

        Image is loaded and then uses a special function "get_image_extend" to place
        a duplicate of the image at the end.  Both images together create one long 
        "sprite" that is 640x40.  This makes scrolling and wrapping easy!

        Once the terrain has scrolled off the screen, it will move to 
        replace the position of the second image (middle of the entire sprite).  
'''
class Level(object):
    ''' Init
        This function is called automatically when we initialize the Class
    '''
    def __init__(self):
        super().__init__()

        # Distance is used to go through the script
        self.distance = 0
        self.distance_timer = pygame.time.get_ticks()

        # Load the script [from file]
        level_data = { 
            # Level entry, in space
            1: { 'name': "STARFIELD", 'speed': 'fast' },
            2: { 'name': "FADE", 'value': 255, 'color': (0,0,0)},


            100: { 'name': "ENEMY", 'type': 10, 'x': 320, 'y': 50 },
            150: { 'name': "ENEMY", 'type': 10, 'x': 320, 'y': 50 },
            200: { 'name': "ENEMY", 'type': 10, 'x': 320, 'y': 50 },
            250: { 'name': "ENEMY", 'type': 11, 'x': 320, 'y': 50 },

            300: { 'name': "ENEMY", 'type': 10, 'x': 320, 'y': 150 },
            350: { 'name': "ENEMY", 'type': 10, 'x': 320, 'y': 150 },
            400: { 'name': "ENEMY", 'type': 10, 'x': 320, 'y': 150 },
            450: { 'name': "ENEMY", 'type': 11, 'x': 320, 'y': 150 },

            451: { 'name': "ENEMY", 'type': 12, 'x': 320, 'y': 100 },

            452: { 'name': "STARFIELD", 'speed': 'slow' },

            510: { 'name': "ENEMY", 'type': 10, 'x': 320, 'y': 50 },
            530: { 'name': "ENEMY", 'type': 10, 'x': 320, 'y': 100 },
            550: { 'name': "ENEMY", 'type': 10, 'x': 320, 'y': 150 },
            570: { 'name': "ENEMY", 'type': 10, 'x': 320, 'y': 200 },

            600: { 'name': "ENEMY", 'type': 13, 'x': 320, 'y': 70 },
            601: { 'name': "ENEMY", 'type': 13, 'x': 320, 'y': 130 },
            602: { 'name': "STARFIELD", 'speed': 'none' },
            603: { 'name': 'BACKGROUND', 'file':'assets/Images/background.png'},
            604: { 'name': "FADE", 'value': 0, 'color': (0,0,0)},

            # Landscape intro here

            # In cave
            801: { 'name': "DARKNESS" },

            # mini-boss enemy pattern
            1001: { 'name': "BRIGHTNESS" }, # lol?
            1000: { 'name': "ENEMY", 'type': 13, 'x': 320, 'y': 70 },
            1010: { 'name': "ENEMY", 'type': 13, 'x': 320, 'y': 100 },
            1020: { 'name': "ENEMY", 'type': 13, 'x': 320, 'y': 130 },
            1030: { 'name': "ENEMY", 'type': 13, 'x': 320, 'y': 160 },

            # flash red boss alert
            2002: { 'name': "FADE", 'value': 0, 'color': (0,0,0)},
            2102: { 'name': "FADE", 'value': 255, 'color': (255,0,0)},
            2152: { 'name': "FADE", 'value': 0, 'color': (255,0,0)},
            2202: { 'name': "FADE", 'value': 255, 'color': (255,0,0)},
            2252: { 'name': "FADE", 'value': 0, 'color': (255,0,0)},

            2300: { 'name': "BOSS", 'type': 1}, # boss #1 yay
            2500: { 'name': "ENEMY", 'type': 12, 'x': 320, 'y': 100 },
            3000: { 'name': "ENEMY", 'type': 12, 'x': 320, 'y': 100 },
            3500: { 'name': "ENEMY", 'type': 12, 'x': 320, 'y': 100 },
            4000: { 'name': "ENEMY", 'type': 12, 'x': 320, 'y': 100 },
            4500: { 'name': "ENEMY", 'type': 12, 'x': 320, 'y': 100 },


        }

        # Save Level
        level_json = json.dumps(level_data)
        file = open('assets/Levels/earth.level', 'w')
        file.write(level_json)
        file.close()

        # Load Level
        with open('assets/Levels/earth.level') as readfile:
            self.script = json.load(readfile)
    

        # Flag variables signal when to spawn things outside of the level handler
        self.enemy_flag = False
        self.boss_flag = False

        # Effect: Darkness
        self.darkness_scale = 0 # scaling for the "darkness" screen effect
        self.darkness_timer = 0
        self.darkness_flag = False

        # Effect: Starfield (Scrolling stars)
        self.starfield_active = False
        self.starfield_timer = 0
        self.starfield_flag = False
        self.starfield_speed = 'slow'
        self.starfield_velocity = 0

        # Effect: Background (static image)
        self.background_active = False
        self.background_image = ''
        self.background_loaded = False

        # Effect: Fade 
        self.fade_level = 0  # start at 0 opacity
        self.fade_target = 0  
        self.fade_timer = 0
        self.fade_color = (0,0,0)



        # Unique objects -- delete this section (move to increment)
        self.objects = pygame.sprite.Group()

        # Ceiling and Ground
        ceiling = Sprite("assets/Images/ceiling.png", 320, 240, True) # filename, width, height, collidable
        ceiling.float_y = 0  # override default
        self.objects.add(ceiling)

        ground = Sprite("assets/Images/ground.png", 320, 240, True)
        ground.float_y = 200  # override default
        self.objects.add(ground)


    ''' Increment
        Progresses distance and handles any script events
    '''
    def increment(self):
        # Increment the distance, which is the key of the script dictionary
        if pygame.time.get_ticks() > self.distance_timer + 1:
            self.distance_timer = pygame.time.get_ticks()
            self.distance += 1

        if pygame.time.get_ticks() > self.starfield_timer:
            self.starfield_flag = True
            # the faster stars are, they aren't on screen long, so have shorter timers
            if self.starfield_speed == 'slow':
                self.starfield_timer = pygame.time.get_ticks() + random.randrange(0, 1000)
                self.starfield_velocity = random.randrange(-10, -1) / 10
            elif self.starfield_speed == 'medium':
                self.starfield_timer = pygame.time.get_ticks() + random.randrange(0, 500)
                self.starfield_velocity = random.randrange(-25, -10) / 10
            elif self.starfield_speed == 'fast':
                self.starfield_timer = pygame.time.get_ticks() + random.randrange(0, 100)
                self.starfield_velocity = random.randrange(-100, -25) / 10

        distance_str = str(self.distance)
        if distance_str in self.script:
            self.script_object = self.script[distance_str]
            print( "Script: [", self.distance, "] " , self.script_object)
            # Handle Script Keywords
            if self.script_object['name'] == "ENEMY":
                self.enemy_flag = self.script_object # store details for when the actual enemy spawns
            if self.script_object['name'] == "DARKNESS":
                self.darkness_scale = 300 # percent scale
                self.darkness_timer = pygame.time.get_ticks()
                self.darkness_flag = True
            if self.script_object['name'] == "BRIGHTNESS":
                self.darkness_scale = 100 # percent scale
                self.darkness_timer = pygame.time.get_ticks()
                self.darkness_flag = False
            if self.script_object['name'] == "STARFIELD":
                self.starfield_timer = pygame.time.get_ticks()
                self.starfield_speed = self.script_object['speed']
                if self.script_object['speed'] == 'none':
                    self.starfield_active = False
                else:
                    self.starfield_active = True
            if self.script_object['name'] == "BACKGROUND":
                self.background_active = True
                self.background_file = self.script_object['file']
                self.background_loaded = False
                if self.background_file == 'none':
                    self.background_active = False
            if self.script_object['name'] == "FADE":
                self.fade_target = self.script_object['value']
                self.fade_color = self.script_object['color']
            if self.script_object['name'] == "BOSS":
                self.boss_flag = self.script_object # store boss details

            del(self.script[distance_str])



    '''  Update
        Handles animations and timing
    '''
    def update(self):

        if pygame.time.get_ticks() > self.fade_timer + 10:
            self.fade_timer = pygame.time.get_ticks()
            if self.fade_level < self.fade_target:
                self.fade_level += 2
            if self.fade_level > self.fade_target:
                self.fade_level -= 2
            

        '''
        # Scroll the terrain
        self.ceiling.float_x -= 0.4
        self.ground.float_x -= 1

        # float_y = 0 # Top of Screen
        if self.ceiling.float_y < 0:
            self.ceiling.float_y += 0.1

        # float_y = 200 # Bottom, minus 40 pixels high
        if self.ground.float_y > 200:
            self.ground.float_y -= 0.1

        # Offscreen
        if self.ceiling.float_x < -320:
            self.ceiling.float_x = 0 # replace the "second" sprite with the first one for "smooth scrolling"
        if self.ground.float_x < -320:
            self.ground.float_x = 0 
        '''

        self.objects.update()


    ''' Draw
        Places all of the level objects
    '''
    def draw(self, win):

        self.objects.draw(win)


