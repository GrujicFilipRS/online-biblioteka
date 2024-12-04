let usernameInput = document.getElementById('username-input');
let pwdInput = document.getElementById('pwd-input');
let loginBtn = document.getElementById('login-btn');

usernameInput.addEventListener('input', function() {
    onInputChange();
});
pwdInput.addEventListener('input', function() {
    onInputChange();
});

function onInputChange() {
    if (usernameInput.value == '' || pwdInput.value == '') {
        loginBtn.disabled = true;
    } else {
        loginBtn.disabled = false;
    }
}