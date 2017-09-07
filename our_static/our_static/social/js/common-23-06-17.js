$(document).ready(function(){
  $(".button-collapse").sideNav();
  $('.modal').modal();
  $(".tab").click(function(event){
    window.location=$(this).find('a').attr('href');
  })
  $('video').click(function(){
    this.paused ? this.play() : this.pause();
  })
  $('.post-menu.media-less').each(function(){
    x = $(this);
    h1 = x.siblings('.post-collection').height();
    h2 = x.parent().siblings('.content').height();
    x.parent().siblings('.hidden-div').css('height', (h1-h2-20)+'px');
  })
  $('.post-menu:not(.media-less)').click(function(){
    $(this).siblings('.collection').slideToggle();
  })
  $('.post-menu.media-less').click(function(){
    $(this).siblings('.collection').slideToggle();
    $(this).parent().siblings('.hidden-div').slideToggle();
  })
  $('body').click(function(event){
    postMenus = document.getElementsByClassName('post-collection');
    hiddenDivs = document.getElementsByClassName('hidden-div');
    if(!event.target.matches('.post-menu-i')){
      for (var i = 0; i < postMenus.length; i++) {
        var openDropdown = postMenus[i];
        if (openDropdown.style.display == "block") {
          $(openDropdown).slideToggle();
        }
        var openhiddenDiv = hiddenDivs[i];
        if (openhiddenDiv.style.display == "block") {
          $(openhiddenDiv).slideToggle();
        }
      }
    }
  })
  $('.likebtn').click(function(event){
    event.preventDefault();
    $this=$(this);
    i = $this.find('i');
    i.toggleClass('liked');
    a = $this.siblings('a.like-count');
    current_like_count = parseInt(a.text().split(' ')[0]);
    if(i.hasClass('liked')){
      a.text((current_like_count+1) + ' likes');
    }else{
      a.text((current_like_count-1) + ' likes');
    }
    $.ajax({
      url: $this.attr('href'),
      method: 'GET',
      dataType: 'json',
      failure: function(error){
        Materialize.toast('Something went wrong!!!', 3000, 'rounded');
      }
    })
  })
  $('.likebtnComment').click(function(event){
    event.preventDefault();
    $this=$(this);
    i = $this.find('i');
    i.toggleClass('liked');
    a = $this.siblings('a.comment-like-count');
    current_like_count = parseInt(a.text());
    if(i.hasClass('liked')){
      a.text(current_like_count+1);
    }else{
      a.text(current_like_count-1);
    }
    $.ajax({
      url: $this.attr('href'),
      method: 'GET',
      dataType: 'json',
      failure: function(error){
        Materialize.toast('Something went wrong!!!', 3000, 'rounded');
      }
    })
  })
  $('.like-count').click(function(event){
    event.preventDefault();
    modal = $('#likersModal .modal-content');
    modal.html('');
    $.ajax({
      url: $(this).attr('href'),
      method: 'GET',
      dataType: 'json',
      success: function(data){
        data=data.data;
        if(data.length==0){
          Materialize.toast('No one has liked this post yet<br>Be the first one', 3000, 'rounded');
        }
        else{
          $('#likersModal').modal('open');
          for(var i=0;i<data.length;i++){
            var obj='\
            <div class="row">\
              <div class="liker" style="background-image: url(\''+data[i].dp+'\')"></div>\
              <a class="liker-name" href="/posts/profile/'+data[i].id+'/">'+data[i].name+'</a>\
            </div>'
            modal.append(obj);
          }
        }
      },
      failure: function(error){
        Materialize.toast('Something went wrong!!!', 3000, 'rounded');
      }
    })
  })
  $('.comment-like-count').click(function(event){
    event.preventDefault();
  })
  $('.sharebtn').click(function(event){
    event.preventDefault();
    id = $(this).attr('pid');
    text = $(this).attr('text');
    url="https://www.facebook.com/sharer/sharer.php?app_id=703088589852677&u=http://vestapp.in/posts/"+id+"/";
    $('#fb_share_button').attr('href', url);
    href="https://twitter.com/intent/tweet?text="+text+"&url=http://vestapp.in/posts/"+id+"/&hashtags=vesta";
    $('#twitter_share_button').attr('href', href);
    $('#shareModal').modal('open');
  })
  $('.deletebtn').click(function(event){
    event.preventDefault();
    href=$(this).attr('href');
    $('#confirm-yes').attr('href', href);
    $('#deleteConfirmModal').modal('open');
  })
  
  var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();
  $('.savebtn, .followbtn').click(function(event){
    event.preventDefault();
    $this=$(this);
    $.ajax({
      url: $this.attr('href'),
      method: 'POST',
      data: {'csrfmiddlewaretoken': csrftoken},
      dataType: 'json',
      success: function(data){
        Materialize.toast(data.message, 3000, 'rounded');
        $this.html(data.text);
      },
      failure: function(error){
        Materialize.toast('Something went wrong!!!', 3000, 'rounded');
      }
    })
  })
  $('#searchbtn').click(function(event){
    event.preventDefault();
    $('#search-form').toggle();
  })
  $('#search-form i').click(function(event){
    $('#search-form').toggle();
  })
  $.ajax({
    url: '/posts/all_users/',
    method: 'GET',
    dataType: 'json',
    success: function(data){
      $('input.autocomplete').autocomplete({
        data: data,
        limit: 7,
        onAutocomplete: function(val) {
          $('#search-form').submit();
        },
      });
    },
    failure: function(error){
      Materialize.toast('Something went wrong!!!', 3000, 'rounded');
    }
  })
  // $('#search-form input').keyup(function(event){
  //   query=$('#search-form input').val();
    // $.ajax({
    //   url: '/search/user/'+query+'/',
    //   method: 'POST',
    //   data: {'csrfmiddlewaretoken': csrftoken},
    //   dataType: 'json',
    //   success: function(data){
    //     Materialize.toast(data.message, 3000, 'rounded');
    //     $this.html(data.text);
    //   },
    //   failure: function(error){
    //     Materialize.toast('Something went wrong!!!', 3000, 'rounded');
    //   }
    // })
  // })
  // $('#search-form .collection a').click(function(event){
  //   event.preventDefault();
  //   x=$(this);
  //   $('#search-form input').val(x.text());
  // })
})
