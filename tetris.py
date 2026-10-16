# Tetris for Casio fx-CG100 - made by Amante de Cristo, using Claude AI
from casioplot import *
LEFT,RIGHT,DOWN,UP,OK,EXE = 23,25,34,14,24,95
KEYS = (23,25,34,14,24,95)
CELL,PW,PH,OX,OY = 8,10,20,140,16
SPEEDS = (32,22,14)  # idle ticks per row (bigger = slower)
LOCK = 8             # ticks you can still slide after landing
HOLD,REP = 120,50     # hold-to-repeat delay and rate (bigger = slower)
HK = 10              # held-key loops that count as 1 gravity tick (smaller = falls faster while holding)
NAMES = ("Easy","Normal","Hard")
TXT = ("","SINGLE","DOUBLE","TRIPLE","TETRIS!")
ABC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
BG,EMPTY,FG = (12,14,20),(26,29,40),(240,244,255)
MUTED,ACCENT,RED = (120,130,155),(0,190,255),(255,80,90)
GREEN,GOLD = (80,230,120),(255,200,60)
MT = ((130,18,"TETRIS",ACCENT,"large"),(112,62,"Choose speed",MUTED,"medium"),
 (130,92,"1  Easy",GREEN,"medium"),(130,117,"2  Normal",GOLD,"medium"),(130,142,"3  Hard",RED,"medium"),
 (100,168,"Made by Amante de Cristo",MUTED,"small"),(100,180,"using Claude AI",MUTED,"small"))
SH = (("00102030","10111213"),("00100111",),
 ("10011121","10112112","01112112","10011112"),("10200111","10112122"),
 ("00101121","20112112"),("10110212","00011121","00100102","01112122"),
 ("00010212","00102001","00101112","20011121"))
WH = ((4,1),(2,2),(3,2),(3,2),(3,2),(2,3),(2,3))
CL = ((0,210,240),(250,210,40),(170,80,220),(60,210,90),(240,70,70),(70,110,255),(255,150,40))
R = [7]
MS = [""]
HS = [[0,"---"],[0,"---"],[0,"---"],[0,"---"],[0,"---"]]
def rnd():
 R[0] = (R[0]*75+74) % 65537
 return R[0] % 7
def lit(v): return v+70 if v < 186 else 255
class Piece:
 def __init__(self):
  self.i = rnd()
  self.r = 0
  self.c = CL[self.i]
  self.x = 3
  self.y = 0
 def blocks(self):
  s = SH[self.i][self.r]
  return [(self.x+int(s[j]),self.y+int(s[j+1])) for j in (0,2,4,6)]
 def rot(self,d): self.r = (self.r+d) % len(SH[self.i])
def fits(grid,p):
 for x,y in p.blocks():
  if x < 0 or x >= PW or y >= PH: return False
  if y >= 0 and grid[y][x] is not None: return False
 return True
def landed(grid,p):
 p.y += 1
 r = not fits(grid,p)
 p.y -= 1
 return r
def rect(x,y,w,h,c):
 for j in range(y,y+h):
  for i in range(x,x+w): set_pixel(i,j,c)
def blk(px,py,c,n):
 lt = c
 if c != EMPTY: lt = (lit(c[0]),lit(c[1]),lit(c[2]))
 for i in range(n-1):
  for j in range(n-1):
   if i == 0 or j == 0: set_pixel(px+i,py+j,lt)
   else: set_pixel(px+i,py+j,c)
def cell(x,y,c): blk(OX+x*CELL,OY+y*CELL,c,CELL)
def draw_field(grid):
 for y in range(PH):
  for x in range(PW):
   c = grid[y][x]
   if c is None: c = EMPTY
   cell(x,y,c)
def show_next(p):
 rect(244,38,48,40,EMPTY)
 w,h = WH[p.i]
 ox = 244+(48-w*8)//2
 oy = 38+(40-h*8)//2
 s = SH[p.i][0]
 for j in (0,2,4,6): blk(ox+int(s[j])*8,oy+int(s[j+1])*8,p.c,8)
