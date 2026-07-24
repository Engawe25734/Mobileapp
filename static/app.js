/*
Mobile Chat App Frontend

Features:
- Authentication
- WebSocket messaging
- Online status
- Typing indicator
- File upload
- WebRTC calls
*/


let username = "";

let token = "";

let socket = null;



// ==============================
// WEBRTC VARIABLES
// ==============================


let localStream = null;

let peers = {};



const rtcConfig = {

    iceServers:[

        {

            urls:
            "stun:stun.l.google.com:19302"

        }

    ]

};

// ==============================
// REGISTER USER
// ==============================


async function register(){


    const usernameInput =
    document.getElementById("username")
    .value
    .trim();



    const phone =
    document.getElementById("phone")
    .value
    .trim();



    const password =
    document.getElementById("password")
    .value;





    let response =
    await fetch("/register",{


        method:"POST",


        headers:{


            "Content-Type":
            "application/json"


        },


        body:JSON.stringify({


            username:usernameInput,


            phone:phone,


            password:password


        })


    });


    let data =
    await response.json();





    document.getElementById(
        "authMessage"
    )
    .innerHTML =
    data.message ||
    "Account created";



}

// ==============================
// LOGIN USER
// ==============================


async function login(){



    const phone =
    document.getElementById("phone")
    .value
    .trim();



    const password =
    document.getElementById("password")
    .value;





    let response =
    await fetch("/login",{


        method:"POST",


        headers:{


            "Content-Type":
            "application/json"


        },


        body:JSON.stringify({


            phone,


            password


        })


    });

    let data =
    await response.json();





    if(data.access_token){



        token =
        data.access_token;



        username =
        data.username;

        localStorage.setItem(
            "token",
            token
        );



        openChat();


    }


    else{


        alert(
            "Invalid login"
        );


    }


}
// ==============================
// OPEN CHAT
// ==============================


function openChat(){



    document
    .getElementById(
        "auth-page"
    )
    .classList
    .add(
        "hidden"
    );

    document
    .getElementById(
        "chat-page"
    )
    .classList
    .remove(
        "hidden"
    );

    connectSocket();



}
// ==============================
// CONNECT WEBSOCKET
// ==============================


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

        encodeURIComponent(
            username
        )


    );

    socket.onopen=function(){


        document
        .getElementById(
            "status"
        )
        .innerHTML =
        "🟢 Online";



    };
    socket.onmessage =
    async function(event){



        let data =
        JSON.parse(
            event.data
        );



        console.log(data);
        // MESSAGE RECEIVED


        if(data.type==="message"){



            displayMessage(

                data.sender,

                data.message

            );


        }

        // TYPING


        if(data.type==="typing"){



            document
            .getElementById(
                "typing"
            )
            .innerHTML =


            data.sender +
            " is typing...";



            setTimeout(()=>{


                document
                .getElementById(
                    "typing"
                )
                .innerHTML="";



            },2000);



        }

        // CALL OFFER


        if(data.type==="offer"){


            await receiveCall(
                data
            );


        }


        // CALL ANSWER


        if(data.type==="answer"){


            let pc =
            peers[data.sender];



            if(pc){


                await pc.setRemoteDescription(

                    new RTCSessionDescription(

                        data.answer

                    )

                );


            }


        }

        // ICE CANDIDATE


        if(data.type==="candidate"){


            let pc =
            peers[data.sender];



            if(pc){


                await pc.addIceCandidate(

                    data.candidate

                );


            }


        }

        if(data.type==="end_call"){


            endCall();


        }




    };

    socket.onclose=function(){



        document
        .getElementById(
            "status"
        )
        .innerHTML =
        "🔴 Offline";


    };



}

// ==============================
// SEND MESSAGE
// ==============================


function sendMessage(){



    let receiver =
    document
    .getElementById(
        "receiver"
    )
    .value
    .trim();





    let message =
    document
    .getElementById(
        "message"
    )
    .value
    .trim();

    if(!receiver || !message)
        return;

    socket.send(JSON.stringify({



        type:"message",


        receiver,


        message



    }));


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

// ==============================
// DISPLAY MESSAGE
// ==============================


function displayMessage(
    sender,
    message
){



    let li =
    document.createElement(
        "li"
    );




    li.innerHTML =

    "<b>"+
    sender+
    "</b><br>"+
    message;





    document
    .getElementById(
        "messages"
    )
    .appendChild(
        li
    );

    li.scrollIntoView({

        behavior:"smooth"

    });


}
// =====================================
// FILE UPLOAD
// =====================================

async function uploadFile(){

    let fileInput =
    document.getElementById("file");


    if(!fileInput.files.length){

        alert("Select a file first");

        return;

    }


    let formData =
    new FormData();


    formData.append(
        "file",
        fileInput.files[0]
    );



    try{


        let response =
        await fetch(
            "/upload",
            {
                method:"POST",
                body:formData
            }
        );



        let data =
        await response.json();



        displayMessage(
            "System",
            "📎 Uploaded: " + data.filename
        );


    }

    catch(error){

        console.log(error);

        alert(
            "Upload failed"
        );

    }


}


// =====================================
// ENTER KEY SEND MESSAGE
// =====================================


function enterSend(event){


    if(event.key==="Enter"){


        sendMessage();


    }


}

// =====================================
// LOAD OLD MESSAGES
// =====================================


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

        "/messages/" +

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

// =====================================
// TYPING STATUS
// =====================================


let typingTimer;



document
.getElementById("message")
.addEventListener(
"input",
function(){



    let receiver =
    document
    .getElementById("receiver")
    .value;




    if(socket && receiver){


        socket.send(JSON.stringify({

            type:"typing",

            receiver:receiver,

            typing:true


        }));


    }




    clearTimeout(
        typingTimer
    );



    typingTimer =
    setTimeout(()=>{


        if(socket && receiver){


            socket.send(JSON.stringify({

                type:"typing",

                receiver:receiver,

                typing:false


            }));


        }


    },1000);



});
// =====================================
// ONLINE USER CHECK
// =====================================


async function loadOnlineUsers(){


    let response =
    await fetch(
        "/online"
    );


    let data =
    await response.json();



    console.log(
        "Online users:",
        data.users
    );


}


// =====================================
// RESTORE SESSION
// =====================================


window.onload=function(){


    let savedToken =
    localStorage.getItem(
        "token"
    );


    if(savedToken){


        token=savedToken;


    }


};
