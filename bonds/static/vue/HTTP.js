let url = document.location.protocol + '//' + document.location.host
const HTTP = axios.create({
    //baseURL: 'http://0.0.0.0:8000/api/',
    baseURL: url + '/api/',
    headers: {
        'X-CSRFToken': csrftoken,
    }
})