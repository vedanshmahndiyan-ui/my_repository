import tkinter as tk
from tkinter import simpledialog
import os

FILENAME = 'tasks.txt'
tasks = []
finished_tasks = []

def load_tasks():
    global tasks
    tasks = []
    if os.path.exists(FILENAME):
        with open(FILENAME, "r") as file:
            for line in file.readlines():
                tasks.append(line.strip())

def save_tasks():
    with open(FILENAME, "w") as file:
        for task in tasks:
            file.write(task + "\n")

def refresh_listbox():
    task_listbox.delete(0, tk.END)
    for task in tasks:
        task_listbox.insert(tk.END, task)

def add_task():
    new_task = task_entry.get()
    if new_task.strip() != "":
        tasks.append(new_task)
        save_tasks()
        refresh_listbox()
        task_entry.delete(0, tk.END)

def finish_task():
    selected = task_listbox.curselection()
    if selected:
        index = selected[0]
        finished_task = tasks.pop(index)
        finished_tasks.append(finished_task)
        save_tasks()
        refresh_listbox()

def task_update():
    selected = task_listbox.curselection()
    if not selected:
        return
    index = selected[0]

    start_date = simpledialog.askstring("Start Date", "Enter start date (YYYY-MM-DD):")
    if start_date is None:
        return

    end_date = simpledialog.askstring("End Date", "Enter end date (YYYY-MM-DD), or leave blank:")
    if end_date is None:
        return

    if end_date.strip() != "":
        finished_task = tasks.pop(index)
        finished_tasks.append(finished_task + " | " + start_date + " | " + end_date)
    else:
        tasks[index] = tasks[index] + " | " + start_date

    save_tasks()
    refresh_listbox()

def quit_app():
    window.destroy()

load_tasks()

window = tk.Tk()
window.title("To-Do List App")

task_entry = tk.Entry(window, width=30)
task_entry.pack(pady=5)

add_button = tk.Button(window, text="Add Task", command=add_task)
add_button.pack(pady=5)

task_listbox = tk.Listbox(window, width=40, height=10)
task_listbox.pack(pady=5)

finish_button = tk.Button(window, text="Finish Selected Task", command=finish_task)
finish_button.pack(pady=5)

update_button = tk.Button(window, text="Update Selected Task", command=task_update)
update_button.pack(pady=5)

quit_button = tk.Button(window, text="Quit", command=quit_app)
quit_button.pack(pady=5)

refresh_listbox()

window.mainloop()