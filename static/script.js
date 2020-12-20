var timeoutID;
var timeout = 1000;

function setup() {
	document.getElementById("theButton").addEventListener("click", makePost, true);
	//set a timeout and call the poller function after timeout milliseconds
	timeoutID = window.setTimeout(poller, timeout);
}

//does what we had before
function makePost() {
	window.clearTimeout(timeoutID); //stops the poll from happening until the post is finished
	var httpRequest = new XMLHttpRequest();

	if (!httpRequest) {
		alert('Giving up :( Cannot create an XMLHTTP instance');
		return false;
	}

	var one = document.getElementById("theMsg").value
	var row = [one]

	var chatRoomName = document.getElementById("chatName").value
	chatRoomName = chatRoomName.trim()
	console.log(chatRoomName)

	//make the request to the server here
	httpRequest.onreadystatechange = function() { handlePost(httpRequest, row) };

	httpRequest.open("POST", "/new_message/"+chatRoomName.trim());
	httpRequest.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');

	var data;
	data = "one=" + one;

	httpRequest.send(data);
}

function handlePost(httpRequest) {
	if (httpRequest.readyState === XMLHttpRequest.DONE) {
		if (httpRequest.status === 200) {
			//when the request succeeds, add the row to the table and cleared out messages
			//addRow(row); //remove this where you would use this in a chat box like location
			//to make sure you see things in the order than they are entered!!!
			clearInput();
			addRows(JSON.parse(httpRequest.responseText)) //new
			timeoutID = window.setTimeout(poller, timeout) //new
		} 
	}
}

//called by timeout once timeout is over
function poller() {
	var httpRequest = new XMLHttpRequest(); //makes new request

	if (!httpRequest) { //check to make sure it was created correctly
		alert('Giving up :( Cannot create an XMLHTTP instance');
		return false;
	}
	var chatRoomName = document.getElementById("chatName").value
	console.log(chatRoomName);
	chatRoomName = chatRoomName.trim() 
	httpRequest.onreadystatechange = function() { handlePoll(httpRequest) };
	httpRequest.open("GET", "/messages/"+chatRoomName.trim());
	httpRequest.send();
}

function handlePoll(httpRequest) {
	if (httpRequest.readyState === XMLHttpRequest.DONE) {
		if (httpRequest.status === 200) {
			addRows(JSON.parse(httpRequest.responseText));
			timeoutID = window.setTimeout(poller, timeout); //once all of this is finished processing,
			//start our poll again which will initiate a new request
		} 
	}
}

//new function
 function addRows(rows) {
	var tab = document.getElementById("messages");
	var newRow, newCell, newText;

	//httpRequest.open("GET", "/homepage")


	while (tab.rows.length > 0) { //clearing the table 
		tab.deleteRow(0);
	}
				for (var j = 0; j<rows.length; j++)
				{
						console.log("Rows j" + rows[j])
						if (rows[j] == "The chat room was deleted. Click anywhere to be redirected.") 
							{
								if(confirm('This chat room has been deleted! Moving you back to the homepage.')){
									window.location.reload();  
								}
							}
						newRow = tab.insertRow();
						newCell = newRow.insertCell();
						newText = document.createTextNode(rows[j]);
						newCell.appendChild(newText);
				}
	//}
}

function clearInput() {
	//clears our text boxes in our form
	document.getElementById("theMsg").value = "";
}

window.addEventListener("load", setup, true);