/*
variables:
    1.current state
    2.opponent state
    3.player score
    4.opponent score
    5.rounds played
    6.reset game
    7.play round
tasks:
    1. Initialize game state
    2. Handle player input
    3. Generate opponent move
    4. Determine round winner
    5. Update scores and rounds played
    6. Reset game state
*/

let playerScore = 0;
let computerScore = 0;
let playerMove = "";

function selectMove(move) {
    playerMove = move;
    // highlight only the chosen button
    for (const name of ["Rock", "Paper", "Scissors"]) {
        document.getElementById(name).classList.toggle("selected", name === move);
    }
}

document.getElementById("Rock").onclick = () => selectMove("Rock");
document.getElementById("Paper").onclick = () => selectMove("Paper");
document.getElementById("Scissors").onclick = () => selectMove("Scissors");

document.getElementById("play-round").onclick = function() {
    if (!playerMove) {
        document.getElementById("result").textContent = "Select a move first!";
        return;
    }

    const choices = ["Rock", "Paper", "Scissors"];
    const computerMove = choices[Math.floor(Math.random() * 3)];
    document.getElementById("computer-move").textContent = computerMove;

    if (playerMove === computerMove) {
        document.getElementById("result").textContent = "Tie!";
    } else if (
        (playerMove === "Rock" && computerMove === "Scissors") ||
        (playerMove === "Paper" && computerMove === "Rock") ||
        (playerMove === "Scissors" && computerMove === "Paper")
    ) {
        document.getElementById("result").textContent = "You Win!";
        playerScore++;
        document.getElementById("player-score").textContent = playerScore;
    } else {
        document.getElementById("result").textContent = "Computer Wins!";
        computerScore++;
        document.getElementById("computer-score").textContent = computerScore;
    }
};

document.getElementById("reset").onclick = function() {
    playerScore = 0;
    computerScore = 0;
    selectMove("");
    document.getElementById("player-score").textContent = "0";
    document.getElementById("computer-score").textContent = "0";
    document.getElementById("computer-move").textContent = "";
    document.getElementById("result").textContent = "";
};