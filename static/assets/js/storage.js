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

    var cashBashTickets = [];
    isInitial = false;
    if (count == 0) {
      isInitial = true;
    }

    if (isInitial) {
      localStorage.setItem(
        "cashBashTicketsChanceThisYear",
        JSON.stringify([0])
      );

      localStorage.setItem(
        "cashBashTicketsChanceNextYear",
        JSON.stringify([0])
      );
      cashBashTickets = [ticket_number];
    } else {
      var found = false;
      cashBashTickets = JSON.parse(localStorage.getItem("cashBashTickets"));

      for (var i = 0; i < cashBashTickets.length; i++) {
        if (cashBashTickets[i] == ticket_number) {
          found = true;
        }
      }
      if (!found) {
        cashBashTickets.push(ticket_number);
      }
    }

    if (ticket_number >= 1 && ticket_number <= 500) {
      localStorage.setItem("cashBashTickets", JSON.stringify(cashBashTickets));
    }

    return true;
  }

  return false;
}
