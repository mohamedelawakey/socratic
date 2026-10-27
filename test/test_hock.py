import sys
from pathlib import Path 

project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.hook import install

install()

print("*" * 20)
print("the test of hook file")
print("*" * 20)

# test the zero devision error
number_1 = 10
number_2 = 0

print(number_1 / number_2)

# test a logic error
print("make a logic error in the average function")
def average(num_1: float, num_2: float):
    # the correct is (num_1 + num_2) / 2
    return num_1 + num_2 / 2

print(average(10, 20))

# test a type error
print("make a type error")
print(1 + "1")
