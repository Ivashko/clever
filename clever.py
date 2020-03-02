import vk_api
import cleverapi
import json
from cleverapi import Action

# 37e757a9ad9b42c47ad2b3bffded3229043a1cf9db08b5a9cdcb5ef6e778a8c7b2a927cb402a56bb4ddb3  12aafb2ff257a38cd495ae183dae854b5379af8eb4af1b0290d732518311e749513b6195b77de56c21212
vk = vk_api.VkApi(token="b73ac51483bc6e8b8bd4bb6a1cc20b28a2a8afd666d522a03122487decb2b761ab9b76a6a92a1c78192a2")
api1 = cleverapi.CleverApi("b75d36fb9a8fc6c859eab78b72c3eb10c916d12556ed1287099a20d4b4cfe4925f501b9d8a875a203ac48")
lp1 = cleverapi.CleverLongPoll(api1)


k=0
f=False
def get_button(label, color, payload=""):
    return {
        "action": {
            "type": "text",
            "payload": json.dumps(payload),
            "label": label
        },
        "color": color
    }


keyboard = {
    "one_time": True,
    "buttons": [
        [
            get_button(label="1", color="positive"),
            get_button(label="2", color="positive"),
            get_button(label="3", color="positive")
        ]
    ]

}

keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
keyboard = str(keyboard.decode('utf-8'))
arrayId = []
file = open('allid.txt')
st = file.readline().split()
for i in range(len(st)):
    arrayId.append(int(st[i]))

while True:
    # Главный цикл
    @lp1.question_handler()
    def new_question(event):
        global arrayId
        for i in range(len(arrayId)):
            vk.method("messages.send",
                      {"peer_id": arrayId[i], "random_id": 0, "message": str(event["question"]["number"]) + '. ' + str(event["question"]["text"])})
            vk.method("messages.send", {"peer_id": arrayId[i], "random_id": 0,
                                        "message": '1. ' + event["question"]["answers"][0]["text"]})
            vk.method("messages.send", {"peer_id": arrayId[i], "random_id": 0,
                                        "message": '2. ' + event["question"]["answers"][1]["text"]})
            vk.method("messages.send", {"peer_id": arrayId[i], "random_id": 0,
                                        "message": '3. ' + event["question"]["answers"][2]["text"],
                                        "keyboard": keyboard})

    @lp1.right_answer_handler()
    def right_answer(event):
        global body
        global id
        global k
        global f
        if 'body' in globals():
            if body.isdigit():
                if event["question"]["right_answer_id"] == (int(body) - 1):
                    vk.method("messages.send", {"peer_id": id, "random_id": 0,
                                                "message": "Вы ответили верно"})
                    if f == False:
                        api.send_action(action_id = Action.ANSWER_CORRECT, user_id=lp.user_id)

                elif k == 0:
                    vk.method("messages.send", {"peer_id": id, "random_id": 0,
                                                "message": "Вы ответили неверно, дальше игра будет не на деньги"})
                    k = 1
                    f = True
                elif k > 0:
                    vk.method("messages.send", {"peer_id": id, "random_id": 0,
                                                "message": "Вы ответили неверно"})
        else:
            f = True

    @lp1.start_game_handler()
    def start_game(event):
        api.send_action(action_id = Action.JOIN_GAME, user_id=lp.user_id)
        global arrayId
        global id
        messages = vk.method("messages.getConversations", {"offset": 0, "count": 20, "filter": "unread"})
        if messages["count"] >= 1:
            id = messages["items"][0]["last_message"]["from_id"]
            try:
                arrayId.remove(id)
            except Exception:
                file = open('allid.txt', 'a')
                file.write(str(id) + ' ')
                file.close()
            arrayId.append(id)
        for i in range(len(arrayId)):
            vk.method("messages.send",
                      {"peer_id": arrayId[i], "random_id": 0, "message": "Игра началась, жди первого вопроса"})

    @lp1.end_game_handler()
    def end_game(event):
        api.send_action(action_id = Action.WATCHED_GAME, user_id=lp.user_id)
        global arrayId
        for i in range(len(arrayId)):
            vk.method("messages.send",
                      {"peer_id": arrayId[i], "random_id": 0, "message": "Игра закончилась, жди начало следующей игры"})

    @lp1.last_time_answer_handler()
    def give_answer(event):
        global body
        global id
        global f
        global k
        question_id = event["question"]["id"]
        messages = vk.method("messages.getConversations", {"offset": 0, "count": 20, "filter": "unread"})
        if messages["count"] >= 1:
            body = messages["items"][0]["last_message"]["text"]
            id = messages["items"][0]["last_message"]["from_id"]
            try:
                api1.send_answer(coins_answer = f, game_id = lp1.game_id, answer_id = (int(body)-1), question_id = question_id, user_id = lp1.user_id)

            except Exception:
                f = True
                vk.method("messages.send", {"peer_id": id, "random_id": 0,
                                            "message": "Ошибка отправки ответа"})
                k = 1
        global arrayId
        vk.method("messages.send",
                  {"peer_id": arrayId[i], "random_id": 0, "message": "Время ответа на вопрос вышло"})

    lp1.game_waiting()
