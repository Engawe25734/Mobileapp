/*
ChatMe App Frontend

Features:
- Authentication
- WebSocket messaging
- Online status
- Typing indicator
- File upload
- Image/Video/Audio sharing
- Message receipts
- WebRTC audio/video calls
- Group calls
*/


let username = "";

let token = "";

let socket = null;


// ==============================
// WEBRTC VARIABLES
// ==============================


let localStream = null;

let peers = {};

let currentCallUser = null;



const rtcConfig = {

    iceServers:[

        {

            urls:

            "stun:stun.l.google.com:19302"

        }

    ]

};



// ==============================
// CHECK SOCKET
// ==============================


function socketReady(){


    if(!socket || socket.readyState !== WebSocket.OPEN){


        alert(

            "Connection not ready"

        );


        return false;


    }


    return true;


}




// ==============================
// REGISTER USER
// ==============================


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



    let response =

    await fetch(

        "/register",

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



    let data =

    await response.json();



    document

    .getElementById("authMessage")

    .innerHTML =

    data.message ||

    "Account created";


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





    socket = new WebSocket(


        protocol +

        window.location.host +

        "/ws/" +

        encodeURIComponent(username)


    );





    socket.onopen=function(){



        document

        .getElementById("status")

        .innerHTML =


        "🟢 Online";



        loadOnlineUsers();



    };







    socket.onmessage =

    async function(event){



        let data =


        JSON.parse(

            event.data

        );




        console.log(

            "SERVER:",

            data

        );





        // =========================
        // TEXT MESSAGE
        // =========================


        if(data.type==="message"){



            displayMessage(

                data.sender,

                data.message

            );



            // send read receipt


            if(data.message_id){



                socket.send(JSON.stringify({



                    type:"read",



                    receiver:data.sender,



                    message_id:data.message_id



                }));



            }



        }







        // =========================
        // FILE MESSAGE
        // =========================


        if(data.type==="file"){



            displayFile(


                data.sender,


                data.filename,


                data.url,


                data.file_type


            );



        }







        // =========================
        // USER STATUS
        // =========================


        if(data.type==="status"){



            loadOnlineUsers();



        }







        // =========================
        // TYPING
        // =========================


        if(data.type==="typing"){



            let typing =

            document

            .getElementById("typing");





            if(data.typing){



                typing.innerHTML =


                data.sender +

                " is typing...";



            }


            else{


                typing.innerHTML="";


            }



        }







        // =========================
        // MESSAGE DELIVERED
        // =========================


        if(data.type==="delivered"){



            console.log(

                "Delivered:",

                data.message_id

            );


        }







        // =========================
        // MESSAGE READ
        // =========================


        if(data.type==="read"){



            console.log(

                "Read:",

                data.message_id

            );


        }







        // =========================
        // PRIVATE CALL OFFER
        // =========================


        if(data.type==="offer"){



            await receiveCall(

                data

            );


        }







        // =========================
        // CALL ANSWER
        // =========================


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







        // =========================
        // ICE CANDIDATE
        // =========================


        if(data.type==="candidate"){



            let pc =

            peers[data.sender];



            if(pc){



                await pc.addIceCandidate(

                    data.candidate

                );



            }



        }







        // =========================
        // CALL ENDED
        // =========================


        if(data.type==="end_call"){



            endCall();



        }



    };






    socket.onclose=function(){



        document

        .getElementById("status")

        .innerHTML =


        "🔴 Offline";



    };



}
// ==============================
// SEND TEXT MESSAGE
// ==============================


function sendMessage(){



    if(!socketReady()){

        return;

    }




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





    if(!receiver || !message){


        return;


    }






    let data = {



        type:"message",



        receiver:receiver,



        message:message



    };





    socket.send(

        JSON.stringify(data)

    );





    displayMessage(

        "You",

        message,

        true

    );





    document

    .getElementById("message")

    .value="";



}





// ==============================
// DISPLAY TEXT MESSAGE
// ==============================


