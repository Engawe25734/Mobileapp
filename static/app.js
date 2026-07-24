/*
ChatMe App Frontend

Features:
- Authentication
- WebSocket messaging
- Online status
- Typing indicator
- File upload
- Image/Video/Audio sharing
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
// LOGIN USER
// ==============================


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





    let response =

    await fetch(

        "/login",

        {


            method:"POST",


            headers:{


                "Content-Type":

                "application/json"


            },


            body:JSON.stringify({


                phone,

                password


            })


        }

    );




    let data =

    await response.json();





    if(data.access_token){



        token = data.access_token;


        username = data.username;



        localStorage.setItem(

            "token",

            token

        );



        localStorage.setItem(

            "username",

            username

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

    .getElementById("auth-page")

    .classList

    .add("hidden");



    document

    .getElementById("chat-page")

    .classList

    .remove("hidden");



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


    };





    socket.onmessage =

    async function(event){



        let data =

        JSON.parse(

            event.data

        );




        console.log(data);





        // =========================
        // TEXT MESSAGE RECEIVED
        // =========================


        if(data.type==="message"){



            displayMessage(

                data.sender,

                data.message

            );


        }







        // =========================
        // FILE MESSAGE RECEIVED
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
        // TYPING STATUS
        // =========================


        if(data.type==="typing"){



            document

            .getElementById("typing")

            .innerHTML =



            data.sender +

            " is typing...";





            setTimeout(()=>{


                document

                .getElementById("typing")

                .innerHTML="";



            },2000);



        }







        // =========================
        // CALL OFFER
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
        // END CALL
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





// ==============================
// DISPLAY TEXT MESSAGE
// ==============================


function displayMessage(

    sender,

    message

){



    let li =

    document

    .createElement("li");





    li.innerHTML =



    "<b>"+

    sender+

    "</b><br>"+

    message;





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

    type

){



    let li =

    document

    .createElement("li");




    let content="";







    // IMAGE


    if(type && type.startsWith("image")){



        content =

        `

        <img

        src="${url}"

        width="220">

        `;


    }







    // VIDEO


    else if(type && type.startsWith("video")){



        content =

        `

        <video

        controls

        width="260">


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







    // DOCUMENT


    else{


        content =



        `

        📄

        <a href="${url}" target="_blank">

        ${filename}

        </a>

        `;



    }







    li.innerHTML =



    "<b>"+

    sender+

    "</b><br>"+

    content;







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

            data.type

        );





        fileInput.value="";



    }



    catch(error){



        console.log(error);



        alert(

            "Upload failed"

        );



    }



}// ==============================
// ENTER KEY SEND
// ==============================


function enterSend(event){


    if(event.key==="Enter"){


        sendMessage();


    }


}





// ==============================
// LOAD OLD MESSAGES
// ==============================


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







// ==============================
// TYPING INDICATOR
// ==============================


let typingTimer;





document

.getElementById("message")

.addEventListener(

"input",

function(){



    let receiver =

    document

    .getElementById("receiver")

    .value

    .trim();







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








// ==============================
// ONLINE USERS
// ==============================


async function loadOnlineUsers(){



    let response =

    await fetch(

        "/online"

    );






    let data =

    await response.json();





    let contacts =

    document

    .getElementById("contacts");





    contacts.innerHTML="";






    data.users.forEach(user=>{



        let div =

        document

        .createElement("div");





        div.className=

        "contact-item";





        div.innerHTML =



        "🟢 " + user;





        div.onclick=function(){



            document

            .getElementById("receiver")

            .value=user;



            document

            .getElementById("chatUser")

            .innerHTML=user;



        };





        contacts.appendChild(div);



    });



}









// ==============================
// RESTORE LOGIN SESSION
// ==============================


window.onload=function(){



    let savedToken =

    localStorage.getItem(

        "token"

    );





    let savedUsername =

    localStorage.getItem(

        "username"

    );







    if(savedToken && savedUsername){



        token=savedToken;



        username=savedUsername;



        openChat();



    }






    loadOnlineUsers();



};






// ==============================
// THEME
// ==============================


function toggleTheme(){


    document.body

    .classList

    .toggle(

        "dark"

    );


}





// ==============================
// EMOJI
// ==============================


function toggleEmoji(){



    document

    .getElementById(

        "emoji-panel"

    )

    .classList

    .toggle(

        "hidden"

    );


}






function addEmoji(

    emoji

){



    let input =

    document

    .getElementById(

        "message"

    );





    input.value += emoji;



}





// ==============================
// GROUP CALL MODAL
// ==============================


function createGroupCall(){



    document

    .getElementById(

        "group-call-modal"

    )

    .classList

    .remove(

        "hidden"

    );


}






function closeModal(){



    document

    .getElementById(

        "group-call-modal"

    )

    .classList

    .add(

        "hidden"

    );


}






function joinGroupCall(){



    let room =

    document

    .getElementById(

        "roomId"

    )

    .value

    .trim();





    if(socket && room){



        socket.send(JSON.stringify({



            type:"join_call",



            room:room



        }));



    }



    closeModal();



}
