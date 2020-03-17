var subentities = document.getElementById('subentities');
var subject = document.getElementById('subject');
var subjectIDlist = {};
var subjectID = '';

// var predicate = document.getElementById('predicate');
var predicateIDlist = {};
var predicateID = '';

var option='wikidata';
var predrequest = new XMLHttpRequest();

var wd_labels = {};

// var flaskurl = 'http://localhost:5000/';

/** server edits**/
var flaskurl = 'https://counqer.mpi-inf.mpg.de/spo/'; 

// display info messages on query click
var waitmsg = "<div class='row alert alert-info alert-dismissible' style='margin-bottom: 0px'><strong>!!</strong> Hold on to your seats, CounQER is fetching the results!<button type='button' class='close' data-dismiss='alert' aria-label='Close'> <span aria-hidden='true'>&times;</span> </button></div>";
var endmsg = "<div class='row alert alert-success alert-success' style='margin-bottom: 0px'><strong>!!</strong> Hope the results satisfy your curiosity!<button type='button' class='close' data-dismiss='alert' aria-label='Close'> <span aria-hidden='true'>&times;</span> </button></div>";
var errmsg = "<div class='row alert alert-warning alert-warning' style='margin-bottom: 0px'><strong>!!</strong> You have counquered CounQER! We ran into problems while executing this query.<button type='button' class='close' data-dismiss='alert' aria-label='Close'> <span aria-hidden='true'>&times;</span> </button></div>";
  
// function to process the json file returned and
// populate the predicate options
function jsonCallback (result){
  var jsonOptions = result;
  var predentities = document.getElementById('predentities');
  var val_inv = '';

  Object.keys(result).forEach(function(itemtype) {
    if (itemtype.includes('_inv')){
      val_inv = ' (inv)';
      // html_inv = '&#x207b &sup1';
    }
    else{
      val_inv = ''; 
    }
    Object.keys(jsonOptions[itemtype]).forEach(function (aligntype) {
      jsonOptions[itemtype][aligntype].forEach(function (item) {
        if (!(item+val_inv in predicateIDlist)) {
          // var dropdown_option = document.createElement('option');
          // dropdown_option.setAttribute('pred-key', item+val_inv);
          // dropdown_option.value = item+val_inv;
          // predentities.appendChild(dropdown_option);
          var isaligned = false;
          if (aligntype == 'aligned'){
            isaligned = true;
          }
          predicateIDlist[item+val_inv] = {type: itemtype, instances: '0', aligned: isaligned};
        }  
      });
    });
  });
  sortedPredAutocomplete();
  // console.log('in jsoncallback, result: ',result);
  // console.log($("#predentities").children().length);
}

// function for displaying information messages
function displayinfo(message) {
  // $('#displayalert').children().replaceWith(message);
  $('#displayalert').append(message);
  $('#displayalert').show();
}

// function to refresh results
function result_refresh () {
  // results
  $(".first").hide();
  $("#s1").empty();
  $("#p1").empty();
  $("#o1").empty();
  $("#q1 a").attr("href", "#");
  $(".second > tbody").empty();
  $(".second > thead > tr > td").empty();
  $(".second").hide();
  $("#displayalert").empty();
  // $(".second").html('<strong>Related Predicates</strong><hr>');
}

// function to refresh inputs
function form_refresh () {
  // $('#objectities').empty();
  $('#subentities').empty();
  $('#predentities').empty();
  $('#subject').val('');
  $('#predicate').val('');
  subjectIDlist = {};
  predicateIDlist = {};
  // objectIDlist = {};
  subjectID = '';
  predicateID = '';
  $("#subject").removeData();
}

// function to initiate ajax for loading predicate options 
$.fn.predautocomplete = function () {
  var fname, path;
  if (option === 'wikidata') {
    fname = 'wikidata.json';
  }
  else if (option === 'dbpedia_raw') {
    fname = 'dbpedia_raw.json';
  }
  else if (option === 'dbpedia_mapped') {
    fname = 'dbpedia_mapped.json'
  }
  path = flaskurl + 'get_predicate_list';
  $.ajax({
    type: 'GET',
    url : path,
    dataType: 'json',
    data: {'fname': fname},
    success: function(result, status){
      jsonCallback(result);
    },
    error: function(){
      console.log("Couldn't load '", fname, "' set predicate json file :(");
    },
    cache: false
  });
};

// function to read returned triples
function gettriples(response, get) {
  var result = [];
  var len = response.length;
  var i;
  if ('o1Label' in response[0] || 's1Label' in response[0]) {
    i = 1;
  }
  else {
    i = 0;
  }
  for (; i<len; i++) {
    var temp = {};
    for (item in response[i]){
      if (item === 's2Label'){
        temp['s2'] = join_entities(response[i][item], 's2', get);
      }
      else if (item === 'o2Label') {
        temp['o2'] = join_entities(response[i][item], 'o2', get);
      }
      else {
        temp[item] = response[i][item];
      }
    }
    result.push(temp);
  }
  return result;
}

// add results to related predicates
function add_child (s2, p2, o2, q2, pstat, direction='', type='predE') {
  // console.log('add child ', s2, o2);
  if ($(".second").is(":hidden")) {
    $(".second").show();
  }
  if (direction === '_inv'){
    direction = '<sup>-1</sup>';
  }
  text = '<tr class="triple">' +
         '<td class="s2 partial">' + insert_trunc_and_full_result(s2) + '</td>' +
         '<td > <div class="col-12 btn btn-warning p2" title="' + insert_pstats(pstat, type) + '">' + p2 + direction + '</div></td>' +
         '<td class="o2 partial">' + insert_trunc_and_full_result(o2) + '</td>' +
         '<td class="q2"><a href="' + q2 + '" target="_blank"><span class="glyphicon glyphicon-new-window" style="font-size: 1em"></span></a></td>' +
         '</tr>' ;
         // '<tr class="p2stat" style="display: none">' + insert_pstats(pstat, type) + '</tr>';
  $(".second > tbody").append(text);
  // console.log(text);
}

