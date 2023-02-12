function getInfo() {
    const xhttp = new XMLHttpRequest();
    let text = document.getElementById('eval-input').value;
    xhttp.open("GET", `/test_view?text=${text}`, true);
    xhttp.send();

    xhttp.onreadystatechange = () => {
        if (xhttp.readyState === 4) {
            try {
                let response = xhttp.responseText;
                let output_text = document.getElementById('output-text');
                output_text.innerHTML = response.output;
            } catch (error) {
                let output_text = document.getElementById('output-text');
                output_text.innerHTML = error + "\n" + "Error 469 david to zase rozbil :(";
            }
        }
    }
}

// setInterval(() => {
    
// }, 500);
