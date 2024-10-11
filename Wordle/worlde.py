words = []
position = {}


with open("words_5", "r") as file:
    for line in file:
        word = line.split()
        words.append(word)


green = input("Write all green letters in the format (a1b3): ")
for let in range(0, len(green), 2): #Saves letters and position
    letter_green = green[let]
    position_green = int(green[let+1]) - 1
    position[letter_green] = position_green
    words = [word for word in words if word[position_green] == letter_green]


