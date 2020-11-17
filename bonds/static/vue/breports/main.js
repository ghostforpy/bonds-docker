
var app = new Vue({
    el: '#app',
    data: {
        message: 'Давайте проанализируем Ваши брокерские отчеты!',
        file: null,
        spiner_visible: false,
        errors: null,
        errors_visible: false,
        year_profit_visible: false,
        year_profit_data: null,
        income_certificate_visible: false,
        income_certificate_data: null
    },
    methods: {
        calc_year_profit: function () {
            var em = this;
            if (this.file) {
                em.year_profit_visible = false;
                em.income_certificate_visible = false;
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
                    //console.log(resp);
                })
                    .catch(function (error) {
                        em.spiner_visible = false;
                        em.errors_visible = true;
                        console.log('FAILURE!!');
                        if (error.response) {
                            // The request was made and the server responded with a status code
                            // that falls out of the range of 2xx
                            //console.log(error.response.data);
                            if (error.response.status === 500) {
                                em.errors = ['Server error'];
                            } else {
                                em.errors = error.response.data;
                            }
                            //console.log(error.response.status);
                            //console.log(error.response.headers);
                        } else if (error.request) {
                            // The request was made but no response was received
                            // `error.request` is an instance of XMLHttpRequest in the browser and an instance of
                            // http.ClientRequest in node.js
                            //console.log(error.request);
                        } else {
                            // Something happened in setting up the request that triggered an Error
                            //console.log('Error', error.message);
                        }
                        //console.log(error.config);
                    });
            }
        },
        income_certificate: function () {
            var em = this;
            if (this.file) {
                em.year_profit_visible = false;
                em.income_certificate_visible = false;
                em.spiner_visible = true;
                em.errors_visible = false;
                let formData = new FormData();
                formData.append('filename', this.file);
                HTTP.post(
                    'breports/income-certificate/',
                    formData
                ).then(function (resp) {
                    em.spiner_visible = false;
                    console.log('SUCCESS!!');
                    em.income_certificate_data = resp.data;
                    em.income_certificate_visible = true;
                    console.log(resp);
                })
                    .catch(function (error) {
                        em.spiner_visible = false;
                        em.errors_visible = true;
                        console.log('FAILURE!!');
                        if (error.response) {
                            // The request was made and the server responded with a status code
                            // that falls out of the range of 2xx
                            //console.log(error.response.data);
                            if (error.response.status === 500) {
                                em.errors = ['Server error'];
                            } else {
                                em.errors = error.response.data;
                            }
                            //console.log(error.response.status);
                            //console.log(error.response.headers);
                        } else if (error.request) {
                            // The request was made but no response was received
                            // `error.request` is an instance of XMLHttpRequest in the browser and an instance of
                            // http.ClientRequest in node.js
                            //console.log(error.request);
                        } else {
                            // Something happened in setting up the request that triggered an Error
                            //console.log('Error', error.message);
                        }
                        //console.log(error.config);
                    });
            }
        },
        func3: function () {

        }
    },
    template: `
    <div id="app">
        <p>{{ message }}</p>
        <b-form-file
        v-model="file"
        :state="Boolean(file)"
        placeholder="Выберите или перетащите файл..."
        drop-placeholder="Перетащите файл..."
        accept=".xls, .xlsx"
        ></b-form-file>
        <div>
            <b-button class="mt-3" v-on:click="calc_year_profit">Среднегодовая доходность</b-button>
            <b-button class="mt-3" v-on:click="income_certificate">Справка о доходах</b-button>
            <b-button class="mt-3" v-if="false" v-on:click="func3">func 3</b-button>
        </div>
        <errors class="mt-3" v-if="errors_visible" v-bind:errors="errors"></errors>
        <div v-if="spiner_visible" class="d-flex justify-content-center mt-3">
            <b-spinner label="Loading..."></b-spinner>
        </div>
        <div id="year_profit_part" v-if="year_profit_visible" class="mt-3">
            <year-profit
            v-bind:year_profit="year_profit_data.year_profit"
            ></year-profit>
            <total-invests
                v-bind:total_invests="year_profit_data.invests"
            ></total-invests>
            <today-cash v-bind:today_cash="year_profit_data.today_cash"></today-cash>
            <div class="row">
                <invests
                class="col-12 col-lg-4"
                v-bind:invests="year_profit_data.invests"
                ></invests>
                <securities
                class="col-12 col-lg-8"
                v-bind:securities="year_profit_data.securities"
                ></securities>
            </div>
        </div>
        <div id="income_certificate_part" v-if="income_certificate_visible" class="mt-3">
            <h4 class="mt-4">Данные, необходимые для заполнения п.5 (Доход от ценных бумаг и долей участия в коммерческих организациях) раздела 1.</h4>
            <part_one v-bind:profits="income_certificate_data.profits"></part_one>
            <div v-if="income_certificate_data.part_five_one.length > 0">
                <h3 class="mt-4">Раздел 5.1</h3>
                <small>Примечание: Местонахождение организации, уставной капитал, долю участия необходимо найти самостоятельно.</small>
                <part_five_dot_one class="mt-3" v-bind:dat="income_certificate_data.part_five_one"></part_five_dot_one>
            </div>
            <div v-if="income_certificate_data.part_five_two.length > 0">
                <h3 class="mt-4">Раздел 5.2</h3>
                <part_five_dot_two
                class="mt-3"
                v-bind:dat="income_certificate_data.part_five_two"></part_five_dot_two>
            </div>
        </div>
    </div>
    `
})