// join string array to comma separated string with total entity count
function join_entities(entityarray, theme='s1', get='predE'){
  var entities = [], entityLabel=[];
  var len = entityarray.length;
  var result = {'trunc': '', 'full': ''}, overflow_idx = -1, overflow_limit = 15;
  var link_prefix = '<a href="', link_mid='" target="_blank">', link_suffix='</a>';
  for (var i=0; i<len; i++){
    var item = '', itemlabel = '';
    item = entityarray[i].split('/');
    itemlabel = item[item.length - 1].split('_').join(' ');
    entityLabel.push(itemlabel);
    
    // insert href for entities
    if (entityarray[i].indexOf('dbpedia') != -1){
      item = link_prefix + entityarray[i] + link_mid;
    }
    else if (entityarray[i].indexOf('wikidata') != -1) {
      item = link_prefix + item.slice(0, item.length - 1).join('/') + link_mid;
    }
    // literals have no href
    else {
      item = '';
    }
    // console.log(item);
    entities.push(item);
    
    if (overflow_idx < 0 && overflow_limit > 0){
      overflow_limit -= itemlabel.length;
      if (overflow_limit <= 0){
        overflow_idx = i;
      }
    }
  }
  // reset overflow limit
  overflow_limit = 15;
  if (overflow_idx >= 0){
    for (var i=0; i<= overflow_idx; i++){
      var end_idx = entityLabel[i].length;
      if (end_idx >= overflow_limit){
        end_idx = overflow_limit;
      }
      if (entities[i].length > 0){
        result['trunc'] += entities[i] + entityLabel[i].slice(0, end_idx+1) + link_suffix;
      }
      else {
        result['trunc'] += entityLabel[i].slice(0, end_idx+1);
      }
      overflow_limit -= end_idx;
      if (i < entities.length - 1){
        result['trunc'] += '; '
      }
    }
    if (entities.length == 1000){
      result['trunc'] = result['trunc'] + ' ... (>' + (entities.length).toString() + ' in total)';  
    }
    else {
      result['trunc'] = result['trunc'] + ' ... (' + (entities.length).toString() + ' in total)';
    }
    
  }
  // else {
  for (var i=0; i<=entities.length-1; i++){
    if (entities[i].length > 0){
      result['full'] += entities[i] + entityLabel[i] + link_suffix;
    }
    else {
      result['full'] += entityLabel[i];
    }
    if (i < entities.length - 1){
      result['full'] += '; '
    }
  } 
  // }
  if (result['trunc'].length == 0) {
    result['trunc'] = result['full'];
  }
  // For empty results
  if (result['full'].length == 0) {
    var emptyResult = '-';
    if (theme === 's1' || theme === 's2' || (theme === 'o1' && get === 'predC') || (theme === 'o2' && get === 'predE')){
      emptyResult = '(0 in total)';
    }
    else if ((theme === 'o1' && get === 'predE') || (theme === 'o2' && get === 'predC')){
      emptyResult = '(no instantiations)'
    }
    result['full'] = emptyResult;
    result['trunc'] = emptyResult;
  }
  // console.log(entityarray);
  // console.log(entityarray.length);
  // console.log(result);
  return(result);
}

// function to add <p> elements for full and truncated results
function insert_trunc_and_full_result (entity) {
  // console.log('entity: ', entity);
  return ('<p class="truncresult">' + entity['trunc'] + '</p> <p class="fullresult">' + entity['full'] +'</p>');
}

// function to add elements containing predicate statistics
function insert_pstats (pstats, type='predE') {
  // console.log(pstats);
  var val = '';
  if (type == 'predC')  {
    if (pstats[0]['numeric_avg']) {
      val = pstats[0]['numeric_avg'].toFixed(3);
    }
    else {
      val = '-'
    }
    // text = '<td colspan="4"> Average value: ' + val + ' </td>'
    text = 'Average value: ' + val;
  }
  else {
    if (pstats[0]['persub_avg_ne']) {
      val = pstats[0]['persub_avg_ne'].toFixed(3);
    }
    else {
      val = '-'
    }
    // text = '<td colspan="4"> Average entities per subject: ' + val + ' </td>'
    text = 'Average entities per subject: ' + val;
  }
  return(text);
}

