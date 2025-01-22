
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Move, Game

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user


class MoveSerializer(serializers.Serializer):
    game_id = serializers.IntegerField()
    position = serializers.IntegerField()
    player_marker = serializers.CharField(max_length=1)  # Expecting 'X' or 'O'

    def validate(self, data):
        game = Game.objects.get(id=data['game_id'])
        if game.status != 'ongoing':
            raise serializers.ValidationError("The game is not ongoing.")
        if Move.objects.filter(game=game, position=data['position']).exists():
            raise serializers.ValidationError("This position is already occupied.")
        return data
    
class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['is_available_for_game']  # Add any other fields you want users to update
