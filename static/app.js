/*
Frontend JavaScript engine
Mobile Chat App

Features:
- Authentication
- Messaging
- File upload
- Audio calls
- Video calls
*/


let token = "";

let username = "";

let socket = null;



// WebRTC

let peerConnection = null;

let localStream = null;



const rtcConfig = {

    iceServers: [

        {
            urls:
            "stun:stun.l.google.com:19302"
        }

    ]

};





// ================================
// Register
// ================================

async function register(){


let usernameInput =
document.getElementById("username").value.trim();


let phone =
document.getElementById("phone").value.trim();


let password =
document.getElementById("password").value;



let response =
await fetch("/register",{

method:"POST",

headers:{

"Content-Type":"application/json"

},

body:JSON.stringify({

username:usernameInput,

phone:phone,

password:password

})

});



let result =
await response.json();



document.getElementById("authMessage").innerHTML =
result.message;


}






// ================================
// Login
// ================================

async function login(){


let phone =
document.getElementById("phone").value.trim();



let password =
document.getElementById("password").value;



let response =
await fetch("/login",{

method:"POST",

headers:{

"Content-Type":"application/json"

},

body:JSON.stringify({

phone:phone,

password:password

})

});



let result =
await response.json();



if(result.access_token){


token =
result.access_token;


username =
result.username.trim();



localStorage.setItem(
"token",
token
);



openChat();



}

else{


alert("Login failed");


}


}





// ================================
// Open Chat
// ================================

function openChat(){


document
.getElementById("auth")
.classList
.add("hidden");



document
.getElementById("chat")
.classList
.remove("hidden");



connectSocket();


}






// ================================
// WebSocket
// ================================

function connectSocket(){


let protocol =
window.location.protocol === "https:"
?
"wss://"
:
"ws://";



socket =
new WebSocket(

protocol +

window.location.host +

"/ws/" +

encodeURIComponent(username)

);




socket.onopen=function(){


document.getElementById("status").innerHTML =
"🟢 Online";


};





socket.onmessage = async function(event){


let data =
JSON.parse(event.data);



console.log(data);




if(data.type==="message"){


displayMessage(

data.sender,

data.message

);


}





// incoming call

if(data.type==="call_request"){


let answer =
confirm(

data.sender+
" is calling. Accept?"

);



if(answer){


createPeerConnection();


}


}






if(data.type==="offer"){


await receiveOffer(data);


}






if(data.type==="answer"){


await peerConnection.setRemoteDescription(

new RTCSessionDescription(

data.answer

)

);


}





if(data.type==="candidate"){


if(peerConnection){


await peerConnection.addIceCandidate(

data.candidate

);


}

}




if(data.type==="end_call"){


endCall();


}



};





socket.onclose=function(){


document.getElementById("status").innerHTML =
"🔴 Disconnected";


};

}





// ================================
// Create WebRTC Connection
// ================================

function createPeerConnection(){


peerConnection =
new RTCPeerConnection(
rtcConfig
);



peerConnection.onicecandidate =
event=>{


if(event.candidate){


socket.send(JSON.stringify({

type:"candidate",

receiver:
document.getElementById("receiver").value,

candidate:event.candidate


}));


}


};




peerConnection.ontrack =
event=>{


document
.getElementById("remoteVideo")
.srcObject =
event.streams[0];


};



}






// ================================
// Start Audio Call
// ================================

async function startAudioCall(){


await makeCall(false);


}





// ================================
// Start Video Call
// ================================

async function startVideoCall(){


await makeCall(true);


}





async function makeCall(video){


let receiver =
document.getElementById("receiver").value.trim();



if(!receiver){

alert("Enter receiver username");

return;

}



localStream =
await navigator.mediaDevices.getUserMedia({

audio:true,

video:video

});



document
.getElementById("localVideo")
.srcObject =
localStream;



createPeerConnection();



localStream.getTracks()
.forEach(track=>{


peerConnection.addTrack(

track,

localStream

);


});



let offer =
await peerConnection.createOffer();



await peerConnection.setLocalDescription(
offer
);



socket.send(JSON.stringify({

type:"offer",

receiver:receiver,

offer:offer

}));



}






// ================================
// Receive Call Offer
// ================================

async function receiveOffer(data){


createPeerConnection();



localStream =
await navigator.mediaDevices.getUserMedia({

audio:true,

video:true

});



document
.getElementById("localVideo")
.srcObject =
localStream;



localStream.getTracks()
.forEach(track=>{


peerConnection.addTrack(

track,

localStream

);


});



await peerConnection.setRemoteDescription(

new RTCSessionDescription(

data.offer

)

);



let answer =
await peerConnection.createAnswer();



await peerConnection.setLocalDescription(
answer
);



socket.send(JSON.stringify({

type:"answer",

receiver:data.sender,

answer:answer

}));



}






// ================================
// End Call
// ================================

function endCall(){



if(localStream){


localStream
.getTracks()
.forEach(track=>track.stop());


}



if(peerConnection){


peerConnection.close();

peerConnection=null;


}



document
.getElementById("localVideo")
.srcObject=null;


document
.getElementById("remoteVideo")
.srcObject=null;




if(socket){


socket.send(JSON.stringify({

type:"end_call",

receiver:
document.getElementById("receiver").value


}));


}


}






// ================================
// Send Message
// ================================

function sendMessage(){


let receiver =
document.getElementById("receiver").value.trim();



let message =
document.getElementById("message").value.trim();



if(!receiver || !message){

return;

}



socket.send(JSON.stringify({

type:"message",

receiver:receiver,

message:message

}));



displayMessage(
"You",
message
);



document.getElementById("message").value="";


}





// ================================
// Display Messages
// ================================

function displayMessage(sender,message){


let item =
document.createElement("li");



item.innerHTML =
"<b>"+
sender+
"</b>: "+
message;



document
.getElementById("messages")
.appendChild(item);


}






// ================================
// Load History
// ================================

async function loadMessages(){


let receiver =
document.getElementById("receiver").value.trim();



let response =
await fetch(

"/messages/"+
encodeURIComponent(username)+
"/"+
encodeURIComponent(receiver)

);



let data =
await response.json();



document.getElementById("messages").innerHTML="";



data.messages.forEach(msg=>{


displayMessage(

msg.sender,

msg.message

);


});


}





// ================================
// Typing Indicator
// ================================

document
.getElementById("message")
.addEventListener(
"input",
function(){


if(socket){


socket.send(JSON.stringify({

type:"typing",

receiver:
document.getElementById("receiver").value,

typing:true

}));


}


});
