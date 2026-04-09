"""
╔══════════════════════════════════════════════════════════╗
║              🐦  FLAPPY FRIEND  🐦                       ║
║                                                          ║
║  USAGE:                                                  ║
║    python flappy_friend.py <image> <jump_image>          ║
║                    [--sound SOUND_FILE]                  ║
║                                                          ║
║  REQUIRED ARGS:                                          ║
║    image        Normal flying photo of your friend       ║
║    jump_image   Photo shown while jumping/flapping       ║
║                                                          ║
║  OPTIONAL ARGS:                                          ║
║    --sound      Sound file on flap (default: win.ogg)   ║
║                                                          ║
║  EXAMPLES:                                               ║
║    python flappy_friend.py friend.png friend_jump.png    ║
║    python flappy_friend.py a.jpg b.jpg --sound yay.wav  ║
║                                                          ║
║  INSTALL:  pip install pygame                            ║
║  CONTROLS: SPACE or mouse click to flap                  ║
╚══════════════════════════════════════════════════════════╝
"""

import pygame
import sys
import random
import math
import argparse

# ──────────────────────────────────────────────────────────
# PARSE COMMAND-LINE ARGUMENTS
# ──────────────────────────────────────────────────────────

parser = argparse.ArgumentParser(
    description="🐦 Flappy Friend — fly your friend across the screen!",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=(
        "Examples:\n"
        "  python flappy_friend.py friend.png friend_jump.png\n"
        "  python flappy_friend.py a.jpg b.jpg --sound yay.wav\n"
    ),
)
parser.add_argument(
    "image",
    metavar="FRIEND_IMAGE",
    help="Path to your friend's normal flying photo (e.g. friend.png)",
)
parser.add_argument(
    "jump_image",
    metavar="FRIEND_IMAGE_JUMP",
    help="Path to the photo shown while jumping/flapping (e.g. friend_jump.png)",
)
parser.add_argument(
    "--sound",
    metavar="JUMP_SOUND",
    default="win.ogg",
    help="Sound file played on each flap (default: win.ogg)",
)

args = parser.parse_args()

FRIEND_IMAGE      = args.image       # required positional arg
FRIEND_IMAGE_JUMP = args.jump_image  # required positional arg
JUMP_SOUND        = args.sound       # optional; defaults to "win.ogg"

# ──────────────────────────────────────────────────────────
# GAME SETTINGS  (tweak these!)
# ──────────────────────────────────────────────────────────
FPS            = 40    # Lower = slower/easier, Higher = faster
GRAVITY        = 0.4
FLAP_POWER     = -8
PIPE_SPEED     = 3
PIPE_GAP       = 220
PIPE_INTERVAL  = 95

# Bird sprite size (width x height) — full photo will fill this
BIRD_W = 100
BIRD_H = 120

# ──────────────────────────────────────────────────────────
# WINDOW
# ──────────────────────────────────────────────────────────
WIN_W, WIN_H = 1300, 800
GROUND_H     = 60


# ══════════════════════════════════════════════════════════
#   HELPERS
# ══════════════════════════════════════════════════════════

def load_friend(path, w, h):
    """Load full friend photo scaled+cropped to bird size, with rounded corners."""
    try:
        img = pygame.image.load(path).convert_alpha()

        # Scale keeping aspect ratio, then center-crop to (w, h)
        iw, ih = img.get_size()
        scale = max(w / iw, h / ih)
        nw, nh = int(iw * scale), int(ih * scale)
        img = pygame.transform.smoothscale(img, (nw, nh))

        # Center crop
        crop_x = (nw - w) // 2
        crop_y = (nh - h) // 2
        cropped = pygame.Surface((w, h), pygame.SRCALPHA)
        cropped.blit(img, (0, 0), (crop_x, crop_y, w, h))

        # Rounded corners mask
        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        mask.fill((0, 0, 0, 0))
        radius = 12
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h), border_radius=radius)

        result = pygame.Surface((w, h), pygame.SRCALPHA)
        result.blit(cropped, (0, 0))
        for px in range(w):
            for py in range(h):
                if mask.get_at((px, py))[3] == 0:
                    result.set_at((px, py), (0, 0, 0, 0))

        print(f"✅ Friend photo loaded: {path}")
        return result
    except Exception as e:
        print(f"⚠️  Could not load image '{path}': {e}")
        print("   Using default yellow bird instead.")
        return None


