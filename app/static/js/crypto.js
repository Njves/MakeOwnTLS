
B = 0
key = localStorage.getItem('key')
if (key) {
    S_Client = key
}
function getRandomArbitrary(min, max) {
    return bigInt(parseInt(Math.random() * (max - min) + min));
}
let random = getRandomArbitrary(Math.pow(10, 15), Math.pow(10,16)-1)
function validate_fields(username, password, error_field) {
    if(!username) {
        error_field.innerText = 'Вы не ввели логин'
    }
    if(!password) {
        error_field.innerText = 'Вы не ввели пароль'
    }
}
a = random
function fetchData() {
    const xhr = new XMLHttpRequest();
    const url = '/get';

    xhr.open('GET', url, true);

    // Обработчик события загрузки
    xhr.onload = function () {
        if (xhr.status === 200) {
            const data = JSON.parse(xhr.responseText);
            console.log(data)
            const g = bigInt(data.g);
            const p = bigInt(data.p);

            console.log(typeof g)
            const requestBody = JSON.stringify({A: g.modPow(a, p)});

            xhr.open('POST', '/send_key', false);
            xhr.setRequestHeader('Content-Type', 'application/json');

            // Обработчик события загрузки
            xhr.onload = function () {
                if (xhr.status === 200) {
                    const responseData = JSON.parse(xhr.responseText);
                    B = bigInt(parseInt(responseData.B));

                    S_Client = B.modPow(a, p)
                    localStorage.setItem('key', S_Client)
                    console.log(`B = ${B}, S_Client = ${S_Client}`);
                } else {
                    console.error(`Ошибка при отправке данных. Статус: ${xhr.status}`);
                }
            };

            // Обработчик сетевых ошибок
            xhr.onerror = function () {
                console.error('Произошла сетевая ошибка');
            };

            // Отправляем запрос
            xhr.send(requestBody);

            console.log(`Получены значения g=${g} и p=${p}`);
        } else {
            console.error(`Ошибка при получении данных. Статус: ${xhr.status}`);
        }
    };

    // Обработчик сетевых ошибок
    xhr.onerror = function () {
        console.error('Произошла сетевая ошибка');
    };

    // Отправляем запрос
    xhr.send();
}
if(!key) {
    fetchData()
}

async function getView(endpoint) {
    const response = await fetch(endpoint, {
            method: 'GET'
        }
    )
    json = await response.json()
    html = base64ToArrayBuffer(json['html'])
    iv = base64ToArrayBuffer(json['iv'])
    let {key, _} = await convertKey(S_Client)
    let page = await decrypt(html, key, iv)
    document.write(page)
}

function base64ToArrayBuffer(base64) {
    const binaryString = window.atob(base64);
    const len = binaryString.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) {
        bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes.buffer;
}

async function processForm() {
    event.preventDefault()
    username = document.forms[0].username.value
    password = document.forms[0].password.value
    error_field = document.getElementById('error')
    validate_fields(username, password, error_field)
    let {key, iv} = await convertKey(S_Client);
    let encryptedName = await encrypt(username, key, iv);
    let encryptedPassword = await encrypt(password, key, iv);
    let data = {
        iv: btoa(String.fromCharCode.apply(null, iv)),
        username: encryptedName,
        password: encryptedPassword
    };
    const response = await fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    const responseData = await response
    showError(error_field, responseData.status, responseData.url)
}
async function convertKey(secretKey){
    const encoder = new TextEncoder();
    const secretKeyBuffer = encoder.encode(secretKey);
    const hashedKey = await window.crypto.subtle.digest('SHA-256', secretKeyBuffer);

    // Import the hashed key as a CryptoKey
    const key = await window.crypto.subtle.importKey(
        'raw',
        hashedKey,
        'AES-GCM',
        false,
        ['encrypt', 'decrypt']
    );

    const iv = window.crypto.getRandomValues(new Uint8Array(12));
    return {key, iv};
}

async function decrypt(text, key, iv){
    // Decode the Base64 string back into an ArrayBuffer
    const encryptedData = new Uint8Array(text);

    // Separate the encrypted data and the tag
    // Decrypt the data
    const decryptedData = await window.crypto.subtle.decrypt(
        {
            name: 'AES-GCM',
            iv: iv,
        },
        key,
        encryptedData.buffer
    );

    const decoded = new TextDecoder().decode(decryptedData);
    return decoded;
}

async function encrypt(text, key, iv) {
    // The data to encrypt
    const data = new TextEncoder().encode(text);

    // Encrypt the data
    const encryptedData = await window.crypto.subtle.encrypt(
        {
            name: 'AES-GCM',
            iv: iv
        },
        key,
        data
    );
    // Convert the encrypted data (including the tag) to a Base64 string
    const encryptedDataArray = new Uint8Array(encryptedData);
    return btoa(String.fromCharCode.apply(null, encryptedDataArray));
}

async function register(event) {
    event.preventDefault()
    username = document.forms[0].username.value
    password = document.forms[0].password.value
    has_admin = document.forms[0].has_admin.checked.toString()
    error_field = document.getElementById('error')
    validate_fields(username, password, error_field)
    let {key, iv} = await convertKey(S_Client);
    let encryptedName = await encrypt(username, key, iv);
    let encryptedPassword = await encrypt(password, key, iv);
    let encryptedAdmin = await encrypt(has_admin, key, iv);
    let data = {
        iv: btoa(String.fromCharCode.apply(null, iv)),
        username: encryptedName,
        password: encryptedPassword,
        has_admin: encryptedAdmin
    };
    const response = await fetch('/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    const responseData = await response
    showError(error_field, responseData.status, responseData.url)
}

async function addCat(event) {
    event.preventDefault()
    name = document.forms[0].name.value
    description = document.forms[0].description.value
    breed = document.forms[0].breed.value
    link = document.forms[0].link.value
    photo_link = document.forms[0].photo_link.value
    error_field = document.getElementById('error')
    let {key, iv} = await convertKey(S_Client);
    let encryptedName = await encrypt(name, key, iv);
    let encryptedDesc = await encrypt(description, key, iv);
    let encryptedBreed = await encrypt(breed, key, iv);
    let encryptedLink = await encrypt(link, key, iv);
    let encryptedPhotoLink = await encrypt(photo_link, key, iv);
    let data = {
        iv: btoa(String.fromCharCode.apply(null, iv)),
        name: encryptedName,
        description: encryptedDesc,
        breed: encryptedBreed,
        link: encryptedLink,
        photo_link:encryptedPhotoLink
    };
    console.log(JSON.stringify(data))
    const response = await fetch('/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    const responseData = await response

    window.location.href = responseData.url;
}

function showError(error_field, status, url) {
    if(status === 200) {
        window.location.href = url;
    }
    if(status === 403) {
        window.location.href = url;
    }
    if(status === 406) {
        error_field.innerText = 'Такой пользователь уже существует'
    }
    if(status === 404) {
        error_field.innerText = 'Такого пользователя не существует'
    }
    if(status === 401) {
        error_field.innerText = 'Неверный пароль'
    }
}