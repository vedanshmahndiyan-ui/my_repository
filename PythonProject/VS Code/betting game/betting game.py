import random
import time
import tkinter as tk
from tkinter import messagebox
from collections import Counter

# =============================================================================
# CONFIGURATION — tweak all numbers here
# =============================================================================
MAX_BET          = 10000
MIN_BET          = 1
FREE_SPIN_MAX_BET = 15
ROWS             = 3
COLS             = 3

STANDARD_SYMBOLS = {"A": 2, "B": 4, "C": 6, "D": 8}
# RTP ~95.6% — see review notes for the math
SYMBOL_VALUES    = {"A": 400, "B": 5, "C": 12, "D": 3}

DAYS_PER_WEEK    = 7
TAX_RATE         = 0.20   # 20% of daily gross winnings
SAVINGS_INTEREST = 0.05   # 5% per day on savings (not crazy OP)

# Fonts
FONT_MAIN = ("Arial", 12)
FONT_BOLD = ("Arial", 12, "bold")
FONT_SLOT = ("Arial", 24, "bold")

# Colours
BG_DARK  = "#2C3E50"
BG_MID   = "#34495E"
BG_CELL  = "#ECF0F1"
COL_WIN  = "#2ECC71"
COL_PAIR = "#F1C40F"
COL_GOLD = "#F1C40F"
COL_GREY = "#BDC3C7"
COL_RED  = "#E74C3C"
COL_BLUE = "#2980B9"


# =============================================================================
# GAME STATE — all mutable data lives here, no scattered globals
# =============================================================================
class GameState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.balance: int          = 0
        self.initial_deposit: int  = 0
        self.session_start: float  = 0.0
        self.total_gross_earned: int = 0
        self.free_spins_left: int  = 0
        # --- Day / Week / Tax ---
        self.day: int              = 1
        self.savings: int          = 0
        self.daily_gross: int      = 0   # gross winnings this day (tax basis)
        self.weekly_tax_debt: int  = 0   # unpaid taxes carried this week
        self.total_days_survived: int = 0
        self.total_tax_paid: int   = 0

state = GameState()


# =============================================================================
# PURE GAME LOGIC (no Tkinter — easy to unit-test separately)
# =============================================================================
def build_spin(rows: int, cols: int) -> list:
    """
    Returns columns[col][row].
    Each column drawn WITHOUT replacement so same symbol can't appear
    twice in the same column vertically. Columns are independent.
    """
    pool = [sym for sym, count in STANDARD_SYMBOLS.items() for _ in range(count)]
    columns = []
    for _ in range(cols):
        remaining = pool[:]
        column    = []
        for _ in range(rows):
            pick = random.choice(remaining)
            remaining.remove(pick)
            column.append(pick)
        columns.append(column)
    return columns


def check_winnings(columns: list, active_lines: list, bet: int) -> tuple:
    """Returns (total_winnings, [(line_number_1based, symbol), ...])."""
    winnings = 0
    details  = []
    for row_idx in active_lines:
        row_syms = [columns[col][row_idx] for col in range(len(columns))]
        if len(set(row_syms)) == 1:
            sym      = row_syms[0]
            payout   = SYMBOL_VALUES[sym] * bet
            winnings += payout
            details.append((row_idx + 1, sym))
    return winnings, details


def validate_bet(bet_str: str, is_free: bool) -> tuple:
    """Returns (is_valid, error_message, capped_bet_value)."""
    if not bet_str.isdigit():
        return False, "Bet must be a whole number.", 0
    bet = int(bet_str)
    if is_free:
        bet = min(bet, FREE_SPIN_MAX_BET)
    if not (MIN_BET <= bet <= MAX_BET):
        return False, f"Bet must be between Rs.{MIN_BET} and Rs.{MAX_BET}.", 0
    return True, "", bet


def calculate_daily_tax() -> int:
    return int(state.daily_gross * TAX_RATE)


def apply_savings_interest() -> int:
    """Apply daily interest to savings. Returns interest earned."""
    if state.savings > 0:
        interest      = int(state.savings * SAVINGS_INTEREST)
        state.savings += interest
        return interest
    return 0


