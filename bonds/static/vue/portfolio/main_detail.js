function prepare_file_before_post(em) {
  if (em.file) {
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
function post_formData(em, formData, url) {
  HTTP.post(
    url,
    formData
  ).then(function (resp) {
    em.spiner_visible = false;
    console.log('SUCCESS!!');
    //console.log(resp);
    url = resp.data.url;
    go_to_url(url);

  })
    .catch(function (error) {
      em.spiner_visible = false;
      em.errors_visible = true;
      console.log('FAILURE!!');
      if (error.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        console.log(error.response.data);
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
    portfolio_visible: false,
    spiner_visible: true,
    errors_visible: false,
    portfolio_title: null,
    portfolio_info: null,
    portfolio_invests: null,
    errors: null,

  },
  beforeMount: function () {
    let portfolio_id = document.location.pathname.split('/')[3];
    let url = 'portfolios/' + portfolio_id;
    let em = this;
    HTTP.get(
      url
    ).then(function (resp) {
      let data = resp.data;
      console.log(resp);
      em.portfolio_title = data.title;

      em.portfolio_info = Object();
      em.portfolio_info.invest_cash = data.invest_cash;
      em.portfolio_info.today_cash = data.today_cash;
      em.portfolio_info.percent_profit = data.percent_profit;
      em.portfolio_info.change_percent_profit = data.change_percent_profit;
      em.portfolio_info.year_percent_profit = data.year_percent_profit;
      em.portfolio_info.change_year_percent_profit = data.change_year_percent_profit;
      em.portfolio_info.strategia = data.strategia;

      em.portfolio_info.is_owner = data.is_owner;
      if (data.is_owner) {
        em.portfolio_info.id = portfolio_id;
        em.portfolio_info.ostatok = data.ostatok;
        em.portfolio_info.created = new Date(data.created).toLocaleString('ru-RU');
        em.portfolio_invests = data.portfolio_invests;
        em.portfolio_info.ostatok_currency = data.securities.filter(
          item => item.security_type == 'currency');
        em.portfolio_info.manual = data.manual;

      } else {
        em.portfolio_info.owner_url = data.owner_url;
        em.portfolio_info.owner_name = data.owner_name;
      };
      em.spiner_visible = false;
      em.portfolio_visible = true;
    })
      .catch(function (error) {
        em.spiner_visible = false;
        em.errors_visible = true;
        console.log('FAILURE!!', error);
        if (error.response) {
          // The request was made and the server responded with a status code
          // that falls out of the range of 2xx
          console.log(error.response.data);
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
  },
  methods: {
    create: function () {
      return
    }
  },
  template: `
    <div id="app">
      <div v-if="portfolio_visible">
        <h3 class="align-self-center">Портфель: {{portfolio_title}}</h3>
        <b-tabs content-class="mt-3">
          <b-tab title="Главная" active>
            <div class="row">
              <portfolio-info
              class="col-sm-4"
              :portfolio_info_object="portfolio_info">
              </portfolio-info>
              <portfolio-invests
              class="col-sm-8"
              v-if="portfolio_info.is_owner"
              :portfolio_invests="portfolio_invests">
              </portfolio-invests>
            </div>
          </b-tab>
          <b-tab title="Настройки" v-bind:disabled="!portfolio_info.is_owner">
            <p>I'm the second tab</p>
          </b-tab>
        </b-tabs>
      </div>
      <errors class="mt-3" v-if="errors_visible" v-bind:errors="errors"></errors>
      <div v-if="spiner_visible" class="d-flex justify-content-center mt-3">
          <b-spinner label="Loading..."></b-spinner>
      </div>
    </div>
    `
})
