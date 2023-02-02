function getTime() {
    let date, realTime, hours, minutes, seconds;
    date = new Date();
    hours = date.getHours();
    minutes = date.getMinutes();
    if (minutes < 10) {
        minutes = "0" + minutes;
    }

    seconds = date.getSeconds();
    if (seconds < 10) {
        seconds = "0" + seconds;
    }

    realTime = hours + ":" + minutes + ":" + seconds;
    return realTime;
}

function writeTime() {
    document.getElementById("time").innerHTML = getTime();
}

window.setInterval("writeTime()", 500);
