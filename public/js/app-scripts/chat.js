var socket = new WebSocket("ws://" + document.location.host + "/websocket");
$( function(){
	fillChannelsList();
	$("#search-input").keyup(fillChannelsList);
	$(".channel").click(selectChannel);
	$("#send-message").click(sendMessage);
	$("#add-channel").click(addChannel);
});

var is_empty = true;

socket.onmessage = function(event){
	var incomingMessage = event.data;
	msg = JSON.parse(incomingMessage);
	
	if(msg['id_channel'] == $("#selected-channel").val()){
		var xmlhttp = getXmlHttp();
		xmlhttp.open('GET', "/username?req="+msg['id_user'], false);
		xmlhttp.send(null);
		name = "";		
		if(xmlhttp.status == 200){
			name = xmlhttp.responseText;
		}
		msgtext = name + ": " + msg['text'];
		addMessage(msgtext);
	}
};

$(window).unload(function (event){
	socket.close();
});

function getXmlHttp(){
   var x = false;
   try {
      x = new XMLHttpRequest();
   }catch(e) {
     try {
        x = new ActiveXObject("Microsoft.XMLHTTP");
     }catch(ex) {
        try {
            req = new ActiveXObject("Msxml2.XMLHTTP");
        }
        catch(e1) {
            x = false;
        }
     }
  }
  return x;
}

function addMessage(text)
{
	if(is_empty)
	{ 
		$("#chat-frame").empty();
		is_empty = false;
	}
	$("#chat-frame").append("<tr><td>"+text+"</td></tr>");
}

function sendMessage()
{
	text = $("#text-message").val();
	idChannel = $("#selected-channel").val();
	
	socket.send('{"id_channel": "'+idChannel+'", "id_user": "'+$("#user-id").val()+'", "text": "'+text+'"}');	
	$("#text-message").val("");
}

function selectChannel()
{
	$("#selected-channel").val( $(this).attr('strid') );
	$("#chat-frame").empty();
	$("#chat-legend").text("Chat: " + $(this).text());

	var xmlhttp = getXmlHttp();
	xmlhttp.open('GET', "/messages?req="+$(this).attr('strid'), false);
	xmlhttp.send(null);
	if(xmlhttp.status == 200)
	{
		response = JSON.parse(xmlhttp.responseText);
		messages = response.messages;
		is_empty = true;
		for(var message in messages)
		{ 
			addMessage(messages[message]); 
			is_empty = false;
		}
		if(is_empty)
		{ addMessage("There are no message in this channel."); }
	}
}

function addChannel(){
	$("#search-input").val("");
	
	if($("#add-channel-input").val() == "")
	{ return; }
	
	channelName = $("#add-channel-input").val()
	var xmlhttp = getXmlHttp();
	xmlhttp.open('GET', "/addchannel?req="+channelName, false);
	xmlhttp.send(null);
	if(xmlhttp.status == 200){	
		$("#add-channel-input").val("")
		fillChannelsList();
	}
}

function fillChannelsList(){
	$("#channels").empty();
	
	var xmlhttp = getXmlHttp();
	
	req = $("#search-input").val();	
	
	if(req == "")
		{ xmlhttp.open('GET', "/channels", false); }
	else
		{ xmlhttp.open('GET', "/channels?req="+req, false); }
	
	xmlhttp.send(null);
	if(xmlhttp.status == 200)
	{ 
		response = JSON.parse(xmlhttp.responseText);
		channels = response.response;
		for(var channel in channels)
		{ $("#channels").append("<li><a class='channel' strid='"+channels[channel].id+"'>"+channels[channel].name+"</li>"); }
		$(".channel").click(selectChannel);
		$(".channel").get(0).click();
}
}
