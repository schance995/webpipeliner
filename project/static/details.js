$(document).ready(function() {

//disable next button on submit
$('#details_form').submit(function(){
    $('#submit_button').prop('disabled', true);
});

});
