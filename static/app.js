/*
ChatMe app.js

Connected with:
- server.py
- auth.py
- api_routes.py

Features:
- Authentication
- JWT session
- WebSocket messaging
- Message history
*/


// =====================================
// CONFIGURATION
// =====================================


const API_URL = "http://localhost:8000";

const WS_URL = "ws://localhost:8000";



let username =
localStorage.getItem("username") || "";


let token =
localStorage.getItem("access_token") || "";


let socket = null;


let selectedUser = "";


let localStream = null;









// =====================================
// REGISTER USER
// Matches server.py /register
// =====================================


async function register(){


    const usernameInput =
    document
    .getElementById("username")
    .value
    .trim();



    const phone =
    document
    .getElementById("phone")
    .value
    .trim();



    const password =
    document
    .getElementById("password")
    .value;



    try{


        const response =
        await fetch(

            `${API_URL}/register`,

            {

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

            }

        );



        const data =
        await response.json();



        document
        .getElementById("authMessage")
        .innerText =
        data.message;



    }

    catch(error){

        console.log(error);

    }


}









// =====================================
// LOGIN USER
// Matches server.py /login
// =====================================


async function login(){


    const phone =
    document
    .getElementById("phone")
    .value
    .trim();



    const password =
    document
    .getElementById("password")
    .value;



    try{


        const response =
        await fetch(

            `${API_URL}/login`,

            {

            method:"POST",

            headers:{

                "Content-Type":
                "application/json"

            },


            body:JSON.stringify({

                phone:phone,

                password:password

            })


            }

        );



        const data =
        await response.json();




        if(response.ok){



            username =
            data.username;



            token =
            data.access_token;




            localStorage.setItem(

                "username",

                username

            );



            localStorage.setItem(

                "access_token",

                token

            );



            openChat();



        }

        else{


            document
            .getElementById("authMessage")
            .innerText =
            data.detail ||
            "Login failed";


        }



    }

    catch(error){

        console.log(error);

    }


}



// =====================================
// REGISTER DEVICE FOR PUSH NOTIFICATIONS
// =====================================

async function registerDevice(token){

    try{

        await fetch(

            `${API_URL}/device/register`,

            {

                method:"POST",

                headers:{

                    "Content-Type":"application/json"

                },

                body:JSON.stringify({

                    username:username,

                    token:token

                })

            }

        );

    }

    catch(error){

        console.error(error);

    }

}






// =====================================
// OPEN CHAT APPLICATION
// =====================================


function openChat(){


    document
    .getElementById("auth-page")
    .classList
    .add("hidden");



    document
    .getElementById("chat-page")
    .classList
    .remove("hidden");



    document
    .getElementById("status")
    .innerText =
    "Connecting...";



    connectSocket();


}









// =====================================
// WEBSOCKET CONNECTION
// Matches server.py
// /ws/{username}
// =====================================


function connectSocket(){



    socket =
    new WebSocket(

        `${WS_URL}/ws/${username}`

    );





    socket.onopen=function(){


        console.log(
            "ChatMe connected"
        );



        document
        .getElementById("status")
        .innerText =
        "Online";


    };






    socket.onmessage = async function(event) {


        const data =
        JSON.parse(event.data);



        console.log(data);




        if(data.type==="message"){


          const decrypted =
          await decryptMessage(

               data.message,

               privateKey

    );


         displayMessage({

              sender:data.sender,

             message:decrypted

    });

        showNotification(
            data.sender,
            data.message

    );

}




        else if(data.type==="file"){


            displayMessage({

                sender:data.sender,

                message:
                "📎 " + data.filename

            });


        }




        else if(data.type==="typing"){


            document
            .getElementById("typing")
            .innerText =
            data.typing
            ?
            "Typing..."
            :
            "";

        }




        else if(data.type==="offer"){


            receiveOffer(data);


        }




        else if(data.type==="answer"){


            receiveAnswer(data);


        }




        else if(data.type==="candidate"){


            receiveCandidate(data);


        }



    };






    socket.onclose=function(){


        document
        .getElementById("status")
        .innerText =
        "Offline";


    };


}









// =====================================
// SEND MESSAGE
// WebSocket message
// =====================================


