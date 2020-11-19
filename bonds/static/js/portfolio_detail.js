function updated_portfolio(data) {
    $('#invest_cash').text(data['invest_cash']);
    $('#id_today_cash').val(data['today_cash']);
    $('#ostatok').text(data['ostatok']);
    $('#percent_profit').text(data['percent_profit']);
    $('#year_percent_profit').text(data['year_percent_profit']);
};

$('#id_cash').keyup(function () {
    action = $('#id_action').val();
    if (action == 'tp') {
        var ndfl = $(this).val() * 0.13;
        $('#id_ndfl').val(ndfl);
    };
});

$('#id_action').change(function (e) {
    if ($(this).val() == 'tp') {
        $('#id_ndfl').slideDown("fast", "linear");
        $('#id_security').slideDown("fast", "linear");
    } else {
        $('#id_ndfl').slideUp("fast", "linear");
        $('#id_security').slideUp("fast", "linear");
    };

});

$(document).on('click', '#add_invest', function (e) {
    e.preventDefault();
    date = $('#id_date').val();
    cash = $('#id_cash').val();
    ndfl = $('#id_ndfl').val();
    security = $('#id_security').val();
    if (ndfl == '') { ndfl = 0 };
    action = $('#id_action').val();
    if (action == 'tp') {
        action = 'Доход';
    } else if (action == 'vp') {
        action = 'Пополнение';
    } else if (action == 'bc') {
        action = 'Комиссия брокера';
    } else if (action == 'br') {
        action = 'Частичное погашении облигаций';
    } else {
        action = 'Снятие';
    };
    $.post(
        $(this).attr('href'),
        {
            cash: $('#id_cash').val(),
            ndfl: ndfl,
            date: $('#id_date').val(),
            action: $('#id_action').val(),
            security: security
        },
        function (data) {
            if (data['status'] == 'ok') {
                id = data['id'];
                var out = '<div class="row align-items-center">';
                out += '<div class="col-9"><div class="row"><div class="col-md-4">';
                out += date + '</div><div class="col-md-4">' + cash;
                if (action == 'Доход') {
                    out += '</br>(НДФЛ: ' + ndfl + ')';
                };
                out += '</div><div class="col-md-4">';
                out += action;
                if (action == 'Доход') {
                    if ($('#id_security option:selected').val() != '') {
                        out += '</br>' + $('#id_security option:selected').text();
                    };
                };
                out += '</div></div></div><div class="col-3">';
                out += '<a class="delete-invest btn btn-danger btn-sm"';
                out += ' href="/portfolio/del_invest/' + id + '/">Удалить</a>';
                out += '</div></div><div class="dropdown-divider"></div>';
                $('.history-table > .row:first').before(out);
                updated_portfolio(data);
                $.toast({
                    title: 'Bonds',
                    content: 'Портфель успешно обновлён.',
                    type: 'success',
                    delay: 5000
                });
            }
            if (data['status'] == 'no money on vklad') {
                $.toast({
                    title: 'Bonds',
                    content: 'Недостаточно денег в кошельке.',
                    type: 'error',
                    delay: 5000
                });
            }
            if (data['status'] == 'no money on portfolio') {
                $.toast({
                    title: 'Bonds',
                    content: 'Недостаточно денег в портфеле.',
                    type: 'error',
                    delay: 5000
                });
            }
            if (data['status'] == 'no_valid') {
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
$(document).on('click', '.del-history', function (e) {
    e.preventDefault();
    elem = $(this)
    $.post(
        $(this).attr('href'),
        function (data) {
            if (data['status'] == 'ok') {
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
            if (data['status'] == 'no money on portfolio') {
                $.toast({
                    title: 'Bonds',
                    content: 'Недостаточно денег в портфеле.',
                    type: 'error',
                    delay: 5000
                });
            };
            if (data['status'] == 'no money on vklad') {
                $.toast({
                    title: 'Bonds',
                    content: 'Недостаточно денег на вкладе.',
                    type: 'error',
                    delay: 5000
                });
            };
            if (data['status'] == 'wrong_action' || data['status'] == 'no_id') {
                $.toast({
                    title: 'Bonds',
                    content: 'Неверные данные.',
                    type: 'error',
                    delay: 5000
                });
            };
        }
    );
});
$(document).on('click', '.delete-invest', function (e) {
    e.preventDefault();
    elem = $(this).closest('.row')
    $.post(
        $(this).attr('href'),
        function (data) {
            if (data['status'] == 'ok') {
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
            if (data['status'] == 'no_money') {
                $.toast({
                    title: 'Bonds',
                    content: 'Недостаточно денег для снятия.',
                    type: 'error',
                    delay: 5000
                });
            };
            if (data['status'] == 'no money on portfolio') {
                $.toast({
                    title: 'Bonds',
                    content: 'Недостаточно денег в портфеле.',
                    type: 'error',
                    delay: 5000
                });
            };
            if (data['status'] == 'no money on vklad') {
                $.toast({
                    title: 'Bonds',
                    content: 'Недостаточно денег на вкладе.',
                    type: 'error',
                    delay: 5000
                });
            };
            if (data['status'] == 'wrong_action' || data['status'] == 'no_id') {
                $.toast({
                    title: 'Bonds',
                    content: 'Неверные данные.',
                    type: 'error',
                    delay: 5000
                });
            };
        }
    );
});
$(document).on('click', '.refresh-portfolio', function (e) {
    e.preventDefault();
    var manual = $('manual').val() == "True";
    console.log(manual)
    $.post(
        $(this).attr('href'),
        { today_cash: $('#id_today_cash').val(), private: $('#id_private').val() },
        function (data) {
            if (data['status'] == 'ok') {
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

$(function () {
    $('#id_date').daterangepicker({
        singleDatePicker: true,
        locale: {
            format: 'DD.MM.YYYY'
        }
    });
});