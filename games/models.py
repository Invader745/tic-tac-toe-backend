from django.db import models

# Create your models here.


from django.contrib.auth.models import User

class Game(models.Model):
    STATUS_CHOICES = [
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
    ]

    player1 = models.ForeignKey(User, related_name='games_as_player1', on_delete=models.CASCADE)
    player2 = models.ForeignKey(User, related_name='games_as_player2', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ongoing')
    winner = models.ForeignKey(User, related_name='games_won', on_delete=models.SET_NULL, null=True, blank=True)
    current_turn = models.CharField(max_length=1, choices=[('X', 'X'), ('O', 'O')], default='X')  # New field
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Game between {self.player1} and {self.player2} - {self.status}"


class Move(models.Model):
    game = models.ForeignKey(Game, related_name='moves', on_delete=models.CASCADE)
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    position = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Move by {self.player} at position {self.position}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_available_for_game = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Profile"
