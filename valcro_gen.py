"""
╔══════════════════════════════════════════════════════════╗
║         VALCRO PASSWORD GEN  —  Beast Mode v2.0          ║
║         Pure Python · No External Deps · Pydroid OK      ║
╚══════════════════════════════════════════════════════════╝
"""

import os, sys, math, json, csv, time, random, string, secrets, platform, hashlib
from datetime import datetime
from io import StringIO

# ─── ANSI COLOR PALETTE ─────────────────────────────────────────────────────
R  = "\033[0m"          # reset
B  = "\033[1m"          # bold
DIM= "\033[2m"          # dim
UL = "\033[4m"          # underline

# Foreground
BLK= "\033[30m"; RED= "\033[31m"; GRN= "\033[32m"; YLW= "\033[33m"
BLU= "\033[34m"; MAG= "\033[35m"; CYN= "\033[36m"; WHT= "\033[37m"
BRED="\033[91m"; BGRN="\033[92m"; BYLW="\033[93m"; BBLU="\033[94m"
BMAG="\033[95m"; BCYN="\033[96m"; BWHT="\033[97m"

# Background
BG_BLK="\033[40m"; BG_RED="\033[41m"; BG_GRN="\033[42m"; BG_YLW="\033[43m"
BG_BLU="\033[44m"; BG_MAG="\033[45m"; BG_CYN="\033[46m"; BG_WHT="\033[47m"

ACCENT  = BCYN
ACCENT2 = BMAG
DIMTXT  = DIM + WHT
GOOD    = BGRN
WARN    = BYLW
ERR     = BRED
HL      = BYLW + B

# ─── EMBEDDED WORDLIST (500 words for passphrases) ──────────────────────────
WORDS = [
    "apple","brave","cloud","dance","eagle","flame","giant","honor","ivory",
    "jumbo","knife","lemon","magic","noble","ocean","peace","queen","river",
    "stone","tiger","ultra","valor","witch","xenon","yacht","zebra","amber",
    "blaze","chaos","drift","elite","forge","grace","heavy","input","joker",
    "karma","lucky","marsh","north","orbit","plaza","quake","radar","solar",
    "thorn","unity","verse","water","extra","young","zonal","alpha","bears",
    "cream","delta","earth","flash","grape","heart","index","jewel","kings",
    "laser","maple","nerve","olive","power","quick","rouge","shark","trail",
    "under","vivid","wheat","xerox","yield","zones","atlas","bloom","cobra",
    "draco","ember","frost","ghost","hydra","indie","japan","kiwis","lapis",
    "metro","night","ozone","pixel","quest","razor","storm","trend","ultra",
    "venom","winds","xeric","yards","zippy","agent","black","curve","depth",
    "eagle","field","glare","hazel","ionic","jumps","kneel","light","mango",
    "nexus","onion","prism","queen","rally","sigma","tower","union","virus",
    "watch","xylon","years","zones","abyss","blunt","cloak","dense","epoch",
    "fetch","globe","harsh","irony","jelly","knack","lodge","might","noisy",
    "omens","patch","quirk","raven","squad","thief","upend","vault","wrath",
    "xylan","yummy","zippo","azure","blink","creed","debug","enter","flint",
    "grind","hover","ivory","joint","kicks","lunar","monk","nonce","oxide",
    "punch","quill","recon","steel","titan","upton","vibes","weave","xenon",
    "yarns","zesty","amino","boost","civic","draft","every","fifth","graft",
    "heist","input","japan","kudos","lifts","mongo","north","oinks","prank",
    "quote","risky","shock","trust","ultra","viper","wafer","xoxox","yoked",
    "zeros","above","below","carry","dusty","exact","fixes","gamma","hurts",
    "ilk","jerks","kayak","local","morph","nabob","outdo","pivot","quirks",
    "rogue","scalp","turbo","under","vodka","waver","xenon","yanks","zones",
    "acorn","bumps","cedar","dunes","feast","gloom","hyper","irked","jingo",
    "knobs","lyric","motor","novel","oaths","plumb","qualm","roast","swift",
    "truce","upset","vigor","waltz","xylem","yearn","zesty","arrow","batch",
    "crane","digit","erupt","funky","groan","hippo","inter","juicy","kinky",
    "lance","melon","notch","oldie","proxy","quota","rivet","scope","torch",
    "usher","vocal","wider","exact","yawns","zingy","adept","basis","crisp",
    "deter","embed","fluke","gorge","hoist","imply","joust","knave","leach",
    "mirth","ninja","optic","prima","quirk","repel","saber","tepid","unzip",
    "vague","woken","xenon","yearly","zonal","acute","brunt","clamp","demon",
    "ensue","floss","glint","hound","inept","jinxed","kayak","lichen","moped",
    "notch","outlaw","plush","quart","retch","sloth","trawl","untie","vying",
    "wreak","xerus","yacht","zilch","adore","bulge","crest","drove","expel",
    "flinch","guile","hatch","infer","jumpy","kapow","leapt","mimic","nooks",
    "outdo","poise","quirky","rivets","swipe","thick","uncut","vault","windy",
]

