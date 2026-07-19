user_name = input("Enter your name: ")
print(f"Hello, {user_name}! Welcome to the To-Do List App.")

tasks = []
num_tasks = int(input('how many tasks do you want to add to your to-do list?: '))
for i in range(num_tasks):
    new_task = input(f"Enter task #{i + 1}: ")
    tasks.append(new_task)

print('Here is your to-do list for today: ')
for index, item in enumerate(tasks, start=1):
    print(f"{index}. {item}")
