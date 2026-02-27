# 🎮 Hangman Game - المشنوق

![Python](https://img.shields.io/badge/python-3.6+-blue.svg)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow.svg)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![GitHub stars](https://img.shields.io/github/stars/moon9io/hangman-game?style=social)

**Hangman Game** is a fully responsive, bilingual (Arabic/English) classic Hangman game with modern features: points system, achievements, daily challenges, leaderboard, and multiple difficulty levels. Available as both a **web version** (pure Vanilla JavaScript) and a **terminal version** (Python).

---

## ✨ Features

### 🌐 Web Version (JavaScript)
- Fully responsive design – works on desktop, tablet, and mobile.
- Bilingual interface (Arabic/English) with RTL/LTR switching.
- Dark/Light theme toggle.
- Interactive keyboard with visual feedback.
- Timer with animated ring.
- Hint system (costs points).
- Achievements (10 unlockable badges).
- Persistent storage using `localStorage`.
- Procedurally generated sounds via Web Audio API.
- Touch and keyboard support.

### 🖥️ Terminal Version (Python)
- Colorful CLI interface using `colorama` and `pyfiglet`.
- Player accounts with JSON-based persistence.
- Leaderboard (top 10 players).
- Daily challenge with 200-point bonus.
- Three difficulty levels (Easy, Medium, Hard).
- Hint system (50 points per hint).
- Countdown timer with time bonus.
- Procedurally generated beep sounds.
- Virtual keyboard display with colored letters.
- Full Arabic/English support with automatic keyboard mapping.

---

## 🚀 Live Demo

Play the web version now: **[Hangman Game Live](https://moon9io.github.io/hangman-game)** (if deployed)

---

## 📸 Screenshots

| Web Version (Dark) | Web Version (Light) | Terminal Version |
|--------------------|---------------------|------------------|
| ![Web Dark](screenshots/web-dark.png) | ![Web Light](screenshots/web-light.png) | ![Terminal](screenshots/terminal.png) |

*(You can add actual screenshots in a `screenshots/` folder.)*

---

## 🛠️ Tech Stack

### Web Version
- **HTML5** – Structure
- **CSS3** – Styling, themes, animations
- **JavaScript (ES6+)** – Game logic, DOM manipulation, localStorage
- **Web Audio API** – Procedural sound generation

### Terminal Version
- **Python 3.6+**
- **colorama** – Colored terminal output
- **pyfiglet** – ASCII art titles

---

## 📦 Installation & Usage

### Web Version
1. Clone the repository:
   ```bash
   git clone https://github.com/moon9io/hangman-game.git
   cd hangman-game
   ```
2. Open `index.html` in your browser.
3. Or deploy to GitHub Pages / any static hosting.

### Terminal Version
1. Ensure Python 3.6+ is installed.
2. Install dependencies:
   ```bash
   pip install colorama pyfiglet
   ```
3. Run the game:
   ```bash
   python hangman.py
   ```

---

## 🎯 How to Play (Web)

1. Choose your language (English / العربية).
2. Select difficulty (Easy / Medium / Hard).
3. Guess letters by clicking the on-screen keyboard or using your physical keyboard.
4. Correct guesses reveal the letter and earn 10 points.
5. Wrong guesses advance the hangman drawing and count as mistakes.
6. You can buy a hint for 50 points (reveals a clue).
7. Win by guessing all letters before running out of attempts or time.
8. Unlock achievements and compete on the leaderboard!

---

## 🏆 Achievements

| Icon | English Name | Arabic Name | Condition |
|------|--------------|-------------|-----------|
| 🎯 | First Blood | الدم الأول | Win your first game |
| ✨ | Flawless | لا تشوبها شائبة | Win with zero mistakes |
| 🔥 | On Fire | مشتعل | Win 3 games in a row |
| ⚡ | Lightning | برق | Win 5 games in a row |
| 💰 | Half a Grand | نصف الألف | Reach 500 points |
| 👑 | Millionaire | مليونير | Reach 1000 points |
| 🧠 | No Cheating | لا للغش | Win 5 games without hints |
| ⏱ | Speed Runner | عداء سريع | Win in under 20 seconds |
| 🌍 | Bilingual | ثنائي اللغة | Win in both languages |
| 🎖 | Veteran | محارب قديم | Play 20 games total |

---

## 🧪 Try It Yourself

Clone the repo and start playing:
```bash
git clone https://github.com/moon9io/hangman-game.git
cd hangman-game
# For web version: open index.html
# For terminal version: python hangman.py
```

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!  
Feel free to check the [issues page](https://github.com/moon9io/hangman-game/issues).

---

## 📝 License

This project is [MIT](LICENSE) licensed.

---

## 👨‍💻 About the Developer

**moon9io**  
- 🔭 Currently working on: [my-arabicj-blog](https://github.com/moon9io/my-arabicj-blog)  
- 🌱 Learning: Web Development, UI/UX Design  
- 📫 How to reach me: [l3939524@gmail.com](mailto:l3939524@gmail.com)  
- 🐦 GitHub: [@moon9io](https://github.com/moon9io)  

> “The best way to predict the future is to invent it.”  

---

⭐️ If you like this project, please give it a star on GitHub!
