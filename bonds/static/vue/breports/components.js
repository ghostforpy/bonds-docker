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
                    item.value = item.value.replace(/0*$/, "").replace(/\.*$/, "");
                    item.currency = item.currency.replace("RUB", "РУБ");
                    return item
                });
            this.profit_div_coupon_operations = el.profit_div_coupon_operations
                .map(function (item) {
                    item.cash = item.cash.replace(/0*$/, "").replace(/\.*$/, "");
                    item.currency = item.currency.replace("RUB", "РУБ");
                    item.tax = item.tax.replace(/0*$/, "").replace(/\.*$/, "");
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
            this.sells_exists = true;
            this.sells = el.sells
                .map(function (item) {
                    item.total_profit = item.total_profit.replace(/0*$/, "").replace(/\.*$/, "");
                    item.total_tax_base_without_commissions = item
                        .total_tax_base_without_commissions.replace(/0*$/, "").replace(/\.*$/, "");
                    item.total_tax_base = item
                        .total_tax_base.replace(/0*$/, "").replace(/\.*$/, "");
                    item.security.faceunit = item.security.faceunit.replace("RUB", "РУБ");
                    return item
                });
            this.last_sell = this.sells.pop();
        };

    },
    template: `
        <div>
            <ul v-if="profit_div_coupon != null">
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
                <li v-for="i in profit_div_coupon">{{i.value}} {{i.currency}}</li>
            </ul>
            <b-collapse
            v-if="profit_div_coupon != null"
            id="profit_div_coupon_operations"
            class="mt-2">
                <div v-for="(i,ind) in profit_div_coupon_operations">
                    <div class="row" v-bind:class="{ 'bg-light': (ind % 2) }">
                        {{i.date}} {{i.action}} по {{i.security.name}}({{i.security.isin}}) в размере
                        {{i.cash}} {{i.currency}}<span v-if="(i.tax > 0)">(Налог: {{i.tax}})</span>
                    </div>
                </div>
            </b-collapse>
            <ul v-if="profit_repo != null">Доход, полученный от сделок РЕПО:
                <li v-for="i in profit_repo">{{i.value}} {{i.currency}}</li>
            </ul>
            <div v-if="sells_exists" class="mt-3">
                <strong>Финансовый результат, полученный с продажи ценных бумаг:</strong>
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
        this.one_row.sells = this.one_row.sells
            .map(function (item) {
                item.count = item.count.replace(/0*$/, "").replace(/\.*$/, "");
                item.price = item.price.replace(/0*$/, "").replace(/\.*$/, "");
                item.sells = item.sells
                    .map(function (i) {
                        i.count = i.count.replace(/0*$/, "").replace(/\.*$/, "");
                        i.price = i.price.replace(/0*$/, "").replace(/\.*$/, "");
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
                <div class="col-3">
                    <b-button v-b-toggle="index_number" variant="info" size="sm" v-on:click="rotate_method">
                        <b-icon
                        icon="chevron-double-down"
                        :rotate="rotate"
                        ></b-icon>
                    </b-button>
                    {{one_row.security.name}} ({{one_row.security.secid}}):
                </div>
                <div class="col-2">
                    {{one_row.total_profit}} {{one_row.security.faceunit}}
                </div>
                <div class="col-2">
                    {{one_row.total_tax_base_without_commissions}} {{one_row.security.faceunit}}
                </div>
                <div class="col-4">
                    {{one_row.total_tax_base}} {{one_row.security.faceunit}}
                </div>
            </div>
            <b-collapse v-bind:id="index_number" class="mt-2">
                <div class="" v-for="(x, ind) in one_row.sells">
                  <div class="row mt-2" v-bind:class="{ 'bg-light': (ind % 2) }">
                    <div class="col-6">
                        {{x.date}} {{x.action}} {{x.count}} шт. по {{x.price}} {{one_row.security.faceunit}}
                    </div>
                    <div class="col-6">
                    <p v-for="y in x.sells">
                        {{y.date}} {{y.action}} {{y.count}} шт. по {{y.price}} {{one_row.security.faceunit}}
                    </p>
                    </div>
                  </div>
                </div>
            </b-collapse>
        </div>
    `
})