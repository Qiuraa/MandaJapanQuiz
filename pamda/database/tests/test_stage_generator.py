from django.contrib.auth.models import User
from django.test import TestCase

from database.models import (
    Deck,
    Vocabulary,
    LearningSession,
    StageAssignment,
    Progress,
)

from database.engine.stage_generator import StageGenerator


class StageGeneratorTest(TestCase):

    def setUp(self):

        self.deck = Deck.objects.create(
            name="HSK 1"
        )

        # Buat 100 vocabulary dummy
        for i in range(100):

            Vocabulary.objects.create(
                deck=self.deck,
                hanzi=f"字{i}",
                pinyin=f"zi{i}",
                meaning=f"Meaning {i}",
                source="TEST"
            )

    def test_generate(self):

        generator = StageGenerator(self.deck)

        result = generator.generate()

        self.assertEqual(
            LearningSession.objects.count(),
            1
        )

        self.assertEqual(
            StageAssignment.objects.count(),
            100
        )

        self.assertEqual(
            Progress.objects.count(),
            100
        )

        self.assertEqual(
            result["total_stage"],
            5
        )

        self.assertEqual(
            result["total_vocabulary"],
            100
        )

    def test_generate_keeps_other_users_sessions_for_same_deck(self):
        other_user = User.objects.create_user(username="other", password="secret")
        LearningSession.objects.create(deck=self.deck, user=other_user)

        generator = StageGenerator(self.deck)
        generator.generate()

        self.assertEqual(
            LearningSession.objects.filter(user=other_user).count(),
            1
        )

