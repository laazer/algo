#!/usr/bin/python
# -*- coding: utf-8 -*-

from Tkinter import *
from time import sleep
import numpy as np
from random import randint
from random import randrange
import tkMessageBox
import sys

LEFT = 'left'
RIGHT = 'right'
DOWN = 'down'
UP = 'up'
SPACE = 'space'

SCALE = 40
OFFSET = 3

# Block size

BSIZE = 1

# Taken from https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTEionaUGziAeKbcUJR9pt3XJME76DbXo2DIxwToysbCUOFOsVg

"""
Attache Case Small: 6 x 10 (60 spaces)
Attache Case Medium: 7 x 11 (77 spaces)
Attache Case Large: 8 x 12 (96 spaces)
"""

XBLOCKS = 15
YBLOCKS = 8

MAXY = YBLOCKS
MAXX = int(XBLOCKS * 2)

WINX = MAXX - XBLOCKS

XCENTER = int(MAXX * 0.70)
YCENTER = int(MAXY/2) - 1

direction_d = {'left': (-1, 0), 'right': (1, 0), 'down': (0, 1), 'up' : (0, -1)}

def scale_up(value):
    return value * SCALE

def scale_down(value):
    return int(value/SCALE)

def random_color():
    r = lambda: randint(0,255)
    return '#%02X%02X%02X' % (r(),r(),r())

def enum(**enums):
    return type('Enum', (), enums)

class counter(object):
    def __init__(self, start=0):
        self.default = start
        self.value = start
        
    #increment
    def i(self, i=1):
        self.value = self.value + i
        
    #decrement 
    def d(self, i=1):
        self.value = self.value - i
        
    #reset
    def r(self):
        self.value = self.default
        
    #override methods
    def __eq__(self, other):
        return self.value == other
        
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __repr__(self):
        return str(self.value)
    
    def __call__(self):
        return self.value
    
    def __lt__(self, other):
        return self.value < other
    
    def __le__(self, other):
        return self.value <= other
    
    def __gt__(self, other):
        return self.value > other
    
    def __ge__(self, other):
        return self.value >= other

class Board(Frame):

    """
    The board represents the tetris playing area. A grid of x by y blocks.
    """

    def __init__(
        self,
        parent,
        scale=20,
        max_x=10,
        max_y=20,
        offset=3,
        ):

        Frame.__init__(self, parent)

        # blocks are indexed by there corrdinates e.g. (4,5), these are

        self.landed = {}
        self.parent = parent
        self.scale = scale
        self.max_x = max_x
        self.max_y = max_y
        self.offset = offset
        

        self.canvas = Canvas(parent, height=max_y * scale + offset,
                             width=max_x * scale + offset)
        self.canvas.pack()
        
        self.shape_ids = []
        self.collision_matrix = np.zeros((MAXY, MAXX), dtype=np.int)
            
    
    def check_collision(self):
        for i in range(len(self.collision_matrix)):
            for j in range(len(self.collision_matrix[i])):
                if(self.collision_matrix[i][j] > 1):
                    return True
        return False
    
    def update_collison_matrix(self, x, y, inc=1):
            self.collision_matrix[y][x] = self.collision_matrix[y][x] + inc
            
    def free_space(self):
        cnt = counter()
        for i in range(len(self.collision_matrix)):
            for j in range(len(self.collision_matrix[i])):
                if(self.collision_matrix[i][j] > 0):
                    cnt.i()
        return cnt
        
            
    def get_corner(self):
        return self.collision_matrix[0][0]
            
    def count_free_space(self):
        cnt = counter()
        for i in collision_matrix:
            for j in i:
                if not j:
                    cnt.i()
        return cnt
    
    def output(self):
        for y in xrange(self.max_y):
            line = []
            for x in xrange(self.max_x):
                if self.landed.get((x, y), None):
                    line.append('X')
                else:
                    line.append('.')
            print ''.join(line)

    def add_block(self, (x, y), colour):
        """
        Create a block by drawing it on the canvas, return
        it's ID to the caller.
        """

        rx = x * self.scale
        ry = y * self.scale

        b_id = self.canvas.create_rectangle(rx, ry, rx + self.scale, ry
                + self.scale, fill=colour)
        self.shape_ids.append(b_id)
        self.update_collison_matrix(x,y)
        return b_id

    def draw_graph(self, x, y):
        for i in range(0, XBLOCKS):
            self.canvas.create_line(i * scale_up(BSIZE), 0, i
                                    * scale_up(BSIZE), scale_up(MAXY),
                                    fill='black')
        for j in range(0, YBLOCKS):
            self.canvas.create_line(0, j * scale_up(BSIZE),
                                    scale_up(MAXX - WINX), j
                                    * scale_up(BSIZE), fill='black')
        self.canvas.create_line(scale_up(MAXX - WINX), 0, scale_up(MAXX
                                - WINX), scale_up(MAXY))

    def draw_border(self):
        self.canvas.create_rectangle(3, 3, scale_up(MAXX),
                scale_up(MAXY), outline='black')

    def move_block(self, id, dxdy, xy):
        """
        Move the block, identified by 'id', by x and y. Note this is a
        relative movement, e.g. move 10, 10 means move 10 pixels right and
        10 pixels down NOT move to position 10,10. 
        """

        (dx, dy) = dxdy
        (x, y) = xy
        self.update_collison_matrix(x, y, -1)
        self.canvas.move(id, dx * self.scale, dy * self.scale)
        self.update_collison_matrix(x + dx, y + dy)

    def delete_block(self, id):
        """
        Delete the identified block
        """

        self.canvas.delete(id)

    def check_block(self, (x, y)):
        """
        Check if the x, y coordinate can have a block placed there.
        That is; if there is a 'landed' block there or it is outside the
        board boundary, then return False, otherwise return true.
        """

        if x < 0 or x >= self.max_x or y < 0 or y >= self.max_y:
            return False
        elif self.landed.has_key((x, y)):
            return False
        else:
            return True


