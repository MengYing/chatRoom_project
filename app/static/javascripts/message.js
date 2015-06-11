var socket;
var msg_controller = new function(){
	var thisObj = this;
	var room = '';
	var sender_id;
	//TODO: bind click event
	return thisObj = {
		init : function(){
			loginWebsocket();
			$(".msg_text").each(function(){
				$(this).bind("click",function(){
					showBar($(this));
				});
			});
		},
		enterMessage : function(event){
			if(event.keyCode == 13){
				
				var str = $("#input_msg").val();
                $.post("/chat2/"+str, {room:room})
					.done(function(data){
						var direction = "right";
						var chat_id = data.chat_id;
						var score = data.score;
						var time = data.timeStamp;
                        console.log("come on");
						console.log('i',time);
						//alert("3454566");
						addMessage(chat_id,str,direction,score);
						$("#input_msg").val("");
						//send msg to other one
						socket.emit("set msg",{sender: sender_id, room:room, chat_id:chat_id, msg:str, score:score});
					    //alert("1233");
					    //alert(time.toSting());
					    $.post("/calculateScore/"+str+"/"+time, {room:room})
						    .done(function(data){
							    //alert("hihi");
							    var direction = "right";
							    var chat_id = data.chat_id;
							    var score = data.score;
							    //addMessage(chat_id,str,direction,score);
							    $(".msg_container[chat_id='"+chat_id+"']").children(".msg_text").css("color",setEmotion(score));
						        socket.emit("update color",{sender: sender_id, room:room, chat_id:parseInt(chat_id), score:score});
					        })
						    .fail(function(){
							    alert('fail to submit the calculateScore!');
						    });
					


					})
					.fail(function(){
						alert('fail to submit the message2!');
					});
				
				
				/*
				$.post("/chat/"+str, {room:room})
					.done(function(data){
						var direction = "right";
						var chat_id = data.chat_id;
						var score = data.score;
						addMessage(chat_id,str,direction,score);
						$("#input_msg").val("");
						//send msg to other one
						socket.emit("set msg",{sender: sender_id, room:room, chat_id:chat_id, msg:str, score:score});
					})
					.fail(function(){
						alert('fail to submit the message!');
					});
*/
			}
		},
		updateMsgColor : function(chat_id,score){
			$.post("/modify_value/" + chat_id, {score:score})
			.done(function(data){
				console.log("updateMsgColor111");
				$(".msg_container[chat_id='"+chat_id+"']").children(".msg_text").css("color",setEmotion(score));
				socket.emit("update color",{sender: sender_id, room:room, chat_id:parseInt(chat_id), score:score});
			    
			})
			.fail(function(){
				alert("update failed!");
			});

        
		},
		modifyMsgColor : function(){
			//user modify the color => post to server
			$.post();
		},
		calculateScore : function(event){
			var str = $("#input_msg").val();
			if(event.keyCode == 13){
		        $.post("/calculateScore/"+str, {room:room})
				.done(function(data){
					var direction = "right";
					var chat_id = data.chat_id;
					var score = data.score;
					//addMessage(chat_id,str,direction,score);
					$(".msg_container[chat_id='"+chat_id+"']").children(".msg_text").css("color",setEmotion(score));
				    socket.emit("update color",{sender: sender_id, room:room, chat_id:parseInt(chat_id), score:score});
			    })
				.fail(function(){
					alert('fail to submit the message2!');
				});		

		    }
			
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
		var output = getMessageDiv(str,color,direction,converse_id,point);
		$('#chat_area').append(output);
		$('#chat_area').scrollTop(output.position().top);
		$('.msg_container[chat_id="' + converse_id + '"]').children(".msg_text").bind("click",function(){
			showBar($(this));
		});
	}

	//handle the block:msg
	function getMessageDiv(str,color,direction,converse_id,point){
		var div = '<div class="msg_container" align="' + direction + '" chat_id ="' + converse_id +'">';
		var img = '<img src="static/images/sample1.jpg" class="head">';
		var span = setMessageContent(direction,str,point);
		///str
		var color_bar = setColorBar(direction,converse_id);
		if(direction == "left")
			div = $(div).append(img).append(span);
		else
			div = $(div).append(span).append(color_bar);
		return div;
	}
	//handle elements in block:msg
	function setMessageContent(direction,str,point){
		var span = '<span class="msg_text" position="' + direction + '" align="left"></span>'
		return $(span).text(str).css("color",setEmotion(point));
	}
	function setEmotion(point){
		var color_list = ["#33CC00","#000000","#CC0000","#CC33FF","#0033CC"];
		var color;
		point = parseFloat(point);
		// console.log("point: " + point);
		if(point == 4.0)
			color = color_list[0];
		else if(point == 3.0)
			color = color_list[2];
		else if(point == 2.0)
			color = color_list[3];
		else if(point == 1.0)
			color = color_list[4];
		else
			color = color_list[1];

		return color;
	}
	function setColorBar(direction,chat_id){
		var block = '<div position="' + direction + '"></div>';
		var span = '<span></span>'
		var emotion = {"happy":4.0, "none":0.0, "anger":3.0, "sorry":2.0, "sadness":1.0};
		
		function emocolor(key){
			if(key=="happy") return "#33CC00";
			if(key=="none") return "#000000";
			if(key=="anger") return "#CC0000";
			if(key=="sorry") return "#CC33FF";
			if(key=="sadness") return "#0033CC";
			return "#FF0000";
		}
		
		for(var key in emotion){
			var onclick = "msg_controller.updateMsgColor('" + chat_id + "','" + emotion[key] +"')";
			var tmp = $(span).text(key).css({"margin":"0px 10px","cursor":"pointer","color":emocolor(key)}).attr("onclick",onclick).attr("emotion",key);
			block = $(block).append(tmp);
		}

		block = $(block).addClass("msg_color_set").css("display","none");
		return block
	}
	function showBar(obj){
		$(obj).siblings(".msg_color_set").show();
		$(obj).unbind("click");
		$(obj).bind("click",function(){
			hideBar($(obj));
		});
	}
	function hideBar(obj){
		$(obj).siblings(".msg_color_set").hide();
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
		console.log("Start connecting to websocket");
		u_id = $('#chat_header').attr("u_id");
		room = $('#chat_header').attr("room_id");
		socket = io.connect('http://127.0.0.1:3000/');
		socket.on('connect', function() {
            socket.emit('join room', {room: room, u_id:u_id});
        });
		socket.on('set room', function(data) {
            room = data.room;
            sender_id = data.sender;
            console.log(room,sender_id);
        });
        setSocketEvent();
	}
	function setSocketEvent(){
		console.log("setSocketEvent");
		socket.on('set msg', function(data) {
			console.log(data);
			if(data.sender != sender_id)
            	addMessage(data.chat_id,data.msg,"left",data.score);
        });

        socket.on('update color', function(data) {
        	console.log(data);
        	if(data.sender != sender_id){
        		$(".msg_container[chat_id='" + data.chat_id + "'] .msg_text").css("color",setEmotion(data.score));
        	}
        });

		socket.on('start chat', function(data) {
			var name_list = data["name_hash"];
			var name;
			for(key in name_list){
				if( key != sender_id)
					name = name_list[key];
			}
            $(".msg_title").text("已連線，請開始聊天...");
            $("#friend_list .friend_text").text(name);
        });

        socket.on('quit room',function(data){
        	console.log( sender_id + " quit!");
        	$(".msg_title").text("對方已離開...QAQ");
        });
	}
};
