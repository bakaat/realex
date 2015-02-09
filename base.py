# python
from datetime import datetime
import hashlib
import uuid

# libs

# local


class SHA1CheckError(Exception):
    """Risen on SHA1hashes mismatch """

    def __str__(self):
        return "SHA1 for response does not match %s" % self.args[0]


class PostDictKeyError(Exception):
    """Risen when required key is missing from post data"""

    def __str__(self):
        return "PostDictKeyError: %s must be present in POST_DATA" % \
            self.args[0]


class RealexFormBase(object):
    """Should be overwritten with values required by realex api."""

    class Meta:
        merchant_id = ""
        account = ""
        secret = ""
        endpoint_url = "https://hpp.sandbox.realexpayments.com/pay"
        response_url = None

    def __init__(self, currency=None, amount=None, data=None, form_attr=None,
                 fields_attr=None, order_id=None, **kw):
        """Creates an instance of form with data for payment request.
        - currency and amount are requires parameters if you want to create the
          form and attach it in the html.
        - data is required if you want to do a validation of realex response


        :param str currency: One of currencies supported by realex. For
                             full list see
        :param amount: Exact amount to be billed to the user
        :type amount: string, float, decimal, int
        :param dict data: POST data for validation (returned by from Realex)
        :param dict form_attr: Extra attributes to be attached to the form,
                               example:
                                   form_attr = {"class": "fancy_form graybg"}
        :param dict fields_attr: Extra attributes to be attached to fields,
                                 example:
                                    fields = {
                                        "merchant_id": {
                                            "class": "nice_merchant id",
                                            "id": "merchantid"}
                                        "currency": {
                                            "class": "currency_sign",
                                            "style": "color:red;"}
                                        }
        :param str order_id: Optional order id to be used for the payment,
                             if not specified, will be generated using
                             following format:
                                order_id = "<current datetime>-<last four
                                            characters of uuid4 hex>"
        :param kw: Any other values that should be sent with the request to
                   Realex
        """
        assert all([self.Meta.merchant_id, self.Meta.account,
                    self.Meta.secret])
        if data:
            self.data = data
            return

        self.form_attr = form_attr
        self.fields_attr = fields_attr

        # setting values required by Realex
        assert all([currency, amount])
        self.fields = dict()
        self.fields['currency'] = currency
        self.fields['amount'] = '%i' % (int(amount) * 100)
        self.fields['timestamp'] = datetime.now().strftime("%Y%m%d%H%M%S")
        uid = uuid.uuid4().hex[-4:]
        self.fields['order_id'] = order_id or \
            "%s-%s" % (self.fields['timestamp'], uid)
        # hash fields
        self.sha1hash = hashlib.sha1(".".join([self.fields['timestamp'],
                                               self.Meta.merchant_id,
                                               self.fields['order_id'],
                                               self.fields['timestamp'],
                                               self.fields['currency']]))
        # sign fields hash with secret and create new hash
        self.fields['sha1hash'] = hashlib.sha1(".".join([
            self.sha1hash.hexdigest(), self.Meta.secret])).hexdigest()
        self.fields['auto_settle_flag'] = 1

        # setting additional values that will be returned to you
        for k, v in kw.items():
            if k not in self.fields:
                self.fields[k] = v

    def as_form(self):
        """Renders the form along with all of it's values."""
        form_attr = self.form_attr or dict()
        form_init = {"action": self.Meta.endpoint_url, "method": "POST"}
        form_attr.update(form_init)
        form_str = "<form %s >\n" % (" ".join(["%s='%s'" % (k, v)
                                               for k, v in form_attr.items()]))
        form_str = "%s %s \n" \
                   "<input type='submit' value='Proceed to secure server'/>" \
                   "</form>" % (form_str, self.as_fields())
        return form_str

    def as_fields(self):
        """Renders only the fields without the enclosing form tag."""
        fields_str = ""
        fields = self.fields_attr or dict()
        all_fields = {
            'merchant_id': self.Meta.merchant_id,
            'account': self.Meta.account
        }
        if self.Meta.response_url:
            all_fields['response_url'] = self.Meta.response_url
        all_fields.update(self.fields)
        for k, v in all_fields.items():
            field_init = {"name": k.upper(), "value": v, "type": "hidden"}
            field_data = fields.get(k, {})
            field_data.update(field_init)
            fields_str = "%s<input " % fields_str
            prepare_extras = " ".join(["%s='%s'" % (x, z)
                                       for x, z in field_data.items()])
            fields_str = "%s %s />\n" % (fields_str, prepare_extras)
        return fields_str

    def is_valid(self):
        """Validates the response from realex. Raises an exception if
        validation fails. If validation is successful it will set the
        cleaned_data attr on self.

        :raises SHA1CheckError: in case if sha1 generated for the response
                                doesn't match the sha1 returned by realex
        :raises PostDictKeyError: for any missing key that is required in the
                                  post response from realex
        """
        required_in_post = ["TIMESTAMP", "MERCHANT_ID", "ORDER_ID", "RESULT",
                            "MESSAGE", "PASREF", "AUTHCODE", "SHA1HASH"]

        for item in required_in_post:
            if item not in self.data.keys():
                raise PostDictKeyError(item)

        required_in_post.remove("SHA1HASH")

        sha1hash = hashlib.sha1(".".join([self.data[x]
                                          for x in required_in_post]))
        sha1hash = hashlib.sha1("%s.%s" % (sha1hash.hexdigest(),
                                           self.Meta.secret))

        if sha1hash.hexdigest() != self.data["SHA1HASH"]:
            raise SHA1CheckError("%s != %s" % (sha1hash.hexdigest(),
                                               self.data["SHA1HASH"]))

        data = dict((k.lower(), v) for k, v in self.data.items())
        setattr(self, 'cleaned_data', data)

