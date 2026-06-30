import random

from database.models import Vocabulary


class QuestionGenerator:

    def __init__(self, vocabulary):

        self.vocabulary = vocabulary

    def generate(self):

        correct_answer = self.vocabulary.pinyin

        wrong_answers = self._get_wrong_answers()

        choices = wrong_answers + [correct_answer]

        random.shuffle(choices)

        return {

            "id": self.vocabulary.id,
            "hanzi": self.vocabulary.hanzi,
            "choices": choices,
            "answer": correct_answer

        }

    def _get_wrong_answers(self):

        wrong = list(

            Vocabulary.objects.filter(
                deck=self.vocabulary.deck
            ).exclude(
                id=self.vocabulary.id
            ).values_list(
                "pinyin",
                flat=True
            ).distinct()

        )

        if not wrong:
            return []

        sample_size = min(3, len(wrong))

        return random.sample(wrong, sample_size)