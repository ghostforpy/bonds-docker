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
  data: function () {
    return {
      security: null,
      facevalue: null,
      issuesize: null,
      initialfacevalue: null,
      couponpercent: null,
      couponvalue: null,
      accint: null
    }
  },
  beforeMount: function () {
    this.security = this.$store.state.security_info;
    this.facevalue = parseFloat(this.security.facevalue);
    this.issuesize = parseFloat(this.security.issuesize);
    this.initialfacevalue = parseFloat(this.security.initialfacevalue);
    this.couponpercent = parseFloat(this.security.couponpercent);
    this.couponvalue = parseFloat(this.security.couponvalue);
    this.accint = parseFloat(this.security.accint);
  },
  methods: {
    return_local_with_currency: function (elem) {
      return elem.toLocaleString('ru-RU', {
        style: 'currency',
        currency: this.security.main_board_faceunit,
        maximumFractionDigits: 10
      });
    }
  },
  computed: {
    computed_facevalue: function () {
      return this.return_local_with_currency(this.facevalue);
    },
    computed_initialfacevalue: function () {
      return this.return_local_with_currency(this.initialfacevalue);
    },
    computed_couponvalue: function () {
      return this.return_local_with_currency(this.couponvalue);
    },
    computed_accint: function () {
      return this.return_local_with_currency(this.accint);
    },
    computed_issuesize: function () {
      return this.issuesize.toLocaleString('ru-RU', {
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
        .replace('ppif', 'БПИФ')
        .replace('futures', 'Фьючерс')
        .replace('index', 'Индекс')
        .replace('etf_ppif', 'ETF')
        .replace('currency', 'Валюта')
    },
    computed_today_price: function () {
      return parseFloat(this.security.today_price)
        .toLocaleString('ru-RU', {
          style: 'currency',
          currency: this.security.main_board_faceunit,
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
        <p v-if="facevalue">Номинальная стоимость: {{ computed_facevalue }}</p>
        <p v-if="issuesize">Объём выпуска: {{ computed_issuesize }}</p>
        <p v-if="security.main_board_faceunit && security.security_type != 'currency'"
        >Валюта номинала: {{ security.main_board_faceunit }}</p>
        <p v-if="initialfacevalue"
        >Первоначальная номинальная стоимость: {{ computed_initialfacevalue }}</p>
        <p v-if="security.matdate">Дата погашения: {{ security.matdate }}</p>
        <p v-if="security.coupondate">Дата выплаты купона: {{ security.coupondate }}</p>
        <p v-if="security.couponfrequency">Периодичность выплаты купона в год: {{ security.couponfrequency }}</p>
        <p v-if="couponpercent">Ставка купона: {{ computed_couponpercent }}</p>
        <p v-if="couponvalue">Сумма купона, в валюте номинала: {{ computed_couponvalue }}</p>
        <p v-if="accint">НКД: {{ computed_accint }}</p>
        <p v-if="security.emitent">Эмитент: {{ security.emitent }}</p>
        <p>Тип: {{ computed_security_type }}</p>
        <p>Цена: {{ computed_today_price}} <span v-bind:class="computed_class_change_percent_profit"
        >({{computed_change_price_percent}})</span></p>
        <p>Дата обновления: {{ security.last_update }}</p>
        <p v-if="security.description">Описание: {{ security.description }}</p>
      </div>
    `
});

Vue.component('security-in-portfolios', {
  data: function () {
    return {
    }
  },
  beforeMount: function () {
  },
  computed: {
    computed_security_in_portfolio: function () {
      return this.$store.state.security_in_portfolios;
    },
  },
  methods: {
  },
  template: `
      <div>
      <b-button variant="secondary" class="mt-4 mb-2 col-12" v-b-toggle.collapsePortfolios>
      Ваши портфели
        </b-button>
        <b-collapse id="collapsePortfolios" class="container-in-collapse">
          <div class="row">
            <div class="col-9 col-md-10 row">
              <div class="col-md-3 d-none d-md-block">
                <p>Портфель</p>
              </div>
              <div class="col-md-3 d-none d-md-block">
                <p>Количество</p>
              </div>
              <div class="col-2 col-md-4 d-none d-md-block">
                <p>Сумма</p>
              </div>
            </div>
            <div class="col-md-2 d-none d-md-block">
            </div>
          </div>
          <div v-for="(one_row,index) in computed_security_in_portfolio">
            <div class="dropdown-divider"></div>
            <portfolio-item-one-row
            :one_row=one_row>
            </portfolio-item-one-row>
          </div>
        </b-collapse>
      </div>
    `
});
Vue.component('portfolio-item-one-row', {
  props: ['one_row'],
  data: function () {
    return {
      currency: null
    }
  },
  beforeMount: function () {
    this.currency = this.$store.state.security_info.main_board_faceunit;
  },
  computed: {
    computed_count: function () {
      return parseFloat(this.one_row.count)
        .toLocaleString('ru-RU', { maximumFractionDigits: 10 });
    },
    computed_cost: function () {
      return parseFloat(this.one_row.total_cost)
        .toLocaleString('ru-RU', {
          style: 'currency',
          currency: this.currency,
          maximumFractionDigits: 2
        });
    },
    computed_cost_in_rub: function () {
      return parseFloat(this.one_row.total_cost_in_rub)
        .toLocaleString('ru-RU', {
          style: 'currency',
          currency: 'RUB',
          maximumFractionDigits: 2
        });
    }

  },
  methods: {
    buy_click: function () {
      this.$store.commit('set_trade_portfolio_id', this.one_row.portfolio);
      this.$store.commit('set_trade_security_action', 'buy');
      this.$bvModal.show('modal-buy-security');
    },
    sell_click: function () {
      this.$store.commit('set_trade_portfolio_id', this.one_row.portfolio);
      this.$store.commit('set_trade_security_action', 'sell');
      this.$bvModal.show('modal-buy-security');
    }
  },
  template: `
      <div class="row">
        <div class="col-9 col-md-10 row">
          <div class="col-12 col-md-3 mb-1 mt-1">
            <span class="d-md-none">Портфель: </span><a class="btn btn-warning btn-sm" :href="one_row.portfolio_url">{{ one_row.portfolio_name}}</a>
          </div>
          <div class="col-12 col-md-3 mb-1 mt-1">
            <span class="d-md-none">Количество: </span><span>{{ computed_count }} шт.</span>
          </div>
          <div class="col-12 col-md-4 mb-1 mt-1">
            <span class="d-md-none">Сумма: </span><span>{{ computed_cost }}</span>
            <span v-if="currency != 'RUB'">({{ computed_cost_in_rub }})</span>
          </div>
        </div>
        <div class="col-2 col-md-2 mb-1 mt-1">
          <b-button
          size="sm"
          variant="success"
          class="mb-1 mt1"
          @click="buy_click">Купить</b-button>
          <b-button
          size="sm"
          variant="danger"
          class="mb-1 mt1"
          @click="sell_click">Продать</b-button>
        </div>
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
      price_invalid: false,
      comission: 0,
      comission_invalid: false,
      nkd: 0,
      nkd_invalid: false,
      count: 0,
      count_invalid: false,
      total_cost: 0,
      //selected: null,
      //options: null
    }
  },
  beforeMount: function () {

  },
  beforeDestroy: function () {

  },
  computed: {
    computed_title: function () {
      if (this.$store.state.trade_security_action) {
        let action = this.$store.state.trade_security_action
          .replace('buy', 'Покупка')
          .replace('sell', 'Продажа');
        let shortname = this.$store.state.security_info.shortname;
        let security_type = this.$store.state.security_info.security_type
          .replace('bond', 'облигаций')
          .replace('share', 'акций')
          .replace('ppif', 'паёв')
        return `${action} ${security_type} "${shortname}"`;
      }
    },
    computed_action: function () {
      if (this.$store.state.trade_security_action) {
        return this.$store.state.trade_security_action
          .replace('buy', 'оплате')
          .replace('sell', 'выплате')
      }
    },
    currency: function () {
      let trade_security = this.$store.state.security_info;
      if (trade_security) {
        return currency_sign(trade_security.main_board_faceunit);
      }
      return null
    },
    security_type: function () {
      let trade_security = this.$store.state.security_info;
      if (trade_security) {
        return trade_security.security_type;
      }
      return null
    }
  },
  methods: {
    calc_total_cost: function () {
      let action = this.$store.state.trade_security_action;
      this.total_cost = parseFloat(this.count) * parseFloat(this.price) + parseFloat(this.nkd);
      if (action == 'sell') {
        this.total_cost = this.total_cost - parseFloat(this.comission);
      } else {
        this.total_cost = this.total_cost + parseFloat(this.comission);
      }
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
      if ((parseFloat(this.comission) < 0) || parseFloat(this.comission) >= parseFloat(this.price)) {
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

      formData.append('portfolio', elem.$store.state.trade_portfolio_id);

      formData.append('date', elem.date);
      formData.append('commission', elem.comission);
      formData.append('count', elem.count);
      formData.append('price', elem.price);
      formData.append('nkd', elem.nkd);
      formData.append('ndfl', 0);
      let trade_security_id = elem.$store.state.security_id;
      formData.append('security', trade_security_id);
      formData.append('buy', elem.$store.state.trade_security_action == 'buy');
      let config = {
        method: 'post',
        url: 'securities-trade-history/',
        data: formData
      };
      request_service(
        config,
        function_success = function (resp) {
          elem.$store.dispatch('get_security', security_id = elem.$store.state.security_id);
          elem.$bvToast.toast('Запись успешно добавлена', {
            title: `Mybonds.space`,
            variant: 'success',
            solid: true
          })
        },
        function_error_response_other = function (error) {
          const h = elem.$createElement;
          // Create the message
          const vNodesMsg = [h('p', `Запись не добавлена`)];
          if (error.response.status === 400) {
            var status = error.response.data;
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
      @ok="handleOk">
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
        v-model="$store.state.trade_portfolio_id"
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
        <label for="total_cost">Общая сумма к {{computed_action}} ({{currency}}):</label>
        <b-form-input id="total_cost" v-model="total_cost" type="number" readonly></b-form-input>
      </b-modal>
    `
})

Vue.component('security-trades', {
  data: function () {
    return {
    }
  },
  beforeMount: function () {
  },
  computed: {
    computed_security_trades: function () {
      return this.$store.state.security_trades;
    },
  },
  methods: {
  },
  template: `
      <div>
      <b-button variant="secondary" class="mt-4 mb-2 col-12" v-b-toggle.collapseTrades>
      История торгов
        </b-button>
        <b-collapse id="collapseTrades" class="container-in-collapse">
          <div class="row">
            <div class="col-md-2 d-none d-md-block">
              <p>Портфель</p>
            </div>
            <div class="col-md-2 d-none d-md-block">
              <p>Количество</p>
            </div>
            <div class="col-md-2 d-none d-md-block">
              <p>Цена</p>
            </div>
            <div class="col-md-2 d-none d-md-block">
              <p>Действие</p>
            </div>
            <div class="col-md-2 d-none d-md-block">
              <p>Дата</p>
            </div>
          </div>
          <div v-for="(one_row,index) in computed_security_trades">
            <div class="dropdown-divider"></div>
            <security-trades-one-row
            :one_row=one_row>
            </security-trades-one-row>
          </div>
        </b-collapse>
      </div>
    `
});
Vue.component('security-trades-one-row', {
  props: ['one_row'],
  data: function () {
    return {
      currency: null
    }
  },
  beforeMount: function () {
    this.currency = this.$store.state.security_info.main_board_faceunit;
  },
  computed: {
    computed_count: function () {
      return parseFloat(this.one_row.count)
        .toLocaleString('ru-RU', { maximumFractionDigits: 10 });
    },
    computed_action: function () {
      return this.one_row.buy ? 'Покупка' : 'Продажа'
    },
    computed_price: function () {
      return parseFloat(this.one_row.price)
        .toLocaleString('ru-RU', {
          style: 'currency',
          currency: this.currency,
          maximumFractionDigits: 2
        });
    },
    computed_commission: function () {
      return parseFloat(this.one_row.commission)
        .toLocaleString('ru-RU', {
          style: 'currency',
          currency: this.currency,
          maximumFractionDigits: 2
        });
    }

  },
  methods: {
    delete_item: function () {
      //this.$store.commit('set_trade_portfolio_id', this.one_row.portfolio);
      //this.$store.commit('set_trade_security_action', 'sell');
      //this.$bvModal.show('modal-buy-security');
      let elem = this;
      let config = {
        method: 'delete',
        url: this.one_row.url_for_delete,
      };
      request_service(
        config,
        function_success = function (resp) {
          console.log(resp);
          elem.$store.dispatch('get_security', security_id = elem.$store.state.security_id);
          elem.$bvToast.toast('Запись успешно удалена', {
            title: `Mybonds.space`,
            variant: 'success',
            solid: true
          })
        },
        function_error_response_other = function (error) {
          const h = elem.$createElement;
          // Create the message
          const vNodesMsg = [h('p', `Запись не удалена`)];
          if (error.response.status === 400) {
            var status = error.response.data;
            vNodesMsg.push(h('p', `${status}`));
          };
          elem.$bvToast.toast(vNodesMsg, {
            title: `Mybonds.space`,
            variant: 'danger',
            solid: true
          })
        }
      );
    }
  },
  template: `
      <div class="row">
        <div class="col-md-2 col-12 mb-1 mt-1">
          <span class="d-md-none">Портфель: </span><a class="btn btn-warning btn-sm" :href="one_row.portfolio_url">{{ one_row.portfolio_name}}</a>
        </div>
        <div class="col-md-2 col-12 mb-1 mt-1">
          <span class="d-md-none">Количество: </span><span>{{ computed_count }} шт.</span>
        </div>
        <div class="col-md-2 col-12 mb-1 mt-1">
          <span class="d-md-none">Цена: </span><span>{{ computed_price }}</span>
        </div>
        <div class="col-md-2 col-12 mb-1 mt-1">
          <span class="d-md-none">Действие: </span><span>{{computed_action}}</span>
        </div>
        <div class="col-md-2 col-12 mb-1 mt-1">
          <span class="d-md-none">Дата: </span><span>{{ one_row.date }}</span>
        </div>
        <div class="col-md-2 col-12 mb-1 mt-1">
        <b-button
        size="sm"
        variant="danger"
        class="mb-1 mt1"
        @click="delete_item">Удалить запись</b-button>
        </div>
      </div>
    `
});