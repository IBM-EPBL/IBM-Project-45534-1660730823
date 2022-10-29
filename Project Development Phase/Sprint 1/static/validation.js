
function valid(){
    var pwd = document.getElementById("password");
    var cpwd = document.getElementById("cpassword");

    
    if(pwd.value >= 6 || cpwd.value >=6){
        alert("Password must be minimum of 6 characters");
        return false;
    }


    else if(pwd.value != cpwd.value){
        alert("Passwords don't Match");
        return false;
    }
    return true;
      
}