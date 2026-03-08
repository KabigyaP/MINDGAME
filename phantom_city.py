"""
╔══════════════════════════════════════════════════════════════════════════╗
║   P H A N T O M   C I T Y  :  N I G H T   P R O T O C O L              ║
║   A Psychological Noir Thriller                                          ║
║                                                                          ║
║   "The city watches. Every choice. Every hesitation. Every nerve."       ║
║                                                                          ║
║   Run:   python3 phantom_city.py   (Python 3.6+, zero install)          ║
╚══════════════════════════════════════════════════════════════════════════╝

ABOUT:
  You are Detective Ray Solano. 3:17 AM. Always raining in Phantom City.
  Five cases. One night. Your reactions reveal more than you know.

PSYCHOLOGICAL FRAMEWORK (peer-reviewed research basis):
  Stress Index     — RT variance, error clustering  [Lazarus & Folkman 1984]
  Anxiety Score    — hypervigilance, threat bias     [Eysenck ACT 2007]
  Depression       — anhedonia proxy, avoidance      [Beck 1979]
  Impulsivity      — pre-cue responses, risk         [Barratt BIS-11 1995]
  Resilience       — recovery curve, retry speed     [Connor-Davidson 2003]
  Susceptibility   — loss aversion, status seeking   [Kahneman & Tversky 1979]
"""

import tkinter as tk
import random, math, time
from collections import deque

# ═══════════════════════════════════════════════════════════
#  WINDOW + LAYOUT
# ═══════════════════════════════════════════════════════════
W, H      = 1100, 680
LB_H      = 52          # letterbox height (cinematic bars)
PLAY_T    = LB_H
PLAY_B    = H - LB_H
PLAY_H    = PLAY_B - PLAY_T
STREET_Y  = PLAY_B - 110   # where the street surface is
SIDEWLK_Y = PLAY_B - 90    # raised sidewalk

# ═══════════════════════════════════════════════════════════
#  COLOUR PALETTE  — noir city night
# ═══════════════════════════════════════════════════════════
# Sky / environment
SKY_TOP    = "#010306"
SKY_BOT    = "#04071a"
FAR_BLD    = "#05080f"    # far buildings
MID_BLD    = "#070c1a"    # mid buildings
NEAR_BLD   = "#0a1025"    # near buildings
STREET_C   = "#060a14"    # wet asphalt
SDWLK_C    = "#08102a"    # sidewalk
HORIZON_C  = "#0d1535"    # slight horizon glow

# Neon / light colors
AMBER      = "#ff9a22"    # street lamp warm
NEON_RED   = "#ff1a44"
NEON_BLUE  = "#0099ff"
NEON_CYAN  = "#00ddff"
NEON_GREEN = "#00ff77"
NEON_PURP  = "#bb44ff"
NEON_PINK  = "#ff33aa"
NEON_GOLD  = "#ffcc00"
NEON_WHITE = "#cce8ff"

# Rain
RAIN_C     = "#4a6aaa"
RAIN_LITE  = "#6688cc"
SPLASH_C   = "#2a4488"

# Character
COAT_C     = "#14182e"
SKIN_C     = "#c4956a"
HAIR_C     = "#1a1008"

# UI
UI_AMBER   = "#ffaa44"
UI_RED     = "#ff3355"
UI_GREEN   = "#33ffaa"
UI_CYAN    = "#00ccff"
UI_DIM     = "#3a4a6a"
UI_HINT    = "#7a9abf"
WHITE      = "#ffffff"
FWHITE     = "#e8f0ff"    # film white (slightly cool)

# Convenience list of neons for random
NEONS = [NEON_RED, NEON_BLUE, NEON_CYAN, NEON_GREEN, NEON_PURP, NEON_PINK, NEON_GOLD]

# ═══════════════════════════════════════════════════════════
#  EASING
# ═══════════════════════════════════════════════════════════
def ease_out(t, p=3):  return 1-(1-max(0.,min(1.,t)))**p
def ease_in(t, p=2):   return max(0.,min(1.,t))**p
def ease_io(t):        t=max(0.,min(1.,t)); return t*t*(3-2*t)
def ease_elastic(t):
    t=max(0.,min(1.,t))
    if t in(0,1): return t
    return 2**(-10*t)*math.sin((t*10-.75)*math.pi*2/3)+1

# ═══════════════════════════════════════════════════════════
#  COLOUR MATH
# ═══════════════════════════════════════════════════════════
def lrp(a, b, t): return a + (b-a)*max(0.,min(1.,t))

def lc(c1, c2, t):
    t=max(0.,min(1.,t))
    r=int(int(c1[1:3],16)*(1-t)+int(c2[1:3],16)*t)
    g=int(int(c1[3:5],16)*(1-t)+int(c2[3:5],16)*t)
    b=int(int(c1[5:7],16)*(1-t)+int(c2[5:7],16)*t)
    return f"#{max(0,min(255,r)):02x}{max(0,min(255,g)):02x}{max(0,min(255,b)):02x}"

def dc(col, f):
    r,g,b=int(col[1:3],16),int(col[3:5],16),int(col[5:7],16)
    return f"#{max(0,min(255,int(r*f))):02x}{max(0,min(255,int(g*f))):02x}{max(0,min(255,int(b*f))):02x}"

def add_col(c1, c2):
    r=min(255,int(c1[1:3],16)+int(c2[1:3],16))
    g=min(255,int(c1[3:5],16)+int(c2[3:5],16))
    b=min(255,int(c1[5:7],16)+int(c2[5:7],16))
    return f"#{r:02x}{g:02x}{b:02x}"

def hsv(h, s=1., v=1.):
    h=(h%360)/360.; i=int(h*6); f2=h*6-i
    p,q,t_=v*(1-s),v*(1-f2*s),v*(1-(1-f2)*s)
    pairs=[(v,t_,p),(q,v,p),(p,v,t_),(p,q,v),(t_,p,v),(v,p,q)]
    r,g,b=pairs[i%6]
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

def col_alpha(col, bg, a):
    """Simulate alpha blending onto background."""
    return lc(bg, col, a)

# ═══════════════════════════════════════════════════════════
#  DRAWING PRIMITIVES
# ═══════════════════════════════════════════════════════════
def glow(c, x, y, r, col, rings=8, fall=0.55, bg=SKY_TOP):
    for i in range(rings, 0, -1):
        t=(i/rings)**2*fall; cr=r*(1+i*0.6/rings)
        c.create_oval(x-cr,y-cr,x+cr,y+cr,fill=lc(bg,col,t),outline="")

def glow_ring(c, x, y, r, col, width=2, rings=3):
    for i in range(rings, 0, -1):
        t=i/rings; cr=r+(rings-i)*2.5
        c.create_oval(x-cr,y-cr,x+cr,y+cr,fill="",
                      outline=lc(SKY_TOP,col,t*0.7),width=max(1,int(width*t)))

def glow_line(c, x1, y1, x2, y2, col, width=2, rings=3):
    for i in range(rings, 0, -1):
        t=i/rings
        c.create_line(x1,y1,x2,y2,fill=lc(SKY_TOP,col,t*0.65),
                      width=max(1,int(width*(1+t*1.4))),smooth=True)

