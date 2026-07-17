#calculator program
import time
import tkinter as tk

OPERATORS = ['+', '-', '*', '/']

def calculator():
    print('Calculator program running')
    print('----------------------------------------------------')

    no1 = float(input("Enter the 1st number: "))

    if isinstance(no1, (int, float)):
        print('1st number registered')
    else:
        print('Enter a valid number')
    print('----------------------------------------------------')

    no2 = float(input("Enter the 2nd number: "))

    if isinstance(no2, (int, float)):
        print('2nd number registered')
    else:
        print('Enter a valid number')
    print('----------------------------------------------------')


    operator = input("Enter the operator(+, -, *, /): ")

    if operator in OPERATORS:
        print('Operator registered')
    else:
        print('Select a valid operator')

    if operator == '+':
        result = no1 + no2
    if operator == '-':
        result = no1 - no2
    if operator == '*':
        result = no1 * no2
    if operator == '/':
        result = no1 / no2
    print('===================================================')

    print(f'{no1} {operator} {no2} = {round(result, 2)}')
    print('===================================================')



for i in range(1000000000000000):
    calculator()