user_name = input("Enter your name: ")
print(f"Hello, {user_name}! Welcome to the To-Do List App.")

tasks = []
finished_tasks = []
num_tasks = int(input('how many tasks do you want to add to your to-do list?: '))
for i in range(num_tasks):
    new_task = input(f"Enter task #{i + 1}: ")
    tasks.append(new_task)

print('Here is your to-do list for today: ')
for index, item in enumerate(tasks, start=1):
    print(f"{index}. {item}")

while True:
    print('\nOptions -> view tasks[v], add task[a],finish task[f], quit[q]')
    choice = input('Enter your choice: ').lower()
    if choice == 'v':
        print('Here is your to-do list for today: ')
        for index, item in enumerate(tasks, start=1):
            print(f"{index}. {item}")
    elif choice == 'a':
        new_task = input("Enter the new task: ")
        tasks.append(new_task)
        print(f"Task '{new_task}' added to your to-do list.")
    elif choice == 'f':
        if tasks:
            print('Here is your to-do list for today: ')
            for index, item in enumerate(tasks, start=1):
                print(f"{index}. {item}")
            task_index = int(input("Enter the number of the task you want to mark as finished: ")) - 1
            if 0 <= task_index < len(tasks):
                finished_task = tasks.pop(task_index)
                finished_tasks.append(finished_task)
                print(f"Task '{finished_task}' marked as finished.")
            else:
                print("Invalid task number.")
        else:
            print("Your to-do list is empty.")
    elif choice == 'q':
        print('Exiting the To-Do List App. Goodbye!')
        break
    elif choice == 'ilovedoom':
        print('You have selected the secret option!')
        print('Fun Fact[totally not tampered with]: Doom is the best game ever made, if you like anything else...just know that I will find you and make you play Doom until you like it. You have been warned. ')
    else:
        print('Invalid choice. Please enter a valid option.')