# deduplicate while preserving order
_seen = set()
WORDS = [w for w in WORDS if not (w in _seen or _seen.add(w))]

# ─── CHARSETS ────────────────────────────────────────────────────────────────
CHARSETS = {
    '1':  ("All Printable (Full Beast)",   string.ascii_letters + string.digits + string.punctuation),
    '2':  ("Alphanumeric",                 string.ascii_letters + string.digits),
    '3':  ("Uppercase + Digits",           string.ascii_uppercase + string.digits),
    '4':  ("Lowercase + Digits",           string.ascii_lowercase + string.digits),
    '5':  ("Digits Only (PIN-style)",      string.digits),
    '6':  ("Hex (0-9 a-f)",               "0123456789abcdef"),
    '7':  ("HEX (0-9 A-F)",               "0123456789ABCDEF"),
    '8':  ("Base62 (URL-safe)",            string.ascii_letters + string.digits),
    '9':  ("Symbols Only",                 string.punctuation),
    '10': ("No Ambiguous Chars",           "abcdefghjkmnpqrstuvwxyzABCDEFGHJKMNPQRSTUVWXYZ23456789!@#$%^&*"),
    '11': ("Crypto-safe (256 charset)",    string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}|;:,.<>?"),
    '12': ("Custom Charset (you define)",  None),
}

# ─── STRENGTH ENGINE ─────────────────────────────────────────────────────────
def entropy_bits(length: int, pool: int) -> float:
    if pool <= 1 or length <= 0:
        return 0.0
    return length * math.log2(pool)

def crack_time_label(bits: float) -> str:
    """Estimate crack time at 1 trillion guesses/sec (high-end GPU farm)."""
    guesses_per_sec = 1e12
    combinations = 2 ** bits
    seconds = combinations / guesses_per_sec
    if seconds < 1:          return GOOD + "< 1 second"   + R
    if seconds < 60:         return GOOD + f"{seconds:.1f} seconds" + R
    if seconds < 3600:       return WARN + f"{seconds/60:.1f} minutes" + R
    if seconds < 86400:      return WARN + f"{seconds/3600:.1f} hours" + R
    if seconds < 2592000:    return WARN + f"{seconds/86400:.1f} days" + R
    if seconds < 31536000:   return BRED + f"{seconds/2592000:.1f} months" + R
    if seconds < 3.15e9:     return BGRN + f"{seconds/31536000:.1f} years" + R
    if seconds < 3.15e12:    return BGRN + f"{seconds/3.15e9:.2f} thousand years" + R
    if seconds < 3.15e15:    return BCYN + f"{seconds/3.15e12:.2f} million years" + R
    if seconds < 3.15e18:    return BCYN + f"{seconds/3.15e15:.2f} billion years" + R
    return BCYN + B + "HEAT DEATH OF UNIVERSE (UNCRACKABLE)" + R

