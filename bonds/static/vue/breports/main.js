function prepare_before_post(em) {
    if (em.file) {
        em.year_profit_visible = false;
        em.income_certificate_visible = false;
        em.spiner_visible = true;
        em.errors_visible = false;
        if (em.file.size > 2621440) {
            em.errors = [
                `Превышен максимальный размер файла.</br>Ваш файл ${em.file.size} B.</br>
                        Максимальный размер файла - 2621440 B (2.5 MB).`
            ];
            em.errors_visible = true;
            em.spiner_visible = false;
            em.file = null;
            return false
        };
    };
    return true
};
function post_formData(em, formData, mode) {
    if (mode == 'calc_year_profit') {
        var url = 'breports/year-profit/';
    } else if (mode == 'income_certificate') {
        var url = 'breports/income-certificate/';
    };
    HTTP.post(
        url,
        formData
    ).then(function (resp) {
        em.spiner_visible = false;
        // console.log('SUCCESS!!');
        if (mode == 'calc_year_profit') {
            em.year_profit_data = resp.data;
            em.year_profit_visible = true;
        } else if (mode == 'income_certificate') {
            em.income_certificate_data = resp.data;
            em.income_certificate_visible = true;
        };

        //console.log(resp);
    })
        .catch(function (error) {
            em.spiner_visible = false;
            em.errors_visible = true;
            //  console.log('FAILURE!!');
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
};
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
        income_certificate_data: null,
        income_sertificate_datepicker_visible: false,
        income_sertificate_datepicker_since_date: null,
        income_sertificate_datepicker_to_date: null,
        tax_load_visible: false,
        selected: 'calc_year_profit',
        options: [
            { value: 'calc_year_profit', text: 'Среднегодовая доходность' },
            { value: 'income_certificate', text: 'Справка о доходах' },
            { value: 'b', text: 'Selected Option' },
            { value: 'd', text: 'This one is disabled', disabled: true }
        ]
    },
    methods: {
        yesterday: function () {
            var date = new Date();
            date.setDate(date.getDate() - 1);
            return date
        },
        send: function () {
            if (this.selected == 'calc_year_profit') {
                this.calc_year_profit();
            } else if (this.selected == 'income_certificate') {
                this.income_certificate();
            }
        },
        calc_year_profit: function () {
            if (prepare_before_post(this)) {
                let formData = new FormData();
                formData.append('filename', this.file);
                post_formData(this, formData, this.selected);
            };
        },
        income_certificate: function () {
            if (prepare_before_post(this)) {
                let formData = new FormData();
                formData.append('filename', this.file);
                formData.append('since_date', this.income_sertificate_datepicker_since_date);
                formData.append('to_date', this.income_sertificate_datepicker_to_date);
                post_formData(this, formData, this.selected);
            };
        },
        func3: function () {

        }
    },
    template: `
    <div id="app">
        <div class="row mx-3">{{ message }}</div>
        <div class="row mx-3 mt-3">
            <b-form-file
            v-model="file"
            :state="Boolean(file)"
            browseText="Обзор"
            placeholder="Выберите или перетащите файл..."
            drop-placeholder="Перетащите файл..."
            accept=".xls, .xlsx"
            ></b-form-file>
            <b-form-select
            size="sm"
            class="mt-3 col-12 col-md-6"
            v-model="selected"
            :options="options"></b-form-select>
        </div>
        <div v-if="selected == 'income_certificate'" class="mt-3 mx-3 row">
            <div class="col-11 col-md-5 pl-0">
                <b-form-datepicker
                size="sm"
                id="income-sertificate-datepicker-since"
                label-no-date-selected="Выберите дату начала"
                v-model="income_sertificate_datepicker_since_date"></b-form-datepicker>
                <b-form-datepicker
                class="mt-3"
                :max="yesterday()"
                size="sm"
                id="income-sertificate-datepicker-to"
                label-no-date-selected="Выберите дату окончания"
                v-model="income_sertificate_datepicker_to_date"></b-form-datepicker>
            </div>
            <div class="col-1 d-flex justify-content-center align-items-center col-md-1">
                <b-icon
                icon="question-circle-fill"
                id="popover-target-question-circle-fill"
                ></b-icon>
                <b-popover target="popover-target-question-circle-fill" triggers="hover" placement="bottomleft">
                    <template #title>Примечание</template>
                    Даты начала и окончания влияют только на данные первого раздела справки о доходах.
                    В данных пятого раздела справки будут отображены все ценные бумаги,
                    остатки по которым на дату окончания брокерского отчета не равны 0.
                </b-popover>
            </div>
        </div>
        <b-button class="mt-3 ml-3" v-on:click="send">Отправить</b-button>
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
            <h4 class="mt-4">Данные, необходимые для заполнения п.5 раздела 1<br>
            (Доход от ценных бумаг и долей участия в коммерческих организациях).</h4>
            <part_one v-bind:profits="income_certificate_data.profits"></part_one>
            <div v-if="income_certificate_data.part_five_one.length > 0">
                <h3 class="mt-5">Раздел 5.1</h3>
                <small>Примечание: Местонахождение организации необходимо найти самостоятельно. Уставной капитал, доля участия участия подлежат проверке.</small>
                <part_five_dot_one class="mt-3" v-bind:dat="income_certificate_data.part_five_one"></part_five_dot_one>
            </div>
            <div v-if="income_certificate_data.part_five_two.length > 0">
                <h3 class="mt-5">Раздел 5.2</h3>
                <small>Примечание: Номинальная величина обязательства указана на текущую дату и не учитывает возможную амортизацию с даты окончания анализа отчета.</small>
                <part_five_dot_two
                class="mt-3"
                v-bind:dat="income_certificate_data.part_five_two"></part_five_dot_two>
            </div>
        </div>
    </div>
    `
})
