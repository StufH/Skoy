from colorama import Fore, Style

filnavn = "elever.txt"

class elev:
    def __init__(self, first, sist, kar):
        self.first = first
        self.sist = sist
        self.fullname = first + " " + sist
        self.kar = kar
        self.email = str.lower(first) + str.lower(sist) + '@elev.skole.no'
        self.alt = self.fullname + " " + self.email + " " + kar

def read_elever_from_file(filnavn):
        elever = []
        with open(filnavn, "r", encoding="utf-8") as file:
            for line in file:
                parts = line.strip().split()
                if len(parts) == 3:
                    first, sist, kar = parts
                    elever.append(elev(first, sist, kar))
                else:
                    print(f"Skipping invalid line: {line.strip()}")
        return elever

def write_elever_to_file(filnavn, elever):
    with open(filnavn, "w", encoding="utf-8") as file:
        for elev in elever:
            file.write(f"{elev.first} {elev.sist} {elev.kar}\n")

elever = read_elever_from_file(filnavn) # Read all students from the file

new_elever = [
    elev('Henrik', 'Stubbeland', "5.5"),
    elev('Eirik', 'Stubbeland', "3.4"),
    elev("Elias", "Henriksen", "700"),
    elev("Abd", "Abd", "6.667"),
    elev("Mathias", "Byåsen", "7")
]

# Avoid duplicates
for new_elev in new_elever:
    if new_elev.email not in [e.email for e in elever]:
        elever.append(new_elev)
# Write all students back to the file
write_elever_to_file(filnavn, elever)

d = 0
while d == 0:
    while True:
        try:
            print(f"{Style.RESET_ALL}1 = print en elevs fulle navn\n"
                  "2 = print en elevs email\n"
                  "3 = print en elevs karakter\n"
                  "4 = print alle elevers fulle navn\n"
                  "5 = print alle elevers email\n"
                  "6 = print alle elevers karakter\n"
                  "7 = print all info om alle elevene\n"
                  "8 = legg til en elev")  # Add a student
            spør = int(input("Hva vil du gjøre?\n"))

            if spør in [1, 2, 3]:  # For options 1, 2, and 3
                spør_1 = int(input(f"Hvilken elev vil du printe ut? (1-{len(elever)})\n"))
                print(Fore.GREEN)

                if 1 <= spør_1 <= len(elever):  # Check that the choice is within range
                    elev_valgt = elever[spør_1 - 1]
                    if spør == 1:
                        print(elev_valgt.fullname)
                        break
                    elif spør == 2:
                        print(elev_valgt.email)
                        break
                    elif spør == 3:
                        print(elev_valgt.kar)
                        break
                else:
                    print("Ugyldig elevnummer.")

            elif spør == 4:
                print(Fore.GREEN)
                for elev in elever:
                    print(elev.fullname)
                break

            elif spør == 5:
                print(Fore.GREEN)
                for elev in elever:
                    print(elev.email)
                break

            elif spør == 6:
                print(Fore.GREEN)
                for elev in elever:
                    print(elev.kar)
                break

            elif spør == 7:
                print(Fore.GREEN)
                for elev in elever:
                    print(elev.alt)
                break

            elif spør == 8:
                print(Fore.GREEN)
                first = input("Fornavn: ")
                sist = input("Etternavn: ")
                kar = input("Karakter: ")
                new_elev = elev(first, sist, kar)
                if new_elev.email not in [e.email for e in elever]:
                    elever.append(new_elev)
                    print("Ny elev lagt til.")
                else:
                    print("Denne eleven finnes allerede.")
                break

            else:
                print("Uglydig funksjons nummer")
                continue

        finally:
            print("")

    while True:
        try:
            stop = str(input("Vil du stoppe? "))
            if stop.lower() == "ja":
                d = 1
                break
            elif stop.lower() == "nei":
                break
            else:
                print("det er ikke et gyldig valg")
                continue

        finally:
            print("")

write_elever_to_file(filnavn, elever) #Write all students back to the file