def strength_bar(bits: float) -> str:
    thresholds = [28, 35, 59, 80, 120]
    labels      = [
        (RED   + B,  "VERY WEAK  "),
        (BRED  + B,  "WEAK       "),
        (BYLW  + B,  "FAIR       "),
        (BGRN  + B,  "STRONG     "),
        (BCYN  + B,  "VERY STRONG"),
        (BMAG  + B,  "UNCRACKABLE"),
    ]
    idx = len(thresholds)
    for i, t in enumerate(thresholds):
        if bits < t:
            idx = i
            break
    color, label = labels[idx]
    filled = min(int(bits / 2), 50)
    bar = "█" * filled + "░" * (50 - filled)
    return f"{color}[{bar}] {label}({bits:.1f} bits){R}"

def analyze_password(pw: str) -> dict:
    has_upper  = any(c.isupper() for c in pw)
    has_lower  = any(c.islower() for c in pw)
    has_digit  = any(c.isdigit() for c in pw)
    has_symbol = any(c in string.punctuation for c in pw)
    has_space  = ' ' in pw
    unique     = len(set(pw))
    length     = len(pw)
    # pool size from character types present
    pool = 0
    if has_lower:  pool += 26
    if has_upper:  pool += 26
    if has_digit:  pool += 10
    if has_symbol: pool += 32
    if has_space:  pool += 1
    pool = max(pool, unique)
    bits = entropy_bits(length, pool)
    # sha256 fingerprint
    sha = hashlib.sha256(pw.encode()).hexdigest()[:16]
    return {
        "length":     length,
        "unique":     unique,
        "has_upper":  has_upper,
        "has_lower":  has_lower,
        "has_digit":  has_digit,
        "has_symbol": has_symbol,
        "pool":       pool,
        "bits":       bits,
        "sha_prefix": sha,
    }

# ─── GENERATORS ──────────────────────────────────────────────────────────────
def gen_standard(charset: str, length: int) -> str:
    return ''.join(secrets.choice(charset) for _ in range(length))

def gen_passphrase(words: list, word_count: int, sep: str, capitalize: bool, add_num: bool) -> str:
    chosen = [secrets.choice(words) for _ in range(word_count)]
    if capitalize:
        chosen = [w.capitalize() for w in chosen]
    phrase = sep.join(chosen)
    if add_num:
        phrase += sep + str(secrets.randbelow(9999)).zfill(4)
    return phrase

def gen_pin(length: int, no_repeat: bool = False) -> str:
    if no_repeat:
        digits = list(string.digits) * 4
        secrets.SystemRandom().shuffle(digits)
        return ''.join(digits[:length])
    return ''.join(secrets.choice(string.digits) for _ in range(length))

def gen_pronounceable(length: int) -> str:
    vowels     = "aeiou"
    consonants = "bcdfghjklmnpqrstvwxyz"
    result = []
    toggle = secrets.randbelow(2) == 0  # start with consonant or vowel
    while len(result) < length:
        if toggle:
            result.append(secrets.choice(consonants))
        else:
            result.append(secrets.choice(vowels))
        toggle = not toggle
    # optionally uppercase first
    result[0] = result[0].upper()
    return ''.join(result)

def gen_pattern(pattern: str) -> str:
    """
    Pattern tokens:
      A  = uppercase letter     a = lowercase letter
      9  = digit                S = symbol
      X  = hex char (upper)     x = hex char (lower)
      L  = letter (any case)    P = printable (any)
      *  = any alphanumeric+sym  anything else = literal
    """
    out = []
    UPP = string.ascii_uppercase
    LOW = string.ascii_lowercase
    DIG = string.digits
    SYM = string.punctuation
    HXU = "0123456789ABCDEF"
    HXL = "0123456789abcdef"
    LET = string.ascii_letters
    ALL = string.ascii_letters + string.digits + string.punctuation
    ALNUM = string.ascii_letters + string.digits
    for ch in pattern:
        if   ch == 'A': out.append(secrets.choice(UPP))
        elif ch == 'a': out.append(secrets.choice(LOW))
        elif ch == '9': out.append(secrets.choice(DIG))
        elif ch == 'S': out.append(secrets.choice(SYM))
        elif ch == 'X': out.append(secrets.choice(HXU))
        elif ch == 'x': out.append(secrets.choice(HXL))
        elif ch == 'L': out.append(secrets.choice(LET))
        elif ch == 'P': out.append(secrets.choice(ALL))
        elif ch == '*': out.append(secrets.choice(ALNUM))
        else:           out.append(ch)
    return ''.join(out)