def load_sound(path):
    try:
        sound = pygame.mixer.Sound(path)
        print(f"✅ Sound loaded: {path}")
        return sound
    except Exception as e:
        print(f"⚠️  Could not load sound '{path}': {e}")
        return None


def make_beep():
    try:
        import numpy as np
        sr = 44100
        dur = 0.12
        t = np.linspace(0, dur, int(sr * dur), False)
        freq = np.linspace(500, 900, len(t))
        wave = (np.sin(2 * np.pi * freq * t) * 0.3 * 32767).astype(np.int16)
        wave = (wave * np.linspace(1, 0, len(t))).astype(np.int16)
        return pygame.sndarray.make_sound(np.column_stack([wave, wave]))
    except Exception:
        return None


# ══════════════════════════════════════════════════════════
#   DRAW FUNCTIONS
# ══════════════════════════════════════════════════════════

def draw_friend_bird(surface, friend_surf, x, y, angle):
    """Draw the FULL friend photo as the flying bird — no border box."""
    # Rotate the friend photo directly with tilt
    rotated = pygame.transform.rotate(friend_surf, -angle)
    rect = rotated.get_rect(center=(x, y))
    surface.blit(rotated, rect)


def draw_default_bird(surface, x, y, w, h, angle):
    """Fallback default yellow bird (rectangular body)."""
    bird_surf = pygame.Surface((w + 20, h + 20), pygame.SRCALPHA)
    cx, cy = w // 2 + 10, h // 2 + 10

    pygame.draw.rect(bird_surf, (245, 197, 24), (10, 10, w, h), border_radius=14)
    pygame.draw.rect(bird_surf, (184, 134, 11), (10, 10, w, h), 2, border_radius=14)

    wing = [(cx-20, cy+5), (cx-5, cy-8), (cx+5, cy+14), (cx-12, cy+18)]
    pygame.draw.polygon(bird_surf, (230, 168, 0), wing)

    pygame.draw.circle(bird_surf, (255,255,255), (cx+14, cy-8), 8)
    pygame.draw.circle(bird_surf, (30, 30, 30),  (cx+15, cy-8), 4)
    pygame.draw.circle(bird_surf, (255,255,255), (cx+16, cy-11), 2)

    beak_x = cx + w // 2 - 2
    beak = [(beak_x, cy), (beak_x+14, cy+5), (beak_x, cy+10)]
    pygame.draw.polygon(bird_surf, (255, 140, 0), beak)

    rotated = pygame.transform.rotate(bird_surf, -angle)
    rect = rotated.get_rect(center=(x, y))
    surface.blit(rotated, rect)


def draw_pipe(surface, pipe):
    px, top, bottom = pipe['x'], pipe['top'], pipe['bottom']
    pw = 56
    cap_h, cap_extra = 24, 9
    green_dark  = (46, 125, 50)
    green_mid   = (76, 175, 80)
    green_light = (129, 199, 132)

    pygame.draw.rect(surface, green_mid,   (px, 0, pw, top))
    pygame.draw.rect(surface, green_light, (px+7, 0, 9, top))
    pygame.draw.rect(surface, green_dark,  (px, 0, pw, top), 2)
    pygame.draw.rect(surface, green_dark,  (px-cap_extra, top-cap_h, pw+cap_extra*2, cap_h), border_radius=4)
    pygame.draw.rect(surface, green_mid,   (px-cap_extra+5, top-cap_h+4, 11, cap_h-8))

    pygame.draw.rect(surface, green_mid,   (px, bottom, pw, WIN_H-bottom))
    pygame.draw.rect(surface, green_light, (px+7, bottom, 9, WIN_H-bottom))
    pygame.draw.rect(surface, green_dark,  (px, bottom, pw, WIN_H-bottom), 2)
    pygame.draw.rect(surface, green_dark,  (px-cap_extra, bottom, pw+cap_extra*2, cap_h), border_radius=4)
    pygame.draw.rect(surface, green_mid,   (px-cap_extra+5, bottom+4, 11, cap_h-8))


