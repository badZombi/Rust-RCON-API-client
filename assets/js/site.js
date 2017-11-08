$( document ).ready(function() {
  $('.player-inner').click(function(){
    $('.player-inner').removeClass("player-selected");
    var player = $(this).attr('data-id');
    $(this).addClass("player-selected");

    console.log(player);
  });

  $('.item-inner').click(function(){
    $('.item-inner').removeClass("item-selected");
    var item = $(this).attr('data-string');
    $(this).addClass("item-selected");

    console.log(item);
  });
});
