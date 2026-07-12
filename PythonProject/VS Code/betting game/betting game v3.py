import random
import time
import tkinter as tk
from tkinter import messagebox
from collections import Counter

# =============================================================================
# CONFIGURATION — change numbers here, nothing else breaks
# =============================================================================

# --- Bank / Loans ---
# Interest charged per bank visit on outstanding loan (10% = 0.10).
# WARNING: the game state expects this as a float multiplier, not a percentage string.
BANK_LOAN_INTEREST = 0.10
# Preset loan amounts offered by the bank.
# Adjust brackets / count to change how many tiers appear in the bank dialog.
LOAN_OPTIONS = [50, 100, 200, 500, 1000]

# Friendly name map for daily-effect upgrades shown in the upgrade bar.
# Keys must match the upgrade "id" in ALL_UPGRADES; values are display strings.
UPGRADE_NAME_MAP = {
    "lucky_spin": "Lucky Spin",
    "tax_break": "Rent Break",
    "bonus_spins": "Bonus Round",
    "double_win": "Double Down",
    "tax_holiday": "Landlord Vanishes",
    "cash_back": "Cash Back",
    "quick_win": "Quick Win",
    "safe_spin": "Safe Spin",
    "roulette_rebate": "Roulette Rebate",
    "roulette_boost": "Wheel Heat",
}

# --- Betting limits ---
# Maximum bet per line (slot machine) or per spin (roulette).
# Keep as int. Raising this makes big wins possible but also speeds up bankruptcy.
MAX_BET = 1000000000000000000
# Minimum bet allowed. Should stay >= 1.
MIN_BET = 1
# Maximum bet allowed during a free spin. Caps the free-spin payout ceiling.
FREE_SPIN_MAX_BET = 15
# Slot grid dimensions. Must be >= 3 for standard 3-reel play.
ROWS = 3
COLS = 3
# Days in a week before new-week tax + devil events. 7 = standard weekly cycle.
DAYS_PER_WEEK = 7
# Cash required to unlock the roulette table from the room.
ROULETTE_UNLOCK_COST = 700

# --- Slot machine symbol pool & payouts ---
# Symbol weights: counts are how many copies of that symbol exist in the pool.
# Higher weight → symbol appears more often. Keep total sum reasonable for RTP.
STANDARD_SYMBOLS  = {"A": 2, "B": 4, "C": 6, "D": 8}
# Payout multipliers × bet for 3-of-a-kind on Game difficulty.
# A = rarest/highest payout, D = common/lowest payout.
GAME_SYMBOL_VALUES     = {"A": 430, "B": 7, "C": 13, "D": 4}
# Payout multipliers × bet for 3-of-a-kind on Realistic difficulty.
REALISTIC_SYMBOL_VALUES = {"A": 400, "B": 5, "C": 12, "D": 3}

# --- Roulette colour map ---
# Standard European roulette red numbers. Do not add 0 (it is green).
ROULETTE_RED_NUMS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
# Ordered list of bet labels. Position matters for the UI dropdown.
ROULETTE_BETS     = ["Red", "Black", "Even", "Odd", "1-18", "19-36", "Single Number"]
# Layout rows for the roulette board display. Must contain all numbers 1-36 in order.
ROULETTE_ROWS     = [[3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36],
                     [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35],
                     [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34]]
# Payout multipliers on Game difficulty. "outside" = red/black/even/odd/dozen.
# Values > true odds make the game easier; < true odds make it harder.
GAME_ROULETTE_PAYOUTS = {"outside": 2.1, "single": 38}
# Payout multipliers on Realistic difficulty. Close to true casino odds.
REALISTIC_ROULETTE_PAYOUTS = {"outside": 2, "single": 36}

# --- Tax / Rent ---
# Base rent paid at the end of each day in Week 1.
# Formula: BASE_DAILY_TAX + (week - 1) * TAX_WEEKLY_STEP
BASE_DAILY_TAX    = 10
# How much rent increases at the start of each new week.
TAX_WEEKLY_STEP   = 10

# --- Savings interest ---
# Daily interest rate for money sitting in savings (0.5% = 0.005).
# Permanent upgrades (bribery) add to this value.
BASE_SAVINGS_INTEREST = 0.005

# --- Starting deposit limits ---
# Player must deposit between these values to start a new run.
MIN_START = 500
MAX_START = 700

# --- Shop / Upgrade economy ---
# Base cost to reroll the shop (rolls 3 new random daily upgrades).
BASE_REROLL_COST         = 50
# Each reroll multiplies the next reroll cost by this factor.
REROLL_COST_MULTIPLIER   = 2.0
# Percentage price increase applied to all shop items per week (0.30 = +30%).
UPGRADE_WEEK_SCALE       = 0.30
# Daily price increase for locked upgrades (0.5% extra each day they sit locked).
LOCK_DAILY_INCREASE      = 0.005

# --- Fonts ---
# Base font family. Swap for "Courier New", "Consolas", "monospace", etc.
PIXEL_FACE = "Courier New"
# Tuple format used by Tkinter. Change size or style here to resize all text.
FONT_MAIN = (PIXEL_FACE, 12)
FONT_BOLD = (PIXEL_FACE, 12, "bold")
FONT_SLOT = (PIXEL_FACE, 24, "bold")
FONT_SMALL = (PIXEL_FACE, 9, "bold")

# --- Colours ---
# Main UI palette. All colours are hex strings. Change values to retheme.
BG_DARK   = "#090C10"  # deepest background
BG_MID    = "#151B22"  # panels / card backgrounds
BG_CELL   = "#F4E7C5"  # slot grid cell colour
COL_WIN   = "#2ECC71"  # win highlight green
COL_PAIR  = "#C9A227"  # pair-match gold
COL_GOLD  = "#D4AF37"  # primary accent gold
COL_GREY  = "#A8B0B8"  # muted text
COL_RED   = "#B91C1C"  # danger / roulette red
COL_BLUE  = "#245A73"  # info / player / roulette red
COL_GREEN = "#0F6B3E"  # action green / deposit
COL_PURP  = "#5B2A86"  # permanent upgrade purple
COL_ORNG  = "#B45309"  # warn orange / lock button
COL_BLACK = "#111111"  # roulette black


# =============================================================================
# UPGRADE CATALOGUE
# perm=False → effect lasts today only   perm=True → permanent stacking buff
# =============================================================================
ALL_UPGRADES = [
    # ---------- Daily ----------
    {
        "id": "lucky_spin",
        "name": "Lucky Spin",
        "desc": "Symbol 'A' count doubled in pool today",
        "base_price": 100,
        "perm": False,
    },
    {
        "id": "tax_break",
        "name": "Rent Break",
        "desc": "Tonight's rent reduced by 20%",
        "base_price": 150,
        "perm": False,
    },
    {
        "id": "bonus_spins",
        "name": "Bonus Round",
        "desc": "Gain 3 free spins right now",
        "base_price": 80,
        "perm": False,
    },
    {
        "id": "double_win",
        "name": "Double Down",
        "desc": "Your next win today pays 2×",
        "base_price": 200,
        "perm": False,
    },
    {
        "id": "tax_holiday",
        "name": "Landlord Vanishes",
        "desc": "Completely skip tonight's rent",
        "base_price": 380,
        "perm": False,
    },
    {
        "id": "cash_back",
        "name": "Cash Back",
        "desc": "Gain 10% of today's winnings back tomorrow",
        "base_price": 120,
        "perm": False,
    },
    {
        "id": "quick_win",
        "name": "Quick Win",
        "desc": "Instantly win Rs.100",
        "base_price": 90,
        "perm": False,
    },
    {
        "id": "safe_spin",
        "name": "Safe Spin",
        "desc": "Next spin guaranteed to at least break even",
        "base_price": 250,
        "perm": False,
    },
    {
        "id": "roulette_rebate",
        "name": "Roulette Rebate",
        "desc": "Your next roulette loss today refunds 50%",
        "base_price": 130,
        "perm": False,
    },
    {
        "id": "roulette_boost",
        "name": "Wheel Heat",
        "desc": "Your next roulette win today pays 1.5x",
        "base_price": 220,
        "perm": False,
    },
    # ---------- Permanent ----------
    {
        "id": "bribery",
        "name": "Bribery",
        "desc": "+0.5% bank interest rate forever (stackable)",
        "base_price": 500,
        "perm": True,
    },
    {
        "id": "tax_lawyer",
        "name": "Rent Lawyer",
        "desc": "-5% to all future rent bills (stackable)",
        "base_price": 750,
        "perm": True,
    },
    {
        "id": "lucky_charm",
        "name": "Lucky Charm",
        "desc": "Permanently add 1 to 'A' symbol in pool",
        "base_price": 900,
        "perm": True,
    },
    {
        "id": "high_roller",
        "name": "High Roller",
        "desc": "Jackpot ('A' win) gives +3 extra free spins",
        "base_price": 600,
        "perm": True,
    },
    {
        "id": "better_odds",
        "name": "Better Odds",
        "desc": "+1 'B' symbol in pool permanently",
        "base_price": 550,
        "perm": True,
    },
    {
        "id": "insurance",
        "name": "Insurance",
        "desc": "Lose only 50% on losing spins (stackable)",
        "base_price": 650,
        "perm": True,
    },
    {
        "id": "hot_streak",
        "name": "Hot Streak",
        "desc": "+25% payout on all wins forever (stackable)",
        "base_price": 800,
        "perm": True,
    },
    {
        "id": "wheel_bias",
        "name": "Wheel Bias",
        "desc": "+10% payout on roulette wins forever (stackable)",
        "base_price": 700,
        "perm": True,
    },
]


