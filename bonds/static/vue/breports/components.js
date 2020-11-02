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
                return el
            })
        }
    },
    template: ` <div>
                    <p>Инвестиции:</p>
                    <ul>
                        <li v-for="item in computed_invests">
                            {{item.action}} {{item.date}} на {{item.cash}}
                        </li>
                    </ul>
                </div>`
})