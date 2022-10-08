const submit_button = document.querySelector('button[type="submit"]');
let user = {
  'login': '',
  'password': '',
};

submit_button.onclick = function() {
  var login = document.querySelector('input[type="login"]').value;
  var password = document.querySelector('input[type="password"]').value;
  user['login'] = login;
  user['password'] = password;
  fetch('/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json;charset=utf-8'
    },
    body: JSON.stringify(user),
  }).then((response) => response.json())
  .then((data) => {
    console.log(data)
  })
}