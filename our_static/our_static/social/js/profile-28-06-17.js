$(document).ready(function(){
  $('#id_dp').change(function(){
    if (this.files && this.files[0]) {
      $('#image-wrapper').show();
      var reader = new FileReader();
      image = $('#image');
      reader.onload = function (e) {
        image.attr("src", e.target.result);
      }
      reader.readAsDataURL(this.files[0]);
    }
  });
  $('.profile-dp img').click(function(event){
    $('.popup-overlay').addClass('popout');
  })
  $('.popup-overlay').click(function(event){
    if(!event.target.matches('.popup')){
      $(this).removeClass('popout');
    }  
  })
})