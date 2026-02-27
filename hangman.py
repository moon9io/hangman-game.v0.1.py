#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   لغبة المشنو#
#
#
#
#
#
"""
HANGMAN - المشنوق
لعبة تخمين الكلمات المتطورة مع نظام نقاط وإنجازات ومتصدرين
"""

import random
import os
import sys
import json
import time
import datetime
from colorama import init, Fore, Back, Style
import pyfiglet

# تهيئة colorama
init(autoreset=True)

# ------------------------ إعدادات ديال الألوان ------------------------
COLOR_TITLE = Fore.YELLOW + Style.BRIGHT
COLOR_WORD = Fore.CYAN + Style.BRIGHT
COLOR_CORRECT = Fore.GREEN
COLOR_WRONG = Fore.RED
COLOR_HINT = Fore.MAGENTA
COLOR_POINTS = Fore.LIGHTYELLOW_EX
COLOR_RESET = Style.RESET_ALL

# ------------------------ إعدادات ديال الصوت ------------------------
def beep(frequency=1000, duration=200):
    """إصدار صوت بسيط (يعمل على ويندوز ولينكس)"""
    try:
        import winsound
        winsound.Beep(frequency, duration)
    except ImportError:
        try:
            # محاولة استخدام beep على لينكس
            os.system(f'play -n synth {duration/1000} sin {frequency} >/dev/null 2>&1')
        except:
            pass  # تجاهل الأخطاء

# ------------------------ إعدادات ديال الصعوبة ------------------------
DIFFICULTY_SETTINGS = {
    'easy':   {'name_en': 'Easy',   'name_ar': 'سهل',   'max_tries': 8, 'time_limit': 120, 'points_multiplier': 1.0},
    'medium': {'name_en': 'Medium', 'name_ar': 'متوسط', 'max_tries': 6, 'time_limit': 90,  'points_multiplier': 1.5},
    'hard':   {'name_en': 'Hard',   'name_ar': 'صعب',   'max_tries': 4, 'time_limit': 60,  'points_multiplier': 2.0}
}

# ------------------------ الاتشيفمنت ------------------------
ACHIEVEMENTS = [
    {'id': 'first_win',      'icon': '🎯', 'name_en': 'First Blood',    'name_ar': 'الدم الأول',
     'desc_en': 'Win your first game',    'desc_ar': 'افوز بأول لعبة',
     'condition': lambda s: s['wins'] >= 1},
    {'id': 'flawless',       'icon': '✨', 'name_en': 'Flawless',        'name_ar': 'لا تشوبها شائبة',
     'desc_en': 'Win with zero mistakes', 'desc_ar': 'افوز بدون أخطاء',
     'condition': lambda s: s.get('last_perfect', False)},
    {'id': 'on_fire',        'icon': '🔥', 'name_en': 'On Fire',         'name_ar': 'مشتعل',
     'desc_en': 'Win 3 games in a row',   'desc_ar': 'افوز 3 مرات متتالية',
     'condition': lambda s: s.get('streak', 0) >= 3},
    {'id': 'lightning',      'icon': '⚡', 'name_en': 'Lightning',       'name_ar': 'برق',
     'desc_en': 'Win 5 games in a row',   'desc_ar': 'افوز 5 مرات متتالية',
     'condition': lambda s: s.get('streak', 0) >= 5},
    {'id': 'half_grand',     'icon': '💰', 'name_en': 'Half a Grand',    'name_ar': 'نصف الألف',
     'desc_en': 'Reach 500 points',       'desc_ar': 'اجمع 500 نقطة',
     'condition': lambda s: s['points'] >= 500},
    {'id': 'millionaire',    'icon': '👑', 'name_en': 'Millionaire',     'name_ar': 'مليونير',
     'desc_en': 'Reach 1000 points',      'desc_ar': 'اجمع 1000 نقطة',
     'condition': lambda s: s['points'] >= 1000},
    {'id': 'no_cheating',    'icon': '🧠', 'name_en': 'No Cheating',     'name_ar': 'لا للغش',
     'desc_en': 'Win 5 games without hints', 'desc_ar': 'افوز 5 مرات بدون تلميحات',
     'condition': lambda s: s.get('wins_without_hints', 0) >= 5},
    {'id': 'speed_runner',   'icon': '⏱', 'name_en': 'Speed Runner',    'name_ar': 'عداء سريع',
     'desc_en': 'Win in under 20 seconds','desc_ar': 'افوز في أقل من 20 ثانية',
     'condition': lambda s: s.get('last_win_time', 999) <= 20},
    {'id': 'bilingual',      'icon': '🌍', 'name_en': 'Bilingual',       'name_ar': 'ثنائي اللغة',
     'desc_en': 'Win in both languages',  'desc_ar': 'افوز باللغتين',
     'condition': lambda s: s.get('wins_ar', 0) > 0 and s.get('wins_en', 0) > 0},
    {'id': 'veteran',        'icon': '🎖', 'name_en': 'Veteran',         'name_ar': 'محارب قديم',
     'desc_en': 'Play 20 games total',    'desc_ar': 'العب 20 لعبة',
     'condition': lambda s: (s['wins'] + s['losses']) >= 20},
]

