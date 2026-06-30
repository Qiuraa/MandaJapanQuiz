from database.models import Progress, StageAssignment


class MasteryCalculator:

    MASTERED_SCORE = 3

    def __init__(self, session):
        self.session = session

    def get_stage_progress(self):
        assignments = StageAssignment.objects.filter(
            session=self.session,
            stage=self.session.current_stage
        )

        total = assignments.count()

        if total == 0:
            return {
                "shown": 0,
                "mastered": 0,
                "pending": 0,
                "total": 0,
                "rate": 0,
            }

        shown = 0
        mastered = 0

        for assignment in assignments:

            progress = Progress.objects.get(
                session=self.session,
                vocabulary=assignment.vocabulary
            )

            if progress.review_count > 0:
                shown += 1

            if (
                progress.first_try_correct
                or progress.mastery >= self.MASTERED_SCORE
            ):
                mastered += 1

        pending = total - mastered

        rate = round(mastered / total * 100, 1)

        return {
            "shown": shown,
            "mastered": mastered,
            "pending": pending,
            "total": total,
            "rate": rate,
        }

    def can_next_stage(self):

        progress = self.get_stage_progress()

        return (
            progress["shown"] == progress["total"]
            and
            progress["rate"] >=
            self.session.deck.mastery_target
        )
