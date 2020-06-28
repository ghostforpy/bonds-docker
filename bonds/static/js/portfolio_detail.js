function updated_portfolio(data) {
        $('#invest_cash').text(data['invest_cash']);
        $('#id_today_cash').val(data['today_cash']);
        $('#ostatok').text(data['ostatok']);
        $('#percent_profit').text(data['percent_profit']);
        $('#year_percent_profit').text(data['year_percent_profit']);
        };
$(document).on('click', '#add_invest', function(e){
    e.preventDefault();
    date = $('#id_date').val();
    cash = $('#id_cash').val();

    action = $('#id_action').val();
    if (action == 'tp') {
        action = 'Доход';
    }else if (action == 'vp') {
        action = 'На портфель';
    }else{
        action = 'На вклад';
    };

    $.post(
        $(this).attr('href'),
        {cash: $('#id_cash').val(), date: $('#id_date').val(), action: $('#id_action').val()},
        function(data){
            if (data['status'] == 'ok'){
                id = data['id'];
                $('.history-table > .row:first').before(`<div class="row align-items-center"><div class="col-9"><div class="row"><div class="col-md-4">${date}</div><div class="col-md-4">${cash}</div><div class="col-md-4">${action}</div></div></div><div class="col-3"><a class="delete-invest btn btn-danger btn-sm" href="/portfolio/del_invest/${id}/">Удалить</a></div></div><div class="dropdown-divider"></div>`);
                updated_portfolio(data);
                $.toast({
                    title: 'Bonds',
                    content: 'Портфель успешно обновлён.',
                    type: 'success',
                    delay: 5000
                    }); 
            }
            if (data['status'] == 'no money on vklad'){
                $.toast({
                    title: 'Bonds',
                    content: 'Недостаточно денег в кошельке.',
                    type: 'error',
                    delay: 5000
                    });
            }
            if (data['status'] == 'no money on portfolio'){
                $.toast({
                    title: 'Bonds',
                    content: 'Недостаточно денег в портфеле.',
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
$(document).on('click','.del-history', function(e){
    e.preventDefault();
    elem = $(this)
    $.post(
        $(this).attr('href'),
        function(data){
            if (data['status'] == 'ok'){
                console.log(data);
                elem.prev('.row').remove()
                elem.next('.dropdown-divider:first').remove()
                elem.remove();
                updated_portfolio(data);
                $.toast({
                    title: 'Bonds',
                    content: 'Портфель успешно обновлён.',
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
$(document).on('click', '.delete-invest', function(e){
    e.preventDefault();
    elem = $(this).closest('.row')
    $.post(
        $(this).attr('href'),
        function(data){
            if (data['status'] == 'ok'){
                console.log(data);
                elem.next('.dropdown-divider:first').remove()
                elem.remove();
                updated_portfolio(data);
                $.toast({
                    title: 'Bonds',
                    content: 'Портфель успешно обновлён.',
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
$(document).on('click', '.refresh-portfolio', function(e){
   e.preventDefault();
   var manual = $('manual').val() == "True";
        console.log(manual)
    $.post(
        $(this).attr('href'),
        {today_cash: $('#id_today_cash').val(), private: $('#id_private').val()},
        function(data){
            if (data['status'] == 'ok'){
                updated_portfolio(data);
                $.toast({
                    title: 'Bonds',
                    content: 'Портфель успешно обновлён.',
                    type: 'success',
                    delay: 5000
                    });
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