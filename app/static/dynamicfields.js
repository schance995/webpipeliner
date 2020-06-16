// script for dynamic fields
let family_select = document.getElementById('pipelineFamily'); // the selector
let city_select = document.getElementById('pipeline'); //the dynamic field
family_select.onchange = function() {
    family = family_select.value;
    // alert(family);
    fetch('/dynamic/' + family).then(function(response) {
        response.json().then(function(data) {
            for (let p of data.pipelines) {
                console.log(p);
            }
            // console.log(JSON.stringify(data));
            // console.log(data);
            // if the table changes in the console then you know that you're getting the data
        })
    });
};
console.log("the script has been loaded");
