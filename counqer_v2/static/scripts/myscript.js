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

// var flaskurl = 'http://localhost:5000/'; 

/** server edits**/
var flaskurl = 'https://counqer.mpi-inf.mpg.de/ftq/'; 


// function for displaying information messages
function displayinfo(message) {
  $('#displayalert').empty();
  $('#displayalert').append(message);
  $('#displayalert').show();
}

// free text form refresh
function ft_form_refresh() {
  $('#queryDisplacy').empty();
  $('#snippetDisplacy').empty();
  $('#answerMedian').empty();
  $('#ftqResults').hide();
  ftresult = {};
}

// function to clear query settings
function clear_query_settings() {
  $("#ftqQuerySetting").toggle();
  $("#entities").val($("#entities option:first").val());
  $("#snippets").val($("#snippets option:first").val());
  $("#querytype").val($("#querytype option:first").val());
}

// function to create integer distribution table
function get_answerDist_tables(data, id) {
  var table_init, caret;
  caret = '<span class="caret"></span></button>';
  table_init = '<table class="dropdown-menu"><thead> <tr>' +
                   ' <th>Cardinal</th> <th>Snippet#</th>' +
                   '</tr> </thead> <tbody>';
  var table_end = '</tbody></table>';
  var tbody = '';
  var idx, integerObj;

  if (id.startsWith('headn')){
    integerObj = data.integers_headn;
  }
  else {
    integerObj = data.integers;
  }
  if (integerObj == null || integerObj == undefined || integerObj.length == 0) {
    return ('');
  }
  // sort on integer value
  integerObj.sort(function(a, b) {
    pos_compare = (parseInt(a.pos) < parseInt(b.pos))? -1: ((parseInt(a.pos) == parseInt(b.pos))? 0: 1);
    return ((parseInt(a.int) < parseInt(b.int))? -1: ((parseInt(a.int) > parseInt(b.int))? 1: pos_compare));
  });


  integerObj.forEach(function (item, index) {
    tbody += '<tr><td>' + item.int + '</td><td>' + item.pos + '</td></tr>';
  })

  return (caret+table_init+tbody+table_end);
}

// function to display median answer
function render_answer(result) {
  data = result.cardinal_stats;
  // create answer row for displaying integer distribution
  var html_answer_dist = '<div class="row vertical-align no-gutter" id="answerDist"></div>';
  $("#answer").append(html_answer_dist);
  // If no answer
  if (!data.hasOwnProperty('integers_headn') || data.integers_headn.length < 1){
    var text = '<div class="col-sm-12">' + 
               'No answer found from snippets' +
               '</div>';
    $("#answerMedian").append(text);
    return;
  }
  dd_preID = '<div class="col-sm-3 text-center dropdown">'+
                    '<button class="btn btn-default dropdown-toggle" type="button" data-toggle="dropdown"'; 
  dd_postID = ' > ';
  dd_post_text = '<span class="caret"></span></button>';
  html_headn = dd_preID + 'id="headnMatchedMedian"' + dd_postID +
                'Head noun matched: ' + data.median_headn + get_answerDist_tables(data, "headnMatchedMedian") + 
                '</div>';
  // html_headn_wgt = dd_preID + 'id="headnWeightMedian"' + dd_postID +
  //               'Head noun + position: ' + data.pos_wgt_median_headn + get_answerDist_tables(data, "headnWeightMedian") + 
  //               '</div>';

  $("#answerMedian").append(html_headn);
  // $("#answerDist").append(get_answerDist_tables(data, "noWeightMedian"));
  // $("#answerDist").append(get_answerDist_tables(data, "posWeightMedian"));

}

