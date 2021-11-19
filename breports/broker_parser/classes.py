from __future__ import annotations
from .parsers import (TinkoffParserXLS, AVAILEBLE_PARSERS,
                      FileNotSupported, WrongParser)
from decimal import Decimal
from datetime import time, date, datetime
# import datetime
from copy import deepcopy


class BrokerReport:
    """main class
    Для анализа парсер должен предоставлять следующие атрибуты:
    - атрибут period - list of datetime.datetime.date дат начала и конца отчета
    - атрибут transactions, который возвращает список словарей транзакций (без учета РЕПО)
    для преобразования в экземпляры класса Transaction
    - атрибут outstanding_transactions, который возвращает список словарей неисполненных
    транзакций(без учета РЕПО), для преобразования в экземпляры класса Transaction
    - атрибут invest_operations, который возвращает словарь (ключами являются наименования валют)
    списков операций для преобразования в экземпляры класса InvestOperation
    - атрибут profit_operations, который возвращает словарь (ключами являются наименования валют)
    списков операций получения доходов (купоны, дивиденды) для преобразования в экземлпяры
    класса Profit
    - атрибут profit_repo, который возвращает словарь (ключами являются наименования валют)
    списков операций получения доходов, полученных от сделок РЕПО для преобразования
    в экземпляры класса ProfitREPO
    - атрибут amortisation_operations, который возвращает словарь (ключами являются
    наименования валют) списков операций амортизаций по облигациям для преобразования
    в экземпляры класса Amortisation
    - атрибут broker_tax_operations, который возвращает словарь (ключами являются
    наименования валют) списков операций уплаты брокеру комиссий за обслуживание счета
    для преобразования в экземпляры класса BrokerTax
    - атрибут repo_transactions, который возвращает список словарей транзакций РЕПО
    для преобразования в экземпляры класса Transaction
    - атрибут outstanding_repo_transactions, который возвращает список словарей неисполненных
    транзакций РЕПО для преобразования в экземпляры класса Transaction
    - атрибут securities_info, который возвращает список словарей ценных бумаг
    для преобразования в экземпляры класса Security
    - атрибут securities_movement, который возвращает список словарей движений
    по ценным бумагам для преобразования в экземпляры класса SecurityMovement.
    - атрибут money_movement, который возвращает словарь (ключами
    являются валюты) словарей движений денежных средств
    для преобразования в экземпляры класса MoneyMovement.
    Парсер должен генерировать исключения:
    - WrongParser, если предложенный файл не соответствует парсеру,
    проверка должна происходить при инициализации экземпляра класса парсера.
    Парсер должен быть добавлен в список parsers.AVAILEBLE_PARSERS.
    """

    def __init__(self, parser_class, filename):
        self.parser_class = parser_class
        self.filename = filename
        self.filenames = [filename]
        try:
            self.parser = parser_class(filename)
        except WrongParser:
            parser_not_found = True
            AVAILEBLE_PARSERS.remove(parser_class)
            for i in AVAILEBLE_PARSERS:
                try:
                    self.parser = i(filename)
                except WrongParser:
                    continue
                self.parser_class = i
                parser_not_found = False
            if parser_not_found:
                raise FileNotSupported

        self.period = self.parser.period  # list of datetime.datetime.date
        self.transactions = self._get_transactions()  # list
        self.outstanding_transactions = self._get_outstanding_transactions()  # list
        self.invest_operations = self._get_invest_operations()  # dict
        self.profit_operations = self._get_profits()  # dict
        self.repo_profit = self._get_repo_profits()  # dict
        self.amortisations = self._get_amortisations()  # dict
        self.broker_taxes = self._get_broker_taxes()  # dict
        self.repo_transactions = self._get_repo_transactions()  # list
        self.outstanding_repo_transactions = self._get_outstanding_repo_transactions()  # list
        self.securities_info = self._get_securities_info()  # list
        self.securities_movement = self._get_securities_movement()  # list
        self.money_movement = self._get_money_movement()  # dict

    def __str__(self):
        return 'Broker report for ' + ', '.join(self.filenames)

    def __add__(self, other):
        if self.parser_class != other.parser_class:
            raise Exception('parser_class must be the same')
        # если начало второго отчета раньше чем первого,
        # переставить местами
        if self.period[0] > other.period[0]:
            return other + self
        period = [self.period, other.period]
        # period.sort(key=lambda x: x[0])
        # уже выполнено выше путём перестановки мест слагаемых
        if period[0][1] >= period[1][1]:
            # второй отчет полностью есть во втором,
            # складывать нет необходимости
            return self
        if (period[1][0] - period[0][1]).days > 1:
            # начало второго отчета должно быть не следующего дня после первого
            raise Exception('reports diff must be less or equal then 1 day')
        # секция объединения имен файлов
        self.filenames.extend(other.filenames)
        # секция объединения периода
        self.period = [period[0][0], period[1][1]]

        def concat_list_sections_sort_date(self_obj, other_obj, attr):
            self_attr = getattr(self_obj, attr).copy()
            other_attr = getattr(other_obj, attr).copy()
            self_attr.extend(other_attr)
            try:
                self_attr = list(set(self_attr))
            except TypeError:  # пустой список
                self_attr = list()
            try:
                # не работает сортировка
                self_attr.sort(key=lambda x: x.date)
            except AttributeError:
                # не работает сортировка
                self_attr.sort(key=lambda x: x.shortname)  # для Security
            setattr(self, attr, self_attr)

        # секция объединения транзакций
        concat_list_sections_sort_date(self, other, 'transactions')
        # секция объединения транзакций репо
        concat_list_sections_sort_date(self, other, 'repo_transactions')
        # секция объединения информации о ценных бумагах
        concat_list_sections_sort_date(self, other, 'securities_info')

        def concat_dict_sections_sort_date(self_obj, other_obj, attr):
            self_attr = getattr(self_obj, attr).copy()
            other_attr = getattr(other_obj, attr).copy()

            currency_list = list(self_attr.keys())
            currency_list.extend(list(other_attr.keys()))
            try:
                currency_list = set(currency_list)
            except TypeError:  # пустой список
                currency_list = list()
            for i in currency_list:
                try:
                    self_attr[i].extend(other_attr[i])
                except KeyError:
                    self_attr[i] = other_attr[i]
                try:
                    self_attr[i] = list(set(self_attr[i]))
                except TypeError:  # пустой список
                    self_attr[i] = list()
                self_attr[i].sort(key=lambda x: x.date)
            setattr(self, attr, self_attr)
        # секция объединения операций пополнения счета/вывода средств
        concat_dict_sections_sort_date(self, other, 'invest_operations')
        # секция объединения операций получения дохода
        concat_dict_sections_sort_date(self, other, 'profit_operations')
        # секция объединения операций получения дохода по сделкам репо
        concat_dict_sections_sort_date(self, other, 'repo_profit')
        # секция объединения операций амортизаций облигаций
        concat_dict_sections_sort_date(self, other, 'amortisations')
        # секция объединения операций уплаты комиссий за брокерское обслуживание
        concat_dict_sections_sort_date(self, other, 'broker_taxes')

        # секция объединения securities_movement
        differense = list(filter(lambda x: x.isin not in map(
            lambda x: x.isin, self.securities_movement),
            other.securities_movement))
        for i in self.securities_movement:
            try:
                i = i + list(filter(
                    lambda x: x.isin == i.isin, other.securities_movement))[0]
            except IndexError:
                # если в прибавляемом списке нет движения,
                # по ценной бумаге переходим к следующей
                continue
            transactions_crediting = [
                k for k in self.transactions
                if k.action == 'Покупка' and k.isin == i.isin]
            i.crediting = sum([k.count for k in transactions_crediting])
            transactions_writeoff = [
                k for k in self.transactions
                if k.action == 'Продажа' and k.isin == i.isin]
            i.writeoff = sum([k.count for k in transactions_writeoff])
            # если по облигации было полное погашение,
            # исходящий остаток будет равен сумме входящего и зачисления
            try:
                amortisations = [
                    k for k in self.amortisations['RUB'] if k.full and k.isin == i.isin
                    ]
            except KeyError:
                # отсутствуют амортизации по облигации
                amortisations = None
            if amortisations:
                i.writeoff = i.crediting + i.incoming_balance
        self.securities_movement.extend(differense)  # дописываем разницу

        # дописать секцию объединения money_movement

        # секция объединения неисполненных транзакций при i = 'transactions'
        # секция объединения неисполненных транзакций РЕПО при i = 'repo_transactions'
        for i in ['transactions', 'repo_transactions']:
            first_list = getattr(self, 'outstanding_' + i)
            second_list = getattr(other, 'outstanding_' + i)
            extended_set = first_list.extend(second_list)
            if not extended_set:
                continue  # если список пуст, переходим к следующей секции
            # исключить транзакции, которые исполнены
            # и есть в соответсвующем списке транзацкций
            try:
                temp = list(set(extended_set).difference(set(getattr(self, i))))
            except TypeError:  # если список исполненных транзакций пуст
                temp = list(set(extended_set))
            temp.sort(key=lambda x: x.date)
            setattr(self, 'outstanding_' + i, temp)

        return self

    def _get_transactions(self):
        data = self.parser.transactions
        result = [Transaction(**i) for i in data]
        return result

    def _get_securities_info(self):
        data = self.parser.securities_info
        result = [Security(**i) for i in data]
        return result

    def _get_securities_movement(self):
        data = self.parser.securities_movement
        result = [SecurityMovement(**i) for i in data]
        return result

    def _get_money_movement(self):
        data = self.parser.money_movement
        result = {i: MoneyMovement(**data[i]) for i in data}
        return result

    def _get_repo_transactions(self):
        data = self.parser.repo_transactions
        result = [Transaction(**i) for i in data]
        return result

    def _get_outstanding_repo_transactions(self):
        data = self.parser.outstanding_repo_transactions
        result = [Transaction(**i) for i in data]
        return result

    def _get_broker_taxes(self):
        data = self.parser.broker_tax_operations
        result = {i: [BrokerTax(**j) for j in data[i]] for i in data}
        return result

    def _get_outstanding_transactions(self):
        data = self.parser.outstanding_transactions
        result = [Transaction(**i) for i in data]
        return result

    def _get_invest_operations(self):
        data = self.parser.invest_operations
        result = {i: [InvestOperation(**j) for j in data[i]] for i in data}
        return result

    def _get_profits(self):
        data = self.parser.profit_operations
        result = {i: [Profit(**j) for j in data[i]] for i in data}
        return result

    def _get_repo_profits(self):
        data = self.parser.profit_repo
        result = {i: [ProfitREPO(**j) for j in data[i]] for i in data}
        return result

    def _get_amortisations(self):
        data = self.parser.amortisation_operations
        result = {i: [Amortisation(**j) for j in data[i]] for i in data}
        return result

    def return_base_profit(self, profits_list, since=None, to=None):
        period = self.period
        if not since:
            since = period[0]
        if not to:
            to = period[1]
        if since > to:
            since, to = period[0], period[1]
        result = {i: sum(
            map(lambda x: x.cash,
                filter(
                    lambda y: since <= y.date <= to,
                    profits_list[i]
                ))
        ) for i in profits_list}
        return {
            'total': result,
            'operations': profits_list
        }

    def total_profit(self, since=None, to=None):
        """
        Возвращает dict с суммами полученного дохода
        без учета дохода от повышения цен,
        где ключами является валюта дохода.
        Т.е. учитывается только доход от дивидендов и купонов.
        :param since: datetime.date
        :param to: datetime.date
        :return: dict
        """

        return self.return_base_profit(self.profit_operations, since, to)

    def total_profit_repo(self, since=None, to=None):
        """
        Возвращает dict с суммами полученного дохода по сделкам РЕПО,
        где ключами является валюта дохода
        :param since: datetime.date
        :param to: datetime.date
        :return: dict
        """
        return self.return_base_profit(self.repo_profit, since, to)

    def total_ndfl(self):
        """
        Возвращает dict с суммами оплаченных НДФЛ,
        где ключами является валюта оплаты
        :return: dict
        """
        profits = self.profit_operations
        result = {i: sum([j.tax for j in profits[i]]) for i in profits}
        return result

    def total_taxes(self):
        """
        озвращает dict со всеми операциями оплаты обслуживания
        брокерского счета, где ключами является валюта оплаты
        :return: dict
        """
        taxes = self.broker_taxes
        result = {i: sum([j.withdrawal_amount for j in taxes[i]]) for i in taxes}
        return result

    def non_zero_securities_movements(self):
        """
        Возвращет list с информацией о движении ценных бумаг,
        количество которых на момент составления отчета не равно 0
        :return: list
        """
        return [i for i in self.securities_movement
                if i.outgoing_balance > 0]

    def get_security_by_secid_isin(self, secid=None, isin=None):
        sec_info = self.securities_info
        for i in sec_info:
            if i.secid == secid or i.isin == isin:
                return i

    def return_none_zero_securities(self):
        """
        Возвращет list с ценными бумагами,
        количество которых на момент составления отчета не равно 0
        :return: list
        """
        sec_movements = self.non_zero_securities_movements()
        result = list()
        for i in sec_movements:
            security = self.get_security_by_secid_isin(
                secid=i.secid,
                isin=i.isin
            )
            temp = list()
            temp.append(i.outgoing_balance)
            temp.append(security)
            result.append(temp)
        return result

    def return_transactions_by_secid_isin(self,
                                          query: list):
        """
        Возвращет list со всеми транзакциями по конкретному инструменту
        :param query: list

        :return: list
        """
        transactions = self.transactions
        return [i for i in transactions if (i.code in query or i.isin in query)]

    def return_docum_by_secid_isin(self, query: list, raise_exceptions=False):
        """
        Возвращает list с транзакциями-основаниями(покупками)
        владения ценными бумагами.
        при недостаточном количестве транзакций вторым параметром возвращает
        количество ценных бумаг, которые необхидмо анализировать по предыдущим отчетам.
        Если raise_exceptions=True, при недостаточном количестве ценных бумаг
        гененрирует исключение NeedEarlierBrokerReport.
        :param query: list
        :param raise_exceptions: bool
        :return: list
        """
        transactions = self.return_transactions_by_secid_isin(query)
        transactions_buy = [
            i for i in transactions if i.action == 'Покупка'
        ]
        transactions_buy.sort(key=lambda x: x.date)
        security_movement = [
            i for i in self.securities_movement if (
                i.secid == query or i.isin == query)][0]
        outgoing_security_balance = security_movement.outgoing_balance
        result = list()
        while outgoing_security_balance > 0:
            try:
                temp = transactions_buy.pop()
            except IndexError:
                break
            result.append(temp)
            outgoing_security_balance -= temp.count
        if outgoing_security_balance > Decimal(0):
            if raise_exceptions:
                raise NeedEarlierBrokerReport
            return result, outgoing_security_balance
        return result

    def return_amortisations_by_isin(self,
                                     query,
                                     since=None,
                                     to=datetime.now().date(),
                                     raise_exceptions=False):
        """
        Вощзвращает список операций амортизаций по isin.
        query: list
        """
        security = list(filter(
            lambda x: x.isin in query, self.securities_info
        ))  # поиск бумаги по isin
        if security:
            currency = security[0].currency
        else:
            if raise_exceptions:
                raise WrongQuery
            else:
                return
        amortisations = list(filter(
            lambda x: ((x.isin in query) and (x.date < to)),
            self.amortisations[currency]
        ))
        if since:
            amortisations = list(filter(
                lambda x: x.date > since,
                amortisations
            ))
        return amortisations

    def return_profit_and_taxes_sell_bonds_by_secid_isin(self,
                                                         query,
                                                         since=None,
                                                         to=datetime.now().date(),
                                                         raise_exceptions=False):
        """
        Возвращает dict с суммой дохода (учитываются только прибыльные операции продажи),
        суммой налогооблагаемой базы (учитываются все транзакции),
        суммой комиссий брокера по операциям покупки и продажи,
        суммой налогооблазаемой базы с учетом комиссий брокера по операциям

        по конкретной ценной бумаге (query) начиная с даты(since).
        Если дата начала не задана, расчеты ведутся с начала брокерсокго отчета.
        Если дата окончания не задана расчеты ведутся до конца брокерского отчета.
        Входящий остаток по бумаге должен быть равен 0.
        При raise_exceptions=True генерирует исключения NoMovements,
        WrongQuery, NeedEarlierBrokerReport.
        :param query: str
        :param since: datetime.date
        :param to: datetime.date
        :param raise_exceptions: bool
        :return: dict or str
        """
        movement = [i for i in self.securities_movement
                    if i.secid == query or i.isin == query]
        if len(movement) == 0:  # по ценной бумаге не было движений
            if raise_exceptions:
                raise NoMovements
            return 'No movements'
        elif len(movement) > 1:  # вернулось больше 1 строки движения ценных бумаг
            if raise_exceptions:
                raise WrongQuery
            return 'Wrong query'
        if movement[0].incoming_balance != Decimal(0):
            # входящий остаток ценных бумаг должен быть равен 0
            # необходимо добавить более ранний брокерский отчет
            if raise_exceptions:
                raise NeedEarlierBrokerReport
            s = 'Wrong query, need more information,'
            s += ' upload an earlier broker report. Incoming balance must be 0.'
            return s
        transaction = self.return_transactions_by_secid_isin([query])
        sell_transactions = [i for i in transaction if i.action == 'Продажа']
        sell_transactions.sort(key=lambda x: x.deal_number)
        amortisations = self.return_amortisations_by_isin(query)
        price_amortisations = list()
        if amortisations:
            price_amortisations = list(
                filter(lambda x: not x.full, amortisations)
            )

            full_amortisation = list(filter(
                lambda x: x.full, amortisations
            ))  # выбор полного погашения облигации
            if full_amortisation:
                sell_transactions.append(full_amortisation[0])
        buy_transactions = [i for i in transaction if i.action == 'Покупка']
        buy_transactions.sort(key=lambda x: x.deal_number)
        result = {}
        for i in sell_transactions:
            count = i.count
            result[i] = list()
            while count > 0:
                if buy_transactions[0].count > count:
                    buy_transaction = deepcopy(buy_transactions)[0]
                    buy_transaction.count = count
                    buy_transaction.broker_commission = buy_transactions[0].broker_commission * \
                        count / buy_transactions[0].count
                    result[i].append(buy_transaction)
                    buy_transactions[0].count -= count
                    buy_transactions[0].broker_commission -= buy_transaction.broker_commission
                    count = 0
                elif buy_transactions[0].count <= count:
                    count -= buy_transactions[0].count
                    result[i].append(buy_transactions.pop(0))
        total_profit = Decimal(0)
        total_tax_base = Decimal(0)
        total_commissions = Decimal(0)
        if since:
            for i in list(result.keys()):
                if i.date < since:
                    del result[i]
        if to != datetime.now().date() and to is not None:
            for i in list(result.keys()):
                if i.date > to:
                    del result[i]
        if not result:
            if raise_exceptions:
                raise NoMovements
            return 'No sell since {} to {}'.format(
                since or self.period[0], to)

        def return_amortisation_sum(amortisation_list, buy_date, sell_date):
            """
            Возвращает сумму амортизаций между операциями покупки и продажи
            """
            if amortisation_list:
                amort = list(
                    filter(
                        lambda x: (
                            buy_date < x.date < sell_date
                        ), amortisation_list)
                )  # выбор амортизаций между покупкой и продажей
                return Decimal(sum(map(lambda x: (x.cash / x.count), amort)))
            return Decimal(0)
        res = dict()
        for i in result.keys():
            if isinstance(i, Amortisation):
                i.price = Decimal(i.cash / i.count)
                i.broker_commission = Decimal(0)
                i.action = 'Погашение облигаций'
        res['sells'] = deepcopy(result)
        for i in result.keys():
            commission = i.broker_commission + sum(
                map(lambda x: x.broker_commission, result[i]))
            tax_base = sum(
                map(lambda x: (
                    # уменьшение цены покупки на сумму амортизаций
                    # между датой покупки и продажи
                    (i.price - (x.price - return_amortisation_sum(
                        price_amortisations,
                        x.date,
                        i.date
                    ))
                    ) * x.count), result[i])
            )
            profit_transactions = list(
                # транзакция продажи считается прибыльной
                # если цена продажи выше, чем цена покупки,
                # уменьшенная на величину амортизаций
                filter(
                    lambda x: (
                        i.price > (
                            x.price - return_amortisation_sum(
                                price_amortisations,
                                x.date,
                                i.date)
                        )),
                    result[i]
                )
            )
            profit = sum(
                map(
                    lambda x: (
                        x.count * (
                            i.price + return_amortisation_sum(
                                price_amortisations,
                                x.date,
                                i.date) - x.price
                        )
                    ), profit_transactions
                )
            )
            result[i].append(['tax_base', tax_base])
            total_tax_base += tax_base
            result[i].append(['profit', profit])
            total_profit += profit
            result[i].append(['commission', commission])
            total_commissions += commission

        res['total_profit'] = total_profit
        res['total_tax_base_without_commissions'] = total_tax_base
        res['total_commissions'] = total_commissions
        res['total_tax_base'] = total_tax_base - total_commissions
        return res

    def all_profit_and_taxes_sell_bonds(self):
        securities = self.securities_info
        result = {}
        for i in securities:
            try:
                result[i] = self.return_profit_and_taxes_sell_bonds_by_secid_isin(
                    i.isin or i.secid, raise_exceptions=True)
            except NoMovements:
                result[i] = 'Движений или продаж по данной бумаге не было'
            except WrongQuery:
                result[i] = 'Неправильный запрос'
            except NeedEarlierBrokerReport:
                result[i] = 'По данной бумаге требуется более ранний отчет'
        return result

    def return_invests_operations_list_by_currency(
            self,
            currency='RUB'):
        """
        Возвращает list list'ов операций инвестирования,
        где каждый list = [cash, datetime.date]
        """
        invests = self.invest_operations[currency]
        result = list()
        for i in invests:
            temp = list()
            temp.append(i.cash * (-1)**(not i.action))
            temp.append(i.date)
            result.append(temp)
        return result

    def check_zero_incoming_balance_securities(self):
        """
        Возвращает True, если по всем ценным бумагам
        входящий остаток равен 0. В противном случае
        возвращает False.
        """
        sec_mov = self.securities_movement
        for i in sec_mov:
            if i.incoming_balance > Decimal(0):
                return False
        return True

    def check_zero_incoming_balance_money(self):
        """
        Возвращает True, если по валютам
        входящий остаток равен 0. В противном случае
        возвращает False.
        """
        money_mov = self.money_movement
        for i in money_mov:
            if money_mov[i].incoming_balance > Decimal(0):
                return False
        return True

    def return_non_zero_outgoing_balance_securities(self):
        """
        Возвращает список с движениями по ценным бумагам,
        исходящий остаток по которым больше 0.
        """
        result = list()
        sec_mov = self.securities_movement
        for i in sec_mov:
            if i.outgoing_balance > Decimal(0):
                result.append(i)
        return result

    def return_currency_money_movements(self):
        """
        Возвращает список с валютами,
        по которым было движение денег или
        был получен доход.
        """
        money_movement = self.money_movement
        result = set()
        for i in money_movement:
            if (money_movement[i].incoming_balance != Decimal(0) or
                money_movement[i].outgoing_balance != Decimal(0) or
                money_movement[i].plan_outgoing_balance != Decimal(0) or
                    money_movement[i].crediting != Decimal(0)):
                result.add(money_movement[i].currency)
        result.update(self.profit_operations.keys())
        return result

    def simple_dict_to_list(self, attr):
        currencies = self.return_currency_money_movements()
        result = list()
        for i in currencies:
            try:
                for j in getattr(self, attr)[i]:
                    if not hasattr(j, 'currency'):
                        setattr(j, 'currency', i)
                    result.append(j)
            except KeyError:
                continue
        return result

    def return_all_invests_operations(self):
        """
        Возвращает список со всеми ивестиционными операциями.
        """
        return self.simple_dict_to_list('invest_operations')

    def return_all_profit_operations(self):
        """
        Возвращает список со всеми доходными операциями.
        """
        return self.simple_dict_to_list('profit_operations')

    def return_list_broker_taxes(self):
        """
        Возвращает список со всеми доходными операциями.
        """
        return self.simple_dict_to_list('broker_taxes')

    def return_list_amortisations(self):
        """
        Возвращает список со всеми амортизациями.
        """
        return self.simple_dict_to_list('amortisations')


