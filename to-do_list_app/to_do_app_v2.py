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

load_tasks()

def initial_tasks():
    num_tasks = input('How many tasks do you want to add to your to-do list?: ').strip()
    if not num_tasks.isdigit():
        print("Invalid input. Did not enter a valid number.")
        return

    num_tasks = int(num_tasks)
    for i in range(num_tasks):
        new_task = input(f"Enter task #{i + 1}: ")
        tasks.append(new_task)
        print(f"Task '{new_task}' added to your to-do list.")
    save_tasks()

def view_tasks():
    if tasks:
        print('\nHere is your to-do list for today: ')
        for index, item in enumerate(tasks, start=1):
            print(f"{index}. {item}")
    else:
        print("\nYour to-do list is empty.")

def add_task():
    new_task = input("Enter the new task: ")
    tasks.append(new_task)
    print(f"Task '{new_task}' added to your to-do list.")
    save_tasks()

def finish_task():
    if not tasks:
        print("Your to-do list is empty.")
        return

    view_tasks()
    user_input = input("Enter the number of the task you want to mark as finished: ").strip()

    if user_input.isdigit():
        task_index = int(user_input) - 1
        if 0 <= task_index < len(tasks):
            finished_task = tasks.pop(task_index)
            finished_tasks.append(finished_task)
            print(f"Task '{finished_task}' marked as finished.")
            save_tasks()
        else:
            print("Invalid task number.")
    else:
        print("Please enter a valid numeric digit.")

def quit_app():
    print("Exiting the To-Do List App. Goodbye!")
    exit()

def task_update():
    if not tasks:
        print("Your to-do list is empty.")
        return

    view_tasks()
    user_input = input("Enter the number of the task you want to update: ").strip()

    if user_input.isdigit():
        task_index = int(user_input) - 1
        if 0 <= task_index < len(tasks):
            start_date = input("Enter start date (YYYY-MM-DD): ")
            end_date = input("Enter end date (YYYY-MM-DD): ")
            if end_date.strip() != "":
                finished_task = tasks.pop(task_index)
                finished_tasks.append(finished_task + " | " + start_date + " | " + end_date)
                print(f"Task '{finished_task}' marked as finished with dates.")
            else:
                tasks[task_index] = tasks[task_index] + " | " + start_date
                print(f"Task '{tasks[task_index]}' updated with start date.")
            save_tasks()
        else:
            print("Invalid task number.")
    else:
        print("Please enter a valid numeric digit.")

def main():
    while True:
        user_name = input("Enter your name: ").strip()
        if not user_name or not user_name.replace(" ", "").isalpha():
            print("Invalid input. Please enter a valid name.")
        else:
            print(f"Hello, {user_name}! Welcome to the To-Do List App.")
            break

    initial_tasks()

    while True:
        print('\nOptions -> view tasks[v] | add task[a] | finish task[f] | update task[u] | quit[q]')
        choice = input('Enter your choice: ').lower().strip()
        if choice == 'v':
            view_tasks()
        elif choice == 'a':
            add_task()
        elif choice == 'f':
            finish_task()
        elif choice == 'u':
            task_update()
        elif choice == 'q':
            quit_app()
        elif choice == 'ilovedoom':
            print('\nYou have selected the secret option!')
            print('Fun Fact: Doom is the best game ever made. If you like anything else... just know that I will find you and make you play Doom until you won\'t be able to play anything else. You have been warned.')
        else:
            print('Invalid choice. Please enter a valid option.')


if __name__ == "__main__":
    main()