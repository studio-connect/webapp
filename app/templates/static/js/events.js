//Long Polling Call Events
function checkCallEvents()
{

    $.ajax({
        type: "GET",
    url: "/calls/events",
    timeout: 30000,
    dataType: "json"
    }).done(function(result) {

        if (result.INCOMING) {
            bootbox.confirm("Incoming call from '" + result.INCOMING  + "', accept?", 
                function(result) {
                    if (result) {
                        $.ajax({url: "/calls/accept"});
                    } else {
                        $.ajax({url: "/calls/dismiss"});
                    }
                    setTimeout("checkCallEvents()", 5000);
                }); 
        } else {
            checkCallEvents();
        }
    });
};

jQuery(document).ready(function () {
    setTimeout("checkCallEvents()", 2000);
});
