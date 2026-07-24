/*
Mobile Chat App Frontend

Features:
- Authentication
- Real-time messaging
- WebSocket communication
- File upload
- Audio/video calls
- Group call signaling
*/


let username = "";

let token = "";

let socket = null;



// ===============================
// WEBRTC
// ===============================


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





// ===============================
// REGISTER
// ===============================


async function register(){


    let user =
    document.getElementById("username")
    .value.trim();



    let phone =
    document.getElementById("phone")
    .value.trim();



    let password =
    document.getElementById("password")
    .value;



    let response =
    await fetch("/register",{


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



    let data =
    await response.json();



    document.getElementById(
        "authMessage"
    ).innerHTML =

    data.message ||

    "Account created";


}







// ===============================
// LOGIN
// ===============================


async function login(){


    let phone =
    document.getElementById("phone")
    .value.trim();



    let password =
    document.getElementById("password")
    .value;



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


        document.getElementById(
            "status"
        ).innerHTML=

        "🟢 Online";


    };







    socket.onmessage = async function(event){


        let data =
        JSON.parse(event.data);



        console.log(data);





        // MESSAGE


        if(data.type==="message"){


            displayMessage(

                data.sender,

                data.message

            );


        }






        // TYPING


        if(data.type==="typing"){


            document.getElementById(
                "typing"
            ).innerHTML =

            data.sender+

            " typing...";


        }







        // CALL OFFER


        if(data.type==="offer"){


            await receiveCall(data);


        }






        // ANSWER


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






        // STATUS


        if(data.type==="status"){


            console.log(

                data.username,

                data.status

            );


        }







        if(data.type==="end_call"){


            endCall();


        }





    };







    socket.onclose=function(){


        document.getElementById(
            "status"
        ).innerHTML=

        "🔴 Offline";


    };



}









// ===============================
// SEND MESSAGE
// ===============================


function sendMessage(){


    let receiver =
    document.getElementById(
        "receiver"
    ).value.trim();



    let message =
    document.getElementById(
        "message"
    ).value.trim();



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
    document.createElement(
        "li"
    );



    li.innerHTML =

    "<b>"+

    sender+

    "</b>: "+

    message;



    document
    .getElementById(
        "messages"
    )
    .appendChild(li);


}









// ===============================
// LOAD HISTORY
// ===============================


async function loadMessages(){



    let receiver =

    document.getElementById(
        "receiver"
    ).value.trim();




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





    document.getElementById(
        "messages"
    ).innerHTML="";





    data.messages.forEach(msg=>{


        displayMessage(

            msg.sender,

            msg.message

        );


    });



}









// ===============================
// WEBRTC CONNECTION
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


        document.getElementById(
            "remoteVideo"
        ).srcObject =

        event.streams[0];


    };




    return pc;


}








// ===============================
// VIDEO CALL
// ===============================


async function startVideoCall(){



    await makeCall(true);


}






function startAudioCall(){


    makeCall(false);


}







async function makeCall(video){



    let receiver =

    document.getElementById(
        "receiver"
    ).value.trim();




    if(!receiver){

        alert(
            "Enter username"
        );

        return;

    }





    localStream =

    await navigator.mediaDevices.getUserMedia({


        audio:true,


        video:video



    });





    document.getElementById(
        "localVideo"
    ).srcObject =

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



    let sender =
    data.sender;





    let pc =
    createPeer(sender);






    localStream =

    await navigator.mediaDevices.getUserMedia({


        audio:true,


        video:true



    });





    document.getElementById(
        "localVideo"
    ).srcObject =

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
// GROUP CALL
// ===============================


function startGroupCall(){


    let room =

    "room_"+Date.now();




    socket.send(JSON.stringify({



        type:"create_call",



        room



    }));



    alert(
        "Room ID: "+room
    );



}






function joinGroupCall(){


    let room =

    prompt(
        "Room ID"
    );



    if(room){


        socket.send(JSON.stringify({


            type:"join_call",


            room



        }));

    }



}








// ===============================
// END CALL
// ===============================


function endCall(){



    if(localStream){


        localStream
        .getTracks()
        .forEach(track=>track.stop());


    }




    Object.values(peers)
    .forEach(pc=>pc.close());




    peers={};





    if(socket){


        socket.send(JSON.stringify({


            type:"end_call"



        }));


    }


}








// ===============================
// FILE UPLOAD
// ===============================


async function uploadFile(){



    let file =

    document.getElementById(
        "file"
    ).files[0];




    if(!file){

        alert(
            "Select file"
        );

        return;

    }






    let form =

    new FormData();



    form.append(
        "file",
        file
    );






    let response =

    await fetch("/upload",{


        method:"POST",


        body:form



    });





    let data =

    await response.json();





    displayMessage(

        "System",

        "Uploaded "+data.filename

    );



}