class NoMovements(Exception):
    pass


class WrongQuery(Exception):
    pass


class NeedEarlierBrokerReport(Exception):
    pass


class SimpleHashMixin:
    def __init__(self,
                 ihash=None):
        self.ihash = ihash

    def __hash__(self):
        return self.ihash

    def __eq__(self, other):
        return self.ihash == self.ihash


class Profit(SimpleHashMixin):
    def __init__(self,
                 date: date = None,
                 action: str = None,
                 cash: Decimal = None,
                 tax: Decimal = None,
                 isin: str = None,
                 currency: str = None,
                 **kwargs):
        SimpleHashMixin.__init__(self, **kwargs)
        self.date = date
        self.action = action
        self.cash = cash
        self.tax = tax
        self.isin = isin
        self.currency = currency

    def __str__(self):
        t = [self.date, self.action, self.cash,
             self.currency, self.tax, self.isin]
        return ' '.join([str(i) for i in t])

    def __repr__(self):
        return self.__str__()


class ProfitREPO(Profit):
    def __init__(self,
                 deal_number: str = None,
                 **kwargs):
        Profit.__init__(self, **kwargs)
        self.deal_number = deal_number

    def __str__(self):
        t = [self.date,
             self.action,
             self.cash,
             self.isin,
             self.deal_number]
        return ' '.join([str(i) for i in t])


