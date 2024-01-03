from requests.auth import HTTPBasicAuth
import requests
import os
import json

# import stripe
from flask import Flask, jsonify, render_template, request
import gspread

import pycurl
from urllib.parse import urlencode
from io import BytesIO

from datetime import datetime

# # # # PAYPAL SANDBOX
PAYPAL_BUSINESS_CLIENT_ID = os.getenv("PAYPAL_SANDBOX_BUSINESS_CLIENT_ID")
PAYPAL_BUSINESS_SECRET = os.getenv("PAYPAL_SANDBOX_BUSINESS_SECRET")
PAYPAL_API_URL = f"https://api-m.sandbox.paypal.com"

# # # # PAYPAL LIVE Details
# PAYPAL_BUSINESS_CLIENT_ID = os.getenv("PAYPAL_LIVE_BUSINESS_CLIENT_ID")
# PAYPAL_BUSINESS_SECRET = os.getenv("PAYPAL_LIVE_BUSINESS_SECRET")
# PAYPAL_API_URL = f"https://api-m.paypal.com"

class Tickets:
    def __init__(self):
        manual_sheet_name = "Cash Bash (Manual)"
        computer_sheet_name = "Cash Bash (Website)"
        sa = gspread.service_account(filename="service_account.json")

        manual_sheet = sa.open(manual_sheet_name)
        computer_sheet = sa.open(computer_sheet_name)

        self._wks = computer_sheet.worksheet("2024")
        self._range = 'A2:B501'
        self._ticket_list = self._wks.get(self._range)

    def save(self):
        self._wks.update(values = self._ticket_list, range_name = self._range)

    def set_sold(self, ticket_number, sold = True):
        if ticket_number >= 1 and ticket_number <= 500:
            self._ticket_list[ticket_number - 1][1] = sold

    def is_sold(self, ticket_number):
        if ticket_number >= 1 and ticket_number <= 500:
            if self._ticket_list[ticket_number - 1][1].upper() == "TRUE":
                return True
        return False

def debug_output(debug_type, debug_msg):
    data = "DynamicMSFDCashBash - debug({debug_type}): {debug_msg}".format(debug_type = debug_type, debug_msg = debug_msg.decode('utf-8'))
    print(data)

def recordAttempt(response):
    computer_sheet_name = "Cash Bash (Website)"
    sa = gspread.service_account(filename="service_account.json")
    computer_sheet = sa.open(computer_sheet_name)

    worksheet = computer_sheet.worksheet("2024 Paypal Log")

    now = datetime.now()
    dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
    body=[dt_string, response]
    worksheet.append_row(body, table_range="A1:B1")

def validatePaypalPurchase(tx, auth_token):


    pp_hostname = "www.paypal.com"
    url = "https://{pp_hostname}/cgi-bin/webscr"
    host = "Host: {pp_hostname}"

    data = {"cmd":"_notify-synch", "tx":tx, "at":auth_token}
    post_data = "&".join([f"{k}={v}" for k, v in data.items()])
    buffer = BytesIO()

    c = pycurl.Curl()
    c.setopt(c.URL, url.format(pp_hostname = pp_hostname))
    c.setopt(pycurl.VERBOSE, 1)
    c.setopt(pycurl.DEBUGFUNCTION, debug_output)
    c.setopt(c.POST, 1)
    # c.setopt(c.RETURNTRANSFER, 1)
    c.setopt(c.POSTFIELDS, post_data)
    c.setopt(c.SSL_VERIFYPEER, 1)
    c.setopt(c.SSL_VERIFYHOST, 2)
    c.setopt(c.HTTPHEADER, [host.format(pp_hostname = pp_hostname)])
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    code = c.getinfo(c.RESPONSE_CODE)
    c.close()

    response = buffer.getvalue()
    recordAttempt(response.decode('utf-8'))
    return (200 == code), {"response":response.decode('utf-8'), "code":code}


    # data = {"cmd":"_notify-synch", "tx":tx, "at":auth_token}
    # response = "&".join([f"{k}={v}" for k, v in data.items()])


app = Flask(__name__)

def generateExampleTicketArrayMap():
    ticket_map_array = []
    for i in range(1, 501):
        avail = True
        if i % 2 == 0:
            avail = False
        ticket = {'available':avail, 'ticket_number':i}
        ticket_map_array.append(ticket)
    return ticket_map_array

def generateExampleModalArrayMap():
    modal_map_array = []
    for i in range(1, 501):
        ticket = {'ticket_number':i}
        modal_map_array.append(ticket)
    return modal_map_array

