import os

from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup

TOKEN = os.environ.get('TOKEN')


class Bot:
    bot = TeleBot(TOKEN)
    _commands = {
        '1': {
            'groups': 'Группа',
            'course': 'Курс',
            'gender': 'Пол',
            'birth_year': 'День рождения',
            'age': 'Возраст',
            'has_children': 'Наличие детей',
            'scholarship': 'Стипендия',
        },
        '2': {
            'departments': 'Кафедра',
            'faculty': 'Факультет',
            'categories': 'Категории',
            'gender': 'Пол',
            'birth_year': 'День рождения',
            'age': 'Возраст',
            'has_children': 'Наличие детей',
            'defense_date': 'Дата защиты',
            'is_phd': 'Научная степень',
            'is_doctor': 'Докторская степень',
            'postgraduate': 'Аспирант',
            'salary': 'Зарплата',
        }
    }
    _user_data = {}

    def main(self):
        print('Бот запущен!')
        self.bot.message_handler(commands=['start'])(self.command_start)
        self.bot.polling(none_stop=True)

    def command_start(self, message):
        chat_id = message.chat.id
        self._user_data = {}
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('1', '2', '3')
        keyboard.add('4', '5', '6')
        keyboard.add('7', '8', '9')
        keyboard.add('10', '11', '12')
        keyboard.add('13')
        self.bot.send_message(chat_id, f'Выдал клавиатуру!',
                              reply_markup=keyboard)
        self.bot.register_next_step_handler(message, self.task)

    def task(self, message):
        chat_id = message.chat.id
        title = list(self._commands[message.text].keys())[0]
        self._user_data[message.text] = {
            title: ''
        }
        self.bot.send_message(chat_id,
                              f'Укажите данные (или отправьте знак -) {self._commands[message.text][title].lower()}')
        self.bot.register_next_step_handler(message, self.get_data)

    def get_data(self, message):
        number = list(self._user_data.keys())[0]
        chat_id = message.chat.id
        for k, v in self._user_data[number].items():
            if v == '':
                self._user_data[number][k] = message.text
                break

        if len(self._user_data[number]) == len(self._commands[number]):
            return self.finale(message)

        for k, v in self._commands[number].items():
            if k not in self._user_data[number]:
                self._user_data[number][k] = ''
                self.bot.send_message(chat_id,
                                      f'Укажите данные {v.lower()}:')
                break
        self.bot.register_next_step_handler(message, self.get_data)

    def finale(self, message):
        chat_id = message.chat.id
        self.bot.send_message(chat_id, 'Все данные успешно получены!')
        number = list(self._user_data.keys())[0]
        clear_dict = {}
        for k, v in self._user_data[number].items():
            if v != '-':
                clear_dict[k] = v

        self.bot.send_message(chat_id, f'Ваши данные: {clear_dict}')

        self.command_start(message)


if __name__ == '__main__':
    bot = Bot()
    bot.main()
