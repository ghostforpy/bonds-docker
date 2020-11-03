
var app = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        message: 'Давайте проанализируем Ваши брокерские отчеты!',
        file: null,
        spiner_visible: false,
        errors: null,
        errors_visible: false,
        year_profit_visible: false,
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
        func2: function () {

        },
        func3: function () {

        }
    }
})
