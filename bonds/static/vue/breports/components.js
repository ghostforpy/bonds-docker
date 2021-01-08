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
            return parseFloat(this.today_cash)
                .toLocaleString('ru-RU', { style: 'currency', currency: 'RUB', maximumFractionDigits: 2 });
        }
    },
    template: '<p>Общая стоимость портфеля на сегодняшний день: {{computed_today_cash}}</p>'
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
            return i.reduce((a, b) => a + b)
                .toLocaleString('ru-RU', { style: 'currency', currency: 'RUB' });
        },
    },
    template: '<p> Всего инвестиций: {{computed_total_invests}}</p>'
})

Vue.component('invests', {
    props: ['invests'],
    computed: {
        computed_invests: function () {
            return this.invests.map(function (number) {
                let el = number;
                el.cash = parseFloat(el.cash)
                    .toLocaleString('ru-RU', { style: 'currency', currency: el.currency, maximumFractionDigits: 10 });
                if (el.action) {
                    el.action = 'Пополнение'
                } else {
                    el.action = 'Снятие'
                };
                el.cash_in_rub_display = parseFloat(el.cash)
                    .toLocaleString('ru-RU', { style: 'currency', currency: 'RUB', maximumFractionDigits: 10 });
                return el
            })
        }
    },
    template: ` <div>
                    <p>Инвестиции:</p>
                    <ul>
                        <li v-for="item in computed_invests">
                            {{item.action}} {{item.date}} на {{item.cash}}
                            <span v-if="(item.currency != 'RUB')">({{item.cash_in_rub_display}})</span>
                        </li>
                    </ul>
                </div>`
})

