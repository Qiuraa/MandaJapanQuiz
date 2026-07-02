from database.engine.stage_manager import StageManager
from database.engine.weighted_selector import WeightedSelector
from database.engine.question_generator import QuestionGenerator
from database.engine.progress_manager import ProgressManager
from database.engine.mastery_calculator import MasteryCalculator

import re
import unicodedata

from database.models import Vocabulary


class QuizEngine:

    def __init__(self, session):

        self.session = session

        self.stage_manager = StageManager(session)

        self.selector = WeightedSelector(session)

        self.progress_manager = ProgressManager(session)

        self.mastery = MasteryCalculator(session)

    def next_question(self):

        vocabulary = self.selector.get_next_vocabulary()

        # Masih ada soal
        if vocabulary is not None:

            question = QuestionGenerator(
                vocabulary
            ).generate()

            question["status"] = "QUESTION"

            return question

        # Stage selesai?
        if self.mastery.can_next_stage():

            if self.stage_manager.next_stage():

                vocabulary = self.selector.get_next_vocabulary()

                if vocabulary is not None:

                    question = QuestionGenerator(
                        vocabulary
                    ).generate()

                    question["status"] = "NEXT_STAGE"

                    question["current_stage"] = (
                        self.session.current_stage
                    )

                    return question

        # Deck selesai?
        if self.stage_manager.is_last_stage():

            return {

                "status": "FINISHED"

            }

        # Masih ada review yang belum selesai
        return {

            "status": "REVIEW"

        }

    def submit_answer(
        self,
        vocabulary_id,
        selected_answer,
        quiz_mode="choice"
    ):

        vocabulary = Vocabulary.objects.get(
            id=vocabulary_id
        )

        normalized_selected = self._normalize_answer(
            selected_answer,
            quiz_mode,
            vocabulary
        )
        normalized_correct = self._normalize_answer(
            vocabulary.pinyin,
            quiz_mode,
            vocabulary
        )

        correct = (
            normalized_selected ==
            normalized_correct
        )

        if correct:

            self.progress_manager.answer_correct(
                vocabulary
            )

        else:

            self.progress_manager.answer_wrong(
                vocabulary
            )

        stage_up = False

        if self.mastery.can_next_stage():

            stage_up = self.stage_manager.next_stage()

        result = self.next_question()

        result["correct"] = correct
        result["hanzi"] = vocabulary.hanzi
        result["selected_answer"] = selected_answer
        result["correct_answer"] = vocabulary.pinyin
        result["meaning"] = vocabulary.meaning
        result["stage_up"] = stage_up
        result["quiz_mode"] = quiz_mode

        return result

    def _normalize_answer(self, value, quiz_mode, vocabulary):
        if not value:
            return ""

        normalized = str(value).strip()

        if quiz_mode == "keyboard":
            normalized = normalized.casefold()
            normalized = normalized.replace(" ", "")
            normalized = normalized.replace("-", "")
            normalized = normalized.replace("・", "")

            normalized = normalized.replace("～", "")

            # a
            normalized = normalized.replace("ā", "a")
            normalized = normalized.replace("á", "a")
            normalized = normalized.replace("ǎ", "a")
            normalized = normalized.replace("à", "a")

            # e
            normalized = normalized.replace("ē", "e")
            normalized = normalized.replace("é", "e")
            normalized = normalized.replace("ě", "e")
            normalized = normalized.replace("è", "e")

            # i
            normalized = normalized.replace("ī", "i")
            normalized = normalized.replace("í", "i")
            normalized = normalized.replace("ǐ", "i")
            normalized = normalized.replace("ì", "i")

            # o
            normalized = normalized.replace("ō", "o")
            normalized = normalized.replace("ó", "o")
            normalized = normalized.replace("ǒ", "o")
            normalized = normalized.replace("ò", "o")

            # u
            normalized = normalized.replace("ū", "u")
            normalized = normalized.replace("ú", "u")
            normalized = normalized.replace("ǔ", "u")
            normalized = normalized.replace("ù", "u")

            # ü -> v
            normalized = normalized.replace("ü", "v")
            normalized = normalized.replace("ǖ", "v")
            normalized = normalized.replace("ǘ", "v")
            normalized = normalized.replace("ǚ", "v")
            normalized = normalized.replace("ǜ", "v")
            # normalized = normalized.replace("ゃ", "や")
            # normalized = normalized.replace("ゅ", "ゆ")
            # normalized = normalized.replace("ょ", "よ")

            return normalized

        return normalized.casefold().replace(" ", "")