function displayMessage(

    sender,

    message,

    mine=false

){



    let li =

    document

    .createElement("li");





    li.className =


    mine ?


    "my-message"


    :


    "other-message";






    let time =

    new Date()

    .toLocaleTimeString();





    li.innerHTML =



    `

    <b>${sender}</b>

    <br>

    ${message}

    <small>

    ${time}

    </small>

    `;





    document

    .getElementById("messages")

    .appendChild(li);





    li.scrollIntoView({

        behavior:"smooth"

    });



}







// ==============================
// DISPLAY FILE MESSAGE
// ==============================


function displayFile(

    sender,

    filename,

    url,

    type,

    mine=false

){



    let li =

    document

    .createElement("li");





    li.className =


    mine ?


    "my-message"


    :


    "other-message";





    let content="";







    // IMAGE


    if(type && type.startsWith("image")){



        content =



        `

        <img

        src="${url}"

        class="chat-image">

        `;



    }







    // VIDEO


    else if(type && type.startsWith("video")){



        content =



        `

        <video

        controls

        class="chat-video">


        <source src="${url}">


        </video>

        `;



    }







    // AUDIO


    else if(type && type.startsWith("audio")){



        content =



        `

        <audio controls>


        <source src="${url}">


        </audio>


        `;



    }







    // FILE


    else{


        content =



        `

        📎

        <a

        href="${url}"

        target="_blank">

        ${filename}

        </a>

        `;



    }







    let time =


    new Date()

    .toLocaleTimeString();







    li.innerHTML =



    `

    <b>${sender}</b>

    <br>

    ${content}

    <small>

    ${time}

    </small>

    `;







    document

    .getElementById("messages")

    .appendChild(li);





    li.scrollIntoView({

        behavior:"smooth"

    });



}
// ==============================
// FILE UPLOAD
// ==============================


async function uploadFile(){



    if(!socketReady()){


        return;


    }






    let receiver =


    document

    .getElementById("receiver")

    .value

    .trim();





    let fileInput =


    document

    .getElementById("file");






    if(!receiver){



        alert(

            "Select receiver first"

        );


        return;


    }







    if(!fileInput.files.length){



        alert(

            "Choose a file"

        );


        return;


    }







    let file =

    fileInput.files[0];







    let formData =

    new FormData();





    formData.append(

        "file",

        file

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






        socket.send(JSON.stringify({



            type:"file",



            receiver:receiver,



            filename:data.filename,



            url:data.url,



            file_type:data.type



        }));







        displayFile(


            "You",


            data.filename,


            data.url,


            data.type,


            true


        );






        fileInput.value="";



    }



    catch(error){



        console.log(error);



        alert(

            "Upload failed"

        );



    }



}








// ==============================
// CREATE PEER CONNECTION
// ==============================


function createPeerConnection(user){



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



        let remote =

        document

        .getElementById(

            "remoteVideo"

        );



        if(remote){



            remote.srcObject =

            event.streams[0];



        }


    };







    if(localStream){



        localStream

        .getTracks()

        .forEach(track=>{


            pc.addTrack(

                track,

                localStream

            );


        });


    }



    return pc;


}








// ==============================
// START AUDIO CALL
// ==============================


async function startAudioCall(){



    let receiver =


    document

    .getElementById("receiver")

    .value

    .trim();





    if(!receiver){



        alert(

            "Select user"

        );


        return;


    }



    currentCallUser=receiver;





    localStream =


    await navigator.mediaDevices.getUserMedia({



        audio:true,

        video:false



    });





    let pc =

    createPeerConnection(

        receiver

    );





    let offer =


    await pc.createOffer();





    await pc.setLocalDescription(

        offer

    );





    socket.send(JSON.stringify({



        type:"offer",



        receiver:receiver,



        offer:offer



    }));



}








// ==============================
// START VIDEO CALL
// ==============================


async function startVideoCall(){



    let receiver =


    document

    .getElementById("receiver")

    .value

    .trim();





    if(!receiver){



        alert(

            "Select user"

        );


        return;


    }





    currentCallUser=receiver;







    localStream =


    await navigator.mediaDevices.getUserMedia({



        audio:true,


        video:true



    });





    let video =


    document

    .getElementById(

        "localVideo"

    );





    if(video){



        video.srcObject=

        localStream;


    }






    let pc =


    createPeerConnection(

        receiver

    );






    let offer =


    await pc.createOffer();





    await pc.setLocalDescription(

        offer

    );






    socket.send(JSON.stringify({



        type:"offer",



        receiver:receiver,



        offer:offer



    }));



}
// ==============================
// WEBRTC PEER CONNECTION
// ==============================