def rr(c, x1, y1, x2, y2, r=8, fill=MID_BLD, outline=UI_DIM, w=1):
    r=min(r,(x2-x1)//2,(y2-y1)//2)
    pts=[x1+r,y1,x2-r,y1,x2,y1,x2,y1+r,x2,y2-r,x2,y2,
         x2-r,y2,x1+r,y2,x1,y2,x1,y2-r,x1,y1+r,x1,y1]
    c.create_polygon(pts,smooth=True,fill=fill,outline=outline,width=w)

def shadow_text(c, x, y, text, font, col, shadow="#000000", soff=2, anchor="center"):
    c.create_text(x+soff, y+soff, text=text, font=font, fill=shadow, anchor=anchor)
    c.create_text(x-1,   y+1,    text=text, font=font, fill=shadow, anchor=anchor)
    c.create_text(x,     y,      text=text, font=font, fill=col,    anchor=anchor)

def tg(c, x, y, text, font, col, gcol, off=3, anchor="center"):
    for dx in range(-off, off+1):
        for dy in range(-off, off+1):
            d=math.sqrt(dx*dx+dy*dy)
            if 0 < d <= off*1.5:
                c.create_text(x+dx,y+dy,text=text,font=font,anchor=anchor,
                              fill=lc(SKY_TOP,gcol,0.5*(1-d/(off*1.9))))
    c.create_text(x,y,text=text,font=font,fill=col,anchor=anchor)

def F(size, bold=False, italic=False):
    style="bold" if bold else ("italic" if italic else "normal")
    return ("Arial", size, style)

def FC(size, bold=False):
    return ("Courier", size, "bold" if bold else "normal")

# ═══════════════════════════════════════════════════════════
#  SCREEN FX LAYER
# ═══════════════════════════════════════════════════════════
class ScreenFX:
    """Grain, letterbox, vignette, color grade."""
    def __init__(self):
        self.grain_intensity = 0.18
        self.tension = 0.        # 0-1, drives color grade
        self.flash_alpha = 0.
        self.flash_col = "#ffffff"
        self.shake_x = 0; self.shake_y = 0
        self.shake_mag = 0.
        self._grain_pts = [(random.randint(0,W), random.randint(0,H)) for _ in range(600)]

    def trigger_flash(self, col="#ffffff", strength=0.7, decay=0.08):
        self.flash_alpha = strength; self.flash_col = col; self._decay = decay

    def trigger_shake(self, mag=10):
        self.shake_mag = max(self.shake_mag, float(mag))

    def step(self):
        self.shake_mag *= 0.78
        if self.shake_mag > 0.5:
            self.shake_x = int(random.gauss(0, self.shake_mag))
            self.shake_y = int(random.gauss(0, self.shake_mag*0.5))
        else:
            self.shake_x = self.shake_y = 0
        if hasattr(self,'_decay'):
            self.flash_alpha = max(0., self.flash_alpha - self._decay)

    def draw_letterbox(self, c):
        """Cinematic black bars — always on."""
        c.create_rectangle(0, 0, W, LB_H, fill="#000000", outline="")
        c.create_rectangle(0, PLAY_B, W, H, fill="#000000", outline="")

    def draw_vignette(self, c):
        steps = 12
        for i in range(steps):
            t = i/steps
            rx = int(W//2*(0.4+t*0.75)); ry = int(H//2*(0.45+t*0.7))
            v = max(0, int((1-t)*0.6*22))
            if v > 0:
                c.create_oval(W//2-rx,H//2-ry,W//2+rx,H//2+ry,
                              fill="",outline=f"#{v:02x}{v:02x}{v:02x}",width=5)

    def draw_grain(self, c):
        """Film grain - subtle noise overlay."""
        intensity = self.grain_intensity + self.tension*0.06
        # Shift grain positions each frame for motion
        for i in range(0, len(self._grain_pts), 2):
            gx, gy = self._grain_pts[i]
            # Only draw a fraction each frame (performance)
            if random.random() < intensity:
                v = random.randint(8, 28)
                c.create_rectangle(gx, gy, gx+1, gy+1,
                                   fill=f"#{v:02x}{v:02x}{v+5:02x}", outline="")

    def draw_flash(self, c):
        if self.flash_alpha < 0.01: return
        v = int(self.flash_alpha*255)
        r2=int(self.flash_col[1:3],16); g2=int(self.flash_col[3:5],16); b2=int(self.flash_col[5:7],16)
        col=f"#{min(255,int(r2*self.flash_alpha)):02x}{min(255,int(g2*self.flash_alpha)):02x}{min(255,int(b2*self.flash_alpha)):02x}"
        c.create_rectangle(0,0,W,H,fill=col,outline="")

    def draw_tension_grade(self, c):
        """Red tint overlay for high tension."""
        if self.tension < 0.1: return
        v = int(self.tension * 22)
        c.create_rectangle(0, PLAY_T, W, PLAY_B,
                           fill=f"#{v:02x}0000", outline="", stipple="gray25")

# ═══════════════════════════════════════════════════════════
#  RAIN SYSTEM  — 320 drops, angled, splashes, reflections
# ═══════════════════════════════════════════════════════════
class RainDrop:
    __slots__ = ('x','y','vx','vy','length','alpha')
    def __init__(self):
        self.reset()
    def reset(self):
        self.x = random.uniform(-50, W+50)
        self.y = random.uniform(-200, PLAY_T+20)
        self.vx = random.uniform(1.8, 3.2)   # wind angle
        self.vy = random.uniform(18, 28)       # fall speed
        self.length = random.uniform(8, 22)
        self.alpha = random.uniform(0.3, 0.9)

class RainSplash:
    __slots__ = ('x','y','r','life','ml','col')
    def __init__(self, x, y):
        self.x=float(x); self.y=float(y); self.r=0.; self.life=22; self.ml=22
        self.col=RAIN_C
    def step(self): self.r=max(0,self.r+0.7); self.life-=1; return self.life>0
    def draw(self, c):
        t=self.life/self.ml; r=self.r
        c.create_oval(self.x-r,self.y-r*0.35,self.x+r,self.y+r*0.35,
                      fill="",outline=lc(STREET_C,self.col,t*0.5),width=1)

class RainSystem:
    def __init__(self, intensity=320):
        self.drops = [RainDrop() for _ in range(intensity)]
        self.splashes = []
        self.intensity = 1.  # multiplier
        # Puddle reflection colors (neon lights reflecting in wet street)
        self.reflection_neons = [
            (random.randint(50,W-50), random.choice(NEONS))
            for _ in range(8)
        ]

    def step(self):
        self.splashes = [s for s in self.splashes if s.step()]
        for d in self.drops:
            d.x += d.vx * self.intensity
            d.y += d.vy * self.intensity
            if d.y > PLAY_B + 10:
                # Create splash at street level
                if d.y < PLAY_B + 30 and random.random() < 0.3:
                    self.splashes.append(RainSplash(d.x, STREET_Y))
                d.reset()

    def draw(self, c):
        # Draw reflection pools first (below street level)
        for rx, rcol in self.reflection_neons:
            ph = math.sin(time.time()*1.2 + rx*0.02)
            length = int(40 + 20*ph)
            alpha = 0.12 + 0.06*ph
            # Puddle shimmer streak
            for i in range(3):
                ry = STREET_Y + 6 + i*4
                c.create_line(rx-length+random.randint(-4,4), ry,
                              rx+length+random.randint(-4,4), ry,
                              fill=lc(STREET_C, rcol, alpha*(1-i*0.25)), width=1)

        # Splashes
        for s in self.splashes: s.draw(c)

        # Rain drops
        for d in self.drops:
            ex = d.x + d.vx * d.length * 0.04
            ey = d.y + d.vy * d.length * 0.04
            col = lc(STREET_C, RAIN_C, d.alpha * self.intensity * 0.8)
            c.create_line(d.x, d.y, ex, ey, fill=col, width=1)

# ═══════════════════════════════════════════════════════════
#  CITY RENDERER  — 3-layer parallax buildings + neons
# ═══════════════════════════════════════════════════════════
class NeonSign:
    def __init__(self, x, y, text, col, size=10):
        self.x=x; self.y=y; self.text=text; self.col=col; self.size=size
        self.flicker_t = random.uniform(0, 100)
        self.flicker_rate = random.uniform(0.02, 0.08)
        self.broken_char = random.randint(0, max(0, len(text)-1)) if random.random()<0.3 else -1
    def draw(self, c, cam_x, layer_speed):
        rx = self.x - cam_x * layer_speed
        if rx < -200 or rx > W+200: return
        # Flicker
        ft = math.sin(time.time()*8 + self.flicker_t)
        if self.broken_char >= 0 and ft > 0.85:
            alpha = 0.15  # off
        else:
            alpha = 0.75 + 0.25*abs(ft)
        col = lc(SKY_TOP, self.col, alpha)
        # Glow
        glow(c, int(rx), self.y, self.size*2.5, self.col, rings=4, fall=0.2)
        c.create_text(int(rx), self.y, text=self.text,
                      font=("Courier", self.size, "bold"), fill=col)

class Building:
    def __init__(self, x, w, h, col, layer):
        self.x=x; self.w=w; self.h=h; self.col=col; self.layer=layer
        self.bot = STREET_Y
        # Generate windows
        self.windows = []
        for wy in range(int(self.bot-h)+12, int(self.bot)-10, 14):
            for wx in range(int(x)+6, int(x+w)-6, 12):
                lit = random.random() < 0.45
                window_col = random.choice([AMBER, NEON_CYAN, NEON_WHITE, "#ff8833"])
                self.windows.append([wx, wy, lit, window_col, random.uniform(0,100)])
        self.neon_sign = None

    def draw(self, c, cam_x, speed):
        rx = self.x - cam_x * speed
        if rx+self.w < -20 or rx > W+20: return
        top = self.bot - self.h
        c.create_rectangle(rx, top, rx+self.w, self.bot,
                           fill=self.col, outline="")
        # Windows
        for wx, wy, lit, wcol, phase in self.windows:
            wrx = wx + rx - self.x
            if lit:
                ft = 0.7 + 0.3*math.sin(time.time()*0.5 + phase)
                c.create_rectangle(wrx-3, wy-3, wrx+3, wy+3,
                                   fill=lc(self.col, wcol, ft*0.85), outline="")
            else:
                c.create_rectangle(wrx-3, wy-3, wrx+3, wy+3,
                                   fill=dc(self.col, 1.4), outline="")

class CityRenderer:
    def __init__(self):
        # Generate 3 layers of buildings that tile
        self.far_buildings   = self._gen_layer(FAR_BLD,  50, 90,  140, 22)
        self.mid_buildings   = self._gen_layer(MID_BLD,  70, 130, 120, 16)
        self.near_buildings  = self._gen_layer(NEAR_BLD, 90, 200, 100, 12)
        # Neon signs
        self.neon_signs = []
        neon_texts = ["HOTEL","BAR","PAWN","JAZZ","24H","DINER","XXX","LIQUOR",
                      "CLUB","CASINO","LOANS","TATTOO","GUNS","DRUGS FREE CLINIC"]
        for _ in range(20):
            bx = random.randint(0, W*3)
            by = random.randint(PLAY_T+40, STREET_Y-60)
            self.neon_signs.append(NeonSign(bx, by,
                                            random.choice(neon_texts),
                                            random.choice(NEONS),
                                            random.randint(9,16)))
        # Street lamps (pairs)
        self.lamps = [(x, STREET_Y-80) for x in range(100, W*3, 220)]
        # Tiled floor for infinite scroll
        self.cam_x = 0.

    def _gen_layer(self, col, min_h, max_h, width_range, n):
        buildings = []
        x = -width_range
        for _ in range(n):
            w = random.randint(60, width_range)
            h = random.randint(min_h, max_h)
            buildings.append(Building(x, w, h, dc(col, random.uniform(0.8,1.2)), 0))
            x += w + random.randint(0, 8)
        # Tile: extend to cover scroll
        total_w = x
        for b in list(buildings):
            buildings.append(Building(b.x + total_w, b.w, b.h, b.col, 0))
            buildings.append(Building(b.x + total_w*2, b.w, b.h, b.col, 0))
        return buildings, total_w

    def set_cam(self, x):
        self.cam_x = x

    def draw_sky(self, c):
        steps = 30
        sky_h = STREET_Y - PLAY_T
        for i in range(steps):
            t = i/steps; y = PLAY_T + int(i*sky_h/steps)
            c.create_rectangle(0, y, W, y+sky_h//steps+1,
                               fill=lc(SKY_TOP, SKY_BOT, t), outline="")
        # Horizon glow (city light pollution)
        for ri in range(6):
            ry = STREET_Y - ri*12 - 5
            alpha = 0.06 * (1-ri/6)
            c.create_rectangle(0, ry, W, ry+14,
                               fill=lc(SKY_BOT, HORIZON_C, alpha), outline="")

    def draw_street(self, c):
        # Wet asphalt
        c.create_rectangle(0, STREET_Y, W, PLAY_B, fill=STREET_C, outline="")
        # Sidewalk
        c.create_rectangle(0, SIDEWLK_Y, W, STREET_Y, fill=SDWLK_C, outline="")
        # Street line reflections
        for x in range(-50, W+100, 120):
            c.create_rectangle(x, STREET_Y+8, x+60, STREET_Y+12,
                               fill=lc(STREET_C,"#ffee88",0.15), outline="")

    def draw_lamps(self, c):
        for lx, ly in self.lamps:
            rx = lx - self.cam_x * 1.0
            if rx < -50 or rx > W+50: continue
            # Post
            c.create_line(int(rx), ly+80, int(rx), ly, fill=dc(SDWLK_C,2.), width=2)
            # Arm
            c.create_line(int(rx), ly, int(rx)+22, ly-10, fill=dc(SDWLK_C,2.), width=2)
            # Glow
            glow(c, int(rx)+22, int(ly)-12, 18, AMBER, rings=6, fall=0.45, bg=STREET_C)
            c.create_oval(int(rx)+18, ly-16, int(rx)+26, ly-8,
                          fill=lc(SKY_TOP,AMBER,0.9), outline="")
            # Light cone on street
            cone_x = int(rx)+22
            c.create_polygon(cone_x-30, STREET_Y+5, cone_x+30, STREET_Y+5,
                             cone_x+12, ly-10, cone_x-12, ly-10,
                             fill=lc(SKY_BOT,AMBER,0.03), outline="")

    def draw(self, c, cam_x=None):
        if cam_x is not None: self.cam_x = cam_x
        self.draw_sky(c)
        # Far buildings
        bldgs, total = self.far_buildings
        for b in bldgs: b.draw(c, self.cam_x % total, 0.25)
        # Mid buildings
        bldgs, total = self.mid_buildings
        for b in bldgs: b.draw(c, self.cam_x % total, 0.55)
        # Neon signs (mid layer)
        for ns in self.neon_signs: ns.draw(c, self.cam_x, 0.55)
        # Near buildings
        bldgs, total = self.near_buildings
        for b in bldgs: b.draw(c, self.cam_x % total, 1.0)
        self.draw_street(c)
        self.draw_lamps(c)

# ═══════════════════════════════════════════════════════════
#  CHARACTER SYSTEM  — detective + NPCs
# ═══════════════════════════════════════════════════════════
class DetectiveSprite:
    """Polygon-animated detective character."""
    ANIM_FRAMES = 12

    def __init__(self, x, y):
        self.x = float(x); self.y = float(y)
        self.walk_frame = 0; self.walking = False
        self.facing = 1     # 1=right, -1=left
        self.target_x = None
        self.speed = 2.8
        self.breath = 0.

    def step(self):
        self.breath += 0.04
        if self.walking:
            self.walk_frame = (self.walk_frame + 1) % self.ANIM_FRAMES
        if self.target_x is not None:
            dx = self.target_x - self.x
            if abs(dx) < self.speed:
                self.x = self.target_x; self.target_x = None; self.walking = False
            else:
                self.facing = 1 if dx > 0 else -1
                self.x += self.speed * self.facing
                self.walking = True

    def draw(self, c, cam_x=0.):
        sx = int(self.x - cam_x); sy = int(self.y)
        f = self.facing
        # Walk cycle — leg angle oscillates
        leg_angle = math.sin(self.walk_frame / self.ANIM_FRAMES * math.pi*2) * 18
        breath_y  = math.sin(self.breath) * 1.5

        # Shadow on ground
        c.create_oval(sx-14, sy+3, sx+14, sy+9, fill=lc(STREET_C,"#000000",0.4), outline="")

        # ─ Legs ─
        for side, ang in [(1, leg_angle), (-1, -leg_angle)]:
            lx = sx + f*side*5
            knee_x = lx + f*math.sin(math.radians(ang))*18
            knee_y = sy - 30 + math.cos(math.radians(abs(ang)))*16
            foot_x = knee_x + f*math.sin(math.radians(ang*0.6))*14
            foot_y = sy + 2
            c.create_line(lx, sy-54+breath_y, knee_x, knee_y,
                          fill=COAT_C, width=5, capstyle="round")
            c.create_line(knee_x, knee_y, foot_x, foot_y,
                          fill=COAT_C, width=4, capstyle="round")
            # Shoe
            c.create_oval(foot_x-5, foot_y-3, foot_x+5+f*3, foot_y+2,
                          fill="#1a1205", outline="")

        # ─ Coat body ─
        arm_swing = math.sin(self.walk_frame / self.ANIM_FRAMES * math.pi*2) * 12
        body_pts = [
            sx-12, sy-54+breath_y,   # left shoulder
            sx+12, sy-54+breath_y,   # right shoulder
            sx+16, sy-20,            # right hip
            sx-16, sy-20             # left hip
        ]
        c.create_polygon(body_pts, fill=dc(COAT_C,1.15), outline="", smooth=True)
        # Coat lapels (lighter)
        c.create_polygon([sx, sy-54+breath_y, sx+f*8, sy-46,
                          sx, sy-40, sx-f*4, sy-46],
                         fill=dc(COAT_C,1.4), outline="")

        # ─ Arms ─
        arm_l_x = sx - f*3 + math.cos(math.radians(arm_swing)) * 12
        arm_l_y = sy - 38 + breath_y + math.sin(math.radians(arm_swing)) * 8
        arm_r_x = sx + f*3 - math.cos(math.radians(arm_swing)) * 12
        arm_r_y = sy - 38 + breath_y - math.sin(math.radians(arm_swing)) * 8
        for ax, ay in [(arm_l_x, arm_l_y), (arm_r_x, arm_r_y)]:
            c.create_line(sx, sy-52+breath_y, int(ax), int(ay),
                          fill=dc(COAT_C,1.2), width=5, capstyle="round")

        # ─ Head ─
        hx = sx; hy = int(sy - 70 + breath_y)
        c.create_oval(hx-9, hy-11, hx+9, hy+5, fill=SKIN_C, outline="")
        # Face details
        eye_x = hx + f*3
        c.create_oval(eye_x-2, hy-5, eye_x+2, hy-1, fill="#1a0a0a", outline="")
        # Hair
        c.create_arc(hx-9, hy-12, hx+9, hy-3, start=0, extent=180,
                     fill=HAIR_C, outline="")

        # ─ Fedora ─
        brim_pts = [hx-14, hy-12, hx+14, hy-12,
                    hx+10, hy-16, hx-10, hy-16]
        c.create_polygon(brim_pts, fill=dc(COAT_C,1.3), outline="")
        c.create_rectangle(hx-8, hy-24, hx+8, hy-13,
                           fill=dc(COAT_C,1.2), outline="")
        # Hat band
        c.create_line(hx-8, hy-16, hx+8, hy-16,
                      fill=dc(COAT_C,0.5), width=2)

class NPCSprite:
    def __init__(self, x, y, col, speed):
        self.x=float(x); self.y=float(y); self.col=col
        self.speed=speed; self.frame=random.randint(0,12)
        self.facing = -1 if speed < 0 else 1
    def step(self):
        self.x += self.speed; self.frame=(self.frame+1)%12
        if self.x > W+100: self.x = -80
        if self.x < -100: self.x = W+80
    def draw(self, c, cam_x=0.):
        sx = int(self.x - cam_x*0.85); sy = int(self.y)
        f = self.facing
        la = math.sin(self.frame/12*math.pi*2)*15
        for side, ang in [(1,la),(-1,-la)]:
            lx=sx+f*side*4
            kx=lx+f*math.sin(math.radians(ang))*13; ky=sy-24+math.cos(math.radians(abs(ang)))*12
            fx=kx+f*math.sin(math.radians(ang*0.5))*10; fy=sy+1
            c.create_line(lx,sy-42,kx,ky,fill=dc(self.col,0.7),width=4,capstyle="round")
            c.create_line(kx,ky,fx,fy,fill=dc(self.col,0.7),width=3,capstyle="round")
        c.create_polygon([sx-9,sy-42,sx+9,sy-42,sx+11,sy-16,sx-11,sy-16],
                         fill=self.col,outline="",smooth=True)
        c.create_oval(sx-6,sy-56,sx+6,sy-44,fill=SKIN_C,outline="")

# ═══════════════════════════════════════════════════════════
#  PARTICLE SYSTEM  — sparks, smoke, impact, data
# ═══════════════════════════════════════════════════════════
class Particle:
    __slots__=('x','y','vx','vy','life','ml','sz','col','kind')
    def __init__(self,x,y,col,vx=0.,vy=0.,life=50,sz=3.,kind="spark"):
        self.x=float(x);self.y=float(y)
        self.vx=float(vx);self.vy=float(vy)
        self.life=life;self.ml=life;self.sz=sz;self.col=col;self.kind=kind
    def step(self):
        self.x+=self.vx;self.y+=self.vy;self.life-=1
        if   self.kind=="spark": self.vy+=0.25;self.vx*=0.92
        elif self.kind=="smoke": self.vy-=0.04;self.sz+=0.08;self.vx+=random.uniform(-.03,.03)
        elif self.kind=="data":  self.vy-=0.28
        elif self.kind=="trail": self.sz*=0.9
        return self.life>0
    def draw(self,c):
        t=self.life/self.ml;r=max(0.5,self.sz*t)
        col=lc(SKY_TOP,self.col,t)
        if self.kind=="smoke":
            c.create_oval(self.x-r,self.y-r,self.x+r,self.y+r,
                          fill=lc(SKY_TOP,self.col,t*0.2),outline="")
        elif self.kind=="data":
            c.create_text(int(self.x),int(self.y),text=random.choice("01"),
                          font=("Courier",7),fill=col)
        else:
            c.create_oval(self.x-r,self.y-r,self.x+r,self.y+r,fill=col,outline="")

class PS:
    def __init__(self,cap=500):
        self.p=[];self.cap=cap
    def emit(self,x,y,col,n=1,**kw):
        for _ in range(n):
            if len(self.p)<self.cap:
                self.p.append(Particle(x,y,col,**kw))
    def burst(self,x,y,col,n=16,spd=4.):
        for _ in range(n):
            a=random.uniform(0,math.pi*2);sp=random.uniform(spd*0.3,spd)
            self.emit(x,y,col,vx=math.cos(a)*sp,vy=math.sin(a)*sp,
                      life=random.randint(35,70),sz=random.uniform(2,5.5))
    def smoke_puff(self,x,y,col,n=8):
        for _ in range(n):
            self.emit(x,y,col,vx=random.uniform(-1,1),vy=random.uniform(-2,-0.5),
                      life=random.randint(40,80),sz=random.uniform(4,10),kind="smoke")
    def step(self): self.p=[p for p in self.p if p.step()]
    def draw(self,c): [p.draw(c) for p in self.p]
    def clear(self): self.p.clear()

# ═══════════════════════════════════════════════════════════
#  TYPEWRITER TEXT  — cinematic narrative system
# ═══════════════════════════════════════════════════════════
class TypewriterText:
    def __init__(self):
        self.lines = []       # list of {'text': str, 'color': str, 'font': tuple, 'y': int, 'x': int, 'anchor': str}
        self.current_line = 0
        self.char_idx = 0
        self.char_timer = 0
        self.char_speed = 2   # frames per character
        self.done = False
        self.blink = 0

    def set_text(self, lines, speed=2):
        """lines: list of (text, color, font, x, y, anchor)"""
        self.lines = lines
        self.current_line = 0
        self.char_idx = 0
        self.char_timer = 0
        self.char_speed = speed
        self.done = False

    def step(self):
        self.blink += 1
        if self.done: return
        self.char_timer += 1
        if self.char_timer >= self.char_speed:
            self.char_timer = 0
            if self.current_line < len(self.lines):
                text = self.lines[self.current_line][0]
                self.char_idx += 1
                if self.char_idx > len(text):
                    self.char_idx = 0
                    self.current_line += 1
            else:
                self.done = True

    def skip(self):
        """Skip to end."""
        self.current_line = len(self.lines)
        self.char_idx = 0
        self.done = True

    def draw(self, c):
        for i, (text, col, font, x, y, anchor) in enumerate(self.lines):
            if i < self.current_line:
                # Fully revealed line
                shadow_text(c, x, y, text, font, col, anchor=anchor)
            elif i == self.current_line:
                # Partially revealed
                partial = text[:self.char_idx]
                shadow_text(c, x, y, partial, font, col, anchor=anchor)
                # Blinking cursor
                if self.blink % 30 < 18:
                    cx2, cy2 = x, y
                    if anchor == "center":
                        cx2 = x + len(partial)*7   # rough advance
                    c.create_text(cx2+2, cy2, text="|",
                                  font=font, fill=UI_AMBER, anchor="w")
            # Lines below current: not shown yet

# ═══════════════════════════════════════════════════════════
#  PSYCHOLOGICAL TRACKER
#  Measures: Stress, Anxiety, Depression, Impulsivity,
#            Resilience, Susceptibility
# ═══════════════════════════════════════════════════════════
class PsychTracker:
    """
    Based on:
    - Lazarus & Folkman (1984) - Stress & Coping
    - Eysenck ACT (2007) - Attentional Control Theory
    - Beck (1979) - Cognitive model of depression
    - Barratt BIS-11 (1995) - Impulsivity
    - Connor-Davidson (2003) - Resilience
    - Kahneman & Tversky (1979) - Prospect theory
    """
    def __init__(self):
        self.session_start = time.time()

        # ── Raw data streams ──────────────────────────────
        # Each click: (timestamp, context, x, y, valid, latency_ms)
        self.clicks = []
        # Response latencies per task-type
        self.latencies = {"chase": [], "evidence": [], "nerve": [],
                          "verdict": [], "shadow": []}
        # Accuracy per task
        self.accuracy  = {"chase": [], "evidence": [], "nerve": [],
                          "verdict": [], "shadow": []}
        # False positives (click on wrong target / wrong time)
        self.false_positives = 0
        self.total_responses = 0
        # Retry data
        self.retry_times = []   # seconds after failure to retry
        self._failure_time = None
        # Reward response delta (performance change after reward)
        self.reward_responses = []   # (score_before, score_after) pairs
        # Moral choices made (0=cautious, 1=aggressive, 2=empathetic)
        self.moral_choices = []
        # Mouse micro-movements during "nerve" task
        self.nerve_deviations = []  # pixel distances from ideal
        # Choice reversal (changed mind)
        self.choice_reversals = 0
        # Task order played
        self.tasks_played = []
        # Performance per session
        self.perf_series = []   # (time, score) for trend
        # Pre-cue clicks (impulsivity)
        self.pre_cue_clicks = 0
        # Completion data
        self.tasks_completed = 0

    def log_click(self, context, x, y, valid, latency_ms):
        self.clicks.append((time.time(), context, x, y, valid, latency_ms))
        self.total_responses += 1
        if not valid: self.false_positives += 1
        if context in self.latencies:
            self.latencies[context].append(latency_ms)

    def log_accuracy(self, context, score_0_to_1):
        if context in self.accuracy:
            self.accuracy[context].append(score_0_to_1)

    def log_failure(self):
        self._failure_time = time.time()

    def log_retry(self):
        if self._failure_time:
            self.retry_times.append(time.time() - self._failure_time)
            self._failure_time = None

    def log_reward_response(self, before, after):
        self.reward_responses.append((before, after))

    def log_moral_choice(self, choice_type):
        """choice_type: 'aggressive', 'cautious', 'empathetic'"""
        self.moral_choices.append(choice_type)

    def log_nerve_deviation(self, px):
        self.nerve_deviations.append(px)

    def log_pre_cue(self):
        self.pre_cue_clicks += 1

    def log_task(self, name):
        self.tasks_played.append(name)
        self.tasks_completed += 1

    def _mean_safe(self, lst, default=50.):
        return sum(lst)/len(lst) if lst else default

    def _variance_safe(self, lst):
        if len(lst) < 2: return 0.
        m = sum(lst)/len(lst)
        return sum((x-m)**2 for x in lst)/len(lst)

    def compute(self):
        """Returns full psychological profile dict."""
        results = {}

        # ── 1. STRESS INDEX ────────────────────────────────────────────────
        # High RT variance + error clustering = stress (Lazarus & Folkman 1984)
        all_lats = []
        for v in self.latencies.values(): all_lats.extend(v)
        if all_lats:
            rt_var = self._variance_safe(all_lats)
            # Normalise variance: 0 = no variance (calm), 100 = high variance (stressed)
            stress_rt = min(100, int(rt_var / 800))
        else:
            stress_rt = 50
        # Error clustering: consecutive false positives boost stress score
        fp_rate = (self.false_positives / max(1, self.total_responses)) * 100
        stress_fp = min(40, int(fp_rate * 1.5))
        results["stress"] = min(100, stress_rt + stress_fp)

        # ── 2. ANXIETY SCORE ───────────────────────────────────────────────
        # Pre-cue clicks (hypervigilance), false positive rate (over-detection)
        # Eysenck ACT (2007): anxiety → impaired inhibition, threat bias
        pre_cue_rate = min(40, self.pre_cue_clicks * 8)
        fp_anxiety   = min(35, int(fp_rate * 1.2))
        # Latency comparison: anxious people are slower on social tasks, faster on threat tasks
        verdict_lat  = self._mean_safe(self.latencies["verdict"], 2500)
        chase_lat    = self._mean_safe(self.latencies["chase"], 300)
        # Threat bias: faster on chase (threat) vs verdict (social)
        threat_bias  = max(0, min(25, int((verdict_lat - chase_lat) / 120)))
        results["anxiety"] = min(100, pre_cue_rate + fp_anxiety + threat_bias)

        # ── 3. DEPRESSION MARKERS ─────────────────────────────────────────
        # Slow retry (Beck 1979), flat reward response (anhedonia proxy)
        if self.retry_times:
            avg_retry = self._mean_safe(self.retry_times)
            # Slow retry (> 8 sec) signals low motivation
            dep_retry = min(40, int(max(0, avg_retry - 2) * 5))
        else:
            dep_retry = 25  # unknown — moderate
        # Flat reward response: reward_responses list of (before, after) score deltas
        if self.reward_responses:
            deltas = [a-b for b,a in self.reward_responses]
            avg_delta = self._mean_safe(deltas, 0)
            # Small positive delta = flat reward response = anhedonia marker
            dep_anhedonia = max(0, min(30, int(30 - avg_delta/3)))
        else:
            dep_anhedonia = 15
        # Task completion: completing fewer tasks = avoidance
        dep_avoid = max(0, (5 - self.tasks_completed) * 5)
        results["depression"] = min(100, dep_retry + dep_anhedonia + dep_avoid)

        # ── 4. IMPULSIVITY ─────────────────────────────────────────────────
        # Pre-cue ratio, fast decisions in verdict (Barratt BIS-11 1995)
        pre_imp = min(40, self.pre_cue_clicks * 10)
        verdict_fast = sum(1 for l in self.latencies["verdict"] if l < 800)
        verdict_imp  = min(30, verdict_fast * 10)
        # Short average latency across all tasks
        if all_lats:
            avg_lat = self._mean_safe(all_lats)
            lat_imp = max(0, min(30, int((1000 - avg_lat) / 30)))
        else: lat_imp = 0
        results["impulsivity"] = min(100, pre_imp + verdict_imp + lat_imp // 3)

        # ── 5. RESILIENCE ─────────────────────────────────────────────────
        # Fast retry, improving performance curve (Connor-Davidson 2003)
        if self.retry_times:
            fast_retries = sum(1 for r in self.retry_times if r < 3.)
            res_retry = min(40, fast_retries * 15)
        else:
            res_retry = 20
        # Performance trend: later performance vs earlier
        if len(self.perf_series) >= 4:
            early_avg = self._mean_safe([s for _,s in self.perf_series[:len(self.perf_series)//2]])
            late_avg  = self._mean_safe([s for _,s in self.perf_series[len(self.perf_series)//2:]])
            trend = (late_avg - early_avg) / max(1, early_avg)
            res_trend = max(0, min(40, int(20 + trend*30)))
        else:
            res_trend = 20
        results["resilience"] = min(100, res_retry + res_trend)

        # ── 6. SUSCEPTIBILITY PROFILE ─────────────────────────────────────
        # Kahneman & Tversky (1979): loss aversion, status seeking
        # High anxiety + impulsivity → FOMO susceptibility
        # High depression → belonging/community susceptibility
        # High stress + resilience → achievement/status susceptibility
        fomo_score     = min(100, results["anxiety"]//2 + results["impulsivity"]//2)
        belonging_score= min(100, results["depression"]//2 + (100-results["resilience"])//2)
        status_score   = min(100, results["stress"]//2 + results["resilience"]//2)
        results["susceptibility"] = {
            "fomo":      fomo_score,
            "belonging": belonging_score,
            "status":    status_score,
            "primary":   max(
                ("FOMO / Loss Aversion", fomo_score),
                ("Belonging / Connection", belonging_score),
                ("Status / Achievement", status_score),
                key=lambda x: x[1]
            )[0]
        }

        # ── MORAL PROFILE ─────────────────────────────────────────────────
        if self.moral_choices:
            from collections import Counter
            mc = Counter(self.moral_choices)
            dominant = max(mc, key=mc.get)
        else:
            dominant = "unknown"
        results["moral_profile"] = dominant

        # ── SIGNATURE ─────────────────────────────────────────────────────
        s = results["stress"]; ax = results["anxiety"]
        d = results["depression"]; im = results["impulsivity"]
        res= results["resilience"]

        if ax >= 65 and im < 40:
            sig = "THE VIGILANT"
            sig_d = ("Hyperaware. You notice what others miss.\n"
                     "Your nervous system runs hot — always scanning for threats.")
        elif im >= 65 and res >= 60:
            sig = "THE LIVEWIRE"
            sig_d = ("Fast. Reactive. You decide before you think.\n"
                     "Your instincts are sharp — but sometimes too sharp.")
        elif d >= 55 and ax < 45:
            sig = "THE HOLLOW"
            sig_d = ("You move through the world with a quiet distance.\n"
                     "Rewards feel flat. Failures feel expected.")
        elif res >= 70 and s < 45:
            sig = "THE OPERATOR"
            sig_d = ("Composed under fire. You fail and get up before\n"
                     "the smoke clears. The city hasn't broken you. Yet.")
        elif s >= 65 and d >= 50:
            sig = "THE BURNING MAN"
            sig_d = ("High pressure inside, low fuel. You're running on\n"
                     "adrenaline and the memory of better days.")
        elif ax >= 55 and im >= 55:
            sig = "THE EDGE WALKER"
            sig_d = ("Paranoid and impulsive in equal measure.\n"
                     "You live on the line between survival and sabotage.")
        else:
            sig = "THE DETECTIVE"
            sig_d = ("Measured. Methodical. You read the scene, not the noise.\n"
                     "The city hasn't gotten to you. Or maybe you're just good at hiding it.")

        # ── HEALTH FLAG ───────────────────────────────────────────────────
        concern = sum([
            s >= 70,
            ax >= 65,
            d >= 60,
            im >= 70,
        ])
        flag = "CRITICAL" if concern >= 3 else "ELEVATED" if concern >= 2 else "NOTABLE" if concern >= 1 else "STABLE"
        results["signature"] = sig
        results["signature_desc"] = sig_d
        results["flag"] = flag
        return results

# ═══════════════════════════════════════════════════════════
#  SCENE TRANSITION
# ═══════════════════════════════════════════════════════════
class Transition:
    def __init__(self):
        self.alpha=0.; self.phase="none"; self.cb=None; self.spd=0.08
    def start(self, cb, spd=0.08):
        self.alpha=0.; self.phase="out"; self.cb=cb; self.spd=spd
    def step(self):
        if self.phase=="none": return
        if self.phase=="out":
            self.alpha=min(1.,self.alpha+self.spd)
            if self.alpha>=1.:
                if self.cb: self.cb()
                self.phase="in"
        else:
            self.alpha=max(0.,self.alpha-self.spd)
            if self.alpha<=0.: self.phase="none"
    def draw(self, c):
        if self.phase=="none" or self.alpha<=0: return
        v=int(self.alpha*255)
        c.create_rectangle(0,0,W,H,fill=f"#{v:02x}{v:02x}{v:02x}",outline="")
    @property
    def active(self): return self.phase!="none"

# ═══════════════════════════════════════════════════════════
#  SCORE POPUP
# ═══════════════════════════════════════════════════════════
class ScorePopup:
    def __init__(self, x, y, text, col, size=15):
        self.x=float(x);self.y=float(y);self.text=text;self.col=col;self.size=size
        self.life=65;self.ml=65;self.vy=-1.8
    def step(self): self.y+=self.vy;self.vy*=0.96;self.life-=1;return self.life>0
    def draw(self, c):
        t=ease_out(self.life/self.ml,2)
        shadow_text(c,int(self.x),int(self.y),self.text,
                    F(self.size,bold=True),lc(SKY_TOP,self.col,t))

# ═══════════════════════════════════════════════════════════
#  SCENE BASE
# ═══════════════════════════════════════════════════════════
class Scene:
    def __init__(self, game):
        self.game=game; self.c=game.canvas; self.tr=game.tracker
        self.ps=PS(500); self.popups=[]; self.frame=0
        self.fx=game.fx; self.rain=game.rain; self.city=game.city
    def add_popup(self,x,y,txt,col,sz=15): self.popups.append(ScorePopup(x,y,txt,col,sz))
    def step_popups(self): self.popups=[p for p in self.popups if p.step()]
    def draw_popups(self): [p.draw(self.c) for p in self.popups]
    def update(self): self.frame+=1; self.ps.step(); self.step_popups(); self.fx.step(); self.rain.step()
    def draw(self): pass
    def click(self,x,y): pass
    def motion(self,x,y): pass
    def key(self,k): pass
    def cleanup(self): self.ps.clear(); self.popups.clear()

# ═══════════════════════════════════════════════════════════
#  SCENE: TITLE  — rain on the city, glitch title
# ═══════════════════════════════════════════════════════════
class TitleScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.timer = 0; self.glitch_t = 0; self.done = False
        self.click_to_skip = False
        self.tagline_alpha = 0.

    def update(self):
        super().update()
        self.timer += 1
        self.tagline_alpha = min(1., max(0., (self.timer-80)/60.))
        self.glitch_t += random.uniform(0, 0.3)
        if self.timer > 260 and not self.done:
            self.click_to_skip = True

    def draw(self):
        c=self.c; c.delete("all"); f=self.frame
        # City scene behind rain
        self.city.draw(c, cam_x=f*0.3)
        self.rain.draw(c)

        # Dark overlay — it's night
        c.create_rectangle(0, PLAY_T, W, PLAY_B,
                           fill=lc(SKY_TOP,"#0a0814",0.5), outline="", stipple="gray50")

        # PHANTOM CITY — glitch title
        t = min(1., (f-20)/40.)
        if t > 0:
            title = "PHANTOM CITY"
            # Glitch offsets
            gx = random.randint(-3,3) if random.random()<0.12 else 0
            gy = random.randint(-2,2) if random.random()<0.12 else 0
            # Red channel
            c.create_text(W//2-3+gx, H//2-80+gy, text=title,
                          font=("Courier", 58, "bold"), fill="#330011", anchor="center")
            # Blue channel
            c.create_text(W//2+3-gx, H//2-80-gy, text=title,
                          font=("Courier", 58, "bold"), fill="#001133", anchor="center")
            # Main
            tg(c, W//2, H//2-80, title, ("Courier",58,"bold"),
               lc(SKY_TOP, FWHITE, t), lc(SKY_TOP, NEON_CYAN, t*0.8), off=6)

        # Subtitle
        if f > 50:
            t2 = min(1., (f-50)/30.)
            shadow_text(c, W//2, H//2-20,
                        "N I G H T   P R O T O C O L",
                        F(14), lc(SKY_TOP, UI_DIM, t2))

        # Tagline
        if self.tagline_alpha > 0:
            shadow_text(c, W//2, H//2+20,
                        '"The city watches. Every choice. Every hesitation. Every nerve."',
                        F(11, italic=True), lc(SKY_TOP, UI_HINT, self.tagline_alpha))

        # Press to continue
        if self.click_to_skip:
            blink = 0.4 + 0.6*math.sin(f*0.08)
            shadow_text(c, W//2, H//2+70, "CLICK  TO  BEGIN",
                        F(14, bold=True), lc(SKY_TOP, UI_AMBER, blink))

        self.fx.draw_vignette(c)
        self.fx.draw_grain(c)
        self.fx.draw_letterbox(c)

        # Time stamp
        shadow_text(c, W-18, LB_H+14, "3:17 AM", FC(11), UI_DIM, anchor="e")

    def click(self, x, y):
        if self.timer > 60:
            self.game.go("prologue")

# ═══════════════════════════════════════════════════════════
#  SCENE: PROLOGUE  — typewriter narrative + city walk
# ═══════════════════════════════════════════════════════════
class PrologueScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.detective = DetectiveSprite(120, SIDEWLK_Y-2)
        self.npcs = [
            NPCSprite(W//2+200, SIDEWLK_Y-2, COAT_C, -1.1),
            NPCSprite(W-100,    SIDEWLK_Y-2, dc(COAT_C,1.3), -0.7),
        ]
        self.tw = TypewriterText()
        self.tw.set_text([
            ("Detective Ray Solano. 11 years on the force.",
             UI_AMBER, F(13), W//2, PLAY_T+28, "center"),
            ("You've seen things this city tries to hide.",
             UI_HINT,  F(12,italic=True), W//2, PLAY_T+54, "center"),
            ("Tonight, five calls came in. You're the only one who answered.",
             FWHITE,   F(13, bold=True), W//2, PLAY_T+82, "center"),
        ], speed=2)
        self.cam_x = 0.
        self.cam_target = 0.
        self.walk_started = False
        self.phase = "text"    # text → walk → done
        self.walk_done_t = 0

    def update(self):
        super().update()
        self.tw.step()
        if self.phase == "text" and self.tw.done:
            self.phase = "walk"
            self.detective.target_x = W//2 - 80
        if self.phase == "walk":
            self.detective.step()
            for npc in self.npcs: npc.step()
            self.cam_target = max(0., self.detective.x - W//3)
            self.cam_x = lrp(self.cam_x, self.cam_target, 0.06)
            if not self.detective.walking and self.detective.target_x is None:
                self.walk_done_t += 1
                if self.walk_done_t > 80:
                    self.game.go("hub")

    def draw(self):
        c=self.c; c.delete("all")
        self.city.draw(c, self.cam_x)
        self.rain.draw(c)
        # NPCs
        for npc in self.npcs: npc.draw(c, self.cam_x*0.85)
        # Detective
        self.detective.draw(c, self.cam_x)
        self.ps.draw(c)

        # Narrative box
        if self.phase == "text":
            rr(c, 20, PLAY_T+12, W-20, PLAY_T+100, r=6,
               fill=lc(SKY_TOP, "#050a18", 0.92), outline=UI_DIM, w=1)
            self.tw.draw(c)
            if self.tw.done:
                shadow_text(c, W//2, PLAY_T+110, "Click to continue →",
                            F(10), UI_DIM)

        self.draw_popups()
        self.fx.draw_vignette(c)
        self.fx.draw_grain(c)
        self.fx.draw_letterbox(c)
        shadow_text(c, W-18, LB_H+14, "3:17 AM", FC(11), UI_DIM, anchor="e")

    def click(self, x, y):
        if self.phase == "text":
            if not self.tw.done: self.tw.skip()
            else: self.phase = "walk"; self.detective.target_x = W//2 - 80

# ═══════════════════════════════════════════════════════════
#  SCENE: HUB  — city alive, cases arrive
# ═══════════════════════════════════════════════════════════
class HubScene(Scene):
    CASES = ["chase", "evidence", "nerve", "verdict", "shadow"]

    def __init__(self, game):
        super().__init__(game)
        self.detective = DetectiveSprite(W//2 - 80, SIDEWLK_Y-2)
        self.npcs = [
            NPCSprite(120,   SIDEWLK_Y-2, dc(COAT_C,1.2), -0.9),
            NPCSprite(W-200, SIDEWLK_Y-2, "#1a2030",       -1.4),
            NPCSprite(W//2+300, SIDEWLK_Y-2, dc(COAT_C,1.5), 0.7),
        ]
        self.cam_x = 0.; self.cam_target = 0.
        self.cases_remaining = list(self.CASES)
        random.shuffle(self.cases_remaining)
        self.cases_done = []
        self.active_case = None
        self.notification = None   # {'text': str, 'timer': int, 'col': str, 'case_key': str}
        self.notif_t = 0
        self.notif_timer_max = 360
        self.notif_display_t = 0
        self.idle_t = 0
        self.car_x = -300.
        self.car_col = random.choice([NEON_RED, NEON_BLUE, "#ffee88"])
        self.car_horn_t = 0
        self.phase = "idle"

        # Case display names
        self.case_names = {
            "chase":    "CASE #1  —  THE PURSUIT",
            "evidence": "CASE #2  —  THE SCENE",
            "nerve":    "CASE #3  —  THE NERVE",
            "verdict":  "CASE #4  —  THE VERDICT",
            "shadow":   "CASE #5  —  THE SHADOW",
        }
        self.case_descs = {
            "chase":    "Vehicle in pursuit. Officer needs assistance. \nRespond immediately.",
            "evidence": "Crime scene secured. Evidence collection required.\nYou have 60 seconds.",
            "nerve":    "Hostage situation. One chance to de-escalate.\nDo not flinch.",
            "verdict":  "Suspect in holding. Two minutes before they walk.\nYou decide.",
            "shadow":   "Rooftop. Dark. One shot. One target.\nDon't miss. Don't rush.",
        }
        # Trigger first case after a brief city walk
        self.first_trigger_t = 120

    def _trigger_next_case(self):
        if not self.cases_remaining:
            # All cases done — go to profile
            self.game.go("profile")
            return
        key = self.cases_remaining.pop(0)
        self.active_case = key
        self.notification = {
            "text": self.case_names[key],
            "desc": self.case_descs[key],
            "timer": self.notif_timer_max,
            "col": UI_RED,
            "case_key": key,
        }
        self.notif_display_t = self.notif_timer_max

    def update(self):
        super().update()
        self.detective.step()
        for npc in self.npcs: npc.step()

        # Camera
        self.cam_target = max(0., self.detective.x - W//3)
        self.cam_x = lrp(self.cam_x, self.cam_target, 0.05)

        # Ambient detective wander
        if self.detective.target_x is None and not self.detective.walking:
            self.idle_t += 1
            if self.idle_t > 90:
                self.idle_t = 0
                self.detective.target_x = random.uniform(W*0.2, W*0.7)

        # Car passes
        self.car_x += 5.5
        if self.car_x > W + 400: self.car_x = -300.; self.car_col = random.choice([NEON_RED, NEON_BLUE, "#ffee88"])

        # Trigger first case
        if self.first_trigger_t > 0:
            self.first_trigger_t -= 1
            if self.first_trigger_t <= 0:
                self._trigger_next_case()

        # Notification countdown
        if self.notification:
            self.notification["timer"] -= 1
            if self.notification["timer"] <= 0:
                # Auto-launch case
                self._launch_case(self.active_case)

        # Police lights ambient particles
        if self.frame % 45 == 0:
            cx = random.randint(100, W-100)
            col = random.choice([NEON_RED, NEON_BLUE])
            self.ps.emit(cx, STREET_Y - 20, col,
                         vx=random.uniform(-2,2), vy=random.uniform(-2,0),
                         life=25, sz=4, kind="spark")

    def _launch_case(self, key):
        self.notification = None
        self.cases_done.append(key)
        scene_map = {"chase": ChaseScene, "evidence": EvidenceScene,
                     "nerve": NerveScene, "verdict": VerdictScene, "shadow": ShadowScene}
        SceneCls = scene_map.get(key, ChaseScene)
        self.game.go_scene(SceneCls)

    def draw(self):
        c=self.c; c.delete("all"); f=self.frame

        # City
        self.city.draw(c, self.cam_x)
        # Car with headlights
        cx = int(self.car_x - self.cam_x * 0.7)
        car_y = STREET_Y + 15
        c.create_rectangle(cx-45, car_y-18, cx+45, car_y+8, fill="#0e1020", outline="")
        c.create_rectangle(cx-38, car_y-28, cx+38, car_y-18, fill="#090e18", outline="")
        # Headlights
        glow(c, cx+42, car_y-8, 14, NEON_WHITE, rings=4, fall=0.35, bg=STREET_C)
        glow(c, cx-42, car_y-8, 14, NEON_WHITE, rings=4, fall=0.35, bg=STREET_C)
        # Tail lights
        c.create_rectangle(cx+38, car_y-16, cx+45, car_y-8, fill=NEON_RED, outline="")
        c.create_rectangle(cx-45, car_y-16, cx-38, car_y-8, fill=NEON_RED, outline="")

        self.rain.draw(c)
        # NPCs
        for npc in self.npcs: npc.draw(c, self.cam_x*0.85)
        # Detective
        self.detective.draw(c, self.cam_x)
        self.ps.draw(c)
        self.draw_popups()

        # Status bar
        done_count = len(self.cases_done)
        total = 5
        rr(c, 8, PLAY_T+8, 260, PLAY_T+42, r=6,
           fill=lc(SKY_TOP,"#060a18",0.95), outline=UI_DIM, w=1)
        shadow_text(c, 18, PLAY_T+25,
                    f"CASES: {done_count}/{total}",
                    F(12,bold=True), UI_AMBER, anchor="w")
        # Progress dots
        for i in range(total):
            dot_x = 120 + i*25; dot_y = PLAY_T+25
            col2 = UI_GREEN if i < done_count else UI_DIM
            c.create_oval(dot_x-5,dot_y-5,dot_x+5,dot_y+5,fill=col2,outline="")

        # NOTIFICATION CARD — incoming case
        if self.notification:
            notif = self.notification
            t_ratio = notif["timer"] / self.notif_timer_max
            slide_in = ease_out(min(1., 1-(notif["timer"]-self.notif_timer_max+60)/60.))
            ny = int(lrp(PLAY_B+100, PLAY_B-130, slide_in))
            # Urgency flash
            flash_alpha = 0.08 + 0.06*math.sin(f*0.25)
            rr(c, W//2-240, ny, W//2+240, ny+110, r=10,
               fill=lc(SKY_TOP,"#08021a",0.97), outline=notif["col"], w=2)
            # Red flash border
            rr(c, W//2-240, ny, W//2+240, ny+110, r=10,
               fill="", outline=lc(SKY_TOP,notif["col"],flash_alpha), w=4)
            # Case name
            shadow_text(c, W//2, ny+22, notif["text"],
                        F(14,bold=True), WHITE)
            # Description
            for li, line in enumerate(notif["desc"].split("\n")):
                shadow_text(c, W//2, ny+44+li*18, line, F(11), UI_HINT)
            # Timer bar
            bar_w = int(480 * t_ratio)
            c.create_rectangle(W//2-240, ny+98, W//2+240, ny+108,
                               fill=lc(SKY_TOP,UI_DIM,0.5), outline="")
            c.create_rectangle(W//2-240, ny+98, W//2-240+bar_w, ny+108,
                               fill=lc(UI_DIM,UI_RED,1-t_ratio), outline="")
            # Respond button
            btn_col = UI_RED if (f%30)<18 else lc(UI_DIM,UI_RED,0.7)
            shadow_text(c, W//2, ny+82, "[ CLICK TO RESPOND ]",
                        F(11,bold=True), btn_col)

        # Ambient time/rain text
        shadow_text(c, W-18, LB_H+14, "3:17 AM", FC(11), UI_DIM, anchor="e")
        shadow_text(c, 18, LB_H+14, "PHANTOM CITY P.D.", FC(10), UI_DIM, anchor="w")

        self.fx.draw_vignette(c)
        self.fx.draw_grain(c)
        self.fx.draw_letterbox(c)

    def click(self, x, y):
        if self.notification:
            self._launch_case(self.active_case)

# ═══════════════════════════════════════════════════════════
#  CASE BASE — shared by all 5 cases
# ═══════════════════════════════════════════════════════════
class CaseScene(Scene):
    def __init__(self, game, case_key, col):
        super().__init__(game)
        self.case_key = case_key
        self.col = col
        self.phase = "intro"
        self.intro_t = 72
        self.score = 0
        self.done = False
        self.done_t = 0
        self.result_text = ""
        self.btn_hover = False
        self.start_t = time.time()
        self.score_before = 0

    def draw_hud(self, right_text=""):
        c=self.c; f=self.frame
        c.create_rectangle(0, 0, W, LB_H, fill="#000000", outline="")
        c.create_rectangle(0, PLAY_B, W, H, fill="#000000", outline="")
        # Case label in letterbox
        tg(c, W//2, LB_H//2, self.case_key.upper()+" PROTOCOL",
           F(13,bold=True), FWHITE, self.col, off=2)
        if right_text:
            shadow_text(c, W-16, LB_H//2, right_text,
                        F(11,bold=True), self.col, anchor="e")
        # Score
        shadow_text(c, 18, LB_H//2, f"SCORE: {self.score:,}",
                    FC(11,bold=True), UI_AMBER, anchor="w")

    def draw_result(self):
        c=self.c; f=self.frame
        t=ease_out(min(1.,(self.done_t-10)/50.))
        rr(c, W//2-200, H//2-70, W//2+200, H//2+70, r=12,
           fill=lc(SKY_TOP,"#06091a",0.97), outline=self.col, w=2)
        shadow_text(c, W//2, H//2-40, "CASE CLOSED",
                    F(18,bold=True), lc(SKY_TOP,FWHITE,t))
        shadow_text(c, W//2, H//2, self.result_text,
                    F(12), lc(SKY_TOP,UI_HINT,t))
        shadow_text(c, W//2, H//2+40, f"SCORE: {self.score:,}",
                    F(14,bold=True), lc(SKY_TOP,UI_AMBER,t))
        blink = 0.4+0.6*math.sin(f*0.1)
        shadow_text(c, W//2, H//2+68, "Click to continue",
                    F(10), lc(SKY_TOP,UI_DIM,blink))

    def finish(self, result_txt):
        self.done = True
        self.result_text = result_txt
        self.tr.log_task(self.case_key)
        if self.score > self.game.high_scores.get(self.case_key, 0):
            self.game.high_scores[self.case_key] = self.score
        elapsed = time.time() - self.start_t
        self.tr.perf_series.append((elapsed, self.score))
        self.tr.log_reward_response(self.score_before, self.score)

    def click_done(self, x, y):
        if self.done and self.done_t > 40:
            self.game.go("hub")
            return True
        return False

# ═══════════════════════════════════════════════════════════
#  CASE 1: THE PURSUIT  — high-speed scroll dodge
#  Measures: reaction time (stress), impulsivity (early clicks),
#            performance under pressure (anxiety)
# ═══════════════════════════════════════════════════════════
CHASE_LANES = [200, 320, 440, 560]
CHASE_SPEED_BASE = 4.5

class ChaseScene(CaseScene):
    def __init__(self, game):
        super().__init__(game, "chase", NEON_RED)
        self.player_lane = 1
        self.player_x = float(CHASE_LANES[self.player_lane])
        self.player_y = float(PLAY_B - 85)
        self.obstacles = []
        self.obs_t = 0; self.obs_interval = 70
        self.speed = CHASE_SPEED_BASE
        self.alive = True
        self.game_t = 62*35   # 35 seconds
        self.target_lane = 1
        self.lane_lerp = 0.
        self.hits = 0; self.dodges = 0
        self.combo = 0; self.max_combo = 0
        self.last_dodge_t = 0
        self.heat = 0.   # 0-1, builds on hits
        # Background scroll
        self.road_offset = 0.
        self.btn_hover = False
        # Obstacle types: car, barrier, civilian
        self.obs_types = ["car","car","barrier","civilian","car"]

    def _spawn(self):
        lane = random.randint(0, 3)
        kind = random.choice(self.obs_types)
        col_map = {"car": NEON_RED, "barrier": NEON_GOLD, "civilian": NEON_CYAN}
        self.obstacles.append({
            "lane": lane, "x": float(CHASE_LANES[lane]),
            "y": float(PLAY_T + 20),
            "kind": kind, "col": col_map[kind], "scored": False,
            "spawn_t": time.time()
        })

    def _die(self):
        if not self.alive: return
        self.alive = False
        self.heat = min(1., self.heat + 0.35)
        self.fx.trigger_shake(16); self.fx.trigger_flash(NEON_RED, 0.55, 0.07)
        self.ps.burst(self.player_x, self.player_y, NEON_RED, n=22, spd=7.)
        self.tr.log_failure()

    def update(self):
        super().update()
        if self.phase == "intro":
            self.intro_t -= 1
            if self.intro_t <= 0: self.phase = "play"
            return
        if self.done: self.done_t += 1; return

        self.game_t -= 1
        self.road_offset = (self.road_offset + self.speed) % 80
        self.speed = CHASE_SPEED_BASE + (1 - self.game_t/(62*35)) * 5.

        # Player lerp to target lane
        target_px = float(CHASE_LANES[self.target_lane])
        self.player_x = lrp(self.player_x, target_px, 0.18)

        if self.alive:
            # Spawn obstacles
            self.obs_t -= 1
            if self.obs_t <= 0:
                self.obs_interval = max(30, 70 - self.score//200*3)
                self.obs_t = self.obs_interval + random.randint(-15, 15)
                self._spawn()

            # Move obstacles
            for obs in self.obstacles:
                obs["y"] += self.speed + 1.2
                # Score dodge
                if not obs["scored"] and obs["y"] > self.player_y + 40:
                    obs["scored"] = True
                    if obs["lane"] != self.target_lane:
                        pts = 50 + self.combo*20
                        self.score += pts
                        self.dodges += 1
                        self.combo += 1; self.max_combo = max(self.max_combo, self.combo)
                        self.add_popup(self.player_x, self.player_y-30,
                                       f"+{pts}  DODGE!", UI_GREEN, 14)
                        self.tr.log_accuracy("chase", 1.0)
                        lat_ms = int((time.time()-obs["spawn_t"])*1000)
                        self.tr.log_click("chase", int(obs["x"]), int(obs["y"]), True, lat_ms)
                # Collision
                if (abs(obs["lane"]-self.target_lane) == 0 and
                    abs(obs["y"]-self.player_y) < 42 and
                    obs["y"] > self.player_y - 60):
                    self.combo = 0; self.hits += 1
                    self.heat = min(1., self.heat + 0.2)
                    self.fx.trigger_shake(8); self.fx.trigger_flash(NEON_RED,0.25,0.1)
                    self.ps.burst(self.player_x, self.player_y, NEON_RED, n=12)
                    self.add_popup(self.player_x, self.player_y-25, "HIT!", UI_RED, 16)
                    self.obstacles.remove(obs)
                    self.tr.log_accuracy("chase", 0.)
                    break

            self.obstacles = [o for o in self.obstacles if o["y"] < PLAY_B+60]

        # Timer
        if self.game_t <= 0 or (not self.alive and self.frame > 60):
            self.finish(f"Dodges: {self.dodges}   Hits: {self.hits}   Max Combo: {self.max_combo}")

        # Tension tracks heat
        self.fx.tension = self.heat * 0.8

        # Trail
        if self.alive and self.frame % 3 == 0:
            self.ps.emit(self.player_x, self.player_y+10, NEON_CYAN,
                         vx=random.uniform(-1,1), vy=random.uniform(1,3),
                         life=20, sz=3, kind="trail")

    def draw(self):
        c=self.c; c.delete("all"); f=self.frame
        sx = self.fx.shake_x; sy = self.fx.shake_y

        # Road background
        c.create_rectangle(0, PLAY_T, W, PLAY_B, fill="#04060e", outline="")

        # Road lanes — moving dashes
        for lane_x in CHASE_LANES:
            # Lane marker
            c.create_line(lane_x-60, PLAY_T, lane_x-60, PLAY_B, fill=dc(FAR_BLD,2.5), width=1)
            c.create_line(lane_x+60, PLAY_T, lane_x+60, PLAY_B, fill=dc(FAR_BLD,2.5), width=1)
            for dy in range(0, int(PLAY_H)+80, 80):
                y = int((dy - self.road_offset) % (PLAY_H+80)) + PLAY_T
                c.create_rectangle(lane_x-3, y, lane_x+3, y+40,
                                   fill=dc(UI_DIM,0.6), outline="")

        # Intro overlay
        if self.phase == "intro":
            t=1-self.intro_t/72.
            c.create_rectangle(0, PLAY_T, W, PLAY_B, fill=lc(SKY_TOP,"#040610",0.95), outline="")
            tg(c, W//2, H//2-30, "THE PURSUIT", F(28,bold=True),
               lc(SKY_TOP,NEON_RED,t), NEON_RED, off=5)
            shadow_text(c, W//2, H//2+20,
                        "Arrow keys or click lanes to dodge.  Don't get hit.",
                        F(12), lc(SKY_TOP,UI_HINT,t))
            self.draw_hud()
            self.fx.draw_vignette(c)
            self.fx.draw_grain(c)
            self.fx.draw_letterbox(c)
            return

        # Speed lines
        spd_frac = (self.speed-CHASE_SPEED_BASE)/5.
        for _ in range(int(spd_frac*25)):
            lx=random.randint(0,W); ly1=random.randint(PLAY_T,PLAY_B)
            c.create_line(lx+sx,ly1+sy, lx+sx, ly1+sy+random.randint(20,60),
                          fill=lc(SKY_TOP,NEON_CYAN,spd_frac*0.15), width=1)

        # Obstacles
        for obs in self.obstacles:
            ox=int(obs["x"])+sx; oy=int(obs["y"])+sy
            kind=obs["kind"]; col=obs["col"]
            if kind == "car":
                c.create_rectangle(ox-24,oy-36,ox+24,oy+8,fill=lc(SKY_TOP,col,0.3),outline="")
                c.create_rectangle(ox-20,oy-50,ox+20,oy-36,fill=lc(SKY_TOP,dc(col,0.8),0.4),outline="")
                glow(c,ox-22,oy-28,8,col,rings=3,fall=0.4,bg=STREET_C)
                glow(c,ox+22,oy-28,8,col,rings=3,fall=0.4,bg=STREET_C)
                c.create_oval(ox-8,oy+2,ox+8,oy+12,fill=lc(SKY_TOP,col,0.6),outline="")
            elif kind == "barrier":
                c.create_rectangle(ox-40,oy-12,ox+40,oy+12,fill=lc(SKY_TOP,col,0.4),outline=col,width=1)
                for bx2 in range(ox-35,ox+40,15):
                    c.create_line(bx2,oy-12,bx2+10,oy+12,fill=col,width=2)
                glow(c,ox,oy,20,col,rings=3,fall=0.3,bg=SKY_TOP)
            elif kind == "civilian":
                c.create_oval(ox-8,oy-48,ox+8,oy-32,fill=SKIN_C,outline="")
                c.create_rectangle(ox-11,oy-32,ox+11,oy,fill=col,outline="")
                glow(c,ox,oy-20,12,col,rings=4,fall=0.35,bg=SKY_TOP)

        self.ps.draw(c)

        # Player vehicle
        if self.alive:
            px=int(self.player_x)+sx; py=int(self.player_y)+sy
            # Car body
            c.create_rectangle(px-26,py-40,px+26,py+12,fill=lc(SKY_TOP,NEON_CYAN,0.25),outline=NEON_CYAN,width=2)
            c.create_rectangle(px-20,py-60,px+20,py-40,fill=lc(SKY_TOP,NEON_CYAN,0.3),outline="")
            # Headlights
            for hx in [-22,22]:
                glow(c,px+hx,py+8,10,NEON_WHITE,rings=4,fall=0.4,bg=STREET_C)
            # Shield / heat display
            if self.heat > 0:
                heat_col = lc(NEON_GREEN,NEON_RED,self.heat)
                glow_ring(c,px,py-20,32,heat_col,width=2,rings=3)
        else:
            # Death debris
            px=int(self.player_x)+sx; py=int(self.player_y)+sy
            c.create_text(px,py,text="💥",font=F(28))

        self.draw_popups()

        # HUD overlays
        secs_left = self.game_t // 62
        self.draw_hud(f"TIME: {secs_left}s  |  COMBO: {self.combo}")

        # Lane indicator
        for i,lx in enumerate(CHASE_LANES):
            if i == self.target_lane:
                c.create_rectangle(lx-58, PLAY_T+2, lx+58, PLAY_T+6,
                                   fill=NEON_CYAN, outline="")

        if self.done: self.draw_result()

        self.fx.draw_tension_grade(c)
        self.fx.draw_vignette(c)
        self.fx.draw_flash(c)
        self.fx.draw_grain(c)
        self.fx.draw_letterbox(c)

    def click(self, x, y):
        if self.click_done(x, y): return
        if self.phase == "intro": self.phase = "play"; return
        if not self.alive: self.tr.log_retry(); self.phase="intro"; self.intro_t=40; self._reset(); return
        # Click a lane
        for i, lx in enumerate(CHASE_LANES):
            if abs(x-lx) < 80:
                click_t = time.time()
                # Check if pre-cue click (clicking on empty lane with no threat)
                threat_in_lane = any(o["lane"]==i and o["y"]<self.player_y-60 and o["y"]>PLAY_T+20
                                     for o in self.obstacles)
                if not threat_in_lane:
                    self.tr.log_pre_cue()
                self.target_lane = i
                break

    def _reset(self):
        self.player_lane=1; self.target_lane=1; self.player_x=float(CHASE_LANES[1])
        self.obstacles=[]; self.obs_t=0; self.speed=CHASE_SPEED_BASE
        self.alive=True; self.combo=0; self.hits=0; self.dodges=0; self.done=False

    def key(self, k):
        if self.phase != "play": return
        if k in ("Left","a","A"):  self.target_lane = max(0, self.target_lane-1)
        if k in ("Right","d","D"): self.target_lane = min(3, self.target_lane+1)

# ═══════════════════════════════════════════════════════════
#  CASE 2: THE SCENE  — evidence hunt under pressure
#  Measures: attention, false positives (anxiety), focus decay
# ═══════════════════════════════════════════════════════════
class EvidenceScene(CaseScene):
    def __init__(self, game):
        super().__init__(game, "evidence", NEON_BLUE)
        self.phase = "intro"; self.intro_t = 72
        self.room_objs = []   # background clutter
        self.evidence = []    # {'x','y','found','col','type','born'}
        self.decoys = []      # false positives: clickable but wrong
        self.game_t = 62*55
        self.found = 0; self.total = 7; self.false_pos = 0
        self.flashlight_x = W//2; self.flashlight_y = H//2
        self.visibility_r = 95.   # flashlight radius
        self._gen_room()

    def _gen_room(self):
        evidence_types = [
            ("SHELL CASING",  NEON_GOLD),
            ("BLOOD STAIN",   NEON_RED),
            ("FOOTPRINT",     NEON_BLUE),
            ("HAIR SAMPLE",   NEON_PURP),
            ("PHONE",         NEON_CYAN),
            ("KNIFE",         NEON_WHITE),
            ("WALLET",        NEON_GREEN),
        ]
        placed = []
        for ev_type, ev_col in evidence_types:
            attempts = 0
            while attempts < 50:
                ex = random.randint(80, W-80)
                ey = random.randint(PLAY_T+60, PLAY_B-60)
                if all(math.hypot(ex-p[0],ey-p[1])>55 for p in placed):
                    placed.append((ex,ey))
                    self.evidence.append({
                        "x": ex, "y": ey, "found": False,
                        "col": ev_col, "type": ev_type,
                        "born": None, "pulse": random.uniform(0,100)
                    })
                    break
                attempts += 1
        # Decoys (wrong items)
        decoy_labels = ["TRASH","DUST","CIGARETTE","NOTHING","DEAD PIGEON"]
        for _ in range(5):
            dx = random.randint(80, W-80)
            dy = random.randint(PLAY_T+60, PLAY_B-60)
            self.decoys.append({"x":dx,"y":dy,"label":random.choice(decoy_labels),"col":UI_DIM})
        # Room furniture clutter (just visual)
        for _ in range(12):
            self.room_objs.append({
                "x": random.randint(50, W-50),
                "y": random.randint(PLAY_T+50, PLAY_B-50),
                "w": random.randint(20,80), "h": random.randint(15,50),
                "col": dc(MID_BLD,random.uniform(0.8,1.5))
            })

    def update(self):
        super().update()
        if self.phase == "intro": self.intro_t-=1; (None if self.intro_t>0 else setattr(self,'phase','play')); return
        if self.done: self.done_t+=1; return
        self.game_t -= 1
        # Light radius shrinks as time passes — anxiety pressure
        self.visibility_r = max(55., 95. - (62*55-self.game_t)/62/55*40.)
        # Mark evidence born time
        for ev in self.evidence:
            if ev["born"] is None: ev["born"] = time.time()
        if self.game_t <= 0 or self.found == self.total:
            accuracy = self.found / max(1, self.found+self.false_pos)
            result = f"Found {self.found}/{self.total}   False leads: {self.false_pos}"
            self.tr.log_accuracy("evidence", accuracy)
            self.finish(result)

    def draw(self):
        c=self.c; c.delete("all"); f=self.frame
        # Dark room
        c.create_rectangle(0, PLAY_T, W, PLAY_B, fill="#030508", outline="")

        if self.phase == "intro":
            t=1-self.intro_t/72.
            tg(c,W//2,H//2-30,"THE SCENE",F(28,bold=True),lc(SKY_TOP,NEON_BLUE,t),NEON_BLUE,off=5)
            shadow_text(c,W//2,H//2+20,"Move mouse to sweep flashlight. Click evidence. Don't touch decoys.",F(12),lc(SKY_TOP,UI_HINT,t))
            self.draw_hud(); self.fx.draw_grain(c); self.fx.draw_letterbox(c); return

        # Flashlight cone — draw visible area
        fx2 = self.flashlight_x; fy2 = self.flashlight_y
        r = self.visibility_r

        # Dark overlay (whole room dark)
        c.create_rectangle(0, PLAY_T, W, PLAY_B, fill="#020407", outline="")
        # Flashlight: concentric ovals from bright center to dark edge
        steps = 16
        for i in range(steps, 0, -1):
            t = i/steps; cr = r*t
            alpha = (1-t)*0.82
            col = lc("#020407", "#1a2030", alpha)
            c.create_oval(fx2-cr, fy2-cr*0.75, fx2+cr, fy2+cr*0.75, fill=col, outline="")
        # Very small bright spot at center
        c.create_oval(fx2-12, fy2-9, fx2+12, fy2+9, fill="#1e2a40", outline="")

        # Room furniture (visible only near flashlight)
        for obj in self.room_objs:
            dist = math.hypot(obj["x"]-fx2, obj["y"]-fy2)
            if dist < r+40:
                alpha = max(0., 1-(dist-r/2)/(r*0.7))
                col = lc("#020407", obj["col"], alpha*0.6)
                c.create_rectangle(obj["x"]-obj["w"]//2, obj["y"]-obj["h"]//2,
                                   obj["x"]+obj["w"]//2, obj["y"]+obj["h"]//2,
                                   fill=col, outline=lc("#020407",UI_DIM,alpha*0.2))

        # Evidence items
        for ev in self.evidence:
            if ev["found"]: continue
            dist = math.hypot(ev["x"]-fx2, ev["y"]-fy2)
            if dist < r+25:
                alpha = max(0., 1-(dist-(r*0.4))/(r*0.8))
                if alpha <= 0.05: continue
                pulse = 0.6+0.4*math.sin(time.time()*4+ev["pulse"])
                col = lc(SKY_TOP, ev["col"], alpha*pulse)
                # Subtle marker — not obvious
                c.create_oval(ev["x"]-10, ev["y"]-10, ev["x"]+10, ev["y"]+10,
                              fill=lc(SKY_TOP, ev["col"], alpha*0.15), outline=col, width=1)
                # Evidence hint glow
                if dist < r*0.6:
                    glow(c, ev["x"], ev["y"], 12, ev["col"], rings=3, fall=0.3, bg=SKY_TOP)

        # Decoys
        for dec in self.decoys:
            dist = math.hypot(dec["x"]-fx2, dec["y"]-fy2)
            if dist < r*0.75:
                alpha = max(0., 1-dist/(r*0.7))
                c.create_oval(dec["x"]-8, dec["y"]-8, dec["x"]+8, dec["y"]+8,
                              fill="", outline=lc(SKY_TOP,UI_DIM,alpha*0.4), width=1, dash=(2,3))

        self.ps.draw(c)
        self.draw_popups()

        # Timer pressure — text
        secs_left = self.game_t // 62
        timer_col = lc(UI_GREEN, NEON_RED, 1-secs_left/55.)
        self.draw_hud(f"EVIDENCE: {self.found}/{self.total}  |  TIME: {secs_left}s")
        # Urgency instruction
        if secs_left < 15:
            blink = 0.4+0.6*math.sin(f*0.25)
            shadow_text(c, W//2, PLAY_B-20, "RUNNING OUT OF TIME",
                        F(13,bold=True), lc(SKY_TOP,NEON_RED,blink))

        if self.done: self.draw_result()
        self.fx.draw_vignette(c)
        self.fx.draw_grain(c)
        self.fx.draw_letterbox(c)

    def click(self, x, y):
        if self.click_done(x,y): return
        if self.phase=="intro": self.phase="play"; return
        if self.done: return
        # Check evidence
        hit_ev = False
        for ev in self.evidence:
            if not ev["found"] and math.hypot(x-ev["x"],y-ev["y"]) < 20:
                ev["found"] = True; self.found += 1
                hit_ev = True
                pts = 200 + (self.total-self.found)*30
                self.score += pts
                rt_ms = int((time.time()-ev["born"])*1000) if ev["born"] else 2000
                self.tr.log_click("evidence", x, y, True, rt_ms)
                self.ps.burst(x, y, ev["col"], n=14)
                self.fx.trigger_flash(ev["col"], 0.15, 0.1)
                self.add_popup(x, y-25, f"+{pts}  {ev['type']}", ev["col"], 14)
                break
        # Check decoys (false positive)
        if not hit_ev:
            for dec in self.decoys:
                if math.hypot(x-dec["x"],y-dec["y"]) < 20:
                    self.false_pos += 1
                    self.tr.log_click("evidence", x, y, False, 0)
                    self.tr.false_positives += 1
                    self.score = max(0, self.score-100)
                    self.ps.emit(x, y, NEON_RED, n=8, vx=0, vy=-1.5, life=30, sz=4)
                    self.add_popup(x, y-20, "-100  FALSE LEAD", NEON_RED, 13)
                    self.fx.trigger_flash(NEON_RED, 0.12, 0.15)
                    break

    def motion(self, x, y):
        self.flashlight_x = x; self.flashlight_y = y

# ═══════════════════════════════════════════════════════════
#  CASE 3: THE NERVE  — hold cursor steady in shrinking zone
#  Measures: anxiety (tremor/deviation), arousal state, regulation
# ═══════════════════════════════════════════════════════════
class NerveScene(CaseScene):
    def __init__(self, game):
        super().__init__(game, "nerve", NEON_GOLD)
        self.phase = "intro"; self.intro_t = 72
        self.target_x = float(W//2); self.target_y = float(H//2 + 20)
        self.zone_r = 55.    # shrinks from 55 to 18
        self.zone_target_r = 55.
        self.zone_decay = 0.
        self.cursor_x = float(W//2); self.cursor_y = float(H//2)
        self.in_zone = False
        self.time_in_zone = 0
        self.time_needed = 220   # frames needed inside zone
        self.rounds = 0; self.max_rounds = 4
        self.round_score = 0
        self.heartbeat_t = 0.
        self.tension_build = 0.
        self.last_out_t = 0
        self.game_t = 62*45

    def update(self):
        super().update()
        if self.phase=="intro": self.intro_t-=1; (None if self.intro_t>0 else setattr(self,'phase','play')); return
        if self.done: self.done_t+=1; return
        self.game_t -= 1
        # Zone shrinks over time within each round
        self.zone_decay += 0.018
        self.zone_r = max(18., 55. - self.zone_decay*22.)
        # Heartbeat
        self.heartbeat_t += 0.06 + self.tension_build*0.04
        # Check cursor in zone
        dist = math.hypot(self.cursor_x-self.target_x, self.cursor_y-self.target_y)
        was_in = self.in_zone
        self.in_zone = dist < self.zone_r
        if self.in_zone:
            self.time_in_zone += 1
            self.tension_build = min(1., self.tension_build + 0.01)
            dev = int(dist)
            self.tr.log_nerve_deviation(dev)
            if self.time_in_zone >= self.time_needed:
                # Round complete
                self.rounds += 1
                pts = int((self.zone_r / 55.) * 300 + (self.time_needed/self.time_in_zone)*200)
                self.score += pts; self.round_score = pts
                self.add_popup(int(self.cursor_x), int(self.cursor_y)-40,
                               f"+{pts}  NERVE HELD", NEON_GOLD, 16)
                self.ps.burst(self.target_x, self.target_y, NEON_GOLD, n=20)
                self.fx.trigger_flash(NEON_GOLD, 0.3, 0.06)
                self.tr.log_accuracy("nerve", 1-dist/55.)
                # Next round: move target, reset
                self.target_x = random.uniform(W*0.25, W*0.75)
                self.target_y = random.uniform(PLAY_T+80, PLAY_B-80)
                self.time_in_zone = 0; self.zone_decay = 0; self.zone_r = 55.
                if self.rounds >= self.max_rounds:
                    self.finish(f"Rounds: {self.rounds}/{self.max_rounds}   Avg deviation logged")
        else:
            if was_in: self.last_out_t = self.frame
            self.time_in_zone = max(0, self.time_in_zone-1)
            self.tension_build = max(0., self.tension_build-0.005)
        if self.game_t <= 0:
            self.finish(f"Rounds: {self.rounds}/{self.max_rounds}   Hold time measured")
        self.fx.tension = self.tension_build * 0.6

    def draw(self):
        c=self.c; c.delete("all"); f=self.frame
        grad_bg_nerve(c)
        if self.phase=="intro":
            t=1-self.intro_t/72.
            tg(c,W//2,H//2-30,"THE NERVE",F(28,bold=True),lc(SKY_TOP,NEON_GOLD,t),NEON_GOLD,off=5)
            shadow_text(c,W//2,H//2+20,"Hold your cursor inside the shrinking circle. Do not move.",F(12),lc(SKY_TOP,UI_HINT,t))
            shadow_text(c,W//2,H//2+48,"Breathe. This is a precision test.",F(11,italic=True),lc(SKY_TOP,UI_DIM,t))
            self.draw_hud(); self.fx.draw_grain(c); self.fx.draw_letterbox(c); return

        tx=int(self.target_x); ty=int(self.target_y)
        # Background grid (subtle crosshair world)
        for gx in range(0,W,60):
            c.create_line(gx,PLAY_T,gx,PLAY_B,fill=lc(SKY_TOP,UI_DIM,0.05),width=1)
        for gy in range(PLAY_T,PLAY_B,60):
            c.create_line(0,gy,W,gy,fill=lc(SKY_TOP,UI_DIM,0.05),width=1)

        # Heartbeat line
        hb_y = PLAY_B - 40
        prev_x = 0; prev_y = hb_y
        for hx in range(W):
            ht = self.heartbeat_t - hx/W*4*math.pi
            amp = 6 + self.tension_build*18
            # ECG-ish: spikes every 80px
            spike = 0
            phase_pos = hx % 80
            if 35 < phase_pos < 40: spike = (phase_pos-35)*amp*2
            elif 40 < phase_pos < 45: spike = (45-phase_pos)*amp*2
            y2 = hb_y + math.sin(ht)*2 + spike
            if hx > 0:
                col = lc(SKY_TOP, NEON_GREEN if self.in_zone else NEON_RED,
                         0.4 + self.tension_build*0.4)
                c.create_line(prev_x,int(prev_y),hx,int(y2),fill=col,width=1)
            prev_x=hx; prev_y=y2

        # Outer rings (guide)
        for ri in range(4):
            rr2=55+ri*22
            c.create_oval(tx-rr2,ty-rr2,tx+rr2,ty+rr2,fill="",
                          outline=lc(SKY_TOP,UI_DIM,0.12),width=1)

        # Target zone
        r=self.zone_r
        zone_col = NEON_GREEN if self.in_zone else NEON_GOLD
        glow(c,tx,ty,r,zone_col,rings=6,fall=0.3,bg=SKY_TOP)
        glow_ring(c,tx,ty,r,zone_col,width=3,rings=4)
        # Zone fill
        c.create_oval(tx-r,ty-r,tx+r,ty+r,
                      fill=lc(SKY_TOP,zone_col,0.07 if self.in_zone else 0.03),outline="")

        # Crosshair target center
        for d in [4,8,12]:
            t2=0.4+0.6*(d/12); col=lc(SKY_TOP,zone_col,t2)
            c.create_line(tx-d,ty,tx+d,ty,fill=col,width=1)
            c.create_line(tx,ty-d,tx,ty+d,fill=col,width=1)

        # Progress arc (time in zone)
        if self.time_in_zone > 0:
            progress = self.time_in_zone / self.time_needed
            extent = int(360*progress)
            try:
                c.create_arc(tx-r-10,ty-r-10,tx+r+10,ty+r+10,
                             start=90,extent=extent,outline=NEON_GREEN,width=3,style="arc")
            except: pass

        # Cursor indicator
        cx2=int(self.cursor_x); cy2=int(self.cursor_y)
        dist=math.hypot(cx2-tx,cy2-ty)
        cursor_col = NEON_GREEN if self.in_zone else lc(NEON_GOLD,NEON_RED,min(1.,dist/120.))
        glow(c,cx2,cy2,6,cursor_col,rings=3,fall=0.4,bg=SKY_TOP)
        c.create_oval(cx2-4,cy2-4,cx2+4,cy2+4,fill=cursor_col,outline="")
        c.create_line(cx2-12,cy2,cx2+12,cy2,fill=cursor_col,width=1)
        c.create_line(cx2,cy2-12,cx2,cy2+12,fill=cursor_col,width=1)

        self.ps.draw(c)
        self.draw_popups()

        # Round progress
        for ri in range(self.max_rounds):
            dot_col = NEON_GOLD if ri < self.rounds else UI_DIM
            c.create_oval(W//2-60+ri*40-6,PLAY_T+18,W//2-60+ri*40+6,PLAY_T+30,fill=dot_col,outline="")

        secs_left=self.game_t//62
        self.draw_hud(f"ROUND {min(self.rounds+1,self.max_rounds)}/{self.max_rounds}  |  TIME: {secs_left}s")

        if not self.in_zone:
            status_col=lc(UI_DIM,NEON_RED,min(1.,(f-self.last_out_t)/60.)) if self.last_out_t else UI_DIM
            shadow_text(c,W//2,PLAY_B-18,"HOLD STEADY",F(12,bold=True),status_col)
        else:
            p=0.5+0.5*math.sin(f*0.15)
            shadow_text(c,W//2,PLAY_B-18,"HOLDING . . .",F(12,bold=True),lc(UI_DIM,NEON_GREEN,p))

        if self.done: self.draw_result()
        self.fx.draw_tension_grade(c)
        self.fx.draw_vignette(c)
        self.fx.draw_flash(c)
        self.fx.draw_grain(c)
        self.fx.draw_letterbox(c)

    def motion(self, x, y): self.cursor_x=float(x); self.cursor_y=float(y)
    def click(self, x, y):
        if self.click_done(x,y): return
        if self.phase=="intro": self.phase="play"

def grad_bg_nerve(c):
    steps=30; ph=PLAY_H
    for i in range(steps):
        t=i/steps; y=PLAY_T+int(i*ph/steps)
        c.create_rectangle(0,y,W,y+ph//steps+2,fill=lc("#020309","#040811",t),outline="")

# ═══════════════════════════════════════════════════════════
#  CASE 4: THE VERDICT  — timed interrogation choices
#  Measures: decisional anxiety, empathy, moral profile
# ═══════════════════════════════════════════════════════════
INTERROGATION_CASES = [
    {
        "setup": "A man sits across from you. His hands are shaking.\n\"I didn't do it. I swear. Please.\" His alibi is weak. The evidence is thin.",
        "question": "What do you do?",
        "options": [
            ("Lean in. Tell him you believe him. Ask him to help you prove it.", "empathetic", 280),
            ("Slam the table. Tell him you have everything you need.", "aggressive", 120),
            ("Stay silent. Let the pressure do the work.", "cautious", 200),
        ]
    },
    {
        "setup": "A teenager. 16. Caught with a stolen laptop.\nShe looks terrified. First offence. Mother works two jobs.",
        "question": "What happens next?",
        "options": [
            ("Release her. Warn her. Give her a way out.", "empathetic", 300),
            ("Book her. Rules are rules. No exceptions.", "aggressive", 100),
            ("Hold her for 24 hours. Let her think about it.", "cautious", 180),
        ]
    },
    {
        "setup": "Your partner tells you the suspect confessed — but you know it was coerced.\nThe DA is watching. Your career is on the line.",
        "question": "What do you do?",
        "options": [
            ("Throw out the confession. Start over. Do it right.", "empathetic", 350),
            ("Stay quiet. Let it play out. You need this win.", "aggressive", 80),
            ("Investigate the confession further before deciding.", "cautious", 220),
        ]
    },
]

class VerdictScene(CaseScene):
    def __init__(self, game):
        super().__init__(game, "verdict", NEON_PURP)
        self.phase = "intro"; self.intro_t = 72
        self.cases_q = INTERROGATION_CASES.copy()
        random.shuffle(self.cases_q)
        self.case_idx = 0
        self.current_q = None
        self.choice_t = 0; self.choice_max = 62*6  # 6 seconds to decide
        self.chosen = None
        self.chosen_result_t = 0
        self.q_start_t = None
        self.answers = []
        self._load_next_q()

    def _load_next_q(self):
        if self.case_idx < len(self.cases_q):
            self.current_q = self.cases_q[self.case_idx]
            self.choice_t = self.choice_max
            self.chosen = None
            self.q_start_t = time.time()
        else:
            self.current_q = None

    def update(self):
        super().update()
        if self.phase=="intro": self.intro_t-=1; (None if self.intro_t>0 else setattr(self,'phase','play')); return
        if self.done: self.done_t+=1; return
        if self.chosen is not None:
            self.chosen_result_t += 1
            if self.chosen_result_t > 80:
                self.case_idx += 1
                if self.case_idx >= len(self.cases_q):
                    empathetic_count = sum(1 for a in self.answers if a=="empathetic")
                    aggressive_count = sum(1 for a in self.answers if a=="aggressive")
                    self.finish(f"Empathetic: {empathetic_count}  Aggressive: {aggressive_count}  Profile logged")
                else:
                    self._load_next_q()
            return
        if self.current_q:
            self.choice_t -= 1
            if self.choice_t <= 0:
                # Timed out — log as cautious/avoidant
                self.chosen = "cautious"
                self.answers.append("avoidant")
                self.tr.log_moral_choice("cautious")
                self.score += 50
                self.chosen_result_t = 0

    def draw(self):
        c=self.c; c.delete("all"); f=self.frame
        # Dark interrogation room
        c.create_rectangle(0,PLAY_T,W,PLAY_B,fill="#03040a",outline="")
        # Overhead light cone
        c.create_polygon(W//2-80,PLAY_T+10, W//2+80,PLAY_T+10,
                         W//2+160,PLAY_B-20, W//2-160,PLAY_B-20,
                         fill=lc(SKY_TOP,AMBER,0.04),outline="")

        if self.phase=="intro":
            t=1-self.intro_t/72.
            tg(c,W//2,H//2-30,"THE VERDICT",F(28,bold=True),lc(SKY_TOP,NEON_PURP,t),NEON_PURP,off=5)
            shadow_text(c,W//2,H//2+20,"Three cases. Six seconds each. Your choice reveals your character.",F(12),lc(SKY_TOP,UI_HINT,t))
            self.draw_hud(); self.fx.draw_grain(c); self.fx.draw_letterbox(c); return

        if self.current_q and not self.done:
            q=self.current_q
            # Table silhouette
            c.create_rectangle(W//2-160,H//2+40,W//2+160,H//2+60,fill=dc(MID_BLD,1.2),outline="")
            c.create_rectangle(W//2-120,H//2+60,W//2+120,H//2+110,fill=dc(MID_BLD,1.1),outline="")
            # Suspect silhouette (across the table)
            sx2=W//2; sy2=H//2-40
            # Body
            c.create_rectangle(sx2-25,sy2-30,sx2+25,sy2+20,fill=dc(FAR_BLD,1.8),outline="")
            # Head
            c.create_oval(sx2-15,sy2-60,sx2+15,sy2-32,fill=dc(MID_BLD,2.2),outline="")
            # Light on suspect
            glow(c,sx2,sy2-20,60,AMBER,rings=6,fall=0.15,bg=SKY_TOP)
            # Shaking hands if anxious (suspect animation)
            shake_amt = math.sin(f*0.4)*3
            c.create_oval(sx2-28+shake_amt,sy2+8,sx2-18+shake_amt,sy2+18,fill=SKIN_C,outline="")
            c.create_oval(sx2+18-shake_amt,sy2+8,sx2+28-shake_amt,sy2+18,fill=SKIN_C,outline="")

            # Setup text
            setup_lines = q["setup"].split("\n")
            rr(c,30,PLAY_T+10,W-30,PLAY_T+70,r=6,
               fill=lc(SKY_TOP,"#05060f",0.95),outline=lc(SKY_TOP,UI_DIM,0.5),w=1)
            for li,line in enumerate(setup_lines):
                shadow_text(c,W//2,PLAY_T+28+li*20,line,F(11,italic=True),UI_HINT)

            # Timer bar — urgent
            ratio=self.choice_t/self.choice_max
            timer_col=lc(NEON_GREEN,NEON_RED,1-ratio)
            c.create_rectangle(30,PLAY_T+74,W-30,PLAY_T+82,fill=lc(SKY_TOP,UI_DIM,0.4),outline="")
            c.create_rectangle(30,PLAY_T+74,30+int((W-60)*ratio),PLAY_T+82,fill=timer_col,outline="")

            # Options
            if self.chosen is None:
                for oi,(text,kind,pts) in enumerate(q["options"]):
                    by=H//2+80+oi*52
                    btn_col=[NEON_CYAN,NEON_RED,NEON_GOLD][oi]
                    hover=self.btn_hover==oi
                    if hover: glow(c,W//2,by,W//2-40,btn_col,rings=3,fall=0.1,bg=SKY_TOP)
                    rr(c,40,by-20,W-40,by+20,r=8,
                       fill=lc(SKY_TOP,dc(btn_col,0.18),0.9) if hover else lc(SKY_TOP,"#05060f",0.95),
                       outline=btn_col if hover else lc(SKY_TOP,UI_DIM,0.5),w=2 if hover else 1)
                    shadow_text(c,W//2,by,text,F(12),WHITE if hover else UI_HINT)
            else:
                # Show result
                chosen_kind=self.answers[-1] if self.answers else "unknown"
                result_col={"empathetic":NEON_CYAN,"aggressive":NEON_RED,
                            "cautious":NEON_GOLD,"avoidant":UI_DIM}.get(chosen_kind,UI_HINT)
                t2=ease_out(self.chosen_result_t/80.)
                tg(c,W//2,H//2+90,"DECISION LOGGED",F(16,bold=True),
                   lc(SKY_TOP,FWHITE,t2),result_col,off=3)

        self.draw_popups()
        qn=min(self.case_idx+1,len(self.cases_q))
        self.draw_hud(f"CASE {qn}/{len(self.cases_q)}  |  SCORE: {self.score:,}")
        if self.done: self.draw_result()
        self.fx.draw_vignette(c)
        self.fx.draw_grain(c)
        self.fx.draw_letterbox(c)

    def click(self, x, y):
        if self.click_done(x,y): return
        if self.phase=="intro": self.phase="play"; return
        if self.done or self.chosen is not None or not self.current_q: return
        for oi,(text,kind,pts) in enumerate(self.current_q["options"]):
            by=H//2+80+oi*52
            if abs(y-by)<22 and 40<x<W-40:
                lat_ms=int((time.time()-(self.q_start_t or time.time()))*1000)
                self.chosen=kind; self.chosen_result_t=0
                self.answers.append(kind)
                self.tr.log_moral_choice(kind)
                self.tr.log_click("verdict",x,y,True,lat_ms)
                self.score+=pts
                self.add_popup(W//2,H//2+50,f"+{pts}",
                               [NEON_CYAN,NEON_RED,NEON_GOLD][oi],16)
                self.ps.burst(x,by,[NEON_CYAN,NEON_RED,NEON_GOLD][oi],n=14)
                return

    def motion(self, x, y):
        self.btn_hover=-1
        if not self.current_q or self.chosen is not None: return
        for oi in range(len(self.current_q["options"])):
            by=H//2+80+oi*52
            if abs(y-by)<22 and 40<x<W-40: self.btn_hover=oi; return

# ═══════════════════════════════════════════════════════════
#  CASE 5: THE SHADOW  — target acquisition + inhibition
#  Measures: impulsivity vs caution, threat detection accuracy
# ═══════════════════════════════════════════════════════════
class ShadowScene(CaseScene):
    def __init__(self, game):
        super().__init__(game, "shadow", NEON_WHITE)
        self.phase = "intro"; self.intro_t = 72
        self.targets = []   # {'x','y','kind','r','age','active','col'}
        self.spawn_t = 0; self.spawn_interval = 90
        self.game_t = 62*40
        self.hits = 0; self.wrong_shots = 0
        self.cursor_x = W//2; self.cursor_y = H//2
        self.scope_r = 50.
        self.scope_target_r = 50.
        self.breathing_t = 0.
        self.holding_breath = False
        self.breath_held_t = 0
        self.background_figures = [(random.randint(80,W-80), random.randint(PLAY_T+40,PLAY_B-80))
                                    for _ in range(6)]

    def _spawn_target(self):
        kind = "hostile" if random.random() < 0.55 else "civilian"
        col = NEON_RED if kind=="hostile" else NEON_CYAN
        # Don't overlap background figures closely
        for _ in range(30):
            x = random.randint(100, W-100)
            y = random.randint(PLAY_T+60, PLAY_B-80)
            self.targets.append({"x":x,"y":y,"kind":kind,"col":col,
                                  "r":0.,"age":0,"active":True,
                                  "born":time.time(),"life":random.randint(120,200)})
            break

    def update(self):
        super().update()
        if self.phase=="intro": self.intro_t-=1; (None if self.intro_t>0 else setattr(self,'phase','play')); return
        if self.done: self.done_t+=1; return
        self.game_t -= 1
        self.breathing_t += 0.025
        if self.holding_breath:
            self.breath_held_t += 1
            self.scope_target_r = max(22., self.scope_r - 2.)
        else:
            self.breath_held_t = 0
            self.scope_target_r = 50.
        self.scope_r = lrp(self.scope_r, self.scope_target_r, 0.12)
        # Spawn targets
        self.spawn_t -= 1
        if self.spawn_t <= 0:
            self.spawn_t = self.spawn_interval + random.randint(-20,20)
            self._spawn_target()
        # Advance targets
        for tgt in self.targets:
            tgt["age"] += 1
            tgt["r"] = min(18., tgt["r"]+1.2)
            tgt["life"] -= 1
        self.targets = [t for t in self.targets if t["life"]>0 and t["active"]]
        if self.game_t <= 0:
            accuracy = self.hits/max(1,self.hits+self.wrong_shots)
            self.finish(f"Hits: {self.hits}   Wrong shots: {self.wrong_shots}   Accuracy: {int(accuracy*100)}%")

    def draw(self):
        c=self.c; c.delete("all"); f=self.frame
        # Rooftop night scene — dark buildings below, targets above
        c.create_rectangle(0,PLAY_T,W,PLAY_B,fill="#020306",outline="")
        # Distant city silhouette
        for bx in range(0,W,45):
            bh=random.randint(30,100) if (bx//45)%7 != 0 else random.randint(80,180)
            c.create_rectangle(bx,PLAY_B-bh,bx+40,PLAY_B,fill=dc(FAR_BLD,1.2),outline="")
        # Rain in background
        self.rain.draw(c)

        if self.phase=="intro":
            t=1-self.intro_t/72.
            tg(c,W//2,H//2-30,"THE SHADOW",F(28,bold=True),lc(SKY_TOP,NEON_WHITE,t),NEON_WHITE,off=5)
            shadow_text(c,W//2,H//2+10,"One shot. Right target only. Don't rush. Don't miss.",F(12),lc(SKY_TOP,UI_HINT,t))
            shadow_text(c,W//2,H//2+36,"Right-click or hold SPACE to hold breath and steady aim.",F(11),lc(SKY_TOP,UI_DIM,t))
            self.draw_hud(); self.fx.draw_grain(c); self.fx.draw_letterbox(c); return

        # Background static figures (civilians to confuse)
        for bfx, bfy in self.background_figures:
            c.create_oval(bfx-6,bfy-18,bfx+6,bfy-4,fill=lc(SKY_TOP,dc(SKIN_C,0.5),0.4),outline="")
            c.create_rectangle(bfx-8,bfy-4,bfx+8,bfy+18,fill=lc(SKY_TOP,dc(COAT_C,1.5),0.35),outline="")

        # Active targets
        for tgt in self.targets:
            tx2=tgt["x"]; ty2=tgt["y"]
            col=tgt["col"]; r=tgt["r"]
            age_frac = min(1., tgt["age"]/30.)
            alpha = min(0.9, age_frac)
            # Silhouette
            c.create_oval(tx2-r*0.5, ty2-r*2, tx2+r*0.5, ty2-r*0.5,
                          fill=lc(SKY_TOP, SKIN_C, alpha*0.5), outline="")
            c.create_rectangle(tx2-r*0.6, ty2-r*0.5, tx2+r*0.6, ty2+r,
                               fill=lc(SKY_TOP, dc(COAT_C,1.8), alpha*0.6), outline="")
            # Target indicator (subtle — player must look carefully)
            if tgt["kind"]=="hostile":
                # Weapon glint
                pulse = 0.5+0.5*math.sin(time.time()*6+tx2)
                c.create_oval(tx2+r*0.4, ty2-r*0.2, tx2+r*0.8, ty2+r*0.2,
                              fill=lc(SKY_TOP,NEON_GOLD,alpha*pulse*0.6),outline="")
            else:
                # Raised hands
                c.create_line(tx2-r,ty2-r*0.3,tx2-r*0.6,ty2-r,fill=lc(SKY_TOP,SKIN_C,alpha*0.5),width=2)
                c.create_line(tx2+r,ty2-r*0.3,tx2+r*0.6,ty2-r,fill=lc(SKY_TOP,SKIN_C,alpha*0.5),width=2)
            # Life timer arc (how long target stays)
            life_ratio = tgt["life"] / 200.
            if life_ratio < 0.3:
                blink = 0.3+0.7*math.sin(f*0.35)
                glow(c,tx2,ty2,r+8,col,rings=2,fall=0.2*blink,bg=SKY_TOP)

        self.ps.draw(c)
        self.draw_popups()

        # SCOPE overlay
        cx2=int(self.cursor_x); cy2=int(self.cursor_y)
        sr=int(self.scope_r)
        # Dark overlay outside scope
        # We simulate this with a dark circle that has full coverage except scope area
        # Draw dark rects around scope
        c.create_rectangle(0,PLAY_T,W,cy2-sr,fill=lc(SKY_TOP,SKY_BOT,0.7),outline="")
        c.create_rectangle(0,cy2+sr,W,PLAY_B,fill=lc(SKY_TOP,SKY_BOT,0.7),outline="")
        c.create_rectangle(0,cy2-sr,cx2-sr,cy2+sr,fill=lc(SKY_TOP,SKY_BOT,0.7),outline="")
        c.create_rectangle(cx2+sr,cy2-sr,W,cy2+sr,fill=lc(SKY_TOP,SKY_BOT,0.7),outline="")
        # Scope circle (clear view)
        glow_ring(c,cx2,cy2,sr,FWHITE,width=3,rings=3)
        # Crosshair
        breath_wobble = 0. if self.holding_breath else math.sin(self.breathing_t*1.8)*4
        bwx=int(breath_wobble); bwy=int(breath_wobble*0.6)
        c.create_line(cx2-sr+8+bwx,cy2+bwy,cx2+sr-8+bwx,cy2+bwy,fill=lc(SKY_TOP,NEON_RED,0.7),width=1)
        c.create_line(cx2+bwx,cy2-sr+8+bwy,cx2+bwx,cy2+sr-8+bwy,fill=lc(SKY_TOP,NEON_RED,0.7),width=1)
        c.create_oval(cx2-6+bwx,cy2-6+bwy,cx2+6+bwx,cy2+6+bwy,fill="",outline=lc(SKY_TOP,NEON_RED,0.5),width=1)
        # Hold breath indicator
        if self.holding_breath:
            t3=min(1.,self.breath_held_t/30.)
            c.create_arc(cx2-sr-12,cy2-sr-12,cx2+sr+12,cy2+sr+12,
                         start=90,extent=int(360*t3),outline=NEON_GREEN,width=2,style="arc")

        secs_left=self.game_t//62
        self.draw_hud(f"HITS: {self.hits}  |  TIME: {secs_left}s")
        shadow_text(c,W//2,PLAY_B-18,
                    "HOLD BREATH (right-click) to steady aim" if not self.holding_breath else "BREATH HELD — shoot now",
                    F(11),UI_DIM if not self.holding_breath else NEON_GREEN)
        if self.done: self.draw_result()
        self.fx.draw_vignette(c)
        self.fx.draw_flash(c)
        self.fx.draw_grain(c)
        self.fx.draw_letterbox(c)

    def click(self, x, y):
        if self.click_done(x,y): return
        if self.phase=="intro": self.phase="play"; return
        if self.done: return
        # Check targets under crosshair (with breathing wobble)
        bw = 0 if self.holding_breath else math.sin(self.breathing_t*1.8)*4
        shot_x = x + bw; shot_y = y + bw*0.6
        # Flash regardless
        self.fx.trigger_flash(NEON_WHITE,0.25,0.12)
        self.ps.burst(x,y,NEON_WHITE,n=8,spd=3.)
        hit_any = False
        for tgt in list(self.targets):
            if math.hypot(shot_x-tgt["x"],shot_y-tgt["y"]) < max(20,tgt["r"]+12):
                hit_any = True
                lat_ms=int((time.time()-tgt["born"])*1000)
                if tgt["kind"]=="hostile":
                    self.hits += 1
                    pts=400+(300 if self.holding_breath else 0)
                    self.score+=pts
                    self.tr.log_click("shadow",x,y,True,lat_ms)
                    self.tr.log_accuracy("shadow",1.)
                    self.ps.burst(tgt["x"],tgt["y"],NEON_RED,n=20,spd=5.)
                    self.add_popup(x,y-30,f"+{pts}  NEUTRALISED",NEON_RED,16)
                    tgt["active"]=False
                else:
                    self.wrong_shots += 1
                    self.score=max(0,self.score-300)
                    self.tr.log_click("shadow",x,y,False,lat_ms)
                    self.tr.false_positives+=1
                    self.tr.log_accuracy("shadow",0.)
                    self.fx.trigger_flash(NEON_CYAN,0.5,0.06)
                    self.fx.trigger_shake(12)
                    self.add_popup(x,y-30,"-300  CIVILIAN HIT",NEON_CYAN,16)
                    tgt["active"]=False
                break
        if not hit_any:
            self.tr.log_pre_cue()

    def motion(self, x, y): self.cursor_x=float(x); self.cursor_y=float(y)
    def key(self, k):
        if k in ("space","space"): self.holding_breath=True
    def key_release(self, k):
        if k in ("space","space"): self.holding_breath=False

# ═══════════════════════════════════════════════════════════
#  SCENE: PSYCHOLOGICAL PROFILE  — animated noir file reveal
# ═══════════════════════════════════════════════════════════
class ProfileScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.results = game.tracker.compute()
        self.reveal_t = 0.
        self.bar_vals = {k: 0. for k in ["stress","anxiety","depression",
                                          "impulsivity","resilience"]}
        self.radar_t = 0.
        self.page = 0       # 0=stats, 1=signature, 2=susceptibility
        self.page_t = 0
        self.orb_t = 0.
        self.typewriter = TypewriterText()
        sig = self.results.get("signature","THE DETECTIVE")
        desc = self.results.get("signature_desc","")
        self.typewriter.set_text([
            (sig, UI_AMBER, F(22,bold=True), W//2, PLAY_T+60, "center"),
            (desc.split("\n")[0], FWHITE, F(13,italic=True), W//2, PLAY_T+96, "center"),
            (desc.split("\n")[1] if "\n" in desc else "", UI_HINT, F(12,italic=True), W//2, PLAY_T+118, "center"),
        ], speed=1)
        self.btn_hover = -1
        # Start rain subsiding (city winding down)
        self.rain.intensity = 0.7

    def update(self):
        super().update()
        self.reveal_t = min(1., self.reveal_t + 0.008)
        self.radar_t  = min(1., self.radar_t  + 0.014)
        self.orb_t += 0.02
        self.typewriter.step()
        # Animate bars
        target_keys = ["stress","anxiety","depression","impulsivity","resilience"]
        for k in target_keys:
            target = self.results.get(k, 50) / 100.
            self.bar_vals[k] = lrp(self.bar_vals[k], target, 0.04)

    def draw(self):
        c=self.c; c.delete("all"); f=self.frame
        # Dark atmospheric background
        c.create_rectangle(0,0,W,H,fill="#020408",outline="")
        # Subtle city outside window (left side)
        self.city.draw(c, cam_x=f*0.1)
        # Dark overlay on city
        c.create_rectangle(0,0,W//3,H,fill=lc(SKY_TOP,"#020408",0.7),outline="",stipple="gray50")

        # FILE FOLDER aesthetic on right 2/3
        rr(c, W//3+10, LB_H+8, W-10, H-LB_H-8, r=6,
           fill=lc(SKY_TOP,"#040810",0.97), outline=lc(SKY_TOP,UI_DIM,0.5), w=1)

        # "CLASSIFIED" stamp effect
        t_reveal = ease_out(self.reveal_t)
        c.create_text(W//3+60, LB_H+24, text="CLASSIFIED",
                      font=F(10,bold=True), fill=lc(SKY_TOP,NEON_RED,t_reveal*0.6),
                      anchor="w")
        c.create_text(W-20, LB_H+24, text="PHANTOM CITY P.D.",
                      font=FC(9), fill=lc(SKY_TOP,UI_DIM,t_reveal), anchor="e")

        # SIGNATURE — typewriter
        self.typewriter.draw(c)

        # Flag badge
        flag = self.results.get("flag","STABLE")
        flag_cols = {"STABLE":NEON_GREEN,"NOTABLE":NEON_GOLD,"ELEVATED":NEON_PURP,"CRITICAL":NEON_RED}
        fc2 = flag_cols.get(flag, UI_HINT)
        glow(c, W//3+50, PLAY_T+155, 22, fc2, rings=4, fall=0.35, bg=SKY_TOP)
        rr(c, W//3+20, PLAY_T+140, W//3+80, PLAY_T+170, r=6,
           fill=lc(SKY_TOP, dc(fc2,0.15), 0.95), outline=fc2, w=2)
        shadow_text(c, W//3+50, PLAY_T+155, flag, F(10,bold=True), WHITE)

        # BAR CHART — psychological dimensions
        bar_data = [
            ("STRESS",      "stress",      lc(NEON_RED,  NEON_GOLD, 0.3)),
            ("ANXIETY",     "anxiety",     NEON_PURP),
            ("DEPRESSION",  "depression",  NEON_BLUE),
            ("IMPULSIVITY", "impulsivity", NEON_PINK),
            ("RESILIENCE",  "resilience",  NEON_GREEN),
        ]
        bx_start = W//3 + 30
        bar_max_w = W - bx_start - 80
        for bi, (label, key, col) in enumerate(bar_data):
            by2 = PLAY_T + 186 + bi*52
            val = self.bar_vals[key]; raw_val = self.results.get(key, 50)
            # Label
            shadow_text(c, bx_start+4, by2-1, label, F(10,bold=True), WHITE, anchor="w")
            # Bar background
            rr(c, bx_start, by2+12, bx_start+bar_max_w, by2+30, r=4,
               fill=lc(SKY_TOP,UI_DIM,0.2), outline=lc(SKY_TOP,UI_DIM,0.3), w=1)
            # Bar fill
            bw = int(val*bar_max_w)
            if bw > 6:
                rr(c, bx_start, by2+12, bx_start+bw, by2+30, r=4,
                   fill=col, outline="", w=0)
                glow(c, bx_start+bw, by2+21, 8, col, rings=3, fall=0.4, bg=SKY_TOP)
            # Percentage
            shadow_text(c, bx_start+bar_max_w+36, by2+21,
                        f"{raw_val}%", F(11,bold=True), WHITE if val>0.5 else UI_HINT)

        # SUSCEPTIBILITY section
        susc = self.results.get("susceptibility", {})
        primary = susc.get("primary","—")
        sy3 = PLAY_T + 456
        rr(c, bx_start, sy3, W-20, sy3+55, r=6,
           fill=lc(SKY_TOP,"#060818",0.95), outline=lc(SKY_TOP,NEON_PURP,0.4), w=1)
        shadow_text(c, bx_start+8, sy3+14, "PRIMARY ENGAGEMENT DRIVER:", F(9), UI_DIM, anchor="w")
        tg(c, bx_start+8+(W-bx_start-28)//2, sy3+36, primary, F(13,bold=True), WHITE, NEON_PURP, off=2)

        # Moral profile
        moral = self.results.get("moral_profile","unknown")
        moral_col = {"empathetic":NEON_CYAN,"aggressive":NEON_RED,
                     "cautious":NEON_GOLD,"avoidant":UI_DIM,"unknown":UI_HINT}.get(moral,UI_HINT)
        shadow_text(c, bx_start+8, sy3+58, f"Interrogation style: {moral.upper()}",
                    F(10), moral_col, anchor="w")

        # Radar chart (left side, over city)
        rcx = W//6; rcy = PLAY_T + 200; rcr = 90
        labels2 = ["STRESS","ANXIETY","DEPRESS","IMPULSE","RESILIENCE"]
        keys2   = ["stress","anxiety","depression","impulsivity","resilience"]
        cols2   = [lc(NEON_RED,NEON_GOLD,0.3),NEON_PURP,NEON_BLUE,NEON_PINK,NEON_GREEN]
        for ri in [0.25,0.5,0.75,1.]:
            rpts=[]
            for i in range(5):
                a=-math.pi/2+i*2*math.pi/5; rr2=rcr*ri
                rpts.extend([rcx+rr2*math.cos(a),rcy+rr2*math.sin(a)])
            c.create_polygon(rpts,fill="",outline=lc(SKY_TOP,UI_DIM,0.25),width=1)
        for i in range(5):
            a=-math.pi/2+i*2*math.pi/5
            c.create_line(rcx,rcy,rcx+rcr*math.cos(a),rcy+rcr*math.sin(a),
                          fill=lc(SKY_TOP,UI_DIM,0.2),width=1)
            lx3=rcx+(rcr+22)*math.cos(a); ly3=rcy+(rcr+22)*math.sin(a)
            shadow_text(c,int(lx3),int(ly3),labels2[i],F(9,bold=True),UI_HINT)
        rpts2=[]
        for i,k in enumerate(keys2):
            v=self.bar_vals.get(k,0.)*self.radar_t
            a=-math.pi/2+i*2*math.pi/5; r2=rcr*v
            rpts2.extend([rcx+r2*math.cos(a),rcy+r2*math.sin(a)])
        if len(rpts2)>=6:
            c.create_polygon(rpts2,fill=lc(SKY_TOP,NEON_CYAN,0.12),outline=NEON_CYAN,width=2)
        for i,k in enumerate(keys2):
            v=self.bar_vals.get(k,0.)*self.radar_t
            a=-math.pi/2+i*2*math.pi/5; r2=rcr*v
            glow(c,int(rcx+r2*math.cos(a)),int(rcy+r2*math.sin(a)),
                 6,cols2[i],rings=3,fall=0.4,bg=SKY_TOP)

        # Disclaimer (small, honest)
        shadow_text(c, W//2, PLAY_B-10,
                    "Reflective profile from gameplay patterns.  Not a clinical assessment.",
                    F(9,italic=True), lc(SKY_TOP,UI_DIM,0.7))

        # Nav buttons
        rr(c, W//2-130, PLAY_B-40, W//2+130, PLAY_B-14, r=8,
           fill=lc(SKY_TOP,"#050a14",0.95), outline=NEON_CYAN if self.btn_hover==0 else UI_DIM, w=1)
        shadow_text(c, W//2, PLAY_B-27, "PLAY AGAIN", F(12,bold=True), WHITE if self.btn_hover==0 else UI_HINT)

        self.ps.draw(c)
        self.fx.draw_vignette(c)
        self.fx.draw_grain(c)
        self.fx.draw_letterbox(c)
        # Letterbox text
        shadow_text(c, 18, LB_H//2, "DETECTIVE RAY SOLANO  —  CASE CLOSED", FC(10), UI_DIM, anchor="w")
        shadow_text(c, W-18, LB_H//2, "PHANTOM CITY P.D.", FC(10), UI_DIM, anchor="e")

    def click(self, x, y):
        if abs(x-W//2)<=130 and PLAY_B-40<=y<=PLAY_B-14:
            self.game.go("title")

    def motion(self, x, y):
        self.btn_hover = 0 if (abs(x-W//2)<=130 and PLAY_B-40<=y<=PLAY_B-14) else -1

# ═══════════════════════════════════════════════════════════
#  GAME CONTROLLER
# ═══════════════════════════════════════════════════════════
SCENE_MAP = {
    "title":    TitleScene,
    "prologue": PrologueScene,
    "hub":      HubScene,
    "profile":  ProfileScene,
}

class Game:
    def __init__(self, root):
        self.root = root
        root.title("PHANTOM CITY: NIGHT PROTOCOL")
        root.resizable(False, False)
        root.configure(bg="#000000")

        self.canvas = tk.Canvas(root, width=W, height=H, bg="#000000",
                                highlightthickness=0, cursor="none")
        self.canvas.pack()

        # Shared systems
        self.tracker    = PsychTracker()
        self.fx         = ScreenFX()
        self.rain       = RainSystem(intensity=300)
        self.city       = CityRenderer()
        self.trans      = Transition()
        self.high_scores = {}

        self.scene = TitleScene(self)

        self.canvas.bind("<Button-1>",        self._lclick)
        self.canvas.bind("<Button-3>",        self._rclick)
        self.canvas.bind("<Motion>",          self._motion)
        self.canvas.bind("<ButtonRelease-3>", self._rrelease)
        root.bind("<KeyPress>",   self._key)
        root.bind("<KeyRelease>", self._keyrel)
        root.bind("<Escape>",     lambda e: self.go("title"))

        self._loop()

    def go(self, name):
        def switch():
            self.scene.cleanup()
            self.scene = SCENE_MAP.get(name, TitleScene)(self)
        self.trans.start(switch, spd=0.09)

    def go_scene(self, SceneCls):
        def switch():
            self.scene.cleanup()
            self.scene = SceneCls(self)
        self.trans.start(switch, spd=0.09)

    def _lclick(self, e):
        if not self.trans.active: self.scene.click(e.x, e.y)
    def _rclick(self, e):
        if not self.trans.active:
            if hasattr(self.scene, 'holding_breath'): self.scene.holding_breath=True
    def _rrelease(self, e):
        if hasattr(self.scene, 'holding_breath'): self.scene.holding_breath=False
    def _motion(self, e):
        if not self.trans.active: self.scene.motion(e.x, e.y)
    def _key(self, e):
        if not self.trans.active: self.scene.key(e.keysym)
    def _keyrel(self, e):
        if hasattr(self.scene, 'key_release'): self.scene.key_release(e.keysym)

    def _loop(self):
        self.trans.step()
        self.scene.update()
        self.scene.draw()
        self.trans.draw(self.canvas)
        self.root.after(16, self._loop)

# ═══════════════════════════════════════════════════════════
#  ENTRY
# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    root = tk.Tk()
    game = Game(root)
    root.mainloop()
