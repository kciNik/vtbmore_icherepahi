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
    if (!document.querySelector('.empty_input')) {
      let div = document.createElement('div');
      div.className = 'empty_input';
      document.querySelector('h1').style.marginBottom = '2%';
      div.innerHTML = 'Введен неверный логин или пароль';
      auth_div.insertBefore(div, login);
    }
  }
  else {
    user['login'] = login.value;
    user['password'] = password.value;
    fetch('http://localhost:5000/api/tokens', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json;charset=utf-8',
        'Authorization': 'Basic ' + btoa(login.value + ":" + password.value)
      },
      body: JSON.stringify(user),
    }).then (response => { response.json().then(data => {
      window.localStorage.setItem('token',data['token']);
      fetch('http://localhost:5000/api/authorization', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json;charset=utf-8',
        'Authorization': 'Bearer ' + data['token']
      },
      body: JSON.stringify(user),
    }).then((response) => {
      if (response.status == 200) {
        window.location.href = 'main.html';
        response.json().then(data => {
          for (key in data) {
            window.localStorage.setItem(key, data[key]);
          };
        })
      }
      else {
        if (!document.querySelector('.empty_input')) {
          let div = document.createElement('div');
          div.className = 'empty_input';
          document.querySelector('h1').style.marginBottom = '2%';
          div.innerHTML = 'Введен неверный логин или пароль';
          auth_div.insertBefore(div, login);
        }
      }
  })
    })})
  }
}