

function popup_message() {
	var url1 = main_url.concat("message/message_popup");
	var xmlHttp2 = null;
    xmlHttp2 = new XMLHttpRequest();
    xmlHttp2.open( "GET", url1, false );
    xmlHttp2.send( null );
	document.getElementById("message_popup").style.display = 'block'; 
	document.getElementById("message_popup").innerHTML = xmlHttp2.responseText;
	var url1 = main_url.concat("message/message_timeout");
	var xmlHttp2 = null;
    xmlHttp2 = new XMLHttpRequest();
    xmlHttp2.open( "GET", url1, false );
    xmlHttp2.send( null ); 
	var timeout = parseInt(xmlHttp2.responseText)
	//document.getElementById("message_popup").innerHTML = xmlHttp2.responseText;
	setTimeout(closemessageunread, timeout*1000);
}



function closemessage(id) {
	document.getElementById("message_popup").style.display = 'none';
	message_unread = "false";
	var url1 = main_url.concat("message/markread_popup/".concat(id));
	var xmlHttp2 = null;
    xmlHttp2 = new XMLHttpRequest();
    xmlHttp2.open( "GET", url1, false );
    xmlHttp2.send( null );
    //show_message_page('0')
}

function closeallmessages(id) {
	document.getElementById("message_popup").style.display = 'none';
	message_unread = "false";
	var url1 = main_url.concat("message/markallread_popup/".concat(id));
	var xmlHttp2 = null;
    xmlHttp2 = new XMLHttpRequest();
    xmlHttp2.open( "GET", url1, false );
    xmlHttp2.send( null );
    show_message_page('0')
}

function deletemessage_popup(id) {
	document.getElementById("message_popup").style.display = 'none';
	var url1 = main_url.concat("message/delete_popup/".concat(id));
	var xmlHttp2 = null;
    xmlHttp2 = new XMLHttpRequest();
    xmlHttp2.open( "GET", url1, false );
    xmlHttp2.send( null );
}

function closemessageunread() {
	document.getElementById("message_popup").style.display = 'none';
	var url2 = main_url.concat("message/deactivate_popup/");
	var xmlHttp2 = null;
    xmlHttp2 = new XMLHttpRequest();
    xmlHttp2.open( "GET", url2, false );
    xmlHttp2.send( null );
}

function show_message(id) {
	var url2 = main_url.concat("message/showmessage/".concat(id));
	var xmlHttp2 = null;
    xmlHttp2 = new XMLHttpRequest();
    xmlHttp2.open( "GET", url2, false );
    xmlHttp2.send( null );
    //document.getElementById("right_half").innerHTML = "yes";
	document.getElementById("message_right_half").innerHTML = xmlHttp2.responseText;
}

function delete_message(id) {
	var url2 = main_url.concat("message/deletemessage/".concat(id));
	var xmlHttp2 = null;
    xmlHttp2 = new XMLHttpRequest();
    xmlHttp2.open( "GET", url2, false );
    xmlHttp2.send( null );
	document.getElementById("message_left_half").innerHTML = xmlHttp2.responseText;
	
	var url2 = main_url.concat("message/showmessage/-1");
	var xmlHttp2 = null;
    xmlHttp2 = new XMLHttpRequest();
    xmlHttp2.open( "GET", url2, false );
    xmlHttp2.send( null );
	document.getElementById("message_right_half").innerHTML = xmlHttp2.responseText;
}

function show_message_page(id) {
	var url2 = main_url.concat("message/showmessagepage/".concat(id));
	var xmlHttp2 = null;
    xmlHttp2 = new XMLHttpRequest();
    xmlHttp2.open( "GET", url2, false );
    xmlHttp2.send( null );
    //document.getElementById("right_half").innerHTML = "yes";
	document.getElementById("message_left_half").innerHTML = xmlHttp2.responseText;
	
	var url2 = main_url.concat("message/showmessage/".concat(id));
	var xmlHttp2 = null;
    xmlHttp2 = new XMLHttpRequest();
    xmlHttp2.open( "GET", url2, false );
    xmlHttp2.send( null );
	document.getElementById("message_right_half").innerHTML = xmlHttp2.responseText;
}

function show_toast_message() {
	var url1 = main_url.concat("message/get_toast/1");
	var xmlHttp2 = null;
    xmlHttp2 = new XMLHttpRequest();
    xmlHttp2.open( "GET", url1, false );
    xmlHttp2.send( null );
    console.log("New toast message");
	document.getElementById("info_popup").style.display = 'block'; 
	document.getElementById("info_popup").innerHTML = xmlHttp2.responseText;
	var url1 = main_url.concat("message/toast_timeout");
	var xmlHttp2 = null;
    xmlHttp2 = new XMLHttpRequest();
    xmlHttp2.open( "GET", url1, false );
    xmlHttp2.send( null ); 
	var timeout = parseInt(xmlHttp2.responseText)
	setTimeout(close_toast_message, timeout*1000);
}

function close_toast_message() {
	popup = $('#info_popup'); 
	popup.fadeOut(1000);
}
