/*
Mobile Chat App Frontend

Features:
- Authentication
- Real-time messaging
- WebSocket connection
- Audio calls
- Video calls
- Group calls
*/


let username = "";

let token = "";

let socket = null;



// ===============================
// WEBRTC
// ===============================


let localStream = null;


// multiple users
let peers = {};



const rtcConfig = {


    iceServers:[

        {

            urls:
            "stun:stun.l.google.com:19302"

        }

    ]

};



// ===============================
// REGISTER
// ===============================


async function register(){


    let username =
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

            username,

            phone,

            password

        })


    });



    let result =
    await response.json();



    document.getElementById(
        "authMessage"
    ).innerHTML =
    result.message || "Account created";


}







// ===============================
// LOGIN
// ===============================


async function login(){


    let phone =
    document.getElementById("phone").value;


    let password =
    document.getElementById("password").value;




    let response =
    await fetch("/login",{


        method:"POST",


        headers:{


            "Content-Type":"application/json"

        },


        body:JSON.stringify({

            phone,

            password

        })

    });



    let data =
    await response.json();



    if(data.access_token){


        token=data.access_token;


        username=data.username;


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







// ===============================
// OPEN CHAT
// ===============================


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







// ===============================
// WEBSOCKET
// ===============================


function connectSocket(){


    let protocol =
    window.location.protocol==="https:"
    ?
    "wss://"
    :
    "ws://";



    socket =
    new WebSocket(

        protocol +

        window.location.host +

        "/ws/" +

        username

    );





    socket.onopen=function(){


        document
        .getElementById("status")
        .innerHTML="🟢 Online";


    };





    socket.onmessage=async function(event){



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
            data.sender+
            " typing...";


        }







        if(data.type==="offer"){


            await receiveCall(data);


        }






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







        if(data.type==="candidate"){


            let pc =
            peers[data.sender];



            if(pc){


                await pc.addIceCandidate(

                    data.candidate

                );


            }


        }






        if(data.type==="user_joined"){


            console.log(
                data.user+
                " joined call"
            );


        }





        if(data.type==="end_call"){


            endCall();


        }




    };






    socket.onclose=function(){


        document
        .getElementById("status")
        .innerHTML="🔴 Offline";


    };


}







// ===============================
// SEND MESSAGE
// ===============================


function sendMessage(){



    let receiver =
    document.getElementById("receiver").value;



    let message =
    document.getElementById("message").value;



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



    document.getElementById(
        "message"
    ).value="";


}








function displayMessage(
    sender,
    message
){


    let li =
    document.createElement("li");



    li.innerHTML =
    "<b>"+
    sender+
    "</b>: "+
    message;



    document
    .getElementById("messages")
    .appendChild(li);


}







// ===============================
// CREATE PEER CONNECTION
// ===============================


function createPeer(user){



    let pc =
    new RTCPeerConnection(
        rtcConfig
    );



    peers[user]=pc;





    pc.onicecandidate=function(event){


        if(event.candidate){


            socket.send(JSON.stringify({

                type:"candidate",

                receiver:user,

                candidate:event.candidate


            }));


        }


    };





    pc.ontrack=function(event){


        let video =
        document.createElement("video");



        video.autoplay=true;


        video.srcObject =
        event.streams[0];



        document
        .getElementById("remoteVideo")
        .appendChild(video);


    };



    return pc;


}







// ===============================
// START VIDEO CALL
// ===============================


async function startVideoCall(){


    let receiver =
    document.getElementById(
        "receiver"
    ).value;



    localStream =
    await navigator.mediaDevices.getUserMedia({

        audio:true,

        video:true

    });




    document
    .getElementById("localVideo")
    .srcObject =
    localStream;





    let pc =
    createPeer(receiver);



    localStream.getTracks()
    .forEach(track=>{


        pc.addTrack(

            track,

            localStream

        );


    });





    let offer =
    await pc.createOffer();



    await pc.setLocalDescription(
        offer
    );





    socket.send(JSON.stringify({

        type:"offer",

        receiver,

        offer


    }));


}








// ===============================
// RECEIVE CALL
// ===============================


async function receiveCall(data){



    let sender=data.sender;



    let pc =
    createPeer(sender);





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


        pc.addTrack(

            track,

            localStream

        );


    });





    await pc.setRemoteDescription(

        new RTCSessionDescription(
            data.offer
        )

    );





    let answer =
    await pc.createAnswer();




    await pc.setLocalDescription(
        answer
    );





    socket.send(JSON.stringify({

        type:"answer",

        receiver:sender,

        answer


    }));


}








// ===============================
// CREATE GROUP CALL
// ===============================


function createGroupCall(){


    let room =
    "room_"+Date.now();



    socket.send(JSON.stringify({

        type:"create_call",

        room


    }));



    alert(
        "Room created: "+room
    );


}








// ===============================
// JOIN GROUP CALL
// ===============================


function joinGroupCall(){


    let room =
    prompt(
        "Enter room ID"
    );



    socket.send(JSON.stringify({

        type:"join_call",

        room


    }));


}








// ===============================
// END CALL
// ===============================


function endCall(){



    if(localStream){


        localStream
        .getTracks()
        .forEach(
            t=>t.stop()
        );


    }




    Object.values(peers)
    .forEach(pc=>{


        pc.close();


    });



    peers={};



    if(socket){


        socket.send(JSON.stringify({

            type:"end_call"

        }));


    }


}