def draw_background(surface, cloud_x):
    for i in range(WIN_H - GROUND_H):
        t = i / (WIN_H - GROUND_H)
        r = int(100 + (176 - 100) * t)
        g = int(180 + (220 - 180) * t)
        b = int(240 + (250 - 240) * t)
        pygame.draw.line(surface, (r, g, b), (0, i), (WIN_W, i))

    def cloud(cx, cy, sc):
        for ox, oy, cr in [(0,0,22),(30,-8,19),(60,0,23)]:
            pygame.draw.circle(surface, (255,255,255),
                               (int(cx+ox*sc), int(cy+oy*sc)), int(cr*sc))

    cloud((cloud_x)       % (WIN_W+160) - 80,  65,  1.0)
    cloud((cloud_x + 200) % (WIN_W+160) - 80, 105,  1.2)
    cloud((cloud_x + 350) % (WIN_W+160) - 80,  48,  0.75)

    pygame.draw.rect(surface, (90, 150, 60),   (0, WIN_H-GROUND_H,      WIN_W, 14))
    pygame.draw.rect(surface, (139, 105, 20),  (0, WIN_H-GROUND_H+14,   WIN_W, GROUND_H-14))
    for gx in range(0, WIN_W, 30):
        pygame.draw.line(surface, (110, 170, 70),
                         (gx, WIN_H-GROUND_H), (gx+15, WIN_H-GROUND_H+10), 2)


