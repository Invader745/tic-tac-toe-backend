# tic-tac-toe-backend
# Tic-Tac-Toe Backend

## Project Overview
This project implements the backend for a Tic-Tac-Toe game with features like:
- User registration and login (JWT-based authentication).
- Starting and playing Tic-Tac-Toe games.
- Tracking game history and user profiles.

## Features
1. User Management:
   - Secure registration and login.
   - Profile management.

2. Game Management:
   - Start games between two users with random marker assignment.
   - Make moves with turn validation and winner/draw detection.

3. Game History:
   - Fetch match history for users.
   - Detailed timeline of moves for each game.

## Prerequisites
- Python 3.x
- Django 4.x
- Django REST Framework
- SQLite

## Setup Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/tic-tac-toe-backend.git
   cd tic-tac-toe-backend

2. Set up a virtual environment:
    python -m venv venv
    # On Windows: venv\Scripts\activate

3. Install dependencies:
    pip install -r requirements.txt

4. Run database migrations:
    python manage.py migrate

5. Start the development server:
    python manage.py runserver

## Assumptions
Markers ('X' and 'O') are randomly assigned at game start.
Users can only play games if both are available.
Moves are validated for turns and game status.

/register/	        POST	Register a new user
/login/	            POST	Login and get JWT token
/start-game/	    POST	Start a new game
/make-move/	        POST	Make a move in a game
/match-history/	    GET	    Get user match history
/update-profile/    PUT	    Update user profile

