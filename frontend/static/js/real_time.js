function getInfo() {
    const outputField = document.getElementById('output-text');

    const xhttp = new XMLHttpRequest();
    let text = document.getElementById('eval-input').value;
    xhttp.open("GET", `/test_view?text=${text}`, false);
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

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');