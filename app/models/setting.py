from app.models import db
from sqlalchemy.ext.hybrid import hybrid_property


class Environment:

    def __init__(self):
        pass

    DEVELOPMENT = 'development'
    STAGING = 'staging'
    PRODUCTION = 'production'
    TESTING = 'testing'


class Setting(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True)

    #
    # General
    #

    app_environment = db.Column(db.String, default=Environment.PRODUCTION)
    # Name of the application. (Eg. Event Yay!, Open Event)
    app_name = db.Column(db.String)
    # Tagline for the application. (Eg. Event Management and Ticketing, Home)
    tagline = db.Column(db.String)
    # App secret
    secret = db.Column(db.String)
    # Static domain
    static_domain = db.Column(db.String)
    # Order Expiry Time in Minutes
    order_expiry_time = db.Column(db.Integer, default=15, nullable=False)

    # Maximum number of complex custom fields allowed for a given form
    max_complex_custom_fields = db.Column(db.Integer, default=30, nullable=False)

    #
    #  STORAGE
    #

    # storage place, local, s3, .. can be more in future
    storage_place = db.Column(db.String)
    # S3
    aws_key = db.Column(db.String)
    aws_secret = db.Column(db.String)
    aws_bucket_name = db.Column(db.String)
    aws_region = db.Column(db.String)
    # Google Storage
    gs_key = db.Column(db.String)
    gs_secret = db.Column(db.String)
    gs_bucket_name = db.Column(db.String)

    #
    # CAPTCHA
    #

    # Google reCAPTCHA
    is_google_recaptcha_enabled = db.Column(db.Boolean, default=False, nullable=False)
    google_recaptcha_site = db.Column(db.String)
    google_recaptcha_secret = db.Column(db.String)

    #
    # Social Login
    #

    # Google Auth
    google_client_id = db.Column(db.String)
    google_client_secret = db.Column(db.String)
    # FB
    fb_client_id = db.Column(db.String)
    fb_client_secret = db.Column(db.String)
    # Twitter
    tw_consumer_key = db.Column(db.String)
    tw_consumer_secret = db.Column(db.String)
    # Instagram
    in_client_id = db.Column(db.String)
    in_client_secret = db.Column(db.String)

    #
    # Payment Gateway
    #

    # Stripe Keys
    stripe_client_id = db.Column(db.String)
    stripe_secret_key = db.Column(db.String)
    stripe_publishable_key = db.Column(db.String)
    stripe_test_client_id = db.Column(db.String)
    stripe_test_secret_key = db.Column(db.String)
    stripe_test_publishable_key = db.Column(db.String)

    # AliPay Keys - Stripe Sources
    alipay_secret_key = db.Column(db.String)
    alipay_publishable_key = db.Column(db.String)

    # Paypal credentials
    paypal_mode = db.Column(db.String)
    paypal_client = db.Column(db.String)
    paypal_secret = db.Column(db.String)
    paypal_sandbox_client = db.Column(db.String)
    paypal_sandbox_secret = db.Column(db.String)

    # Omise credentials
    omise_mode = db.Column(db.String)
    omise_live_public = db.Column(db.String)
    omise_live_secret = db.Column(db.String)
    omise_test_public = db.Column(db.String)
    omise_test_secret = db.Column(db.String)

    # payTM credentials
    is_paytm_activated = db.Column(db.Boolean, default=False, nullable=False)
    paytm_mode = db.Column(db.String)
    paytm_live_merchant = db.Column(db.String)
    paytm_live_secret = db.Column(db.String)
    paytm_sandbox_merchant = db.Column(db.String)
    paytm_sandbox_secret = db.Column(db.String)

    #
    # EMAIL
    #

    # Email service. (sendgrid,smtp)
    email_service = db.Column(db.String)
    email_from = db.Column(db.String)
    email_from_name = db.Column(db.String)
    # Sendgrid
    sendgrid_key = db.Column(db.String)
    # SMTP
    smtp_host = db.Column(db.String)
    smtp_username = db.Column(db.String)
    smtp_password = db.Column(db.String)
    smtp_port = db.Column(db.Integer)
    smtp_encryption = db.Column(db.String)  # Can be tls, ssl, none
    # Google Analytics
    analytics_key = db.Column(db.String)

    #
    # Social links
    #
    google_url = db.Column(db.String)
    github_url = db.Column(db.String)
    twitter_url = db.Column(db.String)
    support_url = db.Column(db.String)
    facebook_url = db.Column(db.String)
    youtube_url = db.Column(db.String)

    #
    # Event Invoices settings
    #
    invoice_sending_day = db.Column(db.Integer, nullable=False, default=1)
    invoice_sending_timezone = db.Column(db.String, nullable=False, default="UTC")
    #
    # Admin Invoice Details
    #
    admin_billing_contact_name = db.Column(db.String)
    admin_billing_phone = db.Column(db.String)
    admin_billing_email = db.Column(db.String)
    admin_billing_country = db.Column(db.String)
    admin_billing_state = db.Column(db.String)
    admin_billing_tax_info = db.Column(db.String)
    admin_company = db.Column(db.String)
    admin_billing_address = db.Column(db.String)
    admin_billing_city = db.Column(db.String)
    admin_billing_zip = db.Column(db.String)
    admin_billing_additional_info = db.Column(db.String)
    #
    # Generators
    #
    android_app_url = db.Column(db.String)
    web_app_url = db.Column(db.String)

    frontend_url = db.Column(db.String, default="http://eventyay.com")

    #
    # Cookie Policy
    #
    cookie_policy = db.Column(db.String,
                              default="This website, and certain approved third parties, use functional, "
                                      "analytical and tracking cookies (or similar technologies) to understand your "
                                      "event preferences and provide you with a customized experience. "
                                      "By closing this banner or by continuing to use the site, you agree. "
                                      "For more information please review our cookie policy.")
    cookie_policy_link = db.Column(db.String, default="https://next.eventyay.com/cookie-policy")

    def __init__(self,
                 app_environment=Environment.PRODUCTION,
                 aws_key=None,
                 aws_secret=None,
                 aws_bucket_name=None,
                 aws_region=None,
                 gs_key=None,
                 gs_secret=None,
                 gs_bucket_name=None,
                 is_google_recaptcha_enabled=False, google_recaptcha_secret=None, google_recaptcha_site=None,
                 google_client_id=None, google_client_secret=None,
                 fb_client_id=None, fb_client_secret=None, tw_consumer_key=None,
                 stripe_client_id=None, stripe_test_client_id=None,
                 stripe_secret_key=None, stripe_publishable_key=None,
                 stripe_test_secret_key=None, stripe_test_publishable_key=None,
                 in_client_id=None, in_client_secret=None,
                 tw_consumer_secret=None, sendgrid_key=None,
                 secret=None, storage_place=None,
                 app_name=None,
                 static_domain=None,
                 tagline=None,
                 google_url=None, github_url=None,
                 twitter_url=None, support_url=None,
                 analytics_key=None,
                 paypal_mode=None,
                 paypal_client=None,
                 paypal_secret=None,
                 paypal_sandbox_client=None,
                 paypal_sandbox_secret=None,
                 email_service=None,
                 email_from=None,
                 email_from_name=None,
                 smtp_host=None,
                 smtp_username=None,
                 smtp_password=None,
                 smtp_port=None,
                 smtp_encryption=None,
                 frontend_url=None,
                 facebook_url=None,
                 youtube_url=None,
                 android_app_url=None,
                 web_app_url=None,
                 cookie_policy=None,
                 cookie_policy_link=None,
                 omise_mode=None,
                 omise_test_public=None,
                 omise_test_secret=None,
                 omise_live_public=None,
                 omise_live_secret=None,
                 alipay_publishable_key=None,
                 alipay_secret_key=None,
                 is_paytm_activated=False,
                 paytm_mode=None,
                 paytm_live_merchant=None,
                 paytm_live_secret=None,
                 paytm_sandbox_merchant=None,
                 paytm_sandbox_secret=None,
                 invoice_sending_day=None,
                 invoice_sending_timezone=None,
                 admin_billing_contact_name=None,
                 admin_billing_phone=None,
                 admin_billing_email=None,
                 admin_billing_country=None,
                 admin_billing_tax_info=None,
                 admin_company=None,
                 admin_billing_address=None,
                 admin_billing_city=None,
                 admin_billing_state=None,
                 admin_billing_zip=None,
                 admin_billing_additional_info=None,
                 order_expiry_time=None,
                 max_complex_custom_fields=30
                 ):
        self.app_environment = app_environment
        self.aws_key = aws_key
        self.aws_secret = aws_secret
        self.aws_bucket_name = aws_bucket_name
        self.aws_region = aws_region

        self.gs_key = gs_key
        self.gs_secret = gs_secret
        self.gs_bucket_name = gs_bucket_name

        self.is_google_recaptcha_enabled = is_google_recaptcha_enabled
        self.google_recaptcha_site = google_recaptcha_site
        self.google_recaptcha_secret = google_recaptcha_secret

        self.google_client_id = google_client_id
        self.google_client_secret = google_client_secret
        self.fb_client_id = fb_client_id
        self.fb_client_secret = fb_client_secret
        self.tw_consumer_key = tw_consumer_key
        self.tw_consumer_secret = tw_consumer_secret
        self.in_client_id = in_client_id
        self.in_client_secret = in_client_secret
        self.sendgrid_key = sendgrid_key
        self.analytics_key = analytics_key
        self.app_name = app_name
        self.static_domain = static_domain
        self.tagline = tagline
        self.secret = secret
        self.storage_place = storage_place
        self.google_url = google_url
        self.github_url = github_url
        self.twitter_url = twitter_url
        self.support_url = support_url
        self.facebook_url = facebook_url
        self.youtube_url = youtube_url
        self.stripe_client_id = stripe_client_id
        self.stripe_publishable_key = stripe_publishable_key
        self.stripe_secret_key = stripe_secret_key
        self.stripe_test_client_id = stripe_test_client_id
        self.stripe_test_publishable_key = stripe_test_publishable_key
        self.stripe_test_secret_key = stripe_test_secret_key
        self.web_app_url = web_app_url
        self.android_app_url = android_app_url
        self.email_service = email_service
        self.smtp_host = smtp_host
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.smtp_port = smtp_port
        self.smtp_encryption = smtp_encryption
        self.email_from = email_from
        self.email_from_name = email_from_name
        self.frontend_url = frontend_url
        self.cookie_policy = cookie_policy
        self.cookie_policy_link = cookie_policy_link

        # Paypal credentials
        self.paypal_mode = paypal_mode
        self.paypal_client = paypal_client
        self.paypal_secret = paypal_secret
        self.paypal_sandbox_client = paypal_sandbox_client
        self.paypal_sandbox_secret = paypal_sandbox_secret

        # Omise Credentials
        self.omise_mode = omise_mode
        self.omise_test_public = omise_test_public
        self.omise_test_secret = omise_test_secret
        self.omise_live_public = omise_live_public
        self.omise_live_secret = omise_live_secret

        # AliPay Credentails
        self.alipay_publishable_key = alipay_publishable_key
        self.alipay_secret_key = alipay_secret_key

        # payTM Credentials
        self.is_paytm_activated = is_paytm_activated
        self.paytm_mode = paytm_mode
        self.paytm_live_merchant = paytm_live_merchant
        self.paytm_live_secret = paytm_live_secret
        self.paytm_sandbox_merchant = paytm_sandbox_merchant
        self.paytm_sandbox_secret = paytm_sandbox_secret

        # Event Invoice settings
        self.invoice_sending_timezone = invoice_sending_timezone
        self.invoice_sending_day = invoice_sending_day

        # Admin Invoice Details
        self.admin_billing_contact_name = admin_billing_contact_name
        self.admin_billing_phone = admin_billing_phone
        self.admin_billing_state = admin_billing_state
        self.admin_billing_country = admin_billing_country
        self.admin_billing_tax_info = admin_billing_tax_info
        self.admin_company = admin_company
        self.admin_billing_address = admin_billing_address
        self.admin_billing_city = admin_billing_city
        self.admin_billing_zip = admin_billing_zip
        self.admin_billing_additional_info = admin_billing_additional_info

        # Order Expiry Time in Minutes
        self.order_expiry_time = order_expiry_time

        self.max_complex_custom_fields = max_complex_custom_fields

    @hybrid_property
    def is_paypal_activated(self):
        if self.paypal_mode == 'sandbox' and self.paypal_sandbox_client and self.paypal_sandbox_secret:
            return True
        elif self.paypal_client and self.paypal_secret:
            return True
        else:
            return False

    @hybrid_property
    def is_stripe_activated(self):
        return self.stripe_client_id is not None

    def __repr__(self):
        return 'Settings'

    def __str__(self):
        return self.__repr__()

    @hybrid_property
    def is_alipay_activated(self):
        if self.alipay_publishable_key and self.alipay_secret_key:
            return True
        else:
            return False

    @hybrid_property
    def is_omise_activated(self):
        if self.omise_mode == 'test' and self.omise_test_public and self.omise_test_secret:
            return True
        elif self.omise_live_public and self.omise_live_secret:
            return True
        else:
            return False
