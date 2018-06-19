
function reload_main_div(url) {
    try {
        if (url.search("clock") != -1) {   //screensaver is either analog clock, digital clock or black screen
            document.getElementById("clocktop").style.display = 'none';
            document.getElementById("datetop").style.display = 'none';
            main_screen_state = "clock";
            main_url_check = main_url.concat("check/clock/".concat(clock_type));
        } else if (url.search("black") != -1) {  //external screensaver mode (cmd or url)
            document.getElementById("clocktop").style.display = 'none';
            document.getElementById("datetop").style.display = 'none';
            main_screen_state = "clock";
            main_url_check = main_url.concat("check/black/".concat(clock_type));
        } else if (url.search("screensaver") != -1) {  //external screensaver mode (cmd or url)
            main_screen_state = "screensaver";
            main_url_check = main_url.concat("check/main/".concat(clock_type));
        } else if (url.search("photoframe") != -1) {  // start photoframe
            document.getElementById("clocktop").style.display = 'none';
            document.getElementById("datetop").style.display = 'none';
            main_screen_state = "photoframe";
            main_url_check = main_url.concat("check/photoframe");
        } else {
            document.getElementById("mainscreenclock").style.display = 'none';
            main_screen_state = "main";
            main_url_check = main_url.concat("check/main");
            document.getElementById("clocktop").style.display = 'block';
            document.getElementById("datetop").style.display = 'block';
        }
        url_save = url;
        console.log("Main url: ".concat(url))
        var url_request = main_url.concat(url);
        var xmlHttp5 = null;
        xmlHttp5 = new XMLHttpRequest();
        xmlHttp5.open( "GET", url, false );
        xmlHttp5.send( null );
        document.getElementById("placeholder_main").innerHTML = xmlHttp5.responseText;
        
        if (url.search("photoframe") != -1) {
            start_photoframe();
        } else {
            stop_photoframe();
        }
        if (url.search("/maindiv") != -1) {
            //add reload to make sure server doesn't refresh screensaver
            if (url.search("/reload") == -1) {
                url_save = url.concat("/reload");
            }
            console.log(url_save);
        }
    }
	catch(err) {
    	console.log(err)
	}
}

function reload_main_body(url) {
	var xmlHttpcheck1 = null;
	xmlHttpcheck1 = new XMLHttpRequest();
	xmlHttpcheck1.open( "GET", url, false );
	xmlHttpcheck1.send( null );
	document.getElementById("main_body").innerHTML = xmlHttpcheck1.responseText	
}

