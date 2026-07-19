user_name = input("Enter your name: ")
print(f"Hello, {user_name}! Welcome to the To-Do List App.")

# task1 = []
# task1.append(input("Enter your task: "))
# print(f"Task 1: {task1[0]} has been added to your to-do list.")
# task1.append(input("Enter your task: "))
# print(f"Task 2: {task1[1]} has been added to your to-do list.")
# task1.append(input("Enter your task: "))
# print(f"Task 3: {task1[2]} has been added to your to-do list.")
tasks = []
num_tasks = int(input('how many tasks do you want to add to your to-do list?: '))
for i in range(num_tasks):
    new_task = input(f"Enter task #{i + 1}: ")
    tasks.append(new_task)

print('Here is your to-do list for today: ')
for index, item in enumerate(tasks, start=1):
    print(f"{index}. {item}")