# #python weight converter

# weight = float(input('Enter weight: '))
# unit = input('Enter unit (L for pounds, K for kilograms): ')

# if unit == 'L':
#     converted_weight = weight * 0.453592
#     print(f'{weight} pounds is equal to {converted_weight:.2f} kilograms.')
# elif unit == 'K':
#     converted_weight = weight / 0.453592
#     print(f'{weight} kilograms is equal to {converted_weight:.2f} pounds.')
# else:    print('Invalid unit. Please enter L for pounds or K for kilograms.')

# tmp = 29
# is_raining = True

# if tmp > 30 or tmp < 10 or is_raining:
#     print('The weather is bad. The outdoor event is canceled.')
# else:
#     print('The weather is good. The outdoor event is on.')

# tmp = 30
# is_sunny = True

# if tmp >= 30 and is_sunny:
#      print('The weather is Hot. Its sunny.')
# elif tmp >= 20 and is_sunny:
#      print('The weather is warm. Its sunny.')
# elif tmp >= 10 and is_sunny:
#         print('The weather is cool. Its sunny.')
# elif tmp >= 0 and is_sunny:
#         print('The weather is cold. Its sunny.')
# else:
#      print('The weather is Too Cold. It is not sunny.')

# tmp = 28
# is_sunny = True

# if tmp >= 30 and is_sunny:
#      print('The weather is Hot. Its sunny.')
# elif tmp >= 20 and not is_sunny:
#      print('The weather is warm. Its cloudy.')
# elif tmp >= 10 and not is_sunny:
#         print('The weather is cool. Its cloudy.')
# elif tmp >= 0 and not is_sunny:
#         print('The weather is cold. Its cloudy.')
# else:
#      print('The weather is Too Cold. It is not sunny.')

num = 6

# print('Positive' if num > 0 else 'Negative')
res= 'Even' if num % 2 == 0 else 'Odd'
print(res)
