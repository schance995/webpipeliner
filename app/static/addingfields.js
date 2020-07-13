$(document).ready(function() {
// if it doesn't exist, returns 0
if ($('#reportDiffExpGenes').length) { 

$('#reportDiffExpGenes').before('<div class="form-group  required"><label class="control-label" for="minCPM">Mincpm</label><input class="form-control" id="minCPM" name="minCPM" required type="text" value=""></div><div class="form-group  required"><label class="control-label" for="minSamples">Minsamples</label><input class="form-control" id="minSamples" name="minSamples" required type="text" value=""></div>');

//$().($('#reportDiffExpGenes')));
console.log("hello world");
}

});