# =============================================================================
# GAME STATE
# =============================================================================
class GameState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.balance: int            = 0
        self.savings: int            = 0
        self.bank_loan: int          = 0
        self.session_start: float    = 0.0
        self.total_gross_earned: int = 0
        self.free_spins_left: int    = 0
        self.current_game: str       = "room"
        self.difficulty: str         = "game"
        self.roulette_unlocked: bool = False
        self.player_x: int           = 185
        self.player_y: int           = 145

        # Calendar
        self.day: int                = 1
        self.week_num: int           = 1
        self.total_days_survived: int = 0
        self.weekly_tax_debt: int    = 0
        self.total_tax_paid: int     = 0

        # Upgrades
        self.perm_upgrades: dict     = {}   # {id: stack_count}
        self.locked_upgrades: list   = []   # [{upgrade, days_locked, current_price}]
        self.daily_effects: dict     = {}   # {id: True}
        self.double_win_used: bool   = False
        self.roulette_rebate_used: bool = False
        self.roulette_boost_used: bool = False

        # Shop state (reset each morning)
        self.reroll_cost: int        = BASE_REROLL_COST

    # --- Derived values ---

    def savings_rate(self) -> float:
        return BASE_SAVINGS_INTEREST + self.perm_upgrades.get("bribery", 0) * 0.005

    def daily_tax(self) -> int:
        base = BASE_DAILY_TAX + (self.week_num - 1) * TAX_WEEKLY_STEP
        reduction = self.perm_upgrades.get("tax_lawyer", 0) * 0.05
        if self.daily_effects.get("tax_break"):
            reduction += 0.20
        if self.daily_effects.get("tax_holiday"):
            return 0
        return max(1, int(base * (1 - reduction)))

    def scaled_price(self, base: int) -> int:
        return int(base * (1 + UPGRADE_WEEK_SCALE * (self.week_num - 1)))

    def symbol_pool(self) -> list:
        pool_dict = dict(STANDARD_SYMBOLS)
        pool_dict["A"] += self.perm_upgrades.get("lucky_charm", 0)
        if self.daily_effects.get("lucky_spin"):
            pool_dict["A"] *= 2
        return [sym for sym, cnt in pool_dict.items() for _ in range(cnt)]

    def is_bankrupt(self) -> bool:
        return self.balance <= 0 and self.savings <= 0


state = GameState()


# =============================================================================
# PURE GAME LOGIC
# =============================================================================
def build_spin() -> list:
    pool = state.symbol_pool()
    return [random.sample(pool, ROWS) for _ in range(COLS)]


def check_winnings(columns: list, active_lines: list, bet: int) -> tuple:
    winnings, details = 0, []
    symbol_values = GAME_SYMBOL_VALUES if state.difficulty == "game" else REALISTIC_SYMBOL_VALUES
    for row in active_lines:
        syms = [columns[c][row] for c in range(COLS)]
        if len(set(syms)) == 1:
            sym    = syms[0]
            payout = symbol_values[sym] * bet
            if state.daily_effects.get("double_win") and not state.double_win_used:
                payout *= 2
                state.double_win_used = True
            winnings += payout
            details.append((row + 1, sym))
    return winnings, details


def validate_bet(bet_str: str, is_free: bool) -> tuple:
    if not bet_str.isdigit():
        return False, "Bet must be a whole number.", 0
    bet = int(bet_str)
    if is_free:
        bet = min(bet, FREE_SPIN_MAX_BET)
    if not (MIN_BET <= bet <= MAX_BET):
        return False, f"Bet must be Rs.{MIN_BET}–Rs.{MAX_BET}.", 0
    return True, "", bet


def spin_roulette(bet_type: str, chosen_number: int | None, bet: int) -> tuple:
    number = random.randint(0, 36)
    colour = roulette_colour(number)
    payout_multiplier = 0
    roulette_payouts = GAME_ROULETTE_PAYOUTS if state.difficulty == "game" else REALISTIC_ROULETTE_PAYOUTS

    if bet_type == "Single Number" and chosen_number == number:
        payout_multiplier = roulette_payouts["single"]
    else:
        check = {
            "Red": colour == "Red",
            "Black": colour == "Black",
            "Even": number != 0 and number % 2 == 0,
            "Odd": number % 2 == 1,
            "1-18": 1 <= number <= 18,
            "19-36": 19 <= number <= 36,
        }.get(bet_type, False)
        if check:
            payout_multiplier = roulette_payouts["outside"]

    winnings = int(bet * payout_multiplier)
    if winnings > 0:
        winnings = int(winnings * (1 + state.perm_upgrades.get("wheel_bias", 0) * 0.10))
    if winnings > 0 and state.daily_effects.get("roulette_boost") and not state.roulette_boost_used:
        winnings = int(winnings * 1.5)
        state.roulette_boost_used = True
    if winnings > 0 and state.daily_effects.get("double_win") and not state.double_win_used:
        winnings *= 2
        state.double_win_used = True

    return number, colour, winnings, payout_multiplier


def roulette_colour(number: int) -> str:
    if number == 0:
        return "Green"
    return "Red" if number in ROULETTE_RED_NUMS else "Black"


def apply_upgrade(uid: str):
    perm_ids = {"bribery", "tax_lawyer", "lucky_charm", "high_roller", "wheel_bias"}
    if uid in perm_ids:
        state.perm_upgrades[uid] = state.perm_upgrades.get(uid, 0) + 1
    elif uid == "bonus_spins":
        state.free_spins_left += 3
    else:
        state.daily_effects[uid] = True


# =============================================================================
# MORNING SEQUENCE — Bank dialog → Shop dialog
# =============================================================================
def run_morning():
    """Called at the start of every new day."""
    # Age locked upgrades from PREVIOUS days (not items locked this session yet)
    for lu in state.locked_upgrades:
        lu["days_locked"]   += 1
        lu["current_price"]  = int(lu["current_price"] * (1 + LOCK_DAILY_INCREASE))

    # Apply savings interest
    interest_earned = 0
    if state.savings > 0:
        interest          = int(state.savings * state.savings_rate())
        state.savings    += interest
        interest_earned   = interest

    state.reroll_cost = BASE_REROLL_COST   # reset shop reroll each morning

    show_morning_bank_dialog(interest_earned)
    show_shop_dialog()
    refresh_ui()


def show_morning_bank_dialog(interest: int):
    if not root.winfo_exists():
        return
    dlg = tk.Toplevel(root)
    dlg.title(f"Week {state.week_num}  Day {state.day} - Rotten Morning")
    dlg.geometry("500x430")
    dlg.configure(bg=BG_DARK)
    dlg.resizable(False, False)
    dlg.transient(root)
    dlg.grab_set()

    tk.Label(dlg,
             text=f"OLD WOODEN HOUSE - WEEK {state.week_num} / DAY {state.day}",
             font=(PIXEL_FACE, 13, "bold"), fg=COL_GOLD, bg=BG_DARK).pack(pady=(16, 6))
    tk.Label(dlg,
             text="Rain leaks through the roof. The slot machine hums in the corner.",
             font=FONT_MAIN, fg=COL_GREY, bg=BG_DARK, wraplength=440).pack(pady=(0, 8))

    # Savings summary box
    sav = tk.Frame(dlg, bg=BG_MID, bd=2, relief="groove")
    sav.pack(fill="x", padx=20, pady=4)
    if interest > 0:
        tk.Label(sav, text=f"Interest earned overnight: +Rs.{interest}",
                 font=FONT_MAIN, fg=COL_WIN, bg=BG_MID).pack(pady=(8, 0))
    tk.Label(sav,
             text=f"Savings: Rs.{state.savings}   ({state.savings_rate()*100:.1f}% / day)",
             font=FONT_BOLD, fg="white", bg=BG_MID).pack(pady=3)
    tk.Label(sav, text=f"Balance: Rs.{state.balance}",
             font=FONT_MAIN, fg=COL_GREY, bg=BG_MID).pack(pady=(0, 8))

    # Rent debt warning
    if state.weekly_tax_debt > 0:
        days_left = DAYS_PER_WEEK - state.day + 1
        wf = tk.Frame(dlg, bg="#922B21", bd=2, relief="groove")
        wf.pack(fill="x", padx=20, pady=4)
        tk.Label(wf,
                 text=f"  RENT DEBT: Rs.{state.weekly_tax_debt}   {days_left} day(s) left!  ",
                 font=FONT_BOLD, fg="white", bg="#922B21").pack(pady=6)

    # Amount entry
    tk.Label(dlg, text="Amount (Rs.):", font=FONT_MAIN, fg=COL_GREY, bg=BG_DARK).pack(pady=(12, 2))
    amt_var    = tk.StringVar(value="0")
    status_var = tk.StringVar()
    tk.Entry(dlg, textvariable=amt_var, font=FONT_MAIN, justify="center", width=14).pack()
    tk.Label(dlg, textvariable=status_var, font=FONT_SMALL, fg=COL_RED, bg=BG_DARK).pack(pady=2)

    def deposit():
        s = amt_var.get().strip()
        if not s.isdigit():
            status_var.set("Enter a whole number.")
            return
        a = int(s)
        if a > state.balance:
            status_var.set(f"Only Rs.{state.balance} in balance!")
            return
        state.balance -= a
        state.savings += a
        status_var.set(f"Deposited Rs.{a}. Savings → Rs.{state.savings}")
        amt_var.set("0")

    def withdraw():
        s = amt_var.get().strip()
        if not s.isdigit():
            status_var.set("Enter a whole number.")
            return
        a = int(s)
        if a > state.savings:
            status_var.set(f"Only Rs.{state.savings} in savings!")
            return
        state.savings -= a
        state.balance += a
        status_var.set(f"Withdrew Rs.{a}. Balance → Rs.{state.balance}")
        amt_var.set("0")

    row = tk.Frame(dlg, bg=BG_DARK)
    row.pack(pady=12)
    tk.Button(row, text="Deposit",  font=FONT_BOLD, bg=COL_GREEN, fg="white",
              width=10, command=deposit).grid(row=0, column=0, padx=6)
    tk.Button(row, text="Withdraw", font=FONT_BOLD, bg=COL_BLUE,  fg="white",
              width=10, command=withdraw).grid(row=0, column=1, padx=6)
    tk.Button(row, text="Done",     font=FONT_BOLD, bg=BG_MID,    fg="white",
              width=8,  command=dlg.destroy).grid(row=0, column=2, padx=6)

    dlg.wait_window()


