words = []
with open("words_5", "r") as file:
    for line in file:
        word = line.split()
        words.append(word)

print(words)
green = input("Write all green letters in the format (a1b3): ")
for i in range(green-)