// funtion to populate table after getting results
function displayresponse (results) {
  objectIDlist = subjectIDlist;
  var triple1={'s1': {}, 'p1': '', 'o1': {}, 'q': ''};
  var triple2={'direct': [], 'inverse': []};
  console.log(results);
  if ('error' in results) {
    if (results.error === 'No co-occurring pair'){
      var msg = "<div class='row alert alert-warning alert-dismissible' style='margin-bottom: 0px'><strong>!!</strong> There exists no alignment for this predicate.<button type='button' class='close' data-dismiss='alert' aria-label='Close'> <span aria-hidden='true'>&times;</span> </button></div>";
      displayinfo(msg);
    }
  }
  triple1['p1'] = results.p1;
  var link_prefix_wd = '<a href="http://wikidata.org/entity/', link_prefix_dbp='<a href="http://dbpedia.org/resource/';
  var link_mid='" target="_blank">', link_suffix='</a>';
  // if initial query was <s, p, ?o>
  if ('s1' in results) {
    if (option === 'wikidata'){
      triple1['s1']['trunc'] = Object.keys(subjectIDlist).find(key => subjectIDlist[key] === results.s1);
      triple1['s1']['trunc'] = link_prefix_wd + results.s1 + link_mid + triple1['s1']['trunc'] + link_suffix;
    }
    else {
      var temp = results.s1.split('/');
      triple1['s1']['trunc'] =  temp[temp.length - 1].split('_').join(' ');
      triple1['s1']['trunc'] = link_prefix_dbp + results.s1 + link_mid + triple1['s1']['trunc'] + link_suffix;
    }
    triple1['s1']['full'] = triple1['s1']['trunc'];
  }
  // if initial query was <?s, p, o>
  else if ('o1' in results) {
    if (option === 'wikidata') {
      triple1['o1']['trunc'] = Object.keys(objectIDlist).find(key => objectIDlist[key] === results.o1);
      triple1['o1']['trunc'] = link_prefix_wd + results.o1 + link_mid + triple1['o1']['trunc'] + link_suffix;
    }
    else {
      var temp = results.o1.split('/');
      triple1['o1']['trunc'] = temp[temp.length - 1].split('_').join(' ');
      triple1['o1']['trunc'] = link_prefix_dbp + results.o1 + link_mid + triple1['o1']['trunc'] + link_suffix;
    }
    triple1['o1']['full'] = triple1['o1']['trunc'];
  }
  if (('error' in results['response'] && 'error' in results['response_inv']) || ('error' in results && results.error === 'No instantiation')) {
    var msg = "<div class='row alert alert-warning alert-dismissible' style='margin-bottom: 0px'><strong>!!</strong> There exist no instantiated facts on the queried and the related set predicates.<button type='button' class='close' data-dismiss='alert' aria-label='Close'> <span aria-hidden='true'>&times;</span> </button></div>";
    displayinfo(msg);
    return;
  }
  else if ('error' in results['response_inv']) {
    if ('o1Label' in results['response'][0]) {
      triple1['o1'] = join_entities(results['response'][0]['o1Label'], 'o1', results.get);
      triple1['type'] = 'direct';
    }
    else if ('s1Label' in results['response'][0]) {
      triple1['s1'] = join_entities(results['response'][0]['s1Label'], 's1', results.get);
      triple1['type'] = 'direct';
    }
    else {
      var msg = "<div class='row alert alert-warning alert-dismissible' style='margin-bottom: 0px'><strong>!!</strong> There exist no instantiated facts on the queried set predicate.<button type='button' class='close' data-dismiss='alert' aria-label='Close'> <span aria-hidden='true'>&times;</span> </button></div>";
      displayinfo(msg);
    }
    triple1['q'] = results['response'][0]['q'];
    triple2['direct'] = gettriples(results['response'], results.get);
  }
  else if ('error' in results['response']) {
    if ('o1Label' in results['response_inv'][0]) {
      triple1['o1'] = join_entities(results['response_inv'][0]['o1Label'], 'o1', results.get);
      triple1['type'] = 'inverse';
    }
    else if ('s1Label' in results['response_inv'][0]) {
      triple1['s1'] = join_entities(results['response_inv'][0]['s1Label'], 's1', results.get);
      triple1['type'] = 'inverse';
    }
    else {
      var msg = "<div class='row alert alert-warning alert-dismissible' style='margin-bottom: 0px'><strong>!!</strong> There exist no instantiated facts on the queried set predicate.<button type='button' class='close' data-dismiss='alert' aria-label='Close'> <span aria-hidden='true'>&times;</span> </button></div>";
      displayinfo(msg);
    }
    triple1['q'] = results['response_inv'][0]['q'];
    triple2['inverse'] = gettriples(results['response_inv'], results.get);
  }
  else {
    if ('o1Label' in results['response'][0]) {
      triple1['o1'] = join_entities(results['response'][0]['o1Label'], 'o1', results.get);
      triple1['type'] = 'direct';
      triple1['q'] = results['response'][0]['q'];
    }
    else if ('s1Label' in results['response'][0]) {
      triple1['s1'] = join_entities(results['response'][0]['s1Label'], 's1', results.get);
      triple1['type'] = 'direct';
      triple1['q'] = results['response'][0]['q'];
    }
    if ('o1Label' in results['response_inv'][0]) {
      triple1['o1'] = join_entities(results['response_inv'][0]['o1Label'], 'o1', results.get);
      triple1['type'] = 'inverse';
      triple1['q'] = results['response_inv'][0]['q'];
    }
    else if ('s1Label' in results['response_inv'][0]) {
      triple1['s1'] = join_entities(results['response_inv'][0]['s1Label'], 's1', results.get);
      triple1['type'] = 'inverse';
      triple1['q'] = results['response_inv'][0]['q'];
    }
    triple2['direct'] = gettriples(results['response'], results.get);
    triple2['inverse'] = gettriples(results['response_inv'], results.get);
  }
  // console.log(triple1);
  // console.log(triple2);
  if (triple1.s1.hasOwnProperty('trunc') && triple1.p1.length > 0 && triple1.o1.hasOwnProperty('trunc')){  
    $(".first").show();
    $("#s1").html(insert_trunc_and_full_result(triple1['s1']));
    $("#o1").html(insert_trunc_and_full_result(triple1['o1']));
    $("#q1 a").attr("href", triple1['q']);
    if (triple1['type'] === "direct") {
      $("#p1").html(triple1['p1']);
      if (results['get'] == 'predE'){
        $("#p1").attr("title", insert_pstats(results['stats']['response'][triple1['p1']], 'predC'));
        // $("#p1stat").html(insert_pstats(results['stats']['response'][triple1['p1']], 'predC'));
      }
      else {
        $("#p1").attr("title", insert_pstats(results['stats']['response'][triple1['p1']]))
        // $("#p1stat").html(insert_pstats(results['stats']['response'][triple1['p1']]));
      }
      
    }
    else {
      if (results['get'] == 'predE'){
        $("#p1").attr("title", insert_pstats(results['stats']['response_inv'][triple1['p1']], 'predC'));
        // $("#p1stat").html(insert_pstats(results['stats']['response_inv'][triple1['p1']], 'predC'));
        $("#p1").html(triple1['p1']);
      }
      else {
        $("#p1").attr("title", insert_pstats(results['stats']['response_inv'][triple1['p1']]));
        // $("#p1stat").html(insert_pstats(results['stats']['response_inv'][triple1['p1']]));
        $("#p1").html(triple1['p1']+'<sup>-1</sup>');
      }
    }
    // console.log('s1.html: ', $("#s1").html());
    // console.log('p1.html: ', $("#p1").html());
    // console.log('o1.html: ', $("#o1").html());
  }
  if (triple2['direct'].length > 0){
    // Modify heading of related predicates
    if (results.get == 'predE'){
      $(".second > thead > tr > td").empty().append('<strong> Related Enumerating Predicates </strong>');
    }
    else if (results.get == 'predC'){
      $(".second > thead > tr > td").empty().append('<strong> Related Counting Predicates </strong>');
    }
    // Add row child for each related predicate SPO triple
    var len = triple2['direct'].length;
    // if (triple1['s1'].length > 0){
    if (triple1['s1'].hasOwnProperty('trunc')){
      for (var i=0; i<len; i++){
        // add related results 
        if ((results['get'] === 'predC' && triple1['s1']['full'].indexOf(';') === -1) || (results['get'] === 'predE')){
          add_child(triple1['s1'], triple2['direct'][i]['p2'], triple2['direct'][i]['o2'], triple2['direct'][i]['q'], results['stats']['response'][triple2['direct'][i]['p2']], '', results['get']);
        }
      }
    }
  }
  if (triple2['inverse'].length > 0) {
    // Modify heading of related predicates
    if (results.get == 'predE'){
      $(".second > thead > tr > td").empty().append('<strong> Related Enumerating Predicates </strong>');
    }
    else if (results.get == 'predC'){
      $(".second > thead > tr > td").empty().append('<strong> Related Counting Predicates </strong>');
    }
    // Add row child for each related predicate SPO triple
    var len = triple2['inverse'].length;
    // if (triple1.s1.length > 0) {
    if (triple1.s1.hasOwnProperty('trunc')){
      for (var i=0; i<len; i++){
        if (results['get'] ===  'predC') {
          if ('s1' in results && triple1['s1']['full'].indexOf(';') === -1) {
            // add inv results if s1 is a single entity
              // console.log(triple1.s1.full, triple1.s1.full.indexOf(';'));
              add_child(triple1['s1'], triple2['inverse'][i]['p2'], triple2['inverse'][i]['o2'], triple2['inverse'][i]['q'], results['stats']['response_inv'][triple2['inverse'][i]['p2']], '', 'predC');
          }
          // queried object is the subject for related predicates
          else if (triple1['o1']['full'].indexOf(';') === -1){
            // add inv results if o1 is a single entity
              // console.log('inv: ', triple1.o1.full, triple1.o1.full.indexOf(';'));
              add_child(triple1['o1'], triple2['inverse'][i]['p2'], triple2['inverse'][i]['o2'], triple2['inverse'][i]['q'], results['stats']['response_inv'][triple2['inverse'][i]['p2']], '', 'predC');
          }
        }
        if (results['get'] === 'predE') {
          add_child(triple1['s1'], triple2['inverse'][i]['p2'], triple2['inverse'][i]['s2'], triple2['inverse'][i]['q'], results['stats']['response_inv'][triple2['inverse'][i]['p2']], '_inv');
        }
      }
    }
  }

}
 
