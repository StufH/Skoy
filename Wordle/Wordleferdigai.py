import tkinter as tk
from tkinter import messagebox

# Load words from file
with open('words_alpha.txt') as f:
    words = [line.strip() for line in f if len(line.strip()) == 5]

def filter_words():
    global words  # Access the global words variable

    grønn = green_entry.get()
    gul = yellow_entry.get()
    grå = gray_entry.get()

    green_positions = {}
    for pos in range(0, len(grønn), 2):
        letter = grønn[pos]
        position = int(grønn[pos + 1]) - 1
        green_positions[letter] = position
        words = [word for word in words if word[position] == letter]

    for pos in range(0, len(gul), 2):
        letter2 = gul[pos]
        position2 = int(gul[pos + 1]) - 1
        words = [word for word in words if letter2 in word and word[position2] != letter2]

    for letter3 in grå:
        if letter3 in green_positions:
            words = [word for word in words if word[green_positions[letter3]] == letter3]
        else:
            words = [word for word in words if letter3 not in word]

    letter_freq = {}
    for word in words:
        for letter in set(word):
            if letter in letter_freq:
                letter_freq[letter] += 1
            else:
                letter_freq[letter] = 1

    def score_word(word):
        return sum(letter_freq[letter] for letter in set(word))

    best_word = max(words, key=score_word)
    messagebox.showinfo("Next Best Word", f"The next best word to try is: {best_word}")

# Create the main window
root = tk.Tk()
root.title("Wordle Helper")

# Create and place the labels and entry widgets
tk.Label(root, text="Green Letters (e.g., a1b3):").grid(row=0, column=0, padx=10, pady=10)
green_entry = tk.Entry(root)
green_entry.grid(row=0, column=1, padx=10, pady=10)

tk.Label(root, text="Yellow Letters (e.g., a1b3):").grid(row=1, column=0, padx=10, pady=10)
yellow_entry = tk.Entry(root)
yellow_entry.grid(row=1, column=1, padx=10, pady=10)

tk.Label(root, text="Gray Letters:").grid(row=2, column=0, padx=10, pady=10)
gray_entry = tk.Entry(root)
gray_entry.grid(row=2, column=1, padx=10, pady=10)

# Create and place the button
tk.Button(root, text="Find Best Word", command=filter_words).grid(row=3, column=0, columnspan=2, pady=20)

# Run the application
root.mainloop()