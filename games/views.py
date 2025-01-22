from django.shortcuts import render

# Create your views here.
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer
from .serializers import UserProfileUpdateSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view
from .models import Game, Move
from .serializers import MoveSerializer
import random
from .models import UserProfile
import time

class RegisterView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Create a UserProfile with is_available_for_game set to False by default
            UserProfile.objects.create(user=user)
            return Response({'message': 'User created successfully!'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        from django.contrib.auth import authenticate

        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

from rest_framework.permissions import IsAuthenticated
from .models import Game
from django.contrib.auth.models import User

class StartGameView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        player = request.user  # Player 1 is the one who is sending the request
        player1 = player.userprofile  # Access the UserProfile related to the user

        # Automatically mark Player 1 as available to start a game
        player1.is_available_for_game = True
        player1.save()

        time(20)

        # Find an available Player 2 (who is also requesting to start a game)
        player2 = UserProfile.objects.filter(is_available_for_game=True).exclude(id=player1.id).first()

        if not player2:
            return Response({"error": "No available players to start a game."}, status=400)

        # Assign random markers X or O
        player1_marker = random.choice(['X', 'O'])
        player2_marker = 'X' if player1_marker == 'O' else 'O'  # The other player gets the opposite marker
        
        # Create the game
        game = Game.objects.create(player1=player, player2=player2.user, status='ongoing')

        # Set both players as unavailable for further games
        player1.is_available_for_game = False
        player2.is_available_for_game = False
        player1.save()
        player2.save()

        return Response({
            "message": "Game started successfully",
            "game_id": game.id,
            "player1": player.username,  # Use player.username, which is a User instance
            "player2": player2.user.username,  # Use player2.user.username to get the User's username
            "player1_marker": player1_marker,
            "player2_marker": player2_marker,
            "status": game.status
        })

    
@api_view(['POST'])
def make_move(request):
    """
    API to make a move in the Tic-Tac-Toe game.
    """
    serializer = MoveSerializer(data=request.data)
    if serializer.is_valid():
        game_id = serializer.validated_data['game_id']
        position = serializer.validated_data['position']
        player_marker = serializer.validated_data['player']  # 'X' or 'O'
        
        # Fetch the game from the database
        game = Game.objects.get(id=game_id)
        
        # Ensure the game is ongoing
        if game.status != 'ongoing':
            return Response({'error': 'Game is not ongoing'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Ensure the move is valid
        if position < 1 or position > 9:
            return Response({'error': 'Invalid position'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the position is already occupied
        if Move.objects.filter(game=game, position=position).exists():
            return Response({'error': 'Position already occupied'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the move is made by the correct player based on current turn
        if (game.current_turn == 'X' and player_marker != 'X') or (game.current_turn == 'O' and player_marker != 'O'):
            return Response({'error': "It's not your turn."}, status=status.HTTP_400_BAD_REQUEST)

        # Save the move
        move = Move.objects.create(game=game, position=position, player_marker=player_marker)

        game.current_turn = 'X' if game.current_turn == 'O' else 'O'

        # Check for winner or draw
        winner = check_winner(game)
        if winner:
            game.status = 'completed'
            game.winner = winner
            game.save()
            return Response({'message': f'Game over! {winner} wins.'}, status=status.HTTP_200_OK)
        
        # Check for draw
        if Move.objects.filter(game=game).count() == 9:
            game.status = 'completed'
            game.winner = 'Draw'
            game.save()
            return Response({'message': 'Game over! It\'s a draw.'}, status=status.HTTP_200_OK)
        
        game.save()
        return Response({'message': 'Move successfully made', 'current_turn': game.current_turn}, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def check_winner(game):
    """
    Function to check the winner of the game.
    """
    # List all possible winning combinations
    win_conditions = [
        [1, 2, 3], [4, 5, 6], [7, 8, 9],  # Rows
        [1, 4, 7], [2, 5, 8], [3, 6, 9],  # Columns
        [1, 5, 9], [3, 5, 7]              # Diagonals
    ]
    
    # Get the moves made by both players (X and O)
    x_moves = Move.objects.filter(game=game, player='X').values_list('position', flat=True)
    o_moves = Move.objects.filter(game=game, player='O').values_list('position', flat=True)

    # Check for winning conditions
    for condition in win_conditions:
        if all(position in x_moves for position in condition):
            return 'X'
        if all(position in o_moves for position in condition):
            return 'O'
    
    return None

@api_view(['GET'])
def game_status(request, game_id):
    """
    API to get the current status of a game.
    """
    try:
        game = Game.objects.get(id=game_id)
    except Game.DoesNotExist:
        return Response({'error': 'Game not found'}, status=status.HTTP_404_NOT_FOUND)

    # Return game status
    status = {
        "game_id": game.id,
        "status": game.status,
        "current_turn": game.current_turn,
        "player1": game.player1.username,
        "player2": game.player2.username,
        "winner": game.winner.username if game.winner else "None",
    }
    return Response(status)

@api_view(['GET'])
def match_history(request):
    """
    API to get the match history of the logged-in user.
    """
    user = request.user
    games = Game.objects.filter(player1=user) | Game.objects.filter(player2=user)
    games = games.order_by('-created_at')

    game_list = []
    for game in games:
        game_list.append({
            "game_id": game.id,
            "opponent": game.player2.username if game.player1 == user else game.player1.username,
            "status": game.status,
            "winner": game.winner.username if game.winner else "Draw"
        })

    return Response(game_list)



class UpdateUserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        """
        API to update the user's profile.
        """
        try:
            # Fetch the UserProfile instance associated with the logged-in user
            profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Deserialize and validate the input
        serializer = UserProfileUpdateSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Profile updated successfully.', 'profile': serializer.data}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)