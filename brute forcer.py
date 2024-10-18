import pyautogui
import itertools
import time
import keyboard

def generate_combinations(length):
    digits = '0123456789'
    return itertools.product(digits, repeat=length)

def brute_force(length):
    combinations = generate_combinations(length)
    for combo in combinations:
        password = ''.join(combo)
        pyautogui.typewrite(password)
        pyautogui.press('enter')
        time.sleep(0.1)  # Adjust the delay as needed

if __name__ == "__main__":
    length = 4  # Set the length of the password
    print("Press '1' to start the brute force process.")
    keyboard.wait('1')  # Wait until '1' key is pressed
    brute_force(length)