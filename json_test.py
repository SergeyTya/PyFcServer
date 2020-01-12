import json


def gen(max, val=0):
    while val <= max:
        val += 1
        if val == max: val = 0
        yield val


gnr = gen(100)
while True:
    print(next(gnr))
