#from sympy.stats.rv import probability

fil = open("words_5", "w")

with open("words_alpha.txt") as f:
    word = []
    for line in f:
        words_5 = line.strip()
        if len(words_5) == 5:
            word.append(words_5.upper())
            fil.write(words_5.upper())
            fil.write("\n")


L = [1, 2, 5,2,3,5,6,7,8,46,4,43,2435,6433,243,45]
Test = input("skriv tall:")

for i in range(len(L)):
    #L = str(L)
    if str(L).startswith(str(Test)) or str(L).startswith(Test):
        print("hei")
#print(L)