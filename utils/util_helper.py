def process_params(param, default, all_args):
    value = default

    if param in all_args:
        sub_val = all_args[all_args.find(param) + len(param):]
        sub_val = sub_val[:sub_val.find('--') if '--' in sub_val else len(sub_val)].strip()

        # SPECIFIC APP cases (try to avoid)
        if param == '--game':
            if '[' in sub_val: sub_val = sub_val[1:-1]
            value = []
            for e in sub_val.split(','):
                if e.count('-') == 1:
                    fr_, to_ = int(e.split('-')[0].strip()), int(e.split('-')[1].strip())
                    value += list(range(fr_, to_ + 1))
                elif e.count('-') == 2:
                    import datetime
                    value.append(datetime.datetime.strptime(e.strip(), '%Y-%m-%d'))
                elif e.count('-') == 0:
                    value.append(int(e))

            return value

        if type(value) == bool:
            assert sub_val in ['True', 'False'], f'error in param: {param} should be True or False'
            value = True if sub_val == 'True' else False
        elif type(value) == int:
            value = int(sub_val)
        elif type(value) == list:
            # remove parenteses
            sub_val = sub_val[1:-1]
            if '[' not in sub_val: sub_val = [a.strip() for a in sub_val.split(',')]
            else: sub_val = [[int(b) for b in a.replace('[','').replace(']','').split(',')] for a in sub_val.replace(' ','').split('],[')]
            value = sub_val
        else:
            value = sub_val.replace("'", '')

    return value


def print_colored(word_try, results):
    W = '\033[0m'  # white (normal)
    R = '\033[31m'  # red
    G = '\033[32m'  # green
    O = '\033[33m'  # orange
    dict_color = {1: G, 0: O, -1:R}
    print('tried: ', end='')
    for l, c in zip(word_try, results):
        print(f"{dict_color[c]}{l}{dict_color[c]}", end='')
    print(f"{W}")


def print_time(start, stop):
    duration = stop - start

    h = int(duration // (60 * 60))
    duration -= h * (60 * 60)
    m = int(duration // 60)
    duration -= m * 60
    s = int(duration)
    duration -= s
    ms = f"{duration:.2f}".split('.')[-1]

    return f"{str(h).zfill(2)}:{str(m).zfill(2)}:{str(s).zfill(2):}.{ms}"

