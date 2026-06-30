from django.test import TestCase

from database.engine.stage_generator import StageGenerator
from database.engine.weighted_selector import WeightedSelector

from database.models import Deck
from database.models import Vocabulary


class WeightedSelectorTest(TestCase):

    def setUp(self):

        deck = Deck.objects.create(
            name="HSK"
        )

        for i in range(100):

            Vocabulary.objects.create(
                deck=deck,
                hanzi=f"字{i}",
                pinyin=f"zi{i}",
                meaning="test",
                source="TEST"
            )

        generator = StageGenerator(deck)

        result = generator.generate()

        self.session = result["session"]

        self.session.current_stage = 5
        self.session.save()

    def test_selector(self):

        selector = WeightedSelector(self.session)

        vocab = selector.get_next_vocabulary()

        self.assertIsNotNone(vocab)