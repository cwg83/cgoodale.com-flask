$(".animatebtn").on("click", function(){
    $('span,header > a').removeClass('animated'); setTimeout(function() { 
    $('span,header > a').addClass('animated'); }, 2);
});