
		
function EventChecker() {
	
	//try catch to keep always going
	try {
		var xmlHttpcheck = null;
		xmlHttpcheck = new XMLHttpRequest();
        console.log(main_url_check)
		xmlHttpcheck.open( "GET", main_url_check, false );
		xmlHttpcheck.send( null );
		console.log("Response: " + xmlHttpcheck.responseText);
		if (xmlHttpcheck.responseText.search("new_message") == -1) {
			if (xmlHttpcheck.responseText.search("no_action") == -1) {
				if (xmlHttpcheck.responseText.search("new_toast") != -1) {
					show_toast_message();
				}
				else if (xmlHttpcheck.responseText.search("clock") != -1 ) {
                    //set clock type etc.
                    if (xmlHttpcheck.responseText.search("analog") != -1 ) { 
                        document.getElementById("mainscreenclock").style.display = 'block';
                        document.getElementById("canvas_analog_clock").style.display = 'block'; 
                        document.getElementById("digital_clock").style.display = 'none';
                        clock_type = "analog"
                        console.log("Clock type set to: " + clock_type)
                    } else if (xmlHttpcheck.responseText.search("digital") != -1 ) {
                        document.getElementById("mainscreenclock").style.display = 'block';
                        clock_type = "digital"
                        document.getElementById("digital_clock").style.display = 'block'; 
                        document.getElementById("canvas_analog_clock").style.display = 'none'; 
                        console.log("Clock type set to: " + clock_type)
                    } else if (xmlHttpcheck.responseText.search("black") != -1 ) {
                        document.getElementById("mainscreenclock").style.display = 'block';
                        clock_type = "black"
                        document.getElementById("digital_clock").style.display = 'none'; 
                        document.getElementById("canvas_analog_clock").style.display = 'none'; 
                        console.log("Clock type set to: " + clock_type)
                    } else {
                        clock_type = "none"
                        document.getElementById("digital_clock").style.display = 'none'; 
                        document.getElementById("canvas_analog_clock").style.display = 'none'; 
                        console.log("Clock type set to: " + clock_type)
                    }
                    if (url_save.search("clock") == -1 || xmlHttpcheck.responseText.search("clock/off") != -1) {  
                        //document.getElementById("mainscreenclock").style.display = 'none';
                        reload_main_div(xmlHttpcheck.responseText);
                    }
				} else if (xmlHttpcheck.responseText.search("black") != -1) {
                    document.getElementById("mainscreenclock").style.display = 'block';
                    clock_type = "black"
                    document.getElementById("digital_clock").style.display = 'none'; 
                    document.getElementById("canvas_analog_clock").style.display = 'none'; 
					reload_main_div("page/black/off");
				} else if (xmlHttpcheck.responseText.search("close_return_main") != -1) {
                    closepopup();
					reload_main_div("page/maindiv/reload");
				} else if (xmlHttpcheck.responseText.search("screensaver") != -1) {
                    clock_type = "screensaver"
                    document.getElementById("mainscreenclock").style.display = 'block';
                    document.getElementById("digital_clock").style.display = 'none'; 
                    document.getElementById("canvas_analog_clock").style.display = 'none';
					reload_main_div(xmlHttpcheck.responseText);
				} else if (xmlHttpcheck.responseText.search("menu") != -1) {
                    document.getElementById("mainscreenclock").style.display = 'none';
					reload_main_div("page/maindiv");
				} else if (xmlHttpcheck.responseText.search("photoframe") != -1) {
                    document.getElementById("mainscreenclock").style.display = 'none';
					reload_main_div(xmlHttpcheck.responseText);
				} else if (xmlHttpcheck.responseText.search("maindiv") != -1) {
					reload_main_div(xmlHttpcheck.responseText);
				} else {
					window.location.href = xmlHttpcheck.responseText;
				}
			}
		} else {
			popup_message();	
		} 
		//setTimeout(EventChecker, 10*1000)
	}
	catch(err) {
    	//setTimeout(EventChecker, 10*1000)
	}
}

function RunCheckEvents() {
	EventChecker();
	console.log("=================Running event checker=================");
	setTimeout(RunCheckEvents, 5*1000);
}

setTimeout(RunCheckEvents, 1*1000);




