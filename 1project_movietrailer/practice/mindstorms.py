import turtle



def draw_square(some_turtle):
  for x in range(0, 4):
    some_turtle.forward(100)
    some_turtle.right(90)

def draw_triangle(some_turtle):
  some_turtle.backward(100)
  some_turtle.left(60)
  some_turtle.forward(100)
  some_turtle.right(120)
  some_turtle.forward(100)

def draw_circle(some_turtle):
  some_turtle.circle(70)

def draw_art():
  window = turtle.Screen()
  window.bgcolor("black")

  brad = turtle.Turtle()
  brad.color("yellow")

  angie = turtle.Turtle()
  angie.color("grey")

  shiloh = turtle.Turtle()
  shiloh.color("pink")

  for i in range(0, 18):
    draw_square(brad)
    brad.right(20)
  #draw_triangle(angie)
  #draw_circle(shiloh)

  window.exitonclick()

draw_art()