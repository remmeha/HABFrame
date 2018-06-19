

var time = {
	timeFormat: 24,
	dateLocation: '.date',
	timeLocation: '.time',
	updateInterval: 1000,
	intervalId: null
};

/**
 * Updates the time that is shown on the screen
 */
time.updateTime = function () {

	var _now = moment(),
		_date = _now.format('dddd, LL');

	$(this.dateLocation).html(_date);
	$(this.timeLocation).html(_now.format(this._timeFormat+':mm'));

}

time.init = function () {

	if (parseInt(time.timeFormat) === 12) {
		time._timeFormat = 'HH'
	} else {
		time._timeFormat = 'HH';
	}

	this.intervalId = setInterval(function () {
		this.updateTime();
	}.bind(this), 1000);

}

time.init()

var canvas = document.getElementById("canvas_analog_clock");
var ctx = canvas.getContext("2d");
var radius = canvas.height / 2;
ctx.translate(radius, radius);
radius = radius * 0.90
setInterval(drawClock, 1000);
var color = '#aaa';


function drawClock() {
  drawFace(ctx, radius);
  drawNumbers(ctx, radius);
  drawTime(ctx, radius);
  updateMedia();
}

function drawFace(ctx, radius) {
  var grad;
  ctx.beginPath();
  ctx.arc(0, 0, radius, 0, 2*Math.PI);
  ctx.fillStyle = 'black';
  ctx.fill();
  //grad = ctx.createRadialGradient(0,0,radius*0.99, 0,0,radius*1);
  //grad.addColorStop(0, color);
  //grad.addColorStop(0.5, color);
  //grad.addColorStop(1, color);
  //ctx.strokeStyle = grad;
  //ctx.lineWidth = radius*0.00;
  //ctx.stroke();
  ctx.beginPath();
  ctx.arc(0, 0, radius*0.03, 0, 2*Math.PI);
  ctx.fillStyle = color;
  ctx.fill();
}

function drawNumbers(ctx, radius) {
  var ang;
  var num;
  ctx.font = radius*0.15 + "px arial";
  ctx.textBaseline="middle";
  ctx.textAlign="center";
  var numbers = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]
  for(num = 1; num < 13; num++){
    ang = num * Math.PI / 6;
    ctx.rotate(ang);
    ctx.translate(0, -radius*0.8);
    ctx.rotate(-ang);
    //ctx.fillText(num.toString(), 0, 0);
   // ctx.fillText(numbers[num-1], 0, 0);
    ctx.rotate(ang);
    ctx.translate(0, radius*0.8);
    ctx.rotate(-ang);
  }
  for(num = 1; num < 13; num++){
    ang = num * Math.PI / 6;
    ctx.rotate(ang);
    ctx.translate(0, -radius*0.94);
    //ctx.rotate(-ang);
    //ctx.fillText(num.toString(), 0, 0);
    //ctx.fillText("I", 0, 0);
    ctx.beginPath();
    ctx.lineWidth = 3;
    //ctx.lineCap = "round";
    ctx.moveTo(0, radius*0.05);
    //ctx.rotate(pos);
    ctx.lineTo(0, -radius*0.01);
    ctx.strokeStyle = '#aaa';
    ctx.stroke();
    //ctx.rotate(ang);
    ctx.translate(0, radius*0.94);
    ctx.rotate(-ang);
  }
}

function drawTime(ctx, radius){
    var now = new Date();
    var hour = now.getHours();
    var minute = now.getMinutes();
    var second = now.getSeconds();
    //hour
    hour=hour%12;
    hour=(hour*Math.PI/6)+
    (minute*Math.PI/(6*60))+
    (second*Math.PI/(360*60));
    drawHand(ctx, hour, radius*0.5, radius*0.03);
    //minute
    minute=(minute*Math.PI/30)+(second*Math.PI/(30*60));
    drawHand(ctx, minute, radius*0.8, radius*0.03);
    // second
    second=(second*Math.PI/30);
    drawHand(ctx, second, radius*0.9, radius*0.02);
}

function drawHand(ctx, pos, length, width) {
    ctx.beginPath();
    ctx.lineWidth = width;
    ctx.lineCap = "round";
    ctx.moveTo(0,0);
    ctx.rotate(pos);
    ctx.lineTo(0, -length);
    ctx.strokeStyle = '#aaa';
    ctx.stroke();
    ctx.rotate(-pos);
}
