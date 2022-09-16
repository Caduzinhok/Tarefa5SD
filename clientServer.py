import queue
from flask import Flask, request
import const
import requests

app = Flask(__name__)

wait_queue = queue.Queue()
blocked = False

@app.route("/obter_permissao", methods=['GET'])
def obter_permissao():
    global permission_queue
    global blocked
    user = request.json['user']
    if blocked:
        wait_queue.put(user)
    else:
        blocked = True
        requests.post(get_user(user) + "/permission", json={"permission": True})
 

@app.route("/atualizar_permissao", methods=['POST'])
def atualizar_permissao():
    global permission_queue
    global blocked
    blocked = False
    if not wait_queue.empty():
        user = wait_queue.get()
        blocked = True
        requests.post(f"{get_user(user)}/conceder_permissao", json={"permission": True})

@app.route("/conceder_permissao", methods=['POST'])
def conceder_permissao():
    permission = request.json['permission']
    print(f"Permissao: {permission}")
    

def get_user(user):
    (ip, port) = const.registry[user]
    return f"http://{ip}:{port}"