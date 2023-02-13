function getInfo() {
    const xhttp = new XMLHttpRequest();
    let text = document.getElementById('eval-input').value;
    xhttp.open("GET", `/test_view?text=${text}`, false);
    xhttp.send();

    xhttp.onreadystatechange = function () {
        if (xhttp.readyState === 4) {
            try {
                let response = JSON.parse(xhttp.responseText);
                response = JSON.stringify(response);
                console.log(response)
                let output_text = document.getElementById('output-text');
                output_text.innerHTML = response.output;
            } catch (error) {
                let output_text = document.getElementById('output-text');
                output_text.innerHTML = /*error + "\n" +*/ "Error 469 david to zase rozbil :(";
            }
        }
    }
}

// setInterval(() => {
    
// }, 500);
