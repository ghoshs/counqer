var subentities = document.getElementById('subentities');
var subject = document.getElementById('subject');
var subjectIDlist = {};
var subjectID = '';

var objentities = document.getElementById('objentities');
var object = document.getElementById('object');
var objectIDlist = {};
var objectID = '';

var predentities = document.getElementById('predentities');
var predicate = document.getElementById('predicate');
var predicateIDlist = {};
var predicateID = '';

var option='wikidata';
var predrequest = new XMLHttpRequest();

var ftoption = 'wikidata';
var ftresult = {};

var flaskurl = 'http://localhost:5000/'; 

/** server edits**/
// var flaskurl = 'https://counqer.mpi-inf.mpg.de/v2/'; 


// free text form refresh
function ft_form_refresh() {
  $('#displacy').empty();
  ftresult = {};
}

// function to display NER results

function render_ner_results(result) {
  var containerEl = document.getElementById('displacy');

  var query_row = document.createElement("div");
  query_row.className = 'row vertical-align no-gutter query';
  query_row.innerHTML = '<div class="col-2"><strong>Query:</strong></div><div class="col-10"></div>';
  containerEl.appendChild(query_row);
  // call annotator on query
  var displacy = new displaCyENT({container: containerEl.querySelector('.query').querySelector('div:last-child')});
  displacy.render(result.query_tags.text, result.query_tags.ents, 'all_matches');

  // add results heading
  var result_heading = document.createElement("div");
  result_heading.className = 'row vertical-align';
  result_heading.innerHTML = '<div class="col-12"><strong>Results</strong></div>';
  containerEl.appendChild(result_heading);

  result.results_tags.forEach(function(item, index) {
    var rownum = index + 1;
    var result_row = document.createElement("div");
    result_row.className = 'row vertical-align no-gutter result';
    result_row.innerHTML = '<div class="col-2">' + rownum.toString() + '.</div><div class="col-10"></div>'

    containerEl.appendChild(result_row);
    var displacy = new displaCyENT({container: containerEl.querySelector('.result:last-child').querySelector('div:last-child')});
    displacy.render(item.text, item.ents, 'all_matches', item.ent_similarity);
  });
}

// ******************************** on document ready **************************************//
$(document).ready(function () {
  //  ******************************* nav controls ********************************//
  $('#navbar').on('click', 'a', function () {
    $('#navbar .active').removeClass('active');
    $(this).addClass('active');
  });

  //  ******************************* nav controls return to top ********************************//
  $('#footerReturn').click(function () {
    $('#navbar .active').removeClass('active');
    $('#navbar > li > a').first().addClass('active');
  });

  // ************************* #ftq form refresh *****************************//
  $('#ftqRefresh').click(function () {
    $('#ftquery').val('');
    ft_form_refresh();
  });

  // ************************* #ftq radio button events
  $('input[type=radio][name=ftq_ents]').change(function () {

    $('#displacy').children('div').slice(2).remove();
    console.log('val: ', this.value);

    if (this.value == 'All entities') {
      var containerEl = document.getElementById('displacy');
      ftresult.results_tags.forEach(function(item, index) {
        var rownum = index + 1;
        var result_row = document.createElement("div");
        result_row.className = 'row vertical-align no-gutter result';
        result_row.innerHTML = '<div class="col-2">' + rownum.toString() + '.</div><div class="col-10"></div>'

        containerEl.appendChild(result_row);
        var displacy = new displaCyENT({container: containerEl.querySelector('.result:last-child').querySelector('div:last-child')});
        displacy.render(item.text, item.ents, 'all_matches', item.ent_similarity);
      });
    }
    else if (this.value == 'Matched entities'){
      var containerEl = document.getElementById('displacy');
      ftresult.results_tags.forEach(function(item, index) {
        var rownum = index + 1;
        var result_row = document.createElement("div");
        result_row.className = 'row vertical-align no-gutter result';
        result_row.innerHTML = '<div class="col-2">' + rownum.toString() + '.</div><div class="col-10"></div>'

        containerEl.appendChild(result_row);
        var displacy = new displaCyENT({container: containerEl.querySelector('.result:last-child').querySelector('div:last-child')});
        displacy.render(item.text, item.ents, 'matched_entities', item.ent_similarity);
      });
    }    
  });

  // ************************* #ftq query event ******************************//
  $("#ftsearch").click(function () {
    ft_form_refresh();
    console.log($("#ftquery").val());
    var query = $("#ftquery").val();
    // displacy.parse(query);
    $.ajax({
      type: 'GET',
      url : flaskurl + 'ftresults',
      datatype : 'json',
      data : {'query': query},
      success : function(result, status){
        console.log("success!");
        console.log(result);
        ftresult = result;
        render_ner_results(ftresult);
      },
      error: function() {
        console.log("no results returned!");
      }
    });
  });
});