class BrokerTax(SimpleHashMixin):
    def __init__(self,
                 date: date = None,
                 time: time = None,
                 execution_date: date = None,
                 operation: str = None,
                 credited_amount: Decimal = None,
                 withdrawal_amount: Decimal = None,
                 **kwargs):
        SimpleHashMixin.__init__(self, **kwargs)
        self.date = date
        self.time = time
        self.execution_date = execution_date
        self.operation = operation
        self.credited_amount = credited_amount
        self.withdrawal_amount = withdrawal_amount

    def __str__(self):
        t = [self.execution_date,
             self.operation,
             self.credited_amount,
             self.withdrawal_amount]
        return ' '.join([str(i) for i in t])

    def __repr__(self):
        return self.__str__()


class InvestOperation(SimpleHashMixin):
    """ class for operations
        currency - str,
        date - Datetime.datetime.date,
        cash - Decimal,
        action - bool,
        operation_number - str,
        order_number - str,
        time - datetim.datetime.time
    """

    def __init__(self,
                 date: date = None,
                 action: bool = None,
                 cash: Decimal = None,
                 currency: str = None,
                 **kwargs):
        SimpleHashMixin.__init__(self, **kwargs)
        self.currency = currency
        self.date = date
        self.action = action
        self.cash = cash

    def __str__(self):
        action = 'Refill' if self.action else 'Removal'
        t = [self.date, action, self.cash, self.currency]
        return ' '.join([str(i) for i in t])

    def __repr__(self):
        return self.__str__()


