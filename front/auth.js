const submit_button = document.querySelector('button[type="submit"]');
const auth_div = document.querySelector('div.container');
let user = {
  'login': '',
  'password': '',
};

submit_button.onclick = function() {
  var login = document.querySelector('input[type="login"]');
  var password = document.querySelector('input[type="password"]');
  if (login.value === '' || password.value === '') {
    let div = document.createElement('div');
    div.className = 'empty_input';
    document.querySelector('h1').style.marginBottom = '2%';
    div.innerHTML = 'Введите логин или пароль';
    auth_div.insertBefore(div, login);
  }
  else {
    user['login'] = login.value;
    user['password'] = password.value;
    fetch('http://localhost:5000/api/authorization', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json;charset=utf-8'
      },
      body: JSON.stringify(user),
    }).then((response) => {
        if (response.ok)
            window.location.href = 'https://habr.com/ru/post/582998/';
    })
    .then((status) => {
        console.log(status);
    })
  }
}