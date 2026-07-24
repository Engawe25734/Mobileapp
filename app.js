app.js

Frontend JavaScript engine
for WhatsApp Clone
*/


let token = "";

let username = "";

let socket = null;

let receiver = "";




// ================================
// Register User
// ================================

async function register(){


let user =
document.getElementById(
"username"
).value;


let phone =
document.getElementById(
"phone"
).value;



let password =
document.getElementById(
"password"
).value;



let response =
await fetch("/register",
{

method:"POST",

headers:
{
"Content-Type":
"application/json"
},


body:JSON.stringify({

username:user,

phone:phone,

password:password

})

});



let result =
await response.json();



document.getElementById(
"authMessage"
).innerHTML =
result.message;


}





// ================================
// Login User
// ================================


async function login(){


let phone =
document.getElementById(
"phone"
).value;



let password =
document.getElementById(
"password"
).value;



let response =
await fetch("/login",
{

method:"POST",

headers:
{

"Content-Type":
"application/json"

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
result.username;



localStorage.setItem(
"token",
token
);



openChat();


}

else{


alert(
"Login failed"
);


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
// Upload File
// ================================


async function uploadFile(){


let fileInput =
document.getElementById(
"file"
);


let file =
fileInput.files[0];


if(!file){

return;

}



let formData =
new FormData();



formData.append(
"file",
file
);



let response =
await fetch(
"/upload",
{

method:"POST",

body:formData

}
);



let result =
await response.json();



socket.send(

JSON.stringify({

type:"file",

receiver:
document
.getElementById(
"receiver"
)
.value,


filename:
result.filename,


path:
result.path,


filetype:
result.type

})

);


}



// ================================
// WebSocket Connection
// ================================


function connectSocket(){


socket =
new WebSocket(

"ws://127.0.0.1:8000/ws/"
+ username

);




socket.onopen=function(){


document
.getElementById(
"status"
)
.innerHTML =
"🟢 Online";


};





socket.onmessage=function(event){


let data =
JSON.parse(
event.data
);



console.log(data);

if(data.type==="file"){


displayMessage(

data.sender,

"📎 File: "
+
data.filename
+
"\n"
+
data.path

);


}


// New message

if(data.type==="message"){


displayMessage(

data.sender,

data.message

);


}





// Typing indicator

if(data.type==="typing"){


if(data.typing){


document
.getElementById(
"typing"
)
.innerHTML =
data.sender
+" is typing...";


}

else{


document
.getElementById(
"typing"
)
.innerHTML="";


}


}





// Delivery receipt

if(data.type==="delivered"){


console.log(

"Message delivered:",
data.message_id

);


}




// Read receipt

if(data.type==="read"){


console.log(

"Message read:",
data.message_id

);


}





};






socket.onclose=function(){


document
.getElementById(
"status"
)
.innerHTML =
"🔴 Disconnected";



// reconnect after 5 seconds

setTimeout(

connectSocket,

5000

);


};


}







// ================================
// Send Message
// ================================


function sendMessage(){


receiver =
document
.getElementById(
"receiver"
)
.value;



let message =
document
.getElementById(
"message"
)
.value;




if(!receiver || !message){

return;

}





let payload={


type:"message",


receiver:receiver,


message:message


};





socket.send(

JSON.stringify(payload)

);




displayMessage(

"You",

message

);



document
.getElementById(
"message"
)
.value="";



}





// ================================
// Display Message
// ================================


function displayMessage(
sender,
message
){


let list =
document
.getElementById(
"messages"
);



let item =
document.createElement(
"li"
);



item.innerHTML =
"<b>"
+sender+
"</b>: "
+message;



list.appendChild(
item
);



}







// ================================
// Enter key send
// ================================


function enterSend(event){


if(event.key==="Enter"){

sendMessage();

}

}

// ================================
// Load previous messages
// ================================

async function loadMessages(){


let receiver =
document
.getElementById(
"receiver"
)
.value;



let response =
await fetch(
"/messages/"
+
username
+
"/"
+
receiver
);



let data =
await response.json();



document
.getElementById(
"messages"
)
.innerHTML="";



data.messages.forEach(
msg=>{


displayMessage(

msg.sender,

msg.message

);


});


}





// ================================
// Typing detection
// ================================


document
.getElementById("message")
.addEventListener(
"input",
function(){


if(socket){


socket.send(

JSON.stringify({

type:"typing",

receiver:
document
.getElementById(
"receiver"
)
.value,


typing:true

})

);


}


});
