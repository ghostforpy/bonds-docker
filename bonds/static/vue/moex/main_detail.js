var app = new Vue({
  el: '#app',
  store: store,
  beforeMount: async function () {
    let security_id = document.location.pathname.split('/')[3];
    store.dispatch('get_security', security_id);
    //store.dispatch('get_security_history', security_id);
  },
  methods: {
    create: function () {
    }
  },
  computed: {
    security_title: function () {
      return this.$store.state.security_title;
    },
    security_in_portfolios: function () {
      return this.$store.state.security_in_portfolios.length;
    },
    security_trades: function () {
      return this.$store.state.security_trades.length;
    },
    security_visible: function () {
      return this.$store.state.security_visible;
    },
    spiner_visible: function () {
      return this.$store.state.spiner_visible;
    },
    errors_visible: function () {
      return this.$store.state.errors_visible;
    },
    errors: function () {
      return this.$store.state.errors;
    }
  },
  template: `
    <div id="app">
      <div v-if="security_visible">
        <div class="d-flex justify-content-between align-items-center">
          <h3 class="align-self-center">{{security_title}}</h3>
          <follow></follow>
        </div>
        <form-trade-securities></form-trade-securities>
        <div class="row">
          <div class="col-md-4">
            <security-info></security-info>
          </div>
          <div class="col-md-8">
            <security-history></security-history>
            <security-in-portfolios v-if="security_in_portfolios"></security-in-portfolios>
            <security-trades v-if="security_trades"></security-trades>
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
