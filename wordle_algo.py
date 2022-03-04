def solve_worldle(date_of_challenge):
    import datetime

    Ma = open('/Users/joao/Documents/Python/wordleSolver/corpus/wordle_av.txt', 'r').read().split('\n')
    Ga = datetime.datetime(2021, 6, 19, 0, 0, 0, 0).replace(hour=0, minute=0, second=0, microsecond=0)
    date_of_challenge_ = date_of_challenge.replace(hour=0, minute=0, second=0, microsecond=0)

    diff = date_of_challenge_ - Ga
    pos_ = int(round(diff.total_seconds() * 1000 / 864e5))

    pos = pos_ % len(Ma)

    return Ma[pos]
