import random

from database.models import (
    StageAssignment,
    Progress,
)


class WeightedSelector:

    def __init__(self, session):
        self.session = session

    def get_next_vocabulary(self):

        available = self._available_stages()

        if not available:
            return None

        stage = self._select_stage(available)

        assignments, progress_dict = self._load_stage(stage)

        return self._weighted_random(
            assignments,
            progress_dict
        )

    def _available_stages(self):

        available = []

        for stage in range(
            1,
            self.session.current_stage + 1
        ):

            assignments = StageAssignment.objects.filter(
                session=self.session,
                stage=stage
            )

            vocab_ids = assignments.values_list(
                "vocabulary_id",
                flat=True
            )

            exists = Progress.objects.filter(
                session=self.session,
                vocabulary_id__in=vocab_ids,
                first_try_correct=False
            ).exists()

            if exists:
                available.append(stage)

        return available

    def _select_stage(self, stages):

        weights = stages

        return random.choices(
            stages,
            weights=weights,
            k=1
        )[0]

    def _load_stage(self, stage):

        assignments = StageAssignment.objects.filter(
            session=self.session,
            stage=stage
        ).select_related("vocabulary")

        vocab_ids = [
            assignment.vocabulary.id
            for assignment in assignments
        ]

        progress_dict = {

            progress.vocabulary_id: progress

            for progress in Progress.objects.filter(
                session=self.session,
                vocabulary_id__in=vocab_ids
            )

        }

        return assignments, progress_dict

    def _weighted_random(
        self,
        assignments,
        progress_dict
    ):

        vocabularies = []
        weights = []

        for assignment in assignments:

            progress = progress_dict[
                assignment.vocabulary.id
            ]

            if progress.first_try_correct:
                continue

            weight = 6 - progress.mastery

            vocabularies.append(
                assignment.vocabulary
            )

            weights.append(weight)

        if not vocabularies:
            return None

        return random.choices(
            vocabularies,
            weights=weights,
            k=1
        )[0]