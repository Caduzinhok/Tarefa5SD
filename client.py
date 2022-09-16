import queue
import sys
import threading
from time import sleep
import const
from flask import Flask, request
import requests
import os
app = Flask(__name__)

# ------------------- Coordinator -------------------

wait_queue = queue.Queue()
blocked = False


@app.route("/obter_permissao", methods=['POST'])
def obter_permissao():
    global permission_queue
    global blocked
    print(f"blocked: {blocked}")
    print(f"Queue: {wait_queue.queue}")
    user = request.json['user']
    print(f"Usuario {user} está pedindo permissao")
    if blocked:
        wait_queue.put(user)
    else:
        blocked = True
        print("Bloqueado neste instante")
        requests.post(get_user(user) + "/conceder_permissao", json={"permission": True})
    return {}
 

@app.route("/atualizar_permissao", methods=['POST'])
def atualizar_permissao_coordinator():
    global permission_queue
    global blocked
    blocked = False
    if not wait_queue.empty():
        user = wait_queue.get()
        blocked = True
        requests.post(f"{get_user(user)}/conceder_permissao", json={"permission": True})
    return {}

# ------------------- -------------------

# ------------------- Client -------------------
permission = False
coordinator = False
coordnator_name = "Coordinator"

@app.route("/conceder_permissao", methods=['POST'])
def conceder_permissao():
    global permission
    permission_from_coordinator = request.json['permission']
    if permission_from_coordinator:
        permission = True
        print("Permissao Garantida")
    return {}

def get_user(user):
    (ip, port) = const.registry[user]
    return f"http://{ip}:{port}"

def request_score():
    wait_for_permission()
    response = requests.get(f"http://{const.CHAT_SERVER_HOST}:{const.CHAT_SERVER_PORT}/get_score")
    print(f"Placar atual: {response.json()['score']}")
    atualizar_permissao()

def start_server(i_am):
    (ip, port) = const.registry[i_am]
    app.run(host=ip, port=port)

def update_score():
    request_score()
    wait_for_permission()
    new_score = input("Entre com um novo placar: ")
    try:
        response = requests.post(f"http://{const.CHAT_SERVER_HOST}:{const.CHAT_SERVER_PORT}/update_score", json={"score": new_score})
        print(f"Novo placar: {response.json()['score']}")
        print("Placar atualizado com sucesso")
    except:
        print(response.json()['error'])
    finally:
        atualizar_permissao()

def wait_for_permission():
    global permission
    if not permission:
        requests.post(f"{get_user(coordnator_name)}/obter_permissao", json={"user": i_am})
    while permission == False:
        sleep(1)
        print("Aguardando permissao...")
    return True

def atualizar_permissao():
    global permission
    permission = False
    requests.post(f"{get_user(coordnator_name)}/atualizar_permissao", json={"user": i_am})

options = {
    "1": request_score,
    "2": update_score,
    "3": exit
}

if __name__ == "__main__":
    i_am = str(sys.argv[1])
    coordnator_name = str(sys.argv[2])

    if i_am == coordnator_name:
        coordinator = True
        print("Eu sou o coordenador")
    threading.Thread(target=start_server, args=(i_am,), daemon=True).start()
    while True:
        print("--------------------------------------------------------------------------------")
        print("1. Obter Placar")
        print("2. Atualizar Placar")
        print("3. Sair")
        option = input("Escolha uma opção: ")
        print("--------------------------------------------------------------------------------")
        if option not in options:
            print("Opção Invalida")
            continue
        os.system('cls||clear')
        options[option]()