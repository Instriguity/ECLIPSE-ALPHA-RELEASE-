#FIRSTLY RUN pip install pygame IN CMD FOR IT TO WORK. USE Visual Studio Code OR ANY OTHER PYTHON RUNNER. 
import pygame
import random
import math
import sys
import json
import os
import tempfile
import socket
import threading
import hashlib
import getpass
import uuid

pygame.init()

# ============================================================
#                         E C L I P S E
#                    ROGUELITE EDITION
# ============================================================

WIDTH = 1250
HEIGHT = 700
FPS = 60

MAX_LEVEL = 15

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT)
)

pygame.display.set_caption(
    "E C L I P S E"
)

clock = pygame.time.Clock()

# ============================================================
# COLORS
# ============================================================

BLACK = (2, 2, 4)
VOID = (6, 5, 8)
DARK = (12, 10, 12)
WHITE = (255, 255, 255)

SOLAR = (255, 225, 45)
SUN = (255, 190, 25)
GOLD = (255, 145, 20)

ORANGE = (255, 105, 25)
DEEP_ORANGE = (210, 55, 10)
RED = (255, 45, 35)

GREEN = (90, 255, 120)
BLUE = (80, 170, 255)
PURPLE = (190, 90, 255)
CYAN = (80, 240, 255)

# ============================================================
# FONTS
# ============================================================

FONT_TINY = pygame.font.SysFont(
    "consolas",
    15,
    bold=True
)

FONT_SMALL = pygame.font.SysFont(
    "consolas",
    20,
    bold=True
)

FONT_MED = pygame.font.SysFont(
    "consolas",
    30,
    bold=True
)

FONT_BIG = pygame.font.SysFont(
    "consolas",
    52,
    bold=True
)

FONT_HUGE = pygame.font.SysFont(
    "consolas",
    76,
    bold=True
)

FONT_TITLE = pygame.font.SysFont(
    "consolas",
    92,
    bold=True
)

# ============================================================
# ONLINE NETWORK SETUP
# ============================================================

SERVER_IP = "127.0.0.1"
SERVER_PORT = 55555

PLAYER_ID = str(
    uuid.uuid4()
)

online_connected = False

sock = None

# Network timing/buffering.
online_send_timer = 0
online_receive_buffer = ""

# ============================================================
# CONNECT TO MULTIPLAYER SERVER
# ============================================================

def connect_to_server():

    global sock
    global online_connected

    print()
    print("========================================")
    print("        E C L I P S E  ONLINE")
    print("========================================")

    print(
        f"[ONLINE] Connecting to "
        f"{SERVER_IP}:{SERVER_PORT}..."
    )

    try:

        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        sock.settimeout(3)

        sock.connect(
            (
                SERVER_IP,
                SERVER_PORT
            )
        )

        sock.setblocking(False)

        online_connected = True

        print("[ONLINE] CONNECTED!")

        print(
            f"[ONLINE] Server: "
            f"{SERVER_IP}:{SERVER_PORT}"
        )

        print(
            f"[ONLINE] Player ID: "
            f"{PLAYER_ID}"
        )

        print(
            "[ONLINE] Multiplayer is ready!"
        )

        print(
            "========================================"
        )

        return True

    except ConnectionRefusedError:

        online_connected = False

        print(
            "[ONLINE] CONNECTION REFUSED!"
        )

        print(
            "[ONLINE] Is the multiplayer server running?"
        )

        if sock is not None:

            try:
                sock.close()
            except Exception:
                pass

        sock = None

        return False

    except socket.timeout:

        online_connected = False

        print(
            "[ONLINE] CONNECTION TIMED OUT!"
        )

        if sock is not None:

            try:
                sock.close()
            except Exception:
                pass

        sock = None

        return False

    except OSError as e:

        online_connected = False

        print(
            f"[ONLINE] CONNECTION ERROR: {e}"
        )

        if sock is not None:

            try:
                sock.close()
            except Exception:
                pass

        sock = None

        return False

# ============================================================
# HELPERS
# ============================================================

def clamp(v, low, high):
    return max(
        low,
        min(high, v)
    )


def distance(
    x1,
    y1,
    x2,
    y2
):
    return math.hypot(
        x2 - x1,
        y2 - y1
    )


def draw_text(
    text,
    font,
    x,
    y,
    color=WHITE,
    center=True
):
    image = font.render(
        str(text),
        True,
        color
    )

    if center:
        rect = image.get_rect(
            center=(
                int(x),
                int(y)
            )
        )
    else:
        rect = image.get_rect(
            topleft=(
                int(x),
                int(y)
            )
        )

    screen.blit(
        image,
        rect
    )


def draw_glow_text(
    text,
    font,
    x,
    y,
    color
):
    """
    Draws layered transparent text behind the main text
    to create a simple neon/glow effect.
    """

    x = int(x)
    y = int(y)

    for offset, alpha in (
        (10, 18),
        (6, 32),
        (3, 52)
    ):
        glow_surface = pygame.Surface(
            (
                WIDTH,
                HEIGHT
            ),
            pygame.SRCALPHA
        )

        image = font.render(
            str(text),
            True,
            (
                color[0],
                color[1],
                color[2],
                alpha
            )
        )

        rect = image.get_rect(
            center=(
                x + random.randint(-offset, offset)
                if offset == 10
                else x,
                y + random.randint(-offset, offset)
                if offset == 10
                else y
            )
        )

        glow_surface.blit(
            image,
            rect
        )

        screen.blit(
            glow_surface,
            (0, 0)
        )

    draw_text(
        text,
        font,
        x,
        y,
        color
    )


# ============================================================
# PROFILE / LOGIN SYSTEM
# ============================================================

PROFILE_FOLDER = os.path.join(
    os.path.expanduser("~"),
    ".eclipse_roguelite"
)

PROFILE_FILE = os.path.join(
    PROFILE_FOLDER,
    "profiles.json"
)

current_username = ""
is_guest = False


def hash_password(password):

    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


