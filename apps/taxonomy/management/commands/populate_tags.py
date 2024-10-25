from django.core.management.base import BaseCommand
from django.db import transaction

from apps.taxonomy.models import Tag

TAGS = [
    ("native", Tag.DOE),
    ("captive", Tag.DOE),
    ("cultivated", Tag.DOE),
    ("released", Tag.DOE),
    ("failing", Tag.DOE),
    ("casual", Tag.DOE),
    ("reproducing", Tag.DOE),
    ("established", Tag.DOE),
    ("colonising", Tag.DOE),
    ("invasive", Tag.DOE),
    ("widespreadInvasive", Tag.DOE),
    ("doubtful occurrence", Tag.ECOLOGICAL),
    ("CITES", Tag.DIRECTIVE),
    ("directiva aves", Tag.DIRECTIVE),
]


class Command(BaseCommand):
    help = "Loads tags with their types from a predefined list"

    def populate_tags(self):
        tag_objects = []
        for tag in TAGS:
            tag_objects.append(Tag(name=tag[0], tag_type=tag[1]))

        Tag.objects.bulk_create(tag_objects, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(f'Successfully created tags'))

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.populate_tags()