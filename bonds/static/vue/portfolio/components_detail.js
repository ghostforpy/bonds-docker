function return_RUB_locale(elem) {
  return parseFloat(elem)
    .toLocaleString('ru-RU', { style: 'currency', currency: 'RUB', maximumFractionDigits: 10 });
};
function return_percent_locale(elem) {
  return parseFloat(elem / 100)
    .toLocaleString('ru-RU', { style: 'percent', maximumFractionDigits: 10 });
};
Vue.component('portfolio-info', {
  props: ['portfolio_info_object'],
  data: function () {
    return {
      class_change_percent_profit: null,
      class_change_year_percent_profit: null,
      today_cash: null,
      portfolio_info: null,
      computed_percent_profit: null,
      computed_year_percent_profit: null,
      computed_change_percent_profit: null,
      computed_change_year_percent_profit: null
    }
  },
  beforeMount: function () {
    this.portfolio_info = this.portfolio_info_object;
    this.today_cash = this.portfolio_info.today_cash;
    this.prepare_profits();
  },
  methods: {
    prepare_profits() {
      let change_percent_profit = this.portfolio_info.change_percent_profit;
      if (change_percent_profit < 0) {
        this.class_change_percent_profit = ['fas', 'text-danger', 'fa-angle-double-down']
      } else if (change_percent_profit > 0) {
        this.class_change_percent_profit = ['fas', 'text-success', 'fa-angle-double-up']
      } else {
        this.class_change_percent_profit = ['text-secondary']
      };
      let change_year_percent_profit = this.portfolio_info.change_year_percent_profit;
      if (change_year_percent_profit < 0) {
        this.class_change_year_percent_profit = ['fas', 'text-danger', 'fa-angle-double-down']
      } else if (change_year_percent_profit > 0) {
        this.class_change_year_percent_profit = ['fas', 'text-success', 'fa-angle-double-up']
      } else {
        this.class_change_year_percent_profit = ['text-secondary']
      };
      this.computed_percent_profit = return_percent_locale(this.portfolio_info.percent_profit);
      this.computed_year_percent_profit = return_percent_locale(this.portfolio_info.year_percent_profit);
      this.computed_change_percent_profit = return_percent_locale(this.portfolio_info.change_percent_profit);
      this.computed_change_year_percent_profit = return_percent_locale(this.portfolio_info.change_year_percent_profit);
    },
    refreshManualPortfolio: function () {
      let formData = new FormData();
      formData.append('today_cash', parseFloat(this.today_cash));
      let url = 'portfolios/' + this.portfolio_info.id + '/';
      let em = this;
      HTTP.patch(
        url,
        formData
      ).then(function (resp) {
        console.log('SUCCESS!!');
        em.portfolio_info.change_percent_profit = resp.data.change_percent_profit;
        em.portfolio_info.change_year_percent_profit = resp.data.change_year_percent_profit;
        em.portfolio_info.percent_profit = resp.data.percent_profit;
        em.portfolio_info.year_percent_profit = resp.data.year_percent_profit;
        em.prepare_profits();
      })
        .catch(function (error) {
          console.log('FAILURE!!');
          if (error.response) {
            // The request was made and the server responded with a status code
            // that falls out of the range of 2xx
            console.log(error.response.data);
            if (error.response.status === 500) {
            } else {
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
  computed: {
    computed_invest_cash: function () {
      return return_RUB_locale(this.portfolio_info.invest_cash);
    },
    computed_today_cash: function () {
      return return_RUB_locale(this.portfolio_info.today_cash);
    },
    computed_ostatok: function () {
      return return_RUB_locale(this.portfolio_info.ostatok);
    }
  },
  template: `
      <div>
        <p v-if="!portfolio_info.is_owner">Владелец: <a v-bind:href="portfolio_info.owner_url">{{portfolio_info.owner_name}}</a></p>
        <p>Всего инвестиций: {{computed_invest_cash}}</p>
        <b-form-group
        id="input-group-1"
        label="Текущий баланс(₽):"
        label-for="input-1">
          <b-form-input
            v-if="portfolio_info.manual"
            id="input-1"
            v-model="today_cash"
            type="number"
            size="sm"
            required
          ></b-form-input>
        </b-form-group>
        <b-button v-if="portfolio_info.manual"
        variant="info"
        size="sm"
        @click="refreshManualPortfolio">Обновить</b-button>
        <p v-if="!portfolio_info.manual">Текущий баланс : {{computed_today_cash}}</p>
        <p v-if="portfolio_info.is_owner">Остаток: {{computed_ostatok}}</p>
        <portfolio-info-ostatok-currency
        :ostatok_currency=portfolio_info.ostatok_currency>
        </portfolio-info-ostatok-currency>
        <p>Доходность: {{computed_percent_profit}} <span v-bind:class="class_change_percent_profit">({{computed_change_percent_profit}})</span></p>
        <p>Годовая доходность: {{computed_year_percent_profit}} <span v-bind:class="class_change_year_percent_profit">({{computed_change_year_percent_profit}})</span></p>
        <p v-if="portfolio_info.strategia !== ''">Стратегия: <span>{{ portfolio_info.strategia }}</span></p>
        <p v-if="portfolio_info.is_owner">Создан: {{portfolio_info.created}}</p>
      </div>
    `
})
Vue.component('portfolio-info-ostatok-currency', {
  props: ['ostatok_currency'],
  computed: {
    computed_ostatok_currency: function () {
      return this.ostatok_currency.map(
        function (item) {
          item.count = parseFloat(item.count)
            .toLocaleString('ru-RU', { style: 'currency', currency: item.shortname, maximumFractionDigits: 2 });
          item.total_cost_in_rub = parseFloat(item.total_cost_in_rub)
            .toLocaleString('ru-RU', { style: 'currency', currency: 'RUB', maximumFractionDigits: 2 });
          return item
        }
      )
    }
  },
  template: `
  <div class="row">
    <div class="col-6"><span>Остаток валюты:</span></div>
    <div class="col-6">
      <p v-for="i in computed_ostatok_currency">
        {{i.count}} ({{i.total_cost_in_rub}})
      </p>
    </div>
  </div>
  `
})
Vue.component('portfolio-invests', {
  props: ['portfolio_invests'],
  data: function () {
    return {
      last_row_portfolio_invests: null,
      portfolio_invests_list: null
    }
  },
  beforeMount: function () {
    this.portfolio_invests_list = this.portfolio_invests;
    this.pop_last_row();
  },
  methods: {
    pop_last_row: function () {
      try {
        this.last_row_portfolio_invests = this.portfolio_invests_list.pop();
        this.last_row_portfolio_invests.index = this.portfolio_invests_list.length;
      } catch (error) {
      }

    },
    removeFromList: function (id) {
      this.portfolio_invests_list.push(this.last_row_portfolio_invests);
      this.portfolio_invests_list = this.portfolio_invests_list.filter(
        function (item, ind) {
          return (ind !== id)
        });
      this.pop_last_row();
    }

  },
  template: `
      <div>
        <b-button variant="secondary" class="mt-4 mb-2 col-12" v-b-toggle.collapseHistoryPortfolio>
        История движения денежных средств
        </b-button>
        <b-collapse id="collapseHistoryPortfolio">
          <div v-if="portfolio_invests_list">
            <div v-for="(one_row,index) in portfolio_invests_list">
              <portfolio-invests-one-row
              @removeItem="removeFromList(index)"
              :one_row=one_row>
              </portfolio-invests-one-row>
              <div class="dropdown-divider"></div>
            </div>
          </div>
          <div v-if="last_row_portfolio_invests">
            <portfolio-invests-one-row
            @removeItem="removeFromList(last_row_portfolio_invests.index)"
            :one_row=last_row_portfolio_invests>
            </portfolio-invests-one-row>
          </div>
        </b-collapse>
      </div>
    `
})
Vue.component('portfolio-invests-one-row', {
  props: ['one_row'],
  computed: {
    computed_cash: function () {
      return parseFloat(this.one_row.cash)
        .toLocaleString('ru-RU',
          {
            style: 'currency',
            currency: this.one_row.currency.replace('SUR', 'RUB'),
            maximumFractionDigits: 10
          });
    },
    computed_cash_in_rub: function () {
      return return_RUB_locale(this.one_row.cash_in_rub);
    },
    computed_ndfl: function () {
      return parseFloat(this.one_row.ndfl)
        .toLocaleString('ru-RU',
          {
            style: 'currency',
            currency: this.one_row.currency.replace('SUR', 'RUB'),
            maximumFractionDigits: 10
          });
    }
  },
  methods: {
    remove_one_row: function () {
      let elem = this;
      HTTP.delete(
        this.one_row.url_for_delete
      ).then(function (resp) {
        //em.spiner_visible = false;
        console.log('SUCCESS!!');
        elem.$emit('removeItem');
      })
        .catch(function (error) {
          //em.spiner_visible = false;
          //em.errors_visible = true;
          console.log('FAILURE!!');
          console.log(error);
          if (error.response) {
            // The request was made and the server responded with a status code
            // that falls out of the range of 2xx
            console.log(error.response.data);
            if (error.response.status === 500) {
              //em.errors = ['Server error'];
            } else {
              //em.errors = error.response.data;
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
  template: `
      <div class="row align-items-center">
        <div class="col-9">
          <div class="row">
            <div class="col-md-4">
              {{ one_row.date }}
            </div>
            <div class="col-md-4">
              {{ computed_cash }}
              <span v-if="one_row.currency != 'SUR'">({{computed_cash_in_rub}})</span>
              <span v-if="one_row.action == 'Доход'">(НДФЛ: {{ computed_ndfl }})</span>
            </div>
            <div class="col-md-4">
            {{ one_row.action }}</br>
            <span v-if="one_row.security">{{ one_row.security }}</span>
            </div>
          </div>
        </div>
          <div class="col-3">
            <b-button
            variant="danger"
            size="sm"
            @click="remove_one_row"
            >Удалить</b-button>
          </div>
      </div>  
    `
})




