import os
import sys

currpath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(currpath, '../../..'))

from flask import Flask, request
from realex import RealexFormBase
app = Flask(__name__)

MERCHANT_ID = "1234abcd"
ACCOUNT = "asdf1234"
SECRET = "zbcd4321"


class RealexForm(RealexFormBase):

    class Meta:
        merchant_id = MERCHANT_ID
        account = ACCOUNT
        secret = SECRET
        endpoint_url = "https://hpp.sandbox.realexpayments.com/pay"
        response_url = "http://localhost/handle"


@app.route("/", methods=['GET'])
def pay():
    form = RealexForm('EUR', 20)
    return "<html><body>%s</body></html>" % form.as_form()


@app.route("/handle", methods=['POST'])
def handle_payment():
    form = RealexForm(data=request.form)
    return form.is_valid()

if __name__ == "__main__":
    app.run()
