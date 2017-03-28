[![PyPI version](https://img.shields.io/pypi/v/edx-shopify.svg)](https://pypi.python.org/pypi/edx-shopify)
[![Build Status](https://travis-ci.org/hastexo/edx-shopify.svg?branch=master)](https://travis-ci.org/hastexo/edx-shopify)
[![codecov](https://codecov.io/gh/hastexo/edx-shopify/branch/master/graph/badge.svg)](https://codecov.io/gh/hastexo/edx-shopify)



# edX Shopify

This is a Django app intended for use in Open edX, as a means of integrating it
with Shopify.

This app provides an LMS endpoint at `webhooks/shopify/order/create` that
accepts a POST request with JSON data.  When the webhook is configured properly
on Shopify (see "Shopify configuration" below), students will be enrolled on
the appropriate courses as soon as an order is created, using the same logic
as batch student enrollment via the Instructor Dashboard.

For the moment, this requires a patched version of edX.  Please refer to the
[hastexo/master/webhooks](https://github.com/hastexo/edx-platform/tree/hastexo/master/webhooks)
fork of `edx-platform`, and the similarly named
[hasteox/master/webhooks](https://github.com/hastexo/edx-configuration/tree/hastexo/master/webhooks)
fork of `edx-configuration`.


## Deployment

The easiest way for platform administrators to deploy the edX Shopify app and
its dependencies to an Open edX installation is to pip install it to the edxapp
virtualenv.

To deploy `edx-shopify`:

1. Install it via pip:

    ```
    $ sudo /edx/bin/pip.edxapp install edx-shopify
    ```

2. Add it to the `ADDL_INSTALLED_APPS`, `WEBHOOK_APPS`, and `WEBHOOK_SETTINGS`
   of your LMS environment, by editing `/edx/app/edxapp/lms.env.json`:

    ```
    "ADDL_INSTALLED_APPS": [
        "edx_shopify"
    ],
    "WEBHOOK_APPS": [
        "edx_shopify"
    ],
    "WEBHOOK_SETTINGS": [
        "edx_shopify": {
            "api_key": "YOUR_SHOPIFY_API_KEY",
            "shop_domain": "YOUR.SHOPIFY.DOMAIN"
        }
    ],
    ```

3. Migrate the `edxapp` database by running:

    ```
    $ sudo /edx/bin/python.edxapp /edx/app/edxapp/edx-platform/manage.py lms --settings=aws migrate
    ```

4. Finally, restart edxapp and its workers:

    ```
    sudo /edx/bin/supervisorctl restart edxapp:
    sudo /edx/bin/supervisorctl restart edxapp_worker:
    ```


## Shopify configuration

For this webhook to work, you'll need to customize your Shopify theme to
[collect customized product
information](https://help.shopify.com/themes/customization/products/get-customization-information-for-products).
Specifically, you'll need to add an `email` field to the order properties, so
that the Shopify user can specify what email will be enrolled on the course
run.  You must validate that field with Javascript so that it is
always filled with a valid email address.

Furthermore, you need to make sure that your product SKU is a valid edX course
ID in your LMS, such as `course-v1:hastexo+hx212+201704`.


## License

This app is licensed under the Affero GPL; see [`LICENSE`](LICENSE) for
details.
