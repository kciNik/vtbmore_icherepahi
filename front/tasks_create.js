const PublicButton = document.querySelector('.PublicButton');
const team = document.querySelector('button[type="tag_team"]');
const ind = document.querySelector('button[type="tag_team"]');
const tok = window.localStorage.getItem('token');
let task = {
  'name': '',
  'description': '',
  'reward_id': '',
  'is_boss': false,
  'target': ''
};

let reward = {
  'value_coins': '',
  'value_nft': '', 
  'is_reward_collected': false
};

team.onclick = function() {
  task['target'] = 'TeamsOnly';
}

ind.onclick = function() {
  task['target'] = 'Individual';
}

PublicButton.onclick = function() {
  var description = document.querySelector('input[type="description_task"]').value;
  var header = document.querySelector('input[type="header_task"]').value;
  var in_coin = document.querySelector('input[type="count_coins"]').value;
  var in_nft = document.querySelector('input[type="count_nft"]').value;
  task['name'] = header;
  task['description'] = description;
  reward['value_coins'] = in_coin;
  reward['value_nft'] = in_nft;
  fetch('http://localhost:5000/user/create_reward', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json;charset=utf-8',
      'Authorization': 'Bearer ' + tok
    },
    body: JSON.stringify(reward),
  }).then(response => {
    response.json().then(data => {
      task['reward_id'] = data['id'];
      fetch('http://localhost:5000/user/create_task', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json;charset=utf-8',
      'Authorization': 'Bearer ' + tok
    },
    body: JSON.stringify(task),
  }).then((response) => {
      if (response.ok)
          window.location.href = 'tasks_page_cw.html';
  })
    })
  })
}