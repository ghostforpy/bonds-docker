Vue.component('follow', {
  data: function () {
    return {
    }
  },
  beforeMount: function () {
  },
  computed: {
    text: function () {
      let st = this.$store.state.is_followed;
      return st ? 'Отписаться' : 'Подписаться'
    },
    variant: function () {
      let st = this.$store.state.is_followed;
      return st ? 'danger' : 'primary'
    }
  },
  methods: {
    toogleFollow: function () {
      let elem = this;
      let config = {
        method: 'post',
        url: this.$store.state.follow_url
      };
      request_service(config,
        function_success = function (resp) {
          elem.$store.dispatch('toogleFollow');
          if (resp.status == 200) {
            elem.$bvToast.toast('Подписка оформлена', {
              title: `Mybonds.space`,
              variant: 'success',
              solid: true
            })
          } else if (resp.status == 204) {
            elem.$bvToast.toast('Подписка удалена', {
              title: `Mybonds.space`,
              variant: 'danger',
              solid: true
            })
          }
        }
      );
    }
  },
  template: `
      <b-button
      size="sm"
      pill
      :variant="variant"
      class="mb-1 mt1"
      @click="toogleFollow">{{text}}
      </b-button>
      `
})

Vue.component('security-info', {
  props: ['security'],
  data: function () {
    return {
      currency: null
    }
  },
  beforeMount: function () {
    this.currency = this.security.main_board_faceunit.replace('SUR', 'RUB');
  },
  methods: {
    return_local_with_currency: function (elem) {
      return parseFloat(elem).toLocaleString('ru-RU', {
        style: 'currency',
        currency: this.currency,
        maximumFractionDigits: 10
      });
    }
  },
  computed: {
    computed_facevalue: function () {
      return this.return_local_with_currency(this.security.facevalue);
    },
    computed_initialfacevalue: function () {
      return this.return_local_with_currency(this.security.initialfacevalue);
    },
    computed_couponvalue: function () {
      return this.return_local_with_currency(this.security.couponvalue);
    },
    computed_accint: function () {
      return this.return_local_with_currency(this.security.accint);
    },
    computed_issuesize: function () {
      return parseFloat(this.security.issuesize).toLocaleString('ru-RU', {
        maximumFractionDigits: 10
      });
    },
    computed_couponpercent: function () {
      return parseFloat(this.security.couponpercent / 100)
        .toLocaleString('ru-RU', { style: 'percent', maximumFractionDigits: 10 });
    },
    computed_security_type: function () {
      return this.security.security_type
        .replace('share', 'Акция')
        .replace('bond', 'Облигация')
        .replace('pif_rshb', 'ОПИФ РСХБ')
        .replace(/^ppif$/, 'БПИФ')
        .replace('futures', 'Фьючерс')
        .replace('index', 'Индекс')
        .replace('etf_ppif', 'ETF')
        .replace('currency', 'Валюта')
        .replace('depositary_receipt', 'Депозитарная расписка')
    },
    computed_today_price: function () {
      return parseFloat(this.security.today_price)
        .toLocaleString('ru-RU', {
          style: 'currency',
          currency: this.security.main_board_faceunit.replace('SUR', 'RUB'),
          maximumFractionDigits: 10
        });
    },
    computed_change_price_percent: function () {
      return parseFloat(this.security.change_price_percent / 100)
        .toLocaleString('ru-RU', { style: 'percent', maximumFractionDigits: 10 });
    },
    computed_class_change_percent_profit: function () {
      let change_percent_profit = this.security.change_price_percent;
      if (change_percent_profit < 0) {
        return ['fas', 'text-danger', 'fa-angle-double-down']
      } else if (change_percent_profit > 0) {
        return ['fas', 'text-success', 'fa-angle-double-up']
      } else {
        return ['text-secondary']
      };
    }
  },
  template: `
      <div>
        <a v-if="security.url" :href="security.url">Перейти на сайт</a>
        <div v-if="security.security_type != 'currency'">
          <p v-if="security.fullname">Полное наименование: {{ security.fullname }}</p>
          <p v-if="security.code">Код: {{ security.code }}</p>
          <p v-if="security.regnumber">Рег.номер: {{ security.regnumber }}</p>
          <p v-if="security.secid">SECID: {{ security.secid }}</p>
          <p v-if="security.isin">ISIN: {{ security.isin }}</p>
        </div>
        <p v-if="security.facevalue && parseFloat(security.facevalue) != 0">Номинальная стоимость: {{ computed_facevalue }}</p>
        <p v-if="security.issuesize && parseFloat(security.issuesize) != 0">Объём выпуска: {{ computed_issuesize }}</p>
        <p v-if="security.main_board_faceunit && security.security_type != 'currency'"
        >Валюта номинала: {{ currency }}</p>
        <p v-if="security.initialfacevalue && parseFloat(security.initialfacevalue) != 0"
        >Первоначальная номинальная стоимость: {{ computed_initialfacevalue }}</p>
        <p v-if="security.matdate">Дата погашения: {{ security.matdate }}</p>
        <p v-if="security.coupondate">Дата выплаты купона: {{ security.coupondate }}</p>
        <p v-if="security.couponfrequency">Периодичность выплаты купона в год: {{ security.couponfrequency }}</p>
        <p v-if="security.couponpercent">Ставка купона: {{ computed_couponpercent }}</p>
        <p v-if="security.couponvalue">Сумма купона, в валюте номинала: {{ computed_couponvalue }}</p>
        <p v-if="security.accint">НКД: {{ computed_accint }}</p>
        <p v-if="security.emitent">Эмитент: {{ security.emitent }}</p>
        <p>Тип: {{ computed_security_type }}</p>
        <p>Цена: {{ computed_today_price}} <span v-bind:class="computed_class_change_percent_profit"
        >({{computed_change_price_percent}})</span></p>
        <p>Дата обновления: {{ security.last_update }}</p>
        <p v-if="security.description">Описание: {{ security.description }}</p>
      </div>
    `
});


