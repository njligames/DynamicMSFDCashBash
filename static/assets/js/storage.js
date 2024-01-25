function CheckBrowser() {
  if ("localStorage" in window && window["localStorage"] !== null) {
    // we can use localStorage object to store data
    return true;
  } else {
    return false;
  }
}

function AddCashBashTicket(ticket_number) {
  if (CheckBrowser()) {
    count = localStorage.length;
    if (count == 0) {
      var cashBashTickets = [ticket_number];

      localStorage.setItem("cashBashTickets", JSON.stringify(cashBashTickets));

      localStorage.setItem(
        "cashBashTicketsChanceThisYear",
        JSON.stringify([0])
      );

      localStorage.setItem(
        "cashBashTicketsChanceNextYear",
        JSON.stringify([0])
      );
      return false;
    } else {
      var cashBashTickets = JSON.parse(localStorage.getItem("cashBashTickets"));
      var found = false;

      var tickets = JSON.parse(localStorage.getItem("cashBashTickets"));

      for (var i = 0; i < tickets.length; i++) {
        if (tickets[i] == ticket_number) {
          found = true;
        }
      }
      if (!found) {
        cashBashTickets.push(ticket_number);
      }
      localStorage.setItem("cashBashTickets", JSON.stringify(cashBashTickets));
    }

    // ticketViewLib.show();
    return true;
  }
}
