from celery import shared_task
from celery.utils.log import get_task_logger

from requests.exceptions import HTTPError

from webhook_receiver.tasks import OrderTask

from .models import WooCommerceOrder as Order
from .utils import process_order


logger = get_task_logger(__name__)


@shared_task(bind=True,
             max_retries=3,
             soft_time_limit=5,
             base=OrderTask,
             autoretry_for=(HTTPError,))
def process(self, data, send_email=False):
    """Parse input data for line items, and create enrollments.

    On any error, raise the exception in order to be handled by
    on_failure().
    """

    logger.debug('Processing order data: %s' % data)
    self.order = Order.objects.get(id=data['id'])

    process_order(self.order, data, send_email)
