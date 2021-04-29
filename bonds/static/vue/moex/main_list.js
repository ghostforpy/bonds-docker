var app = new Vue({
  el: '#app',
  data: function () {
    return {
      search: '',
      next_url: 'first',
      clear_url: 'securities/?search=',
      securities: [],
      new_securities: [],
      upload_busy: false,
      upload_new_busy: false,
      search_taped: false,
      errors_visible: false,
      errors: null,
      spiner_visible: true
    }
  },
  beforeMount: async function () {
    this.search = document.location.search.split('=')[1];
    //console.log(this.search)
    if (this.search === undefined) { this.search = '' };
    this.change_url();
  },
  mounted: function () {
    let url = this.clear_url + this.search;
    if (this.search != '') { this.search_taped = true };
    this.upload_securities(url);
    if (this.search != '') { this.upload_new_securities(this.search) };
  },
  methods: {
    change_url: function () {
      const state = { 'page_id': 1, 'user_id': 1 }
      const url = '?search=' + this.search;
      history.pushState(state, title = '', url)
    },
    upload_securities: function (url) {
      this.upload_busy = true;
      this.spiner_visible = true;
      var elem = this;
      let config = {
        method: 'get',
        url: url
      };
      request_service(
        config,
        function_success = function (resp) {
          elem.upload_busy = false;
          if (!elem.upload_new_busy) { elem.spiner_visible = false };
          elem.next_url = resp.data.next;
          results = resp.data.results;
          if (results.length > 0) {
            elem.securities.push(...results);
          }
          //console.log(resp.data)
        },
        function_catch = function () {
          elem.upload_busy = false;
          if (!elem.upload_new_busy) { elem.spiner_visible = false };
          elem.errors_visible = true;
        },
        function_error_response_500 = () => elem.errors = ['Server error'],
        function_error_response_404 = (error) => elem.errors = error.response.data,
        function_error_response_other = (error) => elem.errors = error.response.data
      );
    },
    upload_new_securities: function (query) {
      var elem = this;
      elem.spiner_visible = true;
      elem.upload_new_busy = true;
      let config = {
        method: 'get',
        url: 'securities/search-new/?search=' + query
      };
      request_service(
        config,
        function_success = function (resp) {
          elem.upload_new_busy = false;
          if (!elem.upload_busy) { elem.spiner_visible = false };
          results = resp.data.results;
          //if (results.length > 0) {
          elem.new_securities.push(...resp.data);
          //}
          //console.log(resp.data)
        },
        function_catch = function () {
          elem.upload_new_busy = false;
          if (!elem.upload_busy) { elem.spiner_visible = false };
        },
        function_error_response_500 = () => elem.errors = ['Server error'],
        function_error_response_404 = (error) => elem.errors = error.response.data,
        function_error_response_other = (error) => elem.errors = error.response.data
      );
    },
    handleUpdateSearhForm: function () {
      if (this.search == '' && this.search_taped == true) {
        this.securities = [];
        this.new_securities = [];
        this.search_taped = false;
        this.upload_securities(this.clear_url);
        this.change_url();
      }
    },
    handleSearch: function () {
      //нажатие кнопки "Поиск"
      this.securities = [];
      this.new_securities = [];
      this.search_taped = true;
      this.upload_securities(this.clear_url + this.search);
      this.upload_new_securities(this.search);
      this.change_url();
    },
    handleUploadSecurities: function () {
      if (this.next_url != null) {
        this.upload_securities(this.next_url)
      }
    }
  },
  computed: {
  },
  template: `
    <div id="app">
      <b-input-group class="mt-3">
        <b-form-input v-model="search" placeholder="Введите наименование, ISIN, SECID..."
        type="search"
        @keyup.enter="handleSearch"
        @update="handleUpdateSearhForm"></b-form-input>
        <b-input-group-append>
          <b-button variant="outline-secondary"
          @click="handleSearch">Поиск</b-button>
        </b-input-group-append>
      </b-input-group>
      
      <div v-if="securities.length > 0" class="row mt-3">
          <security-one-card
          v-for="item in securities"
          :key="item.pk"
          :security=item>
          </security-one-card>
          <div v-if="next_url != null" class="col-12 mb-3">
            <div class="card h-100 w-100">
              <b-button variant="outline-secondary"
              @click="handleUploadSecurities">Ещё</b-button>
            </div>
          </div>
      </div>
      <div v-else class="row mt-3">
        <h3 v-if="!spiner_visible" class="col-12">По вашему запросу в нашей базе ничего не найдено.</h3>
      </div>
      <div v-if="new_securities.length > 0" class="row mt-3">
          <h4 class="col-12 mb-3">Ценные бумаги из сторонних источников:</h4>
          <security-one-card
          v-for="item in new_securities"
          :key="item.isin"
          :security=item>
          </security-one-card>
      </div>
      <errors class="mt-3" v-if="errors_visible" v-bind:errors="errors"></errors>
      <div v-if="spiner_visible" class="d-flex justify-content-center mt-3">
          <b-spinner label="Loading..."></b-spinner>
      </div>
    </div>
    `
});
Vue.component('security-one-card', {
  props: ['security'],
  data: function () {
    return {
      new_security: false
    }
  },
  beforeMount: function () {

  },
  computed: {
    last_update: function () {
      return this.security.last_update
    },
    name: function () {
      let type = this.security.security_type
        .replace('share', 'Акция')
        .replace('bond', 'Облигация')
        .replace('pif_rshb', 'ОПИФ РСХБ')
        .replace(/^ppif$/, 'БПИФ')
        .replace('futures', 'Фьючерс')
        .replace('index', 'Индекс')
        .replace('etf_ppif', 'ETF')
        .replace('currency', 'Валюта')
        .replace('depositary_receipt', 'Депозитарная расписка')
      return `${type} "${this.security.name}"`
    },
    price: function () {
      var elem = this;
      try {
        return parseFloat(this.security.today_price)
          .toLocaleString('ru-RU', {
            style: 'currency',
            currency: this.security.main_board_faceunit.replace('SUR', 'RUB'),
            maximumFractionDigits: 2
          });
      } catch (err) {
        elem.new_security = true;
        return 'New!'
      }

    },
    computed_change_price_percent: function () {
      return parseFloat(this.security.change_price_percent / 100)
        .toLocaleString('ru-RU', { style: 'percent', maximumFractionDigits: 2 });
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
  methods: {
    click: function () {
      document.location.href = this.security.url;
    }
  },
  template: `
    <div class="col-12 col-lg-4 mb-3">
      <div class="card h-100 w-100 border_list_security"
      style="cursor: pointer"
      @click="click">
        <div v-if="security.secid != null" class="card-header header_list_security">
          {{security.secid}}
        </div>
        <div class="card-body ">
        <div class="h-100 d-flex flex-column justify-content-between">
          <div class="">
            <h5 class="card-title">{{name}}</h5>
            <span v-if="security.emitent != ''" class="card-text">Эмитент: {{security.emitent}}</span>
            <p></p>
          </div>
          <div class="d-flex flex-row-reverse">
            <div class="card-text" v-bind:class="{ 'text-primary': new_security }">{{price}} <span v-if="security.change_price_percent != 0 && !new_security"
            v-bind:class="computed_class_change_percent_profit"
            >({{computed_change_price_percent}})</span></div>
          </div>
          
        </div>
          
        </div>
        <div class="card-footer">
          <small v-if="!new_security" class="text-muted">Обновлено: {{last_update}}</small>
        </div>
      </div>
    </div>
    `
});
