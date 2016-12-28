import os

def rename_files():
  file_list = os.listdir("prank 2")
  saved_path = os.getcwd
  os.chdir("prank 2")

  for file_name in file_list:
    os.rename(file_name, file_name.translate(None, "0123456789"))

rename_files()
