let data = {};
for(let key in window.localStorage) {
    if (!window.localStorage.hasOwnProperty(key)) {
      continue;
    }
    data[key] = window.localStorage.getItem(key);
}

if (data !== {}) {
    document.querySelector('.lk-name').innerHTML = data['name'] + '(#)';
    document.querySelector('.nft').innerHTML = data['nft'];
    document.querySelector('.coins').innerHTML = data['coins'];
}