def draw_text_center(surface, font, text, y, color, shadow=True):
    if shadow:
        sh = font.render(text, True, (0, 0, 0))
        surface.blit(sh, sh.get_rect(center=(WIN_W//2+2, y+2)))
    surf = font.render(text, True, color)
    surface.blit(surf, surf.get_rect(center=(WIN_W//2, y)))


def draw_hud(surface, font_big, font_small, score, best):
    shadow = font_big.render(str(score), True, (0, 0, 0))
    surface.blit(shadow, shadow.get_rect(center=(WIN_W//2+2, 52)))
    sc = font_big.render(str(score), True, (245, 197, 24))
    surface.blit(sc, sc.get_rect(center=(WIN_W//2, 50)))
    best_surf = font_small.render(f"BEST: {best}", True, (255, 255, 255))
    surface.blit(best_surf, (10, 10))


# ══════════════════════════════════════════════════════════
#   MAIN
# ══════════════════════════════════════════════════════════

def main():
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Flappy Friend")
    clock = pygame.time.Clock()

    try:
        font_big   = pygame.font.SysFont("couriernew", 52, bold=True)
        font_med   = pygame.font.SysFont("couriernew", 30, bold=True)
        font_small = pygame.font.SysFont("couriernew", 18)
    except Exception:
        font_big   = pygame.font.Font(None, 56)
        font_med   = pygame.font.Font(None, 34)
        font_small = pygame.font.Font(None, 22)

    friend_surf      = load_friend(FRIEND_IMAGE,      BIRD_W, BIRD_H) if FRIEND_IMAGE      else None
    friend_surf_jump = load_friend(FRIEND_IMAGE_JUMP, BIRD_W, BIRD_H) if FRIEND_IMAGE_JUMP else None
    jump_sound  = load_sound(JUMP_SOUND) if JUMP_SOUND else None
    beep        = make_beep()

    def play_jump():
        if jump_sound:   jump_sound.play()
        elif beep:       beep.play()

    COLL_W = BIRD_W - 10
    COLL_H = BIRD_H - 10
    PIPE_W = 56

    def new_bird():
        return {'x': 90, 'y': WIN_H // 2, 'vy': 0}

    jump_frame = 0  # counts down frames to show jump image

    def new_pipe():
        top = random.randint(80, WIN_H - GROUND_H - PIPE_GAP - 80)
        return {'x': WIN_W + 10, 'top': top, 'bottom': top + PIPE_GAP, 'scored': False}

    bird       = new_bird()
    pipes      = []
    score      = 0
    best       = 0
    state      = 'idle'
    pipe_timer = 0
    cloud_x    = 0
    dead_timer = 0

    print("\n🎮 Game started! Press SPACE or click to flap.\n")

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                if event.type == pygame.KEYDOWN and event.key != pygame.K_SPACE:
                    continue
                if state == 'idle':
                    state = 'playing'
                    bird['vy'] = FLAP_POWER
                    play_jump()
                    jump_frame = 12
                elif state == 'playing':
                    bird['vy'] = FLAP_POWER
                    play_jump()
                    jump_frame = 12
                elif state == 'dead' and dead_timer > 30:
                    bird       = new_bird()
                    pipes      = []
                    score      = 0
                    pipe_timer = 0
                    state      = 'playing'
                    bird['vy'] = FLAP_POWER
                    play_jump()
                    jump_frame = 12

        cloud_x = (cloud_x + 0.4) % (WIN_W + 160)

        if state == 'playing':
            bird['vy'] += GRAVITY
            bird['y']  += bird['vy']

            pipe_timer += 1
            if pipe_timer >= PIPE_INTERVAL:
                pipes.append(new_pipe())
                pipe_timer = 0

            bx = bird['x']
            by = bird['y']
            bleft  = bx - COLL_W // 2
            bright = bx + COLL_W // 2
            btop   = by - COLL_H // 2
            bbot   = by + COLL_H // 2

            for pipe in pipes:
                pipe['x'] -= PIPE_SPEED
                if not pipe['scored'] and pipe['x'] + PIPE_W < bx:
                    pipe['scored'] = True
                    score += 1
                    if score > best:
                        best = score
                if bright > pipe['x'] and bleft < pipe['x'] + PIPE_W:
                    if btop < pipe['top'] or bbot > pipe['bottom']:
                        state = 'dead'
                        dead_timer = 0

            pipes = [p for p in pipes if p['x'] > -80]

            if bbot >= WIN_H - GROUND_H:
                state = 'dead'
                dead_timer = 0
            if btop <= 0:
                bird['y'] = COLL_H // 2
                bird['vy'] = 0

        if jump_frame > 0:
            jump_frame -= 1

        if state == 'dead':
            dead_timer += 1

        # ── Draw ──
        draw_background(screen, cloud_x)
        for pipe in pipes:
            draw_pipe(screen, pipe)

        angle = max(-25, min(bird['vy'] * 4, 85))

        if friend_surf:
            # Show jump pic while flapping, normal pic otherwise
            active_surf = (friend_surf_jump if (jump_frame > 0 and friend_surf_jump) else friend_surf)
            draw_friend_bird(screen, active_surf, int(bird['x']), int(bird['y']), angle)
        else:
            draw_default_bird(screen, int(bird['x']), int(bird['y']), BIRD_W, BIRD_H, angle)

        draw_hud(screen, font_big, font_small, score, best)

        if state == 'idle':
            ov = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 110))
            screen.blit(ov, (0, 0))
            draw_text_center(screen, font_med,   "FLAPPY FRIEND",  WIN_H//2 - 80, (245, 197, 24))
            if friend_surf:
                preview = pygame.transform.smoothscale(friend_surf, (80, 100))
                screen.blit(preview, preview.get_rect(center=(WIN_W//2, WIN_H//2 - 5)))
            draw_text_center(screen, font_small, "SPACE or CLICK",  WIN_H//2 + 65, (255, 255, 255))
            draw_text_center(screen, font_small, "to start!",       WIN_H//2 + 92, (200, 200, 200))

        if state == 'dead':
            ov = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 140))
            screen.blit(ov, (0, 0))
            draw_text_center(screen, font_med,   "GAME OVER!",              WIN_H//2 - 70, (255, 80, 80))
            draw_text_center(screen, font_small, f"Score: {score}",          WIN_H//2 - 15, (245, 197, 24))
            draw_text_center(screen, font_small, f"Best:  {best}",           WIN_H//2 + 15, (200, 200, 200))
            if dead_timer > 30:
                draw_text_center(screen, font_small, "SPACE or CLICK to retry", WIN_H//2 + 55, (160, 255, 160))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