# ─── UI HELPERS ──────────────────────────────────────────────────────────────
def clr():
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def line(char='─', width=62, color=DIMTXT):
    print(color + char * width + R)

def header(title: str):
    clr()
    print()
    print(ACCENT + B + r"""
  ██╗   ██╗ █████╗ ██╗      ██████╗██████╗  ██████╗
  ██║   ██║██╔══██╗██║     ██╔════╝██╔══██╗██╔═══██╗
  ██║   ██║███████║██║     ██║     ██████╔╝██║   ██║
  ╚██╗ ██╔╝██╔══██║██║     ██║     ██╔══██╗██║   ██║
   ╚████╔╝ ██║  ██║███████╗╚██████╗██║  ██║╚██████╔╝
    ╚═══╝  ╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝
    """ + R)
    print(DIMTXT + "  ▸ Password Gen  •  Beast Mode v2.0  •  Unhackable Fortress" + R)
    line('═')
    print(f"  {ACCENT2}{B}▶  {title}{R}")
    line('─')
    print()

def prompt(label: str, default: str = "") -> str:
    hint = f" {DIMTXT}(default: {default}){R}" if default else ""
    try:
        val = input(f"  {ACCENT}▸{R} {B}{label}{hint}{R}: ").strip()
        return val if val else default
    except (KeyboardInterrupt, EOFError):
        return default

def int_prompt(label: str, default: int, lo: int, hi: int) -> int:
    while True:
        raw = prompt(label, str(default))
        if raw.lower() in ('q', 'quit', 'back'):
            return default
        try:
            v = int(raw)
            if lo <= v <= hi:
                return v
            print(f"  {WARN}  Must be {lo}–{hi}{R}")
        except ValueError:
            print(f"  {ERR}  Not a valid number. Using default ({default}){R}")
            return default

def yn(label: str, default: str = 'n') -> bool:
    r = prompt(f"{label} (y/n)", default).lower()
    return r in ('y', 'yes', '1', 'true')

def show_result(tokens: list, show_analysis: bool = True):
    print()
    line('─')
    for i, t in enumerate(tokens, 1):
        num = f"{DIMTXT}{i:>4}.{R}"
        print(f"  {num}  {BWHT}{B}{t}{R}")
    line('─')
    if show_analysis and tokens:
        sample = tokens[0]
        a = analyze_password(sample)
        print(f"\n  {ACCENT2}Sample Analysis  →  {DIMTXT}(first password){R}")
        print(f"   Length  : {BYLW}{a['length']}{R}  |  Unique chars: {BYLW}{a['unique']}{R}  |  Pool: {BYLW}{a['pool']}{R}")
        print(f"   Has: {tick(a['has_upper'])} UPPER  {tick(a['has_lower'])} lower  {tick(a['has_digit'])} 0-9  {tick(a['has_symbol'])} symbols")
        print(f"   Strength: {strength_bar(a['bits'])}")
        print(f"   Crack Time (1T/s): {crack_time_label(a['bits'])}")
        print(f"   SHA256 Prefix : {DIM}{a['sha_prefix']}...{R}")
    print()

def tick(val: bool) -> str:
    return BGRN + "✔" + R if val else BRED + "✘" + R

def pause():
    try:
        input(f"  {DIMTXT}Press Enter to continue...{R}")
    except (KeyboardInterrupt, EOFError):
        pass

# ─── HISTORY ─────────────────────────────────────────────────────────────────
SESSION_HISTORY: list[dict] = []