// function to load autocomplete options for wikidata entities
$.fn.wdautocomplete = function (entities, IDlist, val) {
  $.ajax({
    type: 'GET',
    url: 'https://www.wikidata.org/w/api.php',
    dataType: 'jsonp',
    data: {
      'action': 'wbsearchentities',
      'search': val,
      'format': 'json',
      'language': 'en',
      'type': 'item'
    },
    success: function(result, status){
      var jsonOptions = result['search'];
      
      jsonOptions.forEach(function(item) {
        // create new dropdown items
        if (!(item['label'] in IDlist)){
          var dropdown_option = document.createElement('option');
          dropdown_option.value = item['label']+': ' + item['description'];
          entities.appendChild(dropdown_option);
          IDlist[item['label']] = item['id'];
        }
      });
      // console.log('after:: ',IDlist);
    },
    error: function(){
      subject.placeholder = "Couldn't load enity options :(";
    }
  });
  return;
}

// function to load autocomplete options for dbpedia entities
$.fn.dbpautocomplete = function (entities, IDlist, val) {
  $.ajax({
    type: 'GET',
    url: 'https://en.wikipedia.org/w/api.php',
    dataType: 'jsonp',
    data: {
      'action': 'opensearch',
      'search': val,
      'format': 'json',
      'language': 'en',
      'namespace': '0'
    },
    success: function(result, status){
      var jsonOptions = result[1];
    
      var urlList = result[result.length-1];
      i=0;
      jsonOptions.forEach(function(label) {
        if (!(label in IDlist)){
          var dropdown_option = document.createElement('option');
          dropdown_option.value = label;
          entities.appendChild(dropdown_option);
          IDlist[label] = urlList[i];
        }
        i=i+1;
      });
    },
    error: function(){
      subject.placeholder = "Couldn't load enity options :(";
    }
  });
  return;
}

// function to complete sample queries
function samplequeries(payload){
  $.when(form_refresh(), result_refresh()).then(displayinfo(waitmsg));
  subjectIDlist[payload['subject']] = payload['subjectID'];
  subjectID = payload['subjectID'];
  predicateID = payload['predicate'];
  $.when($("#predicate").predautocomplete()).then(order_predicates());
  $("#subject").val(payload['subject']);
  $("#predicate").val(payload['predicate']);
  // $("#object").val(payload['object']);
  option = payload['kbname'];
  if (option === 'wikidata'){
    change_kb_highlight();
  }
  else if (option =='dbpedia_raw'){
    change_kb_highlight("#DBPr-btn", "#WD-btn", "#DBPm-btn");
  }
  else {
    change_kb_highlight("#DBPm-btn", "#WD-btn", "#DBPr-btn");
  }
  $.ajax({
    type: 'GET',
    url: flaskurl+'spoquery',
    contentType: 'application/json',
    dataType: 'json',
    data: {
      'option': payload['kbname'],
      'subject': subjectID,
      'predicate': predicateID
      // 'object': payload['object']
    },
    success: function(result, status){
      // console.log(result);
      console.log(subjectID, predicateID, predicateIDlist);
      displayinfo(endmsg);
      displayresponse(result);
      // subjectIDlist = {};
    },
    error: function(){
      displayinfo(errmsg);
      console.log('error in flask get');
    }
  });
}

// get Wikidata property labels file
function get_wd_labels() {
  $.ajax({
    type : 'GET',
    url : flaskurl+'getwdlabels',
    // async: false,
    dataType: 'text',
    success: function(result, status) {
      var labels = $.csv.toObjects(result);
      labels.forEach(function (item) {
        wd_labels[item['Property'].split('/').pop()] = item['PropLabel'];
      });
      // console.log('Done!',wd_labels);
    },
    error: function(){
      console.log("Couldn't load Wikidata labels. Try again!");
    },
    cache: false 
  });
}

// change KB selection highlights
function change_kb_highlight(selected="#WD-btn", other1="#DBPr-btn", other2="#DBPm-btn"){
  $(selected).addClass("btn-outline-infp").removeClass("btn-link");
  $(other1).addClass("btn-link").removeClass("btn-outline-info");
  $(other2).addClass("btn-link").removeClass("btn-outline-info");
}