def show_shop_dialog():
    if not root.winfo_exists():
        return
    dlg = tk.Toplevel(root)
    dlg.title(f"Week {state.week_num}  Day {state.day} - Devil's Bargain")
    dlg.geometry("540x640")
    dlg.configure(bg=BG_DARK)
    dlg.resizable(False, False)
    dlg.transient(root)
    dlg.grab_set()

    # --- Build slot list ---
    # Locked upgrades fill first (max 3 total slots shown)
    locked_ids = {lu["upgrade"]["id"] for lu in state.locked_upgrades}
    available  = [u for u in ALL_UPGRADES if u["id"] not in locked_ids]
    num_locked = min(len(state.locked_upgrades), 3)
    num_rand   = max(0, 3 - num_locked)
    rand_picks = random.sample(available, min(num_rand, len(available)))

    shop_slots = []
    for lu in state.locked_upgrades[:num_locked]:
        shop_slots.append({
            "upgrade":    lu["upgrade"],
            "price":      lu["current_price"],
            "is_locked":  True,
            "lock_entry": lu,
        })
    for u in rand_picks:
        shop_slots.append({
            "upgrade":    u,
            "price":      state.scaled_price(u["base_price"]),
            "is_locked":  False,
            "lock_entry": None,
        })

    # --- Header ---
    tk.Label(dlg, text="THE DEVIL'S BARGAIN", font=(PIXEL_FACE, 14, "bold"),
             fg=COL_GOLD, bg=BG_DARK).pack(pady=(12, 2))
    tk.Label(dlg,
             text="The devil smiles at your new habit. He lays three offers on the warped floorboards.",
             font=FONT_MAIN, fg="#C084FC", bg=BG_DARK, wraplength=490).pack(pady=(0, 6))

    bal_var = tk.StringVar(value=f"Balance: Rs.{state.balance}")
    tk.Label(dlg, textvariable=bal_var, font=FONT_MAIN, fg=COL_GREY, bg=BG_DARK).pack()

    status_var = tk.StringVar()
    tk.Label(dlg, textvariable=status_var, font=FONT_SMALL,
             fg=COL_GOLD, bg=BG_DARK).pack(pady=2)

    cards_frame = tk.Frame(dlg, bg=BG_DARK)
    cards_frame.pack(fill="x", padx=15, pady=4)

    reroll_var = tk.StringVar()

    def update_reroll_label():
        reroll_var.set(f"Reroll   Rs.{state.reroll_cost}")

    def build_cards():
        for w in cards_frame.winfo_children():
            w.destroy()

        locked_slots = [s for s in shop_slots if s["is_locked"]]
        available_slots = [s for s in shop_slots if not s["is_locked"]]

        def make_buy(idx, slot_list):
            def _buy():
                s = slot_list[idx]
                if state.balance <= s["price"]:
                    status_var.set("Not a good financial decision (anyways you didn't make any to start with)")
                    return
                state.balance -= s["price"]
                if s["is_locked"] and s["lock_entry"] in state.locked_upgrades:
                    state.locked_upgrades.remove(s["lock_entry"])
                apply_upgrade(s["upgrade"]["id"])
                status_var.set(f"Bought '{s['upgrade']['name']}'!")
                shop_slots.remove(s)
                bal_var.set(f"Balance: Rs.{state.balance}")
                refresh_ui()
                root.update_idletasks()
                build_cards()
            return _buy

        def make_lock(idx, slot_list):
            def _lock():
                s = slot_list[idx]
                if s["is_locked"]:
                    status_var.set("Already locked!")
                    return
                entry = {"upgrade": s["upgrade"], "days_locked": 0,
                         "current_price": s["price"]}
                state.locked_upgrades.append(entry)
                s["is_locked"]  = True
                s["lock_entry"] = entry
                shop_slots.remove(s)
                locked_slots.append(s)
                status_var.set(
                    f"Locked '{s['upgrade']['name']}'. Price +0.5%/day.")
                refresh_ui()
                root.update_idletasks()
                build_cards()
            return _lock

        def build_card(slot, idx, slot_list, show_lock=False):
            upg      = slot["upgrade"]
            price    = slot["price"]
            is_perm  = upg["perm"]
            is_locked = slot["is_locked"]

            card = tk.Frame(cards_frame, bg=BG_MID, bd=2, relief="groove")
            card.pack(fill="x", pady=3)

            hdr_bg = COL_PURP if is_perm else COL_BLUE
            badge  = "PERM" if is_perm else "DAILY"
            days = slot["lock_entry"]["days_locked"] if slot["lock_entry"] else 0
            title = f"  [{badge}] {'LOCKED · ' if is_locked else ''}{upg['name']}"
            if is_locked:
                title += f"  ({days}d locked, +0.5%/day)"
            tk.Label(card, text=title, font=FONT_BOLD, fg="white", bg=hdr_bg, anchor="w").pack(fill="x")
            tk.Label(card, text=f"  {upg['desc']}", font=FONT_MAIN, fg=COL_GREY, bg=BG_MID, anchor="w").pack(fill="x")

            btn_row = tk.Frame(card, bg=BG_MID)
            btn_row.pack(pady=4)

            can_afford = state.balance > price
            buy_bg     = COL_GREEN if can_afford else "#566573"

            tk.Button(btn_row, text=f"Buy  Rs.{price}", font=FONT_BOLD,
                      bg=buy_bg, fg="white", width=14,
                      command=make_buy(idx, slot_list)).grid(row=0, column=0, padx=6)

            if show_lock:
                tk.Button(btn_row, text="Lock", font=FONT_BOLD,
                          bg=COL_ORNG, fg="white", width=6,
                          command=make_lock(idx, slot_list)).grid(row=0, column=1, padx=4)

        if locked_slots:
            header = tk.Label(cards_frame, text="[LOCKED BARGAINS]",
                             font=FONT_BOLD, fg=COL_GOLD, bg=BG_DARK, anchor="w")
            header.pack(fill="x", pady=(8, 4))

        for i, slot in enumerate(locked_slots):
            build_card(slot, i, locked_slots, show_lock=False)

        if available_slots:
            header = tk.Label(cards_frame, text="[TONIGHT'S OFFERS]",
                             font=FONT_BOLD, fg=COL_ORNG, bg=BG_DARK, anchor="w")
            header.pack(fill="x", pady=(12, 4))

        for i, slot in enumerate(available_slots):
            build_card(slot, i, available_slots, show_lock=True)

    build_cards()
    update_reroll_label()

    # Bottom row
    bottom = tk.Frame(dlg, bg=BG_DARK)
    bottom.pack(pady=10)

    def reroll():
        if state.balance <= state.reroll_cost:
            status_var.set("Not a good financial decision (anyways you didn't make any to start with)")
            return
        state.balance  -= state.reroll_cost
        state.reroll_cost = int(state.reroll_cost * REROLL_COST_MULTIPLIER)
        bal_var.set(f"Balance: Rs.{state.balance}")
        update_reroll_label()
        refresh_ui()

        locked_slot_ids = {s["upgrade"]["id"] for s in shop_slots if s["is_locked"]}
        avail_new       = [u for u in ALL_UPGRADES if u["id"] not in locked_slot_ids]
        n_new           = sum(1 for s in shop_slots if not s["is_locked"])
        new_picks       = random.sample(avail_new, min(n_new, len(avail_new)))

        kept   = [s for s in shop_slots if s["is_locked"]]
        shop_slots.clear()
        shop_slots.extend(kept)
        for u in new_picks:
            shop_slots.append({"upgrade": u, "price": state.scaled_price(u["base_price"]),
                                "is_locked": False, "lock_entry": None})

        status_var.set(f"Rerolled! Next reroll Rs.{state.reroll_cost}")
        build_cards()

    tk.Button(bottom, textvariable=reroll_var, font=FONT_BOLD,
              bg=COL_PURP, fg="white", width=16, command=reroll).grid(row=0, column=0, padx=8)
    tk.Button(bottom, text="Refuse", font=FONT_BOLD,
              bg=BG_MID, fg="white", width=10, command=dlg.destroy).grid(row=0, column=1, padx=8)

    dlg.wait_window()


def show_outside_menu():
    if not root.winfo_exists():
        return
    dlg = tk.Toplevel(root)
    dlg.title("Outside")
    dlg.geometry("420x320")
    dlg.configure(bg="#1A2E1A")
    dlg.resizable(False, False)
    dlg.transient(root)
    dlg.grab_set()

    tk.Label(dlg, text="COBBLED STREET", font=(PIXEL_FACE, 16, "bold"),
             fg=COL_GOLD, bg="#1A2E1A").pack(pady=(20, 6))
    tk.Label(dlg, text="Rain hammers the cobblestones. The bank rises ahead, stone and iron.",
             font=FONT_MAIN, fg=COL_GREY, bg="#1A2E1A", wraplength=380).pack(pady=(0, 16))

    # Bank icon / symbol
    bank_frame = tk.Frame(dlg, bg="#0F1F0F", bd=2, relief="groove")
    bank_frame.pack(pady=10)
    tk.Label(bank_frame, text="🏦", font=("Segoe UI Emoji", 40), bg="#0F1F0F").pack(pady=10)
    tk.Label(bank_frame, text="THE LEDGER & STONE", font=(PIXEL_FACE, 12, "bold"),
             fg=COL_GOLD, bg="#0F1F0F").pack(pady=(0, 10))

    def enter_bank():
        dlg.destroy()
        show_bank_office()

    tk.Button(dlg, text="Enter Bank", font=FONT_BOLD, bg=COL_GREEN, fg="white",
              width=14, command=enter_bank).pack(pady=8)
    tk.Button(dlg, text="Return Inside", font=FONT_BOLD, bg=BG_MID, fg="white",
              width=14, command=dlg.destroy).pack(pady=4)

    dlg.wait_window()


