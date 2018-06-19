

function update_chart(item_name, period) {
    cur_val = document.getElementById("chart_period_num").innerHTML; 
    console.log(cur_val)
    if ( period == "C") {
        document.getElementById("chart_period_num").innerHTML = "-"
    }
    else if ( period == "H" || period == "D" || period == "W" || period == "M") {
        document.getElementById("small_popup").style.display = 'none';
        if (period != "-") { period = cur_val.concat(period) }
        //document.getElementById("message_popup").style.display = 'block'; 
        //document.getElementById("message_popup").innerHTML = xmlHttp1.responseText;
        var url_request = main_url.concat("item/chart_data/").concat(item_name).concat("/").concat(period);
        var xmlHttp1 = null;
        xmlHttp1 = new XMLHttpRequest();
        xmlHttp1.open( "GET", url_request, false );
        xmlHttp1.send( null );
        var data = JSON.parse(xmlHttp1.responseText);
        //var data = Object.values((xmlHttp1.responseText);
        console.log(data["name"]);
        
        document.getElementById("chart-wrapper").innerHTML = "";
        document.getElementById("chart-wrapper").innerHTML = "<canvas id=\"myChart\"></canvas> ";
        
        draw_chart( "myChart", data );
    } else {
        if (cur_val != "-") { new_val = cur_val.concat(period); }
        else { new_val = period; }
        document.getElementById("chart_period_num").innerHTML = new_val;        
    }
}


function draw_chart( chart, data ) {
	Chart.defaults.global.defaultFontColor = '#aaa';
	Chart.defaults.global.defaultFontFamily = "'Courier New', Courier, monospace";
	//Chart.defaults.global.defaultFontFamily = "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif"
	Chart.defaults.global.defaultFontSize = '18';
	//Chart.defaults.global.defaultFontStyle = 'sans-serif';
	var color = Chart.helpers.color;
	var ctx = document.getElementById("myChart");
	var myChart = new Chart(ctx, {
		type: 'line',
		data: {
				labels: data["labels"],
				datasets: [{
					label: data["name"],
					backgroundColor: color(data["color"]).alpha(0.4).rgbString(),
					borderColor: data["color"],
					data: data["data"],
					fill: data["fill"],
					pointRadius: data["points"]
				}]
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				title: {
					display: false,
					text: 'Chart.js Line Chart'
				},
				tooltips: {
					enabled: false,
					mode: 'index',
					intersect: false,
				},
				hover: {
					mode: 'nearest',
					intersect: false
				},
				legend: {
					display: false,
					labels: {
						fontColor: 'rgb(255, 99, 132)'
					}
				},
				scales: {
					xAxes: [{
						display: true,
						scaleLabel: {
							display: true,
							labelString: data["xlabel"]
						},
						gridLines: { 
							display: data["grid"],
							color: "#666"
						}
					}],
					yAxes: [{
						display: true,
						scaleLabel: {
							display: true,
							labelString: data["ylabel"]
						},
						gridLines: { 
							display: data["grid"],
							color: "#666"
						}
					}]
				}
			}
	});
	
}
