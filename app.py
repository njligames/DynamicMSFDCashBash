import os

# import stripe
from flask import Flask, jsonify, render_template, request
import gspread

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
            return self._ticket_list[ticket_number - 1]
        return False

app = Flask(__name__)

def getTicketArrayMap():
    ticket_map_array = []
    for i in range(1, 501):
        avail = True
        if i % 2 == 0:
            avail = False
        ticket = {'available':avail, 'ticket_number':i}
        ticket_map_array.append(ticket)
    return ticket_map_array

def getTicketBlocks():

    ticket_map_array = getTicketArrayMap()

    def getTicketBlock(ticket):
        available="""
        <button
            type="button"
            class="btn btn-primary btn-custom"
            data-bs-toggle="modal"
            data-bs-target="#exampleModal{ticket_number}"
            data-whatever="{ticket_number}">Ticket #{ticket_number}
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

@app.route("/")
def index():
    return render_template("index.html", len = len(getTicketBlocks()), tickets = getTicketBlocks())

if __name__ == "__main__":
    app.run()
