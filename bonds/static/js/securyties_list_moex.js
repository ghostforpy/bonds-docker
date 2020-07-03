$( document ).ready(function() {
  var moex_list = $('#moex_list').text();
  var query = $('#query').val();
  if (moex_list == 'False') {
    $.get(
      '/securities/search_moex/',
      {'query' : query},
      function(data){
        if (data['status'] == 'ok'){
          var content_out = '<button type="button" class="btn btn-secondary col-12 mb-2"'
          content_out += ' id="buttonMoexList" data-toggle="collapse" data-target="#collapseMoexList"'
          content_out += ' aria-expanded="false" aria-controls="collapseMoexList">Развернуть</button>'
          content_out += '<div class="collapse mt-2" id="collapseMoexList">';
          content_out += '<div class="row">';
          content_out += '<div class="col-md-3 d-none d-md-block">';
          content_out += '<p>Наименование</p>';
          content_out += '</div>';
          content_out += '<div class="col-md-3 d-none d-md-block">';
          content_out += '<p>Эмитент</p>';
          content_out += '</div>';
          content_out += '<div class="col-md-2 d-none d-md-block">';
          content_out += '<p>SECID</p>';
          content_out += '</div>';
          content_out += '<div class="col-md-2 d-none d-md-block">';
          content_out += '<p>ISIN</p>';
          content_out += '</div>';
          content_out += '<div class="col-md-2 d-none d-md-block">';
          content_out += '<p>Regnumber</p>';
          content_out += '</div>';
          content_out += '</div>';
          content_out += '<div class="dropdown-divider d-none d-md-block"></div>';
          var url = '/securities/buy-new/';
          var resp = data['response'];
          $.each(resp, function(index) {
            content_out += '<div class="row align-items-center">';
            content_out += '<div class="col-md-3 mb-2">';
            content_out += '<span class="d-md-none">Наименование:'
            content_out += ' </span><a class="btn btn-warning btn-sm" href="'
            content_out += url + index + '">' + resp[index]['shortname'] + '</a></div>';
            content_out += '<div class="col-md-3">' + '<span class="d-md-none">Эмитент: </span><span>';
            content_out += resp[index]['emitent'] + '</span></div>';
            content_out += '<div class="col-md-2"><span class="d-md-none">SECID: </span><span>';
            content_out += index + '</span></div>'
            content_out += '<div class="col-md-2"><span class="d-md-none">ISIN: </span><span>';
            content_out += resp['isin'] + '</span></div>';
            content_out += '<div class="col-md-2"><span class="d-md-none">Regnumber: </span><span>';
            content_out += resp['regnumber'] + '</span></div></div>';
            content_out += '<div class="dropdown-divider d-none d-md-block"></div>';
            });
          $('#spiner_moex').empty();
          $('#moex_h3').after(content_out);
        }else{
            $('#spiner_moex').empty();
            var content_out = '<h3 class="mt-3 mb-3">По вашему запросу в базе ';
            content_out += '<a href="http://moex.com">moex.com</a>';
            content_out += ' ничего не найдено.</h3>';
            $('#moex_h3').after(content_out);
            $('#moex_h3').empty();
        }
          
      }
    );
  };
});