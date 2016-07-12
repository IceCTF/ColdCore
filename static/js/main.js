$( document ).ready(function() {
  $('select').material_select();

  if($("#country").length)
  {
    $("#country").change(function(e) {
      if($("#country").val() == "ISL")
          $("#prize-info").show("slow");
      else
          $("#prize-info").hide("slow");

    });
  }

});
