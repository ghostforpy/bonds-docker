Vue.use(Vuex)

const store = new Vuex.Store({
  state: {
    portfolio_id: null,
    portfolio_title: null,
    portfolio_info: null,
    is_owner: false,
    portfolio_invests: null,
    trade_securities: null,
    ever_trade_securities: null,
    portfolio_visible: false,
    spiner_visible: true,
    errors_visible: false,
    errors: null

  },
  mutations: {
    init_portfolio(state, data) {
      state.portfolio_title = data.title;
      state.portfolio_id = data.id;
      state.portfolio_info = Object();
      state.portfolio_info.invest_cash = data.invest_cash;
      state.portfolio_info.today_cash = data.today_cash;
      state.portfolio_info.percent_profit = data.percent_profit;
      state.portfolio_info.change_percent_profit = data.change_percent_profit;
      state.portfolio_info.year_percent_profit = data.year_percent_profit;
      state.portfolio_info.change_year_percent_profit = data.change_year_percent_profit;
      state.portfolio_info.strategia = data.strategia;
      state.portfolio_info.is_owner = data.is_owner;
      state.is_owner = data.is_owner;
      if (data.is_owner) {
        state.portfolio_info.id = state.portfolio_id;
        state.portfolio_info.ostatok = data.ostatok;
        state.portfolio_info.created = new Date(data.created).toLocaleString('ru-RU');
        state.portfolio_invests = data.portfolio_invests;
        state.portfolio_info.ostatok_currency = data.securities.filter(
          item => item.security_type == 'currency');
        state.portfolio_info.manual = data.manual;
        state.trade_securities = data.trade_securities;
        let ever_trade_securities = data.trade_securities.map(
          function (item) {
            sec = new Object()
            sec.value = item.security_id;
            sec.text = item.security_name;
            return sec
          });
        state.ever_trade_securities = ever_trade_securities.filter(
          (item, index) => {
            return ever_trade_securities.indexOf(item) === index
          });
      } else {
        state.portfolio_info.owner_url = data.owner_url;
        state.portfolio_info.owner_name = data.owner_name;
      };
    },
    removeItemFromPortfolioInvests(state, id) {
      state.portfolio_invests = state.portfolio_invests.filter(
        function (item, ind) {
          return (ind !== id)
        });
    },
    addItemToPortfolioInvests(state, new_item) {
      state.portfolio_invests.unshift(new_item);
    },
    update_portfolio(state, data) {
      state.portfolio_info.change_percent_profit = data.change_percent_profit;
      state.portfolio_info.change_year_percent_profit = data.change_year_percent_profit;
      state.portfolio_info.invest_cash = data.invest_cash;
      state.portfolio_info.ostatok = data.ostatok;
      state.portfolio_info.percent_profit = data.percent_profit;
      state.portfolio_info.today_cash = data.today_cash;
      state.portfolio_info.year_percent_profit = data.year_percent_profit;
      state.portfolio_info.ostatok_currency = data.securities.filter(
        item => item.security_type == 'currency');
    },
    set_portfolio_visible(state, stat) {
      state.portfolio_visible = stat
    },
    set_spiner_visible(state, stat) {
      state.spiner_visible = stat
    },
    set_errors_visible(state, stat) {
      state.errors_visible = stat
    }
    ,
    set_errors(state, errors) {
      state.errors = errors
    }
  },
  actions: {
    get_portfolio(context, portfolio_id) {
      let config = {
        method: 'get',
        url: 'portfolios/' + portfolio_id
      };
      request_service(
        config,
        function_success = function (resp) {
          context.commit('set_spiner_visible', false);
          context.commit('set_portfolio_visible', true);
          context.commit('init_portfolio', resp.data);
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
    get_updated_portfolio(context) {
      let config = {
        method: 'get',
        url: 'portfolios/' + context.state.portfolio_id + '/get-updated-portfolio/'
      };
      request_service(
        config,
        function_success = function (resp) {
          context.commit('update_portfolio', resp.data);
        },
        function_catch = function () {
          console.log('FAILURE!!', error);
        }
      );
    }
  }
})