function currency_sign(currency) {
  return currency.replace('RUB', '₽')
    .replace('SUR', '₽')
    .replace('РУБ', '₽')
    .replace('USD', '$')
    .replace('EUR', '€')
};
Vue.component('form-trade-securities', {
  data: function () {
    return {
      date: null,
      date_invalid: false,
      price: 0,
      main_board_faceunit: null,
      custom_currency: null,
      list_custom_currency: [
        { value: 'SUR', text: '₽' },
        { value: 'USD', text: '$' },
        { value: 'EUR', text: '€' }
      ],
      price_invalid: false,
      comission: 0,
      comission_invalid: false,
      nkd: 0,
      nkd_invalid: false,
      count: 0,
      count_invalid: false,
      total_cost: 0,
      componentKey: 0,
      trade_portfolio_id: null
      //selected: null,
      //options: null
    }
  },
  beforeMount: function () {
    //console.log('beforemount')
  },
  beforeDestroy: function () {
    //console.log('beforedestroy')
  },
  beforeUpdate: function () {
    //console.log('beforeupdate')
  },
  updated: function () {
    //console.log('updated')
  },
  created: function () {
    var elem = this;
    this.$root.$on('bv::modal::show', (bvEvent, modalId) => {
      //console.log('Modal is about to be shown', bvEvent, modalId);
      elem.date = elem.$store.state.trade_security_date.toJSON().split('T')[0];
      elem.price = elem.$store.state.trade_security_price;
      elem.calc_total_cost();
    })
    let trade_security = this.$store.state.security_info;
    this.main_board_faceunit = trade_security.main_board_faceunit;
    this.custom_currency = trade_security.main_board_faceunit;
    //elem.custom_currency = elem.currency();
  },
  computed: {
    computed_title: function () {
      let action = 'Покупка'
      let shortname = this.$store.state.security_info.shortname;
      let security_type = this.$store.state.security_info.security_type
        .replace('bond', 'облигаций')
        .replace('share', 'акций')
        .replace(/.*ppif$/, 'паёв')
        .replace('depositary_receipt', 'депозитарных расписок')
      return `${action} ${security_type} "${shortname}"`;
    },
    currency: function () {
      //let trade_security = this.$store.state.security_info;
      //if (trade_security) {
      //return currency_sign(trade_security.main_board_faceunit);
      //  return currency_sign(el.main_board_faceunit);
      //}
      //return null
      return currency_sign(this.custom_currency);
    },
    security_type: function () {
      let trade_security = this.$store.state.security_info;
      if (trade_security) {
        return trade_security.security_type;
      }
      return null
    },
    computed_date: function () {
      return this.$store.state.trade_date
    },
    computed_price: function () {
      return this.$store.state.price
    }
  },
  methods: {
    calc_total_cost: function () {
      this.total_cost = parseFloat(this.nkd) +
        parseFloat(this.count) * parseFloat(this.price);
      this.total_cost = this.total_cost + parseFloat(this.comission);
    },
    handleOk: function (bvModalEvt) {
      // Prevent modal from closing
      bvModalEvt.preventDefault()
      // Trigger submit handler
      if (this.validate()) {
        this.handleSubmit()
      }
    },
    validate: function () {
      if (this.date == null) {
        this.date_invalid = true
        return false
      } else {
        this.date_invalid = false
      };
      if (parseFloat(this.price) < 0) {
        this.price_invalid = true
        return false
      } else {
        this.price_invalid = false
      };
      if ((parseFloat(this.comission) < 0) ||
        parseFloat(this.comission) >= parseFloat(this.total_cost)) {
        this.comission_invalid = true
        return false
      } else {
        this.comission_invalid = false
      };
      if (parseFloat(this.nkd) < 0) {
        this.nkd_invalid = true
        return false
      } else {
        this.nkd_invalid = false
      };
      if (parseFloat(this.count) < 1) {
        this.count_invalid = true
        return false
      } else {
        this.count_invalid = false
      };
      return true
    },
    today: function () {
      return new Date()
    },
    options: function () {
      return this.$store.state.portfolios;
    },
    handleSubmit() {
      let elem = this;
      let formData = new FormData();
      formData.append('portfolio', elem.trade_portfolio_id);
      formData.append('date', elem.date);
      formData.append('commission', elem.comission);
      formData.append('count', elem.count);
      formData.append('price', elem.price);
      formData.append('nkd', elem.nkd);

      formData.append('currency', elem.custom_currency);

      formData.append('security_isin', elem.$store.state.security_info.isin);
      let config = {
        method: 'post',
        url: 'securities-trade-history/new-security-buy/',
        data: formData
      };
      request_service(
        config,
        function_success = function (resp) {

          elem.$bvToast.toast('Запись успешно добавлена', {
            title: `Mybonds.space`,
            variant: 'success',
            solid: true
          });
          setTimeout(() => {
            document.location.href = resp.data.next_url
          }, 1000);

        },
        function_error_response_other = function (error) {
          const h = elem.$createElement;
          // Create the message
          const vNodesMsg = [h('p', `Запись не добавлена`)];
          if (error.response.status === 400) {
            var status = error.response.data.data;
            vNodesMsg.push(h('p', `${status}`));
          };
          elem.$bvToast.toast(vNodesMsg, {
            title: `Mybonds.space`,
            variant: 'danger',
            solid: true
          })
        }
      );

      // Hide the modal manually
      this.$nextTick(() => {
        this.$bvModal.hide('modal-buy-security')
      })
    }
  },
  template: `
      <b-modal
      id="modal-buy-security"
      centered
      v-bind:title="computed_title"
      @ok="handleOk"
      :key="componentKey">
        <label for="datepicker">Дата:</label>
        <b-form-datepicker
        id="datepicker"
        v-model="date"
        :max="today()"
        v-bind:class="{ 'is-invalid': date_invalid  }"
        class="mb-2"></b-form-datepicker>
        <label for="portfolio">Портфель:</label>

        <b-form-select id="portfolio"
        class="mb-2"
        v-model="trade_portfolio_id"
        :options="$store.state.portfolios"></b-form-select>
        
        <label for="price">Цена ({{currency}}):</label>
        <b-form-input
        id="price"
        v-model="price"
        type="number"
        min="0"
        class="mb-2"
        v-bind:class="{ 'is-invalid': price_invalid  }"
        @update="calc_total_cost"></b-form-input>
        <label for="portfolio">Валюта:</label>
        <b-form-select id="currency"
        class="mb-2"
        v-model="custom_currency"
        :options="list_custom_currency"></b-form-select>
        <label for="comission">Комиссия ({{currency}}):</label>
        <b-form-input 
        id="comission" 
        v-model="comission" 
        type="number" 
        min="0" 
        max="price"
        class="mb-2"
        v-bind:class="{ 'is-invalid': comission_invalid  }"
        @update="calc_total_cost"></b-form-input>
        <label v-if="security_type == 'bond'" for="nkd">НКД ({{currency}}):</label>
        <b-form-input
        v-if="security_type == 'bond'"
        id="nkd"
        v-model="nkd"
        type="number"
        min="0"
        max="price"
        class="mb-2"
        v-bind:class="{ 'is-invalid': nkd_invalid  }"
        @update="calc_total_cost"></b-form-input>
        <label for="count">Количество (шт.):</label>
        <b-form-input 
        id="count" 
        v-model="count" 
        type="number" 
        min="0"
        class="mb-2"
        v-bind:class="{ 'is-invalid': count_invalid  }"
        @update="calc_total_cost"></b-form-input>
        <label for="total_cost">Общая сумма к оплате ({{currency}}):</label>
        <b-form-input id="total_cost" v-model="total_cost" type="number" readonly></b-form-input>
      </b-modal>
    `
})