class Block(object):

    def __init__(self, id, (x, y)):
        self.id = id
        self.x = x
        self.y = y

    def coord(self):
        return (self.x, self.y)


class shape(object):

    def check_and_create(
        self,
        board,
        coords,
        colour,
        ):
        """
        Check if the blocks that make the shape can be placed in empty coords
        before creating and returning the shape instance. Otherwise, return
        None.
        """

        for coord in coords:
            if not board.check_block(coord):
                return None

        return shape(board, coords, colour)

    def __init__(
        self,
        board,
        coords,
        colour
        ):
        """
        Initialise the shape base.
        """

        self.board = board
        self.blocks = []

        for coord in coords:
            block = Block(self.board.add_block(coord, colour), coord)

            self.blocks.append(block)

    def move(self, direction):
        """
        Move the blocks in the direction indicated by adding (dx, dy) to the
        current block coordinates
        """

        (d_x, d_y) = direction_d[direction]

        for block in self.blocks:

            x = block.x + d_x
            y = block.y + d_y

            if not self.board.check_block((x, y)):
                return False

        for block in self.blocks:

            x = block.x + d_x
            y = block.y + d_y
            self.board.move_block(block.id, (d_x, d_y), (block.x, block.y))

            block.x = x
            block.y = y

        return True
    
    
    def size(self):
        return len(self.coords)

    
    def rotate(self, clockwise=True):
        """
        Rotate the blocks around the 'middle' block, 90-degrees. The
        middle block is always the index 0 block in the list of blocks
        that make up a shape.
        """

        # TO DO: Refactor for DRY

        middle = self.blocks[0]
        rel = []
        for block in self.blocks:
            rel.append((block.x - middle.x, block.y - middle.y))

        # to rotate 90-degrees (x,y) = (-y, x)
        # First check that the there are no collisions or out of bounds moves.

        for idx in xrange(len(self.blocks)):
            (rel_x, rel_y) = rel[idx]
            if clockwise:
                x = middle.x + rel_y
                y = middle.y - rel_x
            else:
                x = middle.x - rel_y
                y = middle.y + rel_x

            if not self.board.check_block((x, y)):
                return False

        for idx in xrange(len(self.blocks)):
            (rel_x, rel_y) = rel[idx]
            if clockwise:
                x = middle.x + rel_y
                y = middle.y - rel_x
            else:
                x = middle.x - rel_y
                y = middle.y + rel_x

            diff_x = x - self.blocks[idx].x
            diff_y = y - self.blocks[idx].y
            self.board.move_block(self.blocks[idx].id, (diff_x, diff_y), (self.blocks[idx].x, self.blocks[idx].y))

            self.blocks[idx].x = x
            self.blocks[idx].y = y

        return True