# =============================================================================
# MORNING DIALOG — shown at the start of each day
# =============================================================================
def show_morning_dialog(interest_earned: int):
    """Modal popup for depositing into savings at the start of a new day."""
    dlg = tk.Toplevel(root)
    dlg.title(f"Day {state.day} — Morning Briefing")
    dlg.geometry("400x360")
    dlg.configure(bg=BG_DARK)
    dlg.resizable(False, False)
    dlg.transient(root)
    dlg.grab_set()   # blocks main window until closed

    week_num = (state.total_days_survived // DAYS_PER_WEEK) + 1

    tk.Label(dlg,
             text=f"Good Morning!  Day {state.day} / {DAYS_PER_WEEK}  —  Week {week_num}",
             font=("Arial", 13, "bold"), fg=COL_GOLD, bg=BG_DARK).pack(pady=(18, 4))

    # Savings summary
    savings_frame = tk.Frame(dlg, bg=BG_MID, bd=2, relief="groove")
    savings_frame.pack(fill="x", padx=20, pady=6)

    if interest_earned > 0:
        tk.Label(savings_frame,
                 text=f"Overnight interest earned: +Rs.{interest_earned}",
                 font=FONT_MAIN, fg=COL_WIN, bg=BG_MID).pack(pady=(8, 2))

    tk.Label(savings_frame,
             text=f"Current Savings: Rs.{state.savings}   (earns {int(SAVINGS_INTEREST*100)}%/day)",
             font=FONT_BOLD, fg="white", bg=BG_MID).pack(pady=(2, 8))

    # Tax debt warning
    if state.weekly_tax_debt > 0:
        days_left = DAYS_PER_WEEK - state.day + 1
        warn = tk.Frame(dlg, bg="#922B21", bd=2, relief="groove")
        warn.pack(fill="x", padx=20, pady=4)
        tk.Label(warn,
                 text=f"  TAX DEBT: Rs.{state.weekly_tax_debt}  |  {days_left} day(s) left!  ",
                 font=FONT_BOLD, fg="white", bg="#922B21").pack(pady=6)

    # Deposit section
    tk.Label(dlg, text="Deposit from balance into savings (Rs.):",
             font=FONT_MAIN, fg=COL_GREY, bg=BG_DARK).pack(pady=(10, 2))

    deposit_var = tk.StringVar(value="0")
    tk.Entry(dlg, textvariable=deposit_var, font=FONT_MAIN,
             justify="center", width=12).pack()

    status_var = tk.StringVar()
    status_lbl = tk.Label(dlg, textvariable=status_var, font=("Arial", 10),
                          fg=COL_RED, bg=BG_DARK)
    status_lbl.pack(pady=2)

    def confirm():
        amt_str = deposit_var.get().strip()
        if not amt_str.isdigit():
            status_var.set("Enter a valid whole number.")
            return
        amt = int(amt_str)
        if amt > state.balance:
            status_var.set(f"You only have Rs.{state.balance} in balance!")
            return
        state.balance  -= amt
        state.savings  += amt
        dlg.destroy()

    btn_row = tk.Frame(dlg, bg=BG_DARK)
    btn_row.pack(pady=14)
    tk.Button(btn_row, text="Deposit & Start Day", font=FONT_BOLD,
              bg="#27AE60", fg="white", width=16, command=confirm).grid(row=0, column=0, padx=8)
    tk.Button(btn_row, text="Skip", font=FONT_BOLD,
              bg=BG_MID, fg="white", width=8,
              command=dlg.destroy).grid(row=0, column=1, padx=8)

    dlg.wait_window()   # pause main loop until dialog closes


# =============================================================================
# END-OF-DAY / WEEK LOGIC
# =============================================================================
def handle_end_day():
    """Called when player clicks 'End Day'."""
    tax = calculate_daily_tax()

    # Tax collector visit
    if tax > 0:
        _collect_tax(tax)
    else:
        messagebox.showinfo(
            "End of Day",
            f"Day {state.day} complete!\n\nNo gross winnings today = no tax owed. Lucky break!"
        )

    state.total_days_survived += 1

    # End of week check
    if state.day == DAYS_PER_WEEK:
        _handle_end_of_week()
        return

    # Advance to next day
    state.day         += 1
    state.daily_gross  = 0

    interest = apply_savings_interest()
    show_morning_dialog(interest)

    _refresh_all_labels()


def _collect_tax(tax: int):
    """
    Tax collector visits. If player can pay → deduct and celebrate.
    If they can't → add to weekly debt and warn them.
    """
    if state.balance >= tax:
        state.balance      -= tax
        state.total_tax_paid += tax
        messagebox.showinfo(
            "Tax Collector",
            f"*knock knock*\n\n"
            f"Agent: 'Evening. Gross winnings today: Rs.{state.daily_gross}'\n"
            f"Agent: 'Tax owed (20%): Rs.{tax}'\n\n"
            f"Rs.{tax} deducted. Have a good night!"
        )
    else:
        state.weekly_tax_debt += tax
        days_left              = DAYS_PER_WEEK - state.day
        messagebox.showwarning(
            "Tax Collector — Insufficient Funds!",
            f"*knock knock*\n\n"
            f"Agent: 'Evening. Tax owed: Rs.{tax}'\n"
            f"Agent: 'You only have Rs.{state.balance}... I'll be back.'\n\n"
            f"Rs.{tax} added to weekly debt!\n"
            f"Total debt this week: Rs.{state.weekly_tax_debt}\n"
            f"You have {days_left} day(s) left to settle up!"
        )


def _handle_end_of_week():
    """Day 7 is over. Check if the player can clear all weekly tax debt."""
    # Note: today's tax was already handled (paid or added to debt) in _collect_tax
    total_owed   = state.weekly_tax_debt
    total_assets = state.balance + state.savings

    if total_owed == 0:
        # Clean week — no debt at all
        _start_new_week()
        return

    if total_assets < total_owed:
        # Can't pay even combining balance + savings → GAME OVER
        _trigger_game_over(total_owed, total_assets)
        return

    # Player CAN pay if they choose — ask them
    choice = messagebox.askyesno(
        "Week-End Tax Settlement",
        f"Week complete! Time to settle your tax debt.\n\n"
        f"Total debt owed: Rs.{total_owed}\n"
        f"Your balance:    Rs.{state.balance}\n"
        f"Your savings:    Rs.{state.savings}\n"
        f"Total assets:    Rs.{total_assets}\n\n"
        f"Pay Rs.{total_owed} now and start a new week?"
    )

    if not choice:
        # Player refused to pay → game over
        _trigger_game_over(total_owed, total_assets)
        return

    # Deduct from balance first, then dip into savings if needed
    if state.balance >= total_owed:
        state.balance -= total_owed
    else:
        remainder      = total_owed - state.balance
        state.balance  = 0
        state.savings -= remainder

    state.total_tax_paid  += total_owed
    state.weekly_tax_debt  = 0
    _start_new_week()


def _start_new_week():
    week_num = (state.total_days_survived // DAYS_PER_WEEK) + 1
    messagebox.showinfo(
        f"Week {week_num - 1} Survived!",
        f"You made it through the week!\n\n"
        f"Total days survived: {state.total_days_survived}\n"
        f"Total tax paid ever: Rs.{state.total_tax_paid}\n"
        f"Balance:             Rs.{state.balance}\n"
        f"Savings:             Rs.{state.savings}\n\n"
        f"Week {week_num} begins. Stay lucky!"
    )
    state.day             = 1
    state.daily_gross     = 0
    state.weekly_tax_debt = 0

    interest = apply_savings_interest()
    show_morning_dialog(interest)
    _refresh_all_labels()


def _trigger_game_over(total_owed: int, total_assets: int):
    week_num = (state.total_days_survived // DAYS_PER_WEEK) + 1
    messagebox.showerror(
        "GAME OVER — Tax Default",
        f"The government has seized all your assets!\n\n"
        f"Weekly tax owed:   Rs.{total_owed}\n"
        f"Your total assets: Rs.{total_assets}\n\n"
        f"You couldn't pay your taxes. Better luck next time!\n\n"
        f"--- FINAL STATS ---\n"
        f"Weeks survived:      {week_num - 1}\n"
        f"Days survived:       {state.total_days_survived}\n"
        f"All-time winnings:   Rs.{state.total_gross_earned}\n"
        f"All-time tax paid:   Rs.{state.total_tax_paid}"
    )
    state.reset()
    game_frame.pack_forget()
    deposit_frame.pack(pady=50)


# =============================================================================
# GUI ACTION HANDLERS
# =============================================================================
def handle_deposit():
    amount_str = deposit_entry.get().strip()
    if not (amount_str.isdigit() and int(amount_str) > 0):
        messagebox.showerror("Error", "Please enter a valid positive deposit amount.")
        return

    state.reset()
    state.balance         = int(amount_str)
    state.initial_deposit = state.balance
    state.session_start   = time.time()

    deposit_frame.pack_forget()
    game_frame.pack(pady=10)
    _refresh_all_labels()
    update_spin_button_ui()

    # First morning briefing
    show_morning_dialog(0)
    update_balance_label()   # reflect any savings deposit from dialog


def handle_spin():
    # 1. Gather active lines
    active_lines = [i for i, var in enumerate([line1_var, line2_var, line3_var]) if var.get()]
    if not active_lines:
        messagebox.showwarning("Selection Error", "Select at least one line to bet on!")
        return

    # 2. Validate bet
    is_free = state.free_spins_left > 0
    ok, err, bet = validate_bet(bet_entry.get().strip(), is_free)
    if not ok:
        messagebox.showwarning("Input Error", err)
        return

    if is_free and int(bet_entry.get()) != bet:
        bet_entry.delete(0, tk.END)
        bet_entry.insert(0, str(bet))
        messagebox.showinfo("Bet Capped", f"Free spin bets capped at Rs.{FREE_SPIN_MAX_BET}/line.")

    total_bet = bet * len(active_lines)

    # 3. Check funds
    if not is_free and total_bet > state.balance:
        messagebox.showerror(
            "Insufficient Funds",
            f"Total bet Rs.{total_bet}, but balance is Rs.{state.balance}."
        )
        return

    # 4. Deduct / consume spin
    if is_free:
        state.free_spins_left -= 1
    else:
        state.balance -= total_bet

    # 5. Run spin
    slots = build_spin(ROWS, COLS)
    _render_grid(slots)

    # 6. Winnings
    winnings, details = check_winnings(slots, active_lines, bet)
    state.balance            += winnings
    state.total_gross_earned += winnings
    state.daily_gross        += winnings   # used for daily tax

    # 7. Free spin bonus
    if any(sym == "A" for _, sym in details):
        state.free_spins_left += 5
        messagebox.showinfo("Bonus!", "THREE 'A' SYMBOLS! You earned 5 FREE SPINS!")

    # 8. Update display
    _update_result_labels(bet, len(active_lines), total_bet, winnings, details, is_free)
    _refresh_all_labels()
    update_spin_button_ui()


# =============================================================================
# DISPLAY HELPERS
# =============================================================================
def _render_grid(slots: list):
    for r in range(ROWS):
        for c in range(COLS):
            grid_labels[r][c].config(text=slots[c][r], bg=BG_CELL)

    for r in range(ROWS):
        row_syms   = [slots[c][r] for c in range(COLS)]
        unique_cnt = len(set(row_syms))
        if unique_cnt == 1:
            for c in range(COLS):
                grid_labels[r][c].config(bg=COL_WIN)
        elif unique_cnt == 2:
            counts = Counter(row_syms)
            paired = {sym for sym, cnt in counts.items() if cnt == 2}
            for c in range(COLS):
                if slots[c][r] in paired:
                    grid_labels[r][c].config(bg=COL_PAIR)


def _update_result_labels(bet, num_lines, total_bet, winnings, details, is_free):
    cost_text = "Rs.0 (FREE)" if is_free else f"Rs.{total_bet}"
    bet_summary_label.config(
        text=f"Bet Rs.{bet} x {num_lines} line(s) — Cost: {cost_text}"
    )
    winnings_label.config(
        text=f"You won: Rs.{winnings}",
        fg=COL_WIN if winnings > 0 else "white",
    )
    winning_nums = [str(ln) for ln, _ in details]
    lines_label.config(
        text=f"Winning Lines: {', '.join(winning_nums)}" if winning_nums
             else "No winning lines this time."
    )


def update_spin_button_ui():
    if state.free_spins_left > 0:
        spin_btn.config(text=f"FREE SPIN ({state.free_spins_left} Left)", bg=COL_BLUE)
    else:
        spin_btn.config(text="SPIN", bg=COL_RED)


def _refresh_all_labels():
    update_balance_label()
    update_day_label()
    update_tax_label()


def update_balance_label():
    balance_label.config(
        text=f"Balance: Rs.{state.balance}     Savings: Rs.{state.savings}"
    )


def update_day_label():
    week_num   = (state.total_days_survived // DAYS_PER_WEEK) + 1
    total_days = state.total_days_survived + 1
    day_label.config(
        text=f"Week {week_num}   |   Day {state.day} of {DAYS_PER_WEEK}   |   Total Days: {total_days}"
    )


def update_tax_label():
    tax      = calculate_daily_tax()
    debt_txt = f"     DEBT: Rs.{state.weekly_tax_debt}" if state.weekly_tax_debt > 0 else ""
    tax_label.config(
        text=f"Today's Gross: Rs.{state.daily_gross}   |   Tax Due (20%): Rs.{tax}{debt_txt}",
        fg=COL_RED if state.weekly_tax_debt > 0 else COL_GREY,
    )


# =============================================================================
# GUI BUILD
# =============================================================================
root = tk.Tk()
root.title("Casino Slot Machine")
root.geometry("500x760")
root.configure(bg=BG_DARK)

# ── DEPOSIT SCREEN ─────────────────────────────────────────────────────────
deposit_frame = tk.Frame(root, bg=BG_DARK)
deposit_frame.pack(pady=50)

tk.Label(deposit_frame, text="Welcome to the Slot Machine!",
         font=("Arial", 16, "bold"), fg="white", bg=BG_DARK).pack(pady=10)
tk.Label(deposit_frame, text="Enter starting balance (Rs.):",
         font=FONT_MAIN, fg="white", bg=BG_DARK).pack()
deposit_entry = tk.Entry(deposit_frame, font=FONT_MAIN, justify="center")
deposit_entry.pack(pady=5)
deposit_entry.insert(0, "500")
tk.Button(deposit_frame, text="Start Game", font=FONT_BOLD,
          bg="#27AE60", fg="white", command=handle_deposit).pack(pady=10)


# ── MAIN GAME FRAME ────────────────────────────────────────────────────────
game_frame = tk.Frame(root, bg=BG_DARK)

# --- Info bar (day / week / tax) ---
info_bar = tk.Frame(game_frame, bg=BG_MID, bd=2, relief="groove")
info_bar.pack(fill="x", padx=10, pady=(6, 2))

day_label = tk.Label(info_bar, text="", font=FONT_BOLD, fg=COL_GOLD, bg=BG_MID)
day_label.pack(pady=(4, 0))

tax_label = tk.Label(info_bar, text="", font=("Arial", 10), fg=COL_GREY, bg=BG_MID)
tax_label.pack(pady=(0, 4))

# --- Balance ---
balance_label = tk.Label(game_frame, text="", font=("Arial", 13, "bold"),
                         fg=COL_GOLD, bg=BG_DARK)
balance_label.pack(pady=4)

# --- Slot grid ---
grid_frame = tk.Frame(game_frame, bg=BG_MID, bd=5, relief="groove")
grid_frame.pack(pady=6)

grid_labels = []
for r in range(ROWS):
    row_labels = []
    for c in range(COLS):
        lbl = tk.Label(grid_frame, text="-", font=FONT_SLOT,
                       width=4, height=1, bg=BG_CELL, fg=BG_DARK,
                       bd=2, relief="sunken")
        lbl.grid(row=r, column=c, padx=5, pady=5)
        row_labels.append(lbl)
    grid_labels.append(row_labels)

# --- Line checkboxes ---
checkbox_frame = tk.LabelFrame(game_frame, text=" Select Lines to Bet On ",
                                font=FONT_BOLD, fg="white", bg=BG_DARK, bd=2, padx=10, pady=5)
checkbox_frame.pack(pady=4)

line1_var = tk.BooleanVar(value=True)
line2_var = tk.BooleanVar(value=True)
line3_var = tk.BooleanVar(value=True)

cb_opts = dict(font=FONT_MAIN, fg="white", bg=BG_DARK,
               selectcolor=BG_MID, activebackground=BG_DARK, activeforeground="white")
tk.Checkbutton(checkbox_frame, text="Top Line",    variable=line1_var, **cb_opts).grid(row=0, column=0, padx=8)
tk.Checkbutton(checkbox_frame, text="Middle Line", variable=line2_var, **cb_opts).grid(row=0, column=1, padx=8)
tk.Checkbutton(checkbox_frame, text="Bottom Line", variable=line3_var, **cb_opts).grid(row=0, column=2, padx=8)

# --- Bet input ---
input_frame = tk.Frame(game_frame, bg=BG_DARK)
input_frame.pack(pady=4)

tk.Label(input_frame, text="Bet per Line (Rs.):",
         font=FONT_MAIN, fg="white", bg=BG_DARK).grid(row=0, column=0, padx=5, sticky="e")
bet_entry = tk.Entry(input_frame, font=FONT_MAIN, width=10, justify="center")
bet_entry.grid(row=0, column=1, padx=5, pady=5)
bet_entry.insert(0, "10")

# --- Buttons ---
spin_btn = tk.Button(game_frame, text="SPIN", font=("Arial", 14, "bold"),
                     bg=COL_RED, fg="white", width=20, command=handle_spin)
spin_btn.pack(pady=6)

end_day_btn = tk.Button(game_frame, text="End Day / Pay Taxes",
                         font=FONT_BOLD, bg="#7F8C8D", fg="white",
                         width=20, command=handle_end_day)
end_day_btn.pack(pady=3)

# --- Result labels ---
bet_summary_label = tk.Label(game_frame, text="", font=FONT_MAIN, fg=COL_GREY, bg=BG_DARK)
bet_summary_label.pack(pady=3)

winnings_label = tk.Label(game_frame, text="", font=("Arial", 14, "bold"),
                           fg="white", bg=BG_DARK)
winnings_label.pack(pady=2)

lines_label = tk.Label(game_frame, text="", font=FONT_MAIN, fg=COL_GREY, bg=BG_DARK)
lines_label.pack()

root.mainloop()