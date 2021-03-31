import random


# To Generate a random level for endless mode
def generate_level():
    level_data = [[".", ".", ".", ".", ".", ".", ".", ".", ".", "0"],
     [".", ".", ".", ".", ".", ".", ".", ".", ".", "1"],
     [".", ".", ".", ".", ".", ".", ".", ".", ".", "2"],
     [".", ".", ".", ".", ".", ".", ".", ".", ".", "3"],
     [".", ".", ".", ".", ".", ".", ".", ".", ".", "4"],
     [".", ".", ".", ".", ".", ".", ".", ".", ".", "5"],
     [".", ".", ".", ".", ".", ".", ".", ".", ".", "6"],
     [".", ".", ".", ".", ".", ".", ".", ".", ".", "7"],
     [".", ".", ".", ".", ".", ".", ".", ".", ".", "8"]
     ]
    for line in level_data:
        if 0 < level_data.index(line) < 5:
            for char in range(len(line)-1):
                if 1 < char < 8:
                    _rdm = random.randint(1, 20)
                    if _rdm > 16:
                        line[char] = "$"
                    elif _rdm > 10:
                        line[char] = "@"
                    elif _rdm > 1:
                        line[char] = "#"
    return level_data


# For Debugging purposes
# print(generate_level())