# ------------------------  الكلمات ------------------------
WORDS_EN = [
    {"word": "python",     "hint": "A snake? No, a programming language"},
    {"word": "hangman",    "hint": "The name of this game"},
    {"word": "computer",   "hint": "Electronic brain"},
    {"word": "internet",   "hint": "World wide web"},
    {"word": "developer",  "hint": "Codes all day"},
    {"word": "keyboard",   "hint": "You type with it"},
    {"word": "algorithm",  "hint": "Step by step"},
    {"word": "database",   "hint": "Stores data"},
    {"word": "network",    "hint": "Connects computers"},
    {"word": "browser",    "hint": "Surf the web"},
    {"word": "software",   "hint": "Programs and apps"},
    {"word": "hardware",   "hint": "Physical parts"},
    {"word": "function",   "hint": "Reusable block of code"},
    {"word": "variable",   "hint": "Stores a value"},
    {"word": "recursion",  "hint": "Function calling itself"},
]

WORDS_AR = [
    {"word": "بايثون",  "hint": "لغة برمجة وثعبان"},
    {"word": "مشنوق",   "hint": "اسم اللعبة نفسه"},
    {"word": "حاسوب",   "hint": "دماغ إلكتروني"},
    {"word": "إنترنت",  "hint": "شبكة عالمية"},
    {"word": "مبرمج",   "hint": "يكتب الأكواد"},
    {"word": "لوحة",    "hint": "تكتب بها"},
    {"word": "خوارزمية","hint": "خطوات منظمة"},
    {"word": "قاعدة",   "hint": "تخزن البيانات"},
    {"word": "شبكة",    "hint": "ربط الأجهزة"},
    {"word": "متصفح",   "hint": "لتتصفح الإنترنت"},
    {"word": "برمجيات", "hint": "البرامج والتطبيقات"},
    {"word": "عتاد",    "hint": "الأجزاء المادية"},
    {"word": "دالة",    "hint": "كتلة قابلة لإعادة الاستخدام"},
    {"word": "متغير",   "hint": "يخزن قيمة"},
    {"word": "استدعاء", "hint": "دالة تستدعي نفسها"},
]

# ------------------------ رشم المشنوق ------------------------
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

# ------------------------ السيف فايل ------------------------
PLAYERS_FILE = 'hangman_players.json'
DAILY_CHALLENGE_FILE = 'daily_challenge.json'

