from django.utils import timezone

from database.models import Progress


class ProgressManager:

    MIN_MASTERY = -5
    MAX_MASTERY = 5

    def __init__(self, session):
        self.session = session

    def answer_correct(self, vocabulary):

        progress = Progress.objects.get(
            session=self.session,
            vocabulary=vocabulary
        )

        # Benar pada kemunculan pertama
        if progress.review_count == 0:

            progress.first_try_correct = True
            progress.mastery = self.MAX_MASTERY

        else:

            progress.mastery = min(
                progress.mastery + 2,
                self.MAX_MASTERY
            )

        progress.review_count += 1
        progress.last_review = timezone.now()

        progress.save()

        return progress

    def answer_wrong(self, vocabulary):

        progress = Progress.objects.get(
            session=self.session,
            vocabulary=vocabulary
        )

        # Salah pertama lebih berat
        if progress.review_count == 0:

            progress.mastery = -2

        else:

            progress.mastery = max(
                progress.mastery - 1,
                self.MIN_MASTERY
            )

        progress.review_count += 1
        progress.first_try_correct = False
        progress.last_review = timezone.now()

        progress.save()

        return progress