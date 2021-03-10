from django.db.models import Model
from django.db.models import GenericIPAddressField, BinaryField, DateTimeField
from django.db.models import CharField, BigIntegerField, EmailField
try:
    # Django 3.1 and later has a built-in JSONField
    from django.db.models import JSONField
except ImportError:
    # For earlier Django versions we must use JSONField from
    # django-jsonfield-backport
    from django_jsonfield_backport.models import JSONField

from django_fsm import FSMIntegerField, ConcurrentTransitionMixin, transition
from django.utils import timezone

from . import STATE

import logging


APP_LABEL = 'webhook_receiver'

logger = logging.getLogger(__name__)


class WebhookData(ConcurrentTransitionMixin, Model):
    """Abstract base class for webhook data."""
    class Meta:
        app_label = APP_LABEL
        abstract = True

    NEW = STATE.NEW
    PROCESSING = STATE.PROCESSING
    PROCESSED = STATE.PROCESSED
    ERROR = STATE.ERROR

    CHOICES = STATE.CHOICES

    # We know we always want to record the webhook source, and the
    # date we received it.
    status = FSMIntegerField(choices=CHOICES,
                             default=NEW,
                             protected=True)
    source = GenericIPAddressField(null=True)
    received = DateTimeField(default=timezone.now)
    headers = JSONField()
    # This is for storing the webhook payload exactly as received
    # (i.e. from request.body), which comes in handy for signature
    # verification.
    body = BinaryField()

    @transition(field=status,
                source=NEW,
                target=PROCESSING,
                on_error=ERROR)
    def start_processing(self):
        logger.debug('Processing webhook %s' % self.id)

    @transition(field=status,
                source=PROCESSING,
                target=PROCESSED,
                on_error=ERROR)
    def finish_processing(self):
        logger.debug('Finishing webhook %s' % self.id)

    @transition(field=status,
                source=PROCESSING,
                target=ERROR)
    def fail(self):
        logger.debug('Failed to process webhook %s' % self.id)


class JSONWebhookData(WebhookData):

    class Meta:
        app_label = APP_LABEL
        abstract = False

    # In addition to the webhook source and timestamp, we also want
    # the webhook content, which in this case is always JSON data.
    content = JSONField(null=True)


class Order(ConcurrentTransitionMixin, Model):
    class Meta:
        app_label = APP_LABEL
        abstract = True

    NEW = STATE.NEW
    PROCESSING = STATE.PROCESSING
    PROCESSED = STATE.PROCESSED
    ERROR = STATE.ERROR

    CHOICES = STATE.CHOICES

    id = BigIntegerField(primary_key=True, editable=False)
    email = EmailField()
    first_name = CharField(max_length=254)
    last_name = CharField(max_length=254)
    received = DateTimeField(default=timezone.now)
    status = FSMIntegerField(choices=CHOICES,
                             default=NEW,
                             protected=True)

    @transition(field=status,
                source=NEW,
                target=PROCESSING,
                on_error=ERROR)
    def start_processing(self):
        logger.debug('Processing order %s' % self.id)

    @transition(field=status,
                source=PROCESSING,
                target=PROCESSED,
                on_error=ERROR)
    def finish_processing(self):
        logger.debug('Finishing order %s' % self.id)

    @transition(field=status,
                source=PROCESSING,
                target=ERROR)
    def fail(self):
        logger.debug('Failed to process order %s' % self.id)


class OrderItem(ConcurrentTransitionMixin, Model):
    class Meta:
        app_label = APP_LABEL
        abstract = True

    NEW = STATE.NEW
    PROCESSING = STATE.PROCESSING
    PROCESSED = STATE.PROCESSED
    ERROR = STATE.ERROR

    CHOICES = STATE.CHOICES

    sku = CharField(max_length=254)
    email = EmailField()
    status = FSMIntegerField(choices=CHOICES,
                             default=NEW,
                             protected=True)

    @transition(field=status,
                source=NEW,
                target=PROCESSING,
                on_error=ERROR)
    def start_processing(self):
        logger.debug('Processing item %s for order %s' % (self.id,
                                                          self.order.id))

    @transition(field=status,
                source=PROCESSING,
                target=PROCESSED,
                on_error=ERROR)
    def finish_processing(self):
        logger.debug('Finishing item %s for order %s' % (self.id,
                                                         self.order.id))

    @transition(field=status,
                source=PROCESSING,
                target=ERROR)
    def fail(self):
        logger.debug('Failed to process item %s '
                     'for order %s' % (self.id,
                                       self.order.id))
