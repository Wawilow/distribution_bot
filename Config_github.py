telegram_token = 'YOUR TOKEN HERE'

ANSWERS = \
{
    'start': {'true': 'Привет, ты подписался на рассылку!\nТеперь тебе будут приходить something.\n\nЧто бы отписатся от рассылки используй команду /stop',
              'false': 'Ты уже подписан на рассылку, если хочешь отписаться от рассылки напиши /stop'},
    'stop': {'true': 'Ты отписался от рассылки, теперь тебе больше не будут приходить оповещения!',
             'false': 'Ты подписался на рассылку!'},
    'last_distribution': 'Последня рассылка, от ',
    'admin': {'true': {
                    'message': 'Admin panel',
                    'keyboard': [[['Рассылка', 'new_distribution'], ['Cтатистика', 'stats']]]
                       },
              'false': 'Вы не являетесь администратором'},
    'cancel': 'Ваш запрос успешно отменен',
    'new_distribution': 'Please send message, he will be copied and after what distributed'
}