class Amortisation(SimpleHashMixin):
    def __init__(self,
                 date: date = None,
                 full: bool = None,
                 cash: Decimal = None,
                 isin: str = None,
                 count: Decimal = None,
                 **kwargs):
        SimpleHashMixin.__init__(self, **kwargs)
        self.cash = cash
        self.date = date
        self.isin = isin
        self.full = full
        self.count = count

    def __str__(self):
        action = 'Full' if self.full else 'Part'
        t = [self.date, action, self.cash, self.isin, self.count, 'pcs']
        return ' '.join([str(i) for i in t])

    def __repr__(self):
        return self.__str__()


class SecurityMovement:
    def __init__(self,
                 shortname: str = None,
                 secid: str = None,
                 isin: str = None,
                 depository: str = None,
                 incoming_balance: Decimal = None,
                 crediting: Decimal = None,
                 writeoff: Decimal = None,
                 outgoing_balance: Decimal = None):
        self.shortname = shortname
        self.secid = secid
        self.isin = isin
        self.depository = depository
        self.incoming_balance = incoming_balance
        self.crediting = crediting
        self.writeoff = writeoff
        self.outgoing_balance = outgoing_balance

    def __str__(self):
        return ' '.join([self.shortname,
                         self.isin or self.secid,
                         str(self.incoming_balance),
                         str(self.crediting),
                         str(self.writeoff),
                         str(self.outgoing_balance)])

    def __repr__(self):
        return self.__str__()

    def __add__(self, other):
        if (
                self.shortname != other.shortname
            ) or (
                self.isin != other.isin
        ) or (
                self.depository != other.depository):
            raise Exception(
                'SecurityMovement must have\
                 the same shortname, isin, depository')
        self.outgoing_balance = other.outgoing_balance
        self.crediting = Decimal(0)
        self.writeoff = Decimal(0)
        return self


