import logging

from django.core.validators import validate_email
from django.conf import settings
from edx_rest_api_client.client import OAuthAPIClient

EDX_BULK_ENROLLMENT_API_PATH = '%s/api/bulk_enroll/v1/bulk_enroll/'


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
        settings.SOCIAL_AUTH_EDX_OAUTH2_URL_ROOT,
        settings.SOCIAL_AUTH_EDX_OAUTH2_KEY,
        settings.SOCIAL_AUTH_EDX_OAUTH2_SECRET,
    )

    bulk_enroll_url = EDX_BULK_ENROLLMENT_API_PATH % settings.SOCIAL_AUTH_EDX_OAUTH2_URL_ROOT  # noqa: E501

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

    logging.debug("Sending POST request "
                  "to %s with parameters %s" % (bulk_enroll_url,
                                                request_params))
    response = client.post(
        bulk_enroll_url,
        request_params
    )

    # Throw an exception if we get anything other than HTTP 200 back
    # from the API (the only other status we might be getting back
    # from the bulk enrollment API is HTTP 400).
    response.raise_for_status()

    # If all is well, log the response at the debug level.
    logging.debug("Received response from %s: %s " % (bulk_enroll_url,
                                                      response.json()))