// generate table entries for top alignments from each item
function get_table_data(item, kb='wd') {
  var asterix = '';
  if (parseFloat(item['score']).toFixed(3) > 0.9) {
    asterix = '*';
  }
  var button_pre = '<a style="padding-left: 5px;" href="';
  var button_post = '" target="_blank"><span class="glyphicon glyphicon-new-window" style="font-size: 1em; float: right;"></span></a>';
  var button_url = '', button = '';
  var labelE, labelC, anchorE = '', anchorC = '';
  var dbp = 'http://dbpedia.org/property/';
  var dbo = 'http://dbpedia.org/ontology/';
  if (kb == 'wd') {
    labelE = item['predE'].split('/').pop();
    labelC = item['predC'].split('/').pop();
  
    if (labelE.split('_inv').shift() in wd_labels){
      if (labelE.indexOf('_inv') !== -1){
        labelE = labelE.split('_inv').shift() + ': ' + wd_labels[labelE.split('_inv').shift()] + '<sup>-1</sup>';  
      }
      else{
        labelE = labelE.split('_inv').shift() + ': ' + wd_labels[labelE.split('_inv').shift()];  
      }
    }
    if (labelC in wd_labels){
      labelC = labelC + ': ' + wd_labels[labelC];  
    }
    if (labelE.indexOf('_inv') !== -1){
      button_url = 'https://query.wikidata.org/#SELECT%20distinct%20%3Fs%20%3FsLabel%20WHERE%7BSERVICE%20wikibase%3Alabel%20%7B%20bd%3AserviceParam'+
                   '%20wikibase%3Alanguage%20%22en%22.%20%7DOPTIONAL%20%7B%3Fo1%20wdt%3A'+ labelE.split(':').shift() +'%20%3Fs.%20%3Fs%20wdt%3A'+
                   labelC.split(':').shift() +'%20%3Fo2.%7D%7D%20limit%2010';
    }
    else {
      button_url = 'https://query.wikidata.org/#SELECT%20distinct%20%3Fs%20%3FsLabel%20WHERE%20%7BSERVICE%20wikibase%3Alabel%20%7B%20bd%3AserviceParam'+
                 '%20wikibase%3Alanguage%20%22en%22.%20%7DOPTIONAL%20%7B%3Fs%20wdt%3A'+labelE.split(':').shift()+'%20%3Fo1%3Bwdt%3A'+
                 labelC.split(':').shift()+'%20%3Fo2.%7D%7D%20limit%2010';  
    }
    anchorE = '<a href="' + item['predE'].split('_inv').shift() + '" target="_blank">' + labelE + '</a>';
    anchorC = '<a href="' + item['predC'] + '" target="_blank">' + labelC + '</a>';
  }
  else if ((kb == 'dbp') || (kb == 'dbo')) {
    if (kb == 'dbp'){
      labelE = item['predE'].split(dbp).pop();
      labelC = item['predC'].split(dbp).pop();  
    }
    else{
      labelE = item['predE'].split(dbo).pop();
      labelC = item['predC'].split(dbo).pop();
    }
    if (labelE.indexOf('_inv') !== -1){
      button_url = 'http://dbpedia.org/snorql/?query=SELECT+distinct+%3Fs+WHERE+%7B%0D%0A%3Fo1+%3C'+
                   item['predE'].split('_inv').shift()+'%3E+%3Fs.%0D%0A%3Fs+%3C'+
                   item['predC']+'%3E+%3Fo2.%0D%0A%7Dlimit+10';
      labelE = labelE.split('_inv').shift() + '<sup>-1</sup>';
    }
    else {
      button_url = 'http://dbpedia.org/snorql/?query=SELECT+distinct+%3Fs+WHERE+%7B%0D%0A%3Fs+%3C'+
                   item['predE']+'%3E+%3Fo1%3B%0D%0A%3C'+item['predC']+
                   '%3E+%3Fo2.%0D%0A%7Dlimit+10'
    }
    anchorE = '<a href="' + item['predE'].split('_inv').shift() + '" target="_blank">' + labelE + '</a>';
    anchorC = '<a href="' + item['predC'] + '" target="_blank">' + labelC + '</a>';
  }
  else {
    labelE = item['predE'].split('/').pop().split('.').join('>');
    labelC = item['predC'].split('/').pop().split('.').join('>');
    if (labelE.indexOf('_inv') !== -1){
      labelE = labelE.split('_inv').shift() + '<sup>-1</sup>';
    }
    button_pre = '';
    button_post = '';
    anchorE = '<a title="' + item['predE'].split('_inv').shift() + '">' + labelE + '</a>';
    anchorC = '<a title="' + item['predC'] + '">' + labelC + '</a>';
  }
  button = button_pre + button_url + button_post;
  var htmldata = '<tr>' + 
                 '<td>' + anchorE + '</td>' +
                 '<td>' + anchorC + '</td>' +
                 '<td>' + parseFloat(item['score']).toFixed(3) + asterix  + button + '</td>' +
                 '</tr>';
  return htmldata;
}

// function to populate alignment results
function fill_alignment_table(result, elementID, kb) {
  var data = $.csv.toObjects(result);
  data.forEach(function (item) {
    $(elementID + " > tbody").append(get_table_data(item, kb));
  });
  $(elementID).DataTable({
    "order": [[2,"desc"]]
  });
  $('.dataTables_length').addClass('bs-select');
}

// make SPARQLQuery to Wikidata
function makeSPARQLQuery( endpointUrl, sparqlQuery, doneCallback ) {
  var settings;
  if (option === 'wikidata') {
    settings = {
      headers: { Accept: 'application/sparql-results+json' },
      data: { query: sparqlQuery}
    }; 
  }
  else {
    settings = {
      headers: { Accept: 'application/sparql-results+json' },
      data: { query: sparqlQuery, output: 'json'}
    };
  }
  return $.ajax( endpointUrl, settings ).then( doneCallback );
}

// function to add #intantiations
function addInstantiations(data, dir=''){
  // console.log(data, dir);
  if (option === 'wikidata' && $.isEmptyObject(wd_labels)){
    $.when(get_wd_labels()).then(console.log('WD labels loaded'));
  }
  data.results.bindings.forEach(function(item) {
    // console.log(item.p.value.split('/').pop());
    var key;
    if (option === 'wikidata'){
      key = item.p.value.split('/').pop();
      if (key in wd_labels && key+': '+wd_labels[key]+dir in predicateIDlist){
        // console.log('updated',key+': '+wd_labels[key]+dir);
        predicateIDlist[key+': '+wd_labels[key]+dir]['instances'] = item.cnt.value;
      }  
    }
    else {
      if (option === 'dbpedia_raw'){
        // separate at capital letters
        key = item.p.value.split('dbpedia.org/property/').pop().split(/(?=[A-Z])/);
        // lowercase 1st char of each word and join all words with ' ' separator
        key = key.map(function(word) { return word.charAt(0).toLowerCase()+word.substring(1) }).join(' ');
        key = 'dbp: ' + key;
      }
      else {
        key = item.p.value.split('dbpedia.org/ontology/').pop().split(/(?=[A-Z])/);
        key = key.map(function(word) { return word.charAt(0).toLowerCase()+word.substring(1)} ).join(' ');
        key = 'dbo: ' + key;
      }
      if (key+dir in predicateIDlist) {
        predicateIDlist[key+dir]['instances'] = item.cnt.value;
      } 
    }    
  });
  sortedPredAutocomplete();
}