class shape_limited_rotate(shape):

    """
    This is a base class for the shapes like the S, Z and I that don't fully
    rotate (which would result in the shape moving *up* one block on a 180).
    Instead they toggle between 90 degrees clockwise and then back 90 degrees
    anti-clockwise.
    """

    def __init__(
        self,
        board,
        coords,
        colour,
        ):

        self.clockwise = True
        super(shape_limited_rotate, self).__init__(board, 
                                                   coords,
                                                   colour)

    def rotate(self, clockwise=True):
        """
        Clockwise, is used to indicate if the shape should rotate clockwise
        or back again anti-clockwise. It is toggled.
        """

        super(shape_limited_rotate,
              self).rotate(clockwise=self.clockwise)
        if self.clockwise:
            self.clockwise = False
        else:
            self.clockwise = True

class shape_helper(shape):
    
    @staticmethod
    def matrix_to_coords(matrix):
        coords = []
        xcount = XCENTER
        ycount = YCENTER
        for r in range(len(matrix)):
            r_count = 0
            for c in matrix[r]:
                if (c == 1):
                    coords.append((c * xcount, ycount))
                xcount = xcount + 1
            ycount = ycount + 1
            xcount = XCENTER
        return coords
    
    #TODO
    #creates a matrix from a set of numbers
    @staticmethod
    def numset_to_matrix(numset):
        m_max = max(numset)
        rsl = np.zeros((len(numset), m_max), dtype=np.int)
        for i in range(len(numset)):
            for j in range(numset[i]):
                rsl[i][j] = 1
        return rsl
                
    
    @staticmethod
    def string_to_numset(s):
        return map((lambda i: int(i)), s.split('x')) 
    
    @staticmethod
    def string_to_matrix(s):
        return shape_helper.numset_to_matrix(shape_helper.string_to_numset(s))
    
    @staticmethod
    def mtc(matrix):
        return shape_helper.matrix_to_coords(matrix)
                    

class custom_shape(shape):
    
    def __init__(self, matrix, color=random_color()):
        self.color = color
        self.matrix = matrix
        self.coords = shape_helper.mtc(self.matrix)
        
    def check_and_create(self, board):
        if(self.color == None):
            self.color = random_color()
        return super(custom_shape, self).check_and_create(board, 
                                                     self.coords, 
                                                     self.color)
    
    def max_width(self):
        return max(map(lambda a: len(a), self.matrix))
    
    def max_hieght(self):
        return len(matrix)


Item_Class = enum(
    HERB = "herb",
    GRENADE = "grenade",
    AMMO = "ammo",
    WEAPON = "weapon")


class game_item(custom_shape):
    
    #name:item name, cost:item price, fp:fire power, fs:fire speed, rs: reload speed, clip:clip size
    #stack: max stacking size
    def __init__(self, name, cost, dimensions, fp=-1, fs=-1, rs=-1, clip=-1, stack=-1, color=random_color(), uid=randint(1, 10000), item_class=None):
        self.name = name
        self.cost = cost
        self.fp = fp
        self.fs = fs
        self.clip = clip
        self.uid = uid
        super(game_item, self).__init__(shape_helper.string_to_matrix(dimensions))
        
    def __eq__(self, other):
        return self.name == other.name
        
class stack_item(game_item):
    
    def __init__(self, name, cost, stack, dimensions, item_class=Item_Class.WEAPON):
        self.current_size = 1
        super(stack_item, self).__init__(self, name=name, cost=cost, stack=stack, dimensions="1x2")
        
    def push(self, item):
        rem = self.clip - self.stack
        if item.stack >= rem:
            self.stack = self.clip
            item.stack = item.stack - rem
        else:
            self.stack = self.stack + item.stack
            item.stack = 0
        
        
        
class weapon_item(game_item):
    
    def __init__(self, name, cost, dimensions, fp=-1, fs=-1, rs=-1, clip=-1, stack=-1, color=random_color(), uid=randint(1, 10000)):
        self.current_size = 1
        super(stack_item, self).__init__(self, name=name, cost=cost, stack=stack, dimensions="1x2", item_class=Item_Class.WEAPON)
        
        
class handgun(weapon_item):
    
    def __init__(self):
        super(handgun, self).init__(self, "handgun", 198000, "3x2", 1.0, 0.47, 1.73, 10, handgun_ammo().name)
        
class red9(game_item):
    
    def __init__(self):
        super(red9, self).init__(self, "red9", 335000, "4x2", 1.6, 0.53, 2.73, 8, handgun_ammo().name)
        
