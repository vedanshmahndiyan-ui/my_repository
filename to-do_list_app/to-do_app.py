import os

FILENAME = 'tasks.txt'

user_name = input("Enter your name: ")
print(f"Hello, {user_name}! Welcome to the To-Do List App.")

finished_tasks = []

def load_tasks():
    global tasks
    tasks = []
    if os.path.exists(FILENAME):
        file = open(FILENAME, "r")
        for line in file.readlines():
            tasks.append(line.strip())
        file.close()

def save_tasks():
    file = open(FILENAME, "w")
    for task in tasks:
        file.write(task + "\n")
    file.close()

tasks = load_tasks()

def initial_tasks(task):
    num_tasks = int(input('how many tasks do you want to add to your to-do list?: '))
    for i in range(num_tasks):
        new_task = input(f"Enter task #{i + 1}: ")
        tasks.append(new_task)
        print(f"Task '{new_task}' added to your to-do list.")

def view_tasks():
    if tasks:
        print('Here is your to-do list for today: ')
        for index, item in enumerate(tasks, start=1):
            print(f"{index}. {item}")
    else:
        print("Your to-do list is empty.")

def add_task():
    new_task = input("Enter the new task: ")
    tasks.append(new_task)
    print(f"Task '{new_task}' added to your to-do list.")
    save_tasks()

def finish_task():
    if tasks:
        view_tasks()
        task_index = int(input("Enter the number of the task you want to mark as finished: ")) - 1
        if 0 <= task_index < len(tasks):
            finished_task = tasks.pop(task_index)
            finished_tasks.append(finished_task)
            print(f"Task '{finished_task}' marked as finished.")
        else:
            print("Invalid task number.")
    else:
        print("Your to-do list is empty.")
    save_tasks()

def quit():
    print("Exiting the To-Do List App. Goodbye!")
    exit()

tasks = load_tasks()

while True:
    print('\nOptions -> view tasks[v] | add task[a] | finish task[f] | quit[q]')
    choice = input('Enter your choice: ').lower()
    if choice == 'v':
        view_tasks()
    elif choice == 'a':
        add_task()
    elif choice == 'f':
        finish_task()
    elif choice == 'q':
        quit()
    elif choice == 'ilovedoom':
        print('You have selected the secret option!')
        print('Fun Fact[totally not tampered with]: Doom is the best game ever made, if you like anything else...just know that I will find you and make you play Doom until you like it. You have been warned. ')
    else:
        print('Invalid choice. Please enter a valid option.')
