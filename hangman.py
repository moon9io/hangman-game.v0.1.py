#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔══════════════════════════════════════════════════════════╗
║               HANGMAN — المشنوق                          ║
║            Word Guessing Game · v4.0                     ║
║                    by moon9io                            ║
║               LYCEE  AZIZ BELAL                          ║
║                ABD EMONIM                                ║
╚══════════════════════════════════════════════════════════╝
"""

import random
import os
import sys
import json
import time
import datetime
import shutil
import threading
import re
import math
import struct
import wave
import tempfile
import subprocess
from colorama import init, Fore, Back, Style

init(autoreset=True)

#
#  TERMINAL UTILITIES
#

def term_width():
    """Get current terminal width"""
    return shutil.get_terminal_size((80, 24)).columns

def term_height():
    return shutil.get_terminal_size((80, 24)).lines

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def strip_ansi(s):
    return re.sub(r'\x1b\[[0-9;]*m', '', s)

def visible_len(s):
    return len(strip_ansi(s))

def hline(char='─', color=Fore.LIGHTBLACK_EX, width=None):
    w = width or term_width()
    print(color + (char * min(w, 120)) + Style.RESET_ALL)

def center_print(text, width=None):
    w = width or term_width()
    pad = max(0, (w - visible_len(text)) // 2)
    print(' ' * pad + text)

def pad_right(text, width):
    return text + ' ' * max(0, width - visible_len(text))

def typewrite(text, delay=0.015):
    if not sys.stdout.isatty():
        print(text)
        return
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def blink_line(text, times=2, pause=0.1):
    for _ in range(times):
        sys.stdout.write('\r' + text)
        sys.stdout.flush()
        time.sleep(pause)
        sys.stdout.write('\r' + ' ' * visible_len(text))
        sys.stdout.flush()
        time.sleep(pause * 0.7)
    sys.stdout.write('\r' + text + '\n')
    sys.stdout.flush()

def spinner(msg, seconds):
    frames = ['⠋','⠙','⠹','⠸','⠼','⠴','⠦','⠧','⠇','⠏']
    end = time.time() + seconds
    i = 0
    while time.time() < end:
        sys.stdout.write(f"\r  {Fore.CYAN}{frames[i%len(frames)]}{Style.RESET_ALL}  {msg}")
        sys.stdout.flush()
        time.sleep(0.07)
        i += 1
    sys.stdout.write('\r' + ' ' * 60 + '\r')
    sys.stdout.flush()

def draw_box(lines, color=Fore.CYAN, width=None):
    w = width or (max(visible_len(l) for l in lines) + 4 if lines else 40)
    out = [color + '╔' + '═'*(w-2) + '╗' + Style.RESET_ALL]
    for l in lines:
        out.append(color + '║' + Style.RESET_ALL + ' ' + pad_right(l, w-4) + ' ' + color + '║' + Style.RESET_ALL)
    out.append(color + '╚' + '═'*(w-2) + '╝' + Style.RESET_ALL)
    return out

def two_column(left, right, sep='   '):
    lw = max((visible_len(l) for l in left), default=0)
    n = max(len(left), len(right))
    left  = left + [''] * (n - len(left))
    right = right + [''] * (n - len(right))
    return [pad_right(l, lw) + sep + r for l, r in zip(left, right)]

def print_lines(lines):
    for l in lines:
        print(l)

#
#  AUDIO ENGINE — pure python, no external files

_sfx_on = True
_music_on = False
_music_stop = threading.Event()
_music_thread = None

def _make_wav(filename, samples, rate=22050):
    with wave.open(filename, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(b''.join(
            struct.pack('<h', max(-32767, min(32767, int(s)))) for s in samples))

def _sine_wave(freq, duration, rate=22050, volume=0.4, fade=0.06):
    n = int(rate * duration)
    fade_n = int(rate * fade)
    out = []
    for i in range(n):
        amp = math.sin(2 * math.pi * freq * i / rate)
        env = min(i / fade_n, 1.0, (n - i) / fade_n) if fade_n else 1.0
        out.append(amp * env * volume * 32767)
    return out

def _chord(frequencies, duration, volume=0.28, rate=22050):
    n = int(rate * duration)
    out = [0.0] * n
    for f in frequencies:
        for i, s in enumerate(_sine_wave(f, duration, rate, volume / len(frequencies))):
            out[i] += s
    return out

def _play(samples, rate=22050, block=False):
    if not _sfx_on:
        return
    def _do():
        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                tmpname = tmp.name
            _make_wav(tmpname, samples, rate)
            if sys.platform == 'win32':
                import winsound
                flags = winsound.SND_FILENAME | (0 if block else winsound.SND_ASYNC)
                winsound.PlaySound(tmpname, flags)
            elif sys.platform == 'darwin':
                p = subprocess.Popen(['afplay', tmpname],
                                     stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL)
                if block:
                    p.wait()
            else:
                for cmd in [['aplay', '-q', tmpname],
                            ['paplay', tmpname],
                            ['play', '-q', tmpname]]:
                    try:
                        p = subprocess.Popen(cmd,
                                             stdout=subprocess.DEVNULL,
                                             stderr=subprocess.DEVNULL)
                        if block:
                            p.wait()
                        return
                    except FileNotFoundError:
                        continue
        except Exception:
            pass
    if block:
        _do()
    else:
        threading.Thread(target=_do, daemon=True).start()

class Sounds:
    @staticmethod
    def correct():
        _play(_sine_wave(523, 0.07) + _sine_wave(659, 0.07) + _sine_wave(784, 0.13))

    @staticmethod
    def wrong():
        _play(_sine_wave(311, 0.09, volume=0.35) + _sine_wave(220, 0.16, volume=0.3))

    @staticmethod
    def win():
        s = []
        for n in [523, 659, 784, 1047, 1319]:
            s += _sine_wave(n, 0.11, volume=0.38)
        s += _chord([523, 659, 784], 0.5, volume=0.42)
        _play(s)

    @staticmethod
    def lose():
        s = []
        for n in [440, 370, 311, 247]:
            s += _sine_wave(n, 0.14, volume=0.32)
        _play(s)

    @staticmethod
    def hint():
        _play(_chord([880, 1100], 0.08) + _chord([1047, 1319], 0.16))

    @staticmethod
    def achievement():
        s = []
        for n in [523, 659, 784, 880, 1047, 1319]:
            s += _sine_wave(n, 0.09, volume=0.36)
        s += _chord([659, 784, 988], 0.45, volume=0.4)
        _play(s)

    @staticmethod
    def click():
        _play(_sine_wave(1200, 0.025, volume=0.18))

    @staticmethod
    def danger():
        _play(_sine_wave(220, 0.11, volume=0.38) + _sine_wave(185, 0.09, volume=0.3))

    @staticmethod
    def fanfare():
        s = []
        for n in [523, 523, 659, 784, 784, 659, 523, 659, 784, 1047]:
            s += _sine_wave(n, 0.10, volume=0.36)
        _play(s)

    @staticmethod
    def tick():
        _play(_sine_wave(900, 0.03, volume=0.12))

# background music
_PENTA = [261, 293, 329, 392, 440, 523, 587, 659, 784, 880]

def _music_loop():
    i = 0
    while not _music_stop.is_set():
        if _sfx_on:
            _play(_sine_wave(_PENTA[i % len(_PENTA)],
                              random.choice([0.18, 0.22, 0.28]),
                              volume=0.10),
                  block=True)
            time.sleep(random.uniform(0.04, 0.18))
        else:
            time.sleep(0.3)
        i += 1

def music_start():
    global _music_on, _music_thread
    _music_on = True
    _music_stop.clear()
    _music_thread = threading.Thread(target=_music_loop, daemon=True)
    _music_thread.start()

def music_stop():
    global _music_on
    _music_on = False
    _music_stop.set()

#  COLOR PALETTE
#
R   = Style.RESET_ALL
B   = Style.BRIGHT
D   = Style.DIM
CY  = Fore.CYAN + B
cy  = Fore.CYAN
YL  = Fore.YELLOW + B
yl  = Fore.YELLOW
GR  = Fore.GREEN + B
gr  = Fore.GREEN
RD  = Fore.RED + B
rd  = Fore.RED
MG  = Fore.MAGENTA + B
mg  = Fore.MAGENTA
WH  = Fore.WHITE + B
wh  = Fore.WHITE
BL  = Fore.BLUE + B
bl  = Fore.BLUE
GY  = Fore.WHITE + D
gy  = Fore.LIGHTBLACK_EX

HIGR = Back.GREEN + Fore.BLACK + B
HIRD = Back.RED + Fore.WHITE + B
HICY = Back.CYAN + Fore.BLACK + B
HIMG = Back.MAGENTA + Fore.WHITE + B
HIYL = Back.YELLOW + Fore.BLACK + B

#
#  GALLOWS DRAWING (responsive)

HANGMAN_PICS = [
    f"""
    {Fore.WHITE}---------
    |       |
    |
    |
    |
    |
    ---------{Style.RESET_ALL}
    """,
    f"""
    {Fore.WHITE}---------
    |       |
    |       O
    |
    |
    |
    ---------{Style.RESET_ALL}
    """,
    f"""
    {Fore.WHITE}---------
    |       |
    |       O
    |       |
    |
    |
    ---------{Style.RESET_ALL}
    """,
    f"""
    {Fore.WHITE}---------
    |       |
    |       O
    |      /|
    |
    |
    ---------{Style.RESET_ALL}
    """,
    f"""
    {Fore.WHITE}---------
    |       |
    |       O
    |      /|\\
    |
    |
    ---------{Style.RESET_ALL}
    """,
    f"""
    {Fore.WHITE}---------
    |       |
    |       O
    |      /|\\
    |      /
    |
    ---------{Style.RESET_ALL}
    """,
    f"""
    {Fore.WHITE}---------
    |       |
    |       {Fore.RED}O{Fore.WHITE}
    |      {Fore.RED}/|\\{Fore.WHITE}
    |      {Fore.RED}/ \\{Fore.WHITE}
    |
    ---------{Style.RESET_ALL}
    """
]

def _gallows_color(mistakes, max_mistakes):
    if max_mistakes == 0:
        return GR
    r = mistakes / max_mistakes
    if r == 0:
        return GR
    if r < 0.34:
        return YL
    if r < 0.5:
        return yl
    if r < 0.67:
        return mg
    if r < 0.84:
        return rd
    return RD

def draw_gallows_large(mistakes, max_mistakes):
    # استخدام الرسم الثابت من HANGMAN_PICS
    if max_mistakes == 0:
        index = 0
    else:
        index = int((mistakes / max_mistakes) * (len(HANGMAN_PICS) - 1))
        index = max(0, min(index, len(HANGMAN_PICS)-1))
    lines = HANGMAN_PICS[index].splitlines()
    # إزالة الأسطر الفارغة من البداية (إن وجدت)
    while lines and lines[0].strip() == '':
        lines.pop(0)
    while lines and lines[-1].strip() == '':
        lines.pop()
    return lines

def draw_gallows_medium(mistakes, max_mistakes):
    # يمكن استخدام نفس الرسم للشاشات المتوسطة
    return draw_gallows_large(mistakes, max_mistakes)

def draw_gallows_mini(mistakes, max_mistakes):
    # تصميم مبسط للشاشات الضيقة
    pc = _gallows_color(mistakes, max_mistakes)
    bc = GY

    def show(part):
        return mistakes >= max(1, round(max_mistakes * part / 6))

    head = pc + 'O' + R if show(1) else '_'
    neck = pc + '|' + R if show(2) else ' '
    arms = (pc + '/' + ('\\' if show(4) else '') + R) if show(3) else ' ' + ('\\' + R if show(4) else '')
    legs = (pc + '/' + ('\\' if show(6) else '') + R) if show(5) else ' ' + ('\\' + R if show(6) else '')

    return [
        f" {bc}┌─┐{R}",
        f" {bc}│ {R}{head}",
        f" {bc}│{R}{neck}",
        f" {bc}│{R}{arms}",
        f" {bc}│{R}{legs}",
        f" {bc}╧═{R}",
    ]

def draw_gallows(mistakes, max_mistakes):
    w = term_width()
    if w >= 70:
        return draw_gallows_large(mistakes, max_mistakes)
    if w >= 45:
        return draw_gallows_medium(mistakes, max_mistakes)
    return draw_gallows_mini(mistakes, max_mistakes)
#
#  KEYBOARD LAYOUT
#

_EN_ROWS = [list('qwertyuiop'), list('asdfghjkl'), list('zxcvbnm')]
_AR_ROWS = [list('ضصثقفغعهخح'), list('جشسيبلاتنم'), list('كطئءؤرىةوز')]

def draw_keyboard(guessed, correct, wrong, lang):
    rows = _EN_ROWS if lang == 'en' else _AR_ROWS
    width = term_width()
    compact = width < 55
    print(f"\n{CY}⌨  {'Keyboard' if lang=='en' else 'لوحة المفاتيح'}{R}")
    for row in rows:
        line = '  '
        for ch in row:
            if ch in wrong:
                line += (RD + f'[{ch}]' + R + ' ') if not compact else (RD + ch + R + ' ')
            elif ch in correct:
                line += (GR + f'[{ch}]' + R + ' ') if not compact else (GR + ch + R + ' ')
            elif ch in guessed:
                line += GY + '·  ' + R if not compact else GY + '· ' + R
            else:
                line += WH + f' {ch} ' + R + ' '
        print(line)

#
#  WORD DISPLAY
#

def display_word(word, guessed, reveal=False):
    parts = []
    for ch in word:
        if ch == ' ':
            parts.append('    ')
            continue
        if ch in guessed:
            parts.append(f" {GR}{B}{ch.upper()}{R} ")
        elif reveal:
            parts.append(f" {RD}{B}{ch.upper()}{R} ")
        else:
            parts.append(f" {WH}_{R} ")
    return ' '.join(parts)

def display_word_boxes(word, guessed, reveal=False):
    top, mid, bot = '', '', ''
    for ch in word:
        if ch == ' ':
            top += '    '
            mid += '    '
            bot += '    '
            continue
        if ch in guessed:
            top += f"{GR}┌─┐{R} "
            mid += f"{GR}│{ch.upper()}│{R} "
            bot += f"{GR}└─┘{R} "
        elif reveal:
            top += f"{RD}┌─┐{R} "
            mid += f"{RD}│{ch.upper()}│{R} "
            bot += f"{RD}└─┘{R} "
        else:
            top += f"{GY}┌─┐{R} "
            mid += f"{GY}│ │{R} "
            bot += f"{GY}└─┘{R} "
    return [f"    {top}", f"    {mid}", f"    {bot}"]

#  PROGRESS BARS
#

def progress_bar(current, total, length=18, invert=False):
    if total == 0:
        return GY + '░' * length + R
    ratio = current / total
    if invert:
        ratio = 1 - ratio
    filled = int(ratio * length)
    if ratio > 0.6:
        col = GR
    elif ratio > 0.3:
        col = YL
    else:
        col = RD
    return col + '█' * filled + GY + '░' * (length - filled) + R

def time_bar(remaining, total, length=None):
    w = min(term_width() - 20, 30)
    if length is not None:
        w = length
    if total == 0:
        return ''
    ratio = remaining / total
    if ratio > 0.5:
        col = GR
    elif ratio > 0.25:
        col = YL
    else:
        col = RD + B
    filled = int(ratio * w)
    icon = '⏱' if remaining > 15 else '⚠'
    return f"{icon} {col}{'█'*filled}{GY}{'░'*(w-filled)}{R} {col}{remaining:>3}s{R}"

#
#  GAME DATA
#

DIFFICULTY = {
    'easy':   {'en':'Easy',   'ar':'سهل',   'tries':8, 'time':120, 'mult':1.0, 'hcost':20},
    'medium': {'en':'Medium', 'ar':'متوسط', 'tries':6, 'time':90,  'mult':1.5, 'hcost':35},
    'hard':   {'en':'Hard',   'ar':'صعب',   'tries':4, 'time':60,  'mult':2.0, 'hcost':50},
}

ACHIEVEMENTS = [
    {'id':'first_win',   'icon':'🎯','en':'First Blood',  'ar':'الدم الأول',
     'desc_en':'Win your first game',  'desc_ar':'اربح أول لعبة',
     'cond':lambda s:s['wins']>=1},
    {'id':'flawless',    'icon':'✨','en':'Flawless',     'ar':'مثالي',
     'desc_en':'Win with zero mistakes','desc_ar':'بدون أي خطأ',
     'cond':lambda s:s.get('perfect',False)},
    {'id':'on_fire',     'icon':'🔥','en':'On Fire',      'ar':'مشتعل',
     'desc_en':'Win 3 games in a row','desc_ar':'3 انتصارات متتالية',
     'cond':lambda s:s.get('streak',0)>=3},
    {'id':'lightning',   'icon':'⚡','en':'Lightning',    'ar':'البرق',
     'desc_en':'Win 5 games in a row','desc_ar':'5 انتصارات متتالية',
     'cond':lambda s:s.get('streak',0)>=5},
    {'id':'half_grand',  'icon':'💰','en':'Half a Grand', 'ar':'نصف الألف',
     'desc_en':'Reach 500 points',    'desc_ar':'500 نقطة',
     'cond':lambda s:s['points']>=500},
    {'id':'millie',      'icon':'👑','en':'Millionaire',  'ar':'الملك',
     'desc_en':'Reach 1000 points',   'desc_ar':'1000 نقطة',
     'cond':lambda s:s['points']>=1000},
    {'id':'no_hints',    'icon':'🧠','en':'No Cheating',  'ar':'بدون غش',
     'desc_en':'Win 5 games without hints','desc_ar':'5 انتصارات بدون تلميحات',
     'cond':lambda s:s.get('wnh',0)>=5},
    {'id':'speed',       'icon':'⏱','en':'Speed Runner', 'ar':'السريع',
     'desc_en':'Win in under 20 sec','desc_ar':'الفوز في أقل من 20 ثانية',
     'cond':lambda s:s.get('best_t',999)<=20},
    {'id':'bilingual',   'icon':'🌍','en':'Bilingual',    'ar':'ثنائي اللغة',
     'desc_en':'Win in both languages','desc_ar':'الفوز باللغتين',
     'cond':lambda s:s.get('wins_ar',0)>0 and s.get('wins_en',0)>0},
    {'id':'veteran',     'icon':'🎖','en':'Veteran',      'ar':'محارب قديم',
     'desc_en':'Play 20 games',      'desc_ar':'20 لعبة',
     'cond':lambda s:(s['wins']+s['losses'])>=20},
    {'id':'comeback',    'icon':'🦅','en':'Comeback King','ar':'ملك العودة',
     'desc_en':'Win after 3 losses in a row','desc_ar':'الفوز بعد 3 هزائم متتالية',
     'cond':lambda s:s.get('comeback',False)},
    {'id':'collect5',    'icon':'🎁','en':'Collector',    'ar':'جامع',
     'desc_en':'Unlock 5 achievements','desc_ar':'فتح 5 إنجازات',
     'cond':lambda s:len(s.get('unlocked',[]))>=5},
    {'id':'two_k',       'icon':'💎','en':'Diamond',      'ar':'الماسة',
     'desc_en':'Reach 2000 points',   'desc_ar':'2000 نقطة',
     'cond':lambda s:s['points']>=2000},
    {'id':'streak10',    'icon':'🌪','en':'Tornado',      'ar':'الإعصار',
     'desc_en':'Win 10 games in a row','desc_ar':'10 انتصارات متتالية',
     'cond':lambda s:s.get('streak',0)>=10},
]

# Word banks
EN_WORDS = [
    {"w":"algorithm",  "cat":"CS",       "h":"Step-by-step problem-solving procedure"},
    {"w":"variable",   "cat":"Code",     "h":"A named container storing a value in memory"},
    {"w":"function",   "cat":"Code",     "h":"A reusable named block of code"},
    {"w":"database",   "cat":"Tech",     "h":"Organised, structured storage for data"},
    {"w":"recursion",  "cat":"Code",     "h":"When a function calls itself"},
    {"w":"framework",  "cat":"Dev",      "h":"A ready-made structure for building apps"},
    {"w":"encryption", "cat":"Security", "h":"Scrambling data to keep it private"},
    {"w":"debugging",  "cat":"Code",     "h":"Finding and fixing errors in programs"},
    {"w":"compiler",   "cat":"CS",       "h":"Translates source code to machine language"},
    {"w":"interface",  "cat":"Design",   "h":"Point of interaction between user and system"},
    {"w":"python",     "cat":"Lang",     "h":"A snake AND a hugely popular language"},
    {"w":"keyboard",   "cat":"HW",       "h":"You are typing on one right now"},
    {"w":"network",    "cat":"Tech",     "h":"Interconnected devices sharing resources"},
    {"w":"browser",    "cat":"Tech",     "h":"Chrome, Firefox, Safari…"},
    {"w":"software",   "cat":"Tech",     "h":"Programs and applications"},
    {"w":"hardware",   "cat":"Tech",     "h":"Physical computer components"},
    {"w":"syntax",     "cat":"Code",     "h":"Grammar rules of a programming language"},
    {"w":"binary",     "cat":"CS",       "h":"Number system using only 0s and 1s"},
    {"w":"server",     "cat":"Tech",     "h":"Provides services over a network"},
    {"w":"pixel",      "cat":"Graphics", "h":"Smallest unit in a digital image"},
    {"w":"galaxy",     "cat":"Space",    "h":"Billions of stars bound by gravity"},
    {"w":"quantum",    "cat":"Physics",  "h":"Smallest discrete unit of a quantity"},
    {"w":"hangman",    "cat":"Game",     "h":"The very game you are playing!"},
    {"w":"achievement","cat":"Game",     "h":"A badge for completing a challenge"},
    {"w":"leaderboard","cat":"Game",     "h":"Ranking of top players by score"},
]

AR_WORDS = [
    {"w":"خوارزمية", "cat":"علوم حاسوب","h":"خطوات منطقية لحل مشكلة"},
    {"w":"برمجة",    "cat":"تقنية",     "h":"كتابة تعليمات يفهمها الحاسوب"},
    {"w":"شبكة",     "cat":"تقنية",     "h":"ربط الأجهزة ببعضها لتبادل البيانات"},
    {"w":"متغير",    "cat":"كود",       "h":"وعاء يحمل قيمة في الذاكرة"},
    {"w":"دالة",     "cat":"كود",       "h":"كتلة كود قابلة للاستدعاء"},
    {"w":"واجهة",    "cat":"تصميم",     "h":"ما يراه المستخدم ويتفاعل معه"},
    {"w":"خادم",     "cat":"تقنية",     "h":"يوفر خدمات للأجهزة الأخرى عبر الشبكة"},
    {"w":"تشفير",    "cat":"أمن",       "h":"تحويل البيانات لصيغة غير مقروءة"},
    {"w":"ذاكرة",    "cat":"أجهزة",     "h":"التخزين المؤقت في الحاسوب"},
    {"w":"معالج",    "cat":"أجهزة",     "h":"عقل الحاسوب المنفذ للعمليات"},
    {"w":"نظام",     "cat":"عام",       "h":"مجموعة عناصر مترابطة تعمل معاً"},
    {"w":"تطبيق",    "cat":"تقنية",     "h":"برنامج مصمم لمهام محددة"},
    {"w":"سحابة",    "cat":"تقنية",     "h":"تخزين البيانات عبر الإنترنت"},
    {"w":"ذكاء",     "cat":"علوم",      "h":"القدرة على التعلم وحل المشكلات"},
    {"w":"بيانات",   "cat":"علوم",      "h":"معلومات خام لم تُعالج بعد"},
    {"w":"اتصال",    "cat":"شبكات",     "h":"تبادل المعلومات بين طرفين"},
    {"w":"روبوت",    "cat":"تقنية",     "h":"آلة تعمل تلقائياً وتحاكي الإنسان"},
    {"w":"تصميم",    "cat":"إبداع",     "h":"عملية التخطيط والإنشاء الجمالي"},
    {"w":"امان",     "cat":"تقنية",     "h":"حماية المعلومات من التهديدات"},
    {"w":"كود",      "cat":"برمجة",     "h":"تعليمات برمجية يفهمها الحاسوب"},
    {"w":"مشنوق",    "cat":"لعبة",      "h":"اسم هذه اللعبة نفسها!"},
    {"w":"مبرمج",    "cat":"مهنة",      "h":"شخص يكتب الكود ليعيش"},
    {"w":"إنترنت",   "cat":"تقنية",     "h":"شبكة عالمية تربط مليارات الأجهزة"},
    {"w":"حاسوب",    "cat":"أجهزة",     "h":"جهاز إلكتروني يعالج البيانات"},
    {"w":"متصفح",    "cat":"تقنية",     "h":"كروم وفايرفوكس وسفاري"},
]

#  PERSISTENCE (JSON)
#

PLAYER_FILE = 'hangman_players.json'
DAILY_FILE  = 'hangman_daily.json'

DEFAULT_STATS = {
    'points': 0,
    'wins': 0,
    'losses': 0,
    'streak': 0,
    'best_streak': 0,
    'wins_ar': 0,
    'wins_en': 0,
    'wnh': 0,
    'total_games': 0,
    'total_time': 0.0,
    'perfect': False,
    'best_t': 999.0,
    'loss_streak': 0,
    'comeback': False,
    'unlocked': []
}

def load_players():
    try:
        with open(PLAYER_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_players(players):
    with open(PLAYER_FILE, 'w', encoding='utf-8') as f:
        json.dump(players, f, ensure_ascii=False, indent=2)

def get_player(name):
    players = load_players()
    if name not in players:
        players[name] = DEFAULT_STATS.copy()
    # ensure all keys exist
    for k, v in DEFAULT_STATS.items():
        players[name].setdefault(k, v)
    save_players(players)
    return players[name]

def save_player(name, stats):
    players = load_players()
    players[name] = stats
    save_players(players)

def check_achievements(stats):
    new = []
    for ach in ACHIEVEMENTS:
        if ach['id'] not in stats['unlocked'] and ach['cond'](stats):
            stats['unlocked'].append(ach['id'])
            new.append(ach)
    return new

def daily_challenge():
    try:
        with open(DAILY_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if data.get('date') == datetime.date.today().isoformat():
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    lang = random.choice(['ar', 'en'])
    word = random.choice(AR_WORDS if lang == 'ar' else EN_WORDS)
    challenge = {
        'date': datetime.date.today().isoformat(),
        'lang': lang,
        'w': word['w'],
        'h': word['h'],
        'cat': word.get('cat', '?')
    }
    with open(DAILY_FILE, 'w', encoding='utf-8') as f:
        json.dump(challenge, f, ensure_ascii=False, indent=2)
    return challenge

#  SCREENS (achievements, leaderboard, stats)
#

def show_achievements(stats, lang):
    clear()
    w = term_width()
    hline('═', YL, w)
    center_print(f"{YL}🏆  {'ACHIEVEMENTS' if lang=='en' else 'الإنجازات'}{R}", w)
    hline('═', YL, w)
    unlocked = len(stats['unlocked'])
    total = len(ACHIEVEMENTS)
    print(f"\n  {progress_bar(unlocked, total, 28)}  {CY}{unlocked}/{total}{R}\n")

    half = total // 2 + total % 2
    left  = []
    right = []
    for i, ach in enumerate(ACHIEVEMENTS):
        ul = ach['id'] in stats['unlocked']
        icon = ach['icon'] if ul else '🔒'
        status = f"{HIGR} ✔ {R}" if ul else f"{GY} · {R}"
        name = ach['en'] if lang=='en' else ach['ar']
        desc = ach['desc_en'] if lang=='en' else ach['desc_ar']
        line = f"  {status} {icon}  {GR if ul else GY}{name}{R}  {GY}—{R}  {GY if not ul else gr}{desc}{R}"
        if i < half:
            left.append(line)
        else:
            right.append(line)

    if w >= 100:
        for l, r in zip(left + ['']*(len(right)-len(left)), right + ['']*(len(left)-len(right))):
            print(pad_right(l or '', 50) + '  │  ' + (r or ''))
    else:
        for l in left + right:
            print(l)

    hline('─', GY, w)
    input(f"\n  {GY}{'Press Enter...' if lang=='en' else 'اضغط Enter...'}{R}")

def show_leaderboard(lang):
    clear()
    w = term_width()
    hline('═', MG, w)
    center_print(f"{MG}🏅  {'LEADERBOARD — Top 10' if lang=='en' else 'قادة النقاط — أفضل 10'}{R}", w)
    hline('═', MG, w)

    players = load_players()
    if not players:
        print(f"\n  {GY}{'No players yet.' if lang=='en' else 'لا يوجد لاعبون بعد.'}{R}")
    else:
        ranked = sorted(players.items(), key=lambda x: x[1].get('points',0), reverse=True)[:10]
        print(f"  {CY}{'#':<4}{'Username':<22}{'Pts':>7}{'W':>5}{'L':>5}{'🔥':>5}{'Ach':>5}{R}")
        hline('─', GY, 55)
        medals = ['🥇','🥈','🥉']
        for i, (name, st) in enumerate(ranked, 1):
            if i <= 3:
                col = YL if i==1 else WH if i==2 else yl
                rank = medals[i-1]
            else:
                col = GY
                rank = f'{i}.'
            print(f"  {col}{rank:<4}{name[:20]:<22}{st.get('points',0):>7}"
                  f"{st.get('wins',0):>5}{st.get('losses',0):>5}"
                  f"{st.get('streak',0):>5}{len(st.get('unlocked',[])):>5}{R}")

    hline('─', GY, w)
    input(f"\n  {GY}{'Press Enter...' if lang=='en' else 'اضغط Enter...'}{R}")

def show_stats(name, stats, lang):
    clear()
    w = term_width()
    hline('═', BL, w)
    center_print(f"{BL}📊  {'STATISTICS' if lang=='en' else 'إحصائيات'}  —  {name}{R}", w)
    hline('═', BL, w)

    total = stats['wins'] + stats['losses']
    winrate = f"{stats['wins']/total*100:.1f}%" if total else 'N/A'
    avg_time = f"{stats['total_time']/total:.1f}s" if total else 'N/A'
    best = f"{stats.get('best_t',999):.1f}s" if stats.get('best_t',999) < 999 else 'N/A'

    left = [
        f"  {GY}{'Points':<20}{R} {YL}{stats['points']}{R}",
        f"  {GY}{'Wins':<20}{R} {GR}{stats['wins']}{R}",
        f"  {GY}{'Losses':<20}{R} {RD}{stats['losses']}{R}",
        f"  {GY}{'Win rate':<20}{R} {CY}{winrate}{R}",
        f"  {GY}{'Current streak':<20}{R} {MG}{stats['streak']}{R}",
        f"  {GY}{'Best streak':<20}{R} {MG}{stats.get('best_streak',0)}{R}",
        f"  {GY}{'Fastest win':<20}{R} {CY}{best}{R}",
        f"  {GY}{'Average time':<20}{R} {CY}{avg_time}{R}",
    ]
    right = [
        f"  {GY}{'No‑hint wins':<20}{R} {GR}{stats.get('wnh',0)}{R}",
        f"  {GY}{'Wins in Arabic':<20}{R} {CY}{stats.get('wins_ar',0)}{R}",
        f"  {GY}{'Wins in English':<20}{R} {CY}{stats.get('wins_en',0)}{R}",
        f"  {GY}{'Total games':<20}{R} {WH}{total}{R}",
        f"",
        f"  {GY}{'Achievements':<20}{R} {YL}{len(stats['unlocked'])}/{len(ACHIEVEMENTS)}{R}",
        f"  {progress_bar(len(stats['unlocked']), len(ACHIEVEMENTS), 20)}",
    ]

    if w >= 80:
        for l, r in zip(left + ['']*(len(right)-len(left)), right + ['']*(len(left)-len(right))):
            if l or r:
                print((l or '') + '  │  ' + (r or ''))
    else:
        for line in left + right:
            if line.strip():
                print(line)

    hline('─', GY, w)
    input(f"\n  {GY}{'Press Enter...' if lang=='en' else 'اضغط Enter...'}{R}")

#  GAME LOOP
#

def play_game(user, stats, lang, difficulty, custom_word=None):
    global _sfx_on

    cfg = DIFFICULTY[difficulty]
    max_tries = cfg['tries']
    time_limit = cfg['time']
    multiplier = cfg['mult']
    hint_cost = cfg['hcost']

    if custom_word:
        wdata = custom_word
    else:
        wdata = random.choice(AR_WORDS if lang=='ar' else EN_WORDS)

    word = wdata['w'].lower()
    hint_text = wdata['h']
    category = wdata.get('cat', '')

    letters = set(c for c in word if c != ' ')
    guessed = set()
    correct = set()
    wrong = set()
    mistakes = 0
    hint_used = False
    combo = 0
    start = time.time()
    active = True
    danger_played = False

    while letters and mistakes < max_tries and active:
        elapsed = time.time() - start
        remaining = max(0, int(time_limit - elapsed))
        if remaining <= 0:
            break
        if remaining <= 10 and not danger_played:
            Sounds.danger()
            danger_played = True

        # render screen
        clear()
        w = term_width()
        # header
        print()
        stats_line = f"  {CY}{user}{R}  ⚡{YL}{stats['points']:>5}{R}pts  ✔{GR}{stats['wins']:>2}{R}  ✘{RD}{stats['losses']:>2}{R}  🔥{MG}{stats['streak']}{R}"
        hline('─', GY, w)
        print(stats_line)
        hline('─', GY, w)
        print()


        for line in draw_gallows(mistakes, max_tries):
            print(line)
        print()


        if w >= 60:
            for line in display_word_boxes(word, guessed):
                print(line)
        else:
            print(f"    {display_word(word, guessed)}")
        print()


        found = sum(1 for c in set(c for c in word if c!=' ') if c in guessed)
        total_u = len(set(c for c in word if c!=' '))
        print(f"  {progress_bar(found, total_u, 16)}  {gr}{found}/{total_u} {'letters' if lang=='en' else 'حرف'}{R}")
        print(f"  {'Mistakes' if lang=='en' else 'الأخطاء'}: {progress_bar(mistakes, max_tries, 14, invert=True)}  ({RD}{mistakes}{R}/{GY}{max_tries}{R})")
        print(f"  {time_bar(remaining, time_limit)}")
        if combo > 1:
            print(f"\n  {HIMG} ×{combo} COMBO! {R}")
        if wrong:
            wrong_str = '  '.join(f"{RD}{c.upper()}{R}" for c in sorted(wrong))
            print(f"\n  {'Wrong' if lang=='en' else 'خاطئة'}: {wrong_str}")
        if hint_used:
            print(f"\n  {MG}💡 {hint_text}{R}")
        else:
            cost_color = YL if stats['points'] >= hint_cost else RD
            print(f"\n  {GY}💡 [H] {'Hint' if lang=='en' else 'تلميح'} {cost_color}{hint_cost}pts{R}")

        # keyboard
        draw_keyboard(guessed, correct, wrong, lang)

        # command bar
        print(f"\n  {GY}{'─'*min(w-4, 68)}{R}")
        if w >= 60:
            opts = [
                f"{WH}[letter]{R} {'Guess' if lang=='en' else 'تخمين'}",
                f"{WH}[H]{R} {'Hint' if lang=='en' else 'تلميح'}",
                f"{WH}[A]{R} {'Ach' if lang=='en' else 'إنجازات'}",
                f"{WH}[S]{R} {'Sound' if lang=='en' else 'صوت'}",
                f"{WH}[Q]{R} {'Quit' if lang=='en' else 'خروج'}",
            ]
            print('  ' + '   '.join(opts))
        else:
            print(f"  {WH}[letter]{R} guess  {WH}[H]{R} hint  {WH}[Q]{R} quit")
        print(f"  {GY}{'─'*min(w-4, 68)}{R}")

        # input
        cmd = input(f"\n  {YL}→  {R}").strip().lower()

        if cmd in ('q','quit','exit'):
            active = False
            break
        if cmd == 'a':
            Sounds.click()
            show_achievements(stats, lang)
            continue
        if cmd == 's':
            _sfx_on = not _sfx_on
            Sounds.click()
            continue
        if cmd in ('h','hint'):
            if hint_used:
                print(f"\n  {RD}{'Hint already used!' if lang=='en' else 'التلميح مستخدم!'}{R}")
            elif stats['points'] < hint_cost:
                print(f"\n  {RD}{'Not enough points!' if lang=='en' else 'نقاط غير كافية!'}{R}")
                Sounds.wrong()
            else:
                stats['points'] -= hint_cost
                hint_used = True
                Sounds.hint()
                print(f"\n  {MG}💡 {hint_text}{R}")
            time.sleep(1.2)
            continue

        # guess a letter
        ch = None
        if len(cmd) == 1 and (cmd.isalpha() or ord(cmd) > 127):
            ch = cmd
        else:
            # ask again
            ch = input(f"  {CY}{'Letter:' if lang=='en' else 'الحرف:'} {R}").strip().lower()
            if ch:
                ch = ch[0]

        if not ch or ch in guessed:
            continue

        guessed.add(ch)
        if ch in letters:
            letters.remove(ch)
            correct.add(ch)
            combo += 1
            points = int(10 * multiplier) + (combo - 1) * 3
            stats['points'] += points
            Sounds.correct()
            msg = f"{'Correct! +' if lang=='en' else 'صحيح! +'}{points}pts"
            if combo > 1:
                msg += f"  ×{combo}"
            print(f"\n  {GR}{msg}{R}")
        else:
            wrong.add(ch)
            mistakes += 1
            combo = 0
            Sounds.wrong()
            print(f"\n  {RD}{'Wrong!' if lang=='en' else 'خطأ!'}  ({max_tries-mistakes} {'left' if lang=='en' else 'متبقية'}){R}")
        time.sleep(0.7)

    # game ended
    elapsed = time.time() - start
    won = (not letters) and active

    clear()
    w = term_width()
    print()
    hline('─', GY, w)
    print(f"  {CY}{user}{R}  ⚡{YL}{stats['points']}{R}pts  ✔{GR}{stats['wins']}{R}  ✘{RD}{stats['losses']}{R}  🔥{MG}{stats['streak']}{R}")
    hline('─', GY, w)
    print()


    final_mis = mistakes if won else max_tries
    for line in draw_gallows(final_mis, max_tries):
        print(line)
    print()


    if w >= 60:
        for line in display_word_boxes(word, guessed, reveal=not won):
            print(line)
    else:
        print(f"    {display_word(word, guessed, reveal=not won)}")
    print()

    if won:
        time_bonus = max(0, int((time_limit - elapsed) / 2))
        combo_bonus = int(combo * 4)
        earned = int(50 * multiplier) + time_bonus + combo_bonus

        stats['points'] += earned
        stats['wins'] += 1
        stats['streak'] += 1
        stats['best_streak'] = max(stats['streak'], stats.get('best_streak', 0))
        stats['perfect'] = (mistakes == 0)
        stats['loss_streak'] = 0
        if elapsed < stats.get('best_t', 999):
            stats['best_t'] = elapsed
        if lang == 'ar':
            stats['wins_ar'] += 1
        else:
            stats['wins_en'] += 1
        if not hint_used:
            stats['wnh'] += 1

        Sounds.win()
        blink_line(f"  {HIGR}  ✔  {'YOU WIN!' if lang=='en' else 'فزت!'}  {R}", times=2)
        print(f"\n  {GY}{'Base:':>14}{R} {YL}+{int(50*multiplier)}{R}")
        if time_bonus:
            print(f"  {GY}{'Time bonus:':>14}{R} {CY}+{time_bonus}{R}")
        if combo_bonus:
            print(f"  {GY}{'Combo bonus:':>14}{R} {MG}+{combo_bonus}{R}")
        hline('─', GY, 30)
        print(f"  {GY}{'Total earned:':>14}{R} {YL}{B}+{earned}{R}")
        print(f"  {GY}{'Time:':>14}{R} {CY}{elapsed:.1f}s{R}")
    else:
        stats['losses'] += 1
        stats['streak'] = 0
        stats['perfect'] = False
        stats['loss_streak'] = stats.get('loss_streak', 0) + 1
        Sounds.lose()
        if not active:
            print(f"  {GY}{'Game abandoned.' if lang=='en' else 'تم التخلي عن اللعبة.'}{R}")
        else:
            blink_line(f"  {HIRD}  ✘  {'YOU LOST!' if lang=='en' else 'خسرت!'}  {R}", times=2)
            print(f"\n  {'The word was:' if lang=='en' else 'الكلمة كانت:'} {YL}{B}{word.upper()}{R}")

    # comeback achievement
    if won and stats.get('loss_streak', 0) >= 3:
        stats['comeback'] = True

    stats['total_games'] += 1
    stats['total_time'] += elapsed
    save_player(user, stats)

    new_achs = check_achievements(stats)
    if new_achs:
        save_player(user, stats)
        print(f"\n  {YL}{'═'*min(w-4,54)}{R}")
        center_print(f"{CY}{'🏆 Achievement Unlocked!' if lang=='en' else '🏆 إنجاز جديد!'}{R}", w)
        for a in new_achs:
            Sounds.achievement()
            name = a['en'] if lang=='en' else a['ar']
            desc = a['desc_en'] if lang=='en' else a['desc_ar']
            typewrite(f"  {a['icon']}  {GR}{B}{name}{R}  —  {GY}{desc}{R}", delay=0.012)
            time.sleep(0.3)
        print(f"  {YL}{'═'*min(w-4,54)}{R}")

    input(f"\n  {GY}{'Press Enter...' if lang=='en' else 'اضغط Enter...'}{R}")

#  DAILY CHALLENGE
#

def play_daily(user, stats, lang):
    chal = daily_challenge()
    today = datetime.date.today().strftime('%A, %d %B %Y')
    clear()
    w = term_width()
    center_print(f"{YL}★  {'DAILY CHALLENGE' if lang=='en' else 'تحدي اليوم'}  ★{R}", w)
    print(f"\n  {GY}{today}{R}")
    print(f"  {'Language:' if lang=='en' else 'اللغة:'} {CY}{chal['lang'].upper()}{R}  "
          f"{'Difficulty: MEDIUM ×2' if lang=='en' else 'الصعوبة: متوسط ×2'}")

    if chal['lang'] != lang:
        lang_name = 'Arabic / العربية' if chal['lang']=='ar' else 'English / الإنجليزية'
        print(f"\n  {YL}{'Today\'s challenge is in' if lang=='en' else 'تحدي اليوم باللغة'}: {lang_name}{R}")
        input(f"\n  {GY}{'Press Enter...' if lang=='en' else 'اضغط Enter...'}{R}")
        return

    input(f"\n  {GY}{'Press Enter to start...' if lang=='en' else 'اضغط Enter للبدء...'}{R}")
    play_game(user, stats, chal['lang'], 'medium',
              custom_word={'w': chal['w'], 'h': chal['h'], 'cat': '⭐ Daily'})
    stats['points'] += 200
    save_player(user, stats)
    print(f"\n  {MG}⭐ +200 bonus points!{R}")
    input(f"\n  {GY}{'Press Enter...' if lang=='en' else 'اضغط Enter...'}{R}")

#  DIFFICULTY SELECTION

def change_difficulty(lang, current):
    clear()
    w = term_width()
    hline('═', CY, w)
    center_print(f"{CY}⚙  {'DIFFICULTY' if lang=='en' else 'الصعوبة'}{R}", w)
    hline('═', CY, w)
    print()
    colors = {'easy': GR, 'medium': YL, 'hard': RD}
    for key, cfg in DIFFICULTY.items():
        col = colors[key]
        mark = f"  {HICY} ← current {R}" if key == current else ''
        name = cfg['en'] if lang=='en' else cfg['ar']
        print(f"  {col}[{key[0].upper()}]{R}  {col}{B}{name:<10}{R}  "
              f"{GY}tries:{cfg['tries']}  time:{cfg['time']}s  ×{cfg['mult']}  "
              f"hint:{cfg['hcost']}pts{R}{mark}")
    print()
    while True:
        choice = input(f"  {YL}{'Choice (E/M/H) or Enter to cancel:' if lang=='en' else 'اختيار (E/M/H) أو Enter للإلغاء:'} {R}").strip().upper()
        if choice == '':
            return current
        if choice == 'E':
            Sounds.click()
            return 'easy'
        if choice == 'M':
            Sounds.click()
            return 'medium'
        if choice == 'H':
            Sounds.click()
            return 'hard'
        print(f"  {RD}{'Type E, M, or H.' if lang=='en' else 'اكتب E أو M أو H.'}{R}")

#  MAIN MENU

def main_menu(user, stats, lang, difficulty):
    clear()
    w = term_width()
    # big title
    if w >= 70:
        print(f"""
{YL}  ██╗  ██╗ █████╗ ███╗   ██╗ ██████╗ ███╗   ███╗ █████╗ ███╗   ██╗{R}
{YL}  ██║  ██║██╔══██╗████╗  ██║██╔════╝ ████╗ ████║██╔══██╗████╗  ██║{R}
{YL}  ███████║███████║██╔██╗ ██║██║  ███╗██╔████╔██║███████║██╔██╗ ██║{R}
{yl}  ██╔══██║██╔══██║██║╚██╗██║██║   ██║██║╚██╔╝██║██╔══██║██║╚██╗██║{R}
{yl}  ██║  ██║██║  ██║██║ ╚████║╚██████╔╝██║ ╚═╝ ██║██║  ██║██║ ╚████║{R}
{GY}  ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝{R}""")
    elif w >= 40:
        print(f"""
  {YL}█▄█ ▄▀█ █▄ █ █▀▀ █▀▄▀█ ▄▀█ █▄ █{R}
  {yl}█ █ █▀█ █ ▀█ █▄█ █ ▀ █ █▀█ █ ▀█{R}""")
    else:
        print(f"  {YL}╔══╗ HANGMAN{R}")

    center_print(f"{CY}المشنوق · Word Guessing Game · v4.0{R}", w)
    print()

    # stats bar
    hline('─', GY, w)
    print(f"  {CY}{user}{R}  ⚡{YL}{stats['points']:>5}{R}pts  ✔{GR}{stats['wins']:>2}{R}  ✘{RD}{stats['losses']:>2}{R}  🔥{MG}{stats['streak']}{R}")
    hline('─', GY, w)

    # menu items
    items = [
        ('1', '▶  Start Game', GR),
        ('2', '⚙  Difficulty', CY),
        ('3', '🏆  Achievements', YL),
        ('4', '🏅  Leaderboard', MG),
        ('5', '⭐  Daily Challenge', BL),
        ('6', '📊  Statistics', bl),
        ('7', '♪   Sound', cy),
        ('8', '♫   Music', cy),
        ('9', '🌍  Language', WH),
        ('0', '⏻   Exit', GY),
    ]
    if lang == 'ar':
        items = [
            ('1', '▶  ابدأ اللعب', GR),
            ('2', '⚙  الصعوبة', CY),
            ('3', '🏆  الإنجازات', YL),
            ('4', '🏅  قادة النقاط', MG),
            ('5', '⭐  تحدي اليوم', BL),
            ('6', '📊  إحصائيات', bl),
            ('7', '♪   الصوت', cy),
            ('8', '♫   الموسيقى', cy),
            ('9', '🌍  اللغة', WH),
            ('0', '⏻   خروج', GY),
        ]

    # layout menu
    if w >= 80:
        half = len(items) // 2
        left = items[:half]
        right = items[half:]
        col_w = 38
        print(f"\n  {CY}╔{'═'*(col_w*2+6)}╗{R}")
        for i in range(max(len(left), len(right))):
            def fmt(it):
                if not it:
                    return ' ' * (col_w+4)
                k, lbl, col = it
                sfx = ''
                if k == '7':
                    sfx = f" {GR}ON{R}" if _sfx_on else f" {RD}OFF{R}"
                if k == '8':
                    sfx = f" {GR}ON{R}" if _music_on else f" {RD}OFF{R}"
                raw = f"  {GY}[{k}]{R}  {col}{lbl}{R}{sfx}"
                return pad_right(raw, col_w+6)
            li = left[i] if i < len(left) else None
            ri = right[i] if i < len(right) else None
            print(f"  {CY}║{R} {fmt(li)}  {CY}│{R}  {fmt(ri)} {CY}║{R}")
        print(f"  {CY}╚{'═'*(col_w*2+6)}╝{R}")
    else:
        #
        print(f"\n  {CY}╔{'═'*(min(w-4,40))}╗{R}")
        for k, lbl, col in items:
            sfx = ''
            if k == '7':
                sfx = f" {GR}ON{R}" if _sfx_on else f" {RD}OFF{R}"
            if k == '8':
                sfx = f" {GR}ON{R}" if _music_on else f" {RD}OFF{R}"
            raw = f"  {GY}[{k}]{R}  {col}{lbl}{R}{sfx}"
            print(f"  {CY}║{R}{raw}")
        print(f"  {CY}╚{'═'*(min(w-4,40))}╝{R}")

#
#  ENTRY POINT
#

def main():
    clear()
    w = term_width()
    center_print(f"{CY}Welcome!  /  أهلاً بك!{R}", w)
    print()
    username = input(f"  {YL}Username / اسم المستخدم: {R}").strip()
    if not username:
        username = 'Player'

    while True:
        lang = input(f"  {YL}Language / اللغة  [en / ar]: {R}").strip().lower()
        if lang in ('en', 'ar'):
            break
        print(f"  {RD}Please type 'en' or 'ar' — اكتب 'en' أو 'ar'{R}")

    stats = get_player(username)
    diff = 'medium'

    spinner(f"{'Loading…' if lang=='en' else 'جارٍ التحميل…'}", 0.7)

    while True:
        main_menu(username, stats, lang, diff)
        choice = input(f"\n  {YL}→  {R}").strip().lower()

        if choice == '1':
            Sounds.click()
            play_game(username, stats, lang, diff)
        elif choice == '2':
            Sounds.click()
            diff = change_difficulty(lang, diff)
        elif choice == '3':
            Sounds.click()
            show_achievements(stats, lang)
        elif choice == '4':
            Sounds.click()
            show_leaderboard(lang)
        elif choice == '5':
            Sounds.click()
            play_daily(username, stats, lang)
        elif choice == '6':
            Sounds.click()
            show_stats(username, stats, lang)
        elif choice == '7':
            _sfx_on = not _sfx_on
            Sounds.click()
            status = 'ON' if _sfx_on else 'OFF'
            print(f"\n  {GY}{'Sound effects:' if lang=='en' else 'المؤثرات الصوتية:'} {GR if _sfx_on else RD}{status}{R}")
            time.sleep(0.8)
        elif choice == '8':
            if _music_on:
                music_stop()
                status = 'OFF'
            else:
                music_start()
                status = 'ON'
            print(f"\n  {GY}{'Music:' if lang=='en' else 'الموسيقى:'} {GR if _music_on else RD}{status}{R}")
            time.sleep(0.8)
        elif choice == '9':
            lang = 'ar' if lang == 'en' else 'en'
            Sounds.click()
            print(f"\n  {MG}{'→ Arabic' if lang=='ar' else '→ English'}{R}")
            time.sleep(0.6)
        elif choice == '0':
            clear()
            print()
            typewrite(f"  {YL}{'Thanks for playing. Goodbye! 👋' if lang=='en' else 'شكراً للعب معنا. مع السلامة! 👋'}{R}", delay=0.02)
            music_stop()
            time.sleep(0.5)
            sys.exit(0)
        else:
            print(f"\n  {RD}{'Invalid choice.' if lang=='en' else 'اختيار غير صحيح.'}{R}")
            time.sleep(0.8)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        music_stop()
        print(f"\n\n  {YL}Goodbye! مع السلامة! 👋{R}\n")
        sys.exit(0)