async function sendMessage(){


    const input =
    document
    .getElementById("message");



    const text =
    input.value.trim();




    if(!text || !selectedUser){

        return;

    }




  const encryptedMessage =
  await encryptMessage(
    text,
    receiverPublicKey
);


socket.send(

    JSON.stringify({

        type:"message",

        receiver:selectedUser,

        message:encryptedMessage

    })

);



    displayMessage({

        sender:username,

        message:text

    });



    input.value="";


}


// =====================================
// CHATME NOTIFICATIONS
// =====================================


function requestNotificationPermission(){


    if("Notification" in window){


        Notification.requestPermission();


    }


}






function showNotification(sender, message){



    if(Notification.permission === "granted"){



        new Notification(

            "ChatMe - New Message",

            {

                body:
                sender + ": " + message,


                icon:
                "/static/icon.png"

            }

        );


    }


}







// =====================================
// LOAD MESSAGE HISTORY
// API: /messages/user1/user2
// =====================================


async function loadMessages(){


    selectedUser =
    document
    .getElementById("receiver")
    .value
    .trim();




    if(!selectedUser){

        return;

    }




    document
    .getElementById("chatUser")
    .innerText =
    selectedUser;





    const response =
    await fetch(

        `${API_URL}/messages/${username}/${selectedUser}`

    );




    const data =
    await response.json();




    const list =
    document
    .getElementById("messages");



    list.innerHTML="";




    data.messages.forEach(msg=>{


        displayMessage({

            sender:msg.sender,

            message:msg.message


        });


    });



}









function displayMessage(data){


    const list =
    document
    .getElementById("messages");



    const item =
    document
    .createElement("li");



    item.innerHTML =

    `
    <strong>${data.sender}</strong>
    :
    ${data.message}
    `;



    list.appendChild(item);



}









function enterSend(event){


    if(event.key==="Enter"){

        sendMessage();

    }


}
// =====================================
// FILE UPLOAD
// Matches server.py /upload
// =====================================


async function uploadFile(){


    const file =
    document
    .getElementById("file")
    .files[0];



    if(!file){

        return;

    }




    const formData =
    new FormData();



    formData.append(

        "file",

        file

    );




    const response =
    await fetch(

        `${API_URL}/upload`,

        {

            method:"POST",

            body:formData

        }

    );




    const data =
    await response.json();




    socket.send(

        JSON.stringify({

            type:"file",

            receiver:selectedUser,

            filename:data.filename,

            url:data.url,

            file_type:data.type


        })

    );



}









// =====================================
// EMOJI FUNCTIONS
// =====================================


function toggleEmoji(){


    document
    .getElementById("emoji-panel")
    .classList
    .toggle("hidden");


}




function addEmoji(emoji){


    document
    .getElementById("message")
    .value += emoji;


}









// =====================================
// DARK MODE
// =====================================


function toggleTheme(){


    document
    .body
    .classList
    .toggle("dark");


}









// =====================================
// GROUP CALL
// =====================================


function createGroupCall(){


    document
    .getElementById("group-call-modal")
    .classList
    .remove("hidden");


}






function joinGroupCall(){


    const room =
    document
    .getElementById("roomId")
    .value
    .trim();



    if(!room){

        return;

    }




    socket.send(

        JSON.stringify({

            type:"join_call",

            room:room

        })

    );



}






function closeModal(){


    document
    .getElementById("group-call-modal")
    .classList
    .add("hidden");


}









// =====================================
// WEBRTC AUDIO / VIDEO CALLING
// =====================================


let peerConnection = null;




const rtcConfig = {


    iceServers:[


        {

            urls:
            "stun:stun.l.google.com:19302"

        }


    ]


};









// ===============================
// CREATE PEER CONNECTION
// ===============================


function createPeerConnection(){


    peerConnection =
    new RTCPeerConnection(

        rtcConfig

    );





    peerConnection.onicecandidate =
    function(event){


        if(event.candidate){


            socket.send(

                JSON.stringify({

                    type:"candidate",

                    receiver:selectedUser,

                    candidate:event.candidate


                })

            );


        }


    };







    peerConnection.ontrack =
    function(event){


        document
        .getElementById("remoteVideo")
        .srcObject =
        event.streams[0];


    };


}









// ===============================
// START AUDIO CALL
// ===============================


