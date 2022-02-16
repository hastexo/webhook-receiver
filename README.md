# Open edX Webhook Receiver

This is a small Django app that listens for incoming webhooks, and
then translates those into calls against the Open edX REST APIs.

It currently provides the following endpoints:

* `webhooks/shopify/order/create` accepts a POST request with JSON
  data, as it would be received by a [Shopify
  webhook](https://help.shopify.com/en/manual/orders/notifications/webhooks)
  firing.

* `webhooks/woocommerce/order/create` accepts a POST request with JSON
  data, as it would be received by a [WooCommerce
  webhook](https://docs.woocommerce.com/document/webhooks/) firing.

* `webhooks/woocommerce/order/update` behaves identically as
  `webhooks/woocommerce/order/create`, for reasons outlined below.

When the webhook is configured properly on the sender side (see
"Webhook Sender Configuration Requirements", below), students will be
enrolled in the appropriate courses as soon as an order is
created. This requires that your Open edX installation runs with the
Bulk Enrollment View enabled.

These webhooks are intended for organizations that already use Shopify
or WooCommerce as their selling platform, and thus have no need or
intention to deploy [Open edX
E-Commerce](https://edx.readthedocs.io/projects/edx-installing-configuring-and-running/en/latest/ecommerce/).


## Open edX Configuration Requirements

### Bulk Enrollment View

* You must enable the Bulk Enrollment view. This view is disabled in a
  default Open edX configuration. To enable it, add
  `ENABLE_BULK_ENROLLMENT_VIEW: true` to your `lms.yml` configuration
  file, and restart the `lms` service via `supervisord`.

* The Bulk Enrollment view also requires that you set
  `ENABLE_COMBINED_LOGIN_REGISTRATION: true`. Combined login
  registration is enabled by default in Open edX, but you may want to
  double-check that your installation follows the default.

Once the bulk enrollment view is enabled, you can try accessing it via
`https://your.openedx.domain/api/bulk_enroll/v1/bulk_enroll`. If the
view is properly enabled, Open edX will respond with an HTTP status
code of 401 (Unauthorized) rather than 404 (Not Found).

### edX OAuth2 Client

Next, you need to create an OAuth2 client so that the webhook
service can communicate with Open edX.

1. In the Django admin interface
   (`https://your.openedx.domain/admin/`), open **Django OAuth
   Toolkit** → **Applications.**

2. Select **Add application**.

3. Leave **Client id** unchanged.

4. Select a **User** that has global _Staff_ permissions.

5. Leave **Redirect uris** blank.

6. For **Client type,** select **Confidential**.

7. For **Authorization grant type**, select **Client credentials**.

8. Leave **Client secret** unchanged.

9. For **Name**, enter `Webhook receiver`, or any other client
   name you find appropriate.

10. Leave **Skip authorization** unchecked.

11. Select **Save**.


## Deployment

The easiest way for platform administrators to deploy the edX Webhooks
app and its dependencies to an Open edX installation is to deploy a
minimal server that exposes the desired endpoint(s), using the
`edx-configuration` Ansible playbooks. A [fork of
`edx-configuration`](https://github.com/hastexo/edx-configuration/tree/hastexo/juniper/webhook-receiver)
exists that defines [a `webhook_receiver`
role](https://github.com/hastexo/edx-configuration/tree/hastexo/juniper/webhook-receiver/playbooks/roles/webhook_receiver)
which you can add to your playbook.


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

An additional quirk that is specific to WooCommerce is that it will
[not call a
webhook](https://github.com/woocommerce/woocommerce/issues/9350) that
listens on any port other than 80, 443, or 8080. This means that you
will not be able to run a separate webhook receiver service on the
same IP address as your Open edX LMS, on a nonstandard port. To
address this, you have two options:

1. Run the webhook receiver service on a dedicated IP address. This
   will also require a separate DNS entry, and either a dedicated
   TLS/SSL certificate, or the use of a wildcard certificate that you
   share with the Open edX LMS.
2. Mount the webhook receiver under your LMS URL, using an nginx
   `proxy_pass` directive. This enables you to receive webhooks on
   `https://your.lms.domain/webhooks`, and they will be redirected to
   the webhook receiver service. The Ansible `webhook_receiver` role
   automates this; set
   `WEBHOOK_RECEIVER_ENABLE_NGINX_INCLUDE` variable to `true` to
   enable this functionality.

If your WooCommerce is set up such that payment for course enrollments
is always via a credit card or voucher, you may want to activate
course enrollments only on payment. To do so, configure your
WooCommerce webhook to fire on the `order.updated` (not
`order.created`) event, and set the `require_payment` configuration
option to `true`.


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
   signature), we return HTTP 403 (Forbidden). If we consider the
   payload valid but it does not include payment information (and
   we’ve been configured to look for it), we return HTTP 402 (Payment
   Required).

3. If we’re able to verify the incoming payload, we return HTTP 200
   (OK), create an asynchronous processing task for Celery, and this
   concludes synchronous request processing.

4. The asynchronous Celery task then makes REST API calls against the
   Open edX instance, invoking the Bulk Enrollment view to enroll
   learners in courses. If any REST API call results in an error,
   Celery will retry up to three times (using the standard retry delay
   of 3 minutes, unless you’re overriding this in your Celery
   configuration).


## I can’t use course IDs as SKUs. What do I do?

Sometimes, configuring products with SKUs that match Open edX course
IDs is not an option, or undesirable. For example, your Open edX
platform may have several consecutive course runs that from a
commercial perspective are all one and the same product. Or your
selling platform might mandate a particular format for SKUs.

In this case, you can use the [Django `redirects`
app](https://docs.djangoproject.com/en/2.2/ref/contrib/redirects/) to
help the webhook receiver find the correct course ID. For example, you
might define https://my.lms.domain/sku/xyz123 to redirect to
https://my.lms.domain/courses/course-v1:org+course+run/.

What the webhook receiver will then do, if it detects a SKU that does
not start with `course-v1:`, is send an HTTP `HEAD` request (with
redirects enabled), to https://my.lms.domain/$prefix$sku (where
`$prefix` is configurable, via `settings.WEBHOOK_RECEIVER_SKU_PREFIX`),
and extract the course ID from the location it is being redirected to.

The `redirects` app is enabled on a typical edX platform
configuration, so it comes in handy for this purpose. However, in
principle you do not _need_ to use it for looking up a course ID from
a SKU. You could also write the redirect (or even a proxy rule) into
your nginx configuration, or handle it at the load balancer level if
your platform uses one.

## License

This app is licensed under the Affero GPL; see [`LICENSE`](LICENSE) for
details.
