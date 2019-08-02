
var current_popup_url = ""
function frontpage_action(page, sub) {
    current_popup_url = main_url.concat("page/popup/").concat(page).concat("/").concat(sub);
    frontpage_action_load(update = "false");
    //make sure that the popup on a clock page closes after xx seconds
        if (main_screen_state == "clock") {
            console.log("closing popup after seconds")
            setTimeout(closepopup, 15000);
        }
}

function frontpage_action_load(update = "true") {
    if ( update == "reload") { url = current_popup_url.concat("/reload"); update = "true" }
    else { url = current_popup_url }
    var xmlHttp4 = null;
    xmlHttp4 = new XMLHttpRequest();
    xmlHttp4.open( "GET", url, false );
    xmlHttp4.send( null );
    //document.getElementById("setsetting_".concat(id)).innerHTML = "yes";
    var cur_state = document.getElementById("message_popup").style.display
    
    console.log("=====reloading widget=====");
    if (xmlHttp4.responseText.search("none_none") == -1 && !(cur_state != "block" && update == "true")) {
        document.getElementById("message_popup").style.display = 'block'; 
        if (xmlHttp4.responseText.search("widget not in sitemap") == -1) {
            console.log("=====reloaded widget =====");
            document.getElementById("message_popup").innerHTML = xmlHttp4.responseText;
        } else {
            console.log("=====widget not in sitemap=====") ;
            closepopup();
            update = "false";
        }
    }
    if (cur_state == "block" && update == "true") { setTimeout(frontpage_action_load.bind(null, "reload"), 5000); }
    
}


function item_action(item_type, item_name, or = "sub") {
	if (item_type == "Switch" || item_type == "Switch_single") {
		var url_request = main_url.concat("item/set/").concat(item_name);
	 	var xmlHttp1 = null;
    	xmlHttp1 = new XMLHttpRequest();
    	xmlHttp1.open( "GET", url_request, false );
    	xmlHttp1.send( null );
    	//document.getElementById("setsetting_".concat(id)).innerHTML = "yes";
		document.getElementById("item_action_".concat(item_name)).innerHTML = xmlHttp1.responseText;
	} else if (item_type == "Chart") {
		var url_request = main_url.concat("item/popup/").concat(item_name).concat("/default");
	 	var xmlHttp1 = null;
    	xmlHttp1 = new XMLHttpRequest();
    	xmlHttp1.open( "GET", url_request, false );
    	xmlHttp1.send( null );
    	//document.getElementById("setsetting_".concat(id)).innerHTML = "yes";
		if (xmlHttp1.responseText.search("none_none") == -1) {
			document.getElementById("large_popup").style.display = 'block'; 
			document.getElementById("large_popup").innerHTML = xmlHttp1.responseText;
			var url_request = main_url.concat("item/chart_data/").concat(item_name).concat("/default");
			var xmlHttp1 = null;
			xmlHttp1 = new XMLHttpRequest();
			xmlHttp1.open( "GET", url_request, false );
			xmlHttp1.send( null );
			var data = JSON.parse(xmlHttp1.responseText);
			//var data = Object.values((xmlHttp1.responseText);
			console.log(data["name"]);
			draw_chart( "myChart", data );
		}
	} else if (item_type == "Chart_popup") {
		var url_request = main_url.concat("item/popup_chart/").concat(item_name).concat("/default");
	 	var xmlHttp1 = null;
    	xmlHttp1 = new XMLHttpRequest();
    	xmlHttp1.open( "GET", url_request, false );
    	xmlHttp1.send( null );
    	//document.getElementById("setsetting_".concat(id)).innerHTML = "yes";
		if (xmlHttp1.responseText.search("none_none") == -1) {
			document.getElementById("small_popup").style.display = 'block'; 
			document.getElementById("small_popup").innerHTML = xmlHttp1.responseText;
		}
	} else {
		var url_request = main_url.concat("item/popup/").concat(item_name);
	 	var xmlHttp1 = null;
    	xmlHttp1 = new XMLHttpRequest();
    	xmlHttp1.open( "GET", url_request, false );
    	xmlHttp1.send( null );
    	//document.getElementById("setsetting_".concat(id)).innerHTML = "yes";
    	if (xmlHttp1.responseText.search("none_none") == -1 && xmlHttp1.responseText.search("</td><td>") == -1) {
			document.getElementById("small_popup").style.display = 'block'; 
			document.getElementById("small_popup").innerHTML = xmlHttp1.responseText;
		} else if (xmlHttp1.responseText.search("none_none") == -1) {
            console.log("Opening large popup");
			document.getElementById("message_popup").style.display = 'block'; 
			document.getElementById("message_popup").innerHTML = xmlHttp1.responseText;
		}
        
	}
	
    if (or == "main") {
        console.log("Reloading main div after action");
        reload_main_div(url_save);
    } 

    reload_set_new_timestamp(3200);
	console.log(url_request)
	
}

