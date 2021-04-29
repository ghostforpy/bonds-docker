var app = new Vue({
  el: '#app',
  store: store,
  data: function () {
    return {
      security: null,
      security_isin: null,
      security_visible: false,
      errors_visible: false,
      errors: null,
      spiner_visible: true
    }
  },
  beforeMount: async function () {
    this.security_isin = document.location.pathname.split('/')[3];
    var elem = this;
    var config = {
      method: 'get',
      url: 'securities/' + elem.security_isin + '/get-new/'
    };
    request_service(
      config,
      function_success = function (resp) {
        elem.security = resp.data;
        //console.log(resp.data);
        elem.$store.dispatch('set_security_info', elem.security);
        elem.security_currency = elem.security.main_board_faceunit.replace('SUR', 'RUB');
        elem.security_visible = true;
        elem.spiner_visible = false;
      },
      function_catch = function (error) {
        elem.errors = error;
        elem.errors_visible = true;
        elem.spiner_visible = false;
      },
      function_error_response_404 = function (error) {
        elem.errors = ['Не найдено'];
        elem.errors_visible = true;
        elem.spiner_visible = false;
      }
    );
  },
  methods: {
  },
  computed: {
  },
  template: `
    <div id="app">
      <div v-if="security_visible">
        <div class="d-flex justify-content-between align-items-center">
          <h3 class="align-self-center">{{security.name}}</h3>
        </div>
        <form-trade-securities></form-trade-securities>
        <div class="row">
          <div class="col-md-4">
            <security-info 
            :security=security>
            </security-info>
          </div>
          <div class="col-md-8">
            <security-history
            :isin=security_isin
            :currency=security_currency>
            </security-history>
          </div>
        </div>
      </div>
      <errors class="mt-3" v-if="errors_visible" v-bind:errors="errors"></errors>
      <div v-if="spiner_visible" class="d-flex justify-content-center mt-3">
          <b-spinner label="Loading..."></b-spinner>
      </div>
    </div>
    `
})
