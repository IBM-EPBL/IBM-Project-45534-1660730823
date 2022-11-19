document.addEventListener('DOMContentLoaded', () => {
    let auth_token;
    $(document).ready(function () {
        $.ajax({
            type: 'get',
            url: 'https://www.universal-tutorial.com/api/getaccesstoken',
            success: function (data) {
                auth_token = data.auth_token
                getCountry(data.auth_token);
            },
            error: function (error) {
                console.log(error);
            },
            headers: {
                "Accept": "application/json",
                "api-token": "d6OnmrD9Lydl9-d2C14o0cDnqv2M4SO5qhJu1zklHwxUde9A4m85xnuV5nd3QksvEew",
                "user-email": "2k19cse001@kiot.ac.in"
            }

        })
        $('#countries').change(function () {
            getState();
        })
    })
    function getCountry(auth_token) {
        $.ajax({
            type: 'get',
            url: 'https://www.universal-tutorial.com/api/countries/',
            success: function (data) {
                data.forEach(element => {
                    $('#countries').append('<option value="' + element.country_name + '">' + element.country_name + '</option>');
                });
                //getState(auth_token)
            },
            error: function (error) {
                console.log(error);
            },
            headers: {
                "Authorization": "Bearer " + auth_token,
                "Accept": "application/json"
            }

        })
    }
    function getState() {
        let country_name = $('#countries').val();
        $.ajax({
            type: 'get',
            url: 'https://www.universal-tutorial.com/api/states/' + country_name,
            success: function (data) {
                $('#states').empty();
                data.forEach(element => {
                    $('#states').append('<option value="' + element.state_name + '">' + element.state_name + '</option>');
                });
                //getCity(auth_token);
            },
            error: function (error) {
                console.log(error);
            },
            headers: {
                "Authorization": "Bearer " + auth_token,
                "Accept": "application/json"
            }

        })
    }

});