const PublicButton = document.querySelector('.PublicButton');
let task = {
  'header': '',
  'description': '',
};

  PublicButton.onclick = function() {
    var description = document.querySelector('input[type="description_task"]');
    var header = document.querySelector('input[type="header_task"]');
    console.log(description,header)
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