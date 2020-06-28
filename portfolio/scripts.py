import datetime
#import numpy as np
import re
import timeit


def percent_profit(today_cash, invest_cash):
    today_cash = float(today_cash)
    invest_cash = float(invest_cash)
    result_percent = (today_cash - invest_cash) / invest_cash * 100
    return round(result_percent, 2)


def days(d1, d2):
    if d1 == d2:
        return 0
    return int(str(d2 - d1).split()[0])


def dict_days_invest(invest_list1, date1):
    tmp = {}
    for i in range(len(invest_list1)):
        d = days(invest_list1[i][1], date1)
        if d in tmp:
            tmp[d] += float(invest_list1[i][0])
        else:
            tmp[d] = float(invest_list1[i][0])
    return tmp


'''
def year_percent_roots(invest_list, today_cash, date=datetime.date.today()):
    # invets_touple - список списков
    # (внесенное количество денег, дата внесения класса datetime.date)
    tmp = {}
    for i in range(len(invest_list)):
        d = days(invest_list[i][1], date)
        if d in tmp:
            tmp[d] += float(invest_list[i][0])
        else:
            tmp[d] = float(invest_list[i][0])
    out = [0 for i in range(1 + max(list(tmp.keys())))]
    for i in tmp:
        out[i] = tmp[i]
    out[0] = float(-today_cash)
    out = out[::-1]
    out = np.roots(out)
    for i in range(len(out)):
        if re.match(r'\(\d.*0j\)$', str(out[i])):
            return float('{:.2f}'.
                         format((float(str(out[i])[1:-4]) - 1) * 365 * 100))

    return None
'''

def year_profit_approx(invest_list, today_cash, date=datetime.date.today()):

    def cacl_cash(dict_invest1, percent):
        n = 1 + percent / 100 / 365
        return sum([dict_invest1[i] * n ** i for i in dict_invest])

    dict_invest = dict_days_invest(invest_list, date)
    EPS = 1
    INCREMENT = 30
    today_cash = today_cash
    # invest_cash = sum([i[0] for i in invest_list])
    result_percent = 5
    delta_percent = 5

    tmp = cacl_cash(dict_invest, result_percent)
    previous_state = tmp > today_cash
    current_state = tmp > today_cash
    delta_percent *= (-1)**current_state
    today_cash = float(today_cash)
    while abs(tmp - today_cash) > EPS and INCREMENT:
        INCREMENT -= 1
        if previous_state != current_state:
            previous_state = current_state
            delta_percent -= delta_percent / 2
            delta_percent *= -1
        result_percent += delta_percent
        tmp = cacl_cash(dict_invest, result_percent)
        current_state = tmp > today_cash
    return round(result_percent, 2)


def year_percent_profit(*args, **kwargs):
    return year_profit_approx(*args, **kwargs)


def test_year_profit(f):
    t = [[49191, datetime.date(2019, 10, 10)],
         [29740, datetime.date(2019, 10, 21)],
         [40149, datetime.date(2019, 10, 21)],
         [55000, datetime.date(2019, 10, 23)],
         [202500, datetime.date(2019, 11, 29)],
         [100000, datetime.date(2019, 12, 23)],
         [50000, datetime.date(2020, 1, 19)],
         [55000, datetime.date(2020, 2, 20)], ]
    print(f(t, 600000, datetime.date(2020, 5, 14)))
    # answer - 6.97


if __name__ == "__main__":
    print('year_percent_roots:')
    a = timeit.default_timer()
    test_year_profit(year_percent_roots)
    print((timeit.default_timer() - a), 's')
    a = timeit.default_timer()
    print('test_year_approx:')
    test_year_profit(year_profit_approx)
    print((timeit.default_timer() - a), 's')
    test_year_profit(year_percent_profit)
    pass