// return a disabled option with headings
function set_heading(text){
  var dropdown_option = document.createElement('option');
  dropdown_option.value = " ";
  dropdown_option.text = text;
  dropdown_option.setAttribute('readonly', 'readonly');
  return dropdown_option;
}

// function to update datalist options
function sortedPredAutocomplete (){
  // console.log('in sorted!');
  var sortablePop = [], sortableUnpop = [], headingPopAlign = '', headingPopNotAlign = '', headingNotPop = '';
  for (var key in predicateIDlist) {
    // console.log(predicateIDlist[key]);
    if (predicateIDlist[key]['instances'] == '0'){
      sortableUnpop.push([key, predicateIDlist[key]['type'], predicateIDlist[key]['instances'], predicateIDlist[key]['aligned']]);
    }
    else{
      sortablePop.push([key, predicateIDlist[key]['type'], predicateIDlist[key]['instances'], predicateIDlist[key]['aligned']]);  
    }
    
  }

  sortablePop.sort(function(a,b) {
    return ((b[3]-a[3]) || (parseInt(b[2]) - parseInt(a[2])));
  });

  $.when($('#predentities').empty()).then(function() {
    // console.log(sortable);
    var predentities = document.getElementById('predentities');
    sortablePop.forEach(function(item) {
      var dropdown_option = document.createElement('option');
      dropdown_option.setAttribute('pred-key', item[0]);
      if (headingPopAlign === '' && item[3]){
        predentities.appendChild(set_heading('== Populated w/ alignments =='));
        headingPopAlign = 'pop w/ align set';
        console.log(headingPopAlign);
      }
      if (headingPopNotAlign === '' && !item[3]){
        predentities.appendChild(set_heading('== Populated w/o alignments =='));
        headingPopNotAlign = 'pop w/o align set';
        console.log(headingPopNotAlign); 
      }
      dropdown_option.value = item[0] + ' (' + item[2] + ')';
      predentities.appendChild(dropdown_option);
    });

    sortableUnpop.forEach(function (item) {
      var dropdown_option = document.createElement('option');
      dropdown_option.setAttribute('pred-key', item[0]);
      if (headingNotPop === ''){
        predentities.appendChild(set_heading('== Unpopulated =='));
        headingNotPop = 'not pop set';
        console.log(headingNotPop);
      }
      dropdown_option.value = item[0];
      predentities.appendChild(dropdown_option)
    });
  });
}

// fucntion to empty predicate ordering on old subject
function emptyPredOrdering() {
  Object.keys(predicateIDlist).forEach(function (item) {
    predicateIDlist[item]['instances'] = '0';
  });
}

// fucntion to check instantiated predicates and reorder predicates
function order_predicates() {
  // console.log('calling order');
  // if the subjectID set then order predicates
  if (subjectID.length !== 0){
    var endpointUrl, sparqlQuery;
    if (option === 'wikidata'){
      endpointUrl = 'https://query.wikidata.org/sparql',
      sparqlQuery1 = "select ?p (count(?o) as ?cnt) where {\n" +
        "  wd:" + subjectID + " ?p ?o.\n" +
        "?x wikibase:directClaim ?p .\n" +
        "  ?x rdfs:label ?label .\n" +
        "  filter(lang(?label) = 'en')\n" +
        " }group by ?p";
      sparqlQuery2 = "select ?p (count(?o) as ?cnt) where {\n" +
        "?o ?p wd:" + subjectID + ". \n" +
        "?x wikibase:directClaim ?p .\n" +
        "  ?x rdfs:label ?label .\n" +
        "  filter(lang(?label) = 'en')\n" +
        " }group by ?p";
    }
    else {
      endpointUrl = 'http://dbpedia.org/sparql';
      if (option === 'dbpedia_raw'){
        sparqlQuery1 = "select ?p (count(?o) as ?cnt) where {\n" +
          "<http://dbpedia.org/resource/"  + subjectID + "> ?p ?o.\n" +
          "filter(regex(str(?p), 'http://dbpedia.org/property/'))}";
        sparqlQuery2 = "select ?p (count(?o) as ?cnt) where {\n" +
          "?o ?p <http://dbpedia.org/resource/"  + subjectID + ">.\n" +
          "filter(regex(str(?p), 'http://dbpedia.org/property/'))}";
      } 
      else {
        sparqlQuery1 = "select ?p (count(?o) as ?cnt) where {\n" +
          "<http://dbpedia.org/resource/"  + subjectID + "> ?p ?o.\n" +
          "filter(regex(str(?p), 'http://dbpedia.org/ontology/'))}";
        sparqlQuery2 = "select ?p (count(?o) as ?cnt) where {\n" +
          "?o ?p <http://dbpedia.org/resource/"  + subjectID + ">.\n" +
          "filter(regex(str(?p), 'http://dbpedia.org/ontology/'))}";
      }
    }
    
    if (!$.isEmptyObject($('#subject').data())){
      if ($('#subject').data('sparql') !== sparqlQuery1 && $('#subject').data('sparqlinv') !== sparqlQuery2){
        emptyPredOrdering();
        // console.log('empty emptyPredOrdering');
        // $.when(makeSPARQLQuery( endpointUrl, sparqlQuery1, function( data ) {
        //   addInstantiations(data);
        //   $('#subject').data('sparql', sparqlQuery1);
        // }),
        // makeSPARQLQuery( endpointUrl, sparqlQuery2, function( data ) {
        //   addInstantiations(data, '_inv');
        //   $('#subject').data('sparqlinv', sparqlQuery2);
        // })).then(sortedPredAutocomplete());
      }
      else {
        return;
      }
    }
    // else {
    makeSPARQLQuery( endpointUrl, sparqlQuery1, function( data ) {
      addInstantiations(data);
      $('#subject').data('sparql', sparqlQuery1);
    });
    makeSPARQLQuery( endpointUrl, sparqlQuery2, function( data ) {
      addInstantiations(data, ' (inv)');
      $('#subject').data('sparqlinv', sparqlQuery2);
    });
    // .then(sortedPredAutocomplete());
    // }
  }
}

