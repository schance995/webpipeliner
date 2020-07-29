// stored in a meta tag
var data = JSON.parse($("#data").attr("data"));

var selected_family;

$(document).ready(function() {
var family_form_select = $("#pipelineFamily");
var pipeline_form_select = $("#pipeline");
var genome_form_select = $("#genome");
// on pipelineFamily change
family_form_select.change(function() {
    selected_family = $(this).children(":selected").text();
    // empty pipeline values except default option
    $('#pipeline option:gt(0)').remove();
    // also empty genome options
    $('#genome option:gt(0)').remove();
    // if not default option then add pipeline and genome options
    if (selected_family !== "Select a family") {
        var new_pipeline_options = data[selected_family].pipelines;
        $.each(new_pipeline_options, function(dummmy, actual) {
            pipeline_form_select.append($("<option></option>")
                                 .attr("value", actual).text(actual));
        });
        // dummy variable holds indices, actual is the string value
        // repeat for genomes
        var new_genome_options = data[selected_family].genomes; 
        $.each(new_genome_options, function(dummmy, actual) {
            genome_form_select.append($("<option></option>")
                                 .attr("value", actual).text(actual));
        });
    };
});

// let Flask validate the form
$('#next_button').click(function(){
        $.ajax({
                url: '/formsubmit',
                data: $('form[name="generalform"]').serialize(),
                type: 'POST',
                success: function(response){
                        console.log(response);
                },
                error: function(error){
                        console.log(error);
                }
        });
});


});
