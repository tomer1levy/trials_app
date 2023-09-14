def mean(list1):
    return round(sum(list1) / len(list1), 2)


def std(list1):
    res = 0
    av = mean(list1)
    for num in list1:
        res += (num - av)**2
    return (res / (len(list1) - 1)) ** 0.5