Vue.component('securities', {
    props: ['securities'],
    computed: {
        computed_securities: function () {
            return this.securities.map(function (security) {
                let security_currency = security.security.faceunit.replace('РУБ', 'RUB');
                security.count = parseFloat(security.count)
                    .toLocaleString('ru-RU', { maximumFractionDigits: 2 });
                security.total = parseFloat(security.total)
                    .toLocaleString('ru-RU', { style: 'currency', currency: security_currency, maximumFractionDigits: 2 });
                security.security.today_price = parseFloat(security.security.today_price)
                    .toLocaleString('ru-RU', { style: 'currency', currency: security_currency, maximumFractionDigits: 2 });
                security.price_in_rub = parseFloat(security.price_in_rub)
                    .toLocaleString('ru-RU', { style: 'currency', currency: 'RUB', maximumFractionDigits: 2 });
                security.total_in_rub = parseFloat(security.total_in_rub)
                    .toLocaleString('ru-RU', { style: 'currency', currency: 'RUB', maximumFractionDigits: 2 });
                return security
            })
        }
    },
    template: ` <div>
                    <p>Ценные бумаги в портфеле:</p>
                    <ul>
                        <li v-for="item in computed_securities">
                            {{item.security.shortname}}({{item.security.secid}})
                            в количестве {{item.count}} штук
                            на общую сумму {{item.total}}
                            <span v-if="(item.security.faceunit != 'РУБ')">
                                (по {{item.price_in_rub}} на общую сумму {{item.total_in_rub}})
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
                    <div class="col-2 d-none d-md-block">
                        <strong>Наименование и организационно-правовая форма организации</strong>
                    </div>
                    <div class="col-2 d-none d-md-block">
                        <strong>Уставной капитал</strong>
                    </div>
                    <div class="col-2 d-none d-md-block">
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
        let security_faceunit = el.security.faceunit.replace('РУБ', 'RUB');
        let security_facevalue = el.security.facevalue;
        el.security.facevalue = parseFloat(el.security.facevalue)
            .toLocaleString('ru-RU', { style: 'currency', currency: security_faceunit, maximumFractionDigits: 10 });
        el.security.share_capital = (parseFloat(security_facevalue) * parseFloat(el.security.issuesize))
            .toLocaleString('ru-RU', { style: 'currency', currency: security_faceunit, maximumFractionDigits: 10 });
        this.last_participation_basis = el.participation_basis.pop();
        this.total = (parseFloat(el.count) * parseFloat(security_facevalue))
            .toLocaleString('ru-RU', { style: 'currency', currency: security_faceunit, maximumFractionDigits: 10 });
    },
    template: `
                <div class="row">
                        <div class=" col-12 col-md-2 mb-1 mt-1">
                            {{one_row.security.emitent}}
                        </div>
                        <div class=" col-12 col-md-2 mb-1 mt-1">
                        Уставной капитал: {{one_row.security.share_capital}}
                        </div>
                        <div class=" col-12 col-md-2 mb-1 mt-1">
                        Количество: {{one_row.count}} шт.,
                        </br>
                        Номинальная стоимость: {{one_row.security.facevalue}}
                        </br>
                        Итого: {{total}}
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
        this.total_cost = (parseFloat(el.security.facevalue) * parseFloat(el.count))
            .toLocaleString('ru-RU', { maximumFractionDigits: 10 });
        el.count = parseFloat(el.count)
            .toLocaleString('ru-RU', { maximumFractionDigits: 10 });
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
                            <span class="d-md-none">Общее количество: </span>{{one_row.count}} шт.
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
            profit_div_coupon_operations: null,
            rotate: 0,
            profit_repo: null,
            sells: null,
            last_sell: null,
            sells_exists: false,
            total_sells_profit: null,
            total_profit: 0
        }
    },
    methods: {
        rotate_method: function () {
            if (this.rotate == 0) {
                this.rotate = 180
            } else {
                this.rotate = 0
            }
        },
    },
    beforeMount: function () {
        var el = this.profits;
        if (el.profit_div_coupon != null) {
            this.profit_div_coupon = el.profit_div_coupon
                .map(function (item) {
                    item.value = parseFloat(item.value)
                        .toLocaleString('ru-RU', { style: 'currency', currency: item.currency, maximumFractionDigits: 10 });
                    return item
                });
            this.profit_div_coupon_operations = el.profit_div_coupon_operations
                .map(function (item) {
                    item.cash = parseFloat(item.cash)
                        .toLocaleString('ru-RU', { style: 'currency', currency: item.currency, maximumFractionDigits: 10 });

                    item.tax_display = parseFloat(item.tax)
                        .toLocaleString('ru-RU', { style: 'currency', currency: item.currency, maximumFractionDigits: 10 });
                    return item
                });
        };
        if (el.profit_repo != null) {
            this.profit_repo = el.profit_repo
                .map(function (item) {
                    item.value = parseFloat(item.value)
                        .toLocaleString('ru-RU', { style: 'currency', currency: item.currency, maximumFractionDigits: 10 });
                    return item
                });
        };
        if (el.sells != null) {
            this.sells_exists = true;
            this.sells = el.sells
                .map(function (item) {
                    let security_faceunit = item.security.faceunit.replace("РУБ", "RUB");
                    item.total_profit = parseFloat(item.total_profit)
                        .toLocaleString('ru-RU', { style: 'currency', currency: security_faceunit, maximumFractionDigits: 10 });
                    item.total_tax_base_without_commissions = parseFloat(item
                        .total_tax_base_without_commissions)
                        .toLocaleString('ru-RU', { style: 'currency', currency: security_faceunit, maximumFractionDigits: 10 });
                    item.total_tax_base = parseFloat(item.total_tax_base)
                        .toLocaleString('ru-RU', { style: 'currency', currency: security_faceunit, maximumFractionDigits: 10 });
                    return item
                });
            this.last_sell = this.sells.pop();
        };

    },
    template: `
        <div class="container">
            <div class="row" v-if="profit_div_coupon != null">
                <div class="col-12">
                    <b-button
                    v-b-toggle.profit_div_coupon_operations
                    variant="info"
                    size="sm"
                    v-on:click="rotate_method">
                        <b-icon
                        icon="chevron-double-down"
                        :rotate="rotate"
                        ></b-icon>
                    </b-button>
                    Доход, полученный от купонов и дивидендов:
                    <p class="ml-2" v-for="i in profit_div_coupon">{{i.value}}</p>
                </div>
            </div>
            <b-collapse
            v-if="profit_div_coupon != null"
            id="profit_div_coupon_operations"
            class="mt-2">
                <div v-for="(i,ind) in profit_div_coupon_operations">
                    <div class="row mb-2" v-bind:class="{ 'bg-light': (ind % 2) }">
                        <span class="col-12">{{i.date}} </br>{{i.action}} по {{i.security.name}}({{i.security.isin}})
                        </br>в размере {{i.cash}}</span>
                        <span v-if="(i.tax > 0)" class="col-12">(Налог: {{i.tax_display}})</span>
                    </div>
                </div>
            </b-collapse>
            <ul v-if="profit_repo != null">Доход, полученный от сделок РЕПО:
                <li v-for="i in profit_repo">{{i.value}} {{i.currency}}</li>
            </ul>
            <div v-if="sells_exists" class="mt-3">
                <strong class="mb-2">Финансовый результат, полученный с продажи ценных бумаг:</strong>
                <div class="d-none d-md-block">
                    <div class="row">
                        <div class="col-3">
                            Наименование
                        </div>
                        <div class="col-2">
                            Доход с продажи
                        </div>
                        <div class="col-2">
                            Налоговая база
                        </div>
                        <div class="col-4">
                            Налоговая база с учетом комиссий
                        </div>
                    </div>
                </div>
                
                <div class="dropdown-divider"></div>
                <div v-for="(i, index) in sells">
                    <part_one_simple_row :one_row="i" :index="index"></part_one_simple_row>
                    <div class="dropdown-divider"></div>
                </div>
                <part_one_simple_row :one_row="last_sell" :index="sells.length"></part_one_simple_row>
            </div>
        </div>
    `
})

