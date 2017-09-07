var videoPlugin = (function()
{
	var video, list, urls, current;

	function upDateDOM(){
		console.log(current);
		video.src = list.children[current].getAttribute('url');
		video.play();

		for(var i = 0; i < list.children.length; i++){
			var currentClass = 'common-video ';
			currentClass += (i == current ? 'active-video' : 'inactive-video');
			list.children[i].setAttribute('class', currentClass);
		}		
	}

	function nextVideo(){
		current = (current + 1)%list.children.length;
		upDateDOM();
	}

	function previousVideo(){
		current = (current - 1 + list.children.length)%list.children.length;
		upDateDOM();
	}

	function changeVideo(index){
		current = parseInt(index);
		upDateDOM();
	}

	function createButtons()
	{
		for(var i = 0; i < urls.length; i++)
		{
			var li = document.createElement('li');
			li.setAttribute('url', urls[i]);
			var current = 'common-video ' + (i == 0 ? 'active-video' : 'inactive-video');
			li.setAttribute('class', current);
			li.addEventListener('click', changeVideo.bind(this, i));
			list.appendChild(li);
		}
	}

	function init(obj)
	{
		video = document.getElementById(obj.video);
		list = document.querySelector(obj.list);
		urls = obj.urls;
		current = 0;
		createButtons();
		document.getElementById(obj.next).addEventListener('click', nextVideo);
		document.getElementById(obj.previous).addEventListener('click', previousVideo);
		video.src = list.children[current].getAttribute('url');
	}

	return {
		'init' : init,
	};

})();