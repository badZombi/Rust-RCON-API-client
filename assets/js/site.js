$( document ).ready(function() {

  $(document.body).on( 'click', '.player-inner', function () {
    $('.player-inner').removeClass("player-selected");
    var player = $(this).attr('data-id');
    var playername = $(this).attr('data-name');
    $(this).addClass("player-selected");
    $('#player').val(player);
    $('#playername').html(playername);
    console.log(player);
  });


  $('.item-inner').click(function(){
    $('.item-inner').removeClass("item-selected");
    var item = $(this).attr('data-string');
    var itemname = $(this).attr('data-name');
    $(this).addClass("item-selected");
    $('#item').val(item);
    $('#itemname').html(itemname);
    console.log(item);
  });

  $("#itemcount").change(function(){
    var count = $(this).val();
    $('#count').val(count);

    console.log(count);
  });
});

function removePlayer(playerId){
  console.log(playerId);
  $("#player-" + playerId).remove()
}

function newPlayer(playerId, playerName, avatar){
  console.log(playerId);

  if($("#player-" + playerId).length == 0) {
    playerTemplate = $("#player-template").clone();

    playerTemplate.attr("id","player-" + playerId);
    playerTemplate.find('.player-inner').attr("data-id",playerId);
    playerTemplate.find('.player-inner').attr("data-name",playerName);
    playerTemplate.find('img').attr("src",avatar);

    playerTemplate.find('h4').html(playerName);
    playerTemplate.appendTo("#cbox");
    playerTemplate.show();
  }


}