// ******************************** on document ready **************************************//
$(document).ready(function () {
  // ******************************** #home predicate events **************************************//
  // populate default predicate options (Wikidata) 
  $("#predicate").predautocomplete();
  
  // on active input in predicate box
  $("#predicate").on('input change', function () {
    // set subject ID on proper matching input
    var selected = $('option[value="'+$(this).val()+'"]').attr('pred-key');
    if ($(this).val() !== '' && selected in predicateIDlist) {
      predicateID = selected;
    }
    else {
      predicateID = '';
    }
  });
  // ******************************** #home subject events **************************************//
  // Empty dropdown content if no input is given
  $("#subject").blur(function () {
    if ($(this).val() === ''){
      $('#subentities').empty();
      subjectIDlist = {};
      subjectID = '';
      $('#subjectID').removeData();
    }
  });

  // on active input in subject box
  $("#subject").on('input', function () {    
  // disable object if object input is non-empty
    var val = $(this).val();
    if (val !== '') {
      // $("#object").prop('disabled', true);
      // call for autocomplete options depending on KB option
      // set subject ID on proper matching input
      if (val !== '' && option === 'wikidata') {
        if (val.split(':')[0] in subjectIDlist){
          subjectID = subjectIDlist[val.split(':')[0]];
          // when -then does not work
          // $.when(order_predicates()).then(sortedPredAutocomplete());
          order_predicates()
        }
        else {
          $(this).wdautocomplete(subentities, subjectIDlist, val);
        }
      }
      else if (val !== '' && (option === 'dbpedia_raw' || option === 'dbpedia_mapped')){
        if (val in subjectIDlist) {
          subjectID = subjectIDlist[$(this).val()];
          subjectID = subjectID.split('/');
          subjectID = subjectID[subjectID.length-1];
          // when -then does not work
          // $.when(order_predicates(option)).then(sortedPredAutocomplete());
          order_predicates();
        }
        else {
          $(this).dbpautocomplete(subentities, subjectIDlist, val);
        }
      }
      else {
        subjectID = '';
        $('#subject').removeData();
      }
    }
    return;
  });
  // ******************************** KB selection events **************************************//
  // changes made on selecting a KB preference
  $("#WD-btn").click(function () {
    if (option !== 'wikidata') {
      // refresh options when KB changes
      result_refresh();
      form_refresh();
    }
    option = 'wikidata';
    change_kb_highlight("#WD-btn", "#DBPr-btn", "#DBPm-btn");    
    $("#predicate").predautocomplete();
  });
  $("#DBPr-btn").click(function () {
    if (option !== 'dbpedia_raw') {
      // refresh options when KB changes
      result_refresh();
      form_refresh();
    }
    option = 'dbpedia_raw';
    change_kb_highlight("#DBPr-btn", "#WD-btn", "#DBPm-btn");
    $("#predicate").predautocomplete();
  });
  $("#DBPm-btn").click(function () {
    if (option !== 'dbpedia_mapped') {
      // refresh options when KB changes
      result_refresh();
      form_refresh();
    }
    option = 'dbpedia_mapped';    
    change_kb_highlight("#DBPm-btn", "#WD-btn", "#DBPr-btn");
    $("#predicate").predautocomplete();
  });
  // ******************************** spo form refresh events **************************************//
  $("#spoRefresh").click(function () {
    option = 'wikidata';
    change_kb_highlight();
    $.when(form_refresh(), result_refresh()).then($("#predicate").predautocomplete());
    // console.log(predicateIDlist);
  });
  // ******************************** query events **************************************//
  // send query parameters to the server
  $("#query").click(function () {
    console.log('sub: '+subjectID+'\npred: '+predicateID+'\noption: '+option);
    // console.log(subjectIDlist);
    // console.log(objectIDlist);
    // display warning message
    if (subjectID.length === 0 && predicateID.length === 0){
      displayinfo("<div class='alert alert-danger alert-dismissible'><strong>Error!</strong> Until CounQER learns telepathy empty fields are not allowed :) <button type='button' class='close' data-dismiss='alert' aria-label='Close'> <span aria-hidden='true'>&times;</span> </button></div>");
      // $('#formalert').show();
    }
    else if (subjectID.length === 0){
      displayinfo("<div class='alert alert-danger alert-dismissible'><strong>Error!</strong> Entity field cannot be empty! <button type='button' class='close' data-dismiss='alert' aria-label='Close'> <span aria-hidden='true'>&times;</span> </button></div>");
    }
    else if (predicateID.length === 0){
      displayinfo("<div class='alert alert-danger alert-dismissible'><strong>Error!</strong> Predicate field cannot be empty! <button type='button' class='close' data-dismiss='alert' aria-label='Close'> <span aria-hidden='true'>&times;</span> </button></div>");
    }
    else{  
      $.when(result_refresh()).then(displayinfo(waitmsg));
      $.ajax({
        type: 'GET',
        url: flaskurl+'spoquery',
        contentType: 'application/json',
        dataType: 'json',
        data: {
          'option': option,
          'subject': subjectID,
          'predicate': predicateID
          // 'object': objectID 
        },
        success: function(result, status){
          // console.log(result);
          // console.log(status);
          displayinfo(endmsg);
          displayresponse(result);
        },
        error: function(){
          displayinfo(errmsg);
          console.log('error in flask get');
        }
      }); 
    }
  });
  // hide alert meassages
  $("[data-hide]").on("click", function(){
    $("#" + $(this).attr("data-hide")).hide();
    // -or-, see below
    // $(this).closest("." + $(this).attr("data-hide")).hide()
  });

  // ******************************** pre-defined queries ******************************//
  $('#wd_eg_1').on('click', function () {
    var payload = {
      subject: "Microsoft",
      subjectID: "Q2283",
      predicate: "P1128: employees",
      // object: "",
      kbname: 'wikidata'
    };
    samplequeries(payload);
  });
  $('#dbpm_eg_1').on('click', function () {
    var payload = {
      subject: "Bundestag",
      subjectID: "Bundestag",
      predicate: "dbo: number of members",
      // object: "",
      kbname: 'dbpedia_mapped'
    };
    samplequeries(payload);
  });
  $('#dbpr_eg_1').on('click', function () {
    var payload = {
      subject: "Leander Paes",
      subjectID: "Leander_Paes",
      predicate: "dbp: gold (inv)",
      // object: "",
      kbname: 'dbpedia_raw'
    };
    samplequeries(payload);
  });
  $('#wd_ideal_1').on('click', function () {
    var payload = {
      subject: "James A. Garfield",
      subjectID: "Q34597",
      predicate: "P40: child",
      // object: "",
      kbname: 'wikidata'
    };
    samplequeries(payload);
  });
  $('#wd_ideal_2').on('click', function () {
    var payload = {
      subject: "World War I",
      subjectID: "Q361",
      predicate: "P1120: number of deaths",
      // object: "",
      kbname: 'wikidata'
    };
    samplequeries(payload);
  });
  $('#wd_ideal_3').on('click', function () {
    var payload = {
      subject: "New York: state of the United States of America",
      subjectID: "Q1384",
      predicate: "P1082: population",
      // object: "",
      kbname: 'wikidata'
    };
    samplequeries(payload);
  });
  $('#dbpm_ideal_1').on('click', function () {
    var payload = {
      subject: "Google",
      subjectID: "Google",
      predicate: "dbo: employer (inv)",
      // object: "",
      kbname: 'dbpedia_mapped'
    };
    samplequeries(payload);
  });
  $('#dbpm_ideal_2').on('click', function () {
    var payload = {
      subject: "Kolkata",
      subjectID: "Kolkata",
      predicate: "dbo: population total",
      // object: "",
      kbname: 'dbpedia_mapped'
    };
    samplequeries(payload);
  });
  // ******************************** predicate button click events ******************************//
  // $('#p1').on('click', function () {
  //   console.log('p1 clicked!!: ', $(this).html());
  //   var sID, sLabel, pID;
  //   if (option == 'wikidata'){
  //     sID = $('#s1 a').eq(1).attr('href').split('http://wikidata.org/entity/').pop();
  //   }
  //   else {
  //     sID = $('#s1 a').eq(1).attr('href').split('http://dbpedia.org/resource/').pop();
  //   }
  //   pID = $('#p1').text();
  //   if (pID.endsWith('-1')){
  //     pID = pID.split('-1').shift() + ' (inv)';
  //   }
  //   sLabel = $('#s1 a').eq(1).text();
  //   var payload = {
  //     subject: sLabel,
  //     subjectID: sID,
  //     predicate: pID,
  //     kbname: option
  //   };
  //   // console.log(payload);
  //   samplequeries(payload);
  // });

  // requires event delegation for dynamically added tags
  $('.second').on('click', '.p2', function () {
    console.log('p2 clicked!!: ',$(this).html());
    var sID, sLabel, pID;
    if (option == 'wikidata'){
      sID = $(this).parent().siblings(".s2").find('a').eq(1).attr('href').split('http://wikidata.org/entity/').pop();
    }
    else {
      sID = $(this).parent().siblings(".s2").find('a').eq(1).attr('href').split('http://dbpedia.org/resource/').pop();
    }
    pID = $(this).text();
    if (pID.endsWith('-1')){
      pID = pID.split('-1').shift() + ' (inv)';
    }
    sLabel = $(this).parent().siblings(".s2").find('a').eq(1).text();
    var payload = {
      subject: sLabel,
      subjectID: sID,
      predicate: pID,
      kbname: option
    };
    samplequeries(payload);
  });

  //  ******************************* nav controls ********************************//
  $('#navbar').on('click', 'a', function () {
    $('#navbar .active').removeClass('active');
    $(this).addClass('active');
    if ($(this).attr('href') == '#topalign'){
      $('#topalign').show();
      $('#spo').hide();
    }
    else {
      $('#topalign').hide();
      $('#spo').show();
    }
  });

  //  ******************************* nav controls return to top ********************************//
  $('#footerReturn').click(function () {
    $('#navbar .active').removeClass('active');
    $('#navbar > li > a').first().addClass('active');
    $('#topalign').hide();
    $('#spo').show();
  });

  // ******************************* alignment tab click *************************** //
  $("#nav_topalign").on('click', 'a', function () {
    var path;
    var kb_name = $(this).html();
    
    if (kb_name === "Wikidata" && $("#tbl_wd_topalign tr").length <= 1){
      $.ajax({
        type: 'GET',
        url : flaskurl+'getalignments',
        dataType: 'text',
        data: {'kbname': 'wikidata'},
        success: function(result, status){
          if ($.isEmptyObject(wd_labels)){
            $.when(get_wd_labels()).then(fill_alignment_table(result, '#tbl_wd_topalign', 'wd'));
          }
          else {
            fill_alignment_table(result, '#tbl_wd_topalign', 'wd');
          }          
        },
        error: function(){
          console.log("Couldn't load WD alignment csv file :(");
        },
        cache: false
      });
    }
    else if (kb_name == 'DBpedia raw' && $("#tbl_dbpr_topalign tr").length <= 1){
      $.ajax({
        type: 'GET',
        url : flaskurl+'getalignments',
        dataType: 'text',
        data: {'kbname': 'dbpedia_raw'},
        success: function(result, status){
          fill_alignment_table(result, '#tbl_dbpr_topalign', 'dbp');
        },
        error: function(){
          console.log("Couldn't load DBPr alignment csv file :(");
        },
        cache: false
      });
    }
    else if (kb_name == 'DBpedia mapped' && $("#tbl_dbpm_topalign tr").length <= 1) {
      $.ajax({
        type: 'GET',
        url : flaskurl+'getalignments',
        dataType: 'text',
        data: {'kbname': 'dbpedia_mapped'},
        success: function(result, status){
          fill_alignment_table(result, '#tbl_dbpm_topalign', 'dbo');
        },
        error: function(){
          console.log("Couldn't load DBPm alignment csv file :(");
        },
        cache: false
      });
    }
    else if (kb_name == 'Freebase' && $("#tbl_fb_topalign tr").length <= 1) {
      $.ajax({
        type: 'GET',
        url : flaskurl+'getalignments',
        dataType: 'text',
        data: {'kbname': 'freebase'},
        success: function(result, status){
          fill_alignment_table(result, '#tbl_fb_topalign', 'fb');
        },
        error: function(){
          console.log("Couldn't load DBPm alignment csv file :(");
        },
        cache: false
      });
    }
  });

});