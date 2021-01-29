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
function go_to_url(url) {
  document.location.href = url;
};
var app = new Vue({
  el: '#app',
  data: {
    main_visible: true,
    manual: false,
    title: null,
    strategia: null,
    description: null,
    file: null,
    spiner_visible: false,
    errors: null,
    errors_visible: false,
    selected: 'da',
    options: [
      { value: 'da', text: 'Всем запрещено' },
      { value: 'af', text: 'Разрешено друзьям' },
      { value: 'al', text: 'Разрешено авторизованным' },
      { value: 'aa', text: 'Разрешено всем' }
    ]
  },
  methods: {
    create: function () {
      let formData = new FormData();
      formData.append('title', this.title);
      formData.append('strategia', this.strategia);
      formData.append('private', this.selected);
      formData.append('description', this.description);
      formData.append('manual', this.manual);
      var url = 'portfolios/';
      if (!this.manual) {
        if (this.file) {
          if (prepare_file_before_post(this)) {
            formData.append('filename', this.file);
            var url = 'portfolios/create-by-breport/';
          }
        }
      };
      post_formData(this, formData, url);
    }
  },
  template: `
    <div id="app">
      <div v-if="main_visible">
        <div class="row mx-3 mt-3">
          <label class="col-12 col-md-12 px-0" for="id_title">Название портфеля:</label>
          <b-form-input
          id="id_title"
          v-model="title"
          class="col-12 col-md-4"
          size="sm"
          placeholder="Введите название портфеля..."
          ></b-form-input>
        </div>
        <div class="row mx-3 mt-3">
          <label class="col-12 col-md-12 px-0" for="id_private">Приватность:</label>
          <b-form-select
            size="sm"
            id="id_private"
            class="col-12 col-md-4"
            v-model="selected"
            :options="options"></b-form-select>
        </div>
        <div class="row mx-3 mt-3">
          <b-form-checkbox
            id="id_manual"
            v-model="manual">
            Ручной ввод балланса
          </b-form-checkbox>
        </div>
        <div class="row mx-3 mt-3">
          <label class="col-12 col-md-12 px-0" for="id_strategia">Стратегия:</label>
          <b-form-input
          id="id_strategia"
          class="col-12 col-md-4"
          v-model="strategia"
          size="sm"
          ></b-form-input>
        </div>
        <div class="row mx-3 mt-3">
          <label class="col-12 col-md-12 px-0" for="id_description">Описание:</label>
          <b-form-textarea
          id="id_description"
          v-model="description"
          class="col-12 col-md-4"
          size="sm"
          placeholder="Введите название портфеля..."
          ></b-form-textarea>
        </div>
        <div class="row mx-3 mt-3">
          <label class="col-12 col-md-12 px-0" for="id_file">Создать на основе брокерского отчета:</label>
          <b-form-file
          class="col-12 col-md-4"
          v-model="file"
          id="id_file"
          size="sm"
          :state="Boolean(file)"
          browseText="Обзор"
          placeholder="Выберите или перетащите файл..."
          drop-placeholder="Перетащите файл..."
          accept=".xls, .xlsx"
          :disabled="manual"
          ></b-form-file>
        </div>
        <b-button class="mt-3 ml-3" v-on:click="create">Создать</b-button>
      </div>
        
        <errors class="mt-3" v-if="errors_visible" v-bind:errors="errors"></errors>
        <div v-if="spiner_visible" class="d-flex justify-content-center mt-3">
            <b-spinner label="Loading..."></b-spinner>
        </div>
    </div>
    `
})