Vue.component('security-history', {
  props: ['isin', 'currency'],
  data: function () {
    return {
      busy: false,
      next_url_security_history: 'first',
      history: []
    }
  },
  computed: {
  },
  methods: {
    loadMore: function () {
      if (this.busy) { return }
      this.busy = true;
      var elem = this;
      if (elem.next_url_security_history == 'first') {
        var config = {
          method: 'get',
          url: 'securities/' + elem.isin + '/new-history/'
        };
      } else if (elem.next_url_security_history != null) {
        var config = {
          method: 'get',
          url: elem.next_url_security_history
        };
      } else {
        return
      };
      request_service(
        config,
        function_success = function (resp) {
          resp.data.results.map(function (item) {
            elem.history.push(
              {
                price: parseFloat(item.price),
                date: new Date(
                  parseFloat(item.date.split('.')[2]),
                  parseFloat(item.date.split('.')[1]) - 1,
                  parseFloat(item.date.split('.')[0]))
              }
            )
          });
          elem.next_url_security_history = resp.data.next;
          elem.busy = false;
        },
        function_catch = function (error) {
          console.log(error)
        }
      );
    }
  },
  beforeMount: function () {
    this.loadMore();
  },
  template: `
      <div>
        <b-button variant="secondary" class="mt-4 mb-2 col-12" v-b-toggle.collapseSecurityHistory>
        История цен
        </b-button>
        <b-collapse id="collapseSecurityHistory" class="container-in-collapse">
          <div class="row">
            <div class="col-8 row">
              <div class="col-lg-4 .offset-lg-1 d-none d-md-block">
                <p>Дата</p>
              </div>
              <div class="col-lg-4 d-none d-md-block">
                <p>Цена</p>
              </div>
            </div>
            <div class="col-2 d-none d-md-block">
            </div>
          </div>
          <div v-if="history.length > 0">
            <div v-for="(one_row,index) in history">
              <div class="dropdown-divider"></div>
              <security-history-one-row
              :one_row=one_row
              :index=index
              :currency=currency>
              </security-history-one-row>
            </div>
            <div class="d-flex justify-content-center mt-2 mb-2"
            v-if="next_url_security_history != null">
              <button type="button" @click="loadMore" class="btn btn-primary btn-sm">
              <span v-show="busy" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
              Ещё</button>
            </div>
          </div>
          <div v-else class="col d-flex justify-content-center">
            <div class="spinner-border text-secondary" role="status">
              <span class="sr-only">Loading...</span>
            </div>
          </div>
        </b-collapse>
      </div>
  `
});
Vue.component('security-history-one-row', {
  props: ['one_row', 'index', 'currency'],
  data: function () {
    return {
    }
  },
  methods: {
    click: function (action) {
      this.$store.dispatch('set_trade_security_action', action);
      this.$store.dispatch('set_trade_security_date', this.one_row.date);
      this.$store.dispatch('set_trade_security_price', this.one_row.price);
      this.$bvModal.show('modal-buy-security');
    },
    buy_click: function () {
    },
    sell_click: function () {
    }
  },
  computed: {
    computed_price: function () {
      return parseFloat(this.one_row.price)
        .toLocaleString('ru-RU', {
          style: 'currency',
          currency: this.currency,
          maximumFractionDigits: 2
        });
    },
    computed_date: function () {
      return this.one_row.date
        .toLocaleString('ru-RU', { year: 'numeric', month: 'numeric', day: 'numeric' });
    }
  },
  beforeMount: function () {
  },
  template: `
      <div class="row">
        <div class="row col-8">
          <div class="col-lg-4 .offset-lg-1 col-12 mt-1 mb-1">
            <span class="d-md-none">Дата: </span>
            <span>{{computed_date}}</span>
          </div>
          <div class="col-lg-4 col-12 mb-1 mt-1">
            <span class="d-md-none">Цена: </span>
            <span>{{computed_price}}</span>
          </div>
        </div>
        <div class="col-4 mb-1 mt-1 d-flex justify-content-center align-content-center flex-wrap">
          <b-button
          size="sm"
          variant="success"
          class="mb-1 mt-1"
          @click="click('buy')">Купить</b-button>
        </div>
      </div>
  `
});