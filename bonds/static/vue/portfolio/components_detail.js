function currency_sign(currency) {
  return currency.replace('RUB', '₽')
    .replace('SUR', '₽')
    .replace('РУБ', '₽')
    .replace('USD', '$')
    .replace('EUR', '€')
};
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
      today_cash: null,
      portfolio_info: null,
    }
  },
  beforeMount: function () {
    this.portfolio_info = this.portfolio_info_object;
    this.today_cash = this.portfolio_info.today_cash;
    this.prepare_profits();
  },
  beforeUpdate: function () {
    this.prepare_profits();
  },
  methods: {
    prepare_profits() {
    },
    refreshManualPortfolio: function () {
      let formData = new FormData();
      formData.append('today_cash', parseFloat(this.today_cash));
      let em = this;

      let config = {
        method: 'patch',
        url: 'portfolios/' + em.portfolio_info.id + '/',
        data: formData
      };
      request_service(
        config,
        function_success = function (resp) {
          console.log('SUCCESS!!');
          // переписать
          em.portfolio_info.change_percent_profit = resp.data.change_percent_profit;
          em.portfolio_info.change_year_percent_profit = resp.data.change_year_percent_profit;
          em.portfolio_info.percent_profit = resp.data.percent_profit;
          em.portfolio_info.year_percent_profit = resp.data.year_percent_profit;
          em.prepare_profits();
          elem.$bvToast.toast('Портфель обновлён.', {
            title: `Mybonds.space`,
            variant: 'success',
            solid: true
          })
        }
      );
    }
  },
  computed: {
    computed_invest_cash: function () {
      return return_RUB_locale(this.$store.state.portfolio_info.invest_cash);
    },
    computed_today_cash: function () {
      return return_RUB_locale(this.$store.state.portfolio_info.today_cash);
    },
    computed_ostatok: function () {
      return return_RUB_locale(this.$store.state.portfolio_info.ostatok);
    },
    is_deny: function () {
      return this.$store.state.is_deny;
    },
    portfolio_ostatok_currency: function () {
      return this.$store.state.portfolio_info.ostatok_currency
    },
    computed_year_percent_profit: function () {
      return return_percent_locale(this.$store.state.portfolio_info.year_percent_profit);
    },
    computed_percent_profit: function () {
      return return_percent_locale(this.$store.state.portfolio_info.percent_profit);
    },
    computed_change_percent_profit: function () {
      return return_percent_locale(this.$store.state.portfolio_info.change_percent_profit);
    },
    computed_change_year_percent_profit: function () {
      return return_percent_locale(this.$store.state.portfolio_info.change_year_percent_profit);
    },
    computed_class_change_percent_profit: function () {
      let change_percent_profit = this.$store.state.portfolio_info.change_percent_profit;
      if (change_percent_profit < 0) {
        return ['fas', 'text-danger', 'fa-angle-double-down']
      } else if (change_percent_profit > 0) {
        return ['fas', 'text-success', 'fa-angle-double-up']
      } else {
        return ['text-secondary']
      };
    },
    computed_class_change_year_percent_profit: function () {
      let change_year_percent_profit = this.portfolio_info.change_year_percent_profit;
      if (change_year_percent_profit < 0) {
        return ['fas', 'text-danger', 'fa-angle-double-down']
      } else if (change_year_percent_profit > 0) {
        return ['fas', 'text-success', 'fa-angle-double-up']
      } else {
        return ['text-secondary']
      };
    }
  },
  template: `
      <div>
        <p v-if="!portfolio_info.is_owner">Владелец: <a v-bind:href="portfolio_info.owner_url">{{portfolio_info.owner_name}}</a></p>
        <div 
        v-if="!is_deny">
          <p>Всего инвестиций: {{computed_invest_cash}}</p>
          <b-form-group
          v-if="portfolio_info.manual"
          id="input-group-1"
          label="Текущий баланс(₽):"
          label-for="input-1">
            <b-form-input
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
          <p v-if="portfolio_info.is_owner && !portfolio_info.manual">Остаток: {{computed_ostatok}}</p>
          <portfolio-info-ostatok-currency
          v-if="portfolio_info.is_owner && portfolio_ostatok_currency.length"
          :ostatok_currency=portfolio_ostatok_currency>
          </portfolio-info-ostatok-currency>
          <p>Доходность: {{computed_percent_profit}} <span v-bind:class="computed_class_change_percent_profit">({{computed_change_percent_profit}})</span></p>
          <p>Годовая доходность: {{computed_year_percent_profit}} <span v-bind:class="computed_class_change_year_percent_profit">({{computed_change_year_percent_profit}})</span></p>
          <p v-if="portfolio_info.strategia !== '' && portfolio_info.strategia !== 'null'">Стратегия: <span>{{ portfolio_info.strategia }}</span></p>
          <p v-if="portfolio_info.is_owner">Создан: {{portfolio_info.created}}</p>
        </div>
        <p v-if="is_deny">Портфель приватный, обратитесь к владельцу для предоставления доступа.</p>
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
  <div class="d-flex flex-row">
    <div class=""><span>Остаток валюты:</span></div>
    <div class="mx-1">
      <p v-for="i in computed_ostatok_currency">
        {{i.count}} ({{i.total_cost_in_rub}})
      </p>
    </div>
  </div>
  `
})
Vue.component('portfolio-invests', {
  //props: ['portfolio_invests', 'portfolio_id', 'ever_trade_securities'],
  data: function () {
    return {
      //last_row_portfolio_invests: null,
      //portfolio_invests_list: null,
      //portfolio_id: null,
      //ever_trade_securities: null
    }
  },
  beforeMount: function () {

  },
  computed: {
    portfolio_invests_list: function () {
      return this.$store.state.portfolio_invests;
    },
    portfolio_id: function () {
      return this.$store.state.portfolio_id;
    },
    ever_trade_securities: function () {
      return this.$store.state.ever_trade_securities;
    }
  },
  methods: {
    removeFromList: function (id) {
      this.$store.commit('removeItemFromPortfolioInvests', id);
      this.$store.dispatch('get_updated_portfolio', simple = true);
    },
    addToList: function (new_item) {
      this.$store.commit('addItemToPortfolioInvests', new_item);
      this.$store.dispatch('get_updated_portfolio', simple = true);
    }

  },
  template: `
      <div>
        <b-button variant="secondary" class="mt-4 mb-2 col-12" v-b-toggle.collapseHistoryPortfolio>
        История движения денежных средств
        </b-button>
        <b-collapse id="collapseHistoryPortfolio" class="container-in-collapse">
        <add-portfolio-invests
        :ever_trade_securities="ever_trade_securities"
        :portfolio_id=portfolio_id
        @addToList="addToList">
        </add-portfolio-invests>
          <div v-if="portfolio_invests_list">
            <div v-for="(one_row,index) in portfolio_invests_list">
              <div class="dropdown-divider"></div>
              <portfolio-invests-one-row
              @removeItem="removeFromList(index)"
              :one_row=one_row>
              </portfolio-invests-one-row>
            </div>
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
      let config = {
        method: 'delete',
        url: elem.one_row.url_for_delete
      };
      request_service(
        config,
        function_success = function (resp) {
          elem.$emit('removeItem');
          elem.$bvToast.toast('Запись успешно удалена', {
            title: `Mybonds.space`,
            variant: 'success',
            solid: true
          })
        },
        function_catch = function (error) {
          elem.$bvToast.toast(`Запись не удалена`, {
            title: `Mybonds.space`,
            variant: 'danger',
            solid: true
          })
        }
      );
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

Vue.component('add-portfolio-invests', {
  props: ['ever_trade_securities', 'portfolio_id'],
  data: function () {
    return {
      date: null,
      cash: null,
      ndfl: null,
      date_format_options: {
        'year': 'numeric', 'month': 'numeric', 'day': 'numeric'
      },
      selected_security: null,
      selected_currency: 'SUR',
      list_security: [
        { value: null, text: 'Выберите бумагу' }
      ],
      list_currency: [
        { value: 'SUR', text: 'РУБ' },
        { value: 'USD', text: 'USD' },
        { value: 'EUR', text: 'EUR' }
      ],
      selected_action: 'vp',
      list_action: [
        { value: 'tp', text: 'Доход' },
        { value: 'br', text: 'Частичное погашение облигаций' },
        { value: 'vp', text: 'Пополнение' },
        { value: 'pv', text: 'Снятие' },
        { value: 'tax', text: 'Налог на доход' },
        { value: 'bc', text: 'Комиссия брокера' }
      ],
      date_invalid: false,
      ndfl_invalid: false,
      cash_invalid: false
    }
  },
  beforeMount: function () {
    let ids = new Array();
    let k = this.ever_trade_securities.filter(function (item) {
      if (!ids.includes(item.value)) {
        ids.push(item.value);
        return true
      }
      return false
    });
    this.list_security.push(...k);
  },
  methods: {
    today: function () {
      return new Date()
    },
    validate_form: function () {
      if (this.date === null) {
        this.date_invalid = true;
        return false
      };
      this.date_invalid = false;
      if ((this.cash === null) || (parseFloat(this.cash) <= 0)) {
        this.$bvToast.toast('Сумма должна быть больше 0.', {
          title: `Mybonds.space`,
          variant: 'danger',
          solid: true
        })
        this.cash_invalid = true;
        return false
      }
      this.cash_invalid = false;
      if (this.selected_action === 'tp') {
        if (
          (this.ndfl === null) ||
          (parseFloat(this.ndfl) < 0) ||
          (parseFloat(this.ndfl) >= parseFloat(this.cash))
        ) {
          this.$bvToast.toast('НДФЛ должен быть больше 0 и меньше суммы.', {
            title: `Mybonds.space`,
            variant: 'danger',
            solid: true
          })
          this.ndfl_invalid = true;
          return false
        }
        this.ndfl_invalid = false;
      }

      return true
    },
    addInvest: function () {
      let elem = this;
      let formData = new FormData();
      if (!this.validate_form()) {
        return
      }
      formData.append('portfolio', elem.portfolio_id);
      formData.append('date', elem.date);
      formData.append('cash', elem.cash);
      formData.append('action', elem.selected_action);
      formData.append('ndfl', elem.selected_action === 'tp' ? elem.ndfl : 0);
      formData.append('security', elem.selected_security !== null ? elem.selected_security : '');
      formData.append('currency', elem.selected_currency);
      let config = {
        method: 'post',
        url: 'portfolios-invest-history/',
        data: formData
      };
      request_service(
        config,
        function_success = function (resp) {
          let new_item = new Object();
          new_item.action = resp.data.action_display;
          new_item.cash = resp.data.cash;
          new_item.cash_in_rub = resp.data.cash_in_rub;
          new_item.currency = resp.data.currency;
          new_item.date = resp.data.date;
          new_item.id = resp.data.id;
          new_item.ndfl = resp.data.ndfl;
          new_item.security = resp.data.security ? resp.data.security_name : null;
          new_item.url_for_delete = resp.data.url_for_delete;
          elem.$emit('addToList', new_item);
          elem.$bvToast.toast('Запись успешно добавлена', {
            title: `Mybonds.space`,
            variant: 'success',
            solid: true
          })
        }
      );
    }
  },
  template: `
  <div class="row align-items-center">
    <div class="col-9">
      <div class="row align-items-center">
        <div class="col-md-4">
          <b-form-datepicker
          ref="date"
          label-no-date-selected="Выберите дату"
          :date-format-options="date_format_options"
          :max="today()"
          v-bind:class="{ 'is-invalid': date_invalid  }"
          v-model="date" size="sm" class="mt-1 mb-2" required></b-form-datepicker>
        </div>
        <div class="col-md-4">
          <b-form-input
            class="mt-1 mb-2"
            placeholder="Введите сумму"
            v-bind:class="{ 'is-invalid': cash_invalid  }"
            ref="cash"
            v-model="cash"
            type="number"
            size="sm"
            required
          ></b-form-input>
          <b-form-select size="sm" class="mt-1 mb-2"
          v-model="selected_currency" :options="list_currency">
          </b-form-select>
          <transition name="fade">
            <b-form-input
              v-if="selected_action == 'tp'"
              class="mt-1 mb-2"
              placeholder="НДФЛ"
              ref="ndfl"
              v-model="ndfl"
              v-bind:class="{ 'is-invalid': ndfl_invalid  }"
              type="number"
              size="sm"
            ></b-form-input>
          </transition>
          <transition name="fade">
            <b-form-select
            size="sm"
            v-if="(selected_action == 'tp')||(selected_action == 'br')||(selected_action == 'tax')"
            v-model="selected_security"
            :options="list_security"
            class="mt-1 mb-2"></b-form-select>
          </transition>
        </div>
        <div class="col-md-4">
          <b-form-select
          size="sm"
          v-model="selected_action"
          :options="list_action"
          class="mt-1 mb-2"></b-form-select>
        </div>
      </div>
    </div>
    <div class="col-3">
      <b-button
      variant="success"
      size="sm"
      @click="addInvest"
      >Добавить</b-button>
    </div>
  </div>
  `
})

Vue.component('portfolio-securities', {
  data: function () {
    return {
      is_owner: false
    }
  },
  beforeMount: function () {
    this.is_owner = this.$store.state.is_owner;
  },
  computed: {
    portfolio_securities_list: function () {
      return this.$store.state.portfolio_securities;
    }
  },
  methods: {
  },
  template: `
      <div>
        <b-button variant="secondary" class="mt-4 mb-2 col-12" v-b-toggle.collapseSecurityInPortfolio>
        Состав портфеля
        </b-button>
        <b-collapse id="collapseSecurityInPortfolio" class="container-in-collapse">
          <div class="row">
            <div class="col-md-3 col-12 mt-1 d-none d-md-block">
              <p>Наименование</p>
            </div>
            <div class="col-md-3 col-12 mt-1 d-none d-md-block">
              <p>Количество</p>
            </div>
            <div class="col-md-2 col-12 mt-1 d-none d-md-block">
              <p>Цена</p>
            </div>
            <div class="col-md-2 col-12 mt-1 d-none d-md-block">
              <p>Итого</p>
            </div>
            <div class="col-md-1 col-12 mt-1 d-none d-md-block">
            </div>
          </div>
          <div v-if="portfolio_securities_list">
            <div v-for="(one_row,index) in portfolio_securities_list">
              <div class="dropdown-divider"></div>
              <portfolio-securities-one-row
              :one_row=one_row
              :is_owner=is_owner>
              </portfolio-securities-one-row>
            </div>
          </div>
        </b-collapse>
      </div>
    `
})

Vue.component('portfolio-securities-one-row', {
  props: ['one_row', 'is_owner'],
  data: function () {
    return {
      class_change_price_percent: null,
      security_id: null
    }
  },
  computed: {
    computed_count: function () {
      return parseFloat(this.one_row.count)
        .toLocaleString('ru-RU',
          {
            maximumFractionDigits: 10
          });
    },
    computed_total_cost_in_rub: function () {
      return return_RUB_locale(this.one_row.total_cost_in_rub);
    },
    computed_change_price_percent: function () {
      return parseFloat(this.one_row.security_change_price_percent);
    },
    computed_security_change_price_percent: function () {
      return return_percent_locale(this.one_row.security_change_price_percent);
    },
    computed_total_cost: function () {
      return parseFloat(this.one_row.total_cost)
        .toLocaleString('ru-RU',
          {
            style: 'currency',
            currency: this.one_row.security_faceunit.replace('SUR', 'RUB'),
            maximumFractionDigits: 2
          });
    },
    computed_price: function () {
      return parseFloat(this.one_row.today_price)
        .toLocaleString('ru-RU',
          {
            style: 'currency',
            currency: this.one_row.security_faceunit.replace('SUR', 'RUB'),
            maximumFractionDigits: 10
          });
    }
  },
  beforeMount: function () {
    let security_change_price_percent = this.one_row.security_change_price_percent;
    if (security_change_price_percent < 0) {
      this.class_change_price_percent = ['fas', 'text-danger', 'fa-angle-double-down']
    } else if (security_change_price_percent > 0) {
      this.class_change_price_percent = ['fas', 'text-success', 'fa-angle-double-up']
    } else {
      this.class_change_price_percent = ['text-secondary']
    };
    this.security_id = this.one_row.security_url.split('/')[2];
  },
  methods: {
    buy_click: function () {
      this.$store.commit('set_trade_security', this.one_row);
      this.$store.commit('set_trade_security_action', 'buy');
      this.$bvModal.show('modal-buy-security');
    },
    sell_click: function () {
      this.$store.commit('set_trade_security', this.one_row);
      this.$store.commit('set_trade_security_action', 'sell');
      this.$bvModal.show('modal-buy-security');
    }
  },
  template: `
      <div class="row align-items-center">
        <div class="col-md-3 col-12 mb-1 mt-1">
          <a class="btn btn-warning btn-sm" v-bind:href="one_row.security_url">{{ one_row.shortname }}</a>
        </div>
        <div class="col-md-3 col-12 mb-1 mt-1">
          <span class="d-md-none">Количество: </span><span>{{ computed_count }} шт.</span>
        </div>
        <div class="col-md-2 col-12 mb-1 mt-1">
          <span class="d-md-none">Цена: </span><span>{{ computed_price }}<br class="d-md-inline d-none"><span class="d-md-none d-inline"> </span>
            <span v-bind:class="class_change_price_percent">({{computed_security_change_price_percent}})</span>
          </span>
        </div>
        <div class="col-md-2 col-12 mb-1 mt-1">
          <span class="d-md-none">Итого: </span><span>{{ computed_total_cost }}</span>
          <span v-if="one_row.security_faceunit != 'SUR'">({{ computed_total_cost_in_rub}})</span>
        </div>
        <div v-if="is_owner" class="col-md-1 col-12 mb-1 mt-1">
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
})

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
      total_cost: 0
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
        let shortname = this.$store.state.trade_security.shortname;
        let security_type = this.$store.state.trade_security.security_type
          .replace('bond', 'облигаций')
          .replace('share', 'акций')
          .replace(/.*ppif$/, 'паёв')
          .replace('depositary_receipt', 'депозитарных расписок')
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
      let trade_security = this.$store.state.trade_security;
      if (trade_security) {
        return currency_sign(trade_security.security_faceunit);
      }
      return null
    },
    security_type: function () {
      let trade_security = this.$store.state.trade_security;
      if (trade_security) {
        return currency_sign(trade_security.security_type);
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
      if ((parseFloat(this.comission) < 0) || parseFloat(this.comission) >= parseFloat(this.total_cost)) {
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
    handleSubmit() {
      let elem = this;
      let formData = new FormData();
      formData.append('portfolio', elem.$store.state.portfolio_id);
      formData.append('date', elem.date);
      formData.append('commission', elem.comission);
      formData.append('count', elem.count);
      formData.append('price', elem.price);
      formData.append('nkd', elem.nkd);
      formData.append('ndfl', 0);
      let trade_security_id = elem.$store.state.trade_security.security_url.split('/')[3];
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
          elem.$store.commit('addItemToTradeSecurities', resp.data);
          elem.$store.dispatch('get_updated_portfolio', simple = false);
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

Vue.component('portfolio-trade-history', {
  data: function () {
    return {
    }
  },
  beforeMount: function () {
  },
  computed: {
    portfolio_trade_history_list: function () {
      return this.$store.state.trade_securities;
    }
  },
  methods: {
  },
  template: `
      <div>
        <b-button variant="secondary" class="mt-4 mb-2 col-12" v-b-toggle.collapseTradeSecurityHistory>
        История торгов
        </b-button>
        <b-collapse id="collapseTradeSecurityHistory" class="container-in-collapse">
          <div class="row">
            <div class="col-md-2 d-none d-md-block">
              <p>Наименование</p>
            </div>
            <div class="col-md-2 d-none d-md-block">
              <p>Количество</p>
            </div>
            <div class="col-md-2 d-none d-md-block">
              <p>Цена</p>
            </div>
            <div class="col-md-2 d-none d-md-block">
              <p>Комиссия</p>
            </div>
            <div class="col-md-2 d-none d-md-block">
              <p>Действие</p>
            </div>
            <div class="col-md-2 d-none d-md-block">
              <p>Дата</p>
            </div>
          </div>
          <div v-if="portfolio_trade_history_list">
            <div v-for="(one_row,index) in portfolio_trade_history_list">
              <div class="dropdown-divider"></div>
              <portfolio-trade-history-one-row
              :one_row=one_row
              :index=index>
              </portfolio-trade-history-one-row>
            </div>
          </div>
        </b-collapse>
      </div>
    `
})

Vue.component('portfolio-trade-history-one-row', {
  props: ['one_row', 'index'],
  data: function () {
    return {
    }
  },
  methods: {
    removeItem: function () {
      let elem = this;
      let config = {
        method: 'delete',
        url: elem.one_row.url_for_delete
      };
      request_service(
        config,
        function_success = function (resp) {
          elem.$store.commit('removeItemFromTradeSecurityHistory', elem.index);
          elem.$store.dispatch('get_updated_portfolio', simple = false)
          elem.$bvToast.toast('Запись успешно удалена', {
            title: `Mybonds.space`,
            variant: 'success',
            solid: true
          })
        },
        function_catch = function (error) {
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
  computed: {
    computed_count: function () {
      return parseFloat(this.one_row.count)
        .toLocaleString('ru-RU',
          {
            maximumFractionDigits: 10
          });
    },
    computed_price: function () {
      return parseFloat(this.one_row.price)
        .toLocaleString('ru-RU', {
          style: 'currency',
          currency: this.one_row.security_faceunit
            .replace('РУБ', 'RUB')
            .replace('SUR', 'RUB'),
          maximumFractionDigits: 10
        });
    },
    computed_commission: function () {
      return parseFloat(this.one_row.commission)
        .toLocaleString('ru-RU', {
          style: 'currency',
          currency: this.one_row.security_faceunit
            .replace('РУБ', 'RUB')
            .replace('SUR', 'RUB'),
          maximumFractionDigits: 10
        });
    }
  },
  template: `
      <div>
        <div class="row align-items-center mt-2">
          <div class="col-md-2 col-12 mb-1 mt-1">
            <a class="btn btn-warning btn-sm" v-bind:href="one_row.security_url">{{ one_row.security_name }}</a>
          </div>
          <div class="col-md-2 col-12 mb-1 mt-1">
            <span class="d-md-none">Количество: </span><span>{{ computed_count }} шт.</span>
          </div>
          <div class="col-md-2 col-12 mb-1 mt-1">
            <span class="d-md-none">Цена: </span><span>{{ computed_price }}</span>
          </div>
          <div class="col-md-2 col-12 mb-1 mt-1">
            <span class="d-md-none">Комиссия: </span><span>{{ computed_commission }}</span>
          </div>
          <div class="col-md-2 col-12 mb-1 mt-1">
            <span class="d-md-none">Действие: </span><span>{{ one_row.buy ? 'Покупка' : 'Продажа' }}</span>
          </div>
          <div class="col-md-2 col-12 mb-1 mt-1">
            <span class="d-md-none">Дата: </span><span>{{ one_row.date }}</span>
          </div>
        </div>
        <b-button
        size="sm"
        variant="danger"
        class="mb-1 mt1"
        @click="removeItem">Удалить запись</b-button>
      </div>
    `
})

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
Vue.component('private', {
  data: function () {
    return {
      selected: null,
      options: [
        { value: 'da', text: 'Всем запрещено' },
        { value: 'af', text: 'Разрешено друзьям' },
        { value: 'al', text: 'Разрешено авторизованным' },
        { value: 'aa', text: 'Разрешено всем' }
      ]
    }
  },
  beforeMount: function () {
    this.selected = this.$store.state.private
  },
  computed: {
  },
  methods: {
    applyPrivate: function () {
      let elem = this;
      let formData = new FormData();
      formData.append('private', elem.selected);
      let config = {
        method: 'post',
        url: '/portfolios/' + elem.$store.state.portfolio_id + '/private/',
        data: formData
      };
      request_service(config,
        function_success = function (resp) {
          if (resp.status == 200) {
            elem.$bvToast.toast('Настройки применены.', {
              title: `Mybonds.space`,
              variant: 'success',
              solid: true
            })
          }
          elem.$store.commit('setPrivate', elem.selected);
        },
        function_catch = function (error) {
          elem.$bvToast.toast('Настройки отклонены.', {
            title: `Mybonds.space`,
            variant: 'danger',
            solid: true
          })
        }
      );
    }
  },
  template: `
    <div class="">
    <span class="">Приватность:</span>
      <div class="mt-1 d-flex flex-row">
        <b-form-select
        v-model="selected"
        :options="options"
        size="sm"
        class="col-7"></b-form-select>
        <div class="col-1">
        </div>
        <b-button
        size="sm"
        pill
        variant="primary"
        class="mb-1 mt1"
        @click="applyPrivate">Применить
        </b-button>
      </div>
    </div>
    `
})