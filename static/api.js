var api = (function() {
    var makeCall = function(endpoint, data, callback) {
        $.ajax({
            url: "/api" + endpoint,
            data: data,
            dataType: "json",
            method: "POST",
            success: function(data) {
                console.log(data);
                callback(data);
                console.log("API call complete");
            },
            failure: function(data) {
                console.error("API call failed");
            }
        });
    };

    return {
        makeCall: makeCall
    };
})();