def loadTicketArrayMap():
    tickets = Tickets()

    ticket_map_array = []
    for i in range(1, 501):
        avail = not tickets.is_sold(i)
        ticket = {'available':avail, 'ticket_number':i}
        print(ticket)
        ticket_map_array.append(ticket)
    return ticket_map_array

def isTicketAvailable(ticket_number):
    if ticket_number >= 1 and ticket_number <= 500:
        tickets = Tickets()
        return not tickets.is_sold(ticket_number)
    return False

def setTicketSold(ticket_number):
    if ticket_number >= 1 and ticket_number <= 500:
        tickets = Tickets()
        tickets.set_sold(ticket_number)

def getTicketBlocks():

    # ticket_map_array = generateExampleTicketArrayMap()
    ticket_map_array = loadTicketArrayMap()

    def getTicketBlock(ticket):
        available="""
        <button
            type="button"
            class="btn btn-primary btn-custom"
            data-bs-toggle="modal"
            data-bs-target="#exampleModal{ticket_number}"
            data-whatever="{ticket_number}"
            >Ticket #{ticket_number}
        </button>
        """

        disabled="""
        <button
            type="button"
            class="btn btn-primary btn-custom"
            data-bs-toggle="modal"
            data-bs-target="#exampleModal{ticket_number}"
            data-whatever="{ticket_number}"
            disabled>Ticket #{ticket_number}
        </button>
        """

        if ticket['available']:
            return available.format(ticket_number = ticket['ticket_number'])
        else:
            return disabled.format(ticket_number = ticket['ticket_number'])

    ticket_array = []

    for ticket in ticket_map_array:
        ticket_array.append(getTicketBlock(ticket))

    return ticket_array


def getModalBlocks():
    modal_map_array = generateExampleModalArrayMap()

    def getModalBlock(ticket_number):
        code_txt = """
        <div
          class="modal fade bd-example-modal-lg"
          id="exampleModal{ticket_number}"
          tabindex="-1"
          role="dialog"
          aria-labelledby="exampleModalLabel"
          aria-hidden="true"
        >
          <div class="modal-dialog modal-lg" role="document">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title" id="exampleModalLabel">Cash Bash Ticket</h5>
                <button
                  type="button"
                  class="close"
                  data-bs-dismiss="modal"
                  aria-label="Close"
                >
                  <span aria-hidden="true">&times;</span>
                </button>
              </div>
              <div class="modal-body" id="exampleModalBody">
                <h1 style="text-align: center"><strong>1st Prize: $10,000</strong></h1>
                <h1 style="text-align: center"><strong>2nd Prize: $2,500</strong></h1>
                <h1 style="text-align: center"><strong>13 Prizes: $500.00</strong></h1>
                <h1 style="text-align: center"><strong>10 Prizes: $100.00</strong></h1>
                <div>&nbsp;</div>
                <ol>
                  <li>$100.00 Per Ticket. Winner need not be present.</li>
                  <li>
                    All numbers will be drawn on September 23rd, 2023 at the Mt. Sinai
                    Fire Department, Station 1, 133 Mount Sinai Avenue.
                  </li>
                  <li>
                    Gates will open at 1 pm and event will run until 5 pm, rain or
                    shine.
                  </li>
                  <li>All winning numbers are re-entered for additional prizes.</li>
                  <li>
                    Only 2 ADULTS per ticket will be allowed entry. Please bring your
                    own lawn chair.
                  </li>
                  <li>
                    Only (up to) 500 tickets will be sold. Tickets must be shown at the
                    gate for entry.
                  </li>
                  <li>No one under 21 will be admited. NO EXCEPTIONS!!!</li>
                  <li>
                    <strong>All tickets will be mailed to the address you put on the
                      application once your payment clears. Tickets purchased after
                      9/1/2023 can be picked up at the gate with photo ID.</strong
                    >
                  </li>
                  <li>
                    You can choose your personal number 1-500. If a ticket number choice
                    is not available, a random number will then be sent to you in its
                    place.
                  </li>
                  <li>
                    For additional questions contact: Cash Bash Committee at:
                    msfdcashbash@gmail.com
                  </li>
                  <li>
                    Entertainment, BBQ and drinks will be available during drawing, all
                    included with ticket purchase.
                  </li>
                  <li>
                    IF LESS THAN 500 TICKETS ARE SOLD, ALL PRIZES WILL BE PRORATED AT 60% OF TOTAL SOLD
                  </li>
                </ol>
                <p>
                  <strong>
                  Enter for a chance to win an additional free ticket for five more dollars, select in drop down.
                    </strong
                  >
                </p>
              </div>
              <div class="col-xs-1" align="center">


                <!-- start button for a ticket -->
                <form name="MyForm" action="payment" onsubmit="return validateForm()" method="post" target="_blank">
                   <input type="hidden" name="cmd" value="_s-xclick" />
                   <input type="hidden" name="ticket_number" value="{ticket_number}" />
                   <table>
                      <tr>
                         <td><input type="hidden" name="on0" value="Cash Bash Ticket #{ticket_number}" />Cash Bash Ticket #{ticket_number}</td>
                      </tr>
                      <tr>
                         <td>
                            <select name="os0">
                               <option value="100">Ticket $100.00 USD</option>
                               <option value="105">Ticket & Chance $105.00 USD</option>
                            </select>
                         </td>
                      </tr>
                      <tr>
                         <td><input type="hidden" name="on1" value="Winner Contact #" />Winner Contact #</td>
                      </tr>
                      <tr>
                         <td><input type="text" name="os1" maxlength="200" required /></td>
                      </tr>
                   </table>
                   <input type="hidden" name="currency_code" value="USD" />
                   <input type="image" src="https://www.paypalobjects.com/en_US/i/btn/btn_cart_LG.gif" border="0" name="submit" alt="PayPal - The safer, easier way to pay online!" />
                   <img alt="" border="0" src="https://www.paypalobjects.com/en_US/i/scr/pixel.gif" width="1" height="1">
                </form>
                <!-- end button for a ticket -->

              </div>
              <div class="modal-footer"></div>
            </div>
          </div>
        </div>

        """

        return code_txt.format(ticket_number = ticket_number)

    modal_array = []

    for modal in modal_map_array:
        modal_array.append(getModalBlock(modal['ticket_number']))

    return modal_array

