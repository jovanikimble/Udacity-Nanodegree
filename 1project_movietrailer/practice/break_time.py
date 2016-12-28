import time
import webbrowser

breaks = 0

print("This progra started on " + time.ctime())
while(breaks < 3):
  time.sleep(10)
  webbrowser.open("https://www.youtube.com/watch?v=Ez1aQPhDuGg")
  breaks += 1