async function startAudioCall(){



    if(!selectedUser){


        alert(
            "Select a user first"
        );


        return;


    }





    createPeerConnection();





    localStream =
    await navigator
    .mediaDevices
    .getUserMedia({

        audio:true

    });





    localStream
    .getTracks()
    .forEach(track=>{


        peerConnection.addTrack(

            track,

            localStream

        );


    });





    const offer =
    await peerConnection
    .createOffer();




    await peerConnection
    .setLocalDescription(

        offer

    );






    socket.send(

        JSON.stringify({

            type:"offer",

            receiver:selectedUser,

            offer:offer


        })

    );





    document
    .getElementById("call-area")
    .classList
    .remove("hidden");


}









// ===============================
// START VIDEO CALL
// ===============================


async function startVideoCall(){



    if(!selectedUser){


        alert(
            "Select a user first"
        );


        return;

    }





    createPeerConnection();






    localStream =
    await navigator
    .mediaDevices
    .getUserMedia({

        video:true,

        audio:true


    });






    document
    .getElementById("localVideo")
    .srcObject =
    localStream;






    localStream
    .getTracks()
    .forEach(track=>{


        peerConnection.addTrack(

            track,

            localStream

        );


    });






    const offer =
    await peerConnection
    .createOffer();






    await peerConnection
    .setLocalDescription(

        offer

    );







    socket.send(

        JSON.stringify({

            type:"offer",

            receiver:selectedUser,

            offer:offer


        })

    );






    document
    .getElementById("call-area")
    .classList
    .remove("hidden");


}









// ===============================
// RECEIVE OFFER
// ===============================


async function receiveOffer(data){



    createPeerConnection();






    localStream =
    await navigator
    .mediaDevices
    .getUserMedia({

        video:true,

        audio:true


    });






    document
    .getElementById("localVideo")
    .srcObject =
    localStream;







    localStream
    .getTracks()
    .forEach(track=>{


        peerConnection.addTrack(

            track,

            localStream

        );


    });







    await peerConnection
    .setRemoteDescription(

        new RTCSessionDescription(

            data.offer

        )

    );






    const answer =
    await peerConnection
    .createAnswer();






    await peerConnection
    .setLocalDescription(

        answer

    );






    socket.send(

        JSON.stringify({

            type:"answer",

            receiver:data.sender,

            answer:answer


        })

    );





    document
    .getElementById("call-area")
    .classList
    .remove("hidden");


}









// ===============================
// RECEIVE ANSWER
// ===============================


async function receiveAnswer(data){



    await peerConnection
    .setRemoteDescription(

        new RTCSessionDescription(

            data.answer

        )

    );


}









// ===============================
// RECEIVE ICE CANDIDATE
// ===============================


async function receiveCandidate(data){



    if(peerConnection){


        await peerConnection
        .addIceCandidate(

            new RTCIceCandidate(

                data.candidate

            )

        );


    }


}









// ===============================
// END CALL
// ===============================


function endCall(){



    if(localStream){


        localStream
        .getTracks()
        .forEach(track=>{


            track.stop();


        });


    }






    if(peerConnection){


        peerConnection.close();


        peerConnection=null;


    }






    document
    .getElementById("call-area")
    .classList
    .add("hidden");






    socket.send(

        JSON.stringify({

            type:"end_call",

            receiver:selectedUser


        })

    );


}









// =====================================
// AUTO LOGIN SESSION RESTORE
// =====================================


window.onload=function(){

    requestNotificationPermission();

    if(username){


        openChat();


    }


};
// =====================================
// CHATME SETTINGS SYSTEM
// =====================================


const API_URL = "http://localhost:8000";




// =====================================
// OPEN SETTINGS
// =====================================

function openSettings(){


    document
    .getElementById("settings-panel")
    .classList
    .remove("hidden");


}




// =====================================
// CLOSE SETTINGS
// =====================================

function closeSettings(){


    document
    .getElementById("settings-panel")
    .classList
    .add("hidden");


}




// =====================================
// OPEN PROFILE SETTINGS
// =====================================

function openProfileSettings(){


    hideAllSettingsPages();


    document
    .getElementById("profile-page")
    .classList
    .remove("hidden");


}




// =====================================
// OPEN PRIVACY SETTINGS
// =====================================

function openPrivacySettings(){


    hideAllSettingsPages();


    document
    .getElementById("privacy-page")
    .classList
    .remove("hidden");


}




// =====================================
// OPEN NOTIFICATION SETTINGS
// =====================================

