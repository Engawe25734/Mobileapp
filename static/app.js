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





// =====================================
// LOGIN USER
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



    if(!phone || !password){


        document
        .getElementById("authMessage")
        .innerHTML =
        "Enter phone and password";


        return;


    }





    try{


        let response = await fetch(

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



        console.log(
            "LOGIN RESULT:",
            data
        );





        if(data.access_token){


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



            openChat();



        }


        else{


            document

            .getElementById("authMessage")

            .innerHTML =


            data.message ||

            "Invalid login";


        }



    }



    catch(error){


        console.log(error);


        document

        .getElementById("authMessage")

        .innerHTML =

        "Cannot connect to server";


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
