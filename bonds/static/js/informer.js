$(document).on('click', '#informer', function (e) {
    e.preventDefault();
    let elem = $(this);
    if ($(this).hasClass('btn-danger')) {
        data1 = { 'enable': 'false' }
    } else {
        data1 = { 'enable': 'true' }
    };
    $.ajax({
        type: "PUT",
        url: $(this).attr('href'),
        data: data1,
        success:
            function (data) {
                elem.toggleClass('btn-danger');
                elem.toggleClass('btn-success');
                console.log(data['enable']);
                if (data['enable'] == false) {
                    $("#informer_enable").text('ы');
                } else {
                    $("#informer_enable").text('');
                };
            }
    });
});
