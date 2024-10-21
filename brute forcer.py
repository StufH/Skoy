import pyautogui
import itertools
import time
import keyboard
import sys

def generate_combinations(length):
    digits = '0123456789'
    return itertools.product(digits, repeat=length)

def brute_force(length, delay):
    try:
        combinations = generate_combinations(length)
        for index, combo in enumerate(combinations, start=1):
            password = ''.join(combo)
            pyautogui.typewrite(password)
            pyautogui.press('enter')
            print(f"Trying password {index}: {password}")
            time.sleep(delay)
            if keyboard.is_pressed('q'):  # Allow user to quit the process
                print("Brute force process stopped by user.")
                break
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    length = 4  # Set the length of the password
    delay = 0.1  # Default delay

    if len(sys.argv) > 1:
        try:
            delay = float(sys.argv[1])
        except ValueError:
            print("Invalid delay value; using default delay of 0.1 seconds.")

    print("Press '1' to start the brute force process. Press 'q' to quit.")
    keyboard.wait('1')
    brute_force(length, delay)