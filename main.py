import arcade,random,math,PIL,time

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 900
SCREEN_TITLE = "PyTetris"
GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 30
FPS = 60.0

# Display Constants
NEXT_SZ=0.9
HOLD_SZ=0.8
LANE_SZ=0.7

# DAS settings
DAS_DELAY = 0.15  # seconds before auto-shift starts
ARR_INTERVAL = 0.05  # seconds between auto-shifts
SOFT_ARR_INTERVAL = 1/30.0

MASTER_TIMINGS = [
    ((0, 499),    {'are':25, 'line_are':25, 'das':14, 'lock':30, 'line_clear':40}),
    ((500, 599),  {'are':25, 'line_are':25, 'das':8, 'lock':26, 'line_clear':25}),
    ((600, 699),  {'are':25, 'line_are':16, 'das':8, 'lock':26, 'line_clear':16}),
    ((700, 799),  {'are':16, 'line_are':12, 'das':8, 'lock':26, 'line_clear':12}),
    ((800, 899),  {'are':12, 'line_are':6,  'das':8, 'lock':26, 'line_clear':6}),
    ((900, 999),  {'are':12, 'line_are':6,  'das':6,  'lock':17, 'line_clear':6}),
    ((1000,1099), {'are':6,  'line_are':6,  'das':6,  'lock':17, 'line_clear':6}),
    ((1100,1199), {'are':5,  'line_are':5,  'das':6,  'lock':15, 'line_clear':6}),
    ((1200,9999), {'are':4,  'line_are':4,  'das':6,  'lock':15, 'line_clear':6}),
]

CR_TIMINGS = [
    [(0,    70,  99), {"COOL":102,"REGRET":160},False,False,False],
    [(100, 170, 199), {"COOL":52,"REGRET":75},False,False,False],
    [(200, 270, 299), {"COOL":49,"REGRET":75},False,False,False],
    [(300, 370, 399), {"COOL":45,"REGRET":68},False,False,False],
    [(400, 470, 499), {"COOL":45,"REGRET":60},False,False,False],
    [(500, 570, 599), {"COOL":42,"REGRET":60},False,False,False],
    [(600, 670, 699), {"COOL":42,"REGRET":50},False,False,False],
    [(700, 770, 799), {"COOL":38,"REGRET":50},False,False,False],
    [(800, 870, 899), {"COOL":38,"REGRET":50},False,False,False],
    [(900, 900, 999), {"COOL": 0,"REGRET":50},False,False,False],
]

DECAY_RATE=[125,80,80,50,50,50,45,45,45,45,40,40,40,40,40,30,30,30,30,30,20,20,20,20,20,15,15,15,15,15,15,15,15,15,15,10,10,10,10,9,9,9,8,8,8,7,7,7,6]

GRADE=[str(i)for i in range(10,0,-1)]
GRADE+=[f"S{i}"for i in range(1,10)]
GRADE+=[f"m{i}"for i in range(1,10)]
GRADE+=["M","MK","MV","MO","MM-","MM","MM+","GM-","GM","GM+","TM-","TM","TM+","ΩM","ΣM","∞M","∞M+"]

GRAVITY = [
    ((  0, 29),  1024),
    (( 30, 34),  1536),
    (( 35, 39),  2048),
    (( 40, 49),  2560),
    (( 50, 59),  3072),
    (( 60, 69),  4096),
    (( 70, 79),  8192),
    (( 80, 89),  12288),
    (( 90, 99),  16384),
    ((100, 119), 20480),
    ((120, 139), 24576),
    ((140, 159), 28672),
    ((160, 169), 32768),
    ((170, 199), 36864),
    ((200, 219), 1024),
    ((220, 229), 8192),
    ((230, 232), 16384),
    ((233, 235), 24576),
    ((236, 238), 32768),
    ((239, 242), 40960),
    ((243, 246), 49152),
    ((247, 250), 57344),
    ((251, 299), 65536),
    ((300, 329), 131072),
    ((330, 359), 196608),
    ((360, 399), 262144),
    ((400, 419), 327680),
    ((420, 449), 262144),
    ((450, 499), 196608),
    ((500, 999), 1310720),
    ]
# Colors
COLORS = {
    'I': (78,172,231),
    'O': (248,211,72),
    'T': (135,48,137),
    'S': (137,192,85),
    'Z': (220,67,51),
    'J': (51,117,186),
    'L': (232,157,69)
}

