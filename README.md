# Rehab Wings - Hand Gesture Controlled Flappy Bird

A therapeutic game designed to aid in hand rehabilitation through gesture-controlled gameplay. This project combines computer vision with the classic Flappy Bird game to create an engaging rehabilitation tool.

## Features

- **Hand Gesture Control**: Play the game using hand gestures (open/close fist)
- **Patient Management**: Track individual patient progress and high scores
- **Time Management**: Limit playtime to 20 minutes per day to prevent overuse
- **Data Analysis**: Comprehensive statistics and progress tracking
- **User-Friendly Interface**: Simple and intuitive controls
- **Database Integration**: Secure storage of patient data and game statistics

## Prerequisites

- Python 3.8+
- MySQL Server
- Webcam
- pip (Python package manager)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/HandGesture-contolled-flappybird.git
   cd HandGesture-contolled-flappybird
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database**
   - Create a MySQL database
   - Update the database configuration in `db_operations.py`
   - Run the database schema setup (if provided)

## How to Play

1. **Start the game**
   ```bash
   python game.py
   ```

2. **Controls**
   - Make a fist to make the bird fly up
   - Release your fist to let the bird fall
   - Press ESC to exit the game
   - After game over, make a fist to play again (if time remains)

3. **View Statistics**
   ```bash
   python analyze_game_data.py
   ```
   - View top high scores
   - Check player statistics
   - Analyze session data
   - View daily statistics

## Data Analysis

The `analyze_game_data.py` script provides detailed analytics:

1. **Top High Scores**: View the highest scores across all patients
2. **Player Statistics**: Detailed stats for individual players
3. **Session Analysis**: In-depth analysis of game sessions
4. **Daily Statistics**: Summary of daily gameplay metrics

## Project Structure

- `game.py`: Main game logic and hand gesture detection
- `db_operations.py`: Database connection and operations
- `analyze_game_data.py`: Data analysis and reporting
- `patient_form.py`: Patient registration and management
- `handopenclose.py`: Hand gesture recognition module
- `requirements.txt`: Project dependencies

## Database Schema

The application uses the following tables:

- `patients`: Stores patient information and high scores
- `game_sessions`: Records each game session with scores and timestamps

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For any questions or support, please contact:
- WhatsApp: +91 9032682005
- GitHub: [@nihith303](https://github.com/nihith303)

## Live Website DEMO

- **Play the Game:** [https://nihith303.github.io/rehab-wings-website-version/](https://nihith303.github.io/rehab-wings-website-version/)
- **GitHub Repo:** [https://github.com/nihith303/rehab-wings-website-version](https://github.com/nihith303/rehab-wings-website-version)

## Acknowledgments

- Special thanks to all contributors and testers
- Inspired by the original Flappy Bird game
- Built with Python, Pygame, and OpenCV
