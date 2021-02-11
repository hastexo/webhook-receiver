# edX Webhooks

This is a small Django app that listens for incoming webhooks, and
then translates those into calls against the Open edX REST APIs.

It currently provides the following endpoint:

* `webhooks/shopify/order/create` accepts a POST request with JSON
  data, as it would be received by a [Shopify
  webhook](https://help.shopify.com/en/manual/orders/notifications/webhooks)
  firing.

* `webhooks/woocommerce/order/create` accepts a POST request with JSON
  data, as it would be received by a [WooCommerce
  webhook](https://docs.woocommerce.com/document/webhooks/) firing.

When the webhook is configured properly on sender side (see "Webhook
sender Configuration Requirements", below), students will be enrolled
on the appropriate courses as soon as an order is created. This
requires that your Open edX installation enables the Bulk Enrollment
View.

These webhooks are intended for organizations that already use Shopify
or WooCommerce as their selling platform, and have thus no intention
to deploy [Open edX
E-Commerce](https://edx.readthedocs.io/projects/edx-installing-configuring-and-running/en/latest/ecommerce/).


## Open edX Configuration Requirements

### Bulk Enrollment View

* You must enable the Bulk Enrollment view. This view is disabled in a
  default Open edX configuration. To enable it, add
  `ENABLE_BULK_ENROLLMENT_VIEW: true` to your `lms.yml`, and
  restart the `lms` service via `supervisord`.

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

The easiest way for platform administrators to deploy the edX Webhooks
app and its dependencies to an Open edX installation is to deploy a
minimal server that exposes the desired endpoint(s).

To deploy `edx-webhooks` as part of your Django application:

1. Install it via pip (into a virtualenv, most probably):

    ```
    $ pip install edx-webhooks
    ```

2. Add it to the `INSTALLED_APPS` list in `settings.py`, and also add
   a `WEBHOOK_SETTINGS` dictionary, like so:

    ```python
    INSTALLED_APPS = [
        'edx_webhooks',
        'edx_webhooks_shopify',
        'edx_webhooks_woocommerce',
    ],
    WEBHOOK_SETTINGS = [
        "edx_shopify": {
            "api_key": "YOUR_SHOPIFY_API_KEY",
            "shop_domain": "YOUR.SHOPIFY.DOMAIN",
        }
    ],
    ```

You can also configure your application using environment variables
and/or a dotenv (`.env`) file; an illustrated example of this is in
`example.env`.

## Webhook Sender Configuration Requirements


### Shopify

For the Shopify webhook to work, you'll need to customize your Shopify
theme to [collect customized product
information](https://help.shopify.com/themes/customization/products/get-customization-information-for-products).
Specifically, you'll need to add an `email` field to the order
properties, so that the Shopify user can specify what email will be
enrolled on the course run.  You must validate that field with
JavaScript, so that it is always filled with a valid email address.

Furthermore, you need to make sure that your product SKU is a valid edX course
ID in your LMS, following the `course-v1:<org>+<course>+<run>` format.


### WooCommerce

For WooCommerce, you’ll need a plugin that can provide additional
product input fields, like [Product Input Fields for
WooCommerce](https://wordpress.org/plugins/product-input-fields-for-woocommerce/). The
webhook receiver will process *the value of the first input field of
type `email`*
(regardless of the field’s title) as the email address of the learner
to be enrolled.

Furthermore, as with Shopify you need to make sure that your product
SKU is a valid edX course ID in your LMS, following the
`course-v1:<org>+<course>+<run>` format.


## Technical background

If you’re interested in how webhook processing works in a little more
detail, here’s how:

1. When the webhook sender invokes the webhook, we immediately store
   its payload, headers, and request source in the database. This
   happens synchronously, while receiving the initial request.

2. Also during the initial request, we check the webhook’s signature,
   and some data identifying the source, from both the headers and the
   payload. If we deem any of them malformed, we return HTTP 400
   (Bad Request); if we consider them well-formed but invalid (such
   as, coming from the wrong source or not having a correct
   signature), we return HTTP 403 (Forbidden).

3. If we’re able to verify the incoming payload, we return HTTP 200
   (OK), create an asynchronous processing task for Celery, and this
   concludes synchronous request processing.

4. The asynchronous Celery task then makes REST API calls against the
   Open edX instance, invoking the Bulk Enrollment view to enroll
   learners in courses. If any REST API call results in an error,
   Celery will retry up to three times (using the standard retry delay
   of 3 minutes, unless you’re overriding this in your Celery
   configuration).


## License

This app is licensed under the Affero GPL; see [`LICENSE`](LICENSE) for
details.
