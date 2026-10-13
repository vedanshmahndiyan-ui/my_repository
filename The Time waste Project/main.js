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

const clicksDisplay = document.getElementById("currentClicks");
const timeDisplay = document.getElementById("timeWasted");
const colorDisplay = document.getElementById("currentColor");
const increaseButton = document.getElementById("increaseClicks");
const decreaseButton = document.getElementById("decreaseClicks");
const resetButton = document.getElementById("resetClicks");
const randomColorButton = document.getElementById("randomColorBtn");

// Makes a random hex colour like "#3FA9C2"
function getRandomColor() {
    const hex = Math.floor(Math.random() * 0x1000000).toString(16);
    return "#" + hex.padStart(6, "0").toUpperCase();
}

function changeColor() {
    currentColor = getRandomColor();
    document.body.style.backgroundColor = currentColor;
    colorDisplay.textContent = currentColor;

    // Pick black or white text so it stays readable on dark/light backgrounds
    const r = parseInt(currentColor.slice(1, 3), 16);
    const g = parseInt(currentColor.slice(3, 5), 16);
    const b = parseInt(currentColor.slice(5, 7), 16);
    const brightness = (r * 299 + g * 587 + b * 114) / 1000;
    document.body.style.color = brightness > 128 ? "#000000" : "#FFFFFF";
}
randomColorButton.addEventListener("click", changeColor);


function increaseClicks() {
    startClicks += clickIncrement;
    clicksDisplay.textContent = startClicks;
};
increaseButton.addEventListener("click", increaseClicks);


function decreaseClicks() {
    startClicks -= clickDecrement;
    clicksDisplay.textContent = startClicks;
};
decreaseButton.addEventListener("click", decreaseClicks);

resetButton.addEventListener("click", () => {
    startClicks = resetClicks;
    clicksDisplay.textContent = startClicks;
});


function updateTimeWasted() {
    timeWasted++;
    timeDisplay.textContent = timeWasted;
    setTimeout(updateTimeWasted, 1000); 
};

updateTimeWasted();