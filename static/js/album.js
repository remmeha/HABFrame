
state = '1';

image_actual2 = new Image();
image_actual1 = new Image();
image1 = $('#pic1');
image2 = $('#pic2'); 

AlbumName1 = "AlbumName1";
AlbumName2 = "AlbumName2";

album_onoff = "off";

random_picture_url = "state/picture/new"
picture_info_url = "state/picture/info"

function toggle_picture_2(AlbumName) {
	document.getElementById("albumName").innerHTML = "please wait...";
	setTimeout(reload_picture1, 5000);
	
	var timeout_out = Math.floor(Math.random() * 1500) + 500
	var timeout_in = Math.floor(Math.random() * 200) + 500 
	
	console.log(AlbumName2)
	image2.fadeOut(0);
	image1.fadeOut(timeout_out, function () {
   	image2.fadeIn(timeout_in, function () {
   	//image1
		console.log("Setting albumname2")
		document.getElementById("albumName").innerHTML = AlbumName2; });
  	});
		
}

function toggle_picture_1() {
	setTimeout(reload_picture2, 5000);	
	document.getElementById("albumName").innerHTML = "please wait...";
	
	var timeout_out = Math.floor(Math.random() * 1500) + 500
	var timeout_in = Math.floor(Math.random() * 200) + 500 
   	
 	//image1.fadeOut(0);
 	console.log(AlbumName1)
    image2.fadeOut(timeout_out, function () {
   	image1.fadeIn(timeout_in, function () { 
   		if (state == '1') {
   			document.getElementById("albumName").innerHTML = "starting...";
   		} else {
			console.log("Setting albumname1")
   			document.getElementById("albumName").innerHTML = AlbumName1;
   		}
   	
   	});
   });
	
}

function reload_picture2() {

	console.log("reloading picture 2")
	document.getElementById("load").innerHTML = "";

	if (state != '2') {
        delete image_actual2;
	   image_actual2 = new Image();
	   image_actual2.onload =	function () {   
	   	document.getElementById("load").innerHTML = ".";	
	   }
	  	image_actual2.src = random_picture_url.concat("?" + new Date().getTime());
	   document.getElementById("pic2img").src = image_actual2.src;
	}
	if (album_onoff == "on") {
		if (state == '1') {
			setTimeout(check_picture_2, 1800);
			state == '2';
		} else if (state == '2') {
			setTimeout(check_picture_2, 1800);
		} else {
			var rand = get_rand_time();
			setTimeout(check_picture_2, rand);
		}
	}
}		      
      
   
function reload_picture1(start = false) {
	
	console.log("reloading picture 1")
	document.getElementById("load").innerHTML = ""; 
      	
    delete image_actual1;
  	image_actual1 = new Image();
  	image_actual1.onload =	function () {   
  			document.getElementById("load").innerHTML = ":"; 
  	}
	var file = null;   
  	image_actual1.src = random_picture_url.concat("?" + new Date().getTime());
	document.getElementById("pic1img").src = image_actual1.src;
	
	var rand = get_rand_time();
	if (album_onoff == "on") {
		setTimeout(check_picture_1, rand);
	}
	
}

function check_picture_1() {
	loaded_picture = document.getElementById("load").innerHTML;
	if (album_onoff == "on") {
		if (loaded_picture == "") {
			var rand = Math.round(Math.random() * (10000 - 5000)) + 5000; 
			document.getElementById("load").innerHTML = "/";
			setTimeout(reload_picture1, 200);
		}  else {
			state = 'loaded';
			document.getElementById("load").innerHTML = "*";
            var xmlHttp1 = null;
            xmlHttp1 = new XMLHttpRequest();
            //xmlHttp1.open( "GET", url_pf_get_picture, false );
            xmlHttp1.open( "GET", picture_info_url, false );
            xmlHttp1.send( null ); 
            AlbumName1 = xmlHttp1.responseText;
			setTimeout(toggle_picture_1, 1000);
		}
	}
}

function check_picture_2() {
	loaded_picture = document.getElementById("load").innerHTML;
	if (album_onoff == "on") {
		if (loaded_picture == "") {
			var rand = Math.round(Math.random() * (10000 - 5000)) + 5000; 
			document.getElementById("load").innerHTML = "/";
			setTimeout(reload_picture2, 1000);
		}  else {
			document.getElementById("load").innerHTML = "*";
            var xmlHttp2 = null;
            xmlHttp2 = new XMLHttpRequest();
            //xmlHttp1.open( "GET", url_pf_get_picture, false );
            xmlHttp2.open( "GET", picture_info_url, false );
            xmlHttp2.send( null ); 
            AlbumName2 = xmlHttp2.responseText;
			setTimeout(toggle_picture_2, 1000);
		}
	}
}


function get_rand_time() {
	var rand = Math.round(Math.random() * (25000 - 10000)) + album_display_time;
	return rand;
}



function start_photoframe() {
	console.log("Starting photoframe")
	album_onoff = "on";
	image1 = $('#pic1');
	image2 = $('#pic2');
    random_picture_url = random_picture_url;
    var xmlHttp1 = null;
    xmlHttp1 = new XMLHttpRequest();
    xmlHttp1.open( "GET", main_url.concat("setting/getsetting/frame_display_time"), false );
    xmlHttp1.send( null ); 
    album_display_time = parseInt(xmlHttp1.responseText)
    console.log(album_display_time)
    toggle_picture_1();
}

function stop_photoframe() {
	//console.log("Stopping photoframe");
	album_onoff = "off";
}


