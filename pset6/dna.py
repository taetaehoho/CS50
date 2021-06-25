import sys
import csv

def main():
    while True:
        if len(sys.argv) == 3:
            break
        else:
            print("Incorrect number of arguments")

    database = []

    with open(sys.argv[1], "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            database.append(row)

    sequence = []
    file = open(sys.argv[2], "r")
    for row in file:
        sequence.append(row)
    strseq = sequence[0]

    seqdict = {}

    keys = database[0]
    for x in keys.keys() - {"name"}:
        max_seq = 0
        for i in range(len(strseq)):
            if strseq[i:i+len(x)] == x:
                max_local = 0 
                n = 0 
                while strseq[(i+n) : (i + n + len(x))] == x:
                    n = n + len(x)
                    max_local += 1
                if max_local > max_seq:
                    max_seq = max_local
        if x in seqdict:
            seqdict[x] = max_seq
        else:
            seqdict[x] = max_seq

    for i in range(len(database)):
        n = 0
        for x in seqdict:
            if seqdict[x] == int(database[i][x]):
                n += 1
        if n == len(seqdict):
            print(database[i]['name'])
            return database[i]['name']
            break
    print("No Match")



main()