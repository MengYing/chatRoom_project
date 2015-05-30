var msg_controller = new function(){
	var thisObj = this;
	//TODO: bind click event
	return thisObj = {
		init : function(){
			$(".msg").each(function(){
				$(this).bind("click",function(){
					showBar($(this));
				});
			});
		},
		enterMessage : function(event){
			if(event.keyCode == 13){
				var str = $("#input_msg").val();
				var room = parseInt($("#chat_header").attr("room_id"));
				$.post("/chat/"+str, {room:room})
					.done(function(data){
						var direction = "left";
						var converse_id = data.record_id;
						var score = data.score;
						addMessage(converse_id,str,direction,score);
						$("#input_msg").val("");
					})
					.fail(function(){
						alert('fail to submit the message!');
					});
			}
		},
		updateMsgColor : function(converse_id,point){
			var color = getColor(point);
			var div = $(".msg[chat_id='" + converse_id + "']");
			$(div).css("color",color);
		},
		modifyMsgColor : function(){
			//user modify the color => post to server
			$.post();
		}
	};

	function print(str){
		console.log(str);
	}
	function getColor(point){
		return "red"
	}

	function addMessage(converse_id,str,direction,point){
		var color = getColor(point);
		var output = getMessageDiv(str,color,direction,converse_id);
		$('#chat_area').append(output);
		$('.msg[chat_id="' + converse_id + '"]').bind("click",function(){
			showBar($(this));
		});
	}

	//handle the block:msg
	function getMessageDiv(str,color,direction,converse_id){
		var div = '<div class="msg_container" align="' + direction + '" chat_id ="' + converse_id +'">';
		var img = '<img src="static/images/sample1.jpg" class="head">';
		var span = setMessageContent(direction,str);
		if(direction == "left")
			div = $(div).append(img).append(span);
		else
			div = $(div).append(span);
		return div;
	}
	//handle elements in block:msg
	function setMessageContent(direction,str){
		var span = '<span class="msg_text" position="' + direction + '" align="left"></span>'
		return $(span).text(str);
	}
	function showBar(obj){
		$(obj).children(".msg_color_set").show();
		$(obj).unbind("click");
		$(obj).bind("click",function(){
			hideBar($(obj));
		});
	}
	function hideBar(obj){
		$(obj).children(".msg_color_set").hide();
		$(obj).unbind("click");
		$(obj).bind("click",function(){
			showBar($(obj));
		});
	}
	function panelUserSetPoint(){
		var block = '<div></div>';
		block = $(block).addClass("msg_color_set").css("display","none").append("lalala");
		return block
	}
};