class shotgun(game_item):
    
    def __init__(self):
        super(shotgun, self).init__(self, "shotgun", 257000, "8x2", 4.0, 1.53, 3.03, 6, shotgun_ammo().name)
        
class riotgun(game_item):
    
    def __init__(self):
        super(riotgun, self).init__(self, "riotgun", 415000, "8x2", 5.0, 1.53, 3.03, 7, shotgun_ammo().name)
        
class rifle(game_item):
    
    def __init__(self):
        super(rifle, self).init__(self, "rifle", 296000, "9x1", 4.0, 2.73, 4.0, 5, rifle_ammo().name)
        
#semi-auto rifle
class rifle_sauto(game_item):
    
    def __init__(self):
        super(rifle_sauto, self).init__(self, "rifle_sauto", 361000, "7x2", 7.0, 1.43, 2.33, 10, rifle_ammo().name)
        
class killer7(game_item):
    
    def __init__(self):
        super(killer7, self).init__(self, "killer7", 77700, "4x2", 25.0, 0.7, 1.83, 7, magnum_ammo().name)
        
class hand_cannon(game_item):
    
    def __init__(self):
        super(hand_cannon, self).init__(self, "hand_cannon", 779000, "4x2", 30.0, 1.17, 3.67, 3, magnum_ammo().name)
                
class reg_grenade(game_item):
    
    def __init__(self):
        super(reg_grenade, self).init__(self, "reg_grenade", 5000, "1x2", item_class=Item_Class.GRENADE)
        
class flash_grenade(game_item):
    
    def __init__(self):
        super(flash_grenade, self).init__(self, "flash_grenade", 5000, "1x2", item_class=Item_Class.GRENADE)
        
class fire_grenade(game_item):
    
    def __init__(self):
        super(fire_grenade, self).init__(self, "fire_grenade", 5000, "1x2", item_class=Item_Class.GRENADE)
        
class first_aid_spray(game_item):
    
    def __init__(self):
        super(first_aid_spray, self).init__(self, "first_aid_spray", 7500, "1x2", item_class=Item_Class.HERB)
        
#health item
class green_herb(game_item):
    
    def __init__(self):
        super(green_herb, self).init__(self, "green_herb", 5000, "1x2", item_class=Item_Class.HERB)
        
#combined herb
class sweet_green_herb(game_item):
    
    def __init__(self):
        super(sweet_green_herb, self).init__(self, "sweet_green_herb", 7500, "1x2", item_class=Item_Class.HERB)
        
class handgun_ammo(stack_item):
    
    def __init__(self):
        super(handgun_ammo, self).__init__("handgun_ammo", 100, 50)
        
class shotgun_ammo(stack_item):
    
    def __init__(self):
        super(shotgun_ammo, self).__init__("shotgun_ammo", 333, 15)
        
class rifle_ammo(stack_item):
    
    def __init__(self):
        super(rifle_ammo, self).__init__("rifle_ammo", 500, 10)
        
class magnum_ammo(stack_item):
    
    def __init__(self):
        super(magnum_ammo, self).__init__("magnum_ammo", 500, 10)
        
    
class square_shape(shape):

    def __init__(self):
        return
    
    def check_and_create(self, board):
        coords = shape_helper.mtc([[1, 1],
                                   [1, 1]])
        return super(square_shape, self).check_and_create(board, coords,
                'red')

    def rotate(self, clockwise=True):
        """
        Override the rotate method for the square shape to do exactly nothing!
        """
        pass


class test_shape(custom_shape):
    
    def __init__(self):
        super(test_shape, self).__init__(shape_helper.string_to_matrix('4x2'))
        

Build = enum(
	AOE_God=1, #lots of AOE damage
	Close_Combat=2, #low range
	Sustain=3) #sneaky (flash-bangs and handguns)
    
    