def load_profiles():

    try:

        os.makedirs(
            PROFILE_FOLDER,
            exist_ok=True
        )

        if not os.path.exists(
            PROFILE_FILE
        ):
            return {}

        with open(
            PROFILE_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if isinstance(
            data,
            dict
        ):
            return data

    except (
        OSError,
        json.JSONDecodeError,
        TypeError,
        ValueError
    ) as error:

        print(
            "PROFILE LOAD ERROR:",
            error
        )

    return {}


def save_profiles(
    profiles
):

    try:

        os.makedirs(
            PROFILE_FOLDER,
            exist_ok=True
        )

        fd, temp_path = tempfile.mkstemp(
            prefix="eclipse_profiles_",
            suffix=".tmp",
            dir=PROFILE_FOLDER
        )

        try:

            with os.fdopen(
                fd,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    profiles,
                    file,
                    indent=4
                )

            os.replace(
                temp_path,
                PROFILE_FILE
            )

        except Exception:

            try:

                os.remove(
                    temp_path
                )

            except OSError:
                pass

    except Exception as error:

        print(
            "PROFILE SAVE ERROR:",
            error
        )


def valid_username(
    username
):

    if not 3 <= len(username) <= 16:
        return False

    allowed = (
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789_-"
    )

    return all(
        character in allowed
        for character in username
    )


def create_profile(
    username,
    password
):

    profiles = load_profiles()

    username = username.strip()
    username_key = username.lower()

    if not valid_username(
        username
    ):

        return (
            False,
            "USERNAME MUST BE 3-16 LETTERS, NUMBERS, _ OR -"
        )

    if username_key in profiles:

        return (
            False,
            "USERNAME ALREADY EXISTS"
        )

    if len(password) < 4:

        return (
            False,
            "PASSWORD MUST BE AT LEAST 4 CHARACTERS"
        )

    profiles[username_key] = {

        "username": username,

        "password": hash_password(
            password
        ),

        "highest_unlocked_level": 1,

        "best_score": 0
    }

    save_profiles(
        profiles
    )

    return (
        True,
        "PROFILE CREATED"
    )


def login_profile(
    username,
    password
):

    profiles = load_profiles()

    username = username.strip()
    username_key = username.lower()

    if username_key not in profiles:

        return (
            False,
            "PROFILE NOT FOUND"
        )

    profile = profiles.get(
        username_key,
        {}
    )

    if not isinstance(
        profile,
        dict
    ):

        return (
            False,
            "PROFILE DATA CORRUPTED"
        )

    if profile.get(
        "password"
    ) != hash_password(
        password
    ):

        return (
            False,
            "INCORRECT PASSWORD"
        )

    return (
        True,
        "LOGIN SUCCESSFUL"
    )


# ============================================================
# GUEST NAME
# ============================================================

def create_guest_name():

    return (
        "GUEST-"
        +
        str(
            random.randint(
                1000,
                9999
            )
        )
    )


# ============================================================
# ECLIPSE LOGIN PARTICLES
# ============================================================

login_particles = []


def create_login_particles():

    login_particles.clear()

    for _ in range(90):

        login_particles.append({

            "x": random.uniform(
                0,
                WIDTH
            ),

            "y": random.uniform(
                0,
                HEIGHT
            ),

            "speed": random.uniform(
                8,
                28
            ),

            "size": random.choice(
                [1, 1, 1, 2]
            ),

            "alpha": random.randint(
                60,
                180
            ),

            "phase": random.uniform(
                0,
                math.tau
            )
        })


def update_login_particles(
    dt
):

    for particle in login_particles:

        particle["y"] -= (
            particle["speed"]
            *
            dt
        )

        particle["phase"] += (
            dt * 1.5
        )

        if particle["y"] < -10:

            particle["y"] = (
                HEIGHT + 10
            )

            particle["x"] = random.uniform(
                0,
                WIDTH
            )


def draw_login_particles(
    time_value
):

    for particle in login_particles:

        pulse = (
            math.sin(
                particle["phase"]
                +
                time_value
            )
            + 1
        ) / 2

        alpha = int(
            particle["alpha"]
            *
            (
                0.45
                +
                pulse * 0.55
            )
        )

        size = particle["size"]

        surface = pygame.Surface(
            (
                size * 4,
                size * 4
            ),
            pygame.SRCALPHA
        )

        pygame.draw.circle(
            surface,
            (
                255,
                170,
                45,
                alpha
            ),
            (
                size * 2,
                size * 2
            ),
            size
        )

        screen.blit(
            surface,
            (
                int(
                    particle["x"]
                    -
                    size * 2
                ),
                int(
                    particle["y"]
                    -
                    size * 2
                )
            )
        )


# ============================================================
# LOGIN BUTTON DRAWING
# ============================================================

def draw_login_button(
    rect,
    title,
    subtitle="",
    active=False,
    accent=GOLD
):

    mouse_pos = pygame.mouse.get_pos()

    hovered = rect.collidepoint(
        mouse_pos
    )

    if active:

        fill = (
            55,
            34,
            12
        )

    elif hovered:

        fill = (
            42,
            28,
            14
        )

    else:

        fill = (
            20,
            18,
            22
        )

    # Shadow

    shadow = pygame.Rect(
        rect.x,
        rect.y + 5,
        rect.width,
        rect.height
    )

    pygame.draw.rect(
        screen,
        (
            0,
            0,
            0
        ),
        shadow,
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        fill,
        rect,
        border_radius=12
    )

    border_color = (
        accent
        if active or hovered
        else (
            70,
            62,
            55
        )
    )

    pygame.draw.rect(
        screen,
        border_color,
        rect,
        2,
        border_radius=12
    )

    title_y = (
        rect.centery - 7
        if subtitle
        else rect.centery
    )

    draw_text(
        title,
        FONT_SMALL,
        rect.centerx,
        title_y,
        accent
        if active or hovered
        else WHITE
    )

    if subtitle:

        draw_text(
            subtitle,
            FONT_TINY,
            rect.centerx,
            rect.centery + 18,
            (
                155,
                145,
                135
            )
        )


# ============================================================
# PROFILE LOGIN SCREEN
# ============================================================

def profile_login():

    global current_username
    global is_guest

    username = ""
    password = ""

    mode = "login"

    active_field = "username"

    message = ""
    message_timer = 0

    login_clock = pygame.time.Clock()

    create_login_particles()

    # --------------------------------------------------------
    # BUTTONS
    # --------------------------------------------------------

    login_button = pygame.Rect(
        420,
        485,
        190,
        58
    )

    create_button = pygame.Rect(
        630,
        485,
        190,
        58
    )

    guest_button = pygame.Rect(
        420,
        555,
        400,
        55
    )

    username_box = pygame.Rect(
        420,
        300,
        400,
        55
    )

    password_box = pygame.Rect(
        420,
        385,
        400,
        55
    )

    running = True

    while running:

        dt = (
            login_clock.tick(FPS)
            /
            1000.0
        )

        dt = min(
            dt,
            0.05
        )

        time_value = (
            pygame.time.get_ticks()
            /
            1000.0
        )

        update_login_particles(
            dt
        )

        # ====================================================
        # EVENTS
        # ====================================================

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                pygame.quit()
                sys.exit()

            # ------------------------------------------------
            # KEYBOARD
            # ------------------------------------------------

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:

                    pygame.quit()
                    sys.exit()

                elif event.key == pygame.K_TAB:

                    if active_field == "username":

                        active_field = "password"

                    else:

                        active_field = "username"

                elif event.key == pygame.K_BACKSPACE:

                    if active_field == "username":

                        username = username[:-1]

                    else:

                        password = password[:-1]

                elif event.key == pygame.K_F1:

                    mode = "login"
                    message = ""
                    message_timer = 0

                elif event.key == pygame.K_F2:

                    mode = "create"
                    message = ""
                    message_timer = 0

                elif event.key == pygame.K_F3:

                    is_guest = True

                    current_username = (
                        create_guest_name()
                    )

                    return

                elif event.key == pygame.K_RETURN:

                    if mode == "login":

                        success, result = login_profile(
                            username,
                            password
                        )

                        if success:

                            profiles = load_profiles()

                            profile = profiles.get(
                                username.lower(),
                                {}
                            )

                            current_username = (
                                profile.get(
                                    "username",
                                    username
                                )
                            )

                            is_guest = False

                            return

                        message = result
                        message_timer = 3

                    else:

                        success, result = create_profile(
                            username,
                            password
                        )

                        if success:

                            current_username = username
                            is_guest = False

                            return

                        message = result
                        message_timer = 3

                elif event.unicode and event.unicode.isprintable():

                    if active_field == "username":

                        if len(username) < 16:

                            allowed = (
                                "abcdefghijklmnopqrstuvwxyz"
                                "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                                "0123456789_-"
                            )

                            if event.unicode in allowed:

                                username += (
                                    event.unicode
                                )

                    else:

                        if len(password) < 32:

                            password += (
                                event.unicode
                            )

            # ------------------------------------------------
            # MOUSE
            # ------------------------------------------------

            elif event.type == pygame.MOUSEBUTTONDOWN:

                if event.button != 1:
                    continue

                mouse_pos = event.pos

                # Username

                if username_box.collidepoint(
                    mouse_pos
                ):

                    active_field = "username"

                # Password

                elif password_box.collidepoint(
                    mouse_pos
                ):

                    active_field = "password"

                # LOGIN

                elif login_button.collidepoint(
                    mouse_pos
                ):

                    mode = "login"

                    success, result = login_profile(
                        username,
                        password
                    )

                    if success:

                        profiles = load_profiles()

                        profile = profiles.get(
                            username.lower(),
                            {}
                        )

                        current_username = (
                            profile.get(
                                "username",
                                username
                            )
                        )

                        is_guest = False

                        return

                    message = result
                    message_timer = 3

                # CREATE

                elif create_button.collidepoint(
                    mouse_pos
                ):

                    mode = "create"

                    success, result = create_profile(
                        username,
                        password
                    )

                    if success:

                        current_username = username
                        is_guest = False

                        return

                    message = result
                    message_timer = 3

                # GUEST

                elif guest_button.collidepoint(
                    mouse_pos
                ):

                    is_guest = True

                    current_username = (
                        create_guest_name()
                    )

                    return

        message_timer = max(
            0,
            message_timer - dt
        )

        # ====================================================
        # BACKGROUND
        # ====================================================

        screen.fill(
            BLACK
        )

        # Deep-space gradient

        for y in range(
            0,
            HEIGHT,
            20
        ):

            shade = int(
                3
                +
                (
                    y
                    /
                    HEIGHT
                )
                * 8
            )

            pygame.draw.rect(
                screen,
                (
                    shade,
                    shade,
                    min(
                        255,
                        shade + 2
                    )
                ),
                (
                    0,
                    y,
                    WIDTH,
                    20
                )
            )

        # ====================================================
        # LARGE ECLIPSE BEHIND UI
        # ====================================================

        eclipse_x = 170
        eclipse_y = HEIGHT // 2

        for radius, alpha in (
            (145, 8),
            (125, 12),
            (105, 18)
        ):

            glow = pygame.Surface(
                (
                    WIDTH,
                    HEIGHT
                ),
                pygame.SRCALPHA
            )

            pygame.draw.circle(
                glow,
                (
                    255,
                    145,
                    20,
                    alpha
                ),
                (
                    eclipse_x,
                    eclipse_y
                ),
                radius
            )

            screen.blit(
                glow,
                (0, 0)
            )

        pygame.draw.circle(
            screen,
            (
                8,
                7,
                9
            ),
            (
                eclipse_x,
                eclipse_y
            ),
            88
        )

        pygame.draw.circle(
            screen,
            GOLD,
            (
                eclipse_x,
                eclipse_y
            ),
            88,
            2
        )

        draw_login_particles(
            time_value
        )

        # ====================================================
        # MAIN PANEL
        # ====================================================

        panel = pygame.Rect(
            350,
            55,
            540,
            590
        )

        shadow = pygame.Rect(
            panel.x + 8,
            panel.y + 10,
            panel.width,
            panel.height
        )

        pygame.draw.rect(
            screen,
            (
                0,
                0,
                0
            ),
            shadow,
            border_radius=24
        )

        pygame.draw.rect(
            screen,
            (
                9,
                8,
                12
            ),
            panel,
            border_radius=24
        )

        pygame.draw.rect(
            screen,
            (
                65,
                55,
                45
            ),
            panel,
            2,
            border_radius=24
        )

        inner_panel = pygame.Rect(
            panel.x + 7,
            panel.y + 7,
            panel.width - 14,
            panel.height - 14
        )

        pygame.draw.rect(
            screen,
            (
                32,
                27,
                22
            ),
            inner_panel,
            1,
            border_radius=20
        )

        # ====================================================
        # LOGO
        # ====================================================

        draw_glow_text(
            "E C L I P S E",
            FONT_BIG,
            WIDTH // 2,
            120,
            GOLD
        )

        draw_text(
            "ROGUELITE // ONLINE",
            FONT_TINY,
            WIDTH // 2,
            157,
            (
                135,
                125,
                115
            )
        )

        # ====================================================
        # MODE TITLE
        # ====================================================

        draw_text(
            "SIGN IN"
            if mode == "login"
            else "CREATE ACCOUNT",
            FONT_MED,
            WIDTH // 2,
            215,
            WHITE
        )

        draw_text(
            "ACCESS YOUR ECLIPSE PROFILE"
            if mode == "login"
            else "CREATE YOUR PILOT PROFILE",
            FONT_TINY,
            WIDTH // 2,
            244,
            (
                145,
                135,
                125
            )
        )

        # ====================================================
        # USERNAME
        # ====================================================

        draw_text(
            "PILOT ID",
            FONT_TINY,
            username_box.x,
            username_box.y - 17,
            (
                170,
                155,
                135
            ),
            center=False
        )

        pygame.draw.rect(
            screen,
            (
                18,
                16,
                21
            ),
            username_box,
            border_radius=10
        )

        pygame.draw.rect(
            screen,
            GOLD
            if active_field == "username"
            else (
                60,
                55,
                50
            ),
            username_box,
            2,
            border_radius=10
        )

        draw_text(
            username
            if username
            else "Enter pilot name...",
            FONT_SMALL,
            username_box.x + 18,
            username_box.centery,
            WHITE
            if username
            else (
                90,
                85,
                80
            ),
            center=False
        )

        # ====================================================
        # PASSWORD
        # ====================================================

        draw_text(
            "PASSWORD",
            FONT_TINY,
            password_box.x,
            password_box.y - 17,
            (
                170,
                155,
                135
            ),
            center=False
        )

        pygame.draw.rect(
            screen,
            (
                18,
                16,
                21
            ),
            password_box,
            border_radius=10
        )

        pygame.draw.rect(
            screen,
            GOLD
            if active_field == "password"
            else (
                60,
                55,
                50
            ),
            password_box,
            2,
            border_radius=10
        )

        if password:

            password_display = (
                "•"
                *
                len(password)
            )

        else:

            password_display = (
                "Enter password..."
            )

        draw_text(
            password_display,
            FONT_SMALL,
            password_box.x + 18,
            password_box.centery,
            WHITE
            if password
            else (
                90,
                85,
                80
            ),
            center=False
        )

        # ====================================================
        # ACTION BUTTONS
        # ====================================================

        draw_login_button(
            login_button,
            "LOGIN",
            "F1",
            mode == "login",
            GOLD
        )

        draw_login_button(
            create_button,
            "CREATE",
            "F2",
            mode == "create",
            GOLD
        )

        # ====================================================
        # GUEST
        # ====================================================

        draw_login_button(
            guest_button,
            "PLAY AS GUEST",
            "NO PROFILE REQUIRED  •  F3",
            False,
            CYAN
        )

        # ====================================================
        # MESSAGE
        # ====================================================

        if message_timer > 0:

            error_message = (
                "INCORRECT" in message
                or
                "NOT FOUND" in message
                or
                "EXISTS" in message
                or
                "MUST" in message
                or
                "CORRUPTED" in message
            )

            draw_text(
                message,
                FONT_TINY,
                WIDTH // 2,
                625,
                RED
                if error_message
                else GREEN
            )

        # ====================================================
        # FOOTER
        # ====================================================

        draw_text(
            "TAB  SWITCH FIELD",
            FONT_TINY,
            420,
            675,
            (
                85,
                80,
                75
            ),
            center=False
        )

        draw_text(
            "ENTER  CONFIRM",
            FONT_TINY,
            830,
            675,
            (
                85,
                80,
                75
            ),
            center=False
        )

        pygame.display.flip()


# ============================================================
# SAVE SYSTEM
# ============================================================

SAVE_FOLDER = os.path.join(
    os.path.expanduser("~"),
    ".eclipse_roguelite"
)

SAVE_FILE = os.path.join(
    SAVE_FOLDER,
    "save.json"
)

highest_unlocked_level = 1
score = 0


def save_game():

    global highest_unlocked_level
    global score

    try:

        os.makedirs(
            SAVE_FOLDER,
            exist_ok=True
        )

        data = {
            "highest_unlocked_level": int(
                clamp(
                    highest_unlocked_level,
                    1,
                    MAX_LEVEL
                )
            ),

            "best_score": int(
                max(
                    0,
                    score
                )
            )
        }

        fd, temp_path = tempfile.mkstemp(
            prefix="eclipse_save_",
            suffix=".tmp",
            dir=SAVE_FOLDER
        )

        try:

            with os.fdopen(
                fd,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    data,
                    file,
                    indent=4
                )

            os.replace(
                temp_path,
                SAVE_FILE
            )

        except Exception:

            try:
                os.remove(
                    temp_path
                )
            except OSError:
                pass

    except Exception as error:

        print(
            "SAVE ERROR:",
            error
        )


def load_game():

    global highest_unlocked_level

    highest_unlocked_level = 1

    try:

        if not os.path.exists(
            SAVE_FILE
        ):
            return

        with open(
            SAVE_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if not isinstance(
            data,
            dict
        ):
            return

        highest_unlocked_level = int(
            clamp(
                data.get(
                    "highest_unlocked_level",
                    1
                ),
                1,
                MAX_LEVEL
            )
        )

    except (
        OSError,
        json.JSONDecodeError,
        TypeError,
        ValueError
    ) as error:

        print(
            "SAVE LOAD ERROR:",
            error
        )

        highest_unlocked_level = 1


# ============================================================
# GLOBAL EFFECTS
# ============================================================

particles = []
shockwaves = []
floating_texts = []

MAX_PARTICLES = 750

screen_shake = 0
hit_stop = 0

impact_flash = 0
impact_flash_strength = 0
impact_invert = 0


def add_shake(
    amount
):

    global screen_shake

    screen_shake = max(
        screen_shake,
        amount
    )


def cinematic_impact(
    x,
    y,
    color,
    strength=1,
    white_frame=True
):

    global hit_stop
    global impact_flash
    global impact_flash_strength
    global impact_invert

    strength = max(
        0.1,
        strength
    )

    hit_stop = max(
        hit_stop,
        0.025 * strength
    )

    impact_flash = max(
        impact_flash,
        0.10 * strength
    )

    impact_flash_strength = max(
        impact_flash_strength,
        strength
    )

    if white_frame:

        impact_invert = max(
            impact_invert,
            0.06 * strength
        )

    add_shake(
        4 * strength
    )

    spawn_particles(
        x,
        y,
        color,
        int(
            12 * strength
        ),
        300 * strength
    )

    shockwaves.append(
        Shockwave(
            x,
            y,
            color,
            strength
        )
    )


# ============================================================
# PARTICLES
# ============================================================

class Particle:

    def __init__(
        self,
        x,
        y,
        color,
        speed=200,
        life=None,
        size=None,
        angle=None
    ):

        self.x = x
        self.y = y

        if angle is None:

            angle = random.uniform(
                0,
                math.tau
            )

        self.vx = (
            math.cos(angle)
            *
            speed
        )

        self.vy = (
            math.sin(angle)
            *
            speed
        )

        self.life = (
            life
            if life is not None
            else random.uniform(
                0.25,
                0.8
            )
        )

        self.max_life = max(
            self.life,
            0.001
        )

        self.size = (
            size
            if size is not None
            else random.uniform(
                2,
                5
            )
        )

        self.color = color

        self.gravity = random.uniform(
            -30,
            40
        )

    def update(
        self,
        dt
    ):

        self.x += (
            self.vx
            *
            dt
        )

        self.y += (
            self.vy
            *
            dt
        )

        self.vy += (
            self.gravity
            *
            dt
        )

        self.vx *= (
            0.985
            **
            (dt * 60)
        )

        self.vy *= (
            0.985
            **
            (dt * 60)
        )

        self.life -= dt

        return self.life > 0

    def draw(self):

        alpha = int(
            255
            *
            clamp(
                self.life
                /
                self.max_life,
                0,
                1
            )
        )

        size = max(
            1,
            int(self.size)
        )

        surf = pygame.Surface(
            (
                size * 6,
                size * 6
            ),
            pygame.SRCALPHA
        )

        pygame.draw.circle(
            surf,
            (
                self.color[0],
                self.color[1],
                self.color[2],
                alpha
            ),
            (
                size * 3,
                size * 3
            ),
            size
        )

        screen.blit(
            surf,
            (
                int(
                    self.x
                    -
                    size * 3
                ),
                int(
                    self.y
                    -
                    size * 3
                )
            )
        )


def spawn_particles(
    x,
    y,
    color,
    amount=20,
    speed=200
):

    available = (
        MAX_PARTICLES
        -
        len(particles)
    )

    amount = min(
        int(amount),
        available
    )

    if amount <= 0:
        return

    for _ in range(amount):

        particles.append(
            Particle(
                x,
                y,
                color,
                random.uniform(
                    speed * 0.25,
                    speed
                )
            )
        )


# ============================================================
# SHOCKWAVE
# ============================================================

class Shockwave:

    def __init__(
        self,
        x,
        y,
        color,
        strength=1
    ):

        self.x = x
        self.y = y

        self.radius = 5

        self.speed = (
            500
            *
            max(
                0.2,
                strength
            )
        )

        self.life = 1.0

        self.color = color

        self.width = (
            5
            *
            max(
                0.2,
                strength
            )
        )

    def update(
        self,
        dt
    ):

        self.radius += (
            self.speed
            *
            dt
        )

        self.life -= (
            1.8
            *
            dt
        )

        return self.life > 0

    def draw(self):

        if self.life <= 0:
            return

        pygame.draw.circle(
            screen,
            self.color,
            (
                int(self.x),
                int(self.y)
            ),
            max(
                1,
                int(self.radius)
            ),
            max(
                1,
                int(
                    self.width
                    *
                    self.life
                )
            )
        )


# ============================================================
# FLOATING TEXT
# ============================================================

class FloatingText:

    def __init__(
        self,
        text,
        x,
        y,
        color
    ):

        self.text = str(text)

        self.x = x
        self.y = y

        self.color = color

        self.life = 1.0
        self.max_life = 1.0

    def update(
        self,
        dt
    ):

        self.y -= (
            55
            *
            dt
        )

        self.life -= dt

        return self.life > 0

    def draw(self):

        if self.life <= 0:
            return

        image = FONT_SMALL.render(
            self.text,
            True,
            self.color
        )

        image.set_alpha(
            int(
                255
                *
                clamp(
                    self.life
                    /
                    self.max_life,
                    0,
                    1
                )
            )
        )

        rect = image.get_rect(
            center=(
                int(self.x),
                int(self.y)
            )
        )

        screen.blit(
            image,
            rect
        )


def floating_text(
    text,
    x,
    y,
    color
):

    if len(floating_texts) >= 100:
        floating_texts.pop(0)

    floating_texts.append(
        FloatingText(
            text,
            x,
            y,
            color
        )
    )


# ============================================================
# BACKGROUND
# ============================================================

stars = []

for _ in range(180):

    stars.append([
        random.uniform(
            0,
            WIDTH
        ),

        random.uniform(
            0,
            HEIGHT
        ),

        random.uniform(
            0.3,
            1.7
        ),

        random.uniform(
            0,
            math.tau
        )
    ])


menu_particles = []

for _ in range(110):

    menu_particles.append({

        "x": random.uniform(
            0,
            WIDTH
        ),

        "y": random.uniform(
            0,
            HEIGHT
        ),

        "speed": random.uniform(
            5,
            28
        ),

        "size": random.randint(
            1,
            3
        ),

        "phase": random.uniform(
            0,
            math.tau
        ),

        "drift": random.uniform(
            -15,
            15
        )
    })


def eclipse_glow(
    x,
    y,
    radius,
    color
):

    for extra, alpha in (
        (38, 12),
        (30, 18),
        (22, 25),
        (14, 35)
    ):

        size = radius + extra

        surf = pygame.Surface(
            (
                size * 2,
                size * 2
            ),
            pygame.SRCALPHA
        )

        pygame.draw.circle(
            surf,
            (
                color[0],
                color[1],
                color[2],
                alpha
            ),
            (
                size,
                size
            ),
            size
        )

        screen.blit(
            surf,
            (
                int(
                    x - size
                ),
                int(
                    y - size
                )
            )
        )


def draw_background(
    t,
    dt=1.0 / FPS
):

    screen.fill(
        BLACK
    )

    # ========================================================
    # MOVING SOLAR ECLIPSE
    # ========================================================

    cx = (
        WIDTH // 2
        +
        math.sin(
            t * 0.12
        )
        *
        220
    )

    cy = (
        280
        +
        math.cos(
            t * 0.10
        )
        *
        30
    )

    # Large atmospheric glow

    for radius, alpha in (
        (300, 4),
        (270, 5),
        (230, 8),
        (195, 12),
        (165, 18)
    ):

        surf = pygame.Surface(
            (
                radius * 2,
                radius * 2
            ),
            pygame.SRCALPHA
        )

        pygame.draw.circle(
            surf,
            (
                255,
                150,
                25,
                alpha
            ),
            (
                radius,
                radius
            ),
            radius
        )

        screen.blit(
            surf,
            (
                int(
                    cx - radius
                ),
                int(
                    cy - radius
                )
            )
        )

    # Eclipse outer ring

    pygame.draw.circle(
        screen,
        (
            95,
            38,
            8
        ),
        (
            int(cx),
            int(cy)
        ),
        125,
        3
    )

    pygame.draw.circle(
        screen,
        (
            45,
            20,
            7
        ),
        (
            int(cx),
            int(cy)
        ),
        116
    )

    pygame.draw.circle(
        screen,
        (
            1,
            1,
            2
        ),
        (
            int(cx),
            int(cy)
        ),
        112
    )

    # Eclipse arcs

    rect = pygame.Rect(
        int(cx - 145),
        int(cy - 145),
        290,
        290
    )

    pygame.draw.arc(
        screen,
        GOLD,
        rect,
        -0.7,
        1.3,
        3
    )

    pygame.draw.arc(
        screen,
        ORANGE,
        rect,
        2.4,
        4.9,
        2
    )

    # ========================================================
    # STARS
    # ========================================================

    for star in stars:

        star[1] += (
            star[2]
            *
            7
            *
            dt
        )

        if star[1] > HEIGHT:

            star[1] = -5

            star[0] = random.uniform(
                0,
                WIDTH
            )

        brightness = int(
            50
            +
            100
            *
            math.sin(
                t * 2
                +
                star[3]
            )
        )

        brightness = clamp(
            brightness,
            25,
            180
        )

        pygame.draw.circle(
            screen,
            (
                brightness,
                brightness,
                brightness
            ),
            (
                int(star[0]),
                int(star[1])
            ),
            max(
                1,
                int(star[2])
            )
        )

    # ========================================================
    # PERSPECTIVE HORIZON
    # ========================================================

    horizon = 510

    for i in range(16):

        y = (
            horizon
            +
            i * i * 1.35
        )

        pygame.draw.line(
            screen,
            (
                22,
                14,
                8
            ),
            (
                0,
                int(y)
            ),
            (
                WIDTH,
                int(y)
            ),
            1
        )

    # ========================================================
    # PERSPECTIVE GRID
    # ========================================================

    for x in range(
        -WIDTH,
        WIDTH * 2,
        100
    ):

        pygame.draw.line(
            screen,
            (
                20,
                12,
                7
            ),
            (
                WIDTH // 2 + x,
                horizon
            ),
            (
                WIDTH // 2 + x * 2,
                HEIGHT
            ),
            1
        )


def draw_menu_effects(
    t,
    dt=1.0 / FPS
):

    for p in menu_particles:

        p["y"] -= (
            p["speed"]
            *
            dt
        )

        p["x"] += (
            math.sin(
                t * 0.5
                +
                p["phase"]
            )
            *
            p["drift"]
            *
            dt
        )

        if p["y"] < -10:

            p["y"] = HEIGHT + 10

            p["x"] = random.uniform(
                0,
                WIDTH
            )

        pulse = (
            0.5
            +
            0.5
            *
            math.sin(
                t * 2
                +
                p["phase"]
            )
        )

        alpha = int(
            40
            +
            pulse * 110
        )

        size = p["size"]

        surf = pygame.Surface(
            (
                size * 4,
                size * 4
            ),
            pygame.SRCALPHA
        )

        pygame.draw.circle(
            surf,
            (
                255,
                170,
                50,
                alpha
            ),
            (
                size * 2,
                size * 2
            ),
            size
        )

        screen.blit(
            surf,
            (
                int(
                    p["x"]
                    -
                    size * 2
                ),
                int(
                    p["y"]
                    -
                    size * 2
                )
            )
        )
    cx = WIDTH // 2
    cy = 295

    for radius, alpha, width, speed in (
        (210, 30, 1, .25),
        (245, 45, 2, -.18),
        (285, 22, 1, .12),
        (330, 18, 1, -.08)
    ):

        surf = pygame.Surface(
            (
                WIDTH,
                HEIGHT
            ),
            pygame.SRCALPHA
        )

        rect = pygame.Rect(
            cx - radius,
            cy - radius,
            radius * 2,
            radius * 2
        )

        start = t * speed

        pygame.draw.arc(
            surf,
            (
                255,
                130,
                20,
                alpha
            ),
            rect,
            start,
            start + 2.5,
            width
        )

        pygame.draw.arc(
            surf,
            (
                255,
                220,
                80,
                alpha
            ),
            rect,
            start + 3.4,
            start + 5.2,
            width
        )

        screen.blit(
            surf,
            (0, 0)
        )

    for y in range(
        20,
        HEIGHT,
        6
    ):
        pygame.draw.line(
            screen,
            (20, 12, 6),
            (
                0,
                y
            ),
            (
                WIDTH,
                y
            ),
            1
        )


# ============================================================
# PLAYER
# ============================================================

class Player:

    def __init__(self):

        self.x = WIDTH // 2
        self.y = HEIGHT - 120

        self.radius = 18
        self.speed = 340

        self.hp = 100
        self.max_hp = 100

        self.energy = 100
        self.max_energy = 100

        self.cooldown = 0

        self.dash_cooldown = 0
        self.dash_timer = 0
        self.invincible = 0

        self.angle = 0
        self.trail = []

        # Weapon
        self.damage = 1
        self.fire_rate = .11
        self.extra_shots = 0
        self.piercing = 0
        self.explosive = 0
        self.crit_chance = 0
        self.crit_multiplier = 2

        # Mobility
        self.speed_multiplier = 1
        self.dash_cost = 30
        self.dash_power = 3.5

        # Defense
        self.shield = 0
        self.max_shield = 0
        self.regen = 0

        # Utility
        self.magnet = 1
        self.drone_count = 0

        # NEW
        self.wrath = 0
        self.max_wrath = 100
        self.nova_cooldown = 0

    def reset_stats(self):

        self.hp = self.max_hp
        self.energy = self.max_energy

        self.cooldown = 0
        self.dash_cooldown = 0
        self.dash_timer = 0
        self.invincible = 0

        self.wrath = 0
        self.nova_cooldown = 0

        self.trail.clear()

    def reset_upgrades(self):

        self.max_hp = 100
        self.hp = 100

        self.max_energy = 100
        self.energy = 100

        self.damage = 1
        self.fire_rate = .11
        self.extra_shots = 0

        self.piercing = 0
        self.explosive = 0
        self.crit_chance = 0
        self.crit_multiplier = 2

        self.speed_multiplier = 1

        self.dash_cost = 30
        self.dash_power = 3.5

        self.shield = 0
        self.max_shield = 0
        self.regen = 0

        self.magnet = 1
        self.drone_count = 0

        self.wrath = 0
        self.max_wrath = 100
        self.nova_cooldown = 0

    def update(self, dt):

        keys = pygame.key.get_pressed()

        dx = 0
        dy = 0

        if keys[pygame.K_a]:
            dx -= 1

        if keys[pygame.K_d]:
            dx += 1

        if keys[pygame.K_w]:
            dy -= 1

        if keys[pygame.K_s]:
            dy += 1

        length = math.hypot(
            dx,
            dy
        )

        if length:
            dx /= length
            dy /= length

        speed = (
            self.speed *
            self.speed_multiplier
        )

        if self.dash_timer > 0:

            speed *= self.dash_power

            self.dash_timer -= dt

            if random.random() < .8:

                spawn_particles(
                    self.x,
                    self.y,
                    GOLD,
                    1,
                    80
                )

        self.x += (
            dx *
            speed *
            dt
        )

        self.y += (
            dy *
            speed *
            dt
        )

        self.x = clamp(
            self.x,
            45,
            WIDTH - 45
        )

        self.y = clamp(
            self.y,
            120,
            HEIGHT - 45
        )

        self.angle += dt * 4

        self.cooldown = max(
            0,
            self.cooldown - dt
        )

        self.dash_cooldown = max(
            0,
            self.dash_cooldown - dt
        )

        self.invincible = max(
            0,
            self.invincible - dt
        )

        self.nova_cooldown = max(
            0,
            self.nova_cooldown - dt
        )

        self.energy = min(
            self.max_energy,
            self.energy +
            12 * dt
        )

        if self.regen > 0:

            self.hp = min(
                self.max_hp,
                self.hp +
                self.regen * dt
            )

        # Magnetise solar orbs.
        for orb in solar_orbs:

            d = distance(
                self.x,
                self.y,
                orb.x,
                orb.y
            )

            if d < 150 * self.magnet:

                angle = math.atan2(
                    self.y - orb.y,
                    self.x - orb.x
                )

                pull = (
                    350 *
                    self.magnet
                )

                orb.x += (
                    math.cos(angle) *
                    pull *
                    dt
                )

                orb.y += (
                    math.sin(angle) *
                    pull *
                    dt
                )

        self.trail.append(
            (
                self.x,
                self.y
            )
        )

        if len(self.trail) > 18:
            self.trail.pop(0)

    def shoot(self):

        if self.cooldown > 0:
            return

        mx, my = pygame.mouse.get_pos()

        base_angle = math.atan2(
            my - self.y,
            mx - self.x
        )

        total = (
            1 +
            self.extra_shots
        )

        for i in range(total):

            if total == 1:
                angle = base_angle

            else:

                spread = .16

                angle = (
                    base_angle +
                    (
                        i -
                        (total - 1) / 2
                    ) *
                    spread
                )

            tx = (
                self.x +
                math.cos(angle) *
                1000
            )

            ty = (
                self.y +
                math.sin(angle) *
                1000
            )

            damage = self.damage
            critical = False

            if random.random() < self.crit_chance:

                damage *= (
                    self.crit_multiplier
                )

                critical = True

            bullets.append(
                Bullet(
                    self.x,
                    self.y,
                    tx,
                    ty,
                    damage,
                    self.piercing,
                    self.explosive,
                    critical
                )
            )

        self.cooldown = self.fire_rate

        spawn_particles(
            self.x,
            self.y,
            SOLAR,
            5,
            100
        )

    def dash(self):

        if (
            self.dash_cooldown <= 0
            and
            self.energy >= self.dash_cost
        ):

            keys = pygame.key.get_pressed()

            dx = 0
            dy = 0

            if keys[pygame.K_a]:
                dx -= 1

            if keys[pygame.K_d]:
                dx += 1

            if keys[pygame.K_w]:
                dy -= 1

            if keys[pygame.K_s]:
                dy += 1

            if dx == 0 and dy == 0:
                dy = -1

            length = math.hypot(
                dx,
                dy
            )

            if length:
                dx /= length
                dy /= length

            self.dash_timer = .23
            self.dash_cooldown = .9
            self.energy -= self.dash_cost
            self.invincible = .42

            self.x += dx * 80
            self.y += dy * 80

            self.x = clamp(
                self.x,
                45,
                WIDTH - 45
            )

            self.y = clamp(
                self.y,
                120,
                HEIGHT - 45
            )

            cinematic_impact(
                self.x,
                self.y,
                GOLD,
                .8,
                False
            )

    def solar_nova(self):

        if (
            self.wrath < self.max_wrath
            or
            self.nova_cooldown > 0
        ):
            return

        self.wrath = 0
        self.nova_cooldown = 2

        floating_text(
            "SOLAR NOVA!",
            self.x,
            self.y - 60,
            SOLAR
        )

        cinematic_impact(
            self.x,
            self.y,
            GOLD,
            5
        )

        spawn_particles(
            self.x,
            self.y,
            GOLD,
            100,
            650
        )

        # Destroy enemy projectiles.
        enemy_projectiles.clear()

        # Damage enemies.
        for enemy in enemies[:]:

            d = distance(
                self.x,
                self.y,
                enemy.x,
                enemy.y
            )

            if d < 400:

                damage = (
                    self.damage *
                    4
                )

                if enemy.hit(damage):

                    if enemy in enemies:
                        enemies.remove(enemy)

        # Damage boss.
        if boss is not None:

            if boss.invincible <= 0:

                boss.hit(
                    self.damage * 8
                )

        add_shake(12)

    def damage_player(self, amount):

        if self.invincible > 0:
            return

        if self.shield > 0:

            absorbed = min(
                self.shield,
                amount
            )

            self.shield -= absorbed
            amount -= absorbed

            floating_text(
                f"SHIELD -{int(absorbed)}",
                self.x,
                self.y - 35,
                BLUE
            )

        if amount > 0:
            self.hp -= amount

        self.invincible = .75

        cinematic_impact(
            self.x,
            self.y,
            RED,
            1.3
        )

    def draw(self):

        for i, pos in enumerate(
            self.trail
        ):

            alpha = int(
                100 *
                i /
                max(
                    1,
                    len(self.trail)
                )
            )

            surf = pygame.Surface(
                (
                    50,
                    50
                ),
                pygame.SRCALPHA
            )

            pygame.draw.circle(
                surf,
                (
                    255,
                    170,
                    30,
                    alpha
                ),
                (
                    25,
                    25
                ),
                3 + i // 5
            )

            screen.blit(
                surf,
                (
                    int(pos[0] - 25),
                    int(pos[1] - 25)
                )
            )

        if (
            self.invincible > 0
            and
            int(
                self.invincible * 18
            ) % 2 == 0
        ):
            return

        if self.shield > 0:

            pygame.draw.circle(
                screen,
                BLUE,
                (
                    int(self.x),
                    int(self.y)
                ),
                30,
                2
            )

        eclipse_glow(
            self.x,
            self.y,
            28,
            GOLD
        )

        for i in range(16):

            angle = (
                self.angle +
                i * math.tau / 16
            )

            length = (
                30 +
                math.sin(
                    self.angle * 2 +
                    i
                ) * 7
            )

            pygame.draw.line(
                screen,
                GOLD,
                (
                    int(
                        self.x +
                        math.cos(angle) *
                        22
                    ),
                    int(
                        self.y +
                        math.sin(angle) *
                        22
                    )
                ),
                (
                    int(
                        self.x +
                        math.cos(angle) *
                        length
                    ),
                    int(
                        self.y +
                        math.sin(angle) *
                        length
                    )
                ),
                2
            )

        pygame.draw.circle(
            screen,
            BLACK,
            (
                int(self.x),
                int(self.y)
            ),
            18
        )

        pygame.draw.circle(
            screen,
            (12, 10, 6),
            (
                int(self.x),
                int(self.y)
            ),
            10
        )

        rect = pygame.Rect(
            int(self.x - 27),
            int(self.y - 27),
            54,
            54
        )

        pygame.draw.arc(
            screen,
            SOLAR,
            rect,
            -.9,
            2.0,
            4
        )

        pygame.draw.arc(
            screen,
            ORANGE,
            rect,
            2.4,
            5.4,
            2
        )


player = Player()


# ============================================================
# SOLAR ORBS
# ============================================================

solar_orbs = []


class SolarOrb:

    def __init__(
        self,
        x,
        y,
        value=8
    ):
        self.x = x
        self.y = y
        self.value = value

        self.life = 10
        self.angle = random.random() * math.tau

    def update(self, dt):

        self.life -= dt
        self.angle += dt * 4

        if distance(
            self.x,
            self.y,
            player.x,
            player.y
        ) < 28:

            player.wrath = min(
                player.max_wrath,
                player.wrath +
                self.value
            )

            floating_text(
                f"+{self.value} WRATH",
                self.x,
                self.y - 15,
                GOLD
            )

            spawn_particles(
                self.x,
                self.y,
                GOLD,
                8,
                100
            )

            return False

        return self.life > 0

    def draw(self):

        pulse = (
            math.sin(
                self.angle * 2
            ) * 3
        )

        eclipse_glow(
            self.x,
            self.y,
            8,
            GOLD
        )

        pygame.draw.circle(
            screen,
            GOLD,
            (
                int(self.x),
                int(self.y)
            ),
            int(6 + pulse)
        )

        pygame.draw.circle(
            screen,
            WHITE,
            (
                int(self.x),
                int(self.y)
            ),
            2
        )


# ============================================================
# DRONES
# ============================================================

class Drone:

    def __init__(self, index):

        self.index = index

        self.angle = (
            index *
            math.tau /
            max(
                1,
                player.drone_count
            )
        )

    def update(self, dt):

        self.angle += dt * 2.2

        if random.random() < .025:
            self.shoot()

    def shoot(self):

        enemies_alive = [
            e for e in enemies
            if e.hp > 0
        ]

        if not enemies_alive:
            return

        target = min(
            enemies_alive,
            key=lambda e: distance(
                self.x(),
                self.y(),
                e.x,
                e.y
            )
        )

        bullets.append(
            Bullet(
                self.x(),
                self.y(),
                target.x,
                target.y,
                max(
                    1,
                    player.damage // 2
                ),
                0,
                0,
                False
            )
        )

    def x(self):

        radius = 55

        return (
            player.x +
            math.cos(self.angle) *
            radius
        )

    def y(self):

        radius = 55

        return (
            player.y +
            math.sin(self.angle) *
            radius
        )

    def draw(self):

        x = self.x()
        y = self.y()

        eclipse_glow(
            x,
            y,
            10,
            CYAN
        )

        pygame.draw.circle(
            screen,
            BLACK,
            (
                int(x),
                int(y)
            ),
            8
        )

        pygame.draw.circle(
            screen,
            CYAN,
            (
                int(x),
                int(y)
            ),
            7,
            2
        )

        pygame.draw.circle(
            screen,
            WHITE,
            (
                int(x),
                int(y)
            ),
            2
        )


# ============================================================
# BULLETS
# ============================================================

bullets = []


class Bullet:

    def __init__(
        self,
        x,
        y,
        tx,
        ty,
        damage=1,
        piercing=0,
        explosive=0,
        critical=False
    ):

        self.x = x
        self.y = y

        dx = tx - x
        dy = ty - y

        length = math.hypot(
            dx,
            dy
        )

        if length == 0:
            length = 1

        speed = 900

        self.vx = (
            dx /
            length *
            speed
        )

        self.vy = (
            dy /
            length *
            speed
        )

        self.damage = damage
        self.piercing = piercing
        self.explosive = explosive
        self.critical = critical

        self.life = 1.2
        self.hit_targets = []

    def update(self, dt):

        self.x += (
            self.vx *
            dt
        )

        self.y += (
            self.vy *
            dt
        )

        self.life -= dt

        if random.random() < .8:

            spawn_particles(
                self.x,
                self.y,
                SOLAR,
                1,
                25
            )

        return (
            self.life > 0
            and
            -50 < self.x < WIDTH + 50
            and
            -50 < self.y < HEIGHT + 50
        )

    def draw(self):

        eclipse_glow(
            self.x,
            self.y,
            5 if not self.critical else 8,
            GOLD if not self.critical else WHITE
        )

        pygame.draw.circle(
            screen,
            WHITE,
            (
                int(self.x),
                int(self.y)
            ),
            4 if self.critical else 3
        )


# ============================================================
# ENEMY PROJECTILES
# ============================================================

enemy_projectiles = []


class EnemyProjectile:

    def __init__(
        self,
        x,
        y,
        tx,
        ty,
        speed=280,
        damage=8,
        color=ORANGE,
        size=7,
        homing=0
    ):

        self.x = x
        self.y = y

        dx = tx - x
        dy = ty - y

        length = math.hypot(
            dx,
            dy
        )

        if length == 0:
            length = 1

        self.vx = (
            dx /
            length *
            speed
        )

        self.vy = (
            dy /
            length *
            speed
        )

        self.speed = speed
        self.damage = damage
        self.color = color
        self.size = size
        self.homing = homing

        self.life = 5

    def update(self, dt):

        if self.homing:

            dx = (
                player.x -
                self.x
            )

            dy = (
                player.y -
                self.y
            )

            target_angle = math.atan2(
                dy,
                dx
            )

            current_angle = math.atan2(
                self.vy,
                self.vx
            )

            difference = (
                (
                    target_angle -
                    current_angle +
                    math.pi
                )
                % math.tau
                - math.pi
            )

            current_angle += clamp(
                difference,
                -.55 * dt,
                .55 * dt
            )

            self.vx = (
                math.cos(
                    current_angle
                ) *
                self.speed
            )

            self.vy = (
                math.sin(
                    current_angle
                ) *
                self.speed
            )

        self.x += (
            self.vx *
            dt
        )

        self.y += (
            self.vy *
            dt
        )

        self.life -= dt

        if distance(
            self.x,
            self.y,
            player.x,
            player.y
        ) < (
            self.size +
            player.radius
        ):

            player.damage_player(
                self.damage
            )

            cinematic_impact(
                self.x,
                self.y,
                self.color,
                .45
            )

            return False

        return (
            self.life > 0
            and
            -100 < self.x < WIDTH + 100
            and
            -100 < self.y < HEIGHT + 100
        )

    def draw(self):

        eclipse_glow(
            self.x,
            self.y,
            self.size + 4,
            self.color
        )

        pygame.draw.circle(
            screen,
            self.color,
            (
                int(self.x),
                int(self.y)
            ),
            self.size
        )

        pygame.draw.circle(
            screen,
            WHITE,
            (
                int(self.x),
                int(self.y)
            ),
            max(
                2,
                self.size // 2
            )
        )


# ============================================================
# ENEMIES
# ============================================================

enemies = []


class Enemy:

    def __init__(
        self,
        level,
        kind=None,
        elite=False
    ):

        side = random.randint(
            0,
            3
        )

        if side == 0:

            self.x = random.randint(
                60,
                WIDTH - 60
            )

            self.y = -60

        elif side == 1:

            self.x = WIDTH + 60

            self.y = random.randint(
                150,
                HEIGHT - 60
            )

        elif side == 2:

            self.x = random.randint(
                60,
                WIDTH - 60
            )

            self.y = HEIGHT + 60

        else:

            self.x = -60

            self.y = random.randint(
                150,
                HEIGHT - 60
            )

        self.level = level
        self.elite = elite

        if kind is None:
            kind = self.choose_kind(
                level
            )

        self.kind = kind

        self.angle = random.uniform(
            0,
            math.tau
        )

        self.wave = random.uniform(
            0,
            math.tau
        )

        self.attack_timer = random.uniform(
            1,
            2
        )

        self.hit_flash = 0

        self.configure()

        if self.elite:

            self.hp *= 2.2
            self.radius += 7
            self.speed *= .88
            self.score *= 3
            self.color = WHITE

    def choose_kind(self, level):

        roll = random.random()

        if level <= 2:
            return "NORMAL"

        if level <= 4:

            if roll < .22:
                return "CHARGER"

            return "NORMAL"

        if level <= 7:

            if roll < .16:
                return "SHOOTER"

            if roll < .34:
                return "CHARGER"

            return "NORMAL"

        if level <= 11:

            if roll < .15:
                return "SHOOTER"

            if roll < .30:
                return "ORBITER"

            if roll < .43:
                return "SPLITTER"

            if roll < .54:
                return "TANK"

            return "NORMAL"

        if roll < .15:
            return "SHOOTER"

        if roll < .30:
            return "ORBITER"

        if roll < .43:
            return "SPLITTER"

        if roll < .54:
            return "TANK"

        if roll < .67:
            return "CHARGER"

        return "NORMAL"

    def configure(self):

        level = self.level

        if self.kind == "NORMAL":

            self.radius = 18
            self.speed = 90 + level * 2.5
            self.hp = 2 + level // 4
            self.color = SOLAR
            self.score = 100

        elif self.kind == "CHARGER":

            self.radius = 16
            self.speed = 112 + level * 3
            self.hp = 3 + level // 4
            self.color = RED
            self.score = 150

        elif self.kind == "SHOOTER":

            self.radius = 19
            self.speed = 65 + level * 1.5
            self.hp = 4 + level // 4
            self.color = PURPLE
            self.score = 220

        elif self.kind == "ORBITER":

            self.radius = 17
            self.speed = 100 + level * 1.8
            self.hp = 4 + level // 4
            self.color = BLUE
            self.score = 240

        elif self.kind == "SPLITTER":

            self.radius = 23
            self.speed = 72 + level * 1.5
            self.hp = 6 + level // 2
            self.color = GREEN
            self.score = 300

        elif self.kind == "TANK":

            self.radius = 30
            self.speed = 45 + level * .8
            self.hp = 10 + level
            self.color = ORANGE
            self.score = 400

    def update(self, dt):

        self.attack_timer -= dt

        self.hit_flash = max(
            0,
            self.hit_flash - dt
        )

        self.wave += dt * 4

        dx = (
            player.x -
            self.x
        )

        dy = (
            player.y -
            self.y
        )

        length = math.hypot(
            dx,
            dy
        )

        if length == 0:
            length = 1

        dx /= length
        dy /= length

        if self.kind == "NORMAL":

            # Slight weaving keeps normal enemies
            # from becoming boring straight-line targets.
            side_x = -dy
            side_y = dx

            weave = (
                math.sin(self.wave) *
                0.25
            )

            vx = (
                dx +
                side_x * weave
            ) * self.speed

            vy = (
                dy +
                side_y * weave
            ) * self.speed

        elif self.kind == "CHARGER":

            if self.attack_timer <= 0:

                self.attack_timer = random.uniform(
                    1.8,
                    2.8
                )

                self.speed *= 2.0

                floating_text(
                    "CHARGING!",
                    self.x,
                    self.y - 25,
                    RED
                )

            else:

                self.speed = max(
                    112 + self.level * 3,
                    self.speed * .96
                )

            vx = dx * self.speed
            vy = dy * self.speed

        elif self.kind == "SHOOTER":

            desired = 330

            if length > desired + 50:

                vx = dx * self.speed
                vy = dy * self.speed

            elif length < desired - 50:

                vx = -dx * self.speed
                vy = -dy * self.speed

            else:

                vx = -dy * self.speed * .65
                vy = dx * self.speed * .65

            if self.attack_timer <= 0:

                self.attack_timer = 1.8

                enemy_projectiles.append(
                    EnemyProjectile(
                        self.x,
                        self.y,
                        player.x,
                        player.y,
                        235 + self.level * 4,
                        5 + self.level // 4,
                        PURPLE,
                        7
                    )
                )

        elif self.kind == "ORBITER":

            vx = (
                dx * self.speed * .25
                -
                dy * self.speed
            )

            vy = (
                dy * self.speed * .25
                +
                dx * self.speed
            )

        elif self.kind == "SPLITTER":

            vx = dx * self.speed
            vy = dy * self.speed

        else:

            vx = dx * self.speed
            vy = dy * self.speed

        self.x += vx * dt
        self.y += vy * dt

        self.angle += dt * 3

        if self.kind == "SHOOTER":

            self.x += (
                math.sin(self.wave) *
                15 *
                dt
            )

        if distance(
            self.x,
            self.y,
            player.x,
            player.y
        ) < (
            self.radius +
            player.radius
        ):

            damage = 8

            if self.kind == "CHARGER":
                damage = 14

            elif self.kind == "TANK":
                damage = 17

            elif self.kind == "SPLITTER":
                damage = 11

            player.damage_player(
                damage
            )

            cinematic_impact(
                self.x,
                self.y,
                self.color,
                .65
            )

            return False

        return True

    def hit(self, damage):

        self.hp -= damage
        self.hit_flash = .11

        if damage > player.damage:

            floating_text(
                "CRITICAL!",
                self.x,
                self.y - 30,
                WHITE
            )

        else:

            floating_text(
                f"-{int(damage)}",
                self.x,
                self.y - 20,
                WHITE
            )

        cinematic_impact(
            self.x,
            self.y,
            self.color,
            .3
        )

        if self.hp <= 0:

            self.destroy()

            return True

        return False

    def destroy(self):

        global score
        global combo
        global combo_timer

        score += (
            self.score +
            combo * 20
        )

        combo += 1

        combo_timer = 2.5

        # Wrath reward.
        orb_count = (
            3 if self.elite
            else 1
        )

        for _ in range(orb_count):

            solar_orbs.append(
                SolarOrb(
                    self.x +
                    random.randint(
                        -15,
                        15
                    ),
                    self.y +
                    random.randint(
                        -15,
                        15
                    ),
                    10 if self.elite else 7
                )
            )

        if self.elite:

            score += 1000

            floating_text(
                "ELITE DESTROYED!",
                self.x,
                self.y - 40,
                GOLD
            )

            spawn_particles(
                self.x,
                self.y,
                GOLD,
                60,
                500
            )

        else:

            spawn_particles(
                self.x,
                self.y,
                self.color,
                20,
                320
            )

        cinematic_impact(
            self.x,
            self.y,
            self.color,
            1.0 if self.elite else .55
        )

        # Splitter creates smaller enemies.
        if (
            self.kind == "SPLITTER"
            and
            self.level >= 6
        ):

            for _ in range(2):

                enemies.append(
                    Enemy(
                        max(
                            1,
                            self.level - 2
                        ),
                        "NORMAL",
                        False
                    )
                )

    def draw(self):

        color = (
            WHITE
            if self.hit_flash > 0
            else self.color
        )

        if self.elite:

            eclipse_glow(
                self.x,
                self.y,
                self.radius + 12,
                GOLD
            )

            pygame.draw.circle(
                screen,
                GOLD,
                (
                    int(self.x),
                    int(self.y)
                ),
                self.radius + 9,
                2
            )

        eclipse_glow(
            self.x,
            self.y,
            self.radius,
            color
        )

        if self.kind == "TANK":

            pygame.draw.circle(
                screen,
                BLACK,
                (
                    int(self.x),
                    int(self.y)
                ),
                self.radius
            )

            pygame.draw.circle(
                screen,
                color,
                (
                    int(self.x),
                    int(self.y)
                ),
                self.radius,
                4
            )

            for i in range(4):

                angle = (
                    self.angle +
                    i * math.pi / 2
                )

                pygame.draw.line(
                    screen,
                    color,
                    (
                        int(
                            self.x +
                            math.cos(angle) * 10
                        ),
                        int(
                            self.y +
                            math.sin(angle) * 10
                        )
                    ),
                    (
                        int(
                            self.x +
                            math.cos(angle) * 28
                        ),
                        int(
                            self.y +
                            math.sin(angle) * 28
                        )
                    ),
                    4
                )

        elif self.kind == "SHOOTER":

            pygame.draw.circle(
                screen,
                BLACK,
                (
                    int(self.x),
                    int(self.y)
                ),
                self.radius
            )

            pygame.draw.circle(
                screen,
                color,
                (
                    int(self.x),
                    int(self.y)
                ),
                self.radius,
                3
            )

            pygame.draw.circle(
                screen,
                color,
                (
                    int(self.x),
                    int(self.y)
                ),
                5
            )

        elif self.kind == "ORBITER":

            pygame.draw.circle(
                screen,
                BLACK,
                (
                    int(self.x),
                    int(self.y)
                ),
                self.radius
            )

            for i in range(3):

                angle = (
                    self.angle +
                    i * math.tau / 3
                )

                pygame.draw.circle(
                    screen,
                    color,
                    (
                        int(
                            self.x +
                            math.cos(angle) *
                            15
                        ),
                        int(
                            self.y +
                            math.sin(angle) *
                            15
                        )
                    ),
                    4
                )

        elif self.kind == "SPLITTER":

            points = []

            for i in range(6):

                angle = (
                    self.angle +
                    i * math.tau / 6
                )

                points.append(
                    (
                        int(
                            self.x +
                            math.cos(angle) *
                            self.radius
                        ),
                        int(
                            self.y +
                            math.sin(angle) *
                            self.radius
                        )
                    )
                )

            pygame.draw.polygon(
                screen,
                color,
                points,
                3
            )

            pygame.draw.circle(
                screen,
                color,
                (
                    int(self.x),
                    int(self.y)
                ),
                5
            )

        else:

            pygame.draw.circle(
                screen,
                color,
                (
                    int(self.x),
                    int(self.y)
                ),
                self.radius
            )

            pygame.draw.circle(
                screen,
                WHITE,
                (
                    int(self.x),
                    int(self.y)
                ),
                max(
                    3,
                    self.radius // 3
                )
            )

        if self.elite:

            pygame.draw.arc(
                screen,
                GOLD,
                pygame.Rect(
                    int(
                        self.x -
                        self.radius -
                        10
                    ),
                    int(
                        self.y -
                        self.radius -
                        10
                    ),
                    (
                        self.radius +
                        10
                    ) * 2,
                    (
                        self.radius +
                        10
                    ) * 2
                ),
                self.angle,
                self.angle + 4,
                3
            )


# ============================================================
# BOSS
# ============================================================

boss = None


class Boss:

    def __init__(self, level):

        self.level = level

        self.x = WIDTH // 2
        self.y = 165

        self.timer = 0
        self.angle = 0

        self.phase = 1

        self.hit_flash = 0

        self.phase_transition = 1.5

        self.attack_timer = 1.8
        self.special_timer = 5

        self.telegraph_timer = 0
        self.telegraph_type = None

        self.rage_timer = 0

        # ----------------------------------------------------
        # LEVEL 5
        # ----------------------------------------------------

        if level == 5:

            self.radius = 62

            self.max_hp = 800

            self.name = "HELIOS"

            self.color = GOLD

            self.kind = "HELIOS"

        # ----------------------------------------------------
        # LEVEL 10
        # ----------------------------------------------------

        elif level == 10:

            self.radius = 76

            self.max_hp = 2000

            self.name = "APPOLO"

            self.color = SOLAR

            self.kind = "APPOLO"

        # ----------------------------------------------------
        # LEVEL 15
        # ----------------------------------------------------

        else:

            self.radius = 105

            self.max_hp = 5000

            self.name = ""

            self.color = RED

            self.kind = "WRATH"

        self.hp = self.max_hp

        self.invincible = 1.5

    def update(self, dt):

        self.timer += dt

        self.angle += (
            dt *
            (
                1.0 +
                self.phase * .5
            )
        )

        self.hit_flash = max(
            0,
            self.hit_flash - dt
        )

        self.invincible = max(
            0,
            self.invincible - dt
        )

        self.telegraph_timer = max(
            0,
            self.telegraph_timer - dt
        )

        self.rage_timer = max(
            0,
            self.rage_timer - dt
        )

        ratio = (
            self.hp /
            self.max_hp
        )

        new_phase = 1

        if ratio <= .66:
            new_phase = 2

        if ratio <= .33:
            new_phase = 3

        if new_phase > self.phase:

            self.phase = new_phase

            self.phase_transition = 1.7

            self.invincible = 1.7

            self.attack_timer = 1.4

            self.special_timer = 3

            enemy_projectiles.clear()

            cinematic_impact(
                self.x,
                self.y,
                self.color,
                2.5
            )

            spawn_particles(
                self.x,
                self.y,
                GOLD,
                100,
                650
            )

            floating_text(
                f"PHASE {self.phase}",
                self.x,
                self.y - 130,
                self.color
            )

        if self.phase_transition > 0:

            self.phase_transition -= dt

            return

        # ----------------------------------------------------
        # MOVEMENT
        # ----------------------------------------------------

        if self.kind == "WRAITH":

            self.x = (
                WIDTH // 2 +
                math.sin(
                    self.timer * .65
                ) * 310
            )

            self.y = (
                170 +
                math.sin(
                    self.timer * 1.1
                ) * 30
            )

        elif self.kind == "APOLLO":

            # Apollo moves in a wide divine orbit.
            self.x = (
                WIDTH // 2 +
                math.sin(
                    self.timer *
                    (
                        .55 +
                        self.phase * .15
                    )
                ) * 390
            )

            self.y = (
                165 +
                math.cos(
                    self.timer * .9
                ) * 50
            )

        else:

            # Final boss gradually becomes more aggressive.
            self.x = (
                WIDTH // 2 +
                math.sin(
                    self.timer *
                    (
                        .55 +
                        self.phase * .22
                    )
                ) * 420
            )

            self.y = (
                165 +
                math.sin(
                    self.timer * 1.2
                ) * 65
            )

        # ----------------------------------------------------
        # ATTACKS
        # ----------------------------------------------------

        self.attack_timer -= dt
        self.special_timer -= dt

        if self.attack_timer <= 0:
            self.fire_attack()

        if self.special_timer <= 0:
            self.special_attack()

        # ----------------------------------------------------
        # COLLISION
        # ----------------------------------------------------

        if distance(
            self.x,
            self.y,
            player.x,
            player.y
        ) < (
            self.radius +
            player.radius
        ):

            if self.kind == "WRATH":
                player.damage_player(18)

            elif self.kind == "APOLLO":
                player.damage_player(12)

            else:
                player.damage_player(10)

    def fire_attack(self):

        base_angle = math.atan2(
            player.y - self.y,
            player.x - self.x
        )

        # ====================================================
        # HELIOS
        # ====================================================

        if self.kind == "HELIOS":

            self.attack_timer = (
                1.25 -
                self.phase * .08
            )

            # Only 1-3 projectiles.
            count = (
                1
                if self.phase == 1
                else 3
            )

            for i in range(count):

                offset = (
                    (
                        i -
                        (count - 1) / 2
                    ) *
                    .20
                )

                angle = (
                    base_angle +
                    offset
                )

                enemy_projectiles.append(
                    EnemyProjectile(
                        self.x,
                        self.y,
                        self.x +
                        math.cos(angle) *
                        1000,
                        self.y +
                        math.sin(angle) *
                        1000,
                        245,
                        5,
                        ORANGE,
                        7
                    )
                )

        # ====================================================
        # APOLLO
        # ====================================================

        elif self.kind == "APOLLO":

            self.attack_timer = (
                1.25 -
                self.phase * .12
            )

            # Apollo fires a fan of divine arrows.
            count = (
                3
                if self.phase == 1
                else 5
            )

            for i in range(count):

                offset = (
                    i -
                    (count - 1) / 2
                ) * .15

                angle = (
                    base_angle +
                    offset
                )

                enemy_projectiles.append(
                    EnemyProjectile(
                        self.x,
                        self.y,
                        self.x +
                        math.cos(angle) *
                        1000,
                        self.y +
                        math.sin(angle) *
                        1000,
                        275,
                        6,
                        GOLD,
                        7
                    )
                )

        # ====================================================
        # SUN GOD OF WRATH
        # ====================================================

        else:

            self.attack_timer = (
                .85 -
                self.phase * .08
            )

            count = (
                3
                if self.phase == 1
                else
                5
                if self.phase == 2
                else 7
            )

            for i in range(count):

                offset = (
                    i -
                    (count - 1) / 2
                ) * .13

                angle = (
                    base_angle +
                    offset
                )

                enemy_projectiles.append(
                    EnemyProjectile(
                        self.x,
                        self.y,
                        self.x +
                        math.cos(angle) *
                        1000,
                        self.y +
                        math.sin(angle) *
                        1000,
                        285 +
                        self.phase * 20,
                        7 +
                        self.phase,
                        RED,
                        8
                    )
                )

    def special_attack(self):

        # ====================================================
        # WRAITH
        # ====================================================

        if self.kind == "WRAITH":

            self.special_timer = (
                5.2 -
                self.phase * .4
            )

            # Gentle radial burst.
            count = (
                10
                if self.phase == 1
                else 14
            )

            for i in range(count):

                angle = (
                    i *
                    math.tau /
                    count
                )

                enemy_projectiles.append(
                    EnemyProjectile(
                        self.x,
                        self.y,
                        self.x +
                        math.cos(angle) *
                        1000,
                        self.y +
                        math.sin(angle) *
                        1000,
                        185,
                        5,
                        GOLD,
                        6
                    )
                )

            return

        # ====================================================
        # APOLLO
        # ====================================================

        if self.kind == "APOLLO":

            self.special_timer = (
                5.2 -
                self.phase * .5
            )

            # Apollo's Sun Ring:
            # rotating rays with big gaps.
            count = (
                12
                if self.phase == 1
                else 16
                if self.phase == 2
                else 20
            )

            rotation = (
                self.timer *
                .8
            )

            for i in range(count):

                angle = (
                    i *
                    math.tau /
                    count +
                    rotation
                )

                enemy_projectiles.append(
                    EnemyProjectile(
                        self.x,
                        self.y,
                        self.x +
                        math.cos(angle) *
                        1000,
                        self.y +
                        math.sin(angle) *
                        1000,
                        205,
                        6,
                        SOLAR,
                        7
                    )
                )

            # Small number of aimed shots.
            for _ in range(
                1 +
                self.phase
            ):

                enemy_projectiles.append(
                    EnemyProjectile(
                        self.x,
                        self.y,
                        player.x,
                        player.y,
                        235,
                        8,
                        WHITE,
                        8
                    )
                )

            floating_text(
                "DIVINE RADIANCE",
                self.x,
                self.y - 110,
                SOLAR
            )

            return

        # ====================================================
        # SUN GOD OF WRATH
        # ====================================================

        self.special_timer = (
            5.5 -
            self.phase * .45
        )

        # Phase 1:
        # Big radial burst.
        if self.phase == 1:

            count = 16

            for i in range(count):

                angle = (
                    i *
                    math.tau /
                    count +
                    self.timer * .35
                )

                enemy_projectiles.append(
                    EnemyProjectile(
                        self.x,
                        self.y,
                        self.x +
                        math.cos(angle) *
                        1000,
                        self.y +
                        math.sin(angle) *
                        1000,
                        200,
                        7,
                        ORANGE,
                        7
                    )
                )

        # Phase 2:
        # Rotating wave.
        elif self.phase == 2:

            count = 18

            for i in range(count):

                angle = (
                    i *
                    math.tau /
                    count +
                    self.timer
                )

                enemy_projectiles.append(
                    EnemyProjectile(
                        self.x,
                        self.y,
                        self.x +
                        math.cos(angle) *
                        1000,
                        self.y +
                        math.sin(angle) *
                        1000,
                        220,
                        8,
                        RED,
                        8
                    )
                )

        # Phase 3:
        # Still dangerous, but leaves space.
        else:

            count = 14

            for i in range(count):

                angle = (
                    i *
                    math.tau /
                    count +
                    self.timer *
                    .8
                )

                enemy_projectiles.append(
                    EnemyProjectile(
                        self.x,
                        self.y,
                        self.x +
                        math.cos(angle) *
                        1000,
                        self.y +
                        math.sin(angle) *
                        1000,
                        235,
                        9,
                        RED,
                        9
                    )
                )

            # Three predictable aimed attacks.
            for _ in range(3):

                enemy_projectiles.append(
                    EnemyProjectile(
                        self.x,
                        self.y,
                        player.x,
                        player.y,
                        250,
                        10,
                        WHITE,
                        9,
                        0
                    )
                )

        floating_text(
            "WRATH OF THE SUN",
            self.x,
            self.y - 140,
            RED
        )

    def hit(self, damage):

        if self.invincible > 0:
            return

        self.hp -= damage

        self.hit_flash = .12

        cinematic_impact(
            self.x,
            self.y,
            self.color,
            .45
        )

        floating_text(
            f"-{int(damage)}",
            self.x +
            random.randint(
                -25,
                25
            ),
            self.y - 35,
            WHITE
        )

    def draw(self):

        color = (
            WHITE
            if self.hit_flash > 0
            else self.color
        )

        # ====================================================
        # HELIOS
        # ====================================================

        if self.kind == "HELIOS":

            eclipse_glow(
                self.x,
                self.y,
                self.radius,
                GOLD
            )

            # Broken eclipse rings.
            for i in range(3):

                radius = (
                    self.radius +
                    18 +
                    i * 15
                )

                rect = pygame.Rect(
                    int(
                        self.x -
                        radius
                    ),
                    int(
                        self.y -
                        radius
                    ),
                    radius * 2,
                    radius * 2
                )

                pygame.draw.arc(
                    screen,
                    GOLD,
                    rect,
                    self.angle + i,
                    self.angle +
                    i + 3.7,
                    3
                )

            pygame.draw.circle(
                screen,
                BLACK,
                (
                    int(self.x),
                    int(self.y)
                ),
                self.radius
            )

            pygame.draw.circle(
                screen,
                ORANGE,
                (
                    int(self.x),
                    int(self.y)
                ),
                32
            )

            pygame.draw.circle(
                screen,
                WHITE,
                (
                    int(self.x),
                    int(self.y)
                ),
                9
            )

        # ====================================================
        # APOLLO
        # ====================================================

        elif self.kind == "APOLLO":

            eclipse_glow(
                self.x,
                self.y,
                self.radius + 10,
                SOLAR
            )

            # Massive halo.
            halo_radius = (
                self.radius +
                30
            )

            pygame.draw.circle(
                screen,
                GOLD,
                (
                    int(self.x),
                    int(self.y)
                ),
                halo_radius,
                5
            )

            # Rotating divine rays.
            for i in range(16):

                angle = (
                    self.angle +
                    i *
                    math.tau /
                    16
                )

                inner = (
                    self.radius +
                    35
                )

                outer = (
                    self.radius +
                    65 +
                    math.sin(
                        self.timer * 3 +
                        i
                    ) * 8
                )

                pygame.draw.line(
                    screen,
                    SOLAR,
                    (
                        int(
                            self.x +
                            math.cos(angle) *
                            inner
                        ),
                        int(
                            self.y +
                            math.sin(angle) *
                            inner
                        )
                    ),
                    (
                        int(
                            self.x +
                            math.cos(angle) *
                            outer
                        ),
                        int(
                            self.y +
                            math.sin(angle) *
                            outer
                        )
                    ),
                    4
                )

            # Divine body.
            points = []

            for i in range(8):

                angle = (
                    self.angle * .3 +
                    i *
                    math.tau /
                    8
                )

                radius = (
                    self.radius
                    if i % 2 == 0
                    else self.radius * .72
                )

                points.append(
                    (
                        int(
                            self.x +
                            math.cos(angle) *
                            radius
                        ),
                        int(
                            self.y +
                            math.sin(angle) *
                            radius
                        )
                    )
                )

            pygame.draw.polygon(
                screen,
                (40, 25, 5),
                points
            )

            pygame.draw.polygon(
                screen,
                SOLAR,
                points,
                4
            )

            # Face/core.
            pygame.draw.circle(
                screen,
                WHITE,
                (
                    int(self.x),
                    int(self.y)
                ),
                25
            )

            pygame.draw.circle(
                screen,
                GOLD,
                (
                    int(self.x),
                    int(self.y)
                ),
                13
            )

            pygame.draw.circle(
                screen,
                ORANGE,
                (
                    int(self.x),
                    int(self.y)
                ),
                6
            )

# ============================================================
# SUN GOD OF WRATH DRAW
# ============================================================

        else:

            eclipse_glow(
                self.x,
                self.y,
                self.radius + 20,
                RED
            )

            # Outer divine crown.
            for i in range(24):

                angle = (
                    self.angle +
                    i * math.tau / 24
                )

                inner = self.radius + 8

                outer = (
                    self.radius +
                    40 +
                    math.sin(
                        self.timer * 4 + i
                    ) * 15
                )

                pygame.draw.line(
                    screen,
                    (255, 80, 20),
                    (
                        int(
                            self.x +
                            math.cos(angle) *
                            inner
                        ),
                        int(
                            self.y +
                            math.sin(angle) *
                            inner
                        )
                    ),
                    (
                        int(
                            self.x +
                            math.cos(angle) *
                            outer
                        ),
                        int(
                            self.y +
                            math.sin(angle) *
                            outer
                        )
                    ),
                    5
                )

            # Outer rings.
            for i in range(4):

                radius = (
                    self.radius +
                    35 +
                    i * 20
                )

                rect = pygame.Rect(
                    int(self.x - radius),
                    int(self.y - radius),
                    radius * 2,
                    radius * 2
                )

                pygame.draw.arc(
                    screen,
                    RED if i % 2 == 0 else GOLD,
                    rect,
                    self.angle + i,
                    self.angle + i + 4.5,
                    3
                )

            # Main body.
            pygame.draw.circle(
                screen,
                BLACK,
                (
                    int(self.x),
                    int(self.y)
                ),
                self.radius
            )

            pygame.draw.circle(
                screen,
                (100, 20, 5),
                (
                    int(self.x),
                    int(self.y)
                ),
                self.radius,
                5
            )

            # God core.
            pygame.draw.circle(
                screen,
                RED,
                (
                    int(self.x),
                    int(self.y)
                ),
                35
            )

            pygame.draw.circle(
                screen,
                ORANGE,
                (
                    int(self.x),
                    int(self.y)
                ),
                23
            )

            pygame.draw.circle(
                screen,
                WHITE,
                (
                    int(self.x),
                    int(self.y)
                ),
                10
            )

            # Wrath eyes.
            pygame.draw.line(
                screen,
                WHITE,
                (
                    int(self.x - 28),
                    int(self.y - 22)
                ),
                (
                    int(self.x - 7),
                    int(self.y - 14)
                ),
                5
            )

            pygame.draw.line(
                screen,
                WHITE,
                (
                    int(self.x + 28),
                    int(self.y - 22)
                ),
                (
                    int(self.x + 7),
                    int(self.y - 14)
                ),
                5
            )

        # Boss label.
        draw_glow_text(
            self.name,
            FONT_MED,
            self.x,
            self.y - (self.radius + 65),
            color
        )

        draw_text(
            f"PHASE {self.phase}",
            FONT_TINY,
            self.x,
            self.y - (self.radius + 42),
            color
        )


# ============================================================
# UPGRADE SYSTEM
# ============================================================

upgrade_choices = []
upgrade_active = False

UPGRADES = {

    "DAMAGE": {
        "name": "SOLAR CORE",
        "description": "+1 DAMAGE",
        "color": RED
    },

    "RAPID": {
        "name": "OVERDRIVE",
        "description": "FIRE 20% FASTER",
        "color": GOLD
    },

    "MULTI": {
        "name": "SOLAR SPLIT",
        "description": "+1 PROJECTILE",
        "color": ORANGE
    },

    "PIERCE": {
        "name": "VOID PIERCER",
        "description": "BULLETS PIERCE +1 ENEMY",
        "color": PURPLE
    },

    "EXPLOSIVE": {
        "name": "SUPERNOVA",
        "description": "BULLETS EXPLODE",
        "color": RED
    },

    "CRIT": {
        "name": "CRITICAL MASS",
        "description": "+10% CRIT CHANCE",
        "color": WHITE
    },

    "SPEED": {
        "name": "SOLAR DRIVE",
        "description": "+15% MOVE SPEED",
        "color": BLUE
    },

    "SHIELD": {
        "name": "ECLIPSE SHIELD",
        "description": "+25 SHIELD",
        "color": CYAN
    },

    "ENERGY": {
        "name": "DARK MATTER",
        "description": "+30 MAX ENERGY",
        "color": PURPLE
    },

    "HEAL": {
        "name": "SOLAR BLOOM",
        "description": "HEAL 30 HP",
        "color": GREEN
    },

    "DRONE": {
        "name": "ORBITAL DRONE",
        "description": "ADD AN AUTO-FIRING DRONE",
        "color": CYAN
    },

    "REGEN": {
        "name": "REGENERATION",
        "description": "REGENERATE 1 HP/SEC",
        "color": GREEN
    },

    "DASH": {
        "name": "PHASE DRIVE",
        "description": "DASH COST -5 ENERGY",
        "color": GOLD
    },

    "WRATH": {
        "name": "WRATH ENGINE",
        "description": "SOLAR ORBS GIVE +50% WRATH",
        "color": ORANGE
    },

    "HEAVY": {
        "name": "HEAVY SUN",
        "description": "+25% BULLET DAMAGE",
        "color": SOLAR
    }
}


def choose_upgrade_options():

    global upgrade_choices
    global upgrade_active

    available = list(UPGRADES.keys())

    upgrade_choices = random.sample(
        available,
        min(3, len(available))
    )

    upgrade_active = True


def apply_upgrade(kind):

    global upgrade_active
    global game_state

    if kind not in UPGRADES:
        return

    if kind == "DAMAGE":

        player.damage += 1

    elif kind == "RAPID":

        player.fire_rate = max(
            0.035,
            player.fire_rate * 0.80
        )

    elif kind == "MULTI":

        player.extra_shots += 1

    elif kind == "PIERCE":

        player.piercing += 1

    elif kind == "EXPLOSIVE":

        player.explosive += 1

    elif kind == "CRIT":

        player.crit_chance = min(
            0.75,
            player.crit_chance + 0.10
        )

    elif kind == "SPEED":

        player.speed_multiplier += 0.15

    elif kind == "SHIELD":

        player.max_shield += 25
        player.shield = player.max_shield

    elif kind == "ENERGY":

        player.max_energy += 30
        player.energy = player.max_energy

    elif kind == "HEAL":

        player.hp = min(
            player.max_hp,
            player.hp + 30
        )

    elif kind == "DRONE":

        player.drone_count += 1

    elif kind == "REGEN":

        player.regen += 1

    elif kind == "DASH":

        player.dash_cost = max(
            10,
            player.dash_cost - 5
        )

    elif kind == "WRATH":

        player.magnet *= 1.5

    elif kind == "HEAVY":

        player.damage = max(
            1,
            int(player.damage * 1.25)
        )

    floating_text(
        UPGRADES[kind]["name"],
        player.x,
        player.y - 55,
        UPGRADES[kind]["color"]
    )

    cinematic_impact(
        player.x,
        player.y,
        UPGRADES[kind]["color"],
        1.5
    )

    spawn_particles(
        player.x,
        player.y,
        UPGRADES[kind]["color"],
        50,
        350
    )

    upgrade_active = False
    game_state = "PLAYING"

    save_game()


def draw_upgrade_screen():

    overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill(
        (0, 0, 0, 205)
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    draw_glow_text(
        "SOLAR EVOLUTION",
        FONT_HUGE,
        WIDTH // 2,
        110,
        GOLD
    )

    draw_text(
        "CHOOSE YOUR NEXT POWER",
        FONT_SMALL,
        WIDTH // 2,
        170,
        ORANGE
    )

    mouse_x, mouse_y = pygame.mouse.get_pos()

    card_width = 300
    card_height = 270
    gap = 35

    start_x = (
        WIDTH -
        (
            card_width * 3 +
            gap * 2
        )
    ) // 2

    for i, kind in enumerate(upgrade_choices):

        x = (
            start_x +
            i * (card_width + gap)
        )

        y = 235

        rect = pygame.Rect(
            x,
            y,
            card_width,
            card_height
        )

        hovered = rect.collidepoint(
            mouse_x,
            mouse_y
        )

        color = UPGRADES[kind]["color"]

        if hovered:

            eclipse_glow(
                x + card_width // 2,
                y + card_height // 2,
                120,
                color
            )

        pygame.draw.rect(
            screen,
            (8, 7, 6),
            rect,
            border_radius=20
        )

        pygame.draw.rect(
            screen,
            color,
            rect,
            3 if hovered else 2,
            border_radius=20
        )

        pygame.draw.circle(
            screen,
            color,
            (
                x + card_width // 2,
                y + 60
            ),
            28,
            3
        )

        draw_text(
            str(i + 1),
            FONT_MED,
            x + card_width // 2,
            y + 60,
            color
        )

        draw_text(
            UPGRADES[kind]["name"],
            FONT_MED,
            x + card_width // 2,
            y + 120,
            color
        )

        draw_text(
            UPGRADES[kind]["description"],
            FONT_TINY,
            x + card_width // 2,
            y + 165,
            WHITE
        )

        draw_text(
            "CLICK TO SELECT",
            FONT_TINY,
            x + card_width // 2,
            y + 225,
            (150, 130, 100)
        )


# ============================================================
# EVENTS
# ============================================================

current_event = None
event_timer = 0


def trigger_event():

    global current_event
    global event_timer

    events = [
        "METEOR RUSH",
        "SOLAR SWARM",
        "ELITE HUNT",
        "BLACKOUT"
    ]

    current_event = random.choice(events)
    event_timer = 7


def start_event_effect():

    global current_event

    if current_event == "SOLAR SWARM":

        for _ in range(4):

            enemies.append(
                Enemy(
                    current_level,
                    random.choice(
                        ["NORMAL", "CHARGER"]
                    ),
                    False
                )
            )

    elif current_event == "ELITE HUNT":

        for _ in range(1):

            enemies.append(
                Enemy(
                    current_level,
                    None,
                    True
                )
            )


# ============================================================
# METEORS
# ============================================================

meteors = []


class Meteor:

    def __init__(self):

        self.x = random.randint(
            40,
            WIDTH - 40
        )

        self.y = -40

        self.speed = random.randint(
            400,
            600
        )

        self.radius = random.randint(
            15,
            28
        )

        self.life = 3

    def update(self, dt):

        self.y += self.speed * dt
        self.life -= dt

        if distance(
            self.x,
            self.y,
            player.x,
            player.y
        ) < self.radius + player.radius:

            player.damage_player(12)

            cinematic_impact(
                self.x,
                self.y,
                RED,
                0.8
            )

            return False

        return (
            self.life > 0
            and
            self.y < HEIGHT + 60
        )

    def draw(self):

        eclipse_glow(
            self.x,
            self.y,
            self.radius,
            ORANGE
        )

        pygame.draw.circle(
            screen,
            ORANGE,
            (
                int(self.x),
                int(self.y)
            ),
            self.radius
        )

        pygame.draw.circle(
            screen,
            GOLD,
            (
                int(self.x),
                int(self.y)
            ),
            self.radius // 2
        )


# ============================================================
# LEVEL SYSTEM
# ============================================================

current_level = 1

level_spawned = 0
level_enemy_target = 0

wave_number = 1
wave_total = 1
wave_timer = 0

spawn_timer = 0
event_cooldown = 10

level_complete_timer = 0

score = 0
combo = 0
combo_timer = 0

boss_banner = 0

game_state = "ROADMAP"

last_upgrade_trigger = -1


def is_boss_level(level):

    return level in (
        5,
        10,
        15
    )


def enemy_limit_for_level(level):

    if is_boss_level(level):
        return 0

    return min(
        10 + level * 4,
        50
    )


def enter_level(level):

    global current_level
    global highest_unlocked_level
    global game_state
    global level_spawned
    global level_enemy_target
    global wave_number
    global wave_total
    global wave_timer
    global spawn_timer
    global event_cooldown
    global level_complete_timer
    global boss
    global boss_banner
    global current_event
    global event_timer
    global upgrade_active
    global last_upgrade_trigger

    current_level = level

    if level > highest_unlocked_level:

        highest_unlocked_level = min(
            MAX_LEVEL,
            level
        )

    level_spawned = 0
    wave_number = 0

    level_enemy_target = enemy_limit_for_level(
        level
    )

    if is_boss_level(level):

        wave_total = 1

    else:

        wave_size = 4 + level // 3

        wave_total = math.ceil(
            level_enemy_target /
            wave_size
        )

    wave_timer = 0.6
    spawn_timer = 0.5

    event_cooldown = random.uniform(
        6,
        10
    )

    level_complete_timer = 0

    boss = None
    boss_banner = 0

    current_event = None
    event_timer = 0

    upgrade_active = False
    last_upgrade_trigger = -1

    enemies.clear()
    bullets.clear()
    enemy_projectiles.clear()
    meteors.clear()
    solar_orbs.clear()
    drones.clear()

    player.x = WIDTH // 2
    player.y = HEIGHT - 120

    # IMPORTANT:
    # reset_stats should reset temporary combat values,
    # NOT permanent upgrades.
    player.reset_stats()

    game_state = "PLAYING"

    floating_text(
        f"LEVEL {level}",
        WIDTH // 2,
        HEIGHT // 2,
        GOLD
    )

    cinematic_impact(
        WIDTH // 2,
        HEIGHT // 2,
        GOLD,
        1
    )

    # ========================================================
    # BOSS
    # ========================================================

    if is_boss_level(level):

        boss = Boss(level)

        # MUCH easier boss scaling.
        boss_hp_multiplier = 0.45

        boss.max_hp = max(
            180,
            int(
                boss.max_hp *
                boss_hp_multiplier
            )
        )

        boss.hp = boss.max_hp

        boss_banner = 3.5

        cinematic_impact(
            WIDTH // 2,
            165,
            ORANGE,
            2
        )

        spawn_particles(
            WIDTH // 2,
            165,
            GOLD,
            100,
            500
        )

        if level == 5:

            floating_text(
                "HELIOS",
                WIDTH // 2,
                260,
                GOLD
            )

        elif level == 10:

            floating_text(
                "APOLLO",
                WIDTH // 2,
                260,
                SOLAR
            )

        else:

            floating_text(
                "SUN GOD OF WRATH",
                WIDTH // 2,
                260,
                RED
            )

    else:

        floating_text(
            f"WAVE 1/{wave_total}",
            WIDTH // 2,
            260,
            ORANGE
        )


# ============================================================
# SPAWN WAVE
# ============================================================

def spawn_wave():

    global level_spawned
    global wave_number

    remaining = (
        level_enemy_target -
        level_spawned
    )

    if remaining <= 0:
        return

    wave_size = min(
        remaining,
        4 + current_level // 3
    )

    wave_number += 1

    for _ in range(wave_size):

        elite_chance = min(
            0.025 +
            current_level * 0.006,
            0.10
        )

        is_elite = (
            random.random() <
            elite_chance
        )

        enemies.append(
            Enemy(
                current_level,
                None,
                is_elite
            )
        )

        level_spawned += 1

    floating_text(
        f"WAVE {wave_number}/{wave_total}",
        WIDTH // 2,
        225,
        ORANGE
    )

    cinematic_impact(
        WIDTH // 2,
        220,
        ORANGE,
        0.35
    )


# ============================================================
# COMPLETE LEVEL
# ============================================================

def complete_level():

    global game_state
    global highest_unlocked_level
    global level_complete_timer
    global score
    global upgrade_active
    global current_event

    if game_state == "LEVEL_COMPLETE":
        return

    score += current_level * 1000

    if current_level >= highest_unlocked_level:

        highest_unlocked_level = min(
            MAX_LEVEL,
            current_level + 1
        )

    enemies.clear()
    enemy_projectiles.clear()
    meteors.clear()
    solar_orbs.clear()

    current_event = None
    upgrade_active = False

    cinematic_impact(
        WIDTH // 2,
        HEIGHT // 2,
        GOLD,
        4
    )

    spawn_particles(
        WIDTH // 2,
        HEIGHT // 2,
        GOLD,
        160,
        600
    )

    level_complete_timer = 2.5

    game_state = "LEVEL_COMPLETE"

    save_game()


# ============================================================
# ROADMAP
# ============================================================

roadmap_nodes = []

for i in range(MAX_LEVEL):

    row = i // 5
    col = i % 5

    x = 280 + col * 180
    y = 230 + row * 115

    roadmap_nodes.append(
        (x, y)
    )


def draw_boss_symbol(
    x,
    y,
    color
):

    eclipse_glow(
        x,
        y,
        7,
        color
    )

    pygame.draw.circle(
        screen,
        color,
        (
            int(x),
            int(y)
        ),
        6,
        2
    )

    pygame.draw.line(
        screen,
        color,
        (
            int(x - 10),
            int(y)
        ),
        (
            int(x + 10),
            int(y)
        ),
        2
    )

    pygame.draw.line(
        screen,
        color,
        (
            int(x),
            int(y - 10)
        ),
        (
            int(x),
            int(y + 10)
        ),
        2
    )


def roadmap_clicked(pos):

    mx, my = pos

    for i, node in enumerate(
        roadmap_nodes
    ):

        level = i + 1

        if level > highest_unlocked_level:
            continue

        if distance(
            mx,
            my,
            node[0],
            node[1]
        ) < 40:

            return level

    return None


def draw_roadmap(t):

    draw_background(t)
    draw_menu_effects(t)

    overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill(
        (0, 0, 0, 145)
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    draw_glow_text(
        "E C L I P S E",
        FONT_TITLE,
        WIDTH // 2,
        70,
        GOLD
    )

    draw_text(
        "SOLAR PATH",
        FONT_SMALL,
        WIDTH // 2,
        125,
        ORANGE
    )

    draw_text(
        "15 SECTORS • 3 ANOMALIES • 1 FINAL GOD",
        FONT_TINY,
        WIDTH // 2,
        150,
        (140, 115, 80)
    )

    # PATH

    for i in range(
        len(roadmap_nodes) - 1
    ):

        x1, y1 = roadmap_nodes[i]
        x2, y2 = roadmap_nodes[i + 1]

        pygame.draw.line(
            screen,
            (55, 30, 10),
            (x1, y1),
            (x2, y2),
            7
        )

        if i + 1 < highest_unlocked_level:

            pygame.draw.line(
                screen,
                GOLD,
                (x1, y1),
                (x2, y2),
                2
            )

    # NODES

    mx, my = pygame.mouse.get_pos()

    for i, node in enumerate(
        roadmap_nodes
    ):

        level = i + 1

        x, y = node

        unlocked = (
            level <=
            highest_unlocked_level
        )

        boss_level = is_boss_level(
            level
        )

        hovered = (
            distance(
                mx,
                my,
                x,
                y
            ) < 40
            and
            unlocked
        )

        if not unlocked:

            color = (55, 40, 25)

        elif hovered:

            color = WHITE

        elif boss_level:

            color = RED

        else:

            color = GOLD

        if hovered:

            eclipse_glow(
                x,
                y,
                42,
                WHITE
            )

        else:

            eclipse_glow(
                x,
                y,
                28,
                color
            )

        pygame.draw.circle(
            screen,
            BLACK,
            (
                int(x),
                int(y)
            ),
            31
        )

        pygame.draw.circle(
            screen,
            color,
            (
                int(x),
                int(y)
            ),
            29,
            3
        )

        draw_text(
            str(level),
            FONT_MED,
            x,
            y,
            color
        )

        if boss_level:

            draw_boss_symbol(
                x,
                y - 45,
                RED
            )

            # FIXED BOSS NAMES
            if level == 5:

                boss_label = "HELIOS"

            elif level == 10:

                boss_label = "APOLLO"

            else:

                boss_label = "SUN GOD"

            draw_text(
                boss_label,
                FONT_TINY,
                x,
                y + 45,
                RED
            )

    draw_text(
        f"SECTOR {highest_unlocked_level:02d} / {MAX_LEVEL}",
        FONT_MED,
        WIDTH // 2,
        HEIGHT - 65,
        GOLD
    )

    draw_text(
        "CLICK A SECTOR     |     ESC QUIT",
        FONT_TINY,
        WIDTH // 2,
        HEIGHT - 30,
        (140, 115, 80)
    )


# ============================================================
# HUD
# ============================================================

def draw_hud():

    panel = pygame.Surface(
        (
            WIDTH - 70,
            110
        ),
        pygame.SRCALPHA
    )

    pygame.draw.rect(
        panel,
        (12, 9, 7, 225),
        (
            0,
            0,
            WIDTH - 70,
            110
        ),
        border_radius=18
    )

    pygame.draw.rect(
        panel,
        (120, 65, 15, 150),
        (
            0,
            0,
            WIDTH - 70,
            110
        ),
        2,
        border_radius=18
    )

    screen.blit(
        panel,
        (35, 22)
    )

    # ========================================================
    # SCORE
    # ========================================================

    draw_text(
        f"{score:,}",
        FONT_BIG,
        120,
        57
    )

    draw_text(
        "SCORE",
        FONT_TINY,
        120,
        89,
        GOLD
    )

    # ========================================================
    # LEVEL
    # ========================================================

    draw_text(
        f"LEVEL {current_level}",
        FONT_MED,
        WIDTH // 2,
        55
    )

    if boss is not None:

        draw_text(
            "BOSS",
            FONT_SMALL,
            WIDTH // 2,
            90,
            RED
        )

    else:

        draw_text(
            f"WAVE {wave_number}/{wave_total}",
            FONT_SMALL,
            WIDTH // 2,
            90,
            ORANGE
        )

    # ========================================================
    # HP
    # ========================================================

    bar_x = WIDTH - 365
    bar_y = 43
    bar_width = 270

    pygame.draw.rect(
        screen,
        DARK,
        (
            bar_x,
            bar_y,
            bar_width,
            14
        ),
        border_radius=7
    )

    hp_ratio = 0

    if player.max_hp > 0:

        hp_ratio = clamp(
            player.hp /
            player.max_hp,
            0,
            1
        )

    pygame.draw.rect(
        screen,
        RED,
        (
            bar_x,
            bar_y,
            int(bar_width * hp_ratio),
            14
        ),
        border_radius=7
    )

    draw_text(
        f"{max(0, int(player.hp))}/{player.max_hp} HP",
        FONT_TINY,
        bar_x,
        75,
        WHITE,
        False
    )

    # ========================================================
    # ENERGY
    # ========================================================

    energy_ratio = 0

    if player.max_energy > 0:

        energy_ratio = clamp(
            player.energy /
            player.max_energy,
            0,
            1
        )

    pygame.draw.rect(
        screen,
        DARK,
        (
            bar_x,
            94,
            bar_width,
            6
        ),
        border_radius=3
    )

    pygame.draw.rect(
        screen,
        GOLD,
        (
            bar_x,
            94,
            int(bar_width * energy_ratio),
            6
        ),
        border_radius=3
    )

    # ========================================================
    # WRATH
    # ========================================================

    wrath_y = 105

    wrath_ratio = 0

    if player.max_wrath > 0:

        wrath_ratio = clamp(
            player.wrath /
            player.max_wrath,
            0,
            1
        )

    pygame.draw.rect(
        screen,
        DARK,
        (
            bar_x,
            wrath_y,
            bar_width,
            7
        ),
        border_radius=3
    )

    pygame.draw.rect(
        screen,
        ORANGE,
        (
            bar_x,
            wrath_y,
            int(bar_width * wrath_ratio),
            7
        ),
        border_radius=3
    )

    if player.wrath >= player.max_wrath:

        draw_glow_text(
            "Q — SOLAR NOVA READY",
            FONT_TINY,
            bar_x + bar_width // 2,
            125,
            GOLD
        )

    else:

        draw_text(
            "WRATH",
            FONT_TINY,
            bar_x,
            125,
            ORANGE,
            False
        )

    # ========================================================
    # COMBO
    # ========================================================

    if combo >= 2:

        draw_glow_text(
            f"x{combo}",
            FONT_BIG,
            WIDTH // 2,
            135,
            SOLAR
        )

    # ========================================================
    # BOSS BAR
    # ========================================================

    if boss is not None:

        draw_text(
            boss.name,
            FONT_MED,
            WIDTH // 2,
            160,
            boss.color
        )

        boss_width = 650

        boss_x = (
            WIDTH // 2 -
            boss_width // 2
        )

        boss_ratio = 0

        if boss.max_hp > 0:

            boss_ratio = clamp(
                boss.hp /
                boss.max_hp,
                0,
                1
            )

        pygame.draw.rect(
            screen,
            DARK,
            (
                boss_x,
                183,
                boss_width,
                16
            ),
            border_radius=8
        )

        pygame.draw.rect(
            screen,
            boss.color,
            (
                boss_x,
                183,
                int(
                    boss_width *
                    boss_ratio
                ),
                16
            ),
            border_radius=8
        )

    # ========================================================
    # BUILD
    # ========================================================

    draw_text(
        f"DMG {player.damage}",
        FONT_TINY,
        45,
        145,
        GOLD,
        False
    )

    draw_text(
        f"SHOT +{player.extra_shots}",
        FONT_TINY,
        145,
        145,
        ORANGE,
        False
    )

    draw_text(
        f"CRIT {int(player.crit_chance * 100)}%",
        FONT_TINY,
        255,
        145,
        WHITE,
        False
    )

    draw_text(
        f"DRONES {player.drone_count}",
        FONT_TINY,
        385,
        145,
        CYAN,
        False
    )

    draw_text(
        "WASD MOVE   LMB FIRE   SPACE DASH   Q NOVA",
        FONT_SMALL,
        WIDTH // 2,
        HEIGHT - 24,
        (140, 120, 90)
    )


# ============================================================
# PLAYING DRAW
# ============================================================

def draw_playing(t):

    draw_background(t)

    # ========================================================
    # METEORS
    # ========================================================

    for meteor in meteors:
        meteor.draw()

    # ========================================================
    # SOLAR ORBS
    # ========================================================

    for orb in solar_orbs:
        orb.draw()

    # ========================================================
    # ENEMIES
    # ========================================================

    for enemy in enemies:
        enemy.draw()

    # ========================================================
    # BOSS
    # ========================================================

    if boss is not None:
        boss.draw()

    # ========================================================
    # PLAYER BULLETS
    # ========================================================

    for bullet in bullets:
        bullet.draw()

    # ========================================================
    # ENEMY PROJECTILES
    # ========================================================

    for projectile in enemy_projectiles:
        projectile.draw()

    # ========================================================
    # DRONES
    # ========================================================

    for drone in drones:
        drone.draw()
    # ============================================================
    # ONLINE PLAYERS
    # ============================================================

    if online_connected:

        for player_id, other in online_players.items():

            if str(player_id) == str(PLAYER_ID):
                continue

            draw_online_player(other)

    # ============================================================
    # LOCAL PLAYER
    # ============================================================

    player.draw()

    # ============================================================
    # DRONES
    # ============================================================

    for drone in drones:
        drone.draw()

    # ============================================================
    # PARTICLES
    # ============================================================

    for particle in particles:
        particle.draw()

    # ============================================================
    # SHOCKWAVES
    # ============================================================

    for shockwave in shockwaves:
        shockwave.draw()

    # ============================================================
    # FLOATING TEXT
    # ============================================================

    for text in floating_texts:
        text.draw()

    # ============================================================
    # HUD
    # ============================================================

    draw_hud()

    # ============================================================
    # EVENT
    # ============================================================

    if current_event is not None:

        if current_event == "BLACKOUT":

            blackout = pygame.Surface(
                (WIDTH, HEIGHT),
                pygame.SRCALPHA
            )

            blackout.fill(
                (0, 0, 10, 155)
            )

            screen.blit(
                blackout,
                (0, 0)
            )

        draw_text(
            current_event,
            FONT_BIG,
            WIDTH // 2,
            240,
            RED
        )

    # ============================================================
    # BOSS BANNER
    # ============================================================

    if boss_banner > 0:

        if current_level == 5:

            title = "HELIOS"

        elif current_level == 10:

            title = "APOLLO"

        elif current_level >= MAX_LEVEL:

            title = "SUN GOD OF WRATH"

        else:

            title = (
                boss.name
                if boss is not None
                else "SOLAR GUARDIAN"
            )

        boss_colour = (
            boss.color
            if boss is not None
            else RED
        )

        draw_glow_text(
            title,
            FONT_BIG,
            WIDTH // 2,
            285,
            boss_colour
        )

    # ============================================================
    # BOSS PHASE TRANSITION
    # ============================================================

    if (
        boss is not None
        and
        getattr(
            boss,
            "phase_transition",
            0
        ) > 0
    ):

        overlay = pygame.Surface(
            (
                WIDTH,
                HEIGHT
            ),
            pygame.SRCALPHA
        )

        overlay.fill(
            (0, 0, 0, 145)
        )

        screen.blit(
            overlay,
            (0, 0)
        )

        draw_glow_text(
            f"PHASE {boss.phase}",
            FONT_HUGE,
            WIDTH // 2,
            HEIGHT // 2,
            boss.color
        )

        if boss.kind == "APOLLO":

            subtitle = "DIVINE ASCENSION"

        elif boss.kind == "WRATH":

            subtitle = "WRATH AWAKENS"

        elif boss.kind == "HELIOS":

            subtitle = "THE SUN IGNITES"

        else:

            subtitle = "SOLAR COLLAPSE"

        draw_text(
            subtitle,
            FONT_SMALL,
            WIDTH // 2,
            HEIGHT // 2 + 70,
            WHITE
        )


# ============================================================
# LEVEL COMPLETE
# ============================================================

def draw_level_complete():

    draw_background(
        pygame.time.get_ticks() / 1000
    )

    overlay = pygame.Surface(
        (
            WIDTH,
            HEIGHT
        ),
        pygame.SRCALPHA
    )

    overlay.fill(
        (0, 0, 0, 190)
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    draw_glow_text(
        "ECLIPSE CLEARED",
        FONT_HUGE,
        WIDTH // 2,
        260,
        GOLD
    )

    draw_text(
        f"SECTOR {current_level}",
        FONT_MED,
        WIDTH // 2,
        335,
        ORANGE
    )

    draw_text(
        f"SCORE  {score:,}",
        FONT_MED,
        WIDTH // 2,
        385,
        WHITE
    )

    if current_level < MAX_LEVEL:

        draw_text(
            f"SECTOR {current_level + 1} UNLOCKED",
            FONT_SMALL,
            WIDTH // 2,
            445,
            GREEN
        )

    else:

        draw_glow_text(
            "THE SUN GOD HAS FALLEN",
            FONT_BIG,
            WIDTH // 2,
            445,
            RED
        )

    draw_text(
        "RETURNING TO SOLAR PATH...",
        FONT_SMALL,
        WIDTH // 2,
        515,
        GOLD
    )


# ============================================================
# GAME OVER
# ============================================================

def draw_game_over():

    draw_background(
        pygame.time.get_ticks() / 1000
    )

    overlay = pygame.Surface(
        (
            WIDTH,
            HEIGHT
        ),
        pygame.SRCALPHA
    )

    overlay.fill(
        (0, 0, 0, 225)
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    draw_glow_text(
        "TOTAL ECLIPSE",
        FONT_HUGE,
        WIDTH // 2,
        245,
        WHITE
    )

    draw_text(
        f"SCORE {score:,}",
        FONT_MED,
        WIDTH // 2,
        350,
        GOLD
    )

    draw_text(
        f"SECTOR {current_level}",
        FONT_MED,
        WIDTH // 2,
        395,
        ORANGE
    )

    draw_text(
        "PRESS ENTER TO TRY AGAIN",
        FONT_SMALL,
        WIDTH // 2,
        485,
        WHITE
    )


# ============================================================
# RESET
# ============================================================

drones = []


def reset_game():

    global game_state
    global current_level
    global highest_unlocked_level
    global score
    global boss
    global combo
    global combo_timer
    global upgrade_active
    global current_event
    global event_timer
    global last_upgrade_trigger
    global wave_number
    global level_spawned
    global level_enemy_target
    global wave_total
    global wave_timer
    global event_cooldown
    global boss_banner
    global level_complete_timer
    global online_receive_buffer

    # --------------------------------------------------------
    # PLAYER
    # --------------------------------------------------------

    player.reset_upgrades()
    player.reset_stats()

    # --------------------------------------------------------
    # CLEAR EVERYTHING
    # --------------------------------------------------------

    drones.clear()

    enemies.clear()
    bullets.clear()
    enemy_projectiles.clear()
    meteors.clear()
    solar_orbs.clear()

    particles.clear()
    shockwaves.clear()
    floating_texts.clear()

    # --------------------------------------------------------
    # ONLINE
    # --------------------------------------------------------

    online_players.clear()
    online_player_visuals.clear()
    online_receive_buffer = ""

    # --------------------------------------------------------
    # PROGRESSION
    # --------------------------------------------------------

    current_level = 1
    

    score = 0

    boss = None

    combo = 0
    combo_timer = 0

    wave_number = 0
    wave_total = 1
    level_spawned = 0
    level_enemy_target = 0

    wave_timer = 0

    event_cooldown = 10

    boss_banner = 0

    upgrade_active = False
    last_upgrade_trigger = -1

    current_event = None
    event_timer = 0

    level_complete_timer = 0

    game_state = "ROADMAP"

    save_game()


# ============================================================
# EVENT UPDATE
# ============================================================

def update_event(dt):

    global event_cooldown
    global current_event
    global event_timer

    # --------------------------------------------------------
    # NO RANDOM EVENTS DURING BOSSES
    # --------------------------------------------------------

    if is_boss_level(current_level):

        current_event = None
        event_timer = 0

        return

    # --------------------------------------------------------
    # ACTIVE EVENT
    # --------------------------------------------------------

    if current_event is not None:

        event_timer -= dt

        # ----------------------------------------------------
        # METEOR RUSH
        # ----------------------------------------------------

        if current_event == "METEOR RUSH":

            if random.random() < 0.045 * dt * 60:

                if len(meteors) < 8:

                    meteors.append(
                        Meteor()
                    )

        # ----------------------------------------------------
        # SOLAR SWARM
        # ----------------------------------------------------

        elif current_event == "SOLAR SWARM":

            if (
                random.random()
                <
                0.012 * dt * 60
                and
                len(enemies) < 14
            ):

                enemies.append(
                    Enemy(
                        current_level,
                        None,
                        False
                    )
                )

        # ----------------------------------------------------
        # ELITE HUNT
        # ----------------------------------------------------

        elif current_event == "ELITE HUNT":

            if (
                random.random()
                <
                0.006 * dt * 60
                and
                len(enemies) < 12
            ):

                enemies.append(
                    Enemy(
                        current_level,
                        None,
                        True
                    )
                )

        # ----------------------------------------------------
        # BLACKOUT
        # ----------------------------------------------------

        elif current_event == "BLACKOUT":

            pass

        # ----------------------------------------------------
        # EVENT FINISHED
        # ----------------------------------------------------

        if event_timer <= 0:

            current_event = None

            event_cooldown = random.uniform(
                7,
                12
            )

        return

    # --------------------------------------------------------
    # WAITING FOR NEXT EVENT
    # --------------------------------------------------------

    event_cooldown -= dt

    if event_cooldown <= 0:

        trigger_event()
        start_event_effect()


# ============================================================
# ONLINE PLAYERS
# ============================================================

online_players = {}

online_player_visuals = {}

online_receive_buffer = ""

online_send_timer = 0

# 0.05 seconds = 20 network updates per second.
ONLINE_SEND_RATE = 0.05


# ============================================================
# RECEIVE ONLINE PLAYERS
# ============================================================

def receive_online_players():

    global online_receive_buffer
    global online_connected
    global sock

    if not online_connected:
        return

    if sock is None:
        return

    # --------------------------------------------------------
    # RECEIVE ALL AVAILABLE DATA
    # --------------------------------------------------------

    while True:

        try:

            data = sock.recv(
                65536
            )

            if not data:

                online_connected = False
                break

            online_receive_buffer += data.decode(
                "utf-8",
                errors="ignore"
            )

        except BlockingIOError:

            break

        except (
            ConnectionResetError,
            BrokenPipeError,
            OSError
        ) as error:

            print(
                f"[ONLINE] CONNECTION LOST WHILE RECEIVING: {error}"
            )

            online_connected = False
            break

        except Exception:

            break

    # --------------------------------------------------------
    # PROCESS COMPLETE JSON LINES
    # --------------------------------------------------------

    while "\n" in online_receive_buffer:

        raw_message, online_receive_buffer = (
            online_receive_buffer.split(
                "\n",
                1
            )
        )

        raw_message = raw_message.strip()

        if not raw_message:
            continue

        try:

            data = json.loads(
                raw_message
            )

        except (
            json.JSONDecodeError,
            TypeError,
            ValueError
        ):

            continue

        if not isinstance(
            data,
            dict
        ):

            continue

        player_id = data.get(
            "id"
        )

        if player_id is None:
            continue

        # ----------------------------------------------------
        # NEVER CREATE OUR OWN REMOTE COPY
        # ----------------------------------------------------

        if str(player_id) == str(PLAYER_ID):
            continue

        # ----------------------------------------------------
        # VALIDATE POSITION
        # ----------------------------------------------------

        try:

            x = float(
                data.get(
                    "x",
                    WIDTH // 2
                )
            )

            y = float(
                data.get(
                    "y",
                    HEIGHT // 2
                )
            )

        except (
            TypeError,
            ValueError
        ):

            continue

        # ----------------------------------------------------
        # KEEP PLAYER INSIDE GAME
        # ----------------------------------------------------

        x = clamp(
            x,
            0,
            WIDTH
        )

        y = clamp(
            y,
            0,
            HEIGHT
        )

        now = pygame.time.get_ticks()

        existing = online_players.get(
            player_id
        )

        # ----------------------------------------------------
        # NEW PLAYER
        # ----------------------------------------------------

        if existing is None:

            online_players[player_id] = {

                "id": player_id,

                "x": x,
                "y": y,

                "target_x": x,
                "target_y": y,

                "name": str(
                    data.get(
                        "name",
                        "ONLINE PLAYER"
                    )
                )[:24],

                "last_seen": now

            }

        # ----------------------------------------------------
        # EXISTING PLAYER
        # ----------------------------------------------------

        else:

            existing["target_x"] = x
            existing["target_y"] = y

            existing["name"] = str(
                data.get(
                    "name",
                    existing.get(
                        "name",
                        "ONLINE PLAYER"
                    )
                )
            )[:24]

            existing["last_seen"] = now


# ============================================================
# UPDATE ONLINE PLAYERS
# ============================================================

def update_online_players(dt):

    interpolation = min(
        1.0,
        dt * 14
    )

    for player_id, other in list(
        online_players.items()
    ):

        if not isinstance(
            other,
            dict
        ):

            continue

        target_x = other.get(
            "target_x",
            other.get(
                "x",
                WIDTH // 2
            )
        )

        target_y = other.get(
            "target_y",
            other.get(
                "y",
                HEIGHT // 2
            )
        )

        try:

            target_x = float(target_x)
            target_y = float(target_y)

        except (
            TypeError,
            ValueError
        ):

            continue

        # ----------------------------------------------------
        # SMOOTH MOVEMENT
        # ----------------------------------------------------

        other["x"] += (
            target_x -
            other["x"]
        ) * interpolation

        other["y"] += (
            target_y -
            other["y"]
        ) * interpolation

        # ----------------------------------------------------
        # SAFETY CLAMP
        # ----------------------------------------------------

        other["x"] = clamp(
            other["x"],
            -50,
            WIDTH + 50
        )

        other["y"] = clamp(
            other["y"],
            -50,
            HEIGHT + 50
        )


# ============================================================
# CLEANUP ONLINE PLAYERS
# ============================================================

def cleanup_online_players():

    now = pygame.time.get_ticks()

    for player_id in list(
        online_players.keys()
    ):

        data = online_players.get(
            player_id
        )

        if not isinstance(
            data,
            dict
        ):

            del online_players[
                player_id
            ]

            continue

        last_seen = data.get(
            "last_seen",
            now
        )

        if (
            now -
            last_seen
            >
            5000
        ):

            del online_players[
                player_id
            ]


# ============================================================
# DRAW ONLINE PLAYER
# ============================================================

def draw_online_player(data):

    try:

        x = float(
            data.get(
                "x",
                WIDTH // 2
            )
        )

        y = float(
            data.get(
                "y",
                HEIGHT // 2
            )
        )

    except (
        TypeError,
        ValueError
    ):

        return

    # ========================================================
    # GLOW
    # ========================================================

    eclipse_glow(
        x,
        y,
        35,
        CYAN
    )

    # ========================================================
    # SHIP
    # ========================================================

    points = [

        (
            int(x),
            int(y - 22)
        ),

        (
            int(x - 17),
            int(y + 18)
        ),

        (
            int(x),
            int(y + 11)
        ),

        (
            int(x + 17),
            int(y + 18)
        )

    ]

    pygame.draw.polygon(
        screen,
        CYAN,
        points
    )

    pygame.draw.polygon(
        screen,
        WHITE,
        points,
        2
    )

    # ========================================================
    # CORE
    # ========================================================

    pygame.draw.circle(
        screen,
        WHITE,
        (
            int(x),
            int(y)
        ),
        5
    )

    pygame.draw.circle(
        screen,
        CYAN,
        (
            int(x),
            int(y)
        ),
        3
    )

    # ========================================================
    # ENGINE
    # ========================================================

    pygame.draw.polygon(
        screen,
        ORANGE,
        [

            (
                int(x - 7),
                int(y + 13)
            ),

            (
                int(x),
                int(y + 30)
            ),

            (
                int(x + 7),
                int(y + 13)
            )

        ]
    )

    # ========================================================
    # NAME
    # ========================================================

    draw_text(
        str(
            data.get(
                "name",
                "ONLINE PLAYER"
            )
        )[:24],
        FONT_TINY,
        x,
        y - 42,
        CYAN
    )


# ============================================================
# LOAD SAVE
# ============================================================

load_game()


# ============================================================
# SEND PLAYER POSITION
# ============================================================

def send_player_position():

    global online_connected
    global sock

    if not online_connected:
        return

    if sock is None:
        return

    if "player" not in globals():
        return

    try:

        data = {

            "id": PLAYER_ID,

            "x": float(
                player.x
            ),

            "y": float(
                player.y
            ),

            "name": str(
                current_username
            )[:24]

        }

        message = (
            json.dumps(
                data,
                separators=(
                    ",",
                    ":"
                )
            )
            + "\n"
        )

        sock.sendall(
            message.encode(
                "utf-8"
            )
        )

    except (
        BlockingIOError,
        ConnectionResetError,
        BrokenPipeError,
        ConnectionAbortedError,
        OSError
    ) as error:

        print(
            f"[ONLINE] CONNECTION LOST WHILE SENDING: {error}"
        )

        online_connected = False

        try:

            sock.close()

        except Exception:

            pass

        sock = None


# ============================================================
# CONNECT TO MULTIPLAYER
# ============================================================

# IMPORTANT:
# connect_to_server() was previously only DEFINED and never CALLED.
# That meant the terminal could never print CONNECTED and
# online_connected always stayed False.
connect_to_server()


# ============================================================
# PROFILE LOGIN
# ============================================================

profile_login()


# ============================================================
# MAIN LOOP
# ============================================================

running = True

while running:

    # ========================================================
    # DELTA TIME
    # ========================================================

    real_dt = (
        clock.tick(FPS)
        /
        1000
    )

    real_dt = min(
        real_dt,
        0.05
    )

    # ========================================================
    # ONLINE MULTIPLAYER
    # ========================================================

    if online_connected:

        online_send_timer -= real_dt

        # ----------------------------------------------------
        # NETWORK UPDATE
        # ----------------------------------------------------

        if online_send_timer <= 0:

            online_send_timer = ONLINE_SEND_RATE

            # Receive first so players feel responsive.
            receive_online_players()

            # Send our position.
            send_player_position()

            # Remove disconnected players.
            cleanup_online_players()

        # ----------------------------------------------------
        # SMOOTH OTHER PLAYERS
        # ----------------------------------------------------

        update_online_players(
            real_dt
        )

    # ========================================================
    # EVENTS
    # ========================================================

    for event in pygame.event.get():

        # ====================================================
        # QUIT
        # ====================================================

        if event.type == pygame.QUIT:

            running = False

        # ====================================================
        # KEYBOARD
        # ====================================================

        elif event.type == pygame.KEYDOWN:

            # =================================================
            # FULLSCREEN TOGGLE
            # =================================================

            if event.key == pygame.K_BACKQUOTE:

                if (
                    pygame.display.get_surface().get_flags()
                    &
                    pygame.FULLSCREEN
                ):

                    screen = pygame.display.set_mode(
                        (
                            WIDTH,
                            HEIGHT
                        )
                    )

                else:

                    screen = pygame.display.set_mode(
                        (
                            WIDTH,
                            HEIGHT
                        ),
                        pygame.FULLSCREEN
                    )

            # =================================================
            # ESCAPE
            # =================================================

            elif event.key == pygame.K_ESCAPE:

                if game_state == "PLAYING":

                    enemies.clear()
                    bullets.clear()
                    enemy_projectiles.clear()
                    meteors.clear()
                    solar_orbs.clear()

                    boss = None

                    current_event = None
                    event_timer = 0

                    upgrade_active = False

                    save_game()

                    game_state = "ROADMAP"

                elif game_state == "UPGRADE":

                    pass

                elif game_state == "LEVEL_COMPLETE":

                    game_state = "ROADMAP"

                else:

                    running = False

            # =================================================
            # DASH
            # =================================================

            elif (
                game_state == "PLAYING"
                and
                event.key == pygame.K_SPACE
            ):

                player.dash()

            # =================================================
            # SOLAR NOVA
            # =================================================

            elif (
                game_state == "PLAYING"
                and
                event.key == pygame.K_q
            ):

                player.solar_nova()

            # =================================================
            # RESTART
            # =================================================

            elif (
                game_state == "GAME_OVER"
                and
                event.key == pygame.K_RETURN
            ):

                reset_game()

            # =================================================
            # UPGRADE 1
            # =================================================

            elif (
                game_state == "UPGRADE"
                and
                event.key == pygame.K_1
            ):

                if len(
                    upgrade_choices
                ) >= 1:

                    apply_upgrade(
                        upgrade_choices[0]
                    )

            # =================================================
            # UPGRADE 2
            # =================================================

            elif (
                game_state == "UPGRADE"
                and
                event.key == pygame.K_2
            ):

                if len(
                    upgrade_choices
                ) >= 2:

                    apply_upgrade(
                        upgrade_choices[1]
                    )

            # =================================================
            # UPGRADE 3
            # =================================================

            elif (
                game_state == "UPGRADE"
                and
                event.key == pygame.K_3
            ):

                if len(
                    upgrade_choices
                ) >= 3:

                    apply_upgrade(
                        upgrade_choices[2]
                    )

        # ====================================================
        # MOUSE
        # ====================================================

        elif (
            event.type ==
            pygame.MOUSEBUTTONDOWN
            and
            event.button == 1
        ):

            # =================================================
            # ROADMAP
            # =================================================

            if game_state == "ROADMAP":

                selected = roadmap_clicked(
                    event.pos
                )

                if selected is not None:

                    enter_level(
                        selected
                    )

            # =================================================
            # SHOOTING
            # =================================================

            elif game_state == "PLAYING":

                player.shoot()

            # =================================================
            # UPGRADE
            # =================================================

            elif game_state == "UPGRADE":

                mx, my = event.pos

                card_width = 300
                card_height = 270
                gap = 35

                start_x = (
                    WIDTH -
                    (
                        card_width * 3 +
                        gap * 2
                    )
                ) // 2

                for i, kind in enumerate(
                    upgrade_choices
                ):

                    rect = pygame.Rect(
                        start_x +
                        i *
                        (
                            card_width +
                            gap
                        ),
                        235,
                        card_width,
                        card_height
                    )

                    if rect.collidepoint(
                        mx,
                        my
                    ):

                        apply_upgrade(
                            kind
                        )

                        break

    # ========================================================
    # HIT STOP
    # ========================================================

    if hit_stop > 0:

        hit_stop -= real_dt

        dt = 0

    else:

        dt = real_dt

    # ========================================================
    # PLAYING
    # ========================================================

    if game_state == "PLAYING":

        player.update(
            dt
        )

        # ====================================================
        # WAVES
        # ====================================================

        if (
            not is_boss_level(
                current_level
            )
            and
            not enemies
            and
            level_spawned <
            level_enemy_target
            and
            not upgrade_active
        ):

            wave_timer -= dt

            if wave_timer <= 0:

                spawn_wave()

                wave_timer = 1.15

        # ====================================================
        # ENEMIES
        # ====================================================

        for enemy in enemies[:]:

            if not enemy.update(
                dt
            ):

                if enemy in enemies:

                    enemies.remove(
                        enemy
                    )

        # ====================================================
        # BULLETS
        # ====================================================

        for bullet in bullets[:]:

            if not bullet.update(
                dt
            ):

                if bullet in bullets:

                    bullets.remove(
                        bullet
                    )

                continue

            bullet_hit = False

            # =================================================
            # BOSS COLLISION
            # =================================================

            if boss is not None:

                if distance(
                    bullet.x,
                    bullet.y,
                    boss.x,
                    boss.y
                ) < (
                    boss.radius +
                    8
                ):

                    if boss.invincible <= 0:

                        boss.hit(
                            bullet.damage
                        )

                        score += 15

                    if bullet in bullets:

                        bullets.remove(
                            bullet
                        )

                    continue

            # =================================================
            # ENEMY COLLISION
            # =================================================

            for enemy in enemies[:]:

                if enemy in bullet.hit_targets:

                    continue

                if distance(
                    bullet.x,
                    bullet.y,
                    enemy.x,
                    enemy.y
                ) < (
                    enemy.radius +
                    8
                ):

                    bullet.hit_targets.append(
                        enemy
                    )

                    destroyed = enemy.hit(
                        bullet.damage
                    )

                    # =========================================
                    # DESTROYED
                    # =========================================

                    if destroyed:

                        if enemy in enemies:

                            enemies.remove(
                                enemy
                            )

                        # =====================================
                        # EXPLOSION
                        # =====================================

                        if bullet.explosive > 0:

                            explosion_radius = (
                                55 +
                                bullet.explosive *
                                20
                            )

                            cinematic_impact(
                                enemy.x,
                                enemy.y,
                                ORANGE,
                                0.65
                            )

                            explosion_damage = max(
                                1,
                                bullet.damage // 2
                            )

                            for other in enemies[:]:

                                if distance(
                                    enemy.x,
                                    enemy.y,
                                    other.x,
                                    other.y
                                ) < explosion_radius:

                                    if other.hit(
                                        explosion_damage
                                    ):

                                        if other in enemies:

                                            enemies.remove(
                                                other
                                            )

                    # =========================================
                    # PIERCING
                    # =========================================

                    if bullet.piercing > 0:

                        bullet.piercing -= 1

                    else:

                        bullet_hit = True

                    break

            if (
                bullet_hit
                and
                bullet in bullets
            ):

                bullets.remove(
                    bullet
                )

        # ====================================================
        # DRONES
        # ====================================================

        while len(
            drones
        ) < player.drone_count:

            drones.append(
                Drone(
                    len(drones)
                )
            )

        while len(
            drones
        ) > player.drone_count:

            drones.pop()

        for drone in drones:

            drone.update(
                dt
            )

        # ====================================================
        # SOLAR ORBS
        # ====================================================

        for orb in solar_orbs[:]:

            if not orb.update(
                dt
            ):

                if orb in solar_orbs:

                    solar_orbs.remove(
                        orb
                    )

        # ====================================================
        # BOSS
        # ====================================================

        if boss is not None:

            boss.update(
                dt
            )

            if boss.hp <= 0:

                score += (
                    5000 +
                    current_level *
                    1500
                )

                cinematic_impact(
                    boss.x,
                    boss.y,
                    boss.color,
                    6
                )

                spawn_particles(
                    boss.x,
                    boss.y,
                    GOLD,
                    250,
                    800
                )

                floating_text(
                    f"{boss.name} DEFEATED!",
                    WIDTH // 2,
                    HEIGHT // 2,
                    GOLD
                )

                boss = None

                enemy_projectiles.clear()

                complete_level()

        # ====================================================
        # NORMAL LEVEL COMPLETE
        # ====================================================

        if (
            not is_boss_level(
                current_level
            )
            and
            level_spawned >=
            level_enemy_target
            and
            len(enemies) == 0
            and
            not upgrade_active
            and
            game_state == "PLAYING"
            and
            last_upgrade_trigger >=
            wave_total
        ):

            complete_level()

        # ====================================================
        # RANDOM EVENTS
        # ====================================================

        update_event(
            dt
        )

        # ====================================================
        # UPGRADES
        # ====================================================

        if (
            not is_boss_level(
                current_level
            )
            and
            wave_number > 0
            and
            wave_number <= wave_total
            and
            wave_number !=
            last_upgrade_trigger
            and
            not upgrade_active
            and
            len(enemies) == 0
            and
            level_spawned >= min(
                level_enemy_target,
                wave_number *
                max(
                    4,
                    4 +
                    current_level // 3
                )
            )
            and
            game_state == "PLAYING"
        ):

            last_upgrade_trigger = (
                wave_number
            )

            choose_upgrade_options()

            upgrade_active = True

            game_state = "UPGRADE"

        # ====================================================
        # PROJECTILES
        # ====================================================

        for projectile in enemy_projectiles[:]:

            if not projectile.update(
                dt
            ):

                if projectile in enemy_projectiles:

                    enemy_projectiles.remove(
                        projectile
                    )

        # ====================================================
        # METEORS
        # ====================================================

        for meteor in meteors[:]:

            if not meteor.update(
                dt
            ):

                if meteor in meteors:

                    meteors.remove(
                        meteor
                    )

        # ====================================================
        # COMBO
        # ====================================================

        combo_timer -= dt

        if combo_timer <= 0:

            combo = 0

        # ====================================================
        # PARTICLES
        # ====================================================

        for particle in particles[:]:

            if not particle.update(
                dt
            ):

                particles.remove(
                    particle
                )

        # ====================================================
        # SHOCKWAVES
        # ====================================================

        for shockwave in shockwaves[:]:

            if not shockwave.update(
                dt
            ):

                shockwaves.remove(
                    shockwave
                )

        # ====================================================
        # FLOATING TEXT
        # ====================================================

        for text in floating_texts[:]:

            if not text.update(
                dt
            ):

                floating_texts.remove(
                    text
                )

        # ====================================================
        # BOSS BANNER
        # ====================================================

        boss_banner = max(
            0,
            boss_banner - dt
        )

        # ====================================================
        # PLAYER DEATH
        # ====================================================

        if player.hp <= 0:

            player.hp = 0

            game_state = "GAME_OVER"

            # Stop active combat immediately.
            enemies.clear()
            bullets.clear()
            enemy_projectiles.clear()
            meteors.clear()
            solar_orbs.clear()

            boss = None

            cinematic_impact(
                player.x,
                player.y,
                GOLD,
                4
            )

            spawn_particles(
                player.x,
                player.y,
                GOLD,
                150,
                650
            )

    # ========================================================
    # UPGRADE STATE
    # ========================================================

    elif game_state == "UPGRADE":

        for particle in particles[:]:

            if not particle.update(
                real_dt
            ):

                particles.remove(
                    particle
                )

        for shockwave in shockwaves[:]:

            if not shockwave.update(
                real_dt
            ):

                shockwaves.remove(
                    shockwave
                )

        for text in floating_texts[:]:

            if not text.update(
                real_dt
            ):

                floating_texts.remove(
                    text
                )

    # ========================================================
    # LEVEL COMPLETE
    # ========================================================

    elif game_state == "LEVEL_COMPLETE":

        level_complete_timer -= real_dt

        for particle in particles[:]:

            if not particle.update(
                real_dt
            ):

                particles.remove(
                    particle
                )

        for shockwave in shockwaves[:]:

            if not shockwave.update(
                real_dt
            ):

                shockwaves.remove(
                    shockwave
                )

        for text in floating_texts[:]:

            if not text.update(
                real_dt
            ):

                floating_texts.remove(
                    text
                )

        if level_complete_timer <= 0:

            game_state = "ROADMAP"

    # ========================================================
    # GAME OVER
    # ========================================================

    elif game_state == "GAME_OVER":

        for particle in particles[:]:

            if not particle.update(
                real_dt
            ):

                particles.remove(
                    particle
                )

        for shockwave in shockwaves[:]:

            if not shockwave.update(
                real_dt
            ):

                shockwaves.remove(
                    shockwave
                )

        for text in floating_texts[:]:

            if not text.update(
                real_dt
            ):

                floating_texts.remove(
                    text
                )

    # ========================================================
    # DRAW
    # ========================================================

    if game_state == "ROADMAP":

        draw_roadmap(
            pygame.time.get_ticks() / 1000
        )

    elif game_state == "PLAYING":

        draw_playing(
            pygame.time.get_ticks() / 1000
        )

    elif game_state == "UPGRADE":

        draw_playing(
            pygame.time.get_ticks() / 1000
        )

        draw_upgrade_screen()

    elif game_state == "LEVEL_COMPLETE":

        draw_level_complete()

    elif game_state == "GAME_OVER":

        draw_game_over()

    # ========================================================
    # IMPACT INVERT
    # ========================================================

    if impact_invert > 0:

        impact_invert -= real_dt

        phase = int(
            impact_invert * 38
        )

        impact_surface = pygame.Surface(
            (
                WIDTH,
                HEIGHT
            )
        )

        if phase % 2 == 0:

            impact_surface.fill(
                WHITE
            )

        else:

            impact_surface.fill(
                BLACK
            )

        alpha = int(
            180 *
            clamp(
                impact_invert /
                0.06,
                0,
                1
            )
        )

        impact_surface.set_alpha(
            alpha
        )

        screen.blit(
            impact_surface,
            (0, 0)
        )

    # ========================================================
    # IMPACT FLASH
    # ========================================================

    if impact_flash > 0:

        impact_flash -= real_dt

        alpha = int(
            90 *
            clamp(
                impact_flash /
                0.10,
                0,
                1
            )
            *
            impact_flash_strength
        )

        alpha = min(
            160,
            alpha
        )

        flash = pygame.Surface(
            (
                WIDTH,
                HEIGHT
            ),
            pygame.SRCALPHA
        )

        flash.fill(
            (
                255,
                210,
                120,
                alpha
            )
        )

        screen.blit(
            flash,
            (0, 0)
        )

    # ========================================================
    # VIGNETTE
    # ========================================================

    vignette = pygame.Surface(
        (
            WIDTH,
            HEIGHT
        ),
        pygame.SRCALPHA
    )

    pygame.draw.rect(
        vignette,
        (
            0,
            0,
            0,
            65
        ),
        (
            0,
            0,
            WIDTH,
            HEIGHT
        ),
        30
    )

    screen.blit(
        vignette,
        (0, 0)
    )

    # ========================================================
    # CAMERA SHAKE
    # ========================================================

    screen_shake *= 0.86

    if abs(screen_shake) < 0.05:

        screen_shake = 0

    # ========================================================
    # DISPLAY
    # ========================================================

    pygame.display.flip()


# ============================================================
# EXIT
# ============================================================

save_game()

# ------------------------------------------------------------
# CLOSE ONLINE CONNECTION
# ------------------------------------------------------------

if sock is not None:

    try:

        sock.close()

    except Exception:

        pass

online_connected = False

pygame.quit()

sys.exit()
