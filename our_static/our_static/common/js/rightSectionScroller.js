var rightSectionScroller = (function()
{
	var list, height, styles;

	function slideUp(){
		list.push(list.shift());

		for(var i = 0; i < list.length; i++){
			list[i].style.zIndex = (i == 0 ? 1500 : 2000);
			list[i].style.top = styles[i] + 'px';
			list[i].style.transition = 	'1s';
		}
	}

	function createStyles(){
		var temp = -height;

		for(var i = 0; i < list.length; i++, temp += height)
			styles.push(temp);

		for(var i = 0; i < list.length; i++){
			list[i].style.zIndex = (i == 0 ? 1500 : 2000);
			list[i].style.top = styles[i] + 'px';
		}
	}
	
	function init(obj)
	{
		height = 230;
		styles = [];
		list = document.querySelector(obj.list);
		list.style.height = obj.length*height + 'px';
		list = list.children;
		createStyles();

		var temp = [];
		for(var i = 0; i < list.length; i++)
			temp.push(list[i]);
		list = temp;
		setInterval(slideUp, obj.time);
	}

	return {
		'init' : init,
	};
})();