function createPeerConnection(user){


    let pc = new RTCPeerConnection(
        rtcConfig
    );


    peers[user] = pc;



    pc.onicecandidate = function(event){


        if(event.candidate){


            socket.send(JSON.stringify({

                type:"candidate",

                receiver:user,

                candidate:event.candidate

            }));


        }


    };



    pc.ontrack=function(event){


        let remote = document.getElementById(
            "remoteVideo"
        );


        remote.innerHTML="";


        let video=document.createElement(
            "video"
        );


        video.srcObject =
        event.streams[0];


        video.autoplay=true;


        video.controls=true;


        video.width=250;


        remote.appendChild(video);


    };


    return pc;


}




// ==============================
// START AUDIO CALL
// ==============================


async function startAudioCall(){



    let receiver =
    document
    .getElementById("receiver")
    .value
    .trim();



    if(!receiver){

        alert(
            "Select user first"
        );

        return;

    }



    localStream =
    await navigator.mediaDevices.getUserMedia({

        audio:true,

        video:false

    });



    let pc =
    createPeerConnection(
        receiver
    );



    localStream
    .getTracks()
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

        receiver:receiver,

        offer:offer,

        callType:"audio"

    }));


    showCallArea();



}






// ==============================
// START VIDEO CALL
// ==============================


async function startVideoCall(){



    let receiver =
    document
    .getElementById("receiver")
    .value
    .trim();



    if(!receiver){


        alert(
            "Select user first"
        );


        return;


    }





    localStream =
    await navigator.mediaDevices.getUserMedia({


        audio:true,


        video:true


    });




    document

    .getElementById(

        "localVideo"

    )

    .srcObject = localStream;





    let pc =

    createPeerConnection(

        receiver

    );




    localStream

    .getTracks()

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


        receiver:receiver,


        offer:offer,


        callType:"video"



    }));





    showCallArea();


}






// ==============================
// RECEIVE CALL
// ==============================


async function receiveCall(data){



    let sender =
    data.sender;



    let pc =
    createPeerConnection(
        sender
    );



    localStream =
    await navigator.mediaDevices.getUserMedia({


        audio:true,


        video:data.callType==="video"



    });





    document

    .getElementById(

        "localVideo"

    )

    .srcObject = localStream;





    localStream

    .getTracks()

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


        answer:answer



    }));





    showCallArea();



}






// ==============================
// END CALL
// ==============================


function endCall(){



    if(localStream){



        localStream

        .getTracks()

        .forEach(track=>{


            track.stop();


        });



        localStream=null;


    }




    Object.values(peers)

    .forEach(pc=>{


        pc.close();


    });




    peers={};




    hideCallArea();



}






// ==============================
// CALL UI
// ==============================


function showCallArea(){


    document

    .getElementById(

        "call-area"

    )

    .classList

    .remove(

        "hidden"

    );


}






function hideCallArea(){



    document

    .getElementById(

        "call-area"

    )

    .classList

    .add(

        "hidden"

    );


}
// ==============================
// MESSAGE DELIVERY RECEIPT
// ==============================


function sendDeliveryReceipt(
    messageId,
    receiver
){


    if(socket && messageId){


        socket.send(JSON.stringify({

            type:"read",

            receiver:receiver,

            message_id:messageId


        }));


    }


}





// ==============================
// HANDLE MESSAGE STATUS
// ==============================


function updateMessageStatus(
    messageId,
    status
){


    let message =
    document.querySelector(
        `[data-id="${messageId}"]`
    );


    if(message){


        let span =
        message.querySelector(
            ".status"
        );


        if(span){


            span.innerHTML=status;


        }


    }


}






// ==============================
// IMPROVED MESSAGE DISPLAY
// ==============================


