let url = document.location.protocol + '//' + document.location.host
const HTTP = axios.create({
    //baseURL: 'http://0.0.0.0:8000/api/',
    baseURL: url + '/api/',
    headers: {
        'X-CSRFToken': csrftoken,
    }
})

function request_service(
    config,
    function_success = () => { },
    function_catch = () => { },
    function_error_response = () => { },
    function_error_response_500 = () => { },
    function_error_response_404 = () => { },
    function_error_response_other = () => { },
    function_error_request = () => { },
    function_error = () => { }
) {
    HTTP.request(config)
        .then(function (resp) {
            function_success(resp);
            //console.log('SUCCESS!!');
            //console.log(resp);
            return resp;
        })
        .catch(function (error) {
            console.log('FAILURE!!');
            function_catch(error);
            if (error.response) {
                function_error_response(error);
                // The request was made and the server responded with a status code
                // that falls out of the range of 2xx
                //console.log(error.response.data);
                if (error.response.status === 500) {
                    function_error_response_500(error);
                } else if (error.response.status === 404) {
                    function_error_response_404(error);
                } else {
                    function_error_response_other(error);
                }
                //console.log(error.response.status);
                //console.log(error.response.headers);
            } else if (error.request) {
                function_error_request(error);
                // The request was made but no response was received
                // `error.request` is an instance of XMLHttpRequest in the browser and an instance of
                // http.ClientRequest in node.js
                //console.log(error.request);
            } else {
                function_error(error);
                // Something happened in setting up the request that triggered an Error
                //console.log('Error', error.message);
            }
            //console.log(error.config);
        });
}