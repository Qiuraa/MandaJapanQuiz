import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from database.models import Deck, Vocabulary


class Command(BaseCommand):

    help = "Import JLPT vocabulary CSV"

    def handle(self, *args, **kwargs):

        folder = Path(__file__).resolve().parents[2] / "csv"

        if not folder.exists():
            self.stdout.write(
                self.style.ERROR(f"Folder CSV tidak ditemukan: {folder}")
            )
            return

        Deck.objects.filter(name__startswith="N").delete()

        files = sorted(folder.glob("*.csv"))

        if not files:
            self.stdout.write(
                self.style.WARNING(f"Tidak ada file CSV di {folder}")
            )
            return

        for file in files:

            deck_name = file.stem.upper()
            deck, _ = Deck.objects.get_or_create(name=deck_name)

            self.stdout.write(f"Import {file.name} -> {deck_name}")

            with open(file, "r", encoding="utf-8-sig", newline="") as f:

                reader = csv.DictReader(f)

                for row in reader:

                    Vocabulary.objects.create(
                        deck=deck,
                        hanzi=row["expression"].strip(),
                        pinyin=row["reading"].strip(),
                        meaning=row["meaning"].strip(),
                        source=file.stem,
                    )

        self.stdout.write(
            self.style.SUCCESS("Import selesai.")
        )