function displayMessage(
    sender,
    message,
    id=null
){



    let li =
    document.createElement(
        "li"
    );



    if(id){


        li.dataset.id=id;


    }





    li.innerHTML = `


        <div>

            <b>${sender}</b>

            <br>

            ${message}

            <span class="status">

                ✓

            </span>


        </div>


    `;




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






// ==============================
// NOTIFICATION SYSTEM
// ==============================


function showNotification(
    title,
    message
){


    if(
        Notification.permission === "granted"
    ){


        new Notification(

            title,

            {

                body:message

            }

        );


    }


}





// ==============================
// REQUEST NOTIFICATION ACCESS
// ==============================


function enableNotifications(){



    if(
        "Notification" in window
    ){


        Notification.requestPermission();


    }


}







// ==============================
// PLAY MESSAGE SOUND
// ==============================


function playMessageSound(){


    let audio =
    new Audio(
        "/static/message.mp3"
    );


    audio.play()
    .catch(()=>{});


}







// ==============================
// UPDATED SOCKET MESSAGE HANDLER
// ==============================


function handleIncomingMessage(data){



    if(data.type==="message"){



        displayMessage(

            data.sender,

            data.message,

            data.message_id

        );



        playMessageSound();



        showNotification(

            "New message from "+data.sender,

            data.message

        );



        sendDeliveryReceipt(

            data.message_id,

            data.sender

        );


    }






    if(data.type==="delivered"){



        updateMessageStatus(

            data.message_id,

            "✓✓"

        );


    }






    if(data.type==="read"){



        updateMessageStatus(

            data.message_id,

            "✓✓ Read"

        );


    }



}







// ==============================
// LOGOUT
// ==============================


function logout(){



    if(socket){


        socket.close();


    }



    localStorage.removeItem(

        "token"

    );



    localStorage.removeItem(

        "username"

    );



    username="";


    token="";



    document

    .getElementById(

        "chat-page"

    )

    .classList

    .add(

        "hidden"

    );





    document

    .getElementById(

        "auth-page"

    )

    .classList

    .remove(

        "hidden"

    );



}







// ==============================
// DELETE LOCAL FILE PREVIEW
// ==============================


function clearFileInput(){


    let file =
    document.getElementById(
        "file"
    );


    if(file){


        file.value="";


    }


}







// ==============================
// FILE TYPE CHECK
// ==============================


function getFileType(file){



    if(file.type.startsWith("image")){


        return "image";


    }



    if(file.type.startsWith("video")){


        return "video";


    }



    if(file.type.startsWith("audio")){


        return "audio";


    }



    return "document";


}







// ==============================
// FILE SIZE VALIDATION
// ==============================


function validateFile(file){



    let maxSize =
    100 * 1024 * 1024;



    if(file.size > maxSize){


        alert(

            "File size cannot exceed 100MB"

        );


        return false;


    }



    return true;


}







// ==============================
// ENHANCED UPLOAD CHECK
// ==============================


async function uploadMedia(){



    let input =
    document.getElementById(
        "file"
    );



    if(!input.files.length){


        alert(
            "Choose a file"
        );


        return;


    }





    let file =
    input.files[0];




    if(!validateFile(file)){


        return;


    }



    let type =
    getFileType(file);



    console.log(

        "Uploading:",

        type

    );



    uploadFile();



}







// ==============================
// CHECK LOGIN TOKEN
// ==============================


function checkAuthentication(){



    let savedToken =
    localStorage.getItem(
        "token"
    );



    let savedUser =
    localStorage.getItem(
        "username"
    );



    if(
        savedToken &&
        savedUser
    ){


        token=savedToken;


        username=savedUser;


        return true;


    }



    return false;


}







// ==============================
// AUTO START
// ==============================


window.addEventListener(

"load",

function(){


    enableNotifications();



    checkAuthentication();



});
// ==============================
// USER PROFILE DATA
// ==============================


let currentProfile = {

    username:"",
    phone:"",
    avatar:""

};






// ==============================
// LOAD USER PROFILE
// ==============================


async function loadProfile(){


    try{


        let response =
        await fetch(

            "/profile/" +

            encodeURIComponent(username),

            {

                headers:{

                    "Authorization":

                    "Bearer " + token

                }

            }

        );



        let data =
        await response.json();




        currentProfile=data;



        updateProfileUI();



    }


    catch(error){


        console.log(

            "Profile loading failed",

            error

        );


    }


}







// ==============================
// UPDATE PROFILE UI
// ==============================


function updateProfileUI(){



    let name =
    document.getElementById(
        "profileName"
    );



    let image =
    document.getElementById(
        "profileImage"
    );





    if(name){


        name.innerHTML =

        currentProfile.username;


    }





    if(image && currentProfile.avatar){


        image.src =

        currentProfile.avatar;


    }



}







// ==============================
// PROFILE IMAGE UPLOAD
// ==============================


async function uploadProfilePicture(){



    let input =
    document.getElementById(
        "profileFile"
    );



    if(
        !input ||
        !input.files.length
    ){


        alert(
            "Select image"
        );


        return;


    }



    let formData =
    new FormData();



    formData.append(

        "file",

        input.files[0]

    );





    try{


        let response =

        await fetch(

            "/profile/upload",

            {


                method:"POST",


                headers:{


                    "Authorization":

                    "Bearer " + token


                },


                body:formData


            }

        );



        let data =
        await response.json();





        currentProfile.avatar =

        data.url;



        updateProfileUI();



    }


    catch(error){


        console.log(error);


    }


}







// ==============================
// PASSWORD VALIDATION
// ==============================


function validatePassword(password){



    if(password.length < 8){


        return false;


    }





    let hasNumber =
    /\d/.test(password);



    let hasLetter =
    /[A-Za-z]/.test(password);



    return (

        hasNumber &&

        hasLetter

    );



}







// ==============================
// SECURITY CHECK
// ==============================


function checkSecurity(){



    if(!token){


        logout();


        return false;


    }



    return true;


}







// ==============================
// AUTHORIZED REQUEST
// ==============================


async function secureFetch(

    url,

    options={}

){



    options.headers = {


        ...(options.headers || {}),



        "Authorization":

        "Bearer " + token



    };





    return fetch(

        url,

        options

    );


}







// ==============================
// BLOCK USER
// ==============================


async function blockUser(user){



    if(!user){


        return;


    }





    let confirmBlock =

    confirm(

        "Block " + user + "?"

    );





    if(!confirmBlock){


        return;


    }






    await secureFetch(

        "/block",

        {


            method:"POST",


            headers:{


                "Content-Type":

                "application/json"


            },


            body:JSON.stringify({


                user:user


            })


        }

    );



    alert(

        "User blocked"

    );


}







// ==============================
// REPORT USER
// ==============================


async function reportUser(user){



    if(!user){


        return;


    }





    await secureFetch(

        "/report",

        {


            method:"POST",


            headers:{


                "Content-Type":

                "application/json"


            },


            body:JSON.stringify({


                user:user


            })


        }

    );




    alert(

        "Report submitted"

    );


}







// ==============================
// CONNECTION STATUS
// ==============================


function checkConnection(){



    if(

        navigator.onLine

    ){


        console.log(

            "Internet connected"

        );


    }


    else{


        console.log(

            "Offline mode"

        );


    }


}







window.addEventListener(

"online",

function(){


    checkConnection();


});






window.addEventListener(

"offline",

function(){


    checkConnection();


});








// ==============================
// CLEAN MESSAGE AREA
// ==============================


function clearMessages(){



    let box =

    document.getElementById(

        "messages"

    );



    if(box){


        box.innerHTML="";


    }


}







// ==============================
// CHAT SETTINGS
// ==============================


function saveSettings(){



    let settings={


        theme:

        document.body.classList.contains(

            "dark"

        ),


        notifications:

        Notification.permission



    };





    localStorage.setItem(

        "chatSettings",

        JSON.stringify(settings)

    );



}







function loadSettings(){



    let settings =

    JSON.parse(

        localStorage.getItem(

            "chatSettings"

        )

    );





    if(settings && settings.theme){



        document.body.classList.add(

            "dark"

        );


    }


}







// ==============================
// INITIALIZE CHATME
// ==============================


function initializeChatMe(){



    loadSettings();



    checkConnection();



    if(username){


        loadProfile();


    }


}






window.addEventListener(

"load",

initializeChatMe

);
