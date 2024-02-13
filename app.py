from requests.auth import HTTPBasicAuth
import requests
import os
import json

from flask import Flask, jsonify, render_template, request
import gspread

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

def recordAttempt(response):
    computer_sheet_name = "Cash Bash (Website)"
    sa = gspread.service_account(filename="service_account.json")
    computer_sheet = sa.open(computer_sheet_name)

    worksheet = computer_sheet.worksheet("2024 Paypal Log")

    now = datetime.now()
    dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
    name = response.get("purchase_units")[0].get("shipping").get("name").get("full_name")
    cashBashTickets = response.get("ticket_numbers")
    numChances = int(response.get("num_chances_next_year"))
    phoneNumber = str(response.get("phone_number"))

    address_line_1 = response.get("purchase_units")[0].get("shipping").get("address").get("address_line_1")
    admin_area_2   = response.get("purchase_units")[0].get("shipping").get("address").get("admin_area_2")
    admin_area_1   = response.get("purchase_units")[0].get("shipping").get("address").get("admin_area_1")
    postal_code    = response.get("purchase_units")[0].get("shipping").get("address").get("postal_code")
    country_code   = response.get("purchase_units")[0].get("shipping").get("address").get("country_code")

    body=[dt_string, name, cashBashTickets, str(numChances), str(phoneNumber), address_line_1, admin_area_2, admin_area_1, postal_code, country_code, str(response)]
    worksheet.append_row(body, table_range="A1:K1")
    
    # obj = json.loads(response)
    # print(obj)
    # body=[dt_string, name, str(response)]
    # worksheet.append_row(body, table_range="A1:C1")

app = Flask(__name__)

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
        tickets.save()

def getTicketBlocks():

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
                    All numbers will be drawn on September 21st, 2024 at the Mt. Sinai
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
                      9/1/2024 can be picked up at the gate with photo ID.</strong
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
                  Enter for a chance to win an additional free ticket for five more dollars.
                    </strong
                  >
                </p>
              </div>
              <div class="col-xs-1" align="center">


                <!-- start button for a ticket -->
                <button
                    type="button"
                    class="btn btn-secondary btn-custom"
                          data-bs-dismiss="modal"
                          aria-label="Close"

                          onclick="AddCashBashTicket('{ticket_number}')"
                    >Add Cash Bash Ticket #{ticket_number} to Cart
                </button>
                <form name="MyForm{ticket_number}" action="cart" method="post">
                   <input type="hidden" name="cmd" value="_s-xclick" />
                   <input type="hidden" name="ticket_number" value="{ticket_number}" />
                   <table>
                      <tr>
                         <td><input type="hidden" name="on0" value="{ticket_number}" /> </td>
                      </tr>
                   </table>
                   <input type="hidden" name="currency_code" value="USD" />


                   <input class="btn btn-primary btn-custom" type="submit" value="Add Cash Bash Ticket #{ticket_number} and Pay" />
                   <img alt="" border="0" src="https://www.paypalobjects.com/en_US/i/scr/pixel.gif" width="1" height="1">
                </form>
                <div></div>
                <form name="MyForm{ticket_number}_cart" action="cart" method="post">
                   <input type="hidden" name="cmd" value="_s-xclick" />
                   <input type="hidden" name="ticket_number" value="0" />
                   <table>
                      <tr>
                         <td><input type="hidden" name="on0" value="0" /> </td>
                      </tr>
                   </table>
                   <input type="hidden" name="currency_code" value="USD" />


                   <input class="btn btn-default btn-custom" type="submit" value="View Cart" />
                   <img alt="" border="0" src="https://www.paypalobjects.com/en_US/i/scr/pixel.gif" width="1" height="1">
                </form>

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

@app.route("/")
def index():
    return render_template("index.html", ticket_len = len(getTicketBlocks()), tickets = getTicketBlocks(), modal_len = len(getModalBlocks()), modals = getModalBlocks())

@app.route('/payment', methods=['POST'])
def payment():
    data = request.form

    phone_number = data["phone_number"]
    currency = "USD"

    return render_template("payment.html", paypal_business_client_id=PAYPAL_BUSINESS_CLIENT_ID, currency = currency, phone_number = phone_number)

@app.route('/cart', methods=['POST', 'GET'])
def cart():
  ticket_number = 0
  if request.method == 'POST':
    data = request.form
    ticket_number = data["ticket_number"]

  return render_template("cart.html", ticket_number = ticket_number)

@app.route("/payment/<order_id>/capture", methods=["POST"])
def capture_payment(order_id):  # Checks and confirms payment
    data = request.data

    captured_payment = paypal_capture_function(order_id)

    if is_approved_payment(captured_payment):
        my_json = data.decode('utf8').replace("'", '"')
        json_data = json.loads(my_json)
        ticket_numbers = json.loads(json_data["ticket_numbers"])

        numNextYearTickets = json.loads(json_data["numNextYearTickets"])
        phoneNumber = json.loads(json_data["phoneNumber"])

        captured_tickets = ""
        for ticket_number in ticket_numbers:
          captured_tickets += str(ticket_number) + " "
          setTicketSold(int(ticket_number))

        captured_payment["ticket_numbers"] = captured_tickets
        captured_payment["num_chances_next_year"] = numNextYearTickets[0][0]
        captured_payment["phone_number"] = phoneNumber
        captured_payment["payment_approved"] = True
    else:
        captured_payment["payment_approved"] = False

    recordAttempt(captured_payment)
    return jsonify(captured_payment)

@app.route("/payment/validate", methods=["POST"])
def validate_tickets():
    validationError = False
    message = "The ticket is sold. Ticket #(s) "

    data = request.data

    my_json = data.decode('utf8').replace("'", '"')
    json_data = json.loads(my_json)
    ticket_numbers = json.loads(json_data["ticket_numbers"])

    invalidTickets = []
    for ticket_number in ticket_numbers:
      if not isTicketAvailable(int(ticket_number)):
          validationError = True
          invalidTickets.append(int(ticket_number))

    result = {"validationError":validationError, "message":message + json.dumps(invalidTickets)}

    return jsonify(result)

@app.route("/payment/calculateTotal", methods=["POST"])
def calculate_total():
    total = 0.0

    data = request.data

    my_json = data.decode('utf8').replace("'", '"')
    json_data = json.loads(my_json)
    ticket_numbers = json.loads(json_data["ticket_numbers"])
    numNextYearTicketsAry = json.loads(json_data["numNextYearTickets"])
    phoneNumber = json_data["phoneNumber"]

    numNextYearTickets = float(numNextYearTicketsAry[0][0])

    for t in ticket_numbers:
        total += 100.0
    total += (numNextYearTickets * 5.0)

    result = {"total":str(total), "phoneNumber":phoneNumber, "ticket_numbers":json.dumps(ticket_numbers), "numNextYearTickets":numNextYearTickets}

    return jsonify(result)

@app.route("/payment/<ticket_number>/validate", methods=["POST"])
def validate_ticket(ticket_number):
    validationError = False
    message = "The ticket is sold. Ticket #"


    if not isTicketAvailable(int(ticket_number)):
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
    currency_code = captured_payment.get("purchase_units")[0].get("payments").get("captures")[0].get("amount").get( "currency_code")
    print(f"Payment happened. Details: {status}, {amount}, {currency_code}")
    if status == "COMPLETED":
        return True
    else:
        return False

if __name__ == "__main__":
    app.run(port=4242)

