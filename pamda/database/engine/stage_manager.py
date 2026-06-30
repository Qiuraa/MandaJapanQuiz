from database.models import LearningSession


class StageManager:

    def __init__(self, session):
        self.session = session

    def get_current_stage(self):
        """
        Mengembalikan stage yang sedang dimainkan.
        """
        return self.session.current_stage

    def get_total_stage(self):
        """
        Mengembalikan jumlah total stage pada deck.
        """
        return self.session.total_stage

    def is_last_stage(self):
        """
        Mengecek apakah stage saat ini adalah stage terakhir.
        """
        return self.session.current_stage >= self.session.total_stage

    def next_stage(self):
        """
        Naik ke stage berikutnya.
        Return True jika berhasil.
        Return False jika sudah stage terakhir.
        """

        if self.is_last_stage():
            return False

        self.session.current_stage += 1

        self.session.save(update_fields=["current_stage"])

        return True

    def reset_stage(self):
        """
        Mengembalikan stage ke Stage 1.
        Digunakan saat user memilih Mulai dari Awal.
        """

        self.session.current_stage = 1

        self.session.save(update_fields=["current_stage"])

    def set_stage(self, stage):
        """
        Digunakan untuk debugging atau testing.
        """

        if stage < 1:
            stage = 1

        if stage > self.session.total_stage:
            stage = self.session.total_stage

        self.session.current_stage = stage

        self.session.save(update_fields=["current_stage"])

        return self.session.current_stage
