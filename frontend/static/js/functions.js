function getCookie(name) {
    if (!document.cookie) {return null;}
    
    const token = document.cookie.split(';')
        .map(c => c.trim())
    
    if (token.length === 0) {return null;}
    return decodeURIComponent(token[0].split('=')[1]);
}

function fetchResult(text) {
    const csrfToken = getCookie('CSRF-TOKEN');

    const xhttp = new XMLHttpRequest();
    xhttp.open("POST", `/test_view?text=${text}`, true);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.setRequestHeader("X-CSRFToken", csrfToken);
    xhttp.send();

    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            return JSON.parse(xhttp.responseText)["validated"][0];
        }
    }
}

function getInfo() {
    const outputField = document.getElementById('output-text');

    const xhttp = new XMLHttpRequest();
    let text = document.getElementById('eval-input').value;
    xhttp.open("GET", `/test_view?text=${text}`, true);
    xhttp.send();

    let data = JSON.parse(xhttp.responseText)["validated"][0];
    console.log(data);
    let claim = data["claim"]
    let label = data["label"]
    let percentage = [(data["supports"] * 100).toFixed(2), (data["refutes"] * 100).toFixed(2)]
    let evidence = data["evidence"]
    console.log(claim)
    console.log(percentage)
    console.log(evidence)

    outputField.innerHTML = `<b>Claim:</b> ${claim}<br/>`;
    outputField.innerHTML += `<b>Label:</b> ${label}<br/>`;
    outputField.innerHTML += `<b>Supports:</b> ${percentage[0]}%<br/>`;
    outputField.innerHTML += `<b>Refutes:</b> ${percentage[1]}%<br/>`;
    outputField.innerHTML += `<b>Evidence:</b> <br/>${evidence}<br/>`;
}