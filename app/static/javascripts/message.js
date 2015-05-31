var msg_controller = new function(){
	var thisObj = this;
	var room = '';
	var sender_id;
	var socket;
	//TODO: bind click event
	return thisObj = {
		init : function(){
			loginWebsocket();
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
						var direction = "right";
						var chat_id = data.chat_id;
						var score = data.score;
						addMessage(chat_id,str,direction,score);
						$("#input_msg").val("");
						//send msg to other one
						socket.emit("set msg",{sender: sender_id, room:room, chat_id:chat_id, msg:str, score:score})
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
	function loginWebsocket(){
		console.log("connect to websocket");
		socket = io.connect('http://127.0.0.1:5000/');
		socket.on('connect', function() {
            socket.emit('join room', {room: 1});
        });
		socket.on('set room', function(data) {
            room = data.room;
            sender_id = data.sender;
            console.log(room,sender_id);
        });
        setSocketEvent();
	}
	function setSocketEvent(){
		socket.on('set msg', function(data) {
			console.log(data)
			if(data.sender != sender_id)
            	addMessage(data.id,data.msg,"left",data.score)
        });
	}
};
function testsocket(){
	socket.emit('my event', {data: "123456"});
}