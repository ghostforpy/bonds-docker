let url = document.location.protocol + '//' + document.location.host
const HTTP = axios.create({
    //baseURL: 'http://0.0.0.0:8000/api/',
    baseURL: url + '/api/',
    headers: {
        'X-CSRFToken': csrftoken,
    }
})

Vue.component('year-profit', {
    props: ['year_profit'],
    template: '<p>Среднегодовая доходность: {{year_profit}} %</p>'
})

Vue.component('today-cash', {
    props: ['today_cash'],
    computed: {
        computed_today_cash: function () {
            return parseFloat(this.today_cash).toFixed(2);
        }
    },
    template: '<p>Общая стоимость портфеля на сегодняшний день: {{computed_today_cash}} РУБ</p>'
})

Vue.component('total-invests', {
    props: ['total_invests'],
    computed: {
        computed_total_invests: function () {
            let i = this.total_invests.map(
                function cash(item) {
                    if (item.action == 'Пополнение') {
                        var sign = 1
                    } else {
                        var sign = -1
                    };
                    return sign * parseFloat(item.cash_in_rub);
                }
            );
            return i.reduce((a, b) => a + b).toFixed(2)
        },
    },
    template: '<p> Всего инвестиций: {{computed_total_invests}} РУБ</p>'
})

Vue.component('invests', {
    props: ['invests'],
    computed: {
        computed_invests: function () {
            return this.invests.map(function (number) {
                let el = number;
                el.cash = parseFloat(el.cash).toFixed(2);
                if (el.action) {
                    el.action = 'Пополнение'
                } else {
                    el.action = 'Снятие'
                };
                if (el.currency == 'RUB') {
                    el.currency = 'РУБ'
                }
                return el
            })
        }
    },
    template: ` <div>
                    <p>Инвестиции:</p>
                    <ul>
                        <li v-for="item in computed_invests">
                            {{item.action}} {{item.date}} на {{item.cash}} {{item.currency}}
                            <span v-if="(item.currency != 'РУБ')">({{item.cash_in_rub}} РУБ)</span>
                        </li>
                    </ul>
                </div>`
})

Vue.component('securities', {
    props: ['securities'],
    computed: {
        computed_securities: function () {
            return this.securities.map(function (security) {
                let el = security;
                security.count = security.count.replace(/0*$/, "").replace(/\.*$/, "");
                security.total = security.total.replace(/0*$/, "").replace(/\.*$/, "");
                security.security.today_price = security.security.today_price
                    .replace(/0*$/, "")
                    .replace(/\.*$/, "");
                security.price_in_rub = security.price_in_rub
                    .replace(/0*$/, "")
                    .replace(/\.*$/, "");
                security.total_in_rub = security.total_in_rub
                    .replace(/0*$/, "")
                    .replace(/\.*$/, "");
                return el
            })
        }
    },
    template: ` <div>
                    <p>Ценные бумаги в портфеле:</p>
                    <ul>
                        <li v-for="item in computed_securities">
                            {{item.security.shortname}}({{item.security.secid}})
                            в количестве {{item.count}} штук
                            на общую сумму {{item.total}} {{item.security.faceunit}}
                            <span v-if="(item.security.faceunit != 'РУБ')">
                                (по {{item.price_in_rub}} РУБ на общую сумму {{item.total_in_rub}} РУБ)
                            </span>
                        </li>
                    </ul>
                </div>`
})

Vue.component('errors', {
    props: ['errors'],
    template: ` <div>
                    <p>Ошибка</p>
                    <ul>
                        <li v-for="error in errors">
                            {{error}}
                        </li>
                    </ul>   
                </div>`
})


Vue.component('part_five_dot_one', {
    props: ['dat'],
    data: function () {
        return {
            last_row: null
        }
    },
    beforeMount: function () {
        var el = this.dat;
        this.last_row = el.pop();
    },
    template: `<div>
                <div class="row">
                    <div class="col-3 d-none d-md-block">
                        <strong>Наименование и организационно-правовая форма организации</strong>
                    </div>
                    <div class="col-3 d-none d-md-block">
                        <strong>Доля участия</strong>
                    </div>
                    <div class="col-6 d-none d-md-block">
                        <strong>Основание участия</strong>
                    </div>
                </div>
                <div class="dropdown-divider d-none d-md-block"></div>
                <div v-for="item in dat">
                    <part_five_dot_one_row v-bind:one_row="item"></part_five_dot_one_row>
                    <div class="dropdown-divider"></div>
                </div>
                <part_five_dot_one_row v-bind:one_row="last_row"></part_five_dot_one_row>
            </div>`
})

