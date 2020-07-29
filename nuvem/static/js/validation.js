let labelElement = document.querySelector('.form-group input[type=file]')
    .parentElement.parentElement.firstElementChild

document.querySelector('#id_tipo').addEventListener('change', e => {
    if(e.target.value === 'keywords') {
        labelElement.innerText = 'Arquivo em Texto'
    }
    else{
        labelElement.innerText = 'Arquivo em PDF ou Texto'
    }
})