$(document).on('click', '#load', function(e){
    e.preventDefault();
    $.get(
        $(this).attr('href'),
        function(data){
            if (data['status'] == 'ok'){
                var hist = data['history'];
                var url = data['url'];
                var content_out = '';
                $.each(hist, function(date, price) {
                    content_out = content_out + '<div class="row align-items-center">'
                    content_out = content_out + '<div class="col-lg-4 .offset-lg-1 col-12 mb-1 mt-1"><span class="d-md-none">Дата: </span><span>'+ date +'</span></div>'
                    content_out = content_out + '<div class="col-lg-4 col-12 mb-1 mt-1"><span class="d-md-none">Цена: </span><span>'+ price +' руб.</span></div>'
                    content_out = content_out + '<div class="col-lg-2 col-4 mb-1 mt-1"><a class="btn btn-success btn-sm" href="'+ url + '?buy=true&date=' + date + '&price=' + price + '">Купить</a></div>'
                    content_out = content_out + '</div><div class="dropdown-divider"></div>'
                });
                $('#spinnerHistory').empty()
                $('#preHistory').after(content_out);
            }
            
        }
    );
});

$( document ).ready(function() {
    $('#load').click();
});

$(function(){
$('#id_date').daterangepicker({
    singleDatePicker: true,
        locale: {
            format: 'DD.MM.YYYY'
                                }
                            });
        });