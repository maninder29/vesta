function isVideo(filename) {
	if(filename.split('/')[0] == 'video') return true;
	return false;
}
function isImage(filename) {
	if(filename.split('/')[0] == 'image') return true;
	return false;
}
function dataURItoBlob(dataURI) {
    var byteString;
    if (dataURI.split(',')[0].indexOf('base64') >= 0)
        byteString = atob(dataURI.split(',')[1]);
    else
        byteString = unescape(dataURI.split(',')[1]);
    var mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];
    var ia = new Uint8Array(byteString.length);
    for (var i = 0; i < byteString.length; i++) {
        ia[i] = byteString.charCodeAt(i);
    }

    return new Blob([ia], {type:mimeString});
}
var canvas = $( '<canvas class="snapshot-generator"></canvas>' ).appendTo(document.body)[0];
var video = $( '<video muted class="snapshot-generator"></video>' ).appendTo(document.body);
error = $('#error');
thumb = $('#thumb');
$('#id_media').change(function(){
	if (this.files && this.files[0]) {
		var file = this.files[0];
		if(file.size > 52428800){
			$('#submit').addClass('disabled');
			error.text('Maximum file size allowed is 50MB');
			error.fadeIn();
		}
		else{
			$('#submit').removeClass('disabled');
			error.fadeOut();
		}
		if(isVideo(file.type)){
			fileURL = URL.createObjectURL(file);
			var events_fired = 0;
			video.one('loadedmetadata loadeddata suspend', function() {
				if(++events_fired == 3) {
					video.one('seeked', function() {
						canvas.height = this.videoHeight;
						canvas.width = this.videoWidth;
						canvas.getContext('2d').drawImage(this, 0, 0);
						var snapshot = canvas.toDataURL('image/jpeg');
						thumb.attr('src', snapshot).fadeIn();
						$('[name=thumbnail]').val(snapshot);
						video.remove();
						canvas.remove();
					}).prop('currentTime', 2);
				}
			}).prop('src', fileURL);
		}
		else if(isImage(file.type)){
			var reader = new FileReader();
			image = thumb;
			reader.onload = function (e) {
			  image.attr("src", e.target.result);
			}
			reader.readAsDataURL(file);
			image.fadeIn();
		}
		else{
			thumb.attr('src', '');
			$('#submit').addClass('disabled');
			error.text('Only image/video files are allowed');
			error.fadeIn();
		}
	}
})
btn = $('#id_media');
$('#image-upload').click(function(event){
	event.preventDefault();
	btn.attr('accept', 'image/*');
	btn.click();
})
$('#video-upload').click(function(event){
	event.preventDefault();
	btn.attr('accept', 'video/*');
	btn.click();
})