def say(t):
 if MS[0] != "": draw_string(244,172,MS[0],BG,"small")
 if t != "": draw_string(244,172,t,GOLD,"small")
 MS[0] = t
def draw_side(mode):
 w,h = PW*CELL,PH*CELL
 for r in ((OX-4,OY-4,w+8,2),(OX-4,OY+h+2,w+8,2),(OX-4,OY-4,2,h+8),(OX+w+2,OY-4,2,h+8)): rect(r[0],r[1],r[2],r[3],ACCENT)
 T = ("SCORE","LINES","LEVEL")
 for i in range(3):
  rect(6,22+i*48,3,32,ACCENT)
  draw_string(14,22+i*48,T[i],MUTED,"small")
 draw_string(14,166,"BEST "+str(HS[0][0]),MUTED,"small")
 draw_string(244,22,"NEXT",MUTED,"small")
 T = ("OK/UP rotate","DOWN soft drop","EXE hard drop")
 for i in range(3): draw_string(244,100+i*14,T[i],MUTED,"small")
 draw_string(244,150,NAMES[mode],GOLD,"medium")
def draw_ui(vals,old):
 for i in range(3):
  if old[i] != vals[i]:
   if old[i] is not None: draw_string(14,36+i*48,old[i],BG,"medium")
   draw_string(14,36+i*48,vals[i],FG,"medium")
   old[i] = vals[i]
 show_screen()
def clear_lines(grid):
 keep = []
 for r in grid:
  if None in r: keep.append(r)
 n = PH-len(keep)
 return [[None]*PW for i in range(n)]+keep,n
def mtext(on):
 for x,y,t,c,s in MT:
  if not on: c = BG
  draw_string(x,y,t,c,s)
def menu():
 mtext(True)
 show_screen()
 mode = -1
 t = 1
 while mode < 0:
  t += 1
  k = getkey()
  if k == 81 or k == 82 or k == 83: mode = k-81; R[0] = t % 65000+1
 mtext(False)
 return mode
def load():
 try:
  f = open("tetris.sc"); p = f.read().split(","); f.close()
  for i in range(5): HS[i] = [int(p[i*2]),p[i*2+1]]
 except: pass
def save():
 try:
  f = open("tetris.sc","w"); f.write(",".join([str(e[0])+","+e[1] for e in HS])); f.close()
 except: pass
def entry(score):
 L = [0,0,0]; c = 0
 rect(90,22,204,148,EMPTY)
 draw_string(100,30,"NEW HIGH SCORE!",GOLD,"medium")
 draw_string(100,54,str(score),FG,"medium")
 draw_string(100,138,"UP/DOWN letter  EXE ok",MUTED,"small")
 draw_string(100,152,"LEFT/RIGHT move",MUTED,"small")
 last = getkey()
 while True:
  rect(120,84,150,34,EMPTY)
  for i in range(3):
   col = FG
   if i == c: col = ACCENT
   draw_string(132+i*40,88,ABC[L[i]],col,"large")
  show_screen()
  k = last
  while k == last: k = getkey()
  last = k
  if k == UP: L[c] = (L[c]+1) % 26
  elif k == DOWN: L[c] = (L[c]+25) % 26
  elif k == RIGHT and c < 2: c += 1
  elif k == LEFT and c > 0: c -= 1
  elif k == EXE: return ABC[L[0]]+ABC[L[1]]+ABC[L[2]]
def add_score(score,nm):
 new = []
 done = False
 for e in HS:
  if not done and score > e[0]: new.append([score,nm]); done = True
  new.append(e)
 for i in range(5): HS[i] = new[i]
 save()
