// script for dynamic fields
let family_select = document.getElementById('pipelineFamily'); // the selector
let city_select = document.getElementById('pipeline'); //the dynamic field
family_select.onchange = function() {
    alert(family_select.value);
}
console.log("the script has been loaded");
