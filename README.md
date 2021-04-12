# Nuvem de Palavras Larhud
Este serviço permite gerar uma nuvem de palavras para textos em português, inglês ou espanhol.
O intuito é que um usuário leigo possa executar uma nuvem de palavras sem que precise instalar nenhum software
em seu computador. Para tal, o usuário precisa apenas enviar um arquivo em PDF ou TXT e o serviço irá gerar a imagem com a nuvem de palavras gerada a partir do texto.

## Como instalar

    git clone git@github.com:bonfimjustino7/larhub.git larhud
    cd larhud
    virtualenv -p python3 venv
    source venv/bin/activate
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py runserver

## Como executar

Basta acessar pelo seu navegador com http://127.0.0.1:8000
