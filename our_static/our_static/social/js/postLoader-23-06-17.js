function initialize(id) {
  // console.log(id);
  $class='.'+id;
  $($class+' video').click(function(){
    this.paused ? this.play() : this.pause();
  })
  $($class+' .post-menu.media-less').each(function(){
    x = $(this);
    h1 = x.siblings('.post-collection').height();
    h2 = x.parent().siblings('.content').height();
    x.parent().siblings('.hidden-div').css('height', (h1-h2-20)+'px');
  })
  $($class+' .post-menu:not(.media-less)').click(function(){
    $(this).siblings('.collection').slideToggle();
  })
  $($class+' .post-menu.media-less').click(function(){
    $(this).siblings('.collection').slideToggle();
    $(this).parent().siblings('.hidden-div').slideToggle();
  })
  $($class+' .likebtn').click(function(event){
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
  $($class+' .like-count').click(function(event){
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
  $($class+' .sharebtn').click(function(event){
    event.preventDefault();
    id = $(this).attr('pid');
    text = $(this).attr('text');
    url="https://www.facebook.com/sharer/sharer.php?app_id=703088589852677&u=https://vestapp.in/posts/"+id+"/";
    $('#fb_share_button').attr('href', url);
    href="https://twitter.com/intent/tweet?text="+text+"&url=https://vestapp.in/posts/"+id+"/&hashtags=vesta";
    $('#twitter_share_button').attr('href', href);
    $('#shareModal').modal('open');
  })
  $($class+' .deletebtn').click(function(event){
    event.preventDefault();
    href=$(this).attr('href');
    $('#confirm-yes').attr('href', href);
    $('#deleteConfirmModal').modal('open');
  })
  
  var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();
  $($class+' .savebtn,'+$class+' .followbtn').click(function(event){
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
  $($class+' .materialboxed').materialbox();
}
postSection = $('#post-section');
postLoader = $('#post-loader');
var visible = true;
function load_pages(category){
  if(checkVisible(postLoader) && visible) {
    visible = false;
    if(postLoader.attr('status') == 'active'){
      $.ajax({
        url : postLoader.attr('url'),
        method : 'GET',
        dataType: "json",
        success: function(data){
          if(data.status == 'deactive'){
            postLoader.attr('status', 'deactive');
            postLoader.css('visibility', 'hidden');
          }else{
            var posts=data.posts;
            for(var i=0 ; i<posts.length ; i++){
              var obj = '\
              <div class="row post '+posts[i].unique_id+'">\
                <div class="col s12">\
                  <a class="btn-floating waves-effect waves-light post-menu ';
                  if(posts[i].flag == 5) obj+='media-less';
                  obj+='"><i class="material-icons post-menu-i">menu</i></a>\
                  <div class="collection post-collection">';
                  if(posts[i].user_status == 1) obj+='\
                    <a href="/posts/timeline/'+posts[i].id+'/edit/" class="collection-item"><i class="fa fa-pencil" aria-hidden="true"></i>Edit</a>\
                    <a href="/posts/timeline/'+posts[i].id+'/delete/" class="collection-item deletebtn"><i class="fa fa-trash" aria-hidden="true"></i>Delete</a>';
                    obj+='<a href="/posts/timeline/'+posts[i].id+'/save/" class="collection-item savebtn"><i class="fa fa-download" aria-hidden="true"></i>Save</a>\
                    <a href="/posts/timeline/'+posts[i].id+'/follow/" class="collection-item followbtn"><i class="fa fa-envelope-open" aria-hidden="true"></i>Discuss</a>\
                  </div>';
                  if(posts[i].flag == 1) obj+='<img src="'+posts[i].media+'" class="materialboxed" style="width: 100%">';
                  else if(posts[i].flag == 2) obj+='<video controls preload="metadata" style="width: 100%;margin-bottom: 42px;"><source src="'+posts[i].media+'" type="video/mp4">Your browser does not support the video tag.</video>';
                  else if(posts[i].flag == 3) obj+='<div class="video-container" style="margin-bottom: 48px;"><iframe src="'+posts[i].embed+'" frameborder="0" allowfullscreen></iframe></div>';
                  else if(posts[i].flag == 4) obj+='\
                    <a class="thumbnail" target="_new" href="'+posts[i].og_link+'">\
                      <div class="row">\
                        <div class="s12">\
                          <div class="row">\
                            <div class="col s12 m6 thumbnail-image" style="background: url('+posts[i].og_image+');"></div>\
                            <div class="col s12 m6" style="color:black">\
                              <h5>'+posts[i].og_title+'</h5>\
                              <p>'+posts[i].og_description+'</p>\
                            </div>\
                          </div>\
                        </div>\
                      </div>\
                    </a>';
                  obj+='<span class="post-name"><a href="/posts/profile/'+posts[i].user_id+'/">'+posts[i].name;
                  if(posts[i].vip == 1) obj+='<i title="Verified profile" class="material-icons vip" style="margin-left:5px">check_circle</i>';
                  obj+='</a>';
                  // if(posts[i].wall_post == 1){
                  //   obj+='\
                  //   <i class="material-icons">play_arrow</i>\
                  //   <a href="/posts/profile/'+posts[i].wall_post_user_id+'/">'+posts[i].wall_post_user_name;
                  //   if(posts[i].wall_post_user_vip == 1) obj+='<i title="Verified profile" class="material-icons vip">check_circle</i>';
                  //   obj+='</a>';
                  // }
                  obj+='</span>\
                </div>\
                <div class="col s12">\
                  <div style="background: url('+posts[i].dp+');"></div>\
                </div>\
                <div class="col s12 content">'+posts[i].content.replace(/\n/g, "<br>");
                if(posts[i].long_post == 1) obj+='... <a href="/posts/'+posts[i].id+'/">read more</a>'
                obj+='</div>\
                <div class="col s12 hidden-div"></div>\
                <div class="col s12">\
                  <a href="/posts/timeline/'+posts[i].id+'/like/" class="likebtn">\
                    <i class="fa fa-heart ';
                    if(posts[i].like_status == 1) obj+='liked';
                    obj+='"></i>\
                  </a>\
                  <a href="/posts/timeline/'+posts[i].id+'/likers/" class="like-count">'+posts[i].likes+' likes</a>\
                  <a class="commentbtn" href="/posts/timeline/'+posts[i].id+'/#comments"><i class="fa fa-comment-o"></i><span>'+posts[i].comments+' comments</span></a>\
                  <a class="sharebtn" pid="timeline/'+posts[i].id+'" text="'+posts[i].text+'" href><i class="fa fa-share-alt"></i>share</a>\
                  <a class="viewbtn" href="javascript:void(0)" title="Number of views"><i class="fa fa-eye"></i><span>'+posts[i].views+'</span></a>\
                </div>\
              </div>';
              postSection.append(obj);
            }
            initialize(posts[0].unique_id);
            // if(profile_user_id)
              // postLoader.attr('url', '/posts/new_'+category+'_list/'+posts[0].unique_id+'/'+profile_user_id);
            // else
              postLoader.attr('url', '/posts/new_'+category+'_list/'+posts[0].unique_id+'/');
          }
          visible = true;
        },
        failure: function(){
          Materialize.toast('Something went wrong!!!', 3000, 'rounded');
        }
      });
    }
  }
}

function checkVisible( elm, eval ) {
  eval = eval || "visible";
  var vpH = $(window).height(), st = $(window).scrollTop(), y = $(elm).offset().top, elementHeight = $(elm).height();
  if (eval == "visible") return ((y < (vpH + st)) && (y > (st - elementHeight)));
  if (eval == "above") return ((y < (vpH + st)));
}