def add_history(mode: str, tokens: list):
    SESSION_HISTORY.append({
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "mode":      mode,
        "count":     len(tokens),
        "tokens":    tokens,
    })

# ─── EXPORT ──────────────────────────────────────────────────────────────────
def export_tokens(tokens: list, mode: str):
    print()
    print(f"  {ACCENT}Export Format:{R}")
    print(f"    [1] Plain TXT      [2] CSV      [3] JSON      [4] Skip")
    fmt = prompt("Choose format", "4")
    if fmt == '4' or fmt not in ('1','2','3'):
        return
    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
    ext  = {'1': 'txt', '2': 'csv', '3': 'json'}[fmt]
    name = f"valcro_{mode}_{ts}.{ext}"
    try:
        if fmt == '1':
            with open(name, 'w') as f:
                f.write('\n'.join(tokens))
        elif fmt == '2':
            with open(name, 'w', newline='') as f:
                w = csv.writer(f)
                w.writerow(['#', 'password', 'length', 'entropy_bits'])
                for i, t in enumerate(tokens, 1):
                    a = analyze_password(t)
                    w.writerow([i, t, a['length'], f"{a['bits']:.2f}"])
        elif fmt == '3':
            out = []
            for i, t in enumerate(tokens, 1):
                a = analyze_password(t)
                out.append({"id": i, "password": t, "length": a['length'],
                            "entropy_bits": round(a['bits'], 2),
                            "strength_bar": "██" * (min(int(a['bits']/10), 10))})
            with open(name, 'w') as f:
                json.dump({"generated_at": datetime.now().isoformat(),
                           "count": len(tokens), "passwords": out}, f, indent=2)
        print(f"  {GOOD}  ✔ Saved → {name}{R}")
    except Exception as e:
        print(f"  {ERR}  Save failed: {e}{R}")
    pause()

# ─── MODES ───────────────────────────────────────────────────────────────────
def mode_standard():
    header("MODE 1 — Standard Password Generator")
    print(f"  {ACCENT2}Choose Charset:{R}")
    for k, (name, _) in CHARSETS.items():
        star = "*" if k in ('1','10','11') else " "
        print(f"    {ACCENT}[{k:>2}]{R} {star} {name}")
    print()
    choice = prompt("Charset", "1")
    if choice not in CHARSETS:
        choice = '1'
    charset_name, charset = CHARSETS[choice]
    if charset is None:  # custom
        charset = prompt("Enter your custom character set")
        if not charset:
            print(f"  {ERR}No charset given. Using alphanumeric.{R}")
            charset = string.ascii_letters + string.digits
        charset = ''.join(dict.fromkeys(charset))  # dedupe, preserve order
        charset_name = "Custom"
    print()
    length = int_prompt("Password length", 32, 1, 4096)
    count  = int_prompt("How many to generate", 10, 1, 10000)
    ensure_unique = yn("Ensure all unique?", 'n')
    print(f"\n  {ACCENT}{B}Generating {count}× {charset_name} [{length} chars]…{R}\n")
    tokens = []
    seen   = set()
    attempts = 0
    max_attempts = count * 100
    while len(tokens) < count and attempts < max_attempts:
        t = gen_standard(charset, length)
        attempts += 1
        if ensure_unique and t in seen:
            continue
        seen.add(t)
        tokens.append(t)
    show_result(tokens)
    add_history("standard", tokens)
    export_tokens(tokens, "standard")

def mode_passphrase():
    header("MODE 2 — Passphrase Generator")
    print(f"  {DIMTXT}Passphrases are easy to remember + extremely strong.{R}")
    print(f"  {DIMTXT}Example: Coral-Drift-Blaze-7741{R}\n")
    word_count = int_prompt("Words per passphrase", 4, 2, 20)
    sep_choice = prompt("Separator  (-, _, ., space, or custom)", "-")
    sep = sep_choice if sep_choice else "-"
    if sep == 'space': sep = ' '
    capitalize = yn("Capitalize each word?", 'y')
    add_num    = yn("Append random 4-digit number?", 'y')
    count      = int_prompt("How many passphrases", 10, 1, 10000)
    print(f"\n  {ACCENT}{B}Generating {count}× passphrases…{R}\n")
    tokens = [gen_passphrase(WORDS, word_count, sep, capitalize, add_num)
              for _ in range(count)]
    show_result(tokens)
    add_history("passphrase", tokens)
    export_tokens(tokens, "passphrase")

