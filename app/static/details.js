$(document).ready(function() {

//disable next button on submit
$('#details_form').submit(function(){
    $('#next_button').prop('disabled', true);
});

});
