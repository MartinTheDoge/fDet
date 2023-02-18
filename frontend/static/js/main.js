const input = document.querySelector('#eval-input');
const output = document.querySelector('#output-text');
const button = document.querySelector('#eval-button');

button.addEventListener("click", c => {
    const text = input.value;
    button.disabled = true;
    fetchResult(text, output, button);
})