
var app = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        message: 'Давайте проанализируем Ваши брокерские отчеты!',
        file: null,
        year_profit_visible: false,
        spiner_visible: false,
        errors: null,
        errors_visible: false,
        year_profit_data: null
    },
    methods: {
        calc_year_profit: function () {
            var em = this;
            if (this.file) {
                em.year_profit_visible = false;
                em.spiner_visible = true;
                em.errors_visible = false;
                let formData = new FormData();
                formData.append('filename', this.file);
                HTTP.post(
                    'breports/year-profit/',
                    formData
                ).then(function (resp) {
                    em.spiner_visible = false;
                    console.log('SUCCESS!!');
                    em.year_profit_data = resp.data;
                    em.year_profit_visible = true;
                    console.log(resp);
                })
                    .catch(function (e) {
                        em.spiner_visible = false;
                        em.errors_visible = true;
                        console.log('FAILURE!!');
                        em.errors = e.response.data;
                        console.log(error);
                    });
            }
        },
        func2: function () {

        },
        func3: function () {

        }
    }
})
