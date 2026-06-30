from django.test import TestCase

from database.engine.mastery_calculator import MasteryCalculator
from database.engine.progress_manager import ProgressManager
from database.engine.quiz_engine import QuizEngine
from database.engine.stage_generator import StageGenerator
from database.models import Deck, LearningSession, Vocabulary


class QuizFeedbackTest(TestCase):

    def setUp(self):
        self.deck = Deck.objects.create(name="Feedback Deck")
        self.vocabulary = Vocabulary.objects.create(
            deck=self.deck,
            hanzi="字",
            pinyin="zi",
            meaning="character",
            source="TEST",
        )
        for i, pinyin in enumerate(["ba", "ma", "ta", "na"], start=1):
            Vocabulary.objects.create(
                deck=self.deck,
                hanzi=f"字{i}",
                pinyin=pinyin,
                meaning=f"meaning {i}",
                source="TEST",
            )
        self.session = StageGenerator(self.deck).generate()["session"]

    def test_submit_answer_returns_feedback_payload(self):
        engine = QuizEngine(self.session)

        feedback = engine.submit_answer(self.vocabulary.id, "wrong")

        self.assertFalse(feedback["correct"])
        self.assertEqual(feedback["hanzi"], self.vocabulary.hanzi)
        self.assertEqual(feedback["selected_answer"], "wrong")
        self.assertEqual(feedback["correct_answer"], self.vocabulary.pinyin)
        self.assertEqual(feedback["meaning"], self.vocabulary.meaning)

    def test_question_generator_handles_small_deck(self):
        deck = Deck.objects.create(name="Tiny Deck")
        correct = Vocabulary.objects.create(
            deck=deck,
            hanzi="字",
            pinyin="zi",
            meaning="character",
            source="TEST",
        )
        Vocabulary.objects.create(
            deck=deck,
            hanzi="A",
            pinyin="ba",
            meaning="meaning",
            source="TEST",
        )

        from database.engine.question_generator import QuestionGenerator

        question = QuestionGenerator(correct).generate()

        self.assertEqual(question["id"], correct.id)
        self.assertEqual(len(question["choices"]), 2)

    def test_can_next_stage_requires_no_pending_items(self):
        deck = Deck.objects.create(name="Pending Stage Deck", stage_size=2, mastery_target=0)
        first = Vocabulary.objects.create(
            deck=deck,
            hanzi="字",
            pinyin="zi",
            meaning="character",
            source="TEST",
        )
        second = Vocabulary.objects.create(
            deck=deck,
            hanzi="词",
            pinyin="ci",
            meaning="word",
            source="TEST",
        )
        session = StageGenerator(deck).generate()["session"]

        ProgressManager(session).answer_correct(first)

        calculator = MasteryCalculator(session)
        progress = calculator.get_stage_progress()

        self.assertEqual(progress["pending"], 1)
        self.assertFalse(calculator.can_next_stage())
        self.assertEqual(progress["total"], 2)

    def test_can_next_stage_requires_all_items_shown(self):
        deck = Deck.objects.create(name="Shown Stage Deck", stage_size=2, mastery_target=80)
        first = Vocabulary.objects.create(
            deck=deck,
            hanzi="字",
            pinyin="zi",
            meaning="character",
            source="TEST",
        )
        second = Vocabulary.objects.create(
            deck=deck,
            hanzi="词",
            pinyin="ci",
            meaning="word",
            source="TEST",
        )
        session = StageGenerator(deck).generate()["session"]

        manager = ProgressManager(session)
        manager.answer_correct(first)

        calculator = MasteryCalculator(session)
        progress = calculator.get_stage_progress()

        self.assertEqual(progress["shown"], 1)
        self.assertEqual(progress["total"], 2)
        self.assertFalse(calculator.can_next_stage())
