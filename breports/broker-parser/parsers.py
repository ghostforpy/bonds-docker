import tinkoff_xls_scripts
from datetime import datetime
from decimal import InvalidOperation
from decimal import Decimal


class WrongParser(Exception):
    pass


class FileNotSupported(Exception):
    pass


class TinkoffParserXLS:
    """ class for parsing broker reports XLS-format"""
    SECTIONS = tinkoff_xls_scripts.SECTIONS
    SECTIONS_LIST = tinkoff_xls_scripts.SECTIONS_LIST
    SHEET_NAME = tinkoff_xls_scripts.SHEET_NAME
    SECTIONS_NAMES = tinkoff_xls_scripts.SECTIONS_NAMES
    CURRENCIES = tinkoff_xls_scripts.CURRENCIES

    def __init__(self, filename):
        self.filename = filename
        self.book = tinkoff_xls_scripts.get_book(self.filename)
        self.sheet = self._get_sheet()

        if not self.verify():
            raise WrongParser

        self.period = tinkoff_xls_scripts.get_period(self.sheet)
        self.secutities_dict_ISIN_by_shortname = tinkoff_xls_scripts. \
            get_secutities_dict_ISIN_by_shortname(self.sheet)
        self.transactions = self._get_transactions()
        self.outstanding_transactions = self._get_outstanding_transactions()

        self.col_names_section_transactions = tinkoff_xls_scripts.get_column_names_in_section(
            self.sheet, self.SECTIONS_NAMES['section_transactions'])

        self.section_operation_RUB = tinkoff_xls_scripts.get_data_by_section(
            self.sheet, self.SECTIONS_NAMES['section_operation_RUB'])
        self.section_operation_USD = tinkoff_xls_scripts.get_data_by_section(
            self.sheet, self.SECTIONS_NAMES['section_operation_USD'])

        self.col_names_section_operation_RUB = tinkoff_xls_scripts.get_column_names_in_section(
            self.sheet, self.SECTIONS_NAMES['section_operation_RUB'])

        self.invest_operations = self._get_invest_operations()
        self.profit_operations = self._get_profit_operations()
        self.broker_tax_operations = self._get_broker_tax_operations()
        self.amortisation_operations = self._get_amortisations()
        self.securities_movement = self._get_securities_movement()
        self.securities_info = self._get_securities_info()
        self.repo_transactions = self._get_repo_transactions()
        self.profit_repo = self._get_profit_repo()
        self.outstanding_repo_transactions = self._get_outstanding_repo_transactions()
        self._parce()

    def verify(self):
        if not tinkoff_xls_scripts.verify_broker_name(self.sheet):
            return False
        return True

    def _get_sheet(self):
        if self.SHEET_NAME in tinkoff_xls_scripts.return_sheets(self.book):
            return self.book.sheet_by_name(self.SHEET_NAME)
        else:
            raise WrongParser

    def _get_outstanding_repo_transactions(self):
        transactions = self.outstanding_transactions
        return [i for i in transactions if i['action'].startswith('РЕПО')]

    def _get_securities_movement(self):
        data = tinkoff_xls_scripts.get_data_by_section(
            self.sheet, self.SECTIONS_NAMES['securities_movement']
        )
        return_decimal = tinkoff_xls_scripts.return_decimal_replase_comma_to_dot
        result = list()
        for i in data:
            temp = dict()
            temp['shortname'] = i[0]
            temp['secid'] = i[1]
            try:
                temp['isin'] = self.secutities_dict_ISIN_by_shortname[i[0]]
            except KeyError:
                temp['isin'] = ''
            temp['depository'] = i[2]
            temp['incoming_balance'] = return_decimal(i[3])  # входящий остаток
            temp['crediting'] = return_decimal(i[4])  # зачисление
            temp['writeoff'] = return_decimal(i[5])  # списание
            # плановый исходящий остаток с учетом режима торгов
            temp['outgoing_balance'] = return_decimal(i[7])
            result.append(temp)
        return result

    def _get_securities_info(self):
        data = tinkoff_xls_scripts.get_data_by_section(
            self.sheet, self.SECTIONS_NAMES['securities']
        )
        return_decimal = tinkoff_xls_scripts.return_decimal_replase_comma_to_dot
        result = list()
        for i in data:
            temp = dict()
            temp['shortname'] = i[0]
            temp['secid'] = i[1]
            temp['isin'] = i[2]
            temp['regnumber'] = i[3]
            temp['emitent'] = i[4]
            temp['type'] = i[5]
            try:
                temp['facevalue'] = return_decimal(i[6])
            except:
                temp['facevalue'] = None
            temp['currency'] = i[7]
            result.append(temp)
        return result

    def _get_broker_tax_operations(self):
        result = dict()
        for currency in self.CURRENCIES:
            data = tinkoff_xls_scripts.get_broker_tax_operations(
                self.sheet, currency=currency)
            t = list()
            for i in data:
                temp = dict()
                temp['date'] = i[0]
                temp['time'] = i[1]
                temp['execution_date'] = i[2]
                temp['operation'] = i[3]
                temp['credited_amount'] = i[4]
                temp['withdrawal_amount'] = i[5]
                temp['ihash'] = hash(tuple(i))
                t.append(temp)
            if t:
                result[currency] = t
        return result

    def _return_transactions(self, data):
        return_decimal = tinkoff_xls_scripts.return_decimal_replase_comma_to_dot
        result = list()
        for i in data:
            temp = dict()
            temp['deal_number'] = i[0]
            temp['order_number'] = i[1]
            temp['date'] = datetime.strptime(i[2], "%d.%m.%Y").date()
            temp['time'] = datetime.strptime(i[3], "%H:%M:%S").time()
            temp['stock_market'] = i[4]
            temp['market_mode'] = i[5]
            temp['action'] = i[6]
            temp['shortname'] = i[7]
            try:
                temp['isin'] = self.secutities_dict_ISIN_by_shortname[i[7]]
            except KeyError:
                temp['isin'] = ''
            temp['code'] = i[8]
            temp['price'] = return_decimal(i[9])
            temp['currency'] = i[10]
            temp['count'] = return_decimal(i[11])
            temp['total_cost_without_nkd'] = return_decimal(i[12])
            temp['nkd'] = return_decimal(i[13])
            temp['total_cost'] = return_decimal(i[14])
            temp['setlement_currency'] = i[15]
            temp['broker_commission'] = return_decimal(i[16])
            temp['commission_currency'] = i[17]
            temp['stock_market_commission'] = return_decimal(i[18])
            temp['stock_market_commission_currency'] = i[19]
            temp['clearing_center_commission'] = return_decimal(i[20])
            temp['clearing_center_commission_currency'] = i[21]
            try:
                temp['repo_rate_percent'] = return_decimal(i[22])
            except InvalidOperation:
                temp['repo_rate_percent'] = ''
            temp['contractor'] = i[23]
            temp['execution_date'] = datetime.strptime(i[24], "%d.%m.%Y").date()
            temp['ihash'] = hash(tuple(i[:22]))
            result.append(temp)
        return result

    def _get_outstanding_transactions(self):
        data = tinkoff_xls_scripts.get_data_by_section(
            self.sheet, self.SECTIONS_NAMES['section_outstanding_transactions']
        )
        return self._return_transactions(data)

    def _get_transactions(self):
        data = tinkoff_xls_scripts.get_data_by_section(
            self.sheet, self.SECTIONS_NAMES['section_transactions']
        )
        result = [i for i in data if not i[6].startswith('РЕПО')]
        return self._return_transactions(result)

    def _get_repo_transactions(self):
        data = tinkoff_xls_scripts.get_data_by_section(
            self.sheet, self.SECTIONS_NAMES['section_transactions']
        )
        result = [i for i in data if i[6].startswith('РЕПО')]
        return self._return_transactions(result)

    def _get_profit_repo(self):
        data = self.repo_transactions
        data_repo_no_zero_percent = [i for i in data if i['repo_rate_percent'] != 0]
        result = dict()
        for i in [j for j in data_repo_no_zero_percent if j['action'].endswith('Покупка')]:
            temp = dict()
            total_cost_without_nkd = i['total_cost_without_nkd']
            days = (i['execution_date'] - i['date']).days
            p = Decimal(0.5 / 100 / 365 * days) * total_cost_without_nkd
            temp['cash'] = p.quantize(Decimal('1.00'))
            temp['deal_number'] = i['deal_number']
            temp['date'] = i['execution_date']
            temp['action'] = 'profit_REPO'
            temp['tax'] = Decimal(0)
            temp['isin'] = i['isin']
            temp['currency'] = i['currency']
            if temp['currency'] not in result:
                result[temp['currency']] = list()
            temp['ihash'] = hash(tuple(i))
            result[temp['currency']].append(temp)
        return result

    def _get_invest_operations(self):
        result = dict()
        for currency in self.CURRENCIES:
            data = tinkoff_xls_scripts.get_invest_operations(
                self.sheet, currency=currency)
            t = list()
            for i in data:
                temp = dict()
                temp['date'] = i[2]
                temp['action'] = i[3] == 'Пополнение счета'
                temp['cash'] = i[4]
                temp['currency'] = currency
                temp['ihash'] = hash(tuple(i))
                t.append(temp)
            if t:
                result[currency] = t
        return result

    def _get_profit_operations(self):
        result = dict()
        for currency in self.CURRENCIES:
            data = tinkoff_xls_scripts.get_profit_oprations(
                self.sheet,
                currency=currency)
            t = list()
            for i in tinkoff_xls_scripts.concat_profit_operations(data):
                temp = dict()
                temp['date'] = i[2]
                temp['action'] = i[3]
                temp['cash'] = i[4]
                temp['tax'] = i[5]
                temp['isin'] = i[6]
                temp['currency'] = currency
                temp['ihash'] = hash(tuple(i))
                t.append(temp)
            if t:
                result[currency] = t
        return result

    def _get_amortisations(self):
        result = dict()
        for currency in self.CURRENCIES:
            data = tinkoff_xls_scripts.get_amortisation_operations(
               self.sheet, currency=currency)
            t = list()
            for i in data:
                temp = dict()
                temp['date'] = i[2]
                temp['full'] = i[3] == 'Погашение облигации'
                temp['cash'] = i[4]
                temp['isin'] = i[6]
                temp['ihash'] = hash(tuple(i))
                t.append(temp)
            if t:
                result[currency] = t
        return result

    def _parce(self):
        pass

    def __str__(self):
        return 'parser for ' + self.filename


AVAILEBLE_PARSERS = [TinkoffParserXLS]


if __name__ == '__main__':
    filename = 'broker_reports/broker-report-slava.xlsx'
    parser = TinkoffParserXLS(filename)
    print(parser)
    data = parser.profit_repo
    print(data)
    print('\n'.join([str(j) for j in data]))