def show_bank_office():
    if not root.winfo_exists():
        return
    dlg = tk.Toplevel(root)
    dlg.title("The Ledger & Stone — Bank")
    dlg.geometry("500x620")
    dlg.configure(bg="#0B1A14")
    dlg.resizable(False, False)
    dlg.transient(root)
    dlg.grab_set()

    # Header
    tk.Label(dlg, text="THE LEDGER & STONE", font=(PIXEL_FACE, 14, "bold"),
             fg=COL_GOLD, bg="#0B1A14").pack(pady=(16, 4))
    tk.Label(dlg, text="Estd. 1847  ·  Licensed Moneylender",
             font=FONT_SMALL, fg=COL_GREY, bg="#0B1A14").pack(pady=(0, 10))

    # Teller window / agent area
    tw = tk.Frame(dlg, bg="#051008", bd=3, relief="ridge")
    tw.pack(fill="x", padx=30, pady=8)

    tk.Label(tw, text="👔", font=("Segoe UI Emoji", 32), bg="#051008").pack(pady=(10, 4))
    tk.Label(tw, text="Agent Harrow", font=(PIXEL_FACE, 12, "bold"),
             fg="white", bg="#051008").pack()
    tk.Label(tw, text='"Your savings impress us. How may we serve?"',
             font=FONT_MAIN, fg=COL_GREY, bg="#051008", wraplength=420).pack(pady=6)

    # Account summary
    summary = tk.Frame(dlg, bg="#0F2818", bd=2, relief="groove")
    summary.pack(fill="x", padx=30, pady=8)

    savings_lbl = tk.Label(summary, text=f"Savings: Rs.{state.savings}",
                           font=FONT_BOLD, fg="white", bg="#0F2818")
    savings_lbl.pack(pady=4, anchor="w", padx=10)

    loan_lbl = tk.Label(summary, text=f"Outstanding Loan: Rs.{state.bank_loan}",
                        font=FONT_BOLD, fg=COL_RED if state.bank_loan > 0 else "white", bg="#0F2818")
    loan_lbl.pack(pady=4, anchor="w", padx=10)

    rate = BANK_LOAN_INTEREST * 100
    rate_lbl = tk.Label(summary, text=f"Current Interest Rate: {rate:.0f}% (per visit)",
                        font=FONT_MAIN, fg=COL_GREY, bg="#0F2818")
    rate_lbl.pack(pady=4, anchor="w", padx=10)

    status_var = tk.StringVar()
    status_lbl = tk.Label(dlg, textvariable=status_var, font=FONT_SMALL,
                          fg=COL_RED, bg="#0B1A14")
    status_lbl.pack(pady=4)

    # Loan option count slider
    slider_frame = tk.Frame(dlg, bg="#0B1A14")
    slider_frame.pack(pady=4)
    tk.Label(slider_frame, text="Loan options visible:", font=FONT_MAIN, fg="white", bg="#0B1A14").pack(side="left", padx=10)
    loan_count_var = tk.IntVar(value=len(LOAN_OPTIONS))
    loan_count_slider = tk.Scale(slider_frame, from_=1, to=len(LOAN_OPTIONS), orient="horizontal",
                                 variable=loan_count_var, bg="#0B1A14", fg=COL_GOLD, highlightthickness=0,
                                 troughcolor=BG_MID, activebackground=COL_GOLD, length=180)
    loan_count_slider.pack(side="left", padx=10)

    def refresh_summary():
        savings_lbl.config(text=f"Savings: Rs.{state.savings}")
        loan_lbl.config(text=f"Outstanding Loan: Rs.{state.bank_loan}",
                        fg=COL_RED if state.bank_loan > 0 else "white")

    def apply_interest():
        if state.bank_loan > 0:
            interest_add = int(state.bank_loan * BANK_LOAN_INTEREST)
            state.bank_loan += interest_add
            state.balance += interest_add
            status_var.set(f"Interest applied: +Rs.{interest_add} added to balance")
            refresh_summary()

    def take_loan(amount):
        if amount <= 0:
            return
        if state.savings > 0 and amount > state.savings * 4:
            status_var.set("The agent shakes his head. 'Your savings do not support that sum.'")
            return
        state.bank_loan += amount
        state.balance += amount
        status_var.set(f"Loan taken: Rs.{amount}. Balance updated.")
        refresh_summary()

    def repay_loan(amount):
        if amount <= 0:
            return
        if amount > state.balance:
            status_var.set("You do not have enough cash on hand.")
            return
        if amount > state.bank_loan:
            amount = state.bank_loan
        state.balance -= amount
        state.bank_loan -= amount
        status_var.set(f"Repaid Rs.{amount}. Remaining loan: Rs.{state.bank_loan}")
        refresh_summary()

    def repay_all():
        if state.bank_loan == 0:
            status_var.set("You owe nothing.")
            return
        if state.bank_loan > state.balance:
            status_var.set("Not enough cash to clear the debt.")
            return
        state.balance -= state.bank_loan
        repaid = state.bank_loan
        state.bank_loan = 0
        status_var.set(f"Debt cleared. Rs.{repaid} paid.")
        refresh_summary()

    def leave_bank():
        dlg.destroy()
        refresh_ui()

    def build_loan_buttons():
        for w in scroll_frame.winfo_children():
            w.destroy()
        count = loan_count_var.get()
        for amt in LOAN_OPTIONS[:count]:
            can_take = state.savings == 0 or amt <= state.savings * 4
            tk.Button(scroll_frame, text=f"Rs.{amt}", font=FONT_MAIN,
                      bg=COL_BLUE if can_take else "#3A3A3A", fg="white",
                      width=20, command=lambda a=amt: take_loan(a)).pack(pady=2)

    loan_count_slider.config(command=lambda _: build_loan_buttons())

    # Scrollable loan button container
    tk.Label(btn_frame, text="Take a Loan:", font=FONT_BOLD, fg="white", bg="#0B1A14").pack(anchor="w", padx=20)

    canvas_frame = tk.Frame(btn_frame, bg="#0B1A14")
    canvas_frame.pack(pady=4, fill="both", expand=True)

    loan_canvas = tk.Canvas(canvas_frame, bg="#0B1A14", highlightthickness=0, height=160)
    loan_scroll = tk.Scrollbar(canvas_frame, orient="vertical", command=loan_canvas.yview)
    scroll_frame = tk.Frame(loan_canvas, bg="#0B1A14")

    scroll_frame.bind("<Configure>", lambda e: loan_canvas.configure(scrollregion=loan_canvas.bbox("all")))
    loan_canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    loan_canvas.configure(yscrollcommand=loan_scroll.set)

    loan_canvas.pack(side="left", fill="both", expand=True, padx=(20, 0))
    loan_scroll.pack(side="right", fill="y")

    def _on_mousewheel(event):
        loan_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    loan_canvas.bind_all("<MouseWheel>", _on_mousewheel)
    build_loan_buttons()

    tk.Label(btn_frame, text="Repay Loan:", font=FONT_BOLD, fg="white", bg="#0B1A14").pack(anchor="w", padx=20, pady=(8, 0))
    repay_row = tk.Frame(btn_frame, bg="#0B1A14")
    repay_row.pack(pady=4)
    tk.Button(repay_row, text="Half", font=FONT_MAIN, bg=COL_GREEN, fg="white",
              width=8, command=lambda: repay_loan(max(1, state.bank_loan // 2))).pack(side="left", padx=4)
    tk.Button(repay_row, text="All", font=FONT_MAIN, bg=COL_GREEN, fg="white",
              width=8, command=repay_all).pack(side="left", padx=4)

    custom_frame = tk.Frame(btn_frame, bg="#0B1A14")
    custom_frame.pack(pady=6)
    tk.Label(custom_frame, text="Custom:", font=FONT_MAIN, fg="white", bg="#0B1A14").pack(side="left", padx=4)
    repay_entry = tk.Entry(custom_frame, font=FONT_MAIN, width=10, justify="center")
    repay_entry.pack(side="left", padx=4)
    repay_entry.bind("<Return>", lambda e: repay_loan(int(repay_entry.get()) if repay_entry.get().isdigit() else 0))
    repay_entry.bind("<Escape>", lambda e: dlg.destroy())
    tk.Button(custom_frame, text="Pay", font=FONT_BOLD, bg=COL_GREEN, fg="white",
              width=6, command=lambda: repay_loan(int(repay_entry.get()) if repay_entry.get().isdigit() else 0)).pack(side="left", padx=4)

    tk.Button(dlg, text="Apply Interest & Leave", font=FONT_BOLD, bg=COL_ORNG, fg="white",
              width=20, command=apply_interest).pack(pady=6)
    tk.Button(dlg, text="Leave Bank", font=FONT_BOLD, bg=BG_MID, fg="white",
              width=14, command=leave_bank).pack(pady=4)

    dlg.wait_window()


def handle_end_day():
    # Bankruptcy check before collecting tax
    if state.balance == 0 and state.savings == 0:
        _game_over_broke()
        return

    tax = state.daily_tax()

    if tax == 0:
        messagebox.showinfo(
            "Midnight Visit",
            "The devil taps one claw against the window.\n\n"
            "'No rent tonight? How useful. Keep playing.'"
        )
    elif state.balance >= tax:
        state.balance        -= tax
        state.total_tax_paid += tax
        messagebox.showinfo(
            "Rent Collector",
            f"*three dull knocks on rotten wood*\n\n"
            f"Rent due for Week {state.week_num}: Rs.{tax}\n"
            f"Rs.{tax} paid from the day's cash.\n\n"
            f"The devil waits behind the collector, pleased.\n"
            f"'Good. Desperation makes the wheel spin sweeter.'"
        )
    else:
        state.weekly_tax_debt += tax
        days_left = DAYS_PER_WEEK - state.day
        messagebox.showwarning(
            "Rent Collector - Can't Pay!",
            f"*the porch sags under heavy boots*\n\n"
            f"Rent owed: Rs.{tax}\n"
            f"You only have Rs.{state.balance}. The debt is marked in red ink.\n\n"
            f"Total rent debt this week: Rs.{state.weekly_tax_debt}\n"
            f"{days_left} day(s) left before eviction.\n\n"
            f"The devil laughs softly. 'A little debt makes the game interesting.'"
        )

    state.total_days_survived += 1

    if state.day == DAYS_PER_WEEK:
        _handle_end_of_week()
        return

    # Next day - spawn player at bed
    state.player_x = 102
    state.player_y = 187
    state.day           += 1
    state.daily_effects  = {}
    state.double_win_used = False
    state.roulette_rebate_used = False
    state.roulette_boost_used = False
    run_morning()


def _handle_end_of_week():
    debt         = state.weekly_tax_debt
    total_assets = state.balance + state.savings

    if debt == 0:
        _start_new_week()
        return

    if total_assets < debt:
        _game_over_tax(debt, total_assets)
        return

    ok = messagebox.askyesno(
        "Weekly Rent Settlement",
        f"Week {state.week_num} over! Outstanding rent debt: Rs.{debt}\n\n"
        f"Balance: Rs.{state.balance}\n"
        f"Savings: Rs.{state.savings}\n"
        f"Total:   Rs.{total_assets}\n\n"
        f"Pay Rs.{debt} and start Week {state.week_num + 1}?"
    )
    if not ok:
        _game_over_tax(debt, total_assets)
        return

    if state.balance >= debt:
        state.balance -= debt
    else:
        rem            = debt - state.balance
        state.balance  = 0
        state.savings -= rem

    state.total_tax_paid  += debt
    state.weekly_tax_debt  = 0
    _start_new_week()


def _start_new_week():
    state.week_num       += 1
    next_tax              = BASE_DAILY_TAX + (state.week_num - 1) * TAX_WEEKLY_STEP
    messagebox.showinfo(
        f"Week {state.week_num - 1} Survived!",
        f"You kept the ruined house for one more week.\n\n"
        f"Total days: {state.total_days_survived}\n"
        f"Rent paid ever: Rs.{state.total_tax_paid}\n"
        f"Balance: Rs.{state.balance}   Savings: Rs.{state.savings}\n\n"
        f"Week {state.week_num} starts now.\n"
        f"Daily rent this week: Rs.{next_tax}"
    )
    # Spawn player at bed for new week
    state.player_x = 102
    state.player_y = 187
    state.day              = 1
    state.weekly_tax_debt  = 0
    state.daily_effects    = {}
    state.double_win_used  = False
    state.roulette_rebate_used = False
    state.roulette_boost_used = False
    run_morning()


# =============================================================================
# END OF DAY / WEEK
# =============================================================================

def _game_over_tax(debt: int, assets: int):
    messagebox.showerror(
        "GAME OVER - EVICTED",
        f"The landlord boards up the old house.\n\n"
        f"Rent owed:   Rs.{debt}\n"
        f"Your assets: Rs.{assets}\n\n"
        f"--- FINAL STATS ---\n"
        f"Weeks:    {state.week_num - 1}\n"
        f"Days:     {state.total_days_survived}\n"
        f"Winnings: Rs.{state.total_gross_earned}\n"
        f"Rent paid: Rs.{state.total_tax_paid}"
    )
    _reset_to_title()


def _game_over_broke():
    messagebox.showerror(
        "GAME OVER - BROKE",
        f"Balance: Rs.0   Savings: Rs.0\n\n"
        f"The slot machine is silent. The broken roulette table is only firewood now.\n\n"
        f"--- FINAL STATS ---\n"
        f"Weeks:    {state.week_num - 1}\n"
        f"Days:     {state.total_days_survived}\n"
        f"Winnings: Rs.{state.total_gross_earned}"
    )
    _reset_to_title()


def _reset_to_title():
    _stop_canvas_redraw()
    state.reset()
    game_frame.pack_forget()
    deposit_frame.pack(pady=50)


# =============================================================================
# CONSTANTS & HELPERS
# =============================================================================

ANIM_TAG = "_anim"
canvas_redraw_job = None

def _stop_canvas_redraw():
    global canvas_redraw_job
    if canvas_redraw_job is not None:
        try:
            root.after_cancel(canvas_redraw_job)
        except Exception:
            pass
        canvas_redraw_job = None

def _anim_after(ms, fn, *args):
    root.after(ms, fn, *args)
def handle_deposit():
    s = deposit_entry.get().strip()
    if not s.isdigit():
        messagebox.showerror("Error", "Please enter a valid amount.")
        return
    amt = int(s)
    if not (MIN_START <= amt <= MAX_START):
        messagebox.showerror("Error", f"Starting deposit must be Rs.{MIN_START}–Rs.{MAX_START}.")
        return

    state.reset()
    state.balance       = amt
    state.session_start = time.time()
    state.difficulty    = difficulty_var.get()

    deposit_frame.pack_forget()
    game_frame.pack(pady=10)
    refresh_ui()
    close_machine_view()
    update_spin_button()
    update_room_scene("You drag the slot machine inside. The broken roulette table leans by the wall.")
    run_morning()
    close_machine_view()
    root.focus_force()


def handle_spin():
    active = [i for i, v in enumerate([line1_var, line2_var, line3_var]) if v.get()]
    if not active:
        messagebox.showwarning("Selection Error", "Pick at least one line!")
        return

    is_free = state.free_spins_left > 0
    ok, err, bet = validate_bet(bet_entry.get().strip(), is_free)
    if not ok:
        messagebox.showwarning("Input Error", err)
        return

    if is_free and int(bet_entry.get()) != bet:
        bet_entry.delete(0, tk.END)
        bet_entry.insert(0, str(bet))

    total_bet = bet * len(active)

    if not is_free and total_bet > state.balance:
        messagebox.showerror("Insufficient Funds",
                             f"Need Rs.{total_bet}, have Rs.{state.balance}.")
        return

    if is_free:
        state.free_spins_left -= 1
    else:
        state.balance -= total_bet

    # Bankruptcy check after spending
    if state.is_bankrupt():
        _game_over_broke()
        return

    slots = build_spin()
    render_grid(slots)

    winnings, details = check_winnings(slots, active, bet)
    state.balance            += winnings
    state.total_gross_earned += winnings

    if any(sym == "A" for _, sym in details):
        bonus = 5 + state.perm_upgrades.get("high_roller", 0) * 3
        state.free_spins_left += bonus
        messagebox.showinfo("JACKPOT!", f"THREE 'A' SYMBOLS! +{bonus} FREE SPINS!")

    update_result_labels(bet, len(active), total_bet, winnings, details, is_free)
    refresh_ui()
    update_spin_button()


def handle_roulette_spin():
    if not state.roulette_unlocked:
        unlock_roulette()
        return

    ok, err, bet = validate_bet(roulette_bet_entry.get().strip(), False)
    if not ok:
        messagebox.showwarning("Input Error", err)
        return
    if bet > state.balance:
        messagebox.showerror("Insufficient Funds", f"Need Rs.{bet}, have Rs.{state.balance}.")
        return

    bet_type = roulette_bet_var.get()
    chosen_number = None
    if bet_type == "Single Number":
        num_str = roulette_number_var.get().strip()
        if not num_str.isdigit() or not (0 <= int(num_str) <= 36):
            messagebox.showwarning("Input Error", "Single number must be between 0 and 36.")
            return
        chosen_number = int(num_str)

    state.balance -= bet
    if state.is_bankrupt():
        _game_over_broke()
        return

    number, colour, winnings, multiplier = spin_roulette(bet_type, chosen_number, bet)
    refund = 0
    if winnings == 0 and state.daily_effects.get("roulette_rebate") and not state.roulette_rebate_used:
        refund = bet // 2
        state.balance += refund
        state.roulette_rebate_used = True
    state.balance += winnings
    state.total_gross_earned += winnings

    render_roulette_result(number, colour)
    update_roulette_result_labels(bet, bet_type, chosen_number, winnings, multiplier, refund)
    refresh_ui()


# =============================================================================
# DISPLAY HELPERS
# =============================================================================
def render_grid(slots):
    for r in range(ROWS):
        for c in range(COLS):
            grid_labels[r][c].config(text=slots[c][r], bg=BG_CELL)
    for r in range(ROWS):
        syms = [slots[c][r] for c in range(COLS)]
        u    = len(set(syms))
        if u == 1:
            for c in range(COLS):
                grid_labels[r][c].config(bg=COL_WIN)
        elif u == 2:
            counts = Counter(syms)
            paired = {sym for sym, cnt in counts.items() if cnt == 2}
            for c in range(COLS):
                if slots[c][r] in paired:
                    grid_labels[r][c].config(bg=COL_PAIR)


def update_result_labels(bet, lines, total_bet, winnings, details, is_free):
    cost = "Rs.0 (FREE)" if is_free else f"Rs.{total_bet}"
    bet_summary_label.config(text=f"Rs.{bet} × {lines} line(s) — cost: {cost}")
    winnings_label.config(text=f"You won: Rs.{winnings}",
                          fg=COL_WIN if winnings > 0 else "white")
    nums = [str(ln) for ln, _ in details]
    lines_label.config(text=(f"Winning lines: {', '.join(nums)}" if nums
                             else "No winning lines this time."))


def update_spin_button():
    if state.free_spins_left > 0:
        spin_btn.config(text=f"FREE SPIN ({state.free_spins_left} left)", bg=COL_BLUE)
    else:
        spin_btn.config(text="SPIN", bg=COL_RED)


def unlock_roulette() -> bool:
    if state.roulette_unlocked:
        return True
    if state.balance < ROULETTE_UNLOCK_COST:
        messagebox.showwarning(
            "Broken Roulette Table",
            f"The roulette table is broken.\n"
            f"Repairs cost Rs.{ROULETTE_UNLOCK_COST}.\n"
            f"You have Rs.{state.balance}."
        )
        return False
    if not messagebox.askyesno(
        "Repair Roulette?",
        f"Pay Rs.{ROULETTE_UNLOCK_COST} to repair the broken roulette table?"
    ):
        return False

    state.balance -= ROULETTE_UNLOCK_COST
    state.roulette_unlocked = True
    update_room_scene("Roulette repaired. The wheel coughs back to life.")
    refresh_ui()
    return True


def close_machine_view():
    state.current_game = "room"
    slot_grid_frame.pack_forget()
    roulette_table_frame.pack_forget()
    slot_controls_frame.pack_forget()
    roulette_controls_frame.pack_forget()
    spin_btn.pack_forget()
    roulette_spin_btn.pack_forget()
    slot_mode_btn.config(bg=BG_MID, fg="white")
    roulette_mode_btn.config(bg=BG_MID, fg="white")
    bet_summary_label.config(text="Walk near a machine and press E to use it.")
    winnings_label.config(text="")
    lines_label.config(text="")
    # Reset focus to root window so text box doesn't capture keys
    root.focus_set()


def _near_slot() -> bool:
    return _near(state.player_x, state.player_y, 42, 46, 132, 144)


def _near_roulette() -> bool:
    return _near(state.player_x, state.player_y, 312, 46, 444, 158)


def set_game_mode(mode: str, from_room: bool = False):
    if mode == "slots" and not (from_room or _near_slot()):
        update_room_scene("Get closer to the slot machine and press E.")
        return
    if mode == "roulette" and not (from_room or _near_roulette()):
        update_room_scene("Get closer to the roulette table and press E.")
        return
    if mode == "roulette" and not unlock_roulette():
        mode = "slots"
        if not (from_room or _near_slot()):
            close_machine_view()
            return

    state.current_game = mode
    if mode == "slots":
        root.title("Casino - Slot Machine")
        slot_mode_btn.config(bg=COL_BLUE, fg="white")
        roulette_mode_btn.config(bg=BG_MID, fg="white")
        roulette_mode_btn.config(text=("Roulette" if state.roulette_unlocked
                                       else f"Repair Roulette Rs.{ROULETTE_UNLOCK_COST}"))
        slot_grid_frame.pack(pady=6)
        roulette_table_frame.pack_forget()
        slot_controls_frame.pack(pady=4)
        roulette_controls_frame.pack_forget()
        spin_btn.pack(pady=6, before=end_day_btn)
        roulette_spin_btn.pack_forget()
        update_spin_button()
        bet_summary_label.config(text="")
        winnings_label.config(text="")
        lines_label.config(text="")
    else:
        root.title("Casino - Roulette")
        roulette_mode_btn.config(bg=COL_BLUE, fg="white")
        roulette_mode_btn.config(text="Roulette")
        slot_mode_btn.config(bg=BG_MID, fg="white")
        slot_grid_frame.pack_forget()
        roulette_table_frame.pack(pady=6)
        slot_controls_frame.pack_forget()
        roulette_controls_frame.pack(pady=4)
        spin_btn.pack_forget()
        roulette_spin_btn.pack(pady=6, before=end_day_btn)
        render_roulette_idle()
        update_roulette_preview()
        winnings_label.config(text="")
        lines_label.config(text="Pick a roulette bet and spin.")


def render_roulette_idle():
    for num, cell in roulette_number_labels.items():
        colour = roulette_colour(num)
        bg = {"Red": COL_RED, "Black": COL_BLACK, "Green": COL_GREEN}[colour]
        cell.config(bg=bg, fg="white", relief="raised")
    roulette_result_label.config(text="ROULETTE TABLE", bg=BG_MID, fg=COL_GOLD)


def render_roulette_result(number: int, colour: str):
    render_roulette_idle()
    bg = {"Red": COL_RED, "Black": COL_BLACK, "Green": COL_GREEN}[colour]
    roulette_number_labels[number].config(bg=COL_GOLD, fg=BG_DARK, relief="sunken")
    parity = "ZERO" if number == 0 else "EVEN" if number % 2 == 0 else "ODD"
    roulette_result_label.config(text=f"LANDED: {number}  {colour.upper()}  {parity}",
                                 bg=bg, fg="white")


def update_roulette_preview(*args):
    bet = roulette_bet_entry.get().strip()
    bet_type = roulette_bet_var.get()
    if bet.isdigit():
        choice = f" on {roulette_number_var.get().strip()}" if bet_type == "Single Number" else ""
        bet_summary_label.config(text=f"Roulette bet: Rs.{bet} on {bet_type}{choice}", fg=COL_GREY)
    else:
        bet_summary_label.config(text="Enter a roulette bet amount", fg=COL_RED)


def update_roulette_result_labels(bet, bet_type, chosen_number, winnings, multiplier, refund):
    choice = f" {chosen_number}" if bet_type == "Single Number" else ""
    bet_summary_label.config(text=f"Rs.{bet} on {bet_type}{choice} - paid {multiplier}x")
    winnings_label.config(text=f"You won: Rs.{winnings}",
                          fg=COL_WIN if winnings > 0 else "white")
    if refund:
        lines_label.config(text=f"No roulette win. Rebate refunded Rs.{refund}.")
    else:
        lines_label.config(text="Roulette hit!" if winnings > 0 else "No roulette win this time.")


def update_room_scene(message: str | None = None):
    global canvas_redraw_job
    if "room_canvas" not in globals():
        return
    if not root.winfo_exists():
        return
    if canvas_redraw_job is not None:
        try:
            root.after_cancel(canvas_redraw_job)
        except Exception:
            pass
        canvas_redraw_job = None

    c = room_canvas
    c.delete(ANIM_TAG)

    # --- Background ---
    c.create_rectangle(8, 8, 472, 232, fill="#0D0805", outline=COL_GOLD, width=3)
    c.create_rectangle(24, 24, 456, 216, fill="#140C07", outline="#2A1A0F", width=1)

    # Ceiling vignette
    shapes = [
        (30, "#120A04", 1), (42, "#0E0803", 1),
        (54, "#0A0602", 1), (66, "#060401", 1),
    ]
    for pad, shade, w in shapes:
        c.create_rectangle(pad, pad, 472 - pad, 232 - pad, fill="", outline=shade, width=w, tags=ANIM_TAG)

    # --- Floorboards ---
    for y in range(42, 216, 28):
        c.create_line(24, y, 456, y, fill="#2C1A0E", width=1, tags=ANIM_TAG)
        c.create_line(24, y + 1, 456, y + 1, fill="#1F1208", width=1, tags=ANIM_TAG)
    for x in range(52, 456, 48):
        c.create_line(x, 24, x - 16, 216, fill="#221408", width=1, tags=ANIM_TAG)

    # --- SLOT MACHINE ---
    sx, sy = 86, 90
    c.create_rectangle(sx - 32, sy - 38, sx + 32, sy + 24, fill="#1A0F07", outline=COL_GOLD, width=2, tags=ANIM_TAG)
    c.create_rectangle(sx - 28, sy - 34, sx + 28, sy + 20, fill="#221408", outline="#3D2A18", width=1, tags=ANIM_TAG)
    rx = [sx - 20, sx, sx + 20]
    for rx0 in rx:
        c.create_rectangle(rx0 - 6, sy - 26, rx0 + 6, sy + 4, fill="#3D0A0A", outline="#F4E7C5", width=1, tags=ANIM_TAG)
        c.create_rectangle(rx0 - 5, sy - 24, rx0 + 5, sy + 2, fill="#1A0505", outline="", tags=ANIM_TAG)
    syms = ["♠", "♣", "♥"]
    for rx0, sym in zip(rx, syms):
        c.create_text(rx0, sy - 10, text=sym, font=("Arial", 11, "bold"), fill=COL_GOLD, tags=ANIM_TAG)
    c.create_line(sx + 30, sy + 10, sx + 36, sy + 24, fill="#8B7355", width=2, tags=ANIM_TAG)
    c.create_oval(sx + 34, sy + 22, sx + 38, sy + 26, fill=COL_ORNG, outline="#5A3000", width=1, tags=ANIM_TAG)
    c.create_oval(sx - 20, sy + 22, sx + 20, sy + 30, fill="#1A0F07", outline="", tags=ANIM_TAG)
    c.create_text(sx, sy + 34, text="SLOT", font=FONT_SMALL, fill=COL_GOLD, tags=ANIM_TAG)
    c.create_text(sx, sy + 42, text="MACHINE", font=("Arial", 7, "bold"), fill=COL_GREY, tags=ANIM_TAG)

    # --- ROULETTE TABLE ---
    rt_x, rt_y = 378, 88
    outline = COL_GOLD if state.roulette_unlocked else COL_RED
    rt_text = "ROULETTE" if state.roulette_unlocked else "BROKEN"
    rt_fill = "#0A1A10" if state.roulette_unlocked else "#1F1208"
    c.create_rectangle(rt_x - 52, rt_y - 38, rt_x + 52, rt_y + 24, fill=rt_fill, outline=outline, width=2, tags=ANIM_TAG)
    c.create_rectangle(rt_x - 46, rt_y - 34, rt_x + 46, rt_y + 20, fill="#0D1410", outline="#1A2A1F", width=1, tags=ANIM_TAG)
    for r in (32, 28):
        c.create_oval(rt_x - r, rt_y - r, rt_x + r, rt_y + r, fill="#0A0A0A",
                      outline=outline if r == 28 else "#1F1F1F", width=1 if r == 28 else 2, tags=ANIM_TAG)
    spokes = [
        (rt_x, rt_y - 28, rt_x, rt_y + 28),
        (rt_x - 28, rt_y, rt_x + 28, rt_y),
        (rt_x - 20, rt_y - 20, rt_x + 20, rt_y + 20),
        (rt_x + 20, rt_y - 20, rt_x - 20, rt_y + 20),
    ]
    for x1, y1, x2, y2 in spokes:
        c.create_line(x1, y1, x2, y2, fill=outline, width=1, tags=ANIM_TAG)
    c.create_oval(rt_x - 4, rt_y - 4, rt_x + 4, rt_y + 4, fill=COL_GOLD, outline="#8B6914", width=1, tags=ANIM_TAG)
    c.create_text(rt_x, rt_y + 34, text=rt_text, font=FONT_SMALL, fill=outline, tags=ANIM_TAG)
    if not state.roulette_unlocked:
        c.create_text(rt_x, rt_y + 42, text="(locked)", font=("Arial", 7), fill=outline, tags=ANIM_TAG)

    # --- BED ---
    bx, by = 102, 186
    c.create_rectangle(bx - 32, by - 18, bx + 32, by + 22, fill="#140C07", outline="#5C3A24", width=2, tags=ANIM_TAG)
    c.create_rectangle(bx - 28, by - 14, bx + 28, by + 18, fill="#221408", outline="#6B4530", width=1, tags=ANIM_TAG)
    c.create_oval(bx - 14, by - 11, bx + 10, by - 1, fill="#C89B8A", outline="#7A5A4A", width=1, tags=ANIM_TAG)
    c.create_rectangle(bx - 28, by - 2, bx + 28, by + 18, fill="#6B2418", outline="#4A1810", width=1, tags=ANIM_TAG)
    for yy in (by + 6, by + 12):
        c.create_line(bx - 28, yy, bx + 28, yy, fill="#4A1810", width=1, tags=ANIM_TAG)
    c.create_text(bx, by + 28, text="BED", font=FONT_SMALL, fill=COL_GREY, tags=ANIM_TAG)

    # --- DEVIL ---
    dx, dy = 240, 50
    # Robe / body
    pts = [dx, dy - 24, dx - 20, dy + 20, dx + 20, dy + 20]
    c.create_polygon(*pts, fill="#140812", outline="#4A1060", width=2, tags=ANIM_TAG)
    c.create_polygon(*pts, fill="#3D1040", outline="", tags=ANIM_TAG)
    c.create_rectangle(dx - 8, dy + 4, dx + 8, dy + 22, fill="#1A0810", outline="#3D1040", width=1, tags=ANIM_TAG)
    # Head
    c.create_oval(dx - 13, dy - 26, dx + 13, dy - 6, fill="#140812", outline="#7B1FA2", width=2, tags=ANIM_TAG)
    c.create_oval(dx - 10, dy - 24, dx + 10, dy - 8, fill="#3D1040", outline="", tags=ANIM_TAG)
    # Eyes
    for ex in (dx - 5, dx + 5):
        c.create_oval(ex - 2, dy - 19, ex + 2, dy - 15, fill=COL_GOLD, outline="#5A3800", width=1, tags=ANIM_TAG)
        c.create_oval(ex - 1, dy - 18, ex + 1, dy - 16, fill="#FFD700", outline="", tags=ANIM_TAG)
    # Mouth
    c.create_arc(dx - 6, dy - 15, dx + 6, dy - 7, start=0, extent=180, style="arc", outline=COL_GOLD, width=1, tags=ANIM_TAG)
    # Horns
    hd = [
        (dx - 10, dy - 24, dx - 16, dy - 32, dx - 8, dy - 20),
        (dx + 10, dy - 24, dx + 16, dy - 32, dx + 8, dy - 20),
    ]
    for hx, hy, hx0, hy0, hx1, hy1 in hd:
        c.create_polygon(hx, hy, hx0, hy0, hx1, hy1, fill="#140812", outline=COL_GOLD, width=1, tags=ANIM_TAG)
    c.create_text(dx, dy + 24, text="DEVIL", font=FONT_SMALL, fill="#C084FC", tags=ANIM_TAG)

    # --- DOOR (Exit) ---
    door_x, door_y = 160, 30
    c.create_rectangle(door_x - 20, door_y - 20, door_x + 20, door_y + 36, fill="#2A1A0A", outline=COL_GOLD, width=2, tags=ANIM_TAG)
    c.create_rectangle(door_x - 16, door_y - 16, door_x + 16, door_y + 32, fill="#1A1008", outline="#3D2A18", width=1, tags=ANIM_TAG)
    c.create_oval(door_x + 8, door_y + 8, door_x + 12, door_y + 12, fill=COL_GOLD, outline="#5A3800", width=1, tags=ANIM_TAG)
    c.create_text(door_x, door_y + 44, text="EXIT", font=FONT_SMALL, fill=COL_GOLD, tags=ANIM_TAG)

    # --- Dust motes ---
    import math
    t = time.time() * 0.5
    seeds = [0.31, 0.73, 1.15, 1.67, 2.29]
    for seed in seeds:
        px = int(40 + 380 * ((math.sin(t + seed) + 1) / 2))
        py = int(30 + 160 * ((math.cos(t * 0.6 + seed * 1.7) + 1) / 2))
        sz = 1 if seed > 1.6 else 2
        c.create_oval(px, py, px + sz, py + sz, fill="#5C3D2A", outline="", tags=ANIM_TAG)

    # --- PLAYER ---
    x, y = state.player_x, state.player_y
    # Shadow on floor
    c.create_oval(x - 9, y + 7, x + 9, y + 14, fill="#050200", outline="", tags=ANIM_TAG)
    # Body
    c.create_rectangle(x - 8, y - 8, x + 8, y + 6, fill=COL_BLUE, outline="white", width=2, tags=ANIM_TAG)
    c.create_rectangle(x - 4, y - 16, x + 4, y - 8, fill="#F4E7C5", outline="white", width=1, tags=ANIM_TAG)
    # Eyes
    c.create_oval(x - 4, y - 14, x - 2, y - 10, fill="#111", tags=ANIM_TAG)
    c.create_oval(x + 2, y - 14, x + 4, y - 10, fill="#111", tags=ANIM_TAG)
    # Highlight arc
    c.create_arc(x - 4, y - 15, x + 4, y - 9, start=200, extent=140, style="arc", outline="white", width=1, tags=ANIM_TAG)

    # --- Nearby highlight ---
    if _near_slot() or _near_roulette() or _near(x, y, 52, 154, 152, 218) or _near(x, y, 196, 22, 284, 100):
        c.create_oval(x - 16, y - 16, x + 16, y + 16, outline=COL_GOLD, width=1, dash=(3, 3), tags=ANIM_TAG)

    # --- Status ---
    room_status_label.config(
        text=message or "Move with WASD / arrow keys. Press E to interact. Press ESC to unfocus text box."
    )

    canvas_redraw_job = root.after(140, update_room_scene)


def _near(px, py, x1, y1, x2, y2) -> bool:
    return x1 <= px <= x2 and y1 <= py <= y2


def move_player(dx: int, dy: int):
    state.player_x = max(36, min(444, state.player_x + dx))
    state.player_y = max(36, min(204, state.player_y + dy))
    update_room_scene()


def handle_room_key(event):
    if "game_frame" in globals() and not game_frame.winfo_ismapped():
        return
    
    # ESC key: unfocus any text entry and return focus to root for movement
    if event.keysym == "Escape":
        root.focus_set()
        return
    
    # If the event came from an Entry or Spinbox, ignore it (don't move/interact)
    if isinstance(event.widget, (tk.Entry, tk.Spinbox)):
        return
    
    # If focus is currently in an Entry or Spinbox, also ignore
    try:
        focus_widget = root.focus_get()
        if focus_widget and isinstance(focus_widget, (tk.Entry, tk.Spinbox)):
            return
    except:
        pass
    
    key = event.keysym.lower()
    if key in {"left", "a"}:
        move_player(-16, 0)
    elif key in {"right", "d"}:
        move_player(16, 0)
    elif key in {"up", "w"}:
        move_player(0, -16)
    elif key in {"down", "s"}:
        move_player(0, 16)
    elif key == "e":
        interact_with_room()


def interact_with_room():
    x, y = state.player_x, state.player_y
    if _near(x, y, 42, 46, 132, 144):
        set_game_mode("slots", from_room=True)
        update_room_scene("You stand at the slot machine you bought with your last money.")
    elif _near(x, y, 312, 46, 444, 158):
        set_game_mode("roulette", from_room=True)
        update_room_scene("The roulette table waits under splintered wood and old smoke.")
    elif _near(x, y, 52, 154, 152, 218):
        update_room_scene("You end the day on a thin mattress beside the machines.")
        handle_end_day()
    elif _near(x, y, 140, 10, 180, 66):
        show_outside_menu()
    elif _near(x, y, 196, 22, 284, 100):
        show_shop_dialog()
        update_room_scene("The devil's grin lingers in the room.")
    else:
        update_room_scene("Nothing here but dust, damp wood, and bad decisions.")


def refresh_ui():
    # Balance row
    balance_label.config(
        text=f"Balance: Rs.{state.balance}     Savings: Rs.{state.savings}"
    )
    # Info bar
    tax = state.daily_tax()
    debt = f"   RENT DEBT: Rs.{state.weekly_tax_debt}" if state.weekly_tax_debt > 0 else ""
    tax_label.config(
        text=(f"{state.difficulty.upper()}  |  Week {state.week_num}  Day {state.day}/{DAYS_PER_WEEK}  "
              f"|  Rent tonight: Rs.{tax}{debt}"),
        fg=COL_RED if state.weekly_tax_debt > 0 else COL_GREY,
    )
    # Upgrades bar
    perms = []
    for uid, label in [("bribery", "Bribery"),
                       ("tax_lawyer", "RentLawyer"),
                       ("lucky_charm", "LuckyCharm"),
                       ("high_roller", "HighRoller"),
                       ("wheel_bias", "WheelBias")]:
        n = state.perm_upgrades.get(uid, 0)
        if n:
            perms.append(f"{label}×{n}")
    perms_label.config(text="Perms: " + (", ".join(perms) if perms else "none"))

    effects = [UPGRADE_NAME_MAP.get(k, k) for k, v in state.daily_effects.items() if v]
    effects_label.config(text="Today: " + (", ".join(effects) if effects else "none"))
    roulette_mode_btn.config(text=("Roulette" if state.roulette_unlocked
                                   else f"Repair Roulette Rs.{ROULETTE_UNLOCK_COST}"))
    update_room_scene()


# =============================================================================
# GUI BUILD
# =============================================================================
root = tk.Tk()
root.title("The Rotten House")
root.geometry("780x880")
root.configure(bg=BG_DARK)

# --- TITLE SCREEN ---
deposit_frame = tk.Frame(root, bg=BG_DARK)
deposit_frame.pack(pady=22)

tk.Label(deposit_frame, text="THE ROTTEN HOUSE",
         font=(PIXEL_FACE, 22, "bold"), fg=COL_GOLD, bg=BG_DARK).pack(pady=10)
story_frame = tk.Frame(deposit_frame, bg=BG_MID, bd=4, relief="ridge")
story_frame.pack(fill="x", padx=24, pady=8)
story = (
    "You were once a millionaire.\n\n"
    "Then one high-stakes card game took the mansion, the cars, the friends, "
    "and your name from every guest list in town.\n\n"
    "Now you live in a falling-apart wooden house with rent due every night. "
    "With the last of your money you bought an old slot machine and a broken "
    f"roulette table. The table can be repaired for Rs.{ROULETTE_UNLOCK_COST}.\n\n"
    "At midnight, the devil visits. He is very pleased with your turn to gambling."
)
tk.Label(story_frame, text=story, font=FONT_MAIN, fg=COL_GREY, bg=BG_MID,
         justify="left", wraplength=640).pack(padx=18, pady=16)
tk.Label(deposit_frame,
         text=f"Last cash in your pocket: Rs.{MIN_START} - Rs.{MAX_START}",
         font=FONT_MAIN, fg=COL_GREY, bg=BG_DARK).pack()
tk.Label(deposit_frame,
         text="Pay rent. Feed the machines. Do not go broke.",
         font=FONT_MAIN, fg=COL_GREY, bg=BG_DARK).pack(pady=(2, 10))
tk.Label(deposit_frame, text="Difficulty:", font=FONT_BOLD, fg=COL_GOLD, bg=BG_DARK).pack(pady=(4, 2))
difficulty_var = tk.StringVar(value="game")
difficulty_frame = tk.Frame(deposit_frame, bg=BG_DARK)
difficulty_frame.pack(pady=(0, 8))
tk.Radiobutton(difficulty_frame, text="Game Difficulty", variable=difficulty_var, value="game",
               font=FONT_MAIN, fg="white", bg=BG_DARK, selectcolor=BG_MID,
               activebackground=BG_DARK, activeforeground="white").grid(row=0, column=0, padx=8)
tk.Radiobutton(difficulty_frame, text="Realistic Difficulty", variable=difficulty_var, value="realistic",
               font=FONT_MAIN, fg="white", bg=BG_DARK, selectcolor=BG_MID,
               activebackground=BG_DARK, activeforeground="white").grid(row=0, column=1, padx=8)
tk.Label(deposit_frame,
         text="Game: better odds and higher payouts. Realistic: casino-style odds.",
         font=FONT_SMALL, fg=COL_GREY, bg=BG_DARK).pack(pady=(0, 6))
deposit_entry = tk.Entry(deposit_frame, font=FONT_MAIN, justify="center", width=12)
deposit_entry.pack(pady=5)
deposit_entry.insert(0, "600")
tk.Button(deposit_frame, text="BUY THE MACHINES", font=FONT_BOLD,
          bg=COL_GREEN, fg="white", width=14, command=handle_deposit).pack(pady=10)


# --- MAIN GAME ---
game_frame = tk.Frame(root, bg=BG_DARK)

# Info bar
info_bar = tk.Frame(game_frame, bg=BG_MID, bd=2, relief="groove")
info_bar.pack(fill="x", padx=10, pady=(6, 2))
tax_label = tk.Label(info_bar, text="", font=FONT_SMALL, fg=COL_GREY, bg=BG_MID)
tax_label.pack(pady=4)

# Balance
balance_label = tk.Label(game_frame, text="", font=(PIXEL_FACE, 13, "bold"),
                          fg=COL_GOLD, bg=BG_DARK)
balance_label.pack(pady=3)

# Top-down room
room_panel = tk.Frame(game_frame, bg=BG_DARK)
room_panel.pack(pady=(2, 6))
room_canvas = tk.Canvas(room_panel, width=480, height=240, bg=BG_DARK,
                        highlightthickness=0)
room_canvas.pack()
room_status_label = tk.Label(room_panel, text="", font=FONT_SMALL,
                             fg=COL_GREY, bg=BG_DARK)
room_status_label.pack(pady=(2, 0))
root.bind_all("<KeyPress>", handle_room_key)

# Upgrade status bar
upg_bar = tk.Frame(game_frame, bg=BG_MID, bd=1, relief="groove")
upg_bar.pack(fill="x", padx=10, pady=(0, 4))
perms_label   = tk.Label(upg_bar, text="Perms: none", font=FONT_SMALL,
                          fg="#A29BFE", bg=BG_MID)
perms_label.pack(side="left", padx=8, pady=2)
effects_label = tk.Label(upg_bar, text="Today: none", font=FONT_SMALL,
                          fg=COL_GOLD, bg=BG_MID)
effects_label.pack(side="right", padx=8, pady=2)

# Game switcher
mode_frame = tk.Frame(game_frame, bg=BG_DARK)
mode_frame.pack(pady=(2, 4))
slot_mode_btn = tk.Button(mode_frame, text="Slot Machine", font=FONT_BOLD,
                          bg=COL_BLUE, fg="white", width=14,
                          command=lambda: set_game_mode("slots"))
slot_mode_btn.grid(row=0, column=0, padx=5)
roulette_mode_btn = tk.Button(mode_frame, text=f"Repair Roulette Rs.{ROULETTE_UNLOCK_COST}", font=FONT_BOLD,
                              bg=BG_MID, fg="white", width=24,
                              command=lambda: set_game_mode("roulette"))
roulette_mode_btn.grid(row=0, column=1, padx=5)
tk.Button(mode_frame, text="Room", font=FONT_BOLD, bg=BG_MID, fg="white",
          width=10, command=close_machine_view).grid(row=0, column=2, padx=5)

# Slot grid
slot_grid_frame = tk.Frame(game_frame, bg=BG_MID, bd=5, relief="groove")
slot_grid_frame.pack(pady=6)
grid_labels = []
for r in range(ROWS):
    row_labels = []
    for c in range(COLS):
        lbl = tk.Label(slot_grid_frame, text="-", font=FONT_SLOT,
                       width=4, height=1, bg=BG_CELL, fg=BG_DARK, bd=2, relief="sunken")
        lbl.grid(row=r, column=c, padx=5, pady=5)
        row_labels.append(lbl)
    grid_labels.append(row_labels)

# Roulette table
roulette_table_frame = tk.Frame(game_frame, bg=COL_GREEN, bd=5, relief="ridge")
roulette_result_label = tk.Label(roulette_table_frame, text="ROULETTE TABLE",
                                 font=(PIXEL_FACE, 14, "bold"), fg=COL_GOLD,
                                 bg=BG_MID, width=32)
roulette_result_label.grid(row=0, column=0, columnspan=13, padx=5, pady=(6, 4), sticky="ew")
roulette_number_labels = {}
zero_lbl = tk.Label(roulette_table_frame, text="0", font=FONT_BOLD, width=4, height=6,
                    bg=COL_GREEN, fg="white", bd=2, relief="raised")
zero_lbl.grid(row=1, column=0, rowspan=3, padx=2, pady=2, sticky="nsew")
roulette_number_labels[0] = zero_lbl
for r, numbers in enumerate(ROULETTE_ROWS, start=1):
    for c, num in enumerate(numbers, start=1):
        bg = COL_RED if num in ROULETTE_RED_NUMS else COL_BLACK
        lbl = tk.Label(roulette_table_frame, text=str(num), font=FONT_SMALL,
                       width=4, height=2, bg=bg, fg="white", bd=2, relief="raised")
        lbl.grid(row=r, column=c, padx=1, pady=1, sticky="nsew")
        roulette_number_labels[num] = lbl
outside_bets = [("1-18", 1, 3), ("EVEN", 4, 3), ("RED", 7, 2),
                ("BLACK", 9, 2), ("ODD", 11, 1), ("19-36", 12, 1)]
for text, col, span in outside_bets:
    tk.Label(roulette_table_frame, text=text, font=FONT_SMALL,
             bg=BG_MID, fg=COL_GOLD, bd=2, relief="ridge").grid(
                 row=4, column=col, columnspan=max(1, span), padx=1, pady=(4, 6), sticky="ew"
             )
roulette_table_frame.pack_forget()

# Result labels - create first but don't pack yet (needed for callbacks)
bet_summary_label = tk.Label(game_frame, text="", font=FONT_MAIN, fg=COL_GREY, bg=BG_DARK)
winnings_label = tk.Label(game_frame, text="", font=(PIXEL_FACE, 14, "bold"),
                           fg="white", bg=BG_DARK)
lines_label = tk.Label(game_frame, text="", font=FONT_MAIN, fg=COL_GREY, bg=BG_DARK)

slot_controls_frame = tk.Frame(game_frame, bg=BG_DARK)
slot_controls_frame.pack(pady=4)

# Line checkboxes
cb_frame = tk.LabelFrame(slot_controls_frame, text=" Select Lines ", font=FONT_BOLD,
                          fg="white", bg=BG_DARK, bd=2, padx=10, pady=5)
cb_frame.pack()
line1_var = tk.BooleanVar(value=True)
line2_var = tk.BooleanVar(value=True)
line3_var = tk.BooleanVar(value=True)
cb_kw = dict(font=FONT_MAIN, fg="white", bg=BG_DARK,
             selectcolor=BG_MID, activebackground=BG_DARK, activeforeground="white")
tk.Checkbutton(cb_frame, text="Top",    variable=line1_var, **cb_kw).grid(row=0, column=0, padx=10)
tk.Checkbutton(cb_frame, text="Middle", variable=line2_var, **cb_kw).grid(row=0, column=1, padx=10)
tk.Checkbutton(cb_frame, text="Bottom", variable=line3_var, **cb_kw).grid(row=0, column=2, padx=10)

# Bet input
inp = tk.Frame(slot_controls_frame, bg=BG_DARK)
inp.pack(pady=4)
tk.Label(inp, text="Bet per line (Rs.):", font=FONT_MAIN,
         fg="white", bg=BG_DARK).grid(row=0, column=0, padx=5, sticky="e")
bet_entry = tk.Entry(inp, font=FONT_MAIN, width=10, justify="center")
bet_entry.grid(row=0, column=1, padx=5, pady=5)
bet_entry.insert(0, "10")

roulette_controls_frame = tk.Frame(game_frame, bg=BG_DARK)
roulette_controls_frame.pack(pady=4)
roulette_bet_var = tk.StringVar(value="Red")
roulette_number_var = tk.StringVar(value="7")
roulette_bet_row = tk.Frame(roulette_controls_frame, bg=BG_DARK)
roulette_bet_row.pack(pady=3)
tk.Label(roulette_bet_row, text="Roulette bet:", font=FONT_MAIN,
         fg="white", bg=BG_DARK).grid(row=0, column=0, padx=5, sticky="e")
roulette_bet_menu = tk.OptionMenu(roulette_bet_row, roulette_bet_var, *ROULETTE_BETS)
roulette_bet_menu.config(font=FONT_MAIN, bg=BG_MID, fg="white", width=13,
                         activebackground=BG_MID, activeforeground="white")
roulette_bet_menu.grid(row=0, column=1, padx=5)
tk.Label(roulette_bet_row, text="Number:", font=FONT_MAIN,
         fg="white", bg=BG_DARK).grid(row=0, column=2, padx=5, sticky="e")
roulette_number_spin = tk.Spinbox(roulette_bet_row, from_=0, to=36, textvariable=roulette_number_var,
                                   font=FONT_MAIN, width=4, justify="center",
                                   command=update_roulette_preview)
roulette_number_spin.bind("<Escape>", lambda e: root.focus_set())
roulette_number_spin.grid(row=0, column=3, padx=5)

roulette_amt_row = tk.Frame(roulette_controls_frame, bg=BG_DARK)
roulette_amt_row.pack(pady=3)
tk.Label(roulette_amt_row, text="Bet amount (Rs.):", font=FONT_MAIN,
         fg="white", bg=BG_DARK).grid(row=0, column=0, padx=5, sticky="e")
roulette_bet_entry = tk.Entry(roulette_amt_row, font=FONT_MAIN, width=10, justify="center")
roulette_bet_entry.bind("<Escape>", lambda e: root.focus_set())
roulette_bet_entry.grid(row=0, column=1, padx=5, pady=5)
roulette_bet_entry.insert(0, "10")
roulette_controls_frame.pack_forget()

# Define update function after all widgets are created
def update_cost_preview(*args):
    """Update cost preview when line selection changes."""
    active = [i for i, v in enumerate([line1_var, line2_var, line3_var]) if v.get()]
    if active and bet_entry.get().isdigit():
        bet = int(bet_entry.get())
        lines = len(active)
        total_cost = bet * lines
        cost_text = f"Cost preview: Rs.{bet} × {lines} line(s) = Rs.{total_cost}"
        bet_summary_label.config(text=cost_text, fg=COL_GREY)
    elif not active:
        bet_summary_label.config(text="Select at least one line", fg=COL_RED)

# Bind callbacks to line selections
line1_var.trace_add("write", update_cost_preview)
line2_var.trace_add("write", update_cost_preview)
line3_var.trace_add("write", update_cost_preview)
bet_entry.bind("<KeyRelease>", update_cost_preview)
roulette_bet_var.trace_add("write", update_roulette_preview)
roulette_number_var.trace_add("write", update_roulette_preview)
roulette_bet_entry.bind("<KeyRelease>", update_roulette_preview)

# Buttons
spin_btn = tk.Button(game_frame, text="SPIN", font=(PIXEL_FACE, 14, "bold"),
                     bg=COL_RED, fg="white", width=20, command=handle_spin)
spin_btn.pack(pady=6)
roulette_spin_btn = tk.Button(game_frame, text="SPIN ROULETTE", font=(PIXEL_FACE, 14, "bold"),
                              bg=COL_RED, fg="white", width=20, command=handle_roulette_spin)
end_day_btn = tk.Button(game_frame, text="Sleep / Pay Rent", font=FONT_BOLD,
                        bg="#7F8C8D", fg="white", width=20, command=handle_end_day)
end_day_btn.pack(pady=3)

# Pack result labels in correct order
bet_summary_label.pack(pady=3)
winnings_label.pack(pady=2)
lines_label.pack()

root.mainloop()
