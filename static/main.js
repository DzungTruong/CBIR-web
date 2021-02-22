// ----- custom js ----- //

// hide initial
$("#searching").hide();
$("#results-table").hide();
$("#error").hide();
$("#apScore").hide();

// global
var url = 'https://storage.googleapis.com/cbirdemo.appspot.com/oxbuild/';
var urlqueries = 'https://storage.cloud.google.com/cbirdemo.appspot.com/queries/all_souls_000013.jpg';
var data = [];


$(function() {

  // sanity check
  console.log( "ready!" );

  // image click
  $(".img").click(function() {

    // empty/hide results
    $("#results").empty();
    $("#results-table").hide();
    $("#error").hide();
    $("#apScore").hide();

    // add active class to clicked picture
    $("#queryImage").find("*").removeClass("active");
    $(this).addClass("active")

    // grab image url
    var image = $(this).attr("src")
    console.log(image)

    // show searching text
    $("#searching").show();
    console.log("searching...")

    // ajax request
    $.ajax({
      type: "POST",
      url: "/search",
      data : { img : image },
      // handle success
      success: function(result) {
        console.log(result.results);
        var data = result.results
        $("#results-table").show();
        // loop through results, append to dom
        for (i = 0; i < data.length; i++) {
          $("#results").append('<tr><th><a href="'+url+data[i]["image"]+'"><img src="'+url+data[i]["image"]+
            '" class="result-img"></a></th><th>'+data[i]['score']+'</th></tr>')
          $("#searching").hide();
        };
        $("#apScore").show();
        document.getElementById("apScore").innerHTML = "AP Score: " + result.ap;
      },
      // handle error
      error: function(error) {
        console.log(error);
        // append to dom
        $("#error").append()
      }
    });

  });

});