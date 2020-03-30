import os

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

# get total lines of the input file
def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1
