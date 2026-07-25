/*
ChatMe Authentication Module

Features:
- User registration
- User login
- JWT token storage
- Automatic session restore
*/


let username = "";

let token = "";

let socket = null;


// =====================================
// REGISTER USER
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



    if(!usernameInput || !phone || !password){

        document
        .getElementById("authMessage")
        .innerHTML =
        "Please fill all fields";

        return;

    }



    try{


        let response = await fetch(

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

        data.message;



    }


    catch(error){


        console.log(error);


        document
        .getElementById("authMessage")
        .innerHTML =
        "Server error";


    }


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



    if(!phone || !password){

        document
        .getElementById("authMessage")
        .innerHTML =
        "Enter phone number and password";

        return;

    }



    try{


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

                    phone:phone,

                    password:password

                })

            }
        );



        let data =
        await response.json();





        if(!response.ok){


            document
            .getElementById("authMessage")
            .innerHTML =
            data.detail || "Login failed";


            return;


        }





        // SAVE LOGIN INFORMATION

        token =
        data.access_token;


        username =
        data.username;




        localStorage.setItem(

            "token",

            token

        );



        localStorage.setItem(

            "username",

            username

        );




        document

        .getElementById("authMessage")

        .innerHTML =

        "Login successful";





        // HIDE LOGIN PAGE

        document

        .getElementById("auth-page")

        .classList

        .add(

            "hidden"

        );




        // SHOW CHAT PAGE

        document

        .getElementById("chat-page")

        .classList

        .remove(

            "hidden"

        );





        connectSocket();


        loadProfile();


    }



    catch(error){


        console.log(error);


        document

        .getElementById("authMessage")

        .innerHTML =

        "Server connection error";


    }



}

// =====================================
// OPEN CHAT AFTER LOGIN
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




    connectSocket();


}






// =====================================
// RESTORE LOGIN SESSION
// =====================================


function checkAuthentication(){



    let savedToken =

    localStorage.getItem(

        "token"

    );



    let savedUsername =

    localStorage.getItem(

        "username"

    );





    if(savedToken && savedUsername){



        token =
        savedToken;



        username =
        savedUsername;



        openChat();



        return true;


    }



    return false;


}






// =====================================
// LOGOUT
// =====================================


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




    token="";


    username="";





    document

    .getElementById("chat-page")

    .classList

    .add("hidden");




    document

    .getElementById("auth-page")

    .classList

    .remove("hidden");


}






// =====================================
// START APPLICATION
// =====================================


window.addEventListener(

"load",

function(){


    checkAuthentication();


});
// =====================================
// WEBSOCKET CONNECTION
// =====================================


function connectSocket(){


    let protocol =
    window.location.protocol === "https:"
    ? "wss://"
    : "ws://";



    socket = new WebSocket(

        protocol +

        window.location.host +

        "/ws/" +

        username

    );



    socket.onopen=function(){


        console.log(
            "WebSocket connected"
        );


        document
        .getElementById("status")
        .innerHTML =
        "🟢 Online";


    };




    socket.onmessage=function(event){


        let data =
        JSON.parse(event.data);



        console.log(
            "Received:",
            data
        );



        if(data.type==="message"){


            displayMessage(

                data.sender,

                data.message

            );


        }


    };





    socket.onclose=function(){


        document
        .getElementById("status")
        .innerHTML =
        "🔴 Offline";


    };


}
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
function displayMessage(sender,message){


    let li =
    document.createElement("li");



    li.innerHTML = `

    <b>${sender}</b>

    <br>

    ${message}

    `;



    document
    .getElementById("messages")
    .appendChild(li);


}
// ==============================
// SEND MESSAGE
// ==============================

function sendMessage(){

    if(!socket){

        alert("Not connected");

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
// DISPLAY MESSAGE
// ==============================


function displayMessage(sender,message){


    let item =
    document.createElement("li");


    item.innerHTML = `

    <b>${sender}</b>

    <br>

    ${message}

    `;


    document
    .getElementById("messages")
    .appendChild(item);


}
