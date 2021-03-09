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
  store: store,
  beforeMount: async function () {
    let portfolio_id = document.location.pathname.split('/')[3];
    store.dispatch('get_portfolio', portfolio_id);
  },
  methods: {
    create: function () {
    }
  },
  computed: {
    portfolio_title: function () {
      return this.$store.state.portfolio_title;
    },
    portfolio_info: function () {
      return this.$store.state.portfolio_info;
    },
    portfolio_visible: function () {
      return this.$store.state.portfolio_visible;
    },
    is_owner: function () {
      return this.$store.state.is_owner;
    },
    is_deny: function () {
      return this.$store.state.is_deny;
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
      <div v-if="portfolio_visible">
        <div class="d-flex justify-content-between">
          <h3 class="align-self-center">Портфель: {{portfolio_title}}</h3>
          <follow v-if="!is_owner"></follow>
        </div>
        <b-tabs content-class="mt-3">
          <b-tab title="Главная" active>
            <div class="row">
              <portfolio-info
                class="col-sm-4"
                :portfolio_info_object="portfolio_info">
              </portfolio-info>
              <div class="col-sm-8">
                <portfolio-invests
                  v-if="portfolio_info.is_owner"
                  >
                </portfolio-invests>
                <portfolio-securities
                v-if="!is_deny">
                </portfolio-securities>
                <portfolio-trade-history
                  v-if="portfolio_info.is_owner"
                  >
                </portfolio-trade-history>
              </div>
            </div>
            <form-trade-securities
            v-if="is_owner"></form-trade-securities>
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
