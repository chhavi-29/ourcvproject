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


 ## Install the dependencies: Make sure you have Python installed, then run the following command to download the required libraries:

bash
pip install pygame opencv-contrib-python mediapipe==0.10.14 numpy
(Note: mediapipe==0.10.14 is recommended specifically for Apple Silicon Mac compatibility!)

## Run the game:

bash
python3 main.py
## 📂 Project Structure

main.py - The core application entry point and game state machine.

game_engine.py - Handles the underlying scoring logic, lives, and educational difficulty scaling.

game_objects.py - Manages the physics and interactions for the dropping fruits, bombs, and splice animations.

hand_tracker.py & input_manager.py - Interfaces with the webcam and mediapipe to track player movements.

ui_manager.py - Handles the rendering of the HUD, Start Screen, and Game Over dashboard.

question_generator.py - Generates dynamic math equations based on the current difficulty level.

assets/ - Contains background images, sound effects, and UI sprites.

 ## 👥 Meet the Team

Developed collaboratively to make education physically active and fun!

Member 1: Core Game Engine, Physics, and Logic Flow

Member 2: Computer Vision, Hand Tracking, and Input Management

Member 3: Audio, User Interface, and Graphical Polishing

