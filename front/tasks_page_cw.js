const MyTasksButton = document.querySelector('.MyTasksButton');
const CheckButton = document.querySelector('.CheckButton');
const CreateButton = document.querySelector('.button');
let user = {
  'login': 'ilya',
  'password': '123',
};

MyTasksButton.onclick = function() {
    fetch('http://localhost:5000/api/task/all', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json;charset=utf-8'
      },
      body: JSON.stringify(user),
    }).then((response) => {
        if (response.ok)
            //window.location.href = 'https://habr.com/ru/post/582998/';
          console.log(response)
          response.json();
    }).then((data) => {
      console.log(data)
    })
  }


  CheckButton.onclick = function() {
    fetch('http://localhost:5000/api/authorization', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json;charset=utf-8'
      },
      body: JSON.stringify(user),
    }).then((response) => {
        if (response.ok)
            //window.location.href = 'https://habr.com/ru/post/582998/';
          console.log(response)
          response.json();
    }).then((data) => {
      console.log(data)
    })
  }

  CreateButton.onclick = function() {
            window.location.href = 'http://127.0.0.1:5500/front/tasks_create.html';
  }