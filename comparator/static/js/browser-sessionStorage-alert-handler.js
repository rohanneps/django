$(document).ready(function() {
    if (!sessionStorage["alert_count"]){
        sessionStorage.setItem("alert_count", 0);
    }

    window.onpageshow = function(event) {
        if (event.persisted) {
            window.location.reload();
        }
    };

    var type = '';
    var process_id = '';
    var server_addr = '';

    if (window.location.href.split('/').length == 7){
        type = window.location.href.split('/')[5];
        process_id = window.location.href.split('/')[4];
        server_addr = window.location.href.split('/', 4).join('/');

        sessionStorage.setItem("type", type);
        sessionStorage.setItem("process_id", process_id);
        sessionStorage.setItem("server_addr", server_addr);
    }else{
        process_id = sessionStorage.getItem("process_id");
        server_addr = sessionStorage.getItem("server_addr");
    }

    function getStats() {
        $.ajax({
            url: server_addr + '/' + process_id + '/get-comparison-status',
            success: function (data) {
                console.log(data);
                if (data == 'Completed') {
                    location.reload();
                    window.alert('Completed!');
                    sessionStorage.setItem("alert_count", 1);
                } else {
                    setTimeout(function () {
                        getStats();
                    }, 5000);
                }
            }
        });
    }

    if (sessionStorage.getItem("alert_count") == 0){
        getStats();
    }
});