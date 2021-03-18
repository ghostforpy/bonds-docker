Vue.use(Vuex)

const store = new Vuex.Store({
  state: {
    security_id: null,
    security_title: null,
    security_info: null,
    is_liked: null,
    is_followed: null,
    follow_url: null,
    ever_trade_securities: null,
    //part securities in portfolio

    //other
    security_visible: false,
    spiner_visible: true,
    errors_visible: false,
    errors: null

  },
  mutations: {
    init_security(state, data) {
      console.log(data);
    },
    setFollow(state, followed) {
      state.is_followed = followed
    },
    set_security_visible(state, stat) {
      state.security_visible = stat
    },
    set_spiner_visible(state, stat) {
      state.spiner_visible = stat
    },
    set_errors_visible(state, stat) {
      state.errors_visible = stat
    },
    set_errors(state, errors) {
      state.errors = errors
    }
  },
  actions: {
    get_security(context, security_id) {
      let config = {
        method: 'get',
        url: 'securities/' + security_id
      };
      request_service(
        config,
        function_success = function (resp) {
          //console.log(resp.data);
          context.commit('set_spiner_visible', false);
          context.commit('set_security_visible', true);
          context.commit('init_security', resp.data);
        },
        function_catch = function () {
          context.commit('set_spiner_visible', false);
          context.commit('set_errors_visible', true);
        },
        function_error_response_500 = () => context.commit('set_errors', ['Server error']),
        function_error_response_404 = (error) => context.commit('set_errors', error.response.data),
        function_error_response_other = (error) => context.commit('set_errors', error.response.data)
      );
    },
    toogleFollow(context) {
      context.commit('setFollow', !context.state.is_followed);
    }
  }
})