Vue.use(Vuex)

const store = new Vuex.Store({
  state: {
    security_id: null,
    security_title: null,
    security_info: null,
    is_liked: null,
    is_followed: null,
    follow_url: null,
    //security_history: [],
    //next_url_security_history: 'first',
    //busy: true,
    //modal trades
    trade_security_action: null,
    trade_portfolio_id: null,
    trade_security_date: null,
    trade_price: 0,
    //trades
    //security_trades: null,
    //part securities in portfolio
    //security_in_portfolios: null,
    portfolios: [],
    //other
    //security_visible: false,
    //spiner_visible: true,
    //errors_visible: false,
    //errors: null

  },
  mutations: {
    set_security_info(state, security) {
      state.security_info = security;
      for (let t in security.all_portfolios) {
        state.portfolios.push({ value: t, text: security.all_portfolios[t] })
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
  },
  actions: {
    set_security_info(context, security) {
      context.commit('set_security_info', security)
    },
    set_trade_security_action(context, trade_security_action) {
      context.commit('set_trade_security_action', trade_security_action)
    },
    set_trade_security_date(context, trade_security_date) {
      context.commit('set_trade_security_date', trade_security_date)
    },
    set_trade_security_price(context, trade_security_price) {
      context.commit('set_trade_security_price', trade_security_price)
    },
    toogleFollow(context) {
      context.commit('setFollow', !context.state.is_followed);
    }
  }
})