class MoneyMovement:
    def __init__(self,
                 currency: str = None,
                 incoming_balance: Decimal = None,
                 outgoing_balance: Decimal = None,
                 plan_outgoing_balance: Decimal = None,
                 crediting: Decimal = None):
        self.currency = currency
        self.incoming_balance = incoming_balance
        self.outgoing_balance = outgoing_balance
        self.plan_outgoing_balance = plan_outgoing_balance
        self.crediting = crediting

    def __str__(self):
        return ' '.join([self.currency,
                         str(self.incoming_balance),
                         str(self.outgoing_balance),
                         str(self.plan_outgoing_balance),
                         str(self.crediting)])

    def __repr__(self):
        return self.__str__()

    def __add__(self, other):
        if self.currency != other.currency:
            raise Exception(
                'MoneyMovement must have\
                 the same currency')
        self.outgoing_balance = other.outgoing_balance
        self.crediting = other.crediting
        self.plan_outgoing_balance = other.plan_outgoing_balance
        return self


class Security:
    def __init__(self,
                 shortname: str = None,
                 secid: str = None,
                 isin: str = None,
                 regnumber: str = None,
                 type: str = None,
                 facevalue: Decimal = None,
                 currency: str = None,
                 emitent: str = None):
        self.shortname = shortname
        self.secid = secid
        self.isin = isin
        self.regnumber = regnumber
        self.type = type
        self.facevalue = facevalue
        self.currency = currency
        self.emitent = emitent

    def __str__(self):
        return ' '.join([self.shortname, self.isin or self.secid])

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash((self.isin or self.secid,
                     self.shortname,
                     self.type,
                     self.currency))

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()