function openNotificationSettings(){


    hideAllSettingsPages();


    document
    .getElementById("notification-page")
    .classList
    .remove("hidden");


}




// =====================================
// OPEN APPEARANCE SETTINGS
// =====================================

function openAppearanceSettings(){


    hideAllSettingsPages();


    document
    .getElementById("appearance-page")
    .classList
    .remove("hidden");


}




// =====================================
// OPEN STORAGE
// =====================================

function openStorageSettings(){


    alert(
        "Cloud storage coming soon"
    );


}




// =====================================
// OPEN ACCOUNT
// =====================================

function openAccountSettings(){


    hideAllSettingsPages();


    document
    .getElementById("account-page")
    .classList
    .remove("hidden");


}




// =====================================
// HIDE SETTINGS PAGES
// =====================================

function hideAllSettingsPages(){


    let pages = [

        "profile-page",

        "privacy-page",

        "notification-page",

        "appearance-page",

        "account-page"

    ];



    pages.forEach(function(page){


        let element =
        document.getElementById(page);



        if(element){


            element
            .classList
            .add("hidden");


        }


    });


}





// =====================================
// UPLOAD PROFILE PICTURE
// =====================================

async function uploadProfilePicture(){


    const file =

    document
    .getElementById("profile-upload")
    .files[0];



    if(!file){

        return;

    }



    let formData = new FormData();


    formData.append(

        "file",

        file

    );



    try{


        const response = await fetch(

            `${API_URL}/profile/${username}/picture`,

            {

                method:"POST",

                body:formData

            }

        );



        const data =
        await response.json();



        document
        .getElementById("profile-picture")
        .src =
        data.profile_picture;



        document
        .getElementById("settings-avatar")
        .src =
        data.profile_picture;



        document
        .getElementById("edit-avatar")
        .src =
        data.profile_picture;



    }


    catch(error){


        console.error(

            "Profile upload error:",

            error

        );


    }


}






// =====================================
// SAVE PROFILE
// =====================================

async function saveProfile(){


    const bio =

    document
    .getElementById("edit-bio")
    .value;



    try{


        await fetch(

            `${API_URL}/profile/${username}/bio`,

            {

                method:"PUT",

                headers:{


                    "Content-Type":

                    "application/json"


                },


                body:JSON.stringify({

                    bio:bio

                })


            }

        );



        alert(

            "Profile updated"

        );


    }


    catch(error){


        console.error(error);


    }


}






// =====================================
// SAVE PRIVACY SETTINGS
// =====================================

async function savePrivacy(){


    const settings = {


        last_seen:

        document
        .getElementById("last-seen")
        .value,



        online_status:

        document
        .getElementById("online-status")
        .value,



        profile_picture:

        document
        .getElementById("profile-privacy")
        .value,



        read_receipts:

        document
        .getElementById("read-receipts")
        .checked,



        typing_indicator:

        document
        .getElementById("typing-status")
        .checked


    };



    await fetch(

        `${API_URL}/profile/${username}/privacy`,

        {

            method:"PUT",

            headers:{

                "Content-Type":

                "application/json"

            },


            body:JSON.stringify(settings)


        }

    );



    alert(

        "Privacy saved"

    );


}






// =====================================
// SAVE NOTIFICATIONS
// =====================================

async function saveNotifications(){


    const settings = {


        messages:

        document
        .getElementById("message-notifications")
        .checked,



        calls:

        document
        .getElementById("call-notifications")
        .checked,



        groups:

        document
        .getElementById("group-notifications")
        .checked


    };



    await fetch(

        `${API_URL}/profile/${username}/notifications`,

        {

            method:"PUT",

            headers:{

                "Content-Type":

                "application/json"

            },


            body:JSON.stringify(settings)


        }

    );


    alert(

        "Notification settings saved"

    );


}






// =====================================
// SAVE APPEARANCE
// =====================================

function saveAppearance(){


    const dark =

    document
    .getElementById("dark-mode")
    .checked;



    if(dark){


        document
        .body
        .classList
        .add("dark-mode");


    }

    else{


        document
        .body
        .classList
        .remove("dark-mode");


    }



    localStorage.setItem(

        "theme",

        dark ? "dark" : "light"

    );


}






// =====================================
// LOGOUT
// =====================================

function logout(){


    localStorage.removeItem(

        "token"

    );


    localStorage.removeItem(

        "username"

    );



    window.location.reload();


}
