/* 
variables required:
    1.clicks
    2.time wasted
    3.current colour
    4.Random color
    5.increase clicks
    6.decrease clicks
    7.reset clicks

*/

let startClicks = 0;
let timeWasted = 0;
let currentColor = "#FFFFFF"; // Default color
let clickIncrement = 1;
let clickDecrement = 1;
let resetClicks = 0;

const timeDisplay = document.getElementById("timeDisplay");
const colorDisplay = document.getElementById("colorDisplay");
const increaseButton = document.getElementById("increaseButton");
const decreaseButton = document.getElementById("decreaseButton");
const resetButton = document.getElementById("resetButton");

increaseButton.addEventListener("click", () => {
    startClicks += clickIncrement;
});

decreaseButton.addEventListener("click", () => {
    startClicks -= clickDecrement;
});

resetButton.addEventListener("click", () => {
    startClicks = resetClicks;
});

