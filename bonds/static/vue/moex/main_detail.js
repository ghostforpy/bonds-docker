var app = new Vue({
  el: '#app',
  store: store,
  beforeMount: async function () {
    let security_id = document.location.pathname.split('/')[3];
    store.dispatch('get_security', security_id);
  },
  methods: {
    create: function () {
    }
  },
  computed: {
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
        
      </div>
      <errors class="mt-3" v-if="errors_visible" v-bind:errors="errors"></errors>
      <div v-if="spiner_visible" class="d-flex justify-content-center mt-3">
          <b-spinner label="Loading..."></b-spinner>
      </div>
    </div>
    `
})
