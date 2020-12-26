import xlrd
import datetime
from decimal import Decimal
import re

DIR_TO_FILE = 'broker_reports'
SHEET_NAME = 'broker_rep'
BROKER_NAME = 'Брокер: АО «Тинькофф Банк», ИНН/КПП 7710140679/773401001'
BROKER_NAME_ROW = 1
PERIOD_ROW = 5
SECTIONS = {
    '1.1': 'Информация о совершенных и исполненных сделках на конец отчетного периода',
    '1.2': 'Информация о неисполненных сделках на конец отчетного периода',
    '1.3': 'Сделки за расчетный период, обязательства из которых прекращены  не в результате исполнения',
    '1.4': 'Информация об изменении расчетных параметров сделок РЕПО',
    '2.': 'Операции с денежными средствами',
    'RUB': 'Операции с денежными средствами в валюте RUB',
    'USD': 'Операции с денежными средствами в валюте USD',
    'EUR': 'Операции с денежными средствами в валюте EUR',
    '3.1': 'Движение по ценным бумагам инвестора',
    '3.2': 'Движение по производным финансовым инструментам',
    '3.3': 'Информация о позиционном состоянии по производным финансовым инструментам из таблицы',
    '4.1': 'Информация о ценных бумагах',
    '4.2': 'Информация об инструментах, не квалифицированных в качестве ценной бумаги',
    '4.3': 'Информация о производных финансовых инструментах',
    '5.': 'Информация о торговых площадках',
    '6.': 'Расшифровка дополнительных кодов используемых в отчете',
    'АО «Тинькофф Банк»': ''
}
CURRENCIES = ['RUB', 'USD', 'EUR']

SECTIONS_NAMES = {
    'section_transactions': '1.1',
    'section_outstanding_transactions': '1.2',
    # '1.3' : 'Сделки за расчетный период, обязательства из которых прекращены  не в результате исполнения',
    # '1.4' : 'Информация об изменении расчетных параметров сделок РЕПО',
    'section_money_movement': '2.',
    'section_operation_RUB': 'RUB',
    'section_operation_USD': 'USD',
    'section_operation_EUR': 'EUR',
    'securities_movement': '3.1',
    # '3.2' : 'Движение по производным финансовым инструментам',
    # '3.3' : 'Информация о позиционном состоянии по производным финансовым инструментам из таблицы',
    'securities': '4.1',
    # '4.2' : 'Информация об инструментах, не квалифицированных в качестве ценной бумаги',
    # '4.3' : 'Информация о производных финансовых инструментах',
    # '5.' : 'Информация о торговых площадках',
    # '6.' : 'Расшифровка дополнительных кодов используемых в отчете',
    'АО «Тинькофф Банк»': ''
}
SECTIONS_LIST = list(SECTIONS.keys())


class LastRow(Exception):
    pass


def get_book(filename):
    try:
        return xlrd.open_workbook(filename=filename)
    except FileNotFoundError:
        print('no file')
        return None


def return_sheets(book):
    return [i.name for i in book.sheets()]


def get_broker_name(sheet):
    row = sheet.row_values(BROKER_NAME_ROW)
    return row[0]


def verify_broker_name(sheet):
    name = get_broker_name(sheet)
    return name == BROKER_NAME


def get_period(sheet):
    cell_value = sheet.row_values(PERIOD_ROW)[0]
    pattern = '\d\d\.\d\d\.\d{4}'
    period = [datetime.datetime.strptime(i, "%d.%m.%Y").date()
              for i in re.findall(pattern, cell_value)]
    period.sort()
    return period


def get_row_of_section_name(sheet, section):
    # возвращает номер строки с названием конкретного раздела
    count = 1 if section in CURRENCIES else 0
    for rownum in range(sheet.nrows):
        row = sheet.row_values(rownum)
        c_el = row[0]
        if c_el.startswith(section):
            if count:
                # пропуск первого вхождения для подразделов из раздела 2.
                count -= 1
            else:
                return rownum
    return False


def get_row_of_next_section(sheet, section):
    # возвращает номер строки с названием следующего раздела
    # если раздел последний генерирует ошибку LastRow
    next_section_index = SECTIONS_LIST.index(section)

    try:
        next_section = SECTIONS_LIST[next_section_index + 1]
    except IndexError:
        raise LastRow
    num = get_row_of_section_name(sheet, next_section)
    i = 1
    while not num:
        num = get_row_of_section_name(sheet,
                                      SECTIONS_LIST[next_section_index + i])
        i += 1
    return num


def row_or_col_is_empty(row_or_col, is_row=False, is_col=False):
    # возвращает True, если строка или столбец пустой по всей таблице секции
    # в строке проверяет только первые LENGHT_NUM ячеек
    LENGHT_NUM = 50
    if is_col == is_row:
        raise Exception('must be difference')
    lenght = LENGHT_NUM if is_row else len(row_or_col)
    for i in range(lenght):
        if row_or_col[i] != '':
            return False
    return True


