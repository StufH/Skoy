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
fjern = input("skriv bokstav:")




#Fjerner ord som inneholder alt som skrives
"""
total_filtrert = [word for word in words if not any(letter in word for letter in fjern)]
print(total_filtrert)
"""


#Fjerne ord som starter med bokstav
"""
word = [i for i in word if not str(i).startswith(fjern)]
print(word)
"""