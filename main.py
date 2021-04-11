import json
import random

from flask import Flask, request
from flask_ngrok import run_with_ngrok

app = Flask(__name__)
run_with_ngrok(app)

player_class = {
    'rogue': {
        'name': 'лучник',
        'img': '1540737/589067242bb745888af3'
    },
    'warrior': {
        'name': 'воин',
        'img': '213044/3f782265ae22fc4c70bf'
    },
    'mage': {
        'name': 'маг',
        'img': '965417/cc20291e933d36005bfb'
    }
}

enemy_class = [
    {'name': 'Гоблин', 'img': '1652229/d7631868d5d036309926'},
    {'name': 'Тролль', 'img': '965417/328443a8bbada504fe7a'},
    {'name': 'Оборотень', 'img': '1540737/2d30e575d9001a52ed76'},
]


def offer_class(user_id, req, res):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.FIO':
            if name := entity['value'].get('first_name'):
                name = name.capitalize()
                session_state[user_id]['first_name'] = name
                res['response']['txt'] = f'Приятно познакомиться {name}, выбери свой класс'
                res['response']['card'] = {
                    'type': 'item_list',
                    'header': {
                        'text': f'Приятно познакомиться {name}, выбери свой класс'
                    },
                    'items': [
                        {
                            'image_id': player_class['warrior']['img'],
                            'title': player_class['warrior']['name'],
                            'description': 'Меч - грозное оружие',
                            'button': {
                                'text': 'Выбрать война',
                                'payload': {'class': 'warrior'}
                            }
                        },
                        {
                            'image_id': player_class['mage']['img'],
                            'title': player_class['mage']['name'],
                            'description': 'Фаербол - грозное оружие',
                            'button': {
                                'text': 'Выбрать мага',
                                'payload': {'class': 'mage'}
                            }
                        },
                        {
                            'image_id': player_class['rogue']['img'],
                            'title': player_class['rogue']['name'],
                            'description': 'Лук - грозное оружие',
                            'button': {
                                'text': 'Выбрать лучника',
                                'payload': {'class': 'rogue'}
                            }
                        }
                    ],
                    'footer': {
                        'text': 'Не ошибись с выбором'
                    }
                }
                session_state[user_id] = {
                    'state': 2
                }
                return
    else:
        res['response']['text'] = 'Не расслышала имя. Повторите пожалуйств'


def offer_adventure(user_id, req, res):
    try:
        selected_class = req['request']['payload']['class']
    except KeyError:
        res['response']['txt'] = 'Пожалуйста, выберите класс'
    session_state[user_id].update({
        'class': selected_class,
        'state': 3
    })
    res['response'] = {
        'text': f'{selected_class.capitalize()} - прекрасный выбор',
        'card': {
            'type': 'BigImage',
            'image_id': player_class[selected_class]['img'],
            'title': f'{selected_class.capitalize()} - прекрасный выбор'
        },
        'buttons': [
            {
                'title': 'В бой',
                'payload': {'fight': True},
                'hide': True
            },
            {
                'title': 'Завершить приключение',
                'payload': {'fight': True},
                'hide': True
            }
        ]
    }


def offer_fight(user_id, req, res):
    try:
        answer = req['request']['payload']['fight']
    except KeyError:
        res['response']['text'] = 'Пожалуйста, выберите действие'
        return
    if answer:
        enemy = random.choice(enemy_class)
        session_state[user_id]['state'] = 4
        res['response'] = {
            'text': f'Ваш противник - {enemy["name"]}',
            'card': {
                'type': 'BigImage',
                'image_id': enemy['img'],
                'title': f"Ваш противник - {enemy['name']}"
            },
            'buttons': [
                {
                    'title': 'Ударить',
                    'payload': {'fight': True},
                    'hide': True
                },
                {
                    'title': 'Убежать',
                    'payload': {'fight': True},
                    'hide': True
                }
            ]
        }
    else:
        end_game(user_id, req, res)


def end_game(user_id, req, res):
    try:
        answer = req['request']['payload']['fight']
    except KeyError:
        res['response']['text'] = 'Пожалуйста, выбирите действие'
        return
    if not answer:
        res['response']['text'] = 'Ваше приключение закончилось, не успев начаться'
    else:
        res['response']['text'] = 'Вы победили противника, о Вашем подвиге не забудут!'
    res['response']['end_session'] = True


@app.route('/post', methods=['POST'])
def get_alice_request():
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(request.json, response)
    return json.dumps(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']
    if req['session']['new']:
        res['response']['text'] = 'Привет, мы тут играем в игру. Назови свое имя'
        session_state['user_id'] = {
            'state': 1
        }
        return
    states[session_state[user_id]['state']](user_id, req, res)


states = {
    1: offer_class,
    2: offer_adventure,
    3: offer_fight,
    4: end_game
}
session_state = {}

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