@app.route("/hello")
def hello_world():
    return jsonify("hello, world!")

@app.route("/success")
def success():

    tx = ""
    if request.method == 'GET':
      tx = request.args.get('tx')
    if None == tx:
        tx = ""

    auth_token = os.getenv('PAYPAL_AUTH_TOKEN')

    valid, details = validatePaypalPurchase(tx.upper(), auth_token)

    if valid:
        return render_template("success.html", userdetails = details)
    return jsonify(details)

@app.route("/")
def index():
    return render_template("index.html", ticket_len = len(getTicketBlocks()), tickets = getTicketBlocks(), modal_len = len(getModalBlocks()), modals = getModalBlocks())

@app.route('/payment', methods=['POST'])
def payment():
    data = request.form

    ticket_number = data["ticket_number"]
    phone_number = data["os1"]
    price = data["os0"]
    currency = "USD"

    return render_template("payment.html", paypal_business_client_id=PAYPAL_BUSINESS_CLIENT_ID, currency = currency, ticket_number = ticket_number, phone_number = phone_number, price = price)

@app.route("/payment/<order_id>/capture", methods=["POST"])
def capture_payment(order_id):  # Checks and confirms payment
    data = request.data

    captured_payment = paypal_capture_function(order_id)

    if is_approved_payment(captured_payment):
        # Do something (for example Update user field)
        my_json = data.decode('utf8').replace("'", '"')
        json_data = json.loads(my_json)
        ticket_number = json_data["ticket_number"]

        setTicketSold(ticket_number)

    return jsonify(captured_payment)

@app.route("/payment/<ticket_number>/validate", methods=["POST"])
def validate_ticket(ticket_number):
    validationError = False
    message = "The ticket is sold. Ticket #"


    if not isTicketAvailable(ticket_number):
        validationError = True
        message += str(ticket_number)

    result = {"validationError":validationError, "message":message}

    return jsonify(result)


def paypal_capture_function(order_id):
    post_route = f"/v2/checkout/orders/{order_id}/capture"
    paypal_capture_url = PAYPAL_API_URL + post_route
    basic_auth = HTTPBasicAuth(PAYPAL_BUSINESS_CLIENT_ID, PAYPAL_BUSINESS_SECRET)
    headers = {
        "Content-Type": "application/json",
    }
    response = requests.post(url=paypal_capture_url, headers=headers, auth=basic_auth)
    response.raise_for_status()
    json_data = response.json()
    return json_data

def is_approved_payment(captured_payment):
    status = captured_payment.get("status")
    amount = captured_payment.get("purchase_units")[0].get("payments").get("captures")[0].get("amount").get("value")
    currency_code = captured_payment.get("purchase_units")[0].get("payments").get("captures")[0].get("amount").get(
        "currency_code")
    print(f"Payment happened. Details: {status}, {amount}, {currency_code}")
    if status == "COMPLETED":
        return True
    else:
        return False

if __name__ == "__main__":
    app.run(port=4242)

