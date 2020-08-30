// pipelines and families are stored in a meta tag

$(document).ready(function() {
var data = JSON.parse($("#data").attr("data"));
selected_family = $(this).children(":selected").text(); 

// on pipelineFamily change
function update() {
    selected_family = $('#family').children(":selected").text();
    // if default option not selected, empty pipeline values except default option
    $('#pipeline option:gt(0)').remove();
    // also empty genome options
    $('#genome option:gt(0)').remove();
    // if not default option then add pipeline and genome options
    if (selected_family !== "Select a family") {
        var new_pipeline_options = data[selected_family].pipelines;
        $.each(new_pipeline_options, function(dummmy, actual) {
            $('#pipeline').append($("<option></option>")
            .attr("value", actual).text(actual));
        });
        // dummy variable holds indices, actual is the string value
        // repeat for genomes
        var new_genome_options = data[selected_family].genomes; 
        $.each(new_genome_options, function(dummmy, actual) {
            $('#genome').append($("<option></option>")
            .attr("value", actual).text(actual));
        });
    };
};
update();
$('#family').change(update);
// disable submit button on form submit
$('#basics_form').submit(function(){
    $('#next_button').prop('disabled', true);
});

});