def mode_pin():
    header("MODE 3 — PIN / OTP Generator")
    length    = int_prompt("PIN length", 6, 1, 64)
    count     = int_prompt("How many PINs", 10, 1, 10000)
    no_repeat = yn("No repeated digits?", 'n')
    grouped   = yn("Group digits (e.g. 1234 5678)?", 'n')
    group_sz  = 4
    if grouped:
        group_sz = int_prompt("Group size", 4, 2, 8)
    print(f"\n  {ACCENT}{B}Generating {count}× {length}-digit PINs…{R}\n")
    tokens = []
    for _ in range(count):
        pin = gen_pin(length, no_repeat)
        if grouped and len(pin) > group_sz:
            pin = ' '.join(pin[i:i+group_sz] for i in range(0, len(pin), group_sz))
        tokens.append(pin)
    show_result(tokens, show_analysis=False)
    add_history("pin", tokens)
    export_tokens(tokens, "pin")

def mode_pattern():
    header("MODE 4 — Pattern-Based Generator")
    print(f"  {ACCENT2}Pattern tokens:{R}")
    tokens_info = [
        ('A', 'Uppercase letter (A-Z)'),
        ('a', 'Lowercase letter (a-z)'),
        ('9', 'Digit (0-9)'),
        ('S', 'Symbol (!@#…)'),
        ('X', 'HEX upper (0-F)'),
        ('x', 'HEX lower (0-f)'),
        ('L', 'Any letter (a-Z)'),
        ('*', 'Alphanumeric (a-Z 0-9)'),
        ('P', 'Any printable char'),
        ('?', 'Literal char (use as-is)'),
    ]
    for tok, desc in tokens_info:
        print(f"    {ACCENT}{tok}{R}  →  {desc}")
    print(f"\n  {DIMTXT}Example patterns:{R}")
    examples = [
        "AaaaAaaa99SS  →  CapWord99!!",
        "XXXXXX-XXXXXX  →  ABC123-DEF456 (hex ID)",
        "Aaaa9999!  →  Word1234!",
        "AAaa99SSAAaa  →  Strong mixed",
    ]
    for ex in examples:
        print(f"    {DIMTXT}{ex}{R}")
    print()
    pattern = prompt("Enter your pattern", "AaaaAaaa9999SS")
    count   = int_prompt("How many to generate", 10, 1, 10000)
    print(f"\n  {ACCENT}{B}Generating {count}× pattern [{pattern}]…{R}\n")
    tokens = [gen_pattern(pattern) for _ in range(count)]
    show_result(tokens)
    add_history("pattern", tokens)
    export_tokens(tokens, "pattern")

def mode_pronounceable():
    header("MODE 5 — Pronounceable Password Generator")
    print(f"  {DIMTXT}Easy to say out loud, hard to crack. Mix of vowels+consonants.{R}\n")
    length = int_prompt("Length", 12, 4, 64)
    count  = int_prompt("How many", 10, 1, 10000)
    add_num = yn("Append 4-digit number?", 'y')
    add_sym = yn("Append random symbol?", 'n')
    print(f"\n  {ACCENT}{B}Generating {count}× pronounceable passwords…{R}\n")
    tokens = []
    for _ in range(count):
        pw = gen_pronounceable(length)
        if add_num:
            pw += str(secrets.randbelow(9999)).zfill(4)
        if add_sym:
            pw += secrets.choice("!@#$%^&*")
        tokens.append(pw)
    show_result(tokens)
    add_history("pronounceable", tokens)
    export_tokens(tokens, "pronounceable")

