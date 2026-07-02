from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    preferred_language = models.CharField(max_length=20, default="mandarin")

    def __str__(self):
        return self.user.username


class Deck(models.Model):
    name = models.CharField(max_length=50, unique=True)

    description = models.TextField(blank=True)

    stage_size = models.PositiveIntegerField(default=20)

    mastery_target = models.PositiveIntegerField(default=80)

    def __str__(self):
        return self.name
    
class Vocabulary(models.Model):

    deck = models.ForeignKey(
        Deck,
        on_delete=models.CASCADE,
        related_name="vocabularies"
    )

    hanzi = models.CharField(max_length=50)

    pinyin = models.CharField(max_length=100)

    meaning = models.CharField(max_length=200)

    source = models.CharField(
        max_length=100,
        blank=True
    )

    def __str__(self):
        return self.hanzi

class LearningSession(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="learning_sessions",
        null=True,
        blank=True,
    )

    deck = models.ForeignKey(
        Deck,
        on_delete=models.CASCADE,
        related_name="learning_sessions"
    )

    current_stage = models.PositiveIntegerField(default=1)

    total_stage = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    last_played = models.DateTimeField(auto_now=True)

    last_vocabulary = models.ForeignKey(
    Vocabulary,
    on_delete=models.SET_NULL,
    null=True,
    blank=True
    )
class StageAssignment(models.Model):

    session = models.ForeignKey(
        LearningSession,
        on_delete=models.CASCADE,
        related_name="assignments"
    )

    vocabulary = models.ForeignKey(
        Vocabulary,
        on_delete=models.CASCADE
    )

    stage = models.PositiveIntegerField()

    class Meta:
        unique_together = ("session", "vocabulary")

        indexes = [
            models.Index(fields=['session', 'stage'])
        ]

class Progress(models.Model):

    session = models.ForeignKey(
        LearningSession,
        on_delete=models.CASCADE,
        related_name="progresses"
    )

    vocabulary = models.ForeignKey(
        Vocabulary,
        on_delete=models.CASCADE,
        related_name="progresses",
    )

    mastery = models.SmallIntegerField(default=0)

    first_try_correct = models.BooleanField(default=False)

    review_count = models.PositiveIntegerField(default=0)

    last_review = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        unique_together = ("session", "vocabulary")