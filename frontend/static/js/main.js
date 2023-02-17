const input = document.querySelector('#eval-input');
const output = document.querySelector('#output-text');
const button = document.querySelector('#eval-button');

button.addEventListener("click", c => {
    console.log(fetchResult(input.value))
})