$(document).on('click', '#follow', function (e) {
    e.preventDefault();
    let elem = $(this);
    $.post(
        $(this).attr('href'),
        {},
        function (data) {
            if (data['status'] == 'ok') {
                elem.toggleClass('btn-danger');
                elem.toggleClass('btn-primary');
                if (data['result'] == 'added') {
                    elem.text('Отписаться')
                } else {
                    elem.text('Подписаться')
                };
            };
        }
    );
});
