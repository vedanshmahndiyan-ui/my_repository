import random

MAX_LINES = 3
MAX_BET = 10000
MIN_BET = 1

ROWS = 3
COLS = 3

# How many of each symbol go into the "pool" (rarer = harder to land)
symbols_count = {
    "A": 2,
    "B": 4,
    "C": 6,
    "D": 8
}

# --- HOW FAIRNESS WORKS ---
# Each column independently picks from a pool of 20 symbols.
# Probability of symbol X landing on any row of any column = count(X) / 20
#
#   A: 2/20 = 10%  →  P(3 in a row) = 0.10^3 = 0.10%
#   B: 4/20 = 20%  →  P(3 in a row) = 0.20^3 = 0.80%
#   C: 6/20 = 30%  →  P(3 in a row) = 0.30^3 = 2.70%
#   D: 8/20 = 40%  →  P(3 in a row) = 0.40^3 = 6.40%
#
# For 100% RTP (perfectly fair), payout should = 1 / P(win):
#   A = 1/0.001 = 1000x,  B = 125x,  C = ~37x,  D = ~16x
#
# The old values (A=5, B=4, C=3, D=2) gave only 24.6% RTP — the house
# kept 75 cents of every rupee. That's worse than a rigged carnival game.
#
# These values give ~99% RTP (you get back ~₹99 per ₹100 bet on average):
symbol_values = {
    "A": 300,   # rare   → big payout
    "B": 40,    # uncommon
    "C": 9,     # common
    "D": 2      # very common → small payout
}
# RTP check: 300*0.001 + 40*0.008 + 9*0.027 + 2*0.064 = 0.991 = 99.1%


def check_winnings(columns, lines, bet, values):
    winnings = 0
    winning_lines = []
    for line in range(lines):
        symbol = columns[0][line]
        for column in columns:
            symbol_to_check = column[line]
            if symbol != symbol_to_check:
                break
        else:
            winnings += values[symbol] * bet
            winning_lines.append(line + 1)
    return winnings, winning_lines


def get_slot_machine_spin(rows, cols, symbols):
    all_symbols = []
    for symbol, symbol_count in symbols.items():
        for _ in range(symbol_count):
            all_symbols.append(symbol)

    columns = []
    for _ in range(cols):
        column = []  # FIX: was `columns = []` — that reset the outer list every loop!
        current_symbols = all_symbols[:]
        for _ in range(rows):
            value = random.choice(current_symbols)
            current_symbols.remove(value)
            column.append(value)
        columns.append(column)  # FIX: was `columns.append(columns)` — list appending itself!

    return columns


def print_slot_machine(columns):
    for row in range(len(columns[0])):
        for i, column in enumerate(columns):
            if i != len(columns) - 1:
                print(column[row], end=' | ')
            else:
                print(column[row], end='')
        print()


def deposit():
    while True:
        amount = input("Enter the amount you want to deposit: ₹")
        if amount.isdigit() and int(amount) > 0:
            return int(amount)
        else:
            print("Please enter a valid positive number.")
    # FIX: removed unreachable `return amount` that was here


def no_of_lines():
    while True:
        lines = input(f"Enter the number of lines you want to bet on (1-{MAX_LINES}): ")
        if lines.isdigit() and 1 <= int(lines) <= MAX_LINES:
            return int(lines)
        else:
            print("Please enter a valid number of lines.")
    # FIX: removed unreachable `return lines` that was here


def get_bet():
    while True:
        bet = input(f"Enter the amount you want to bet on each line (₹{MIN_BET}-₹{MAX_BET}): ₹")
        if bet.isdigit() and MIN_BET <= int(bet) <= MAX_BET:
            return int(bet)
        else:
            print(f"Please enter a valid bet amount between ₹{MIN_BET} and ₹{MAX_BET}.")
    # FIX: removed unreachable `return bet` that was here


def spin(balance):
    # FIX: removed `balance = deposit()` — was asking for a new deposit every single spin!
    lines = no_of_lines()
    while True:
        bet = get_bet()
        total_bet = bet * lines
        if total_bet > balance:
            print(f"You do not have enough balance to place this bet. Your current balance is ₹{balance}.")
        else:
            break

    print(f"\nYou are betting ₹{bet} on {lines} lines. Total bet: ₹{total_bet}.")

    slots = get_slot_machine_spin(ROWS, COLS, symbols_count)
    print_slot_machine(slots)

    winnings, winning_lines = check_winnings(slots, lines, bet, symbol_values)
    print(f"\nYou won ₹{winnings}.")
    if winning_lines:
        print("You won on lines:", *winning_lines)
    else:
        print("No winning lines this time. Better luck next spin!")

    return winnings - total_bet


def main():
    balance = deposit()
    while True:
        print(f"\nCurrent balance: ₹{balance}")
        answer = input("Press enter to play (q to quit): ")
        if answer == "q":
            break
        balance += spin(balance)

    print(f"\nYou left with ₹{balance}")


main()