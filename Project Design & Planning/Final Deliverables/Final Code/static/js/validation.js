// function valid(){
//     var pwd = document.getElementById("password");
//     var cpwd = document.getElementById("cpassword");


//     if(pwd.value >= 6 || cpwd.value >=6){
//         alert("Password must be minimum of 6 characters");
//         return false;
//     }


//     else if(pwd.value != cpwd.value){
//         alert("Passwords don't Match");
//         return false;
//     }
//     return true;

// }


function validatepassword() {
    var password = document.getElementById('password-error');
    var cpassword = document.getElementById('cpassword-error');
    var passwordcheck = document.getElementById('password').value.trim();
    var passwordcheck1 = document.getElementById('cpassword').value.trim();
    if (passwordcheck === '') {
        password.innerHTML = 'Please create your password';
        document.getElementById("password").style.borderColor = "red";
        return false;
    }
    if (!passwordcheck.match(/^(?=.*[0-9])(?=.*[!@#$%^&*])[a-zA-Z0-9!@#$%^&*]{7,15}$/)) {
        password.innerHTML = '7-15 characters[At least one numeric digit and special character]';
        document.getElementById("password").style.borderColor = "red";
        return false;
    }
    if (passwordcheck.match(/^(?=.*[0-9])(?=.*[!@#$%^&*])[a-zA-Z0-9!@#$%^&*]{7,15}$/)) {
        password.innerHTML = '';
        document.getElementById("password").style.borderColor = "Green";
    }
    if (passwordcheck1 === '') {
        cpassword.innerHTML = 'Please confirm your password';
        document.getElementById("cpassword").style.borderColor = "red";
        return false;
    }
    if (passwordcheck1 !== passwordcheck) {
        cpassword.innerHTML = 'Password does not match';
        document.getElementById("cpassword").style.borderColor = "red";
        return false;
    }
    if (passwordcheck1 === passwordcheck) {
        cpassword.innerHTML = '';
        document.getElementById("cpassword").style.borderColor = "Green";
        return true;
    }

}