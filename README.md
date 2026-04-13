# 🍉 Tiny Thinkers (Fruit Ninja CV Edition)

**Tiny Thinkers** is an interactive, educational twist on the classic Fruit Ninja game. Instead of fruitlessly slashing for high scores, players use their actual hands (via webcam hand-tracking) to slash the correct answers to math questions dropping from the top of the screen!

Built specifically for children, this game combines physical movement with mathematics to make learning engaging, fast-paced, and fun.

## 🌟 Key Features

- **🎮 Computer Vision Controls**: Play entirely hands-free! The game uses your webcam and Google's MediaPipe model to track your hand movements and draw a virtual blade on the screen.
- **🧠 Educational Gameplay**: Math equations are dynamically generated. The correct answer drops as a fruit, while incorrect answers drop as bombs. Slice the fruit, dodge the bombs!
- **⚡ Dynamic Leveling**: The game starts on `Easy` and automatically scales to `Medium` and `Hard` as you chain together 5 consecutive correct answers!
- **🎨 Child-Friendly UI**: Restyled with heavy-contrast fonts, pastel interactive menu buttons, and bright, colorful background overlays.
- **🖱️ Multi-Input Support**: Play away from the computer using your hands or sit up close and use the mouse to click through menus and slice fruits.

## 🛠️ Technology Stack

- **Python 3.9+**: The core backend language.
- **Pygame**: Handles the game loop, 2D physics, UI rendering, and asset processing.
- **OpenCV & MediaPipe**: Powers the real-time hand-tracking model that translates physical movement into game inputs.

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone <>
   cd FruitNinja-cv
