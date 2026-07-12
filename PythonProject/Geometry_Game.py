import turtle
from random import randint


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def falls_in_rect(self, rectangle):
        return (rectangle.point1.x < self.x < rectangle.point2.x and
                rectangle.point1.y < self.y < rectangle.point2.y)

    def dist_frm_point(self, point):
        return ((self.x - point.x) ** 2 + (self.y - point.y) ** 2) ** 0.5


class Rectangle:
    def __init__(self, point1, point2):
        self.point1 = point1
        self.point2 = point2

    def ar_of_rect(self):
        return (self.point2.x - self.point1.x) * (self.point2.y - self.point1.y)


class GUIRectangle(Rectangle):
    def draw(self, canvas):
        canvas.penup()
        canvas.goto(self.point1.x, self.point1.y)
        canvas.pendown()

        width = self.point2.x - self.point1.x
        height = self.point2.y - self.point1.y

        for _ in range(2):
            canvas.forward(width)
            canvas.left(90)
            canvas.forward(height)
            canvas.left(90)


class GUIPoint(Point):
    def draw(self, canvas, size=6, color='red'):
        canvas.penup()
        canvas.goto(self.x, self.y)
        canvas.pendown()
        canvas.dot(size, color)


# --- Generate a VALID rectangle ---
x1, x2 = sorted([randint(0, 500), randint(100, 700)])
y1, y2 = sorted([randint(0, 500), randint(100, 700)])

rectangle = GUIRectangle(Point(x1, y1), Point(x2, y2))


# --- Game Input ---
print('=======================')
print('Rectangle Coordinates:',
      f"({rectangle.point1.x}, {rectangle.point1.y}) and ({rectangle.point2.x}, {rectangle.point2.y})")

user_point = GUIPoint(
    float(input('Guess X: ')),
    float(input('Guess Y: '))
)

user_area = float(input('Enter the area of the rectangle: '))


# --- Results ---
inside = user_point.falls_in_rect(rectangle)
actual_area = rectangle.ar_of_rect()

print('Your point was inside rectangle:', inside)
print('Your area was off by:', abs(actual_area - user_area))


# --- Drawing ---
screen = turtle.Screen()
screen.setup(width=800, height=800)

myturtle = turtle.Turtle()
myturtle.speed(1)

# Draw rectangle and point
rectangle.draw(canvas=myturtle)
user_point.draw(canvas=myturtle)

turtle.done()