Vue.component('part_five_dot_one_row', {
    props: ['one_row'],
    data: function () {
        return {
            last_participation_basis: null,
            total: null
        }
    },
    beforeMount: function () {
        var el = this.one_row;
        el.count = el.count.replace(/0*$/, "").replace(/\.*$/, "");
        el.security.facevalue = el.security.facevalue
            .replace(/0*$/, "")
            .replace(/\.*$/, "");
        this.last_participation_basis = el.participation_basis.pop();
        this.total = (parseFloat(el.count) * parseFloat(el.security.facevalue))
            .toFixed(7)
            .replace(/0*$/, "")
            .replace(/\.*$/, "");
    },
    template: `
                <div class="row">
                        <div class=" col-12 col-md-3 mb-1 mt-1">
                            {{one_row.security.emitent}}
                        </div>
                        <div class=" col-12 col-md-3 mb-1 mt-1">
                        Количество: {{one_row.count}} шт.,
                        </br>
                        Номинальная стоимость: {{one_row.security.facevalue}} 
                        {{one_row.security.faceunit}}
                        </br>
                        Итого: {{total}} {{one_row.security.faceunit}}
                        </div>
                        <div class=" col-12 col-md-6 mb-1 mt-1">
                            <span v-for="i in one_row.participation_basis">
                                <span>сделка № {{i.deal_number}}
                                (поручение № {{i.order_number}}) от {{i.date}},</span>
                                </br>
                            </span>
                            <span>сделка № {{last_participation_basis.deal_number}}
                            (поручение № {{last_participation_basis.order_number}}) от 
                            {{last_participation_basis.date}}</span>
                        </div>
                    </div>
    `
})


Vue.component('part_five_dot_two', {
    props: ['dat'],
    data: function () {
        return {
            last_row: null
        }
    },
    beforeMount: function () {
        var el = this.dat;
        this.last_row = el.pop();
    },
    template: `<div>
                <div class="row">
                    <div class="col-3 d-none d-md-block">
                        <strong>Вид ценной бумаги</strong>
                    </div>
                    <div class="col-2 d-none d-md-block">
                        <strong>Лицо, выпустившее ценную бумагу</strong>
                    </div>
                    <div class="col-3 d-none d-md-block">
                        <strong>Номинальная величина обязательства</br>(руб.)</strong>
                    </div>
                    <div class="col-1 d-none d-md-block">
                        <strong>Общее количество</strong>
                    </div>
                    <div class="col-3 d-none d-md-block">
                        <strong>Общая стоимость</br>(руб.)</strong>
                    </div>
                </div>
                <div class="dropdown-divider d-none d-md-block"></div>
                <div v-for="item in dat">
                    <part_five_dot_two_row v-bind:one_row="item"></part_five_dot_two_row>
                    <div class="dropdown-divider"></div>
                </div>
                <part_five_dot_two_row v-bind:one_row="last_row"></part_five_dot_two_row>
            </div>`
})

Vue.component('part_five_dot_two_row', {
    props: ['one_row'],
    data: function () {
        return {
            total_cost: null
        }
    },
    beforeMount: function () {
        var el = this.one_row;
        el.count = el.count.replace(/0*$/, "").replace(/\.*$/, "");
        this.total_cost = el.security.facevalue * el.count;
    },
    template: `<div class="row">
                        <div class=" col-12 col-md-3 mb-1 mt-1">
                            {{one_row.security.security_type}} "{{one_row.security.name}}"
                        </div>
                        <div class=" col-12 col-md-2 mb-1 mt-1">
                            {{one_row.security.emitent}}
                        </div>
                        <div class=" col-12 col-md-3 mb-1 mt-1">
                            <span class="d-md-none">Номинальная величина обязательства(руб.): </span>{{total_cost}}
                        </div>
                        <div class=" col-12 col-md-1 mb-1 mt-1">
                            <span class="d-md-none">Общее количество: </span>{{one_row.count}}
                        </div>
                        <div class=" col-12 col-md-3 mb-1 mt-1">
                            <span class="d-md-none">Общая стоимость(руб.): </span>{{total_cost}}
                        </div>
                    </div>`
})

Vue.component('part_one', {
    props: ['profits'],
    data: function () {
        return {
            profit_div_coupon: null,
            profit_repo: null,
            sells: null,
            total_sells_profit: null,
            total_profit: 0
        }
    },
    beforeMount: function () {
        var el = this.profits;
        if (el.profit_div_coupon != null) {
            this.profit_div_coupon = el.profit_div_coupon
                .map(function (item) {
                    item.value = item.value.replace(/0*$/, "").replace(/\.*$/, "");
                    item.currency = item.currency.replace("RUB", "РУБ");
                    return item
                });
        };
        if (el.profit_repo != null) {
            this.profit_repo = el.profit_repo
                .map(function (item) {
                    item.value = item.value.replace(/0*$/, "").replace(/\.*$/, "");
                    item.currency = item.currency.replace("RUB", "РУБ");
                    return item
                });
        };
        if (el.sells != null) {
            this.sells = el.sells
                .map(function (item) {
                    item.total_profit = item.total_profit.replace(/0*$/, "").replace(/\.*$/, "");
                    item.security.faceunit = item.security.faceunit.replace("RUB", "РУБ");
                    return item
                });
        };

    },
    template: `
        <div>
            <ul v-if="profit_div_coupon != null">Доход, полученный от купонов и дивидендов:
                <li v-for="i in profit_div_coupon">{{i.value}} {{i.currency}}</li>
            </ul>
            <ul v-if="profit_repo != null">Доход, полученный от сделок РЕПО:
                <li v-for="i in profit_repo">{{i.value}} {{i.currency}}</li>
            </ul>
            <ul v-if="sells != null">Доход, полученный с продажи ценных бумаг:
                <li v-for="i in sells">
                    {{i.security.secid}}: {{i.total_profit}} {{i.security.faceunit}}
                </li>
            </ul>
        </div>
    `
})