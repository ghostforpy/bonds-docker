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
    }
  },
  template: `
      <div>
        <p v-if="!portfolio_info.is_owner">Владелец: <a v-bind:href="portfolio_info.owner_url">{{portfolio_info.owner_name}}</a></p>
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
        v-if="portfolio_info.is_owner && portfolio_info.ostatok_currency.length"
        :ostatok_currency=portfolio_info.ostatok_currency>
        </portfolio-info-ostatok-currency>
        <p>Доходность: {{computed_percent_profit}} <span v-bind:class="class_change_percent_profit">({{computed_change_percent_profit}})</span></p>
        <p>Годовая доходность: {{computed_year_percent_profit}} <span v-bind:class="class_change_year_percent_profit">({{computed_change_year_percent_profit}})</span></p>
        <p v-if="portfolio_info.strategia !== '' && portfolio_info.strategia !== 'null'">Стратегия: <span>{{ portfolio_info.strategia }}</span></p>
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
      this.$store.dispatch('get_updated_portfolio');
    },
    addToList: function (new_item) {
      this.$store.commit('addItemToPortfolioInvests', new_item);
      this.$store.dispatch('get_updated_portfolio');
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

