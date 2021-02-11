from celery import Task
from celery.utils.log import get_task_logger

from django.db import transaction

logger = get_task_logger(__name__)


class OrderTask(Task):
    """Process a newly received order.

    On failure, store the order in an ERROR state.
    """

    def __init__(self):
        """Set up an order as an instance member, so we can manipulate it both
        from task methods and from handlers.
        """

        self.order = None

    def on_success(self, retval, task_id, args, kwargs):
        "Success handler: log successful order processing."
        logger.info('Successfully processed '
                    'order %s' % self.order.id)

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Retry handler: log an exception stack trace and a prose message,
        then save the order with an ERROR status.

        """
        logger.warning('Failed to fully '
                       'process order %s '
                       '(task ID %s), retrying: %s' % (self.order.id,
                                                       task_id,
                                                       exc))

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Failure handler: log an exception stack trace and a prose message,
        then save the order with an ERROR status

        """
        logger.error('Failed to fully '
                     'process order %s '
                     '(task ID %s): %s' % (self.order.id,
                                           task_id,
                                           exc))
        self.order.fail()
        with transaction.atomic():
            self.order.save()