class Transaction(SimpleHashMixin):
    """
    class for transactions
    """

    def __init__(self,
                 deal_number: str = None,
                 order_number: str = None,
                 execution_sign: str = None,
                 date: date = None,
                 time: time = None,
                 stock_market: str = None,
                 market_mode: str = None,
                 action: str = None,
                 shortname: str = None,
                 isin: str = None,
                 code: str = None,
                 price: Decimal = None,
                 currency: str = None,
                 count: Decimal = None,
                 total_cost_without_nkd: Decimal = None,
                 nkd: Decimal = None,
                 total_cost: Decimal = None,
                 setlement_currency: str = None,
                 broker_commission: Decimal = None,
                 commission_currency: str = None,
                 stock_market_commission: Decimal = None,
                 stock_market_commission_currency: str = None,
                 clearing_center_commission: Decimal = None,
                 clearing_center_commission_currency: str = None,
                 repo_rate_percent=None,
                 contractor: str = None,
                 execution_date: date = None,
                 **kwargs):
        SimpleHashMixin.__init__(self, **kwargs)
        self.deal_number = deal_number
        self.order_number = order_number
        self.date = date
        self.time = time
        self.stock_market = stock_market
        self.market_mode = market_mode
        self.action = action
        self.shortname = shortname
        self.isin = isin
        self.code = code
        self.price = price
        self.currency = currency
        self.count = count
        self.total_cost_without_nkd = total_cost_without_nkd
        self.nkd = nkd
        self.total_cost = total_cost
        self.setlement_currency = setlement_currency
        self.broker_commission = broker_commission
        self.commission_currency = commission_currency
        self.stock_market_commission = stock_market_commission
        self.stock_market_commission_currency = stock_market_commission_currency
        self.clearing_center_commission = clearing_center_commission
        self.clearing_center_commission_currency = clearing_center_commission_currency
        self.repo_rate_percent = repo_rate_percent
        self.contractor = contractor
        self.execution_date = execution_date

    def __str__(self):
        t = [self.date,
             self.action,
             self.isin or self.code,
             str(self.count) + 'pcs',
             'price=' + str(self.price),
             self.deal_number,
             self.broker_commission]
        return ' '.join([str(i) for i in t])

    def __repr__(self):
        return self.__str__()
