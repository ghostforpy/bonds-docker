$(document).on('click', '.friends', function(e){
        e.preventDefault();
        var elem = this
        $.post(
          $(this).attr('href'),
          function(data){
            if (data['status'] == 'request_saved'){
              $.toast({
                    title: 'Bonds',
                    content: 'Запрос в друзья направлен.',
                    type: 'success',
                    delay: 5000
                    });
              $(elem).attr('href', data['url']);
              $(elem).text('Отменить запрос в друзья');
              $(elem).removeClass('btn-success btn-danger btn-primary').addClass('btn-secondary');
            };
            if (data['status'] == 'already_friends'){
              $.toast({
                    title: 'Bonds',
                    content: 'Вы уже друзья.',
                    type: 'warning',
                    delay: 5000
                    });
            };
            if (data['status'] == 'friend_added'){
              $.toast({
                    title: 'Bonds',
                    content: 'Друг добавлен.',
                    type: 'success',
                    delay: 5000
                    });
              $(elem).siblings().remove();
              $(elem).attr('href', data['url']);
              $(elem).text('Удалить из друзей');
              $(elem).removeClass('btn-success btn-secondary btn-primary').addClass('btn-danger');
            };
            if (data['status'] == 'already_exist'){
              $.toast({
                    title: 'Bonds',
                    content: 'Этот пользователель уже направил запрос.',
                    type: 'info',
                    delay: 5000
                    });
              $(elem).attr('href', data['url_accept']);
              $(elem).text('Добавить в друзья');
              $(elem).removeClass('btn-danger btn-secondary btn-primary').addClass('btn-success');
              
              $(elem).after($(elem).clone().
                attr('href', data['url_reject']).
                text('Отклонить запрос в друзья').
                removeClass('btn-success btn-secondary btn-primary').addClass('btn-danger'));
            };
            if (data['status'] == 'request_reject'){
              $.toast({
                    title: 'Bonds',
                    content: 'Запрос в друзья отклонён.',
                    type: 'error',
                    delay: 5000
                    });
              $(elem).siblings().remove();
              $(elem).attr('href', data['url']);
              $(elem).text('Направить запрос в друзья');
              $(elem).removeClass('btn-success btn-secondary btn-danger').addClass('btn-primary');
            };
            if (data['status'] == 'friend_deleted'){
              $.toast({
                    title: 'Bonds',
                    content: 'Друг удалён.',
                    type: 'error',
                    delay: 5000
                    });
              $(elem).attr('href', data['url']);
              $(elem).text('Направить запрос в друзья');
              $(elem).removeClass('btn-success btn-secondary btn-danger').addClass('btn-primary');
            };
            if (data['status'] == 'no_user_in_friends'){
              $.toast({
                    title: 'Bonds',
                    content: 'Нет такого друга в друзьях.',
                    type: 'error',
                    delay: 5000
                    });
            };
            if (data['status'] == 'no_friend_id'){
              $.toast({
                    title: 'Bonds',
                    content: 'Нет такого друга.',
                    type: 'error',
                    delay: 5000
                    });
            };
            if (data['status'] == 'no_valid'){
              $.toast({
                    title: 'Bonds',
                    content: 'Данные не валидны.',
                    type: 'error',
                    delay: 5000
                    });
            };
            if (data['status'] == 'no_friend_request_id'){
              $.toast({
                    title: 'Bonds',
                    content: 'Такого запроса не существует.',
                    type: 'error',
                    delay: 5000
                    });
            };
            if (data['status'] == 'request_canceled'){
              $.toast({
                    title: 'Bonds',
                    content: 'Запрос отменён.',
                    type: 'info',
                    delay: 5000
                    });
              $(elem).siblings().remove();
              $(elem).attr('href', data['url']);
              $(elem).text('Направить запрос в друзья');
              $(elem).removeClass('btn-success btn-secondary btn-danger').addClass('btn-primary');
            };
            if (data['status'] == 'no_user_id'){
              $.toast({
                    title: 'Bonds',
                    content: 'Нет такого пользователя.',
                    type: 'info',
                    delay: 5000
                    });
            };
          }
          );
        });
