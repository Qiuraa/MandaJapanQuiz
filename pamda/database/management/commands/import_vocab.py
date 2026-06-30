import json
from pathlib import Path

from django.core.management.base import BaseCommand

from database.models import Deck, Vocabulary


class Command(BaseCommand):

    help = "Import vocabulary JSON"

    def handle(self, *args, **kwargs):

        folder = Path(__file__).resolve().parents[2] / "json"

        if not folder.exists():
            self.stdout.write(self.style.ERROR(f"Folder JSON tidak ditemukan: {folder}"))
            return

        Deck.objects.filter(name="HSK").delete()

        files = sorted(folder.glob("*.json"))
        if not files:
            self.stdout.write(self.style.WARNING(f"Tidak ada file JSON di {folder}"))
            return

        for file in files:
            deck_name = file.stem.upper()
            deck, _ = Deck.objects.get_or_create(name=deck_name)

            self.stdout.write(f"Import {file.name} -> {deck_name}")

            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)

            for item in data:
                forms = item.get("forms") or []
                if not forms:
                    continue

                form = forms[0]
                transcriptions = form.get("transcriptions", {})

                Vocabulary.objects.create(
                    deck=deck,
                    hanzi=item.get("simplified", ""),
                    pinyin=transcriptions.get("pinyin", ""),
                    meaning="; ".join(form.get("meanings", [])),
                    source=file.stem,
                )

        self.stdout.write(self.style.SUCCESS("Import selesai."))