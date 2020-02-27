[![PyPI version](https://img.shields.io/pypi/v/edx-webhooks.svg)](https://pypi.python.org/pypi/edx-shopify)
[![Build Status](https://travis-ci.org/hastexo/edx-webhooks.svg?branch=master)](https://travis-ci.org/hastexo/edx-shopify)
[![codecov](https://codecov.io/gh/hastexo/edx-webhooks/branch/master/graph/badge.svg)](https://codecov.io/gh/hastexo/edx-shopify)



# edX Webhooks

This is a Django app that listens for incoming webhooks, and then
translates those into REST API calls against the Open edX Bulk
Enrollment API.

It currently provides the following endpoints:

* `webhooks/shopify/order/create` accepts a POST request with JSON
  data, as it would be received by a Shopify webhook firing.  When the
  webhook is configured properly on Shopify (see "Shopify
  configuration" below), students will be enrolled on the appropriate
  courses as soon as an order is created. This is intended as a
  replacement of [Open edX
  E-Commerce](https://edx.readthedocs.io/projects/edx-installing-configuring-and-running/en/latest/ecommerce/),
  for organizations that already use Shopify as a selling platform.

## Open edX Configuration Requirements

### Bulk Enrollment View

* You must enable the Bulk Enrollment view. This view is disabled in a
  default Open edX configuration. To enable it, add
  `ENABLE_BULK_ENROLLMENT_VIEW: true` to your `lms.env.json`, and
  restart `edxapp`.

* The Bulk Enrollment view also requires that you set
  `ENABLE_COMBINED_LOGIN_REGISTRATION: true`. Combined login
  registration is enabled by default in Open edX, but you may want to
  double-check that your installation follows the default.

Once the bulk enrollment view is enabled, you can try accessing it via
`https://your.openedx.domain/api/bulk_enroll/v1/bulk_enroll/`. If the
view is properly enabled, Open edX will respond with an HTTP status
code of 401 (unauthorized) rather than 404 (not found).

### edX OAuth2 Client

Next, you need to create an OAuth2 client so that the webhook
service can communicate with Open edX.

1. Open `https://your.openedx.domain/admin/oauth2_provider/application`.

2. Select **Add application**.

3. Leave the **User** field blank.

4. For **Client Name**, enter `Webhook receiver`, or any other client
   name you find appropriate.

5. For **URL,** enter the URL that your Webhook receiver runs at, such
   as `https://webhooks.openedx.domain`.

6. For **Redirect URL**, enter
   `https://webhooks.openedx.domain/complete/edx-oauth2`. This is the OAuth
   client endpoint.

   The system automatically generates values in the **Client ID** and
   **Client Secret** fields.

7. For **Client Type,** select **Authorization code.**

8. Enable **Skip Authorization.**

9. Select **Save.**


## Deployment

The easiest way for platform administrators to deploy the edX Shopify app and
its dependencies to an Open edX installation is to deploy a minimal
server that exposes the desired endpoint(s).

To deploy `edx-webhooks` as part of your Django application:

1. Install it via pip (into a virtualenv, most probably):

    ```
    $ pip app install edx-webhooks
    ```

2. Add it to the `INSTALLED_APPS` list in `settings.py`, and also add
   a `WEBHOOK_SETTINGS` dictionary, like so:

    ```python
    INSTALLED_APPS = [
	    'social_django',
        'edx_shopify',
    ],
	AUTHENTICATION_BACKENDS = (
        'auth_backends.backends.EdXOAuth2',
        'django.contrib.auth.backends.ModelBackend',
	)
	SOCIAL_AUTH_STRATEGY = 'auth_backends.strategies.EdxDjangoStrategy'
    WEBHOOK_SETTINGS = [
        "edx_shopify": {
            "api_key": "YOUR_SHOPIFY_API_KEY",
            "shop_domain": "YOUR.SHOPIFY.DOMAIN",
        }
    ],
    ```


## Shopify configuration

For the Shopify webhook to work, you'll need to customize your Shopify
theme to [collect customized product
information](https://help.shopify.com/themes/customization/products/get-customization-information-for-products).
Specifically, you'll need to add an `email` field to the order
properties, so that the Shopify user can specify what email will be
enrolled on the course run.  You must validate that field with
JavaScript, so that it is always filled with a valid email address.

Furthermore, you need to make sure that your product SKU is a valid edX course
ID in your LMS, such as `course-v1:hastexo+hx212+201704`.


## License

This app is licensed under the Affero GPL; see [`LICENSE`](LICENSE) for
details.
