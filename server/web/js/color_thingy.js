function color_thingy_t(topbar,canvas,controls,picker,sender)
{
	this.topbar=topbar;
	this.canvas=canvas;
	this.controls=controls;
	this.picker=picker;
	this.sender=sender;
	this.ctx=canvas.getContext('2d');
	this.border_size=1;
	this.canvas.style.border='black solid '+this.border_size+'px';
	this.x_cells=8;
	this.y_cells=8;
	this.is_down=false;
	this.frame=
	[
		[[255,0,0],[0,255,0],[255,0,0],[0,255,0],[255,0,0],[0,255,0],[255,0,0],[0,255,0]],
		[[0,255,0],[255,0,0],[0,255,0],[255,0,0],[0,255,0],[255,0,0],[0,255,0],[255,0,0]],
		[[255,0,0],[0,255,0],[255,0,0],[0,255,0],[255,0,0],[0,255,0],[255,0,0],[0,255,0]],
		[[0,255,0],[255,0,0],[0,255,0],[255,0,0],[0,255,0],[255,0,0],[0,255,0],[255,0,0]],
		[[255,0,0],[0,255,0],[255,0,0],[0,255,0],[255,0,0],[0,255,0],[255,0,0],[0,255,0]],
		[[0,255,0],[255,0,0],[0,255,0],[255,0,0],[0,255,0],[255,0,0],[0,255,0],[255,0,0]],
		[[255,0,0],[0,255,0],[255,0,0],[0,255,0],[255,0,0],[0,255,0],[255,0,0],[0,255,0]],
		[[0,255,0],[255,0,0],[0,255,0],[255,0,0],[0,255,0],[255,0,0],[0,255,0],[255,0,0]]
	];

	var _this=this;
	window.addEventListener('resize',function(evt){_this.resize(evt);});
	window.addEventListener('orientationchange',function(evt){_this.resize(evt);});

	this.sender.addEventListener('click',function(evt)
	{
		if(_this.valid_frame())
		{
			_this.xhr(JSON.stringify(_this.frame),null,
			function(error)
			{
				console.log(error);
			});
		}
	});

	this.canvas.addEventListener('mousedown',function(evt){_this.set_down(evt);});
	this.canvas.addEventListener('touchstart',function(evt){_this.set_down(evt);});
	window.addEventListener('mouseup',function(evt){_this.set_up(evt);});
	window.addEventListener('touchend',function(evt){_this.set_up(evt);});
	window.addEventListener('touchcancel',function(evt){_this.set_up(evt);});
	window.addEventListener('touchleave',function(evt){_this.set_up(evt);});
	this.canvas.addEventListener('mousemove',function(evt){_this.draw(evt);});
	this.canvas.addEventListener('touchmove',function(evt){_this.draw(evt);});

	this.xhr('',function(data)
	{
		var old_frame=_this.frame;
		_this.frame=JSON.parse(data);
		if(!_this.valid_frame())
			_this.frame=old_frame;
		_this.resize();
	},
	function(error)
	{
		_this.resize();
		console.log(error);
	},
	'GET','?get_frame');
}

color_thingy_t.prototype.calc_canvas=function()
{
	var props=
	{
		x:this.canvas.offsetLeft,
		y:this.canvas.offsetTop,
		width:this.canvas.offsetWidth-this.border_size*2,
		height:this.canvas.offsetHeight-this.border_size*2,
		cell_w:this.canvas.offsetWidth/this.x_cells,
		cell_h:this.canvas.offsetHeight/this.y_cells
	};
	return props;
}

color_thingy_t.prototype.resize=function()
{
	var height=window.innerHeight-this.topbar.offsetHeight-this.controls.offsetHeight;
	if(height<120)
		height=window.innerHeight;
	this.canvas.style.width=this.canvas.style.height=this.canvas.height=this.canvas.width=height;
	this.controls.style.width=height;
	this.draw_frame();
}

color_thingy_t.prototype.set_down=function(evt)
{
	this.is_down=true;
	this.draw(evt);
}

color_thingy_t.prototype.set_up=function()
{
	this.is_down=false;
	this.draw_frame();
}

color_thingy_t.prototype.draw=function(evt)
{
	if(!this.is_down||(evt.touches&&evt.touches.length==0))
		return false;
	if(evt.touches)
		evt=evt.touches[0];
	var props=this.calc_canvas();
	var x=Math.floor((window.scrollX+evt.clientX-props.x+this.border_size)/props.cell_w);
	var y=Math.floor((window.scrollY+evt.clientY-props.y+this.border_size)/props.cell_h);
	if(x>=this.x_cells)
		x=this.x_cells-1;
	if(x<0)
		x=0;
	if(y>=this.y_cells)
		y=this.y_cells-1;
	if(y<0)
		y=0;
	this.frame[y][x]=this.rgb_from_html(this.picker.value);
	this.draw_frame();
}

color_thingy_t.prototype.valid_frame=function()
{
	if(this.frame.length!=this.y_cells)
		return false;
	for(var yy=0;yy<this.y_cells;++yy)
	{
		if(this.frame[yy].length!=this.x_cells)
			return false;
		for(var xx=0;xx<this.x_cells;++xx)
			if(this.frame[yy][xx].length!=3)
				return false;
	}
	return true;
}

color_thingy_t.prototype.rgb_arr_to_css=function(col)
{
	return 'rgb('+col[0]+','+col[1]+','+col[2]+')';
}

color_thingy_t.prototype.rgb_from_html=function(col)
{
	if(col.length!=7||col[0]!='#')
		return [0,0,0];
	var rgb_col=
	[
		parseInt(col.substr(1,2),16),
		parseInt(col.substr(3,2),16),
		parseInt(col.substr(5,2),16)
	];
	return rgb_col;
}

color_thingy_t.prototype.draw_frame=function()
{
	if(!this.valid_frame())
	{
		console.log('Invalid frame!');
		return;
	}
	var props=this.calc_canvas();
	this.ctx.clearRect(0,0,this.canvas.width,this.canvas.height);
	for(var yy=0;yy<this.y_cells;++yy)
		for(var xx=0;xx<this.x_cells;++xx)
		{
			this.ctx.strokeStyle=this.ctx.fillStyle=this.rgb_arr_to_css(this.frame[yy][xx]);
			this.ctx.fillRect(xx*props.cell_w,yy*props.cell_h,
				props.cell_w,props.cell_h);
			this.ctx.strokeRect(xx*props.cell_w,yy*props.cell_h,
				props.cell_w,props.cell_h);
		}
}

color_thingy_t.prototype.xhr=function(data,onsuccess,onerror,method,request)
{
	if(!method)
		method='POST';
	if(!request)
		request='';
	var xmlhttp=new XMLHttpRequest();
	xmlhttp.onreadystatechange=function()
	{
		if(xmlhttp.readyState==4)
		{
			if(xmlhttp.status==200)
			{
				if(onsuccess)
					onsuccess(xmlhttp.responseText);
			}
			else
			{
				onerror('Response '+xmlhttp.status);
			}
		}
	};
	xmlhttp.open(method,request,true);
	xmlhttp.send(data);
}
