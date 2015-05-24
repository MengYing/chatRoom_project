var msg_controller = new function(){
	var thisObj = this;
	//TODO: bind click event
	return thisObj = {
		addMessage : function(converse_id,str,direction,point){
			var color = getColor(point);
			var output = getMessageDiv(str,color,direction,converse_id);
			$('#chat_area').append(output);
		},
		updateMsgColor : function(converse_id,point){
			var color = getColor(point);
			var div = $(".msg[chat_id='" + converse_id + "']");
			$(div).css("color",color)
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
	function getMessageDiv(str,color,direction,converse_id){
		var div = '<div></div>';
		var style = {"height":"auto", "background-color":"green", "color":"red"};
		var attr = {"chat_id":converse_id, "position":direction};
		div = $(div).addClass("msg").attr(attr).css(style);
		return setMessageContent(div,str);
	}
	function setMessageContent(div,str){
		// TODO: handle span
		return $(div).append(str);
	}
	function bindClickEvent(){

	}
};