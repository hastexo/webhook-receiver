from .celery import app as celery_app  # noqa: F401


class STATE:
    NEW = 0
    PROCESSING = 1
    PROCESSED = 2
    ERROR = -1

    CHOICES = (
        (NEW, 'New'),
        (PROCESSING, 'Processing'),
        (PROCESSED, 'Processed'),
        (ERROR, 'Error'),
    )