// function to display NER annotations
function render_ner_annotations(result) {
  var queryContainer = document.getElementById('queryDisplacy');
  var radio_option;
  var query_row = document.createElement("div");

  if ($('#entities').val() == 'Matched entities'){
    radio_option = 'matched_entities';
  }
  else {
    radio_option = 'all_matches';
  }
  // query annotation //
  // query_row.className = 'row vertical-align no-gutter query';
  queryContainer.innerHTML = '<div class="col-2" style="padding: 2px;"><strong>Annotated query: </strong></div><div class="col-10" style="padding: 2px;"></div>';
  // queryContainer.appendChild(query_row);
  // call annotator on query
  var displacy = new displaCyENT({container: queryContainer.querySelector('div:last-child')});
  displacy.render(result.query_tags.text, result.query_tags.ents, 'query');

  // Result snippet annotation
  var snippetContainer = document.getElementById('snippetDisplacy');
  var result_heading = document.createElement("div");
  result_heading.className = 'row vertical-align';
  result_heading.innerHTML = '<div class="col-12"><strong>Ranked snippets with annotation</strong></div>';
  snippetContainer.appendChild(result_heading);

  var resultTable = document.createElement("table");
  resultTable.className = 'table table-striped';
  var resultTbody = document.createElement("tbody");

  result.results_tags.forEach(function(item, index) {
    var rownum = index + 1;
    var result_row = document.createElement("tr");
    // result_row.className = 'row vertical-align no-gutter result';
    // result_row.innerHTML = '<div class="col-2">' + rownum.toString() + '.</div><div class="col-10"></div>'
    result_row.className = 'result';
    result_row.innerHTML = '<th scope="row">' + rownum.toString() + '</th><td></td>';

    resultTbody.appendChild(result_row);
    var displacy = new displaCyENT({container: resultTbody.querySelector('.result:last-child').querySelector('td:last-child')});
    displacy.render(item.text, item.ents, radio_option);
  });
  resultTable.appendChild(resultTbody);
  snippetContainer.appendChild(resultTable);
}

// function to render all components
function render_results(result) {
  render_answer(ftresult);
  render_ner_annotations(ftresult);
  $('#ftqResults').show();
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
    clear_query_settings();
  });

  // ************************* #ftq radio button events
  $('#entities').change(function () {
    console.log(this.value);
    console.log(ftresult);
    // execute only if there are results in the current display
    if ($.isEmptyObject(ftresult)) {
      return;
    }

    $('#snippetDisplacy').children('table').remove();
    // console.log('val: ', this.value);
    var containerEl = document.getElementById('snippetDisplacy');
    var resultTable = document.createElement("table");
    resultTable.className = 'table table-striped';
    var resultTbody = document.createElement("tbody");
    var radio_option;
    if (this.value == 'All entities'){
      radio_option = 'all_matches';
    }
    else {
      radio_option = 'matched_entities';
    }
    ftresult.results_tags.forEach(function(item, index) {
      var rownum = index + 1;
      var result_row = document.createElement("tr");
      // result_row.className = 'row vertical-align no-gutter result';
      // result_row.innerHTML = '<div class="col-2">' + rownum.toString() + '.</div><div class="col-10"></div>';
      result_row.className = 'result';
      result_row.innerHTML = '<th scope="row">' + rownum.toString() + '</th><td></td>';

      resultTbody.appendChild(result_row);
      var displacy = new displaCyENT({container: resultTbody.querySelector('.result:last-child').querySelector('td:last-child')});
      displacy.render(item.text, item.ents, radio_option);
    });
    resultTable.appendChild(resultTbody);
    containerEl.appendChild(resultTable);    
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
      data : {'query': query, 'snippets': $("#snippets").val()},
      success : function(result, status){
        console.log("success!");
        console.log(result);
        ftresult = result;
        render_results(ftresult);
      },
      error: function() {
        console.log("no results returned!");
        var msg = "<div class='alert alert-warning alert-dismissible' style='margin-bottom: 0px'>" + 
                  "<strong>!!</strong> We could not retrieve any results! Server error <strong>!!</strong> " + 
                  "<button type='button' class='close' data-dismiss='alert' aria-label='Close'>" + 
                  "<span aria-hidden='true'>&times;</span> </button></div>";
        displayinfo(msg);
      }
    });
  });

  // *********************** ftq query settings *******************************//
  $("#ftqQuerySettingIcon").click(function (){
    $("#ftqQuerySetting").toggle();
  });

  // *********************** ftq clear settings *******************************//
  $("#ftqClearSettings").click(function () {
    clear_query_settings();
  });

  // 
  $("#posWeightMedian").on("click", function () {
      alert('posmedian');
      $(".tblpos-median").toggle();
  });
  $("#noWeightMedian").on("click", function () {
      alert('posmedian');
      $(".tblmedian").toggle();
  });
});