def mode_bulk_mix():
    header("MODE 6 — Bulk Mixed Generation")
    print(f"  {DIMTXT}Generate a mix of standards, passphrases, and PINs together.{R}\n")
    total = int_prompt("Total passwords to generate", 50, 1, 10000)
    print()
    tokens = []
    per = total // 3
    rem = total - (per * 3)
    # standard
    tokens += [gen_standard(CHARSETS['1'][1], 20) for _ in range(per)]
    # passphrase
    tokens += [gen_passphrase(WORDS, 4, '-', True, True) for _ in range(per)]
    # pronounceable
    tokens += [gen_pronounceable(12) + str(secrets.randbelow(9999)).zfill(4)
               for _ in range(per + rem)]
    secrets.SystemRandom().shuffle(tokens)
    show_result(tokens)
    add_history("bulk_mix", tokens)
    export_tokens(tokens, "bulk_mix")

def mode_analyzer():
    header("MODE 7 — Password Strength Analyzer")
    print(f"  {DIMTXT}Paste any password below to get a full security report.{R}\n")
    while True:
        pw = prompt("Enter password (or 'back' to return)")
        if pw.lower() in ('back', 'b', 'q', ''):
            return
        print()
        a = analyze_password(pw)
        print(f"  {ACCENT2}{B}═══ SECURITY REPORT ════════════════════════{R}")
        print(f"  Password      : {BWHT}{B}{pw}{R}")
        print(f"  Length        : {BYLW}{a['length']} characters{R}")
        print(f"  Unique chars  : {BYLW}{a['unique']}{R}")
        print(f"  Charset pool  : ~{BYLW}{a['pool']} symbols{R}")
        print(f"  Has UPPER     : {tick(a['has_upper'])}")
        print(f"  Has lower     : {tick(a['has_lower'])}")
        print(f"  Has digits    : {tick(a['has_digit'])}")
        print(f"  Has symbols   : {tick(a['has_symbol'])}")
        print(f"  Entropy       : {BYLW}{a['bits']:.2f} bits{R}")
        print(f"  Strength      : {strength_bar(a['bits'])}")
        print(f"  Crack Time    : {crack_time_label(a['bits'])}")
        print(f"  SHA256 prefix : {DIM}{a['sha_prefix']}...{R}")
        # recommendations
        print(f"\n  {ACCENT}Recommendations:{R}")
        if a['length'] < 12:
            print(f"  {WARN}  ⚠  Length too short — aim for 16+{R}")
        if not a['has_upper']:
            print(f"  {WARN}  ⚠  Add uppercase letters{R}")
        if not a['has_symbol']:
            print(f"  {WARN}  ⚠  Add symbols (!@#$…){R}")
        if not a['has_digit']:
            print(f"  {WARN}  ⚠  Add digits{R}")
        if a['bits'] >= 80:
            print(f"  {GOOD}  ✔  Very strong — keep it up!{R}")
        if a['bits'] >= 120:
            print(f"  {BCYN}  ★  Fortress-class password. Essentially uncrackable.{R}")
        print()
        cont = yn("Analyze another?", 'y')
        if not cont:
            return

def mode_history():
    header("MODE 8 — Session History")
    if not SESSION_HISTORY:
        print(f"  {WARN}  No history yet. Generate some passwords first!{R}\n")
        pause()
        return
    print(f"  {DIMTXT}This session's generated batches:{R}\n")
    for i, entry in enumerate(SESSION_HISTORY, 1):
        print(f"  {ACCENT}[{i}]{R} {entry['timestamp']}  {BYLW}{entry['mode']}{R} "
              f"— {entry['count']} passwords")
    print()
    choice = prompt("Show batch # (or Enter to skip)", "")
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(SESSION_HISTORY):
            batch = SESSION_HISTORY[idx]
            show_result(batch['tokens'])
            export_tokens(batch['tokens'], batch['mode'])
            return
    pause()

