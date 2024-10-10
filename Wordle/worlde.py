from sympy.stats.rv import probability

fil = open("words_5", "w")

with open("words_alpha.txt") as f:
    words = []
    for line in f:
        words_5 = line.strip()
        if len(words_5) == 5:
            words.append(words_5)
            fil.write(words_5)
            fil.write("\n")

fil.close()



grønn = str(input("skriv alle grønne bokstaver med posisjon (f.eks. a1b3): "))
for pos in range(0, len(grønn), 2):
    letter = grønn[pos]
    position = int(grønn[pos + 1]) - 1
    words = [word for word in words if word[position] == letter]


gul = str(input("skriv alle gule bokstaver med posisjon: "))
for pos in range(0, len(gul), 2):
    letter2 = gul[pos]
    position2 = int(gul[pos + 1]) - 1
    words = [word for word in words if word[position2] == letter2]


grå = str(input("skriv alle grå bokstaver:"))
for pos in range(0, len(gul), 2):
    letter3 = gul[pos]
    position3 = int(gul[pos + 1]) - 1
    words = [word for word in words if not any(letter in word for letter in grå) and word for word in words if not word[position2] == letter2]
print(words)



#Testing testing testing testging







