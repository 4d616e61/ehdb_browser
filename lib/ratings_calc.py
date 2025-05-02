import math

decision_space = []

for i in range(1,11):
    decision_space.append(i / 2)





def avg(lst):
    if len(lst) == 0:
        return 0
    res = 0
    for v in lst:
        res += v
    return res / len(lst)


def avg_add(lst, val):
    if len(lst) == 0:
        return val
    res = val
    for v in lst:
        res += v
    return res / (len(lst) + 1)


def cmp_rounded(v0, v1):
    return round(v0, 2) == round(v1, 2)


def get_next_choice(cur_list, target):
    min_delta = 10000
    best_choice = -1
    for v in decision_space:
        cur_res = avg_add(cur_list, v)
        delta = abs(target - cur_res)
        if delta < min_delta:
            min_delta = delta
            best_choice = v
    return best_choice


def get_least_steps(target):

    votes = []
    while (not cmp_rounded(avg(votes), target)):
        choice = get_next_choice(votes, target)
        votes.append(choice)
    return len(votes)



