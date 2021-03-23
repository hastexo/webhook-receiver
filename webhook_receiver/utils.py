import base64
import hashlib
import hmac
import json
import logging

from django.core.validators import validate_email
from django.conf import settings
from django.db import transaction

from edx_rest_api_client.client import OAuthAPIClient
from ipware import get_client_ip

from .models import JSONWebhookData


EDX_BULK_ENROLLMENT_API_PATH = '%s/api/bulk_enroll/v1/bulk_enroll/'

logger = logging.getLogger(__name__)


def receive_json_webhook(request):
    # Grab data from the request, and save it to the database right
    # away.
    data = JSONWebhookData(headers=dict(request.headers),
                           body=request.body)
    with transaction.atomic():
        data.save()

    # Transition the state from NEW to PROCESSING
    data.start_processing()
    with transaction.atomic():
        data.save()

    # Look up the source IP
    ip, is_routable = get_client_ip(request)
    if ip is None:
        logger.warning("Unable to get client IP for webhook %s" % data.id)
    data.source = ip
    with transaction.atomic():
        data.save()

    # Parse the payload as JSON
    try:
        try:
            data.content = json.loads(data.body)
        except TypeError:
            # Python <3.6 can't call json.loads() on a byte string
            data.content = json.loads(data.body.decode('utf-8'))
    except Exception:
        # For any other exception, set the state to ERROR and then
        # throw the exception up the stack.
        fail_and_save(data)
        raise

    return data


def fail_and_save(data):
    data.fail()
    with transaction.atomic():
        data.save()


def finish_and_save(data):
    data.finish_processing()
    with transaction.atomic():
        data.save()


def get_hmac(key, body):
    digest = hmac.new(key.encode('utf-8'),
                      body,
                      hashlib.sha256).digest()
    return base64.b64encode(digest).decode()


def hmac_is_valid(key, body, hmac_to_verify):
    return get_hmac(key, body) == hmac_to_verify


def enroll_in_course(course_id,
                     email,
                     send_email=True):
    """
    Auto-enroll email in course.

    Uses the bulk enrollment API, defined in lms/djangoapps/bulk_enroll
    """

    # Raises ValidationError if invalid
    validate_email(email)

    client = OAuthAPIClient(
        settings.WEBHOOK_RECEIVER_EDX_OAUTH2_URL_ROOT,
        settings.WEBHOOK_RECEIVER_EDX_OAUTH2_KEY,
        settings.WEBHOOK_RECEIVER_EDX_OAUTH2_SECRET,
    )

    bulk_enroll_url = EDX_BULK_ENROLLMENT_API_PATH % settings.WEBHOOK_RECEIVER_EDX_OAUTH2_URL_ROOT  # noqa: E501

    # The bulk enrollment API allows us to enroll multiple identifiers
    # at once, using a comma-separated list for the courses and
    # identifiers parameters. We deliberately want to process
    # enrollments one by one, so we use a single request for each
    # course/identifier combination.
    request_params = {
        "auto_enroll": True,
        "email_students": send_email,
        "action": "enroll",
        "courses": course_id,
        "identifiers": email,
    }

    logger.debug("Sending POST request "
                 "to %s with parameters %s" % (bulk_enroll_url,
                                               request_params))
    response = client.post(
        bulk_enroll_url,
        request_params
    )

    # Throw an exception if we get any error back from the API.
    # Apart from an HTTP 200, we might also get:
    #
    # HTTP 400: if we've sent a malformed request (for example, one
    #           with a course ID in a format that Open edX can't
    #           parse)
    # HTTP 401: if our authentication token has expired
    # HTTP 403: if our auth token is linked to a user ID that lacks
    #           staff credentials in one of the courses we want to
    #           enroll the learner in
    # HTTP 404: if we've specified a course ID that does not exist
    #           (although it does follow the format that Open edX expects)
    # HTTP 500: in case of a server-side issue
    if response.status_code >= 400:
        logger.error("POST request to %s with parameters %s "
                     "returned HTTP %s" % (bulk_enroll_url,
                                           request_params,
                                           response.status_code))
    response.raise_for_status()

    # If all is well, log the response at the debug level.
    logger.debug("Received response from %s: %s " % (bulk_enroll_url,
                                                     response.json()))