# SRS rotation and wall kicks
offsets_I = {(0,1):[(1,0),(-1,0),(2,0),(-1,-1),(2,2)], (1,0):[(-1,0),(1,0),(-2,0),(1,1),(-2,-2)],
             (1,2):[(0,-1),(-1,-1),(2,-1),(-1,1),(2,-2)], (2,1):[(0,1),(1,1),(-2,1),(1,-1),(-2,2)],
             (2,3):[(-1,0),(1,0),(-2,0),(1,1),(-2,-2)], (3,2):[(1,0),(-1,0),(2,0),(-1,-1),(2,2)],
             (3,0):[(0,1),(1,1),(-2,1),(1,-1),(-2,2)], (0,3):[(0,-1),(-1,-1),(2,-1),(-1,1),(2,-2)],
             (0,2):[(0,0),(0,1),(1,1),(-1,1),(1,0),(-1,0)], (2,0):[(0,0),(0,-1),(-1,-1),(1,-1),(-1,0),(1,0)],
             (1,3):[(0,0),(1,0),(1,2),(1,1),(0,2),(0,1)], (3,1):[(0,0),(-1,0),(-1,2),(-1,1),(0,2),(0,1)]}

offsets_oth = {(0,1):[(0,0),(-1,0),(-1,1),(0,-2),(-1,-2)], (1,0):[(0,0),(1,0),(1,-1),(0,2),(1,2)],
               (1,2):[(0,0),(1,0),(1,-1),(0,2),(1,2)], (2,1):[(0,0),(-1,0),(-1,1),(0,-2),(-1,-2)],
               (2,3):[(0,0),(1,0),(1,1),(0,-2),(1,-2)], (3,2):[(0,0),(-1,0),(-1,-1),(0,2),(-1,2)],
               (3,0):[(0,0),(-1,0),(-1,-1),(0,2),(-1,2)], (0,3):[(0,0),(1,0),(1,1),(0,-2),(1,-2)],
               (0,2):[(1,-1),(0,1),(1,1),(-1,1),(1,0),(-1,0)], (2,0):[(-1,1),(0,-1),(-1,-1),(1,-1),(-1,0),(1,0)],
               (1,3):[(-1,-1),(1,0),(1,2),(1,1),(0,2),(0,1)], (3,1):[(1,1),(-1,0),(-1,2),(-1,1),(0,2),(0,1)]}
SRS_OFFSETS = {'I': offsets_I, 'O': {}, 'other': offsets_oth}

# Up,Right=+
# Tetromino shapes
SHAPES = {
    'I': [
        [(-1,0),(0,0),(1,0),(2,0)],
        [(0,1),(0,0),(0,-1),(0,-2)],
        [(-2,0),(-1,0),(0,0),(1,0)],
        [(0,2),(0,1),(0,0),(0,-1)]
        ],
    'O': [
        [(0,0),(1,0),(0,1),(1,1)]
        ]*4,
    'T': [
        [(-1,0),(0,0),(1,0),(0,1)],
        [(0,1),(0,0),(0,-1),(1,0)],
        [(-1,0),(0,0),(1,0),(0,-1)],
        [(0,1),(0,0),(0,-1),(-1,0)]
        ],
    'S': [
        [(-1,0),(0,0),(0,1),(1,1)],
        [(0,1),(0,0),(1,0),(1,-1)],
        [(-1,-1),(0,-1),(0,0),(1,0)],
        [(-1,1),(-1,0),(0,0),(0,-1)]
        ],
    'Z': [
        [(-1,1),(0,1),(0,0),(1,0)],
        [(1,1),(1,0),(0,0),(0,-1)],
        [(-1,0),(0,0),(0,-1),(1,-1)],
        [(0,1),(0,0),(-1,0),(-1,-1)]
        ],
    'J': [
        [(-1,1),(-1,0),(0,0),(1,0)],
        [(0,1),(0,0),(0,-1),(1,1)],
        [(-1,0),(0,0),(1,0),(1,-1)],
        [(-1,-1),(0,1),(0,0),(0,-1)]
        ],
    'L': [
        [(-1,0),(0,0),(1,0),(1,1)],
        [(0,1),(0,0),(0,-1),(1,-1)],
        [(-1,-1),(-1,0),(0,0),(1,0)],
        [(-1,1),(0,1),(0,0),(0,-1)]
        ]
}
SHAPE_PLACE=[x for x in SHAPES.keys()]
def get_master_timing(level):
    for (low, high), t in MASTER_TIMINGS:
        if low <= level <= high:
            return t
    return MASTER_TIMINGS[-1][1]

