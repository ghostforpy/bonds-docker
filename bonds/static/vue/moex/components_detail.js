Vue.component('follow', {
  data: function () {
    return {
    }
  },
  beforeMount: function () {
  },
  computed: {
    text: function () {
      let st = this.$store.state.is_followed;
      return st ? 'Отписаться' : 'Подписаться'
    },
    variant: function () {
      let st = this.$store.state.is_followed;
      return st ? 'danger' : 'primary'
    }
  },
  methods: {
    toogleFollow: function () {
      let elem = this;
      let config = {
        method: 'post',
        url: this.$store.state.follow_url
      };
      request_service(config,
        function_success = function (resp) {
          elem.$store.dispatch('toogleFollow');
          if (resp.status == 200) {
            elem.$bvToast.toast('Подписка оформлена', {
              title: `Mybonds.space`,
              variant: 'success',
              solid: true
            })
          } else if (resp.status == 204) {
            elem.$bvToast.toast('Подписка удалена', {
              title: `Mybonds.space`,
              variant: 'danger',
              solid: true
            })
          }
        }
      );
    }
  },
  template: `
      <b-button
      size="sm"
      pill
      :variant="variant"
      class="mb-1 mt1"
      @click="toogleFollow">{{text}}
      </b-button>
      `
})

Vue.component('security-info', {
  data: function () {
    return {
      security: null,
      facevalue: null,
      issuesize: null,
      initialfacevalue: null,
      couponpercent: null,
      couponvalue: null,
      accint: null
    }
  },
  beforeMount: function () {
    this.security = this.$store.state.security_info;
    this.facevalue = parseFloat(this.security.facevalue);
    this.issuesize = parseFloat(this.security.issuesize);
    this.initialfacevalue = parseFloat(this.security.initialfacevalue);
    this.couponpercent = parseFloat(this.security.couponpercent);
    this.couponvalue = parseFloat(this.security.couponvalue);
    this.accint = parseFloat(this.security.accint);
  },
  methods: {
    return_local_with_currency: function (elem) {
      return elem.toLocaleString('ru-RU', {
        style: 'currency',
        currency: this.security.main_board_faceunit,
        maximumFractionDigits: 10
      });
    }
  },
  computed: {
    computed_facevalue: function () {
      return this.return_local_with_currency(this.facevalue);
    },
    computed_initialfacevalue: function () {
      return this.return_local_with_currency(this.initialfacevalue);
    },
    computed_couponvalue: function () {
      return this.return_local_with_currency(this.couponvalue);
    },
    computed_accint: function () {
      return this.return_local_with_currency(this.accint);
    },
    computed_issuesize: function () {
      return this.issuesize.toLocaleString('ru-RU', {
        maximumFractionDigits: 10
      });
    },
    computed_couponpercent: function () {
      return parseFloat(this.security.couponpercent / 100)
        .toLocaleString('ru-RU', { style: 'percent', maximumFractionDigits: 10 });
    },
    computed_security_type: function () {
      return this.security.security_type
        .replace('share', 'Акция')
        .replace('bond', 'Облигация')
        .replace('pif_rshb', 'ОПИФ РСХБ')
        .replace('ppif', 'БПИФ')
        .replace('futures', 'Фьючерс')
        .replace('index', 'Индекс')
        .replace('etf_ppif', 'ETF')
        .replace('currency', 'Валюта')
    },
    computed_today_price: function () {
      return parseFloat(this.security.today_price)
        .toLocaleString('ru-RU', {
          style: 'currency',
          currency: this.security.main_board_faceunit,
          maximumFractionDigits: 10
        });
    },
    computed_change_price_percent: function () {
      return parseFloat(this.security.change_price_percent / 100)
        .toLocaleString('ru-RU', { style: 'percent', maximumFractionDigits: 10 });
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
  template: `
      <div>
        <a v-if="security.url" :href="security.url">Перейти на сайт</a>
        <div v-if="security.security_type != 'currency'">
          <p v-if="security.fullname">Полное наименование: {{ security.fullname }}</p>
          <p v-if="security.code">Код: {{ security.code }}</p>
          <p v-if="security.regnumber">Рег.номер: {{ security.regnumber }}</p>
          <p v-if="security.secid">SECID: {{ security.secid }}</p>
          <p v-if="security.isin">ISIN: {{ security.isin }}</p>
        </div>
        <p v-if="facevalue">Номинальная стоимость: {{ computed_facevalue }}</p>
        <p v-if="issuesize">Объём выпуска: {{ computed_issuesize }}</p>
        <p v-if="security.main_board_faceunit && security.security_type != 'currency'"
        >Валюта номинала: {{ security.main_board_faceunit }}</p>
        <p v-if="initialfacevalue"
        >Первоначальная номинальная стоимость: {{ computed_initialfacevalue }}</p>
        <p v-if="security.matdate">Дата погашения: {{ security.matdate }}</p>
        <p v-if="security.coupondate">Дата выплаты купона: {{ security.coupondate }}</p>
        <p v-if="security.couponfrequency">Периодичность выплаты купона в год: {{ security.couponfrequency }}</p>
        <p v-if="couponpercent">Ставка купона: {{ computed_couponpercent }}</p>
        <p v-if="couponvalue">Сумма купона, в валюте номинала: {{ computed_couponvalue }}</p>
        <p v-if="accint">НКД: {{ computed_accint }}</p>
        <p v-if="security.emitent">Эмитент: {{ security.emitent }}</p>
        <p>Тип: {{ computed_security_type }}</p>
        <p>Цена: {{ computed_today_price}} <span v-bind:class="computed_class_change_percent_profit"
        >({{computed_change_price_percent}})</span></p>
        <p>Дата обновления: {{ security.last_update }}</p>
        <p v-if="security.description">Описание: {{ security.description }}</p>
      </div>
    `
})