Vue.component('part_one_simple_row', {
    props: ['one_row', 'index'],
    data: function () {
        return {
            index_number: null,
            rotate: 0
        }
    },
    beforeMount: function () {
        this.index_number = 'collapse-' + this.index.toString();
        var security_faceunit = this.one_row.security.faceunit.replace("РУБ", "RUB");
        this.one_row.sells = this.one_row.sells
            .map(function (item) {
                item.count = item.count.replace(/0*$/, "").replace(/\.*$/, "");
                item.price = parseFloat(item.price)
                    .toLocaleString('ru-RU', { style: 'currency', currency: security_faceunit, maximumFractionDigits: 10 });
                item.sells = item.sells
                    .map(function (i) {
                        i.count = i.count.replace(/0*$/, "").replace(/\.*$/, "");
                        i.price = parseFloat(i.price)
                            .toLocaleString('ru-RU', { style: 'currency', currency: security_faceunit, maximumFractionDigits: 10 });
                        return i
                    })
                return item
            });
    },
    methods: {
        rotate_method: function () {
            if (this.rotate == 0) {
                this.rotate = 180
            } else {
                this.rotate = 0
            }
        },
    },
    template: `
        <div>
            <div class="row">
                <div class="col-12 col-md-3">
                    <b-button v-b-toggle="index_number" variant="info" size="sm" v-on:click="rotate_method">
                        <b-icon
                        icon="chevron-double-down"
                        :rotate="rotate"
                        ></b-icon>
                    </b-button>
                    {{one_row.security.name}} ({{one_row.security.secid}}):
                </div>
                <div class="d-inline-flex col-12 col-md-2">
                    <span class="d-block d-md-none mr-1">Доход с продажи: </span><span>{{one_row.total_profit}}</span>
                </div>
                <div class="d-inline-flex col-12 col-md-2">
                    <span class="d-block d-md-none mr-1">Налоговая база: </span><span>{{one_row.total_tax_base_without_commissions}}</span>
                </div>
                <div class="d-inline-flex col-12 col-md-4">
                    <span class="d-block d-md-none mr-1">Налоговая база с учетом комиссий: </span><span>{{one_row.total_tax_base}}</span>
                </div>
            </div>
            <b-collapse v-bind:id="index_number" class="mt-2">
                <div class="" v-for="(x, ind) in one_row.sells">
                  <div class="row mt-2" v-bind:class="{ 'bg-light': !(ind % 2) }">
                    <div class="col-6">
                        {{x.date}} {{x.action}} {{x.count}} шт. по {{x.price}}
                    </div>
                    <div class="col-6">
                    <p v-for="y in x.sells">
                        {{y.date}} {{y.action}} {{y.count}} шт. по {{y.price}}
                    </p>
                    </div>
                  </div>
                </div>
            </b-collapse>
        </div>
    `
})