//add new key=>value to the HTML5 storage
function SaveItem() {

	var name = document.forms.ShoppingList.name.value;
	var data = document.forms.ShoppingList.data.value;
	localStorage.setItem(name, data);
	doShowAll();

}
//------------------------------------------------------------------------------
//change an existing key=>value in the HTML5 storage
function ModifyItem() {
	var name1 = document.forms.ShoppingList.name.value;
	var data1 = document.forms.ShoppingList.data.value;
	//check if name1 is already exists

//check if key exists
			if (localStorage.getItem(name1) !=null)
			{
			  //update
			  localStorage.setItem(name1,data1);
			  document.forms.ShoppingList.data.value = localStorage.getItem(name1);
			}


	doShowAll();
}
//-------------------------------------------------------------------------
//delete an existing key=>value from the HTML5 storage
function RemoveItem() {
	var name = document.forms.ShoppingList.name.value;
	document.forms.ShoppingList.data.value = localStorage.removeItem(name);
	doShowAll();
}
//-------------------------------------------------------------------------------------
//restart the local storage
function ClearAll() {
	localStorage.clear();
	doShowAll();
}
//--------------------------------------------------------------------------------------
// dynamically populate the table with shopping list items
//below step can be done via PHP and AJAX too.
function doShowAll() {
	if (CheckBrowser()) {
		var key = "";
		var list = "<tr><th>Item</th><th>Value</th></tr>\n";
		var i = 0;
		//for more advance feature, you can set cap on max items in the cart
		for (i = 0; i <= localStorage.length-1; i++) {
			key = localStorage.key(i);
			list += "<tr><td>" + key + "</td>\n<td>"
					+ localStorage.getItem(key) + "</td></tr>\n";
		}
		//if no item exists in the cart
		if (list == "<tr><th>Item</th><th>Value</th></tr>\n") {
			list += "<tr><td><i>empty</i></td>\n<td><i>empty</i></td></tr>\n";
		}
		//bind the data to html table
		//you can use jQuery too....
		document.getElementById('list').innerHTML = list;
	} else {
		alert('Cannot save shopping list as your browser does not support HTML 5');
	}
}

function createJSONObject() {
	if (CheckBrowser()) {
        var list = "{ \"cart\" : [\n";
		var key = "";
		var i = 0;
		//for more advance feature, you can set cap on max items in the cart
		for (i = 0; i <= localStorage.length-2; i++) {
			key = localStorage.key(i);
			list += "{\"" + key + "\" : \""
					+ localStorage.getItem(key) + "\"},\n";
		}
        if(i <= localStorage.length-1) {
			key = localStorage.key(i);
			list += "{\"" + key + "\" : \""
					+ localStorage.getItem(key) + "\"}\n";
        }
        list += "]}";
        return JSON.parse(list);
	} else {
		alert('Cannot save shopping list as your browser does not support HTML 5');
	}
    return JSON.parse("{ \"cart\" : []}\n");
}

/*
 =====> Checking the browser support
 //this step may not be required as most of modern browsers do support HTML5
 */
 //below function may be redundant
function CheckBrowser() {
	if ('localStorage' in window && window['localStorage'] !== null) {
		// we can use localStorage object to store data
		return true;
	} else {
			return false;
	}
}
//-------------------------------------------------
/*
You can extend this script by inserting data to database or adding payment processing API to shopping cart..
*/

$(document).ready(function() {
	const ticketViewLib = {
        myspan: function() {
            $('<span>').text('Some text')
        },


    mydiv: function(ticket_number) {
      $('#outerdiv').append(
        $('<div>').prop({
          id: 'innerdiv',
          innerHTML: 'Hi there! ' + ticket_number,
          className: 'border pad'
        })
      );
    },
    mydiv2: function(ticket_number) {
      $('#outerdiv2').append(
        $('<div>').prop({
          id: 'innerdiv',
          innerHTML: "you " + ticket_number,
          className: 'border pad'
        })
      );
    },
        mydiv3: function(ticket_number) {
            $("<div>", {class: "card rounded-3 mb-4"}).append(
                $("<div>", {class: "card-body p-4"}).append(
                    $("<div>", {class: "row d-flex justify-content-between align-items-center"}).append(
                        $("<div>", {class: "col-md-2 col-lg-2 col-xl-2"}).append(
                            $('<img>',{class:'img-fluid rounded-3',src:'https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-shopping-carts/img1.webp',alt:'Cotton T-shirt'})
                        ),
                        $("<div>", {class: "col-md-3 col-lg-3 col-xl-3"}).append(
                            $("<p>", {class: "lead fw-normal mb-2"}).text(
                                "Cash Bash Ticket"
                            ),
                            $("<p>").text( "" + ticket_number).prepend(
                                $('<span>', {class: "text-muted"}).text("Ticket Number ")

                            )
                        )
                    )
                )
            ).appendTo("#outerdiv2")

        }
  }
	let tickets = [1, 2, 3];




  $.each( tickets, function( index, value ){
      //sum += value;
      ticketViewLib.mydiv3(value);
  });


});