def over(score,lines):
 rect(90,22,204,148,EMPTY)
 draw_string(112,28,"GAME OVER",RED,"large")
 draw_string(104,58,"Score "+str(score)+"  Lines "+str(lines),FG,"small")
 for i in range(5): draw_string(120,78+i*14,str(i+1)+"  "+HS[i][1]+"  "+str(HS[i][0]),GOLD,"small")
 draw_string(104,154,"EXE = menu",MUTED,"small")
 show_screen()
def play(mode):
 base = SPEEDS[mode]
 grid = [[None]*PW for i in range(PH)]
 draw_field(grid)
 draw_side(mode)
 MS[0] = ""
 p = Piece(); nxt = Piece(); show_next(nxt)
 score,lines,level,combo = 0,0,1,0
 old = [None,None,None]
 drawn = []; last = None
 rep,fall,lk,hs = 0,0,0,0
 dead = False; fl = False
 draw_ui([str(score),str(lines),str(level)],old)
 dirty = True
 while not dead:
  key = getkey()
  if key == last: rep += 1
  else: rep = 0
  last = key
  fire = rep == 0 or (rep > HOLD and (rep-HOLD) % REP == 0)
  held = key in KEYS
  lock = False
  if held and fire:
   if key == LEFT or key == RIGHT:
    d = key-24; p.x += d
    if fits(grid,p): dirty = True; lk = 0
    else: p.x -= d
   elif key == DOWN:
    p.y += 1
    if fits(grid,p): score += 1; fall = 0; dirty = True
    else: p.y -= 1
   elif rep == 0 and (key == OK or key == UP):
    p.rot(1); good = fits(grid,p)
    if not good:
     for dx in (1,-1,2,-2):
      p.x += dx
      if fits(grid,p): good = True; break
      p.x -= dx
    if good: dirty = True; lk = 0
    else: p.rot(-1)
   elif rep == 0 and key == EXE:
    while True:
     p.y += 1
     if not fits(grid,p): p.y -= 1; break
     score += 2
    dirty = True; lock = True
  tick = True
  if held:
   hs += 1; tick = hs >= HK
   if tick: hs = 0
  if tick:
   fall += 1
   if landed(grid,p):
    lk += 1
    if lk > LOCK: lock = True
    else:
     c = p.c
     if lk % 2: c = FG
     for x,y in p.blocks():
      if y >= 0: cell(x,y,c)
     fl = True; show_screen()
   else:
    lk = 0; f = base-level
    if f < base//4: f = base//4
    if fall >= f: fall = 0; p.y += 1; dirty = True
  if lock:
   new = p.blocks()
   for x,y in drawn:
    if y >= 0 and (x,y) not in new: cell(x,y,EMPTY)
   for x,y in new:
    if y >= 0: grid[y][x] = p.c; cell(x,y,p.c)
   drawn = []; fl = False; t = ""
   grid,n = clear_lines(grid)
   if n > 0:
    combo += 1; lines += n
    score += ((0,100,300,600,1000)[n]+50*(combo-1))*level
    level = lines//10+1; draw_field(grid); t = TXT[n]
    if combo > 1: t = t+" x"+str(combo)
   else: combo = 0
   say(t); p = nxt; nxt = Piece(); show_next(nxt)
   fall = 0; lk = 0
   if not fits(grid,p): dead = True
   draw_ui([str(score),str(lines),str(level)],old); dirty = True
  if dirty and not dead:
   new = p.blocks()
   for x,y in drawn:
    if y >= 0 and (x,y) not in new: cell(x,y,EMPTY)
   for x,y in new:
    if y >= 0 and (fl or (x,y) not in drawn): cell(x,y,p.c)
   drawn = new; fl = False; dirty = False; show_screen()
 return score,lines
def main():
 rect(0,0,384,192,BG)
 load()
 while True:
  s,l = play(menu())
  if s > HS[4][0]: add_score(s,entry(s))
  over(s,l)
  k = 0
  while k != EXE: k = getkey()
  rect(0,0,384,192,BG)
main()
