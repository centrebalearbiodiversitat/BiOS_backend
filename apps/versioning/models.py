from django.db import models


class Source(models.Model):
    DATABASE = 0
    JOURNAL_ARTICLE = 1
    BOOK = 2
    AI = 3
    WEB_PAGE = 4
    DOCUMENT = 5
    EXPERT = 6

    ORIGIN_CHOICES = (
        (DATABASE, 'database'),
        (JOURNAL_ARTICLE, 'journal_article'),
        (BOOK, 'book'),
        (AI, 'ai'),
        (WEB_PAGE, 'web_page'),
        (DOCUMENT, 'document'),
        (EXPERT, 'expert'),
    )
    TRANSLATE_CHOICES = {
        DATABASE: 'database',
        'database': DATABASE,
        JOURNAL_ARTICLE: 'journal_article',
        'journal_article': JOURNAL_ARTICLE,
        BOOK: 'book',
        'book': BOOK,
        AI: 'ai',
        'ai': AI,
        WEB_PAGE: 'web_page',
        'web_page': WEB_PAGE,
        DOCUMENT: 'document',
        'document': DOCUMENT,
        EXPERT: 'expert',
        'expert': EXPERT,
    }

    name = models.CharField(max_length=255, unique=True)
    origin = models.PositiveSmallIntegerField(choices=ORIGIN_CHOICES)

    def __str__(self):
        return self.name


class Batch(models.Model):
    PENDING = 0
    ACCEPTED = 1
    REJECTED = 2
    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
    )
    
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=PENDING)

    def __str__(self):
        return f'{self.created_at.year}-{self.created_at.month}-{self.created_at.day}__{self.id}'

    class Meta:
        verbose_name_plural = "batches"
