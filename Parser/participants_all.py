import csv

def get_participants_all_list(mycsvfile = "/p/collabnets/participants_lists/participants_test.csv"):
    mylist = []
    with open(mycsvfile) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in spamreader:
            mylist.append(row[0].strip())
    return mylist

print(get_participants_all_list())