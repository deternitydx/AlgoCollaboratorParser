import csv

def get_participants_all_list(mycsvfile = "/p/collabnets/participants_lists/participants_all.csv"):
    mylist = []
    with open(mycsvfile) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in spamreader:
            mylist.append(row)
    return mylist

# print(participants_all_list())