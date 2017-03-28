from celery import Task
from celery import shared_task
from celery.utils.log import get_task_logger

from .models import Order
from .utils import process_order

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

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Failure handler: log an exception stack trace and a prose message,
        then save the order with an ERROR status.

        """

        logger.error(exc, exc_info=True)
        logger.error('Failed to fully '
                     'process order %s '
                     '(task ID %s)' % (self.order.id,
                                       task_id))
        self.order.status = Order.ERROR
        self.order.save()


@shared_task(bind=True,
             max_retries=3,
             soft_time_limit=5,
             base=OrderTask)
def process(self, data, send_email=False):
    """Parse input data for line items, and create enrollments.

    On any error, raise the exception in order to be handled by
    on_failure().
    """

    logger.debug('Processing order data: %s' % data)
    self.order = Order.objects.get(id=data['id'])

    process_order(self.order, data, send_email, logger)
