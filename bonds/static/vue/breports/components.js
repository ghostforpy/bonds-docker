const HTTP = axios.create({
    baseURL: 'http://0.0.0.0:8000/api/',
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
                    return parseFloat(item.cash);
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
                                (по {{item.price_in_rub}} РУБ на общую сумму {{item.total_in_rub}})
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