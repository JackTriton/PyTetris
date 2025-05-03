import arcade,random,math

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 900
SCREEN_TITLE = "Tetris"
GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 30
FPS = 60.0

# DAS settings
DAS_DELAY = 0.15  # seconds before auto-shift starts
ARR_INTERVAL = 0.05  # seconds between auto-shifts
SOFT_ARR_INTERVAL = 1/30.0

MASTER_TIMINGS = [
    ((0, 499),    {'are':25, 'line_are':25, 'das':14, 'lock':30, 'line_clear':40}),
    ((500, 599),  {'are':25, 'line_are':25, 'das':8, 'lock':30, 'line_clear':25}),
    ((600, 699),  {'are':25, 'line_are':16, 'das':8, 'lock':30, 'line_clear':16}),
    ((700, 799),  {'are':16, 'line_are':12, 'das':8, 'lock':30, 'line_clear':12}),
    ((800, 899),  {'are':12, 'line_are':6,  'das':8, 'lock':30, 'line_clear':6}),
    ((900, 999),  {'are':12, 'line_are':6,  'das':6,  'lock':17, 'line_clear':6}),
    ((1000,1099), {'are':6,  'line_are':6,  'das':6,  'lock':17, 'line_clear':6}),
    ((1100,1199), {'are':5,  'line_are':5,  'das':6,  'lock':15, 'line_clear':6}),
    ((1200,9999), {'are':4,  'line_are':4,  'das':6,  'lock':15, 'line_clear':6}),
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
        self.reset_game()

    def reset_game(self):
        self.grid = [[None]*GRID_WIDTH for _ in range(GRID_HEIGHT)]
        self.bag = random.sample(list(SHAPES.keys()), 7)
        self.hold = None
        self.hold_used = False
        self.next_pieces = []
        self.level = 0
        self.score = 0
        self.combo = 0
        self.frame=arcade.Sprite("./image/frame.png")
        self.frame_list=arcade.SpriteList()
        self.frame_list.append(self.frame)
        self.frame.center_x, self.frame.center_y=300+5*CELL_SIZE, 100+10*CELL_SIZE
        self.drop_timer = 0.0
        self.lock_timer = 0.0
        self.are_timer = 0.0
        self.line_are_timer = 0.0
        self.pending_spawn = False
        self.move_left = self.move_right = self.move_down = False
        self.das_timer = self.arr_timer = 0.0
        self.das_down_timer = self.arr_down_timer = 0.0
        self.spawn_piece()
        self.paused = False
        self.game_over = False
        self.move_floor=0

    def spawn_piece(self):
        if self.move_left:
            spawn=-1
        elif self.move_right:
            spawn=0
        else:
            spawn=1
        # increase level on each spawn
        self.level += 1 if (self.level+1)%100!=0 else 0
        self.timing = get_master_timing(self.level)
        if len(self.bag) < 7: self.bag += random.sample(list(SHAPES.keys()), 7)
        shape = self.bag.pop(0)
        self.piece = Piece(shape,spawn)
        while len(self.next_pieces) < 6:
            if len(self.bag) < 7:
                self.bag += random.sample(list(SHAPES.keys()), 7)
            self.next_pieces.append(self.bag.pop(0))
        self.hold_used = False
        if not self.piece._valid(self.grid): self.game_over = True

    def on_draw(self):
        self.clear()
        # Settled blocks
        arcade.draw_rect_filled(
            arcade.rect.XYWH(300+5*CELL_SIZE, 100+10*CELL_SIZE, CELL_SIZE*GRID_WIDTH, CELL_SIZE*GRID_HEIGHT),(0,0,0,100))
        for y, row in enumerate(self.grid):
            for x, color in enumerate(row):
                if color:
                    arcade.draw_rect_filled(
                        arcade.rect.XYWH(300+(x+0.5)*CELL_SIZE, 100+(y+0.5)*CELL_SIZE, CELL_SIZE-1, CELL_SIZE-1),
                        color
                    )
                    arcade.draw_rect_outline(
                        arcade.rect.XYWH(300+(x+0.5)*CELL_SIZE, 100+(y+0.5)*CELL_SIZE, CELL_SIZE-1, CELL_SIZE-1),
                        arcade.color.BLACK,border_width=2
                    )
            if self.pending_spawn and all(c is not None for c in row):
                delay = self.line_are_timer or self.are_timer
                arcade.draw_rect_filled(
                    arcade.rect.XYWH(300+5*CELL_SIZE, 100+(y+0.5)*CELL_SIZE, CELL_SIZE*GRID_WIDTH, CELL_SIZE-1),
                    (255,255,255,int(200*delay))
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
        # Active piece
        for x, y in self.piece.current_coords():
            arcade.draw_rect_filled(
                arcade.rect.XYWH(300+(x+0.5)*CELL_SIZE, 100+(y+0.5)*CELL_SIZE, CELL_SIZE-1, CELL_SIZE-1),
                COLORS[self.piece.shape]
            )
            arcade.draw_rect_outline(
                arcade.rect.XYWH(300+(x+0.5)*CELL_SIZE, 100+(y+0.5)*CELL_SIZE, CELL_SIZE-1, CELL_SIZE-1),
                arcade.color.BLACK,border_width=2
            )
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
            for dx, dy in SHAPES[self.hold][0]:
                csz=CELL_SIZE*0.8
                f=SNO(self.hold)
                dx+=f[0];dy+=f[1]
                arcade.draw_rect_filled(
                    arcade.rect.XYWH(130+dx*csz, 100+(GRID_HEIGHT-2)*CELL_SIZE+dy*csz, csz-1, csz-1),
                    COLORS[self.hold]
                )
                arcade.draw_rect_outline(
                    arcade.rect.XYWH(130+dx*csz, 100+(GRID_HEIGHT-2)*CELL_SIZE+dy*csz, csz-1, csz-1),
                    arcade.color.BLACK,border_width=2
                )
                if self.hold_used:
                    arcade.draw_rect_filled(
                        arcade.rect.XYWH(130+dx*csz, 100+(GRID_HEIGHT-2)*CELL_SIZE+dy*csz, csz-1, csz-1),
                        (0,0,0,100)
                    )

        # Next pieces
        arcade.draw_rect_filled(
                arcade.rect.XYWH(360+(GRID_WIDTH)*CELL_SIZE, 150+(GRID_HEIGHT+2)*CELL_SIZE, CELL_SIZE*5, CELL_SIZE*4),
                (0,0,0,100)
            )
        for dx,dy in SHAPES[self.bag[0]][0]:
            csz=CELL_SIZE*0.9
            f=SNO(self.bag[0])
            dx+=f[0];dy+=f[1]
            arcade.draw_rect_filled(
                arcade.rect.XYWH(360+(GRID_WIDTH)*CELL_SIZE+dx*csz, 150+(GRID_HEIGHT+2)*CELL_SIZE+dy*csz, csz-1, csz-1),
                COLORS[self.bag[0]]
            )
            arcade.draw_rect_outline(
                arcade.rect.XYWH(360+(GRID_WIDTH)*CELL_SIZE+dx*csz, 150+(GRID_HEIGHT+2)*CELL_SIZE+dy*csz, csz-1, csz-1),
                arcade.color.BLACK,border_width=2
            )
        for idx, shape in enumerate(self.bag[1:6]):
            csz=CELL_SIZE*0.7
            for dx, dy in SHAPES[shape][0]:
                f=SNO(shape)
                dx+=f[0];dy+=f[1]
                arcade.draw_rect_filled(
                    arcade.rect.XYWH(360+(GRID_WIDTH+2)*CELL_SIZE+dx*csz, 100+(GRID_HEIGHT-2-idx*3)*CELL_SIZE+dy*csz, csz-1, csz-1),
                    COLORS[shape]
                )
                arcade.draw_rect_outline(
                    arcade.rect.XYWH(360+(GRID_WIDTH+2)*CELL_SIZE+dx*csz, 100+(GRID_HEIGHT-2-idx*3)*CELL_SIZE+dy*csz, csz-1, csz-1),
                    arcade.color.BLACK,border_width=2
                )
        # score display
        arcade.draw_text(f"Score: {self.score}", 10, SCREEN_HEIGHT-20, arcade.color.WHITE, 14)
        arcade.draw_text(f"Level: {self.level}", 150, SCREEN_HEIGHT-20, arcade.color.WHITE, 14)

        if self.paused:
            arcade.draw_text("PAUSED", SCREEN_WIDTH/2-50, SCREEN_HEIGHT/2, arcade.color.WHITE, 24)
        if self.game_over:
            arcade.draw_text("GAME OVER", SCREEN_WIDTH/2-80, SCREEN_HEIGHT/2, arcade.color.RED, 24)

    def clear_check(self):
        return self.grid[:]!=[r for r in self.grid if any(c is None for c in r)]

    def clear_lines(self):
        new_grid = [r for r in self.grid if any(c is None for c in r)]
        cleared = GRID_HEIGHT - len(new_grid)
        for _ in range(cleared):
            new_grid.append([None] * GRID_WIDTH)
        self.grid = new_grid
        sc = math.ceil((self.level + cleared) / 4) * cleared
        if cleared > 0:
            self.combo += 1
            sc *= self.combo
        else:
            self.combo = 0
        if all(all(cell is None for cell in row) for row in self.grid):
            sc *= 4
        self.score += sc
        self.level += cleared
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
            self.das_down_timer += dt
            if self.das_down_timer >= self.timing['das']/FPS:
                self.arr_down_timer += dt
                if self.arr_down_timer >= self.timing['line_clear']/FPS:
                    self.try_drop(dt)
        # gravity
        self.drop_timer += dt
        if self.drop_timer >= self.timing['are']/FPS:
            self.drop_timer -= self.timing['are']/FPS
            self.try_drop(dt)

    def try_drop(self,dt=None):
        if all(0<=nx<GRID_WIDTH and ny>=0 and self.grid[ny][nx] is None
               for nx,ny in [(x,y-1) for x,y in self.piece.current_coords()]):
            self.piece.y-=1
            self.lock_timer=0
            self.move_floor=0
        else:
            self.lock_timer+=dt if dt is not None else 1
            if self.lock_timer>=self.timing['lock']/FPS or self.move_floor>=15:
                self.lock_piece()

    def lock_piece(self):
        for x,y in self.piece.current_coords(): self.grid[y][x]=COLORS[self.piece.shape]
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
            self.try_drop()
        elif key==arcade.key.UP and not self.pending_spawn:
            while all(0<=nx<GRID_WIDTH and ny>=0 and self.grid[ny][nx] is None
                      for nx,ny in [(x,y-1) for x,y in self.piece.current_coords()]):
                self.piece.y-=1
            self.lock_piece()
        elif key in (arcade.key.Z,arcade.key.X,arcade.key.C):
            self.piece.rotate(-1 if key==arcade.key.Z else 1,self.grid)
            self.move_floor+=1 if self.lock_timer!=0 else 0
            if key==arcade.key.C: self.piece.rotate(1,self.grid)
        elif key==arcade.key.A and not self.hold_used:
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
