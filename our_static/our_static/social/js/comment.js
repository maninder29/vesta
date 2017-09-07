$(document).ready(function(){
  url='';
  element='';
  csrftoken = $("[name=csrfmiddlewaretoken]").val();
  $('.comment-update').click(function(event){
    event.preventDefault();
    $this=$(this);
    element=$this.parent().parent();
    element.removeClass('glow');
    url=$this.attr('href');
    text=$this.parent().siblings('p').html();
    textarea=$('#commentUpdateModal textarea');
    textarea.val(text.replace(/<br>/g, "\n").replace(/&nbsp;/g, " "));
    textarea.trigger('autoresize');
    $('#commentUpdateModal').modal('open');
    textarea.focus();
  })
  $('#commentUpdateModal button').click(function(){
    text=$('#commentUpdateModal textarea').val();
    $.ajax({
      url: url,
      method: 'POST',
      data: {
        'content': text,
        'csrfmiddlewaretoken': csrftoken
      },
      dataType: 'json',
      success: function(data){
        element.find('p').html(text.replace(/\n/g, "<br>"));
        element.addClass('glow');
      }
    })
  })
})