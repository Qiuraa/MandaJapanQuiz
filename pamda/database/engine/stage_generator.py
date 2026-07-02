import random

from database.models import (
    LearningSession,
    Vocabulary,
    StageAssignment,
    Progress,
)


class StageGenerator:

    def __init__(self, deck, user=None):
        self.deck = deck
        self.user = user

    def generate(self):
        """
        Membuat Learning Session baru.

        Flow:
        1. Hapus session lama
        2. Buat session baru
        3. Ambil semua vocabulary pada deck
        4. Acak vocabulary
        5. Bagi menjadi stage
        6. Simpan StageAssignment
        7. Buat Progress
        """

        # Hapus session lama milik user yang sama jika ada
        if hasattr(self, "user") and self.user is not None:
            LearningSession.objects.filter(
                deck=self.deck,
                user=self.user
            ).delete()
        else:
            LearningSession.objects.filter(
                deck=self.deck,
                user__isnull=True
            ).delete()

        # Buat session baru
        session = LearningSession.objects.create(
            deck=self.deck,
            user=getattr(self, "user", None)
        )

        # Ambil seluruh vocabulary
        vocabularies = list(
            Vocabulary.objects.filter(
                deck=self.deck
            )
        )

        # Pastikan deck tidak kosong
        if not vocabularies:
            raise Exception(
                "Deck tidak memiliki vocabulary."
            )

        # Acak urutan vocabulary
        random.shuffle(vocabularies)

        assignments = []
        progresses = []

        stage_size = self.deck.stage_size

        # Assign stage
        for index, vocabulary in enumerate(vocabularies):

            stage = (index // stage_size) + 1

            assignments.append(
                StageAssignment(
                    session=session,
                    vocabulary=vocabulary,
                    stage=stage
                )
            )

            progresses.append(
                Progress(
                    session=session,
                    vocabulary=vocabulary,
                    mastery=0,
                    first_try_correct=False,
                    review_count=0
                )
            )

        # Simpan sekaligus (lebih cepat)
        StageAssignment.objects.bulk_create(assignments)
        Progress.objects.bulk_create(progresses)

        total_stage = (
            len(vocabularies) + stage_size - 1
        ) // stage_size

        session.total_stage = total_stage
        session.save(update_fields=["total_stage"])

        return {
            "session": session,
            "total_stage": total_stage,
            "total_vocabulary": len(vocabularies),
            "stage_size": stage_size,
        }
