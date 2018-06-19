
function updateMedia() {
   //this function is triggered from DrawClock()
   var elementExists = document.getElementById("mediaprogress");
   if (elementExists && elementExists.innerHTML != "-" && elementExists.innerHTML != "Paused" && elementExists.innerHTML != "Playing" && elementExists.innerHTML != "Stopped") {
       var playing = document.getElementById("mediaplaying").innerHTML;
       var timeStampInMs = window.performance && window.performance.now && window.performance.timing && window.performance.timing.navigationStart ? window.performance.now() + window.performance.timing.navigationStart : Date.now();
       
       if (playing == "PAUSE") {
           var lastchecked = document.getElementById("medialastchecked").innerHTML;
           var starttime = parseInt(document.getElementById("mediastarttime").innerHTML);
           var endtime = parseInt(document.getElementById("mediaendtime").innerHTML);
           document.getElementById("mediastarttime").innerHTML = (starttime + timeStampInMs - lastchecked).toString();
           document.getElementById("mediaendtime").innerHTML = (endtime + timeStampInMs - lastchecked).toString();
       }
       document.getElementById("medialastchecked").innerHTML = timeStampInMs;
       var starttime = parseInt(document.getElementById("mediastarttime").innerHTML);
       var endtime = parseInt(document.getElementById("mediaendtime").innerHTML);
       var duration = parseFloat((endtime - starttime)/1000.0).toFixed(0);
       if (timeStampInMs > endtime) { timeStampInMs = endtime; }
       if (timeStampInMs < starttime) { timeStampInMs = starttime; }
       var timespend = parseFloat((timeStampInMs - starttime)/1000.0).toFixed(0);
       var progress = parseFloat((timespend / duration)*100).toFixed(1);
       if (progress > 100) {
           progress = 100
           timespend = duration 
           document.getElementById("mediaplaying").innerHTML = "PAUSE"
       }
       if (playing != "PAUSE") {
           if (duration > 10*60) {
                document.getElementById("mediaprogress").innerHTML = timespend.toString().toHHMMSS() + " / " + duration.toString().toHHMMSS() + " (" + progress.toString() + "%)";
           } else {
               document.getElementById("mediaprogress").innerHTML = timespend.toString().toHHMMSS() + " / " + duration.toString().toHHMMSS();
           }
       } else {
           document.getElementById("mediaprogress").innerHTML = timespend.toString().toHHMMSS() + " / " + duration.toString().toHHMMSS() + " (paused)";
       }
   }
}

String.prototype.toHHMMSS = function () {
    var sec_num = parseInt(this, 10); // don't forget the second param
    var hours   = Math.floor(sec_num / 3600);
    var minutes = Math.floor((sec_num - (hours * 3600)) / 60);
    var seconds = sec_num - (hours * 3600) - (minutes * 60);

    if (hours   < 10) {hours   = "0"+hours;}
    if (minutes < 10) {minutes = "0"+minutes;}
    if (seconds < 10) {seconds = "0"+seconds;}
    if (hours == 0) {
        return minutes+':'+seconds;
    } else {
        return hours+':'+minutes+':'+seconds;
    }
}

function item_media_action(item_name, command, action) {
	var url_request = main_url.concat("item/").concat(command).concat("/").concat(item_name).concat("/").concat(action);
	var xmlHttp1 = null;
	console.log(url_request)
    xmlHttp1 = new XMLHttpRequest();
    xmlHttp1.open( "GET", url_request, false );
    xmlHttp1.send( null );
    if (action == "PAUSE") {
        document.getElementById("mediaplaying").innerHTML = "PAUSE"
    }
	if (action == "PLAY") {
        document.getElementById("mediaplaying").innerHTML = "PLAY"
    }	
    if (action == "NEXT" || action == "PREVIOUS") {
        document.getElementById("mediaplaying").innerHTML = "PLAY"
        var timeStampInMs = window.performance && window.performance.now && window.performance.timing && window.performance.timing.navigationStart ? window.performance.now() + window.performance.timing.navigationStart : Date.now();
        document.getElementById("mediastarttime").innerHTML = timeStampInMs
        document.getElementById("mediaendtime").innerHTML = timeStampInMs + 3*60*1000
        reload_set_new_timestamp(2500);
    }
}

function widget_media_action(page_name, widget_name, item_name, command, action) {
    item_media_action(item_name, command, action);
    setTimeout(frontpage_action_load, 2000);
}
