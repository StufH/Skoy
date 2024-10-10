#from sympy.stats.rv import probability

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



grønn = str(input("skriv alle grønne bokstaver med posisjon (f.eks. a1b3)"))
for pos in range(0, len(grønn), 2):
    letter = grønn[pos]
    position = int(grønn[pos + 1]) - 1
    words = [word for word in words if word[position] == letter]


gul = str(input("skriv alle gule bokstaver"))



grå = str(input("skriv alle grå bokstaver:"))
words = [word for word in words if not any(letter in word for letter in grå)]
print(words)











#Fjerne ord som starter med bokstav
"""
word = [i for i in word if not str(i).startswith(fjern)]
print(word)
"""