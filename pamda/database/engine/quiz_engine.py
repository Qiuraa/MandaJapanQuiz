from database.engine.stage_manager import StageManager
from database.engine.weighted_selector import WeightedSelector
from database.engine.question_generator import QuestionGenerator
from database.engine.progress_manager import ProgressManager
from database.engine.mastery_calculator import MasteryCalculator

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
        selected_answer
    ):

        vocabulary = Vocabulary.objects.get(
            id=vocabulary_id
        )

        normalized_selected = (
            selected_answer or ""
        ).strip().casefold()

        normalized_correct = (
            vocabulary.pinyin
        ).strip().casefold()

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

        return result