$(function(){
      $('#id_count, #id_price, #id_comission').keyup(function(){
        var price = parseFloat($('#id_price').val());
        var count = parseFloat($('#id_count').val());
        var comission = parseFloat($('#id_comission').val());
        var ostatok = parseFloat({{portfolio.ostatok}});
        if (isNaN(price)) {
          price = 0;
        };
        if (isNaN(comission)) {
          comission = 0;
        };
        if (isNaN(count)) {
          count = 0;
        };
        res = price * count + comission
          $('#cost').text(res);
        var action = ($('#action').val() == 'Покупка');
        if (action && (res > ostatok)){
          $('#cost').addClass('text-danger');
          $('#sub').prop('disabled', true);
          $('#sm').prop('hidden', false);
        }else{
          $('#cost').removeClass('text-danger');
          $('#sub').prop('disabled', false);
          $('#sm').prop('hidden', true);
        };
      });
      $('')
    });
$(function(){
      $('#id_date').daterangepicker({
          singleDatePicker: true,
              locale: {
                  format: 'DD.MM.YYYY'
                                      }
                                  });
              });