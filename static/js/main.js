
function reload_main_div(url) {
    try {
        if (url.search("clock") != -1) {   //screensaver is either analog clock, digital clock or black screen
            document.getElementById("clocktop").style.display = 'none';
            document.getElementById("datetop").style.display = 'none';
            main_screen_state = "clock";
            main_url_check = main_url.concat("check/clock/".concat(clock_type));
            get_widget_clock_page();
        } else if (url.search("black") != -1) {  //external screensaver mode (cmd or url)
            document.getElementById("clocktop").style.display = 'none';
            document.getElementById("datetop").style.display = 'none';
            main_screen_state = "clock";
            main_url_check = main_url.concat("check/black/".concat(clock_type));
            document.getElementById("widget_clock_page").innerHTML = ""
        } else if (url.search("screensaver") != -1) {  //external screensaver mode (cmd or url)
            main_screen_state = "screensaver";
            main_url_check = main_url.concat("check/main/".concat(clock_type));
            document.getElementById("widget_clock_page").innerHTML = ""
        } else if (url.search("photoframe") != -1) {  // start photoframe
            document.getElementById("clocktop").style.display = 'none';
            document.getElementById("datetop").style.display = 'none';
            main_screen_state = "photoframe";
            main_url_check = main_url.concat("check/photoframe");
            document.getElementById("widget_clock_page").innerHTML = ""
        } else {
            document.getElementById("mainscreenclock").style.display = 'none';
            main_screen_state = "main";
            main_url_check = main_url.concat("check/main");
            document.getElementById("clocktop").style.display = 'block';
            document.getElementById("datetop").style.display = 'block';
            document.getElementById("widget_clock_page").innerHTML = ""
        }
        url_save = url;
        console.log("Main url: ".concat(url))
        var url_request = main_url.concat(url);
        var xmlHttp5 = null;
        xmlHttp5 = new XMLHttpRequest();
        xmlHttp5.open( "GET", url, false );
        xmlHttp5.send( null );
        if (xmlHttp5.responseText == "gotomain") {  // start photoframe
            var xmlHttp5 = null;
            xmlHttp5 = new XMLHttpRequest();
            xmlHttp5.open( "GET", "page/maindiv", false );
            xmlHttp5.send( null );
            url = "page/maindiv";
        }
        document.getElementById("placeholder_main").innerHTML = xmlHttp5.responseText;
        autoSizeText();
        
        if (url.search("photoframe") != -1) {
            start_photoframe();
        } else {
            stop_photoframe();
        }
        if (url.search("/maindiv") != -1 || url.search("/menuwidget") != -1) {
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

function get_widget_clock_page() {
    var xmlHttpcheck1 = null;
    xmlHttpcheck1 = new XMLHttpRequest();
    xmlHttpcheck1.open( "GET", main_url.concat("page/clk_widget/"), false );
    xmlHttpcheck1.send( null );
    document.getElementById("widget_clock_page").innerHTML = xmlHttpcheck1.responseText;
    if (xmlHttpcheck1.responseText == "") {
         document.getElementById("widget_clock_page").width = "0%";
         document.getElementById("clock_page_clk").width = "100%";
    } else {
        document.getElementById("widget_clock_page").width = "50%";
        document.getElementById("clock_page_clk").width = "50%";
    }
    resize_digital_clk();
}

function resize_digital_clk() {    
    //resize digital clock text:
    if (clock_type == "digital") {
        if (document.getElementById("widget_clock_page").innerHTML == "") {
            var target = parseInt($(window).width() / 2); 
            var targettable = target; }
        else { var target = parseInt($(window).width() / 2.7); var targettable = "100%"; }
        el = document.getElementById("mainscreenclocktable");
        $(el).css('width', targettable);
        el = document.getElementById("digital_clock");
        $(el).css('width', target);
        $(el).css('font-size', "300px");
        var resizeText, _results1;
          resizeText = function() {
            var elNewFontSize;
            elNewFontSize = (parseInt($(el).css('font-size').slice(0, -2)) - 1) + 'px';
            return $(el).css('font-size', elNewFontSize);
          };
          _results1 = [];
          var tries = 0;
          while (el.scrollWidth  > target && tries < 150) {
            _results1.push(resizeText());
            tries += 1;
          }
        
        var topmargin = ((screen.height - el.scrollHeight)/2).toString() + "px";
        console.log("Top margin: " + topmargin) // 189px
        document.getElementById("mainscreenclock").style.top = topmargin;
        
    } else {
        var size = parseInt(($(window).width() * 0.9) / 2.5);
        var topmargin = ((screen.height - size)/2).toString() + "px";
        console.log("Top margin: " + topmargin) // 189px
        document.getElementById("mainscreenclock").style.top = topmargin;
    }
}



var autoSizeText;
autoSizeText = function() {
  var el, elements, _i, _len, _results;
  elements = $('.resize');
  console.log(elements);
  if (elements.length < 0) {
    return;
  }
  _results = [];
  for (_i = 0, _len = elements.length; _i < _len; _i++) {
    el = elements[_i];
    _results.push((function(el) {
      var resizeText, _results1;
      resizeText = function() {
        var elNewFontSize;
        elNewFontSize = (parseInt($(el).css('font-size').slice(0, -2)) - 2) + 'px';
        return $(el).css('font-size', elNewFontSize);
      };
      _results1 = [];
      var tries = 0;
      while (el.parentElement.parentElement.parentElement.scrollHeight + 4 > el.parentElement.parentElement.parentElement.parentElement.offsetHeight && tries < 15) {
        _results1.push(resizeText());
        tries += 1;
      }
      return _results1;
    })(el));
  }
  console.log(_results);
  return _results;
};
