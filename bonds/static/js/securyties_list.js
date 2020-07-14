
$(document).on('click', '.refresh_security', function(e){
    e.preventDefault();
    var id = '#'+$(this).attr('href').split('/')[3]
    var id_last_update = id + '_last_update' 
    $.post(
        $(this).attr('href'),
        function(data){
            if (data['status'] == 'ok'){
                $.toast({
                    title: 'Bonds',
                    content: 'Информация обновлена.',
                    type: 'success',
                    delay: 5000
                    });
                $(id).text(data['price']);
                $(id_last_update).text(data['last_update']);
            };
            if (data['status'] == 'no_id_security'){
                $.toast({
                    title: 'Bonds',
                    content: 'Такой бумаги нет.',
                    type: 'error',
                    delay: 5000
                    });

            };
            if (data['status'] == 'no data'){
                $.toast({
                    title: 'Bonds',
                    content: 'Обновить данные не удалось.',
                    type: 'error',
                    delay: 5000
                    });
            }
            if (data['status'] == 'already update'){
                $.toast({
                    title: 'Bonds',
                    content: 'Данные были уже обновлены.',
                    type: 'information',
                    delay: 5000
                    });
            }
            
        }
        );
});