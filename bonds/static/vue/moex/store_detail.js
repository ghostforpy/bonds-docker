Vue.use(Vuex)

const store = new Vuex.Store({
  state: {
    security_id: null,
    security_title: null,
    security_info: null,
    is_liked: null,
    is_followed: null,
    follow_url: null,
    security_history: [],
    //modal trades
    trade_security_action: null,
    trade_portfolio_id: null,
    trade_date: null,
    trade_price: 0,
    //trades
    security_trades: null,
    //part securities in portfolio
    security_in_portfolios: null,
    portfolios: [],
    //other
    security_visible: false,
    spiner_visible: true,
    errors_visible: false,
    errors: null

  },
  mutations: {
    init_security(state, data) {
      console.log(data);

      state.security_title = data.shortname;
      state.security_id = data.id;
      state.follow_url = data.follow_url;
      state.security_info = {
        shortname: data.shortname,
        fullname: data.fullname,
        security_type: data.security_type,
        secid: data.secid,
        isin: data.isin,
        regnumber: data.regnumber,
        today_price: data.today_price,
        change_price_percent: data.change_price_percent,
        main_board_faceunit: data.main_board_faceunit.replace('РУБ', 'RUB').replace('SUR', 'RUB'),
        issuesize: data.issuesize,
        matdate: data.matdate,
        last_update: data.last_update,
        facevalue: data.facevalue,
        initialfacevalue: data.initialfacevalue,
        url: data.url,
        emitent: data.emitent,
        couponvalue: data.couponvalue,
        couponpercent: data.couponpercent,
        couponfrequency: data.couponfrequency,
        coupondate: data.coupondate,
        accint: data.accint
      };
      state.security_trades = data.trades;
      state.security_in_portfolios = data.portfolios;
      for (let t in data.all_portfolios) {
        state.portfolios.push({ value: t, text: data.all_portfolios[t] })
      }
    },
    set_security_history(state, history) {
      for (let t in history) {
        state.security_history.push(
          {
            price: parseFloat(history[t]),
            date: new Date(
              parseFloat(t.split('.')[2]),
              parseFloat(t.split('.')[1]) - 1,
              parseFloat(t.split('.')[0]))
          }
        )
      }
    },
    set_trade_security_action(state, trade_security_action) {
      state.trade_security_action = trade_security_action
    },
    set_trade_security_date(state, date) {
      state.trade_security_date = date
    },
    set_trade_security_price(state, price) {
      state.trade_security_price = price
    },
    set_trade_portfolio_id(state, trade_portfolio_id) {
      state.trade_portfolio_id = trade_portfolio_id
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
    get_security_history(context, security_id) {
      let config = {
        method: 'get',
        url: 'securities/' + security_id + '/history/'
      };
      request_service(
        config,
        function_success = function (resp) {
          //context.commit('set_spiner_visible', false);
          //context.commit('set_security_visible', true);
          context.commit('set_security_history', resp.data);
        },
        function_catch = function () {
          //context.commit('set_spiner_visible', false);
          //context.commit('set_errors_visible', true);
        }
      );
    },
    toogleFollow(context) {
      context.commit('setFollow', !context.state.is_followed);
    }
  }
})