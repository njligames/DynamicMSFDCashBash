import os

# import stripe
from flask import Flask, jsonify, render_template, request
import gspread

import pycurl
from urllib.parse import urlencode
from io import BytesIO

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

    print("DynamicMSFDCashBash - debug({debug_type}): {debug_msg}".format(debug_type = debug_type, debug_msg = debug_msg))

def validatePaypalPurchase(tx, auth_token):
    pp_hostname = "www.paypal.com"
    url = "https://{pp_hostname}/cgi-bin/webscr"
    host = "Host: {pp_hostname}"

    data = {"cmd":"_notify-synch", "tx":tx, "at":auth_token}
    post_data = "&".join([f"{k}={v}" for k, v in data.items()])
    buffer = BytesIO()

    print("post_data = " + post_data)
    print("url = " + url.format(pp_hostname = pp_hostname))
    print("HTTPHEADER = " + str([host.format(pp_hostname = pp_hostname)]))

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

def loadTicketArrayMap():
    tickets = Tickets()

    ticket_map_array = []
    for i in range(1, 501):
        avail = not tickets.is_sold(i)
        ticket = {'available':avail, 'ticket_number':i}
        print(ticket)
        ticket_map_array.append(ticket)
    return ticket_map_array

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
    return render_template("index.html", len = len(getTicketBlocks()), tickets = getTicketBlocks())

if __name__ == "__main__":
    app.run(port=4242)