def SNO(shape):
    if shape=="O":
        dx=-0.5
        dy=-0.5
    elif shape=="I":
        dx=-0.5
        dy=0
    else:
        dx=0
        dy=-0.5
    return dx,dy

def ELO(shape):
    if shape=="O":
        dx=0
    else:
        dx=1
    return dx

def ERO(shape):
    if shape=="I":
        dx=2
    else:
        dx=1
    return dx

class Piece:
    def __init__(self, shape,spawn=1):
        self.shape = shape
        self.rotation = 0
        self.blocks = SHAPES[shape]
        self.last_kick=0
        if spawn==-1:
            self.x = 1+spawn+ELO(shape)
        elif spawn==1:
            self.x=GRID_WIDTH//2
        else:
            self.x=GRID_WIDTH-(1+ERO(shape))
        self.y = GRID_HEIGHT-2

    def current_coords(self):
        return [(self.x+dx, self.y+dy) for dx, dy in self.blocks[self.rotation]]

    def rotate(self, dir, grid):
        old, new = self.rotation, (self.rotation+dir)%4
        offsets = SRS_OFFSETS.get(self.shape, SRS_OFFSETS['other']).get((old,new), [(0,0)])
        for i, (ox, oy) in enumerate(offsets):
            self.rotation, self.x, self.y = new, self.x+ox, self.y+oy
            if self._valid(grid): self.last_kick=i;return True
            self.rotation, self.x, self.y = old, self.x-ox, self.y-oy
        return False

    def _valid(self, grid):
        for x,y in self.current_coords():
            if x<0 or x>=GRID_WIDTH or y<0 or grid[y][x] is not None: return False
        return True