timeStampMs = window.performance && window.performance.now && window.performance.timing && window.performance.timing.navigationStart ? window.performance.now() + window.performance.timing.navigationStart : Date.now();
nextExecute = timeStampMs + 15000;
console.log(nextExecute);
console.log(timeStampMs);

function reload_after_action() {
	var timeStampInMs = window.performance && window.performance.now && window.performance.timing && window.performance.timing.navigationStart ? window.performance.now() + window.performance.timing.navigationStart : Date.now();
	if (timeStampInMs > nextExecute && url_save.search("photoframe") == -1 && url_save.search("messages") == -1 && url_save.search("clock") == -1) {
		console.log("Reloading main div");
		reload_main_div(url_save);
		nextExecute = timeStampInMs + 8000
	} else if (timeStampInMs > nextExecute && url_save.search("clock") != -1) {
        console.log("Reloading clk widget");
		get_widget_clock_page();
		nextExecute = timeStampInMs + 8000
    }
	setTimeout(reload_after_action, 250);
}
setTimeout(reload_after_action, 1000);

function reload_set_new_timestamp(addMs) {
	var timeStampInMs = window.performance && window.performance.now && window.performance.timing && window.performance.timing.navigationStart ? window.performance.now() + window.performance.timing.navigationStart : Date.now();
	nextExecute = timeStampInMs + addMs;
	console.log("Rescheduling next reload action");
}

function closepopup() {
	document.getElementById("small_popup").style.display = 'none';
	document.getElementById("message_popup").style.display = 'none'; 
	document.getElementById("large_popup").style.display = 'none'; 
    document.getElementById("large_popup").innerHTML = "";
    document.getElementById("small_popup").innerHTML = "";
    document.getElementById("message_popup").innerHTML = "";
}

function closesmallpopup() {
	document.getElementById("small_popup").style.display = 'none';
	document.getElementById("small_popup").innerHTML = "";
}

function item_popup_action(item_name, command, action, popupclose = true) {
	var url_request = main_url.concat("item/").concat(command).concat("/").concat(item_name).concat("/").concat(action);
	var xmlHttp1 = null;
	console.log(url_request)
        xmlHttp1 = new XMLHttpRequest();
        xmlHttp1.open( "GET", url_request, false );
        xmlHttp1.send( null );
    console.log(popupclose);
    if (xmlHttp1.responseText == "reload_widget_popup") { setTimeout(frontpage_action_load, 1000); }
    else { document.getElementById("item_action_".concat(item_name)).innerHTML = xmlHttp1.responseText; }
    if (popupclose) {
        closesmallpopup();
    }
		
}


function item_setpoint_action(item_name, step, mini, maxi, action) {
	cur_val = parseFloat(document.getElementById("setpoint").innerHTML);
	step = parseFloat(step)
	mini = parseFloat(mini)
	maxi = parseFloat(maxi)
    console.log(cur_val)
	if (document.getElementById("setpoint").innerHTML == "NULL") { cur_val = mini; }
	if (action == "add") {
		new_val = cur_val + step;
		if (new_val > maxi) { new_val = maxi; }
        if (step < 1) { document.getElementById("setpoint").innerHTML = parseFloat(new_val).toFixed(1);	}
        else { document.getElementById("setpoint").innerHTML = (new_val);	}
	}
	if (action == "rem") {
		new_val = cur_val - step;
		if (new_val < mini) { new_val = mini; }
		if (step < 1) { document.getElementById("setpoint").innerHTML = parseFloat(new_val).toFixed(1);	}
        else { document.getElementById("setpoint").innerHTML = (new_val);	}
	}
	if (action == "OK") {
		item_popup_action(item_name, 'cmd', cur_val)
	}
}

function item_slider_action(item_name, step, mini, maxi, action) {
	cur_val = parseFloat(document.getElementById("setpoint").value);
	if (document.getElementById("setpoint").innerHTML == "NULL") { cur_val = mini; }
	if (action == "OK") {
		item_popup_action(item_name, 'cmd', cur_val, popupclose = false)
	}
    try {
        document.getElementById("setpoint_value").innerHTML = cur_val;
    } catch(err) {
    	//setTimeout(EventChecker, 10*1000)
	}
}

function item_colorpicker_action(item_name, action) {
	var cur_val = document.getElementById("color").value.replace("#", "Color");
	document.getElementById("item_action_".concat(item_name)).innerHTML = cur_val;
	if (action == "ON") {
		item_popup_action(item_name, 'cmd', "ON")
	}
	if (action == "OFF") {
		item_popup_action(item_name, 'cmd', "Color000000")
	}
	if (action == "SET") {
		item_popup_action(item_name, 'cmd', cur_val)
	}
}

    