def get_row_slice_of_section(sheet, section):
    # возвращает лист листов из строк конкретной секции,
    # фильтрует полностью пустые строки и строки, в которых находится
    # только номер страницы документа
    first_row = get_row_of_section_name(sheet, section) + 2
    last_row = get_row_of_next_section(sheet, section) - 1
    result = list()
    for rownum in range(first_row, last_row + 1):
        row = sheet.row_values(rownum)
        if row_or_col_is_empty(row, is_row=True):
            # пропуск пустых строк
            continue
        result.append(row)
    return result


def get_column_names_in_section(sheet, section):
    # возвращает лист из наименований столбцов конкретной секции
    names_row = get_row_of_section_name(sheet, section) + 1
    list_names = sheet.row_values(names_row)
    result = [i.replace('\n', '') for i in list_names]
    return result


def get_data_by_section(sheet, section, append_row_names=False):
    # возвращает лист листов, состоящий из строк конкретной секции,
    # при необходимости можно добавить шапку из наименований,
    # фильтрует полностью пустые столбцы
    try:
        data = get_row_slice_of_section(sheet, section)
    except LastRow:
        return False
    result = list()
    if append_row_names:
        row_names = get_column_names_in_section(sheet, section)
        result.append(row_names)
    for i in data:
        result.append(i)
    if not result:
        return ''

    for col in reversed(range(len(result[0]))):
        if row_or_col_is_empty([row[col] for row in result], is_col=True):
            for row in result:
                del row[col]
    # при анализе секции 2 происходит удаление пустых столбцов,
    # изза этого смещается таблица
    if section in CURRENCIES:
        if len(result[0]) != 7:
            [i.insert(0, '') for i in result]
            [i.insert(0, '') for i in result]
    if section == '4.1':
        if len(result[0]) != 8:
            [i.insert(3, '') for i in result]
    return result


def parce_section_2(sheet, currency, mode):
    section = currency
    data = get_data_by_section(sheet, section)
    result = list()
    if mode == 'invest_operations':
        actions = ['Пополнение счета', 'Вывод средств']
    elif mode == 'profit_operations':
        actions = ['Налог (дивиденды)',
                   'Выплата дивидендов',
                   'Налог (купонный доход)',
                   'Выплата купонов']
        securities = get_secutities_dict_ISIN_by_shortname(sheet)
    elif mode == 'broker_tax_operations':
        actions = ['Комиссия по тарифу']
    elif mode == 'amortisation_operations':
        actions = ['Частичное погашение облигации (амортизация номинала)',
                   'Погашение облигации']
        securities = get_secutities_dict_ISIN_by_shortname(sheet)
    for row in data:
        if row[3] in actions:
            temp = list()
            try:
                temp.append(datetime.datetime.strptime(row[0], "%d.%m.%Y").date())
                temp.append(datetime.datetime.strptime(row[1], "%H:%M:%S").time())
            except ValueError:
                temp.append('')
                temp.append('')
            temp.append(datetime.datetime.strptime(row[2], "%d.%m.%Y").date())
            temp.append(row[3])
            temp.append(Decimal(row[4].replace(',', '.')))
            temp.append(Decimal(row[5].replace(',', '.')))
            try:
                security_isin = securities[row[6].split('/')[0]]
                temp.append(security_isin)
                count = Decimal(row[6].split('/')[1].split()[0])
                temp.append(count)
            except (UnboundLocalError, TypeError):
                temp.append('')
                temp.append('')
            result.append(temp)
    return result


def same_rows(row1, row2):
    for k in [0, 1, 2, 6]:
        if row1[k] != row2[k]:
            return False
    return True


def return_decimal_replase_comma_to_dot(s):
    return Decimal(s.replace(',', '.'))


def concat_profit_operations(data):
    result = list()
    for i in range(len(data)):
        k = False
        for j in range(i + 1, len(data)):
            try:
                if same_rows(data[i], data[j]):

                    if 'Выплата купонов' in data[i] or \
                       'Выплата дивидендов' in data[i]:
                        main_row = data[i]
                        tax_row = data[j]
                    else:
                        main_row = data[j]
                        tax_row = data[i]
                    temp = main_row[:3]
                    temp.append('profit')
                    temp.append(main_row[4])
                    temp.append(tax_row[5])
                    temp.append(main_row[6])
                    result.append(temp)
                    k = True
                    del data[j]
            except IndexError:
                continue
        if not k:
            try:
                temp = data[i][:3]
                temp.append('profit')
                temp.append(data[i][4])
                temp.append(Decimal(0))
                temp.append(data[i][6])
                result.append(temp)
            except IndexError:
                continue
    return result


def get_invest_operations(sheet, currency):
    return parce_section_2(sheet, currency, 'invest_operations')


def get_profit_oprations(sheet, currency):
    return parce_section_2(sheet, currency, 'profit_operations')


def get_broker_tax_operations(sheet, currency):
    return parce_section_2(sheet, currency, 'broker_tax_operations')


def get_amortisation_operations(sheet, currency):
    return parce_section_2(sheet, currency, 'amortisation_operations')


def get_securities(sheet):
    section = SECTIONS_NAMES['securities']
    data = get_data_by_section(sheet, section, append_row_names=False)
    return data


def get_secutities_dict_ISIN_by_shortname(sheet):
    data = get_securities(sheet)
    result = {row[0]: row[2] for row in data}
    return result