class Tetris(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color((106,90,205))
        self.block_sprite=[[[[] for _ in range(8)] for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.hold_sprite=[[] for _ in range(8)]
        self.next_sprite=[[] for _ in range(8)]
        self.lane_sprite=[[[] for _ in range(5)] for _ in range(8)]
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                for i in range(8):
                    block=arcade.Sprite(
                        arcade.Texture(PIL.Image.open("./image/block.png").convert("RGBA")).crop(30*(i%4),30*(i//4),30,30),
                        center_x=300+(x+0.5)*CELL_SIZE, center_y=100+(y+0.5)*CELL_SIZE, 
                        image_width=30,
                        image_height=30)
                    self.block_sprite[y][x][i]=block
        for a,(i,v) in enumerate(SHAPES.items()):
            ns=int(CELL_SIZE*NEXT_SZ);hs=int(CELL_SIZE*HOLD_SZ);ls=int(CELL_SIZE*LANE_SZ)
            f=SNO(i)
            n=[];h=[];l=[[] for _ in range(5)]
            for dx,dy in v[0]:
                dx+=f[0];dy+=f[1]
                h.append(
                    arcade.Sprite(
                        arcade.Texture(PIL.Image.open("./image/block.png").convert("RGBA").resize((hs*4,hs*2),PIL.Image.Resampling.LANCZOS)).crop(hs*(a%4),hs*(a//4),hs,hs),
                        center_x=200+dx*hs, center_y=95+(GRID_HEIGHT-2)*CELL_SIZE+dy*hs, 
                        image_width=hs,image_height=hs)
                    )
                n.append(
                    arcade.Sprite(
                        arcade.Texture(PIL.Image.open("./image/block.png").convert("RGBA").resize((ns*4,ns*2),PIL.Image.Resampling.LANCZOS)).crop(ns*(a%4),ns*(a//4),ns,ns),
                        center_x=300+(GRID_WIDTH)*CELL_SIZE+dx*ns, center_y=110+(GRID_HEIGHT+2)*CELL_SIZE+dy*ns, 
                        image_width=ns,
                        image_height=ns)
                    )
                for j in range(5):
                    l[j].append(
                        arcade.Sprite(
                            arcade.Texture(PIL.Image.open("./image/block.png").convert("RGBA").resize((ls*4,ls*2),PIL.Image.Resampling.LANCZOS)).crop(ls*(a%4),ls*(a//4),ls,ls),
                            center_x=350+(GRID_WIDTH+1)*CELL_SIZE+dx*ls, center_y=110+(GRID_HEIGHT-2-j*3)*CELL_SIZE+dy*ls, 
                            image_width=ls,
                            image_height=ls)
                        )
            self.hold_sprite[a]=h
            self.next_sprite[a]=n
            self.lane_sprite[a]=l
        self.reset_game()

    def reset_game(self):
        self.start_time = time.time()
        self.section_start_time = self.start_time
        self.section=0
        self.g_section=GRAVITY[:]
        self.gs=0
        self.cr_section=CR_TIMINGS[:]
        self.cool_count = 0
        self.regret_count = 0
        self.grid = [[None]*GRID_WIDTH for _ in range(GRID_HEIGHT)]
        k=random.sample(["I","T","J","L"],1)
        w=list(SHAPES.keys());w.remove(k[0])
        self.bag = k+random.sample(w, 6)
        self.hold = None
        self.hold_used = False
        self.up_used = False
        self.next_pieces = []
        self.level = 0
        self.speed_level = 0
        self.in_grade = 0
        self.gp=0
        self.cool = 0
        self.regret = 0
        self.score = 0
        self.combo = 0
        self.frame=arcade.Sprite("./image/frame.png")
        self.frame_list=arcade.SpriteList()
        self.block_list=arcade.SpriteList()
        self.hold_list=arcade.SpriteList()
        self.next_list=arcade.SpriteList()
        self.lane_list=arcade.SpriteList()
        self.frame_list.append(self.frame)
        self.frame.center_x, self.frame.center_y=500,450
        self.drop_timer = 0.0
        self.lock_timer = 0.0
        self.are_timer = 0.0
        self.line_are_timer = 0.0
        self.decay_timer=0.0
        self.pending_spawn = False
        self.move_left = self.move_right = self.move_down = False
        self.das_timer = self.arr_timer = 0.0
        self.das_down_timer = self.arr_down_timer = 0.0
        self.spawn_piece()
        self.paused = False
        self.game_over = False
        self.move_floor = 0
        self.p_move = 0

    def spawn_piece(self):
        if self.move_left:
            spawn=-1
        elif self.move_right:
            spawn=0
        else:
            spawn=1
        # increase level on each spawn
        self.level += 1 if (self.level+1)%100!=0 else 0
        if self.level>=self.cr_section[self.section][0][1] and not self.cr_section[self.section][2]:
            self.cr_section[self.section][2]=True
            elapsed = time.time() - self.section_start_time
            if elapsed <= self.cr_section[self.section][1]["COOL"]:
                self.cool+=1
                self.cr_section[self.section][3]=True
        elapsed = time.time() - self.section_start_time
        if elapsed >= self.cr_section[self.section][1]["REGRET"]:
            self.regret+=1
            self.cr_section[self.section][4]=True
        if self.level>self.cr_section[self.section][0][2]:
            self.section+=1
            self.section_start_time=time.time()
        cr_count = max(self.cool - self.regret,0)
        self.speed_level = self.level + cr_count * 100
        self.timing = get_master_timing(self.speed_level)
        while len(self.next_pieces) < 7:
            if len(self.bag)==0:
                self.bag += random.sample(list(SHAPES.keys()), 7)
            self.next_pieces.append(self.bag.pop(0))
        shape = self.next_pieces.pop(0)
        piece=Piece(shape,spawn)
        if not piece._valid(self.grid): self.game_over = True
        else:
            self.piece = piece
            self.hold_used = False
            self.up_used = False

    def on_draw(self):
        self.clear()
        self.block_list.clear()
        self.hold_list.clear()
        self.next_list.clear()
        self.lane_list.clear()
        # Settled blocks
        arcade.draw_rect_filled(
            arcade.rect.XYWH(300+5*CELL_SIZE, 100+10*CELL_SIZE, CELL_SIZE*GRID_WIDTH, CELL_SIZE*GRID_HEIGHT),(0,0,0,100))
        for y, row in enumerate(self.grid):
            for x, color in enumerate(row):
                if color:
                    i=SHAPE_PLACE.index(color);b=self.block_sprite[y][x][i]
                    if not self.block_list.__contains__(b):
                        self.block_list.append(b)
        for x, y in self.piece.current_coords():
            i=SHAPE_PLACE.index(self.piece.shape);b=self.block_sprite[y][x][i]
            if not self.block_list.__contains__(b):
                self.block_list.append(b)
        arcade.draw_rect_filled(
                arcade.rect.XYWH(300+(GRID_WIDTH)*CELL_SIZE, 120+(GRID_HEIGHT+2)*CELL_SIZE, CELL_SIZE*5, CELL_SIZE*4),
                (0,0,0,100)
            )
        arcade.draw_rect_filled(
                arcade.rect.XYWH(350+(GRID_WIDTH+1)*CELL_SIZE, 115+(GRID_HEIGHT-8)*CELL_SIZE, CELL_SIZE*4, CELL_SIZE*15),
                (0,0,0,100)
            )
        arcade.draw_rect_filled(
                arcade.rect.XYWH(205, 650, 160, 140),
                (0,0,0,100)
            )
        self.frame_list.draw()
        # Ghost piece
        ghost = Piece(self.piece.shape)
        ghost.rotation = self.piece.rotation
        ghost.x, ghost.y = self.piece.x, self.piece.y
        while ghost._valid(self.grid):
            ghost.y -= 1
        if ghost.y!=self.piece.y:
            ghost.y += 1
            for x, y in ghost.current_coords():
                arcade.draw_rect_outline(
                    arcade.rect.XYWH(300+(x+0.5)*CELL_SIZE, 100+(y+0.5)*CELL_SIZE, CELL_SIZE-1, CELL_SIZE-1),
                    arcade.color.RED,border_width=2
                )
        self.block_list.draw()
        for y, row in enumerate(self.grid):
            if self.pending_spawn and all(c is not None for c in row):
                delay = self.line_are_timer or self.are_timer
                arcade.draw_rect_filled(
                    arcade.rect.XYWH(300+5*CELL_SIZE, 100+(y+0.5)*CELL_SIZE, CELL_SIZE*GRID_WIDTH, CELL_SIZE-1),
                    (255,255,255,int(200*delay))
                )
        # Active piece
        for x, y in self.piece.current_coords():
            if self.pending_spawn:
                delay = self.line_are_timer or self.are_timer
                arcade.draw_rect_filled(
                arcade.rect.XYWH(300+(x+0.5)*CELL_SIZE, 100+(y+0.5)*CELL_SIZE, CELL_SIZE-1, CELL_SIZE-1),
                (255,255,255,int(255*delay)))
            elif ghost.y==self.piece.y:
                arcade.draw_rect_filled(
                arcade.rect.XYWH(300+(x+0.5)*CELL_SIZE, 100+(y+0.5)*CELL_SIZE, CELL_SIZE-1, CELL_SIZE-1),
                (0,0,0,int(150*(self.lock_timer*FPS/self.timing['lock'])))
            )
        # Hold display
        if self.hold:
            i=SHAPE_PLACE.index(self.hold);b=self.hold_sprite[i]
            if not self.hold_list.__contains__(b[0]):
                for x in b:
                    self.hold_list.append(x)
            self.hold_list.draw()
            if self.hold_used:
                csz=int(CELL_SIZE*HOLD_SZ)
                f=SNO(self.hold)
                for dx, dy in SHAPES[self.hold][0]:
                    dx+=f[0];dy+=f[1]
                    arcade.draw_rect_filled(
                        arcade.rect.XYWH(200+dx*csz, 95+(GRID_HEIGHT-2)*CELL_SIZE+dy*csz, csz-1, csz-1),
                        (0,0,0,100)
                    )

        # Next pieces
        i=SHAPE_PLACE.index(self.next_pieces[0]);b=self.next_sprite[i]
        if not self.next_list.__contains__(b[0]):
            for x in b:
                self.next_list.append(x)
        for j in range(1,6):
            i=SHAPE_PLACE.index(self.next_pieces[j]);b=self.lane_sprite[i][j-1]
            if not self.lane_list.__contains__(b[0]):
                for x in b:
                    self.lane_list.append(x)
        
        self.next_list.draw()
        self.lane_list.draw()
        # score display
        arcade.draw_text(f"Score: {self.score}", 10, SCREEN_HEIGHT-20, arcade.color.WHITE, 14)
        arcade.draw_text(f"Level: {self.level}", 150, SCREEN_HEIGHT-20, arcade.color.WHITE, 14)
        arcade.draw_text(f"Grade:{self.grade}", 10, SCREEN_HEIGHT-40, arcade.color.GOLD, 16)
        if self.cr_section[self.section][3]:
            d="COOL"
            c=arcade.color.AQUA
        if self.cr_section[self.section][4]:
            d="REGRET"
            c=arcade.color.ORANGE if self.cr_section[self.section][3] else arcade.color.RED
        if not (self.cr_section[self.section][3] or self.cr_section[self.section][4]):
            d=""
            c=arcade.color.WHITE
        arcade.draw_text(f"{d}", 10, SCREEN_HEIGHT-60, c, 14)

        if self.paused:
            arcade.draw_text("PAUSED", SCREEN_WIDTH/2-50, SCREEN_HEIGHT/2, arcade.color.WHITE, 24)
        if self.game_over:
            arcade.draw_text("GAME OVER", SCREEN_WIDTH/2-80, SCREEN_HEIGHT/2, arcade.color.RED, 24)

    def clear_check(self):
        return self.grid[:]!=[r for r in self.grid if any(c is None for c in r)]

    def get_ingrade(self,cleared):
        if cleared==1:
            if self.in_grade<5:pt=10
            elif self.in_grade<10:pt=5
            else: pt=2
            cm=1
        elif cleared==2:
            if self.in_grade<3:pt=20
            elif self.in_grade<6:pt=15
            elif self.in_grade<10:pt=12
            else: pt=10
            cm=1+0.1*(self.combo//2) if self.combo<10 else 2
        elif cleared==3:
            if self.in_grade==0:pt=40
            elif self.in_grade<4:pt=30
            elif self.in_grade<7:pt=20
            elif self.in_grade<10:pt=15
            else: pt=13
            cm=1+0.1*(self.combo+2) if self.combo<10 else 2.5
        else:
            if self.in_grade==0:pt=50
            elif self.in_grade<5:pt=40
            else: pt=30
            cm=1.5+0.2*min(max(self.combo-2,0),5)+0.1*max(self.combo-5,0) if self.combo<10 else 3
        if self.combo==1: cm=1
        return math.ceil(pt*cm)*(1+self.level//250)
        
    def clear_lines(self):
        new_grid = [r for r in self.grid if any(c is None for c in r)]
        cleared = GRID_HEIGHT - len(new_grid)
        for _ in range(cleared):
            new_grid.append([None] * GRID_WIDTH)
        self.grid = new_grid
        if cleared > 0:
            self.combo += 1
            self.in_grade += self.get_ingrade(cleared)
        else:
            self.combo = 0
        self.level += max(1,2*(cleared-1)) if cleared > 0 else 0
        return cleared

    def on_update(self, dt):
        if self.paused or self.game_over: return
        if self.pending_spawn:
            delay = self.line_are_timer or self.are_timer
            delay -= dt
            if self.line_are_timer:
                self.line_are_timer = delay
            else:
                self.are_timer = delay
            if delay <= 0:
                cleared = self.clear_lines()
                self.spawn_piece()
                self.are_timer = 0.0
                self.line_are_timer = 0.0
                self.pending_spawn = False
            return
        # handle DAS horizontal
        if self.move_left or self.move_right:
            self.das_timer += dt
            if self.das_timer >= self.timing['das']/FPS:
                self.arr_timer += dt
                if self.arr_timer >= SOFT_ARR_INTERVAL:  # immediate ARR
                    self.arr_timer = 0
                    self.move_floor+=1 if self.lock_timer!=0 else 0
                    dx = -1 if self.move_left else 1
                    self.piece.x += dx
                    if not self.piece._valid(self.grid): self.piece.x -= dx
        # handle DAS soft drop
        if self.move_down:
            if self.das_down_timer==0:
                self.try_drop()
            self.das_down_timer += dt
            if self.das_down_timer >= self.timing['das']/FPS:
                self.try_drop()
        # gravity
        self.drop_timer += dt
        while self.drop_timer >= self.gravity()/FPS:
            self.drop_timer -= self.gravity()/FPS
            self.try_drop()
        
        self.decay_timer += dt
        if self.decay_timer >= self.decay()/FPS:
            self.decay_timer= 0
            self.in_grade=max(self.in_grade-1,0)
            
        if not all(0<=nx<GRID_WIDTH and ny>=0 and self.grid[ny][nx] is None
               for nx,ny in [(x,y-1) for x,y in self.piece.current_coords()]):
            self.lock_timer+=dt
        else:
            self.lock_timer=0
        if self.p_move!=self.move_floor:
            self.lock_timer=0
            self.p_move=self.move_floor
        if self.lock_timer>=self.timing['lock']/FPS or self.move_floor>=15:
            self.lock_piece()
        self.get_grade()

    def get_grade(self):
        g=self.in_grade
        if math.floor(self.in_grade + max(self.cool - self.regret,0))>=100:
            self.gp+=1
            self.in_grade=0
        self.grade=GRADE[self.gp]
        
    def decay(self):
        return DECAY_RATE[min(len(DECAY_RATE)-1,int(self.gp))]
    
    def gravity(self):
        while self.speed_level > self.g_section[self.gs][0][1]:
            self.gs+=1
        return 65536/self.g_section[self.gs][1]
        
    def try_drop(self):
        if all(0<=nx<GRID_WIDTH and ny>=0 and self.grid[ny][nx] is None
               for nx,ny in [(x,y-1) for x,y in self.piece.current_coords()]):
            self.piece.y-=1
            self.lock_timer=0
            self.move_floor=0

    def lock_piece(self):
        for x,y in self.piece.current_coords(): self.grid[y][x]=self.piece.shape
        # apply line clear ARE if any lines
        cl=self.clear_check()
        if cl:
            self.line_are_timer = self.timing['line_are']/FPS
        else:
            self.are_timer = self.timing['are']/FPS
        self.pending_spawn = True
        self.lock_timer = 0
        self.drop_timer = 0
        self.move_floor = 0


    def on_key_press(self,key,_):
        if key == arcade.key.R or (key==arcade.key.ESCAPE and self.game_over):self.reset_game();return
        elif key==arcade.key.ESCAPE: self.paused=not self.paused;return
        if self.paused or self.game_over: return
        if key==arcade.key.LEFT:
            self.move_left=True;self.move_right=False;self.das_timer=0
            self.move_floor+=1 if self.lock_timer!=0 else 0
            self.piece.x-=1
            if not self.piece._valid(self.grid): self.piece.x+=1
        elif key==arcade.key.RIGHT:
            self.move_right=True;self.move_left=False;self.das_timer=0;self.arr_timer=0
            self.piece.x+=1
            self.move_floor+=1 if self.lock_timer!=0 else 0
            if not self.piece._valid(self.grid): self.piece.x-=1
        elif key==arcade.key.DOWN:
            self.move_down=True;self.das_down_timer=0
        elif key==arcade.key.UP and not self.pending_spawn:
            while all(0<=nx<GRID_WIDTH and ny>=0 and self.grid[ny][nx] is None
                      for nx,ny in [(x,y-1) for x,y in self.piece.current_coords()]):
                self.piece.y-=1
            self.up_used=True
            self.lock_piece()
        elif key==arcade.key.RSHIFT:
            while all(0<=nx<GRID_WIDTH and ny>=0 and self.grid[ny][nx] is None
                      for nx,ny in [(x,y-1) for x,y in self.piece.current_coords()]):
                self.piece.y-=1
        elif key in (arcade.key.Z,arcade.key.X,arcade.key.C):
            self.piece.rotate(-1 if key==arcade.key.Z else 1,self.grid)
            self.move_floor+=1 if self.lock_timer!=0 else 0
            if key==arcade.key.C: self.piece.rotate(1,self.grid)
        elif key==arcade.key.A and not (self.hold_used or self.up_used):
            if self.hold is None: self.hold,self.piece=self.piece.shape,None;self.spawn_piece()
            else: self.hold,self.piece.shape=self.piece.shape,self.hold;self.piece = Piece(self.piece.shape)
            self.hold_used=True

    def on_key_release(self,key,_):
        if key==arcade.key.LEFT: self.move_left=False
        elif key==arcade.key.RIGHT: self.move_right=False
        elif key==arcade.key.DOWN: self.move_down=False

if __name__=='__main__':
    Tetris()
    arcade.run()