def load_players():
    """تحميل بيانات جميع اللاعبين"""
    try:
        with open(PLAYERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_players(players):
    """حفظ بيانات جميع اللاعبين"""
    with open(PLAYERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(players, f, ensure_ascii=False, indent=2)

def get_player_stats(username):
    """الحصول على إحصائيات لاعب معين (وإنشائها إن لم توجد)"""
    players = load_players()
    if username not in players:
        players[username] = {
            'points': 0,
            'wins': 0,
            'losses': 0,
            'streak': 0,
            'best_streak': 0,
            'wins_ar': 0,
            'wins_en': 0,
            'wins_without_hints': 0,
            'total_games': 0,
            'total_time': 0,
            'last_perfect': False,
            'last_win_time': 0,
            'unlocked_achievements': [],
            'games_history': []  
        }
    return players, players[username]

def save_player_stats(username, stats):
    """حفظ إحصائيات لاعب معين"""
    players = load_players()
    players[username] = stats
    save_players(players)

# ------------------------ تحدي اليوم ------------------------
def load_daily_challenge():
    """تحميل تحدي اليوم (كلمة ثابتة لكل يوم)"""
    try:
        with open(DAILY_CHALLENGE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # التحقق من أن التحدي لا يزال لليوم الحالي
        today = datetime.date.today().isoformat()
        if data.get('date') == today:
            return data
    except FileNotFoundError:
        pass
    # إنشاء تحدي جديد لهذا اليوم
    lang = random.choice(['ar', 'en'])
    word_list = WORDS_AR if lang == 'ar' else WORDS_EN
    word_data = random.choice(word_list)
    challenge = {
        'date': datetime.date.today().isoformat(),
        'lang': lang,
        'word': word_data['word'],
        'hint': word_data['hint']
    }
    with open(DAILY_CHALLENGE_FILE, 'w', encoding='utf-8') as f:
        json.dump(challenge, f, ensure_ascii=False, indent=2)
    return challenge

# ------------------------ للواجهة ------------------------
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_title():
    clear_screen()
    try:
        title = pyfiglet.figlet_format("HANGMAN", font="slant")
        print(COLOR_TITLE + title + Style.RESET_ALL)
        subtitle = pyfiglet.figlet_format("المشنوق", font="digital")
        print(COLOR_TITLE + subtitle + Style.RESET_ALL)
    except:
        print(COLOR_TITLE + "="*50)
        print("HANGMAN - المشنوق".center(50))
        print("="*50 + Style.RESET_ALL)
    print()

def display_hangman(mistakes, max_tries):
    """عرض الرسم بناءً على عدد الأخطاء"""
    index = int((mistakes / max_tries) * (len(HANGMAN_PICS) - 1))
    return HANGMAN_PICS[index]

def display_keyboard(used_letters, correct_letters, lang):
    """عرض لوحة مفاتيح افتراضية مع تلوين الأحرف"""
    if lang == 'en':
        rows = [
            "q w e r t y u i o p",
            " a s d f g h j k l ",
            "  z x c v b n m    "
        ]
    else:
        rows = [
            "ض ص ث ق ف غ ع ه خ ح ج",
            "ش س ي ب ل ا ت ن م ك",
            "ط ئ ء ؤ ر لا ى ة و ز ظ"
        ]
    print(f"\n{' ' * 10}{Fore.CYAN}{'Keyboard' if lang == 'en' else 'لوحة المفاتيح'}:{Style.RESET_ALL}")
    for row in rows:
        line = " " * 10
        for ch in row.split():
            if ch in used_letters:
                if ch in correct_letters:
                    line += f"{Fore.GREEN}{ch} "
                else:
                    line += f"{Fore.RED}{ch} "
            else:
                line += f"{Fore.WHITE}{ch} "
        print(line + Style.RESET_ALL)

def check_achievements(stats):
    """فحص الإنجازات وإرجاع قائمة الإنجازات الجديدة"""
    newly_unlocked = []
    for ach in ACHIEVEMENTS:
        if ach['id'] not in stats['unlocked_achievements'] and ach['condition'](stats):
            stats['unlocked_achievements'].append(ach['id'])
            newly_unlocked.append(ach)
    return newly_unlocked

def display_achievements(stats, lang):
    """عرض جميع الإنجازات مع حالتها"""
    clear_screen()
    print_title()
    print(f"\n{Fore.CYAN}{'ACHIEVEMENTS' if lang == 'en' else 'الإنجازات'}{Style.RESET_ALL}")
    print("-" * 60)
    for ach in ACHIEVEMENTS:
        unlocked = ach['id'] in stats['unlocked_achievements']
        status = f"{Fore.GREEN}✔{Style.RESET_ALL}" if unlocked else f"{Fore.RED}✘{Style.RESET_ALL}"
        name = ach['name_en'] if lang == 'en' else ach['name_ar']
        desc = ach['desc_en'] if lang == 'en' else ach['desc_ar']
        print(f"{status} {ach['icon']} {name}: {desc}")
    print("-" * 60)
    input(f"\n{Fore.CYAN}{'Press Enter to continue...' if lang == 'en' else 'اضغط Enter للمتابعة...'}{Style.RESET_ALL}")

def display_leaderboard(lang):
    """عرض قادة النقاط (أفضل 10 لاعبين)"""
    players = load_players()
    if not players:
        print(f"\n{Fore.YELLOW}{'No players yet.' if lang == 'en' else 'لا يوجد لاعبون بعد.'}{Style.RESET_ALL}")
        input(f"\n{Fore.CYAN}{'Press Enter...' if lang == 'en' else 'اضغط Enter...'}{Style.RESET_ALL}")
        return
    # ترتيب تنازلي حسب النقاط
    sorted_players = sorted(players.items(), key=lambda x: x[1]['points'], reverse=True)[:10]
    clear_screen()
    print_title()
    print(f"\n{Fore.CYAN}{'🏆 LEADERBOARD' if lang == 'en' else '🏆 قادة النقاط'}{Style.RESET_ALL}")
    print("=" * 60)
    print(f"{'#':<3} {'Username':<20} {'Points':<10} {'Wins':<6} {'Streak':<6}")
    print("-" * 60)
    for i, (username, data) in enumerate(sorted_players, 1):
        print(f"{i:<3} {username:<20} {data['points']:<10} {data['wins']:<6} {data['streak']:<6}")
    print("=" * 60)
    input(f"\n{Fore.CYAN}{'Press Enter to continue...' if lang == 'en' else 'اضغط Enter للمتابعة...'}{Style.RESET_ALL}")

def display_stats(stats, lang):
    """عرض إحصائيات متقدمة للاعب الحالي"""
    clear_screen()
    print_title()
    print(f"\n{Fore.CYAN}{'📊 STATISTICS' if lang == 'en' else '📊 إحصائيات'}{Style.RESET_ALL}")
    print("=" * 50)
    print(f"{'Points' if lang == 'en' else 'النقاط'}: {stats['points']}")
    print(f"{'Wins' if lang == 'en' else 'انتصارات'}: {stats['wins']}")
    print(f"{'Losses' if lang == 'en' else 'هزائم'}: {stats['losses']}")
    total = stats['wins'] + stats['losses']
    if total > 0:
        win_rate = (stats['wins'] / total) * 100
        print(f"{'Win rate' if lang == 'en' else 'نسبة الفوز'}: {win_rate:.1f}%")
    else:
        print(f"{'Win rate' if lang == 'en' else 'نسبة الفوز'}: N/A")
    print(f"{'Current streak' if lang == 'en' else 'السلسلة الحالية'}: {stats['streak']}")
    print(f"{'Best streak' if lang == 'en' else 'أفضل سلسلة'}: {stats.get('best_streak', 0)}")
    print(f"{'Games without hints' if lang == 'en' else 'ألعاب بدون تلميحات'}: {stats.get('wins_without_hints', 0)}")
    print(f"{'Wins in Arabic' if lang == 'en' else 'انتصارات بالعربية'}: {stats.get('wins_ar', 0)}")
    print(f"{'Wins in English' if lang == 'en' else 'انتصارات بالإنجليزية'}: {stats.get('wins_en', 0)}")
    print(f"{'Achievements unlocked' if lang == 'en' else 'الإنجازات المفتوحة'}: {len(stats['unlocked_achievements'])}/{len(ACHIEVEMENTS)}")
    print("=" * 50)
    input(f"\n{Fore.CYAN}{'Press Enter to continue...' if lang == 'en' else 'اضغط Enter للمتابعة...'}{Style.RESET_ALL}")

# ------------------------ لعبة Hangman الرئيسية ------------------------
def play_game(username, stats, lang_choice, difficulty):
    """تنفيذ جولة لعبة واحدة"""
    settings = DIFFICULTY_SETTINGS[difficulty]
    max_tries = settings['max_tries']
    time_limit = settings['time_limit']
    points_multiplier = settings['points_multiplier']

   
    word_list = WORDS_AR if lang_choice == 'ar' else WORDS_EN
    word_data = random.choice(word_list)
    word = word_data['word']
    hint = word_data['hint']

    word_letters = set(word)
    alphabet = set('abcdefghijklmnopqrstuvwxyz') if lang_choice == 'en' else set('ابتثجحخدذرزسشصضطظعغفقكلمنهويءآأؤإئة')
    used_letters = set()
    correct_letters = set()
    wrong_letters = set()
    mistakes = 0
    hint_used = False
    start_time = time.time()
    game_active = True

    while len(word_letters) > 0 and mistakes < max_tries and game_active:
        clear_screen()
        print_title()

        elapsed = time.time() - start_time
        time_left = max(0, time_limit - int(elapsed))
        if time_left <= 0:
            game_active = False
            break

        print(display_hangman(mistakes, max_tries))

        print(f"\n{Fore.YELLOW}{'Word' if lang_choice == 'en' else 'الكلمة'}: {Style.RESET_ALL}", end='')
        for letter in word:
            if letter in used_letters:
                print(f"{COLOR_CORRECT}{letter}{Style.RESET_ALL}", end=' ')
            else:
                print("_", end=' ')
        print()

        print(f"{COLOR_POINTS}{'Points' if lang_choice == 'en' else 'النقاط'}: {stats['points']} | "
              f"{'Streak' if lang_choice == 'en' else 'سلسلة'}: {stats['streak']} | "
              f"{'Mistakes' if lang_choice == 'en' else 'الأخطاء'}: {mistakes}/{max_tries} | "
              f"{'Time' if lang_choice == 'en' else 'الوقت'}: {time_left}s{Style.RESET_ALL}")

        if wrong_letters:
            print(f"\n{Fore.RED}{'Wrong letters' if lang_choice == 'en' else 'الأحرف الخاطئة'}: {', '.join(sorted(wrong_letters))}{Style.RESET_ALL}")

        display_keyboard(used_letters, correct_letters, lang_choice)

        print(f"\n{Fore.CYAN}{'Options:' if lang_choice == 'en' else 'الخيارات:'}{Style.RESET_ALL}")
        print(f"1. {'Guess a letter' if lang_choice == 'en' else 'تخمين حرف'}")
        print(f"2. {'Buy hint (50 pts)' if lang_choice == 'en' else 'شراء تلميح (50 نقطة)'}")
        print(f"3. {'View achievements' if lang_choice == 'en' else 'عرض الإنجازات'}")
        print(f"4. {'Return to main menu' if lang_choice == 'en' else 'العودة للقائمة الرئيسية'}")

        choice = input(f"{Fore.YELLOW}{'Choice' if lang_choice == 'en' else 'اختيار'}: {Style.RESET_ALL}").strip()

        if choice == '1':

            guess = input(f"{Fore.CYAN}{'Enter a letter' if lang_choice == 'en' else 'أدخل حرفاً'}: {Style.RESET_ALL}").strip().lower()
            if len(guess) != 1:
                print(f"{Fore.RED}{'Please enter a single letter.' if lang_choice == 'en' else 'الرجاء إدخال حرف واحد.'}{Style.RESET_ALL}")
                input(f"{Fore.LIGHTBLACK_EX}{'Press Enter' if lang_choice == 'en' else 'اضغط Enter'}{Style.RESET_ALL}")
                continue
            if guess not in alphabet:
                print(f"{Fore.RED}{'Invalid character.' if lang_choice == 'en' else 'حرف غير صالح.'}{Style.RESET_ALL}")
                input(f"{Fore.LIGHTBLACK_EX}{'Press Enter' if lang_choice == 'en' else 'اضغط Enter'}{Style.RESET_ALL}")
                continue
            if guess in used_letters:
                print(f"{Fore.RED}{'You already used that letter.' if lang_choice == 'en' else 'لقد استخدمت هذا الحرف مسبقاً.'}{Style.RESET_ALL}")
                input(f"{Fore.LIGHTBLACK_EX}{'Press Enter' if lang_choice == 'en' else 'اضغط Enter'}{Style.RESET_ALL}")
                continue

            used_letters.add(guess)
            if guess in word_letters:
                word_letters.remove(guess)
                correct_letters.add(guess)
                stats['points'] += int(10 * points_multiplier)
                print(f"{COLOR_CORRECT}{'Good guess!' if lang_choice == 'en' else 'إجابة صحيحة!'}{Style.RESET_ALL}")
                beep(800, 150)
            else:
                mistakes += 1
                wrong_letters.add(guess)
                print(f"{COLOR_WRONG}{'Wrong guess!' if lang_choice == 'en' else 'إجابة خاطئة!'}{Style.RESET_ALL}")
                beep(300, 300)

            input(f"{Fore.LIGHTBLACK_EX}{'Press Enter' if lang_choice == 'en' else 'اضغط Enter'}{Style.RESET_ALL}")

        elif choice == '2':
            if hint_used:
                print(f"{Fore.RED}{'Hint already used in this game.' if lang_choice == 'en' else 'لقد استخدمت التلميح بالفعل في هذه الجولة.'}{Style.RESET_ALL}")
            else:
                if stats['points'] < 50:
                    print(f"{Fore.RED}{'Not enough points! (50 required)' if lang_choice == 'en' else 'نقاط غير كافية! (50 مطلوبة)'}{Style.RESET_ALL}")
                else:
                    stats['points'] -= 50
                    hint_used = True
                    print(f"{Fore.MAGENTA}{'Hint' if lang_choice == 'en' else 'تلميح'}: {hint}{Style.RESET_ALL}")
                    beep(880, 200)
            input(f"{Fore.LIGHTBLACK_EX}{'Press Enter' if lang_choice == 'en' else 'اضغط Enter'}{Style.RESET_ALL}")

        elif choice == '3':
            display_achievements(stats, lang_choice)

        elif choice == '4':
# الخسارة
            game_active = False
            break

        else:
            print(f"{Fore.RED}{'Invalid choice.' if lang_choice == 'en' else 'اختيار غير صحيح.'}{Style.RESET_ALL}")
            input(f"{Fore.LIGHTBLACK_EX}{'Press Enter' if lang_choice == 'en' else 'اضغط Enter'}{Style.RESET_ALL}")


    clear_screen()
    print_title()
    elapsed = time.time() - start_time

    if mistakes >= max_tries or time_left <= 0 or not game_active:
        # خسارة
        print(display_hangman(max_tries, max_tries))
        print(f"\n{COLOR_WRONG}{'You lost!' if lang_choice == 'en' else 'لقد خسرت!'}{Style.RESET_ALL}")
        if not game_active and choice == '4':
            print(f"{Fore.YELLOW}{'You returned to main menu.' if lang_choice == 'en' else 'عدت للقائمة الرئيسية.'}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}{'The word was' if lang_choice == 'en' else 'الكلمة كانت'}: {COLOR_WORD}{word}{Style.RESET_ALL}")
        stats['losses'] += 1
        stats['streak'] = 0
        stats['last_perfect'] = False
        beep(200, 1000)
    else:
        # فوز
        time_bonus = max(0, int((time_limit - elapsed) / 2))
        win_points = 50 * points_multiplier + time_bonus
        stats['points'] += win_points
        stats['wins'] += 1
        stats['streak'] += 1
        if stats['streak'] > stats.get('best_streak', 0):
            stats['best_streak'] = stats['streak']
        if lang_choice == 'ar':
            stats['wins_ar'] += 1
        else:
            stats['wins_en'] += 1
        if not hint_used:
            stats['wins_without_hints'] += 1
        stats['last_perfect'] = (mistakes == 0)
        stats['last_win_time'] = elapsed
        stats['total_games'] = stats.get('total_games', 0) + 1
        stats['total_time'] = stats.get('total_time', 0) + elapsed

        print(display_hangman(mistakes, max_tries))
        print(f"\n{COLOR_CORRECT}{'Congratulations!' if lang_choice == 'en' else 'تهانينا!'}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'You guessed the word' if lang_choice == 'en' else 'لقد خمنت الكلمة'}: {COLOR_WORD}{word}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'You earned' if lang_choice == 'en' else 'لقد ربحت'}: {win_points} points (including {time_bonus} time bonus){Style.RESET_ALL}")
        beep(600, 200); beep(800, 200); beep(1000, 400)

    save_player_stats(username, stats)

    new_achievements = check_achievements(stats)
    if new_achievements:
        print(f"\n{Fore.CYAN}{'New achievements unlocked!' if lang_choice == 'en' else 'إنجازات جديدة مفتوحة!'}{Style.RESET_ALL}")
        for ach in new_achievements:
            name = ach['name_en'] if lang_choice == 'en' else ach['name_ar']
            print(f"{ach['icon']} {name}")
            beep(1000, 100); beep(1200, 100); beep(1400, 200)
        save_player_stats(username, stats)

    input(f"\n{Fore.CYAN}{'Press Enter to continue...' if lang_choice == 'en' else 'اضغط Enter للمتابعة...'}{Style.RESET_ALL}")

# ------------------------ تحدي اليوم ------------------------
def play_daily_challenge(username, stats, lang_choice):
    """تنفيذ تحدي اليوم (صعوبة ثابتة)"""
    challenge = load_daily_challenge()
    if challenge['lang'] != lang_choice:
        print(f"{Fore.YELLOW}{'Today\'s challenge is in ' + challenge['lang'] + ' language.' if lang_choice == 'en' else 'تحدي اليوم باللغة ' + ('العربية' if challenge['lang']=='ar' else 'الإنجليزية')}{Style.RESET_ALL}")
        input(f"{Fore.CYAN}{'Press Enter...' if lang_choice == 'en' else 'اضغط Enter...'}{Style.RESET_ALL}")
        return
    word = challenge['word']
    hint = challenge['hint']
    max_tries = 6 
    time_limit = 90
    points_multiplier = 2.0

    word_letters = set(word)
    alphabet = set('abcdefghijklmnopqrstuvwxyz') if lang_choice == 'en' else set('ابتثجحخدذرزسشصضطظعغفقكلمنهويءآأؤإئة')
    used_letters = set()
    correct_letters = set()
    wrong_letters = set()
    mistakes = 0
    start_time = time.time()
    game_active = True

    while len(word_letters) > 0 and mistakes < max_tries and game_active:
        clear_screen()
        print_title()
        print(f"{Fore.CYAN}{'⭐ DAILY CHALLENGE ⭐' if lang_choice == 'en' else '⭐ تحدي اليوم ⭐'}{Style.RESET_ALL}\n")

        elapsed = time.time() - start_time
        time_left = max(0, time_limit - int(elapsed))
        if time_left <= 0:
            game_active = False
            break

        print(display_hangman(mistakes, max_tries))

        print(f"\n{Fore.YELLOW}{'Word' if lang_choice == 'en' else 'الكلمة'}: {Style.RESET_ALL}", end='')
        for letter in word:
            if letter in used_letters:
                print(f"{COLOR_CORRECT}{letter}{Style.RESET_ALL}", end=' ')
            else:
                print("_", end=' ')
        print()

        print(f"{COLOR_POINTS}{'Mistakes' if lang_choice == 'en' else 'الأخطاء'}: {mistakes}/{max_tries} | "
              f"{'Time' if lang_choice == 'en' else 'الوقت'}: {time_left}s{Style.RESET_ALL}")

        if wrong_letters:
            print(f"\n{Fore.RED}{'Wrong letters' if lang_choice == 'en' else 'الأحرف الخاطئة'}: {', '.join(sorted(wrong_letters))}{Style.RESET_ALL}")

        display_keyboard(used_letters, correct_letters, lang_choice)

        print(f"\n{Fore.CYAN}{'Options:' if lang_choice == 'en' else 'الخيارات:'}{Style.RESET_ALL}")
        print(f"1. {'Guess a letter' if lang_choice == 'en' else 'تخمين حرف'}")
        print(f"2. {'Return to main menu' if lang_choice == 'en' else 'العودة للقائمة الرئيسية'}")

        choice = input(f"{Fore.YELLOW}{'Choice' if lang_choice == 'en' else 'اختيار'}: {Style.RESET_ALL}").strip()

        if choice == '1':
            guess = input(f"{Fore.CYAN}{'Enter a letter' if lang_choice == 'en' else 'أدخل حرفاً'}: {Style.RESET_ALL}").strip().lower()
            if len(guess) != 1 or guess not in alphabet or guess in used_letters:
                continue
            used_letters.add(guess)
            if guess in word_letters:
                word_letters.remove(guess)
                correct_letters.add(guess)
                print(f"{COLOR_CORRECT}{'Good guess!' if lang_choice == 'en' else 'إجابة صحيحة!'}{Style.RESET_ALL}")
                beep(800, 150)
            else:
                mistakes += 1
                wrong_letters.add(guess)
                print(f"{COLOR_WRONG}{'Wrong guess!' if lang_choice == 'en' else 'إجابة خاطئة!'}{Style.RESET_ALL}")
                beep(300, 300)
            input(f"{Fore.LIGHTBLACK_EX}{'Press Enter' if lang_choice == 'en' else 'اضغط Enter'}{Style.RESET_ALL}")

        elif choice == '2':
            game_active = False
            break

    clear_screen()
    print_title()
    if mistakes >= max_tries or time_left <= 0:
        print(display_hangman(max_tries, max_tries))
        print(f"\n{COLOR_WRONG}{'You lost the daily challenge!' if lang_choice == 'en' else 'خسرت تحدي اليوم!'}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'The word was' if lang_choice == 'en' else 'الكلمة كانت'}: {COLOR_WORD}{word}{Style.RESET_ALL}")
    else:
        print(display_hangman(mistakes, max_tries))
        print(f"\n{COLOR_CORRECT}{'You completed the daily challenge!' if lang_choice == 'en' else 'أكملت تحدي اليوم!'}{Style.RESET_ALL}")
        bonus = 200
        stats['points'] += bonus
        print(f"{Fore.YELLOW}{'You earned' if lang_choice == 'en' else 'لقد ربحت'}: {bonus} bonus points{Style.RESET_ALL}")
        beep(600, 200); beep(800, 200); beep(1000, 400)
        save_player_stats(username, stats)

    input(f"\n{Fore.CYAN}{'Press Enter to continue...' if lang_choice == 'en' else 'اضغط Enter للمتابعة...'}{Style.RESET_ALL}")

# ------------------------ القائمة الرئيسية ------------------------
def main():
    print_title()
    print(f"{Fore.CYAN}{'🎮 HANGMAN - المشنوق'}{Style.RESET_ALL}")
    print("=" * 60)

    username = input(f"{Fore.YELLOW}Enter your username / أدخل اسم المستخدم: {Style.RESET_ALL}").strip()
    if not username:
        username = "Player"

    while True:
        lang_choice = input(f"{Fore.YELLOW}Choose language / اختر اللغة (en/ar): {Style.RESET_ALL}").strip().lower()
        if lang_choice in ['en', 'ar']:
            break
        print(f"{Fore.RED}Invalid input. / إدخال غير صحيح.{Style.RESET_ALL}")

    players, stats = get_player_stats(username)

    difficulty = 'medium'

    while True:
        print_title()
        print(f"{Fore.GREEN}{'Welcome, ' + username if lang_choice == 'en' else 'مرحباً، ' + username}{Style.RESET_ALL}")
        print("=" * 60)
        print(f"{Fore.CYAN}{'Points' if lang_choice == 'en' else 'النقاط'}: {stats['points']} | "
              f"{'Wins' if lang_choice == 'en' else 'انتصارات'}: {stats['wins']} | "
              f"{'Losses' if lang_choice == 'en' else 'هزائم'}: {stats['losses']} | "
              f"{'Streak' if lang_choice == 'en' else 'سلسلة'}: {stats['streak']}")
        print("=" * 60)
        print("1. " + ('Start Game' if lang_choice == 'en' else 'ابدأ اللعب'))
        print("2. " + ('Difficulty' if lang_choice == 'en' else 'الصعوبة'))
        print("3. " + ('Achievements' if lang_choice == 'en' else 'الإنجازات'))
        print("4. " + ('Leaderboard' if lang_choice == 'en' else 'قادة النقاط'))
        print("5. " + ('Daily Challenge' if lang_choice == 'en' else 'تحدي اليوم'))
        print("6. " + ('Statistics' if lang_choice == 'en' else 'إحصائيات'))
        print("7. " + ('Exit' if lang_choice == 'en' else 'خروج'))
        print("=" * 60)

        choice = input(f"{Fore.YELLOW}{'Choice' if lang_choice == 'en' else 'اختيار'}: {Style.RESET_ALL}").strip()

        if choice == '1':
            play_game(username, stats, lang_choice, difficulty)

        elif choice == '2':
            print(f"\n{Fore.CYAN}{'Select difficulty:' if lang_choice == 'en' else 'اختر الصعوبة:'}{Style.RESET_ALL}")
            for key, val in DIFFICULTY_SETTINGS.items():
                name = val['name_en'] if lang_choice == 'en' else val['name_ar']
                print(f"   {key}: {name}")
            diff_input = input(f"{Fore.YELLOW}{'Enter difficulty' if lang_choice == 'en' else 'أدخل الصعوبة'}: {Style.RESET_ALL}").strip().lower()
            if diff_input in DIFFICULTY_SETTINGS:
                difficulty = diff_input
                print(f"{Fore.GREEN}{'Difficulty set to ' + difficulty if lang_choice == 'en' else 'تم تعيين الصعوبة إلى ' + difficulty}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}{'Invalid difficulty.' if lang_choice == 'en' else 'صعوبة غير صحيحة.'}{Style.RESET_ALL}")
            input(f"{Fore.LIGHTBLACK_EX}{'Press Enter' if lang_choice == 'en' else 'اضغط Enter'}{Style.RESET_ALL}")

        elif choice == '3':
            display_achievements(stats, lang_choice)

        elif choice == '4':
            display_leaderboard(lang_choice)

        elif choice == '5':
            play_daily_challenge(username, stats, lang_choice)

        elif choice == '6':
            display_stats(stats, lang_choice)

        elif choice == '7':
            print(f"\n{Fore.YELLOW}{'Goodbye!' if lang_choice == 'en' else 'مع السلامة!'}{Style.RESET_ALL}")
            sys.exit()

        else:
            print(f"{Fore.RED}{'Invalid choice.' if lang_choice == 'en' else 'اختيار غير صحيح.'}{Style.RESET_ALL}")
            input(f"{Fore.LIGHTBLACK_EX}{'Press Enter' if lang_choice == 'en' else 'اضغط Enter'}{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Goodbye! مع السلامة!{Style.RESET_ALL}")
        sys.exit()
