/*
Frontend JavaScript engine
for mobile app
*/

let token = "";
let username = "";
let socket = null;


// ================================
// Register User
// ================================

async function register(){

    let user = document.getElementById("username").value.trim();
    let phone = document.getElementById("phone").value.trim();
    let password = document.getElementById("password").value;


    let response = await fetch("/register", {

        method:"POST",

        headers:{
            "Content-Type":"application/json"
        },

        body:JSON.stringify({

            username:user,
            phone:phone,
            password:password

        })

    });


    let result = await response.json();


    document.getElementById("authMessage").innerHTML =
    result.message;

}



// ================================
// Login User
// ================================

async function login(){

    let phone =
    document.getElementById("phone").value.trim();


    let password =
    document.getElementById("password").value;



    let response = await fetch("/login",{

        method:"POST",

        headers:{
            "Content-Type":"application/json"
        },

        body:JSON.stringify({

            phone:phone,
            password:password

        })

    });


    let result = await response.json();



    if(result.access_token){

        token = result.access_token;

        username = result.username.trim();


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
// Upload File
// ================================

async function uploadFile(){

    let file =
    document.getElementById("file").files[0];


    if(!file){
        return;
    }


    let formData = new FormData();

    formData.append(
        "file",
        file
    );



    let response = await fetch("/upload",{

        method:"POST",

        body:formData

    });



    let result = await response.json();



    socket.send(JSON.stringify({

        type:"file",

        receiver:
        document
        .getElementById("receiver")
        .value
        .trim(),


        filename:result.filename,

        path:result.path,

        filetype:result.type


    }));

}



// ================================
// WebSocket Connection
// ================================

function connectSocket(){


    let protocol =
    window.location.protocol === "https:"
    ? "wss://"
    : "ws://";



    let wsUrl =
    protocol +
    window.location.host +
    "/ws/" +
    encodeURIComponent(username);



    console.log(
        "Connecting:",
        wsUrl
    );



    socket = new WebSocket(wsUrl);



    socket.onopen=function(){

        document
        .getElementById("status")
        .innerHTML="🟢 Online";


        console.log(
            "WebSocket connected"
        );

    };



    socket.onmessage=function(event){


        let data =
        JSON.parse(event.data);



        console.log(data);



        if(data.type==="message"){

            displayMessage(
                data.sender,
                data.message
            );

        }



        if(data.type==="typing"){

            document
            .getElementById("typing")
            .innerHTML =
            data.typing
            ?
            data.sender+" is typing..."
            :
            "";

        }



        if(data.type==="delivered"){

            console.log(
                "Delivered:",
                data.message_id
            );

        }



        if(data.type==="read"){

            console.log(
                "Read:",
                data.message_id
            );

        }


    };



    socket.onclose=function(){

        document
        .getElementById("status")
        .innerHTML="🔴 Disconnected";


        setTimeout(
            connectSocket,
            5000
        );

    };



    socket.onerror=function(error){

        console.log(
            "WebSocket error",
            error
        );

    };


}




// ================================
// Send Message
// ================================

function sendMessage(){


    let receiver =
    document
    .getElementById("receiver")
    .value
    .trim();



    let message =
    document
    .getElementById("message")
    .value
    .trim();



    if(!receiver || !message || !socket){

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



    document
    .getElementById("message")
    .value="";


}





// ================================
// Display Message
// ================================

function displayMessage(sender,message){


    let list =
    document.getElementById("messages");



    let item =
    document.createElement("li");



    item.innerHTML =
    "<b>"+sender+"</b>: "+message;



    list.appendChild(item);

}




// ================================
// Enter Key Send
// ================================

function enterSend(event){

    if(event.key==="Enter"){

        sendMessage();

    }

}




// ================================
// Load Messages
// ================================

async function loadMessages(){


    let receiver =
    document
    .getElementById("receiver")
    .value
    .trim();



    if(!receiver){
        return;
    }



    let response =
    await fetch(
        "/messages/"
        +
        encodeURIComponent(username)
        +
        "/"
        +
        encodeURIComponent(receiver)
    );



    let data =
    await response.json();



    document
    .getElementById("messages")
    .innerHTML="";



    data.messages.forEach(msg=>{


        displayMessage(

            msg.sender,

            msg.message

        );


    });


}




// ================================
// Typing Detection
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
            document
            .getElementById("receiver")
            .value
            .trim(),


            typing:true

        }));

    }


});
