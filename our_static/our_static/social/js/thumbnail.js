var thumbnail = (function()
{
	var textField, thumbnailSection;

	function sendRequest()
	{
		$.ajax({
			url : '/thumbnail',
			method : 'POST',
			data: {'text' : textField.value},
			dataType: "json",
			success: updateStatus,
		});
	}

	function updateStatus(data)
	{
		if(data.match == 'false')
		{
			thumbnailSection.style.display = 'none';
		}

		else
		{
			console.log(data.data);
			thumbnailSection.style.display = 'block';
			var image = thumbnailSection.children[0];
			var div = thumbnailSection.children[1];
			var p = thumbnailSection.children[2];
			var a = thumbnailSection.parentNode;

			image.setAttribute('src', data.data.image);
			div.innerHTML = data.data.title;
			p.innerHTML = data.data.description;
			a.setAttribute('href', data.data.url);
			a.setAttribute('target', 'new');
		}
	}

	function init(obj)
	{
		textField = document.getElementById(obj.textField);
		thumbnailSection = document.getElementById(obj.thumbnail);
		if(textField) textField.addEventListener('keyup', sendRequest);
	}

	return {
		'init' : init,
	};

})();