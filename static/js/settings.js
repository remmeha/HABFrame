

function setsetting(id) {
	var url_request_main_sensor = main_url.concat("setting/setsetting/").concat(id);
	 var xmlHttp = null;
    xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", url_request_main_sensor, false );
    xmlHttp.send( null );
    //document.getElementById("setsetting_".concat(id)).innerHTML = "yes";
	document.getElementById("setsetting_".concat(id)).innerHTML = xmlHttp.responseText;
}