class attache(object):
    
    def __init__(self, item_universe, build, board, items):
		self.items = items
		self.build = build
		self.item_universe = item_universe
        #self.build_dic = {Build.AOE_God:0, Build.Close_Combat:0, Build.Sustain:0}
        #self.board = board
	
    """
    def addItem(self, item):
        #Do we add this item? TODO
            self.items[item.uid] = item
            pass

    def remove_item(self, uid):
        #TODO (is this needed)
            del self.items[uid]
            pass

    def item_compare(self, itemA, itemB):
        #TODO
            pass

    def choose_build(self):
        #TODO
            pass

    def check_capacity(self):
        #TODO 
            pass
    """
    
    def reduce_and_sort(self):
        wl = []
        gl = []
        hl = []
        al = []
        il = {Item_Class.WEAPON: wl,
                Item_Class.GRENADE: gl,
                Item_Class.HERB: hl,
                Item_Class.AMMO: al}
        #reduces items to individual lists
        for item in self.items:
            if item.item_class == Item_Class.WEAPON:
                if not item in wl:
                    wl.append(item)
            if item.item_class == Item_Class.GRENADE:
                gl.append(item)
            if item.item_class == Item_Class.HERB:
                hl.append(item)
            if item.item_class == Item_Class.AMMO:
                if item.clip == item.stack: #checks if the stack is full
                    al.append(item)
                for a in al:
                    if item.stack == 0:
                        break
                    if a == item and a.stack < a.clip:
                        a.push(item)
                if item.stack > 0:
                    al.append(item)
        #optimizes item selecttion
        size = counter(WINX * MAXY)
        result = []
        tmp = []
        for key in il.keys():
            ls = il[key]
            if len(ls) > 0:
                if key == Item_Class.WEAPON:
                    tmp = self.optomize(ls, int(size/2))
                    size.d(total_weight(tmp)
                    result = result + tmp[0:2]
                elif key == Item_Class.AMMO:
                    tmp = self.optomize(ls, int(size/2))
                    size.d(total_weight(tmp)
                    result = result + tmp
                elif key == Item_Class.HERB:
                    tmp = self.optomize(ls, int(size/2)
                    size.d(total_weight(tmp)
                    result = result + tmp
                elif key == Item_Class.GRENADE:
                    tmp = self.optomize(ls, size)
                    size.d(total_weight(tmp)
                    result = result + tmp
                    
                    
    def optomize(self, item_list, max_wieght):
        ls = []
        for i in range(len(item_list)):
            item = item_list[i]
            key = item.__class__
            if len(ls) == 0:
                ls.append(item)
            else:
                for j in range(len(ls)):
                    key2 = ls[j].__class__
                    if self.item_universe[key].index(item.item_class) < self.item_universe[key2].index(ls[j].item_class):
                        ls.insert(j, item)
                        break
                    elif j == (len(ls) - 1):
                        ls.append(ls[j])
        while(self.total_weight(ls) > max_wieght):
            ls.pop()
        return ls
    
    def total_weight(self, item_list):
        return sum(map(lambda i: i.size))
                       
                        
    

        
class game_controller(object):

    """
    Main game loop and receives GUI callback events for keypresses etc...
    """

    def __init__(self, parent):
        """
        Intialise the game...
        """

        self.parent = parent
        self.delay = 1000  # ms


        self.board = Board(parent, scale=SCALE, max_x=MAXX, max_y=MAXY,
                           offset=OFFSET)
        
        # lookup table
        self.shapes = [test_shape()]
        for i in range(40):
            self.shapes.append(test_shape())
            
        self.item_universe = {
            handgun: [Build.Sustain, Build.Close_Combat, Build.AOE_God], 
            red9: [Build.Sustain, Build.Close_Combat, Build.AOE_God], 
            shotgun: [Build.AOE_God, Build.Close_Combat, Build.Sustain], 
            riotgun: [Build.AOE_God, Build.Close_Combat, Build.Sustain], 
            rifle: [Build.Sustain, Build.Close_Combat, Build.AOE_God],
            rifle_sauto: [Build.Sustain, Build.Close_Combat, Build.AOE_God],
            killer7: [Build.Close_Combat, Build.AOE_God, Build.Sustain], 
            hand_cannon: [Build.Close_Combat, Build.AOE_God, Build.Sustain], 
            reg_grenade: [Build.Sustain, Build.AOE_God, Build.Close_Combat], 
            flash_grenade: [Build.Close_Combat, Build.Sustain, Build.AOE_God],
            fire_grenade: [Build.AOE_God, Build.Close_Combat, Build.Sustain], 
            first_aid_spray: [], #empty list == good in all builds
            green_herb: [], 
            sweet_green_herb: [], 
            handgun_ammo: [Build.Sustain, Build.Close_Combat, Build.AOE_God], 
            shotgun_ammo: [Build.AOE_God, Build.Close_Combat, Build.Sustain], 
            rifle_ammo: [Build.Sustain, Build.Close_Combat, Build.AOE_God], 
            magnum_ammo: [Build.Close_Combat, Build.AOE_God, Build.Sustain]
            }
        
        #self.attache = attache(self.item_universe, self.board)
        

        #index of current shape
        self.shape_num = 0

        #self.board.pack(side=BOTTOM)

        self.parent.bind('<Left>', self.left_callback)
        self.parent.bind('<Right>', self.right_callback)
        self.parent.bind('<space>', self.space_callback)
        self.parent.bind('<Down>', self.down_callback)
        self.parent.bind('<Up>', self.up_callback)
        #self.parent.bind('<1>', self.one_callback)
        self.parent.bind('a', self.a_callback)
        self.parent.bind('s', self.s_callback)
        self.parent.bind('p', self.p_callback)
        self.parent.bind('x', self.x_callback)
        self.parent.bind('z', self.z_callback)

        self.shape = self.get_next_shape()

        # self.board.output()

        self.after_id = self.parent.after(self.delay,
                self.move_my_shape)

        
        self.board.draw_border()
        self.board.draw_graph(XBLOCKS, YBLOCKS)
    
    def handle_move(self, direction):
        return self.shape.move(direction)
    
    def left_callback(self, event):
        if self.shape:
            self.handle_move(LEFT)

    def right_callback(self, event):
        if self.shape:
            self.handle_move(RIGHT)

    def space_callback(self, event):
        self.change_shape()

    def down_callback(self, event):
        if self.shape:
            self.handle_move(DOWN)
    
    def up_callback(self, event):
        if self.shape:
            self.handle_move(UP)

    def a_callback(self, event):
        if self.shape:
            self.shape.rotate(clockwise=True)

    def s_callback(self, event):
        if self.shape:
            self.shape.rotate(clockwise=False)

    def p_callback(self, event):
        self.parent.after_cancel(self.after_id)
        tkMessageBox.askquestion(title='Paused!', message='Continue?',
                                 type=tkMessageBox.OK)
        self.after_id = self.parent.after(self.delay,
                self.move_my_shape)
        
    def x_callback(self, event):
        self.easy_place()
        
    def z_callback(self, event):
        self.move_to_corner()

    def move_my_shape(self):
        if self.shape:
            self.after_id = self.parent.after(self.delay,
                    self.move_my_shape)
    
    def change_shape(self):
        #delete section, comment back in to keep it
        """
        for block in self.shape.blocks:
            self.board.delete_block(block.id)
        """
        #print self.board.collision_matrix
        if(not self.board.check_collision()):
            if(self.shape_num >= len(self.shapes)):
                self.shape_num = 0
            self.shape = self.shapes[self.shape_num].check_and_create(self.board)
            self.shape_num = self.shape_num + 1
        return self.shape
        
            
    def get_next_shape(self):
        """
        Randomly select which tetrominoe will be used next.
        """

        the_shape = self.shapes[randint(0, len(self.shapes) - 1)]
        return the_shape.check_and_create(self.board)
    
    
    def easy_place(self):
        place = [0, 0, 0, 0]
        #left, right, up, down
        cs = self.shape #current shape
        cnt = counter(WINX * MAXY)
        for shape in self.shapes:
            self.move_to_corner()
            while(cs.blocks[0].id == self.change_shape().blocks[0].id and cnt > 0):
                if(place[0] <= WINX - 5):
                #if(place[0] <= WINX):
                    self.handle_move(RIGHT)
                    place[0] = place[0] + 1
                elif(place[2] <= MAXY):
                    self.move_to_edge()
                    place[0] = 0
                    self.handle_move(DOWN)
                    place[2] = place[2] + 1
                else:
                    self.move_to_edge()
                    place[0] = 0
                cnt.d()
            place[0] = 0
            place[2] = 0
            cnt.r()
            cs = self.shape
                
    def move_to_edge(self):
        cnt = counter()
        while(cnt < MAXX):
            self.handle_move(LEFT)
            cnt.i()
            
    def move_to_corner(self):
        cnt = counter(MAXY * MAXX)
        while (cnt > 0):
            self.handle_move(LEFT)
            self.handle_move(UP)
            cnt.d()
        

if __name__ == '__main__':
    root = Tk()
    root.title('Best thing EVER!!!!')
    theGame = game_controller(root)

    root.mainloop()
