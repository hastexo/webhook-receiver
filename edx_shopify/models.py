from django.db import models
from django.utils import timezone

from django_fsm import FSMIntegerField, ConcurrentTransitionMixin, transition

from . import STATE

import logging


APP_LABEL = 'edx_shopify'

logger = logging.getLogger(__name__)


class Order(ConcurrentTransitionMixin, models.Model):
    class Meta:
        app_label = APP_LABEL

    NEW = STATE.NEW
    PROCESSING = STATE.PROCESSING
    PROCESSED = STATE.PROCESSED
    ERROR = STATE.ERROR

    CHOICES = STATE.CHOICES

    id = models.BigIntegerField(primary_key=True, editable=False)
    email = models.EmailField()
    first_name = models.CharField(max_length=254)
    last_name = models.CharField(max_length=254)
    received = models.DateTimeField(default=timezone.now)
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


class OrderItem(ConcurrentTransitionMixin, models.Model):
    class Meta:
        app_label = APP_LABEL

    NEW = STATE.NEW
    PROCESSING = STATE.PROCESSING
    PROCESSED = STATE.PROCESSED
    ERROR = STATE.ERROR

    CHOICES = STATE.CHOICES

    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT
    )
    sku = models.CharField(max_length=254)
    email = models.EmailField()
    status = FSMIntegerField(choices=CHOICES,
                             default=NEW,
                             protected=True)

    unique_together = ('order', 'sku', 'email')

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