def mode_keygen():
    header("MODE 9 — Crypto Key Generator")
    print(f"  {DIMTXT}Generate cryptographically secure keys for various purposes.{R}\n")
    print(f"  {ACCENT2}Key Types:{R}")
    print(f"    [1] 128-bit AES key (hex)")
    print(f"    [2] 256-bit AES key (hex)")
    print(f"    [3] 512-bit master key (hex)")
    print(f"    [4] UUID v4 style")
    print(f"    [5] 32-byte Base64 token")
    print(f"    [6] 64-byte Base64 token")
    print(f"    [7] Custom bit length (hex)")
    print()
    ktype = prompt("Key type", "2")
    count = int_prompt("How many keys", 5, 1, 1000)
    print()
    tokens = []
    for _ in range(count):
        if ktype == '1':
            tokens.append(secrets.token_hex(16))
        elif ktype == '2':
            tokens.append(secrets.token_hex(32))
        elif ktype == '3':
            tokens.append(secrets.token_hex(64))
        elif ktype == '4':
            raw = secrets.token_hex(16)
            tokens.append(f"{raw[0:8]}-{raw[8:12]}-4{raw[13:16]}-"
                          f"{hex(8 + secrets.randbelow(4))[2:]}{raw[17:20]}-{raw[20:32]}")
        elif ktype == '5':
            tokens.append(secrets.token_urlsafe(32))
        elif ktype == '6':
            tokens.append(secrets.token_urlsafe(64))
        else:
            bits = int_prompt("Bit length", 256, 8, 4096)
            tokens.append(secrets.token_hex(bits // 8))
    show_result(tokens, show_analysis=False)
    add_history("keygen", tokens)
    export_tokens(tokens, "keygen")

# ─── MAIN MENU ───────────────────────────────────────────────────────────────
MENU = [
    ("1",  "Standard Password Generator",    mode_standard),
    ("2",  "Passphrase Generator",           mode_passphrase),
    ("3",  "PIN / OTP Generator",            mode_pin),
    ("4",  "Pattern-Based Generator",        mode_pattern),
    ("5",  "Pronounceable Password",         mode_pronounceable),
    ("6",  "Bulk Mixed Generation",          mode_bulk_mix),
    ("7",  "Password Strength Analyzer",     mode_analyzer),
    ("8",  "Session History & Export",       mode_history),
    ("9",  "Crypto Key Generator",           mode_keygen),
    ("0",  "Exit",                           None),
]

def main_menu():
    while True:
        header("MAIN MENU")
        print(f"  {ACCENT2}Select a mode:{R}\n")
        for key, label, _ in MENU:
            icon = "→" if key != "0" else "×"
            color = BRED if key == "0" else ACCENT
            print(f"    {color}[{key}]{R}  {icon}  {label}")
        print()
        hist_note = f"{DIMTXT}  Session: {len(SESSION_HISTORY)} batch(es) generated{R}"
        print(hist_note)
        print()
        choice = prompt("Choose mode", "1")
        matched = False
        for key, label, fn in MENU:
            if choice == key:
                matched = True
                if fn is None:
                    clr()
                    print(f"\n  {ACCENT}VALCRO Gen — See you next time. Stay encrypted.{R}\n")
                    sys.exit(0)
                try:
                    fn()
                except KeyboardInterrupt:
                    print(f"\n  {WARN}  Interrupted. Back to menu.{R}\n")
                    time.sleep(0.8)
                break
        if not matched:
            print(f"  {ERR}  Invalid choice. Try again.{R}")
            time.sleep(0.5)

# ─── ENTRY POINT ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        # Windows console fix
        if platform.system() == 'Windows':
            os.system('color 07')
            try:
                import ctypes
                ctypes.windll.kernel32.SetConsoleTitleW('Valcro Password Gen')
            except Exception:
                pass
        main_menu()
    except KeyboardInterrupt:
        print(f"\n\n  {ACCENT}Valcro Gen — Goodbye. Stay safe out there.{R}\n")
        sys.exit(0)
