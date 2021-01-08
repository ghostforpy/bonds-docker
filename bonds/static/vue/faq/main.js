Vue.component('question-item', {
  props: ['question_item', 'index'],
  data: function () {
    return {
      index_number: null,
      rotate: 0
    }
  },
  beforeMount: function () {
    this.index_number = 'collapse-' + this.index.toString();
  },
  methods: {
    rotate_method: function () {
      if (this.rotate == 0) {
        this.rotate = 180
      } else {
        this.rotate = 0
      }
    },
  },
  template:
    `<div class="border border-secondary rounded-sm">
      <div
      class="d-flex align-items-center"
      v-b-toggle="index_number"
      v-on:click="rotate_method"
      >
        <b-icon
        class="m-2"
        icon="chevron-double-down"
        :rotate="rotate"
        ></b-icon><b class="m-2">{{question_item.question}}</b>
      </div>
      <b-collapse v-bind:id="index_number" class="m-2">
       <div v-html="question_item.answer"></div>
      </b-collapse>
    </div>`
})

var app = new Vue({
  el: '#app',
  data: {
    message: 'Как пользоваться сервисом mybonds.space',
    questions: [
      {
        question: 'Как создать портфель?', answer: `
        <span>Для создания портфеля необходимо залогиниться на сайте, <span class="d-md-none">нажать <span class="navbar-light"><span class="navbar-toggler"><span class="navbar-toggler-icon"></span></span></span> слева вверху экрана,
      выбрать "Мои портфели"</span><span class="d-none d-md-block">нажать <button type="button" class="btn btn-warning dropdown-toggle">
      User
    </button> справа вверху экрана, выбрать "Мои портфели"</span> и на появившейся странице нажать <a class="btn btn-dark" href="#">
      Создать портфель
      </a>.</span>
      ` },
      {
        question: 'Как добавить (купить) ценную бумагу в портфель?', answer: `
      <span>Для добавления ценной бумаги в портфель необходимо перейти в раздел "Рынок", с помощью строки поиска <div class="input-group w-auto d-inline-flex">
      <input type="text" class="form-control" placeholder="Название" aria-label="search" aria-describedby="basic-addon2">
      <div class="input-group-append">
        <button class="btn btn-outline-secondary" type="submit">Поиск</button>
      </div>
    </div> найти нужную
      позицию, открыть её детализацию. В разделе <button type="button" class="btn btn-secondary btn-sm">История цен</button> напротив нужной даты нажать 
      <button class="btn btn-success btn-sm">Купить</button>. На странице покупки ценной бумаги необходимо заполнить все поля, в том числе если значение равняется 0.
      Далее необходимо нажать кнопку <button class="btn btn-success btn-sm">Купить</button>. Если какое из полей будет заполнено некорректно, кнопка покупки будет неактивна <button class="btn btn-success btn-sm" disabled>Купить</button>.</span>
      ` },
      {
        question: 'Как продать ценную бумагу в портфеле?', answer: `
      <span>Для продажи ценной бумаги необходимо перейти на страницу портфеля, в разделе <button type="button" class="btn btn-secondary btn-sm">Состав портфеля</button>
    найти нужную позицию и нажать <button class="btn btn-danger btn-sm">Продать</button>. На странице продажи ценной бумаги необходимо заполнить все поля, в том числе если значение равняется 0.
      Далее необходимо нажать кнопку <button class="btn btn-danger btn-sm">Продать</button>. Если какое из полей будет заполнено некорректно, кнопка продажи будет неактивна <button class="btn btn-danger btn-sm" disabled>Продать</button>.</span>
      ` },
      {
        question: 'Какие форматы брокерских отчётов поддерживаются в разделе "Отчёты"?', answer: `
      <p>Формат файла - xlsx, размер файла - до 2.5 МБ. Для нормальной работы сервиса необходимо чтобы начало брокерского отчёта было с даты открытия счёта или ранее,
      входящие остатки по валютам и ценным бумагам должны равняться 0.</p>
      <p>На данный момент поддерживаются отчёты от брокера Тинькофф, для добавления других брокеров пишите на <a href="mailto:admin@mybonds.space">
      admin@mybonds.space</a> администратору сервиса.
      ` }
    ]
  },
  template: `
    <div id="app">
      <h4 class="mt-2 mb-3">{{ message }}</h4>
      <div v-for="(item, ind) in questions" class="mb-2">
        <question-item :question_item="item" :index="ind"></question-item>
      </div>
    </div>
    `
})

