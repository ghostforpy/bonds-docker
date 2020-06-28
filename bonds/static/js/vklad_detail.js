function updated_vklad(data){
            $('#invest_cash').text(data['invest_cash']);
            $('#today_cash').text(data['today_cash']);
            $('#ostatok').text(data['ostatok']);
            $('#percent_profit').text(data['percent_profit']);
            $('#year_percent_profit').text(data['year_percent_profit']);
        };
$(document).on('click', '#add_vklad', function(e){
    e.preventDefault();
    date = $('#id_date').val();
    cash = $('#id_cash').val();
    popolnenie = $('#id_popolnenie').prop('checked');
    if (popolnenie) {
        popolnenie = 'Пополнение';
    }else{
        popolnenie = 'Снятие';
    };
    $.post(
        $(this).attr('href'),
        {cash: $('#id_cash').val(), date: $('#id_date').val(), popolnenie: $('#id_popolnenie').prop('checked')},
        function(data){
            if (data['status'] == 'ok'){
                id = data['id'];
                $('.history-table > .row:first').before(`<div class="row align-items-center"><div class="col-9"><div class="row"><div class="col-md-4">${date}</div><div class="col-md-4">${cash}</div><div class="col-md-4">${popolnenie}</div></div></div><div class="col-3"><a class="delete-vklad btn btn-danger btn-sm" href="/vklad/del_vklad/${id}/">Удалить</a></div></div><div class="dropdown-divider"></div>`);
                updated_vklad(data);
                $.toast({
                    title: 'Bonds',
                    content: 'Кошелек успешно обновлён.',
                    type: 'success',
                    delay: 5000
                    }); 
            }
            if (data['status'] == 'no_money'){
                $.toast({
                    title: 'Bonds',
                    content: 'Недостаточно денег для снятия.',
                    type: 'error',
                    delay: 5000
                    });
            }
            if (data['status'] == 'no_valid'){
                $.toast({
                    title: 'Bonds',
                    content: 'Введённые данные неверны.',
                    type: 'warning',
                    delay: 5000
                    });
            }

        }
    );
});

$(document).on('click', '.delete-vklad', function(e){
    e.preventDefault();
    elem = $(this).closest('.row')
    $.post(
        $(this).attr('href'),
        function(data){
            if (data['status'] == 'ok'){
                elem.next('.dropdown-divider:first').remove()
                elem.remove();
                updated_vklad(data);
                $.toast({
                    title: 'Bonds',
                    content: 'Кошелек успешно обновлён.',
                    type: 'success',
                    delay: 5000
                    });

            };
            if (data['status'] == 'no_money'){
                $.toast({
                    title: 'Bonds',
                    content: 'Недостаточно денег для снятия.',
                    type: 'error',
                    delay: 5000
                    });
            }
        }
        );
});
$(document).on('click', '.refresh-vklad', function(e){
   e.preventDefault();
    $.get(
        $(this).attr('href'),
        function(data){
            if (data['status'] == 'ok'){
                updated_vklad(data);
            };
        }
    );
});
$(function(){
$('#id_date').daterangepicker({
    singleDatePicker: true,
        locale: {
            format: 'DD.MM.YYYY'
                                }
                            });
        });