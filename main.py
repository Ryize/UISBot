import json
import os

import requests
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup

TOKEN = os.environ.get('TOKEN')
API_URL = 'http://localhost:8000/api/'


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
        },
        '3': {
            'faculty': 'Факультет',
            'department': 'Кафедра',
        }
    }
    __apis = ['students', 'instructors', 'dissertations', 'departments',
              'instructors-by-subject',
              'instructors-by-activity', 'exam-results', 'session-results',
              'examiners', 'grades-by-instructor',
              'thesis-topics', 'thesis-supervisors', 'instructor-load', ]

    __models_params = {
        'id': 'Номер',

        # Faculty
        "name": "Название",
        "deanery": "Деканат",

        # Department
        "faculty": "Факультет",

        # InstructorCategory
        "category": "Категория преподавателя",

        # Instructor
        "first_name": "Имя",
        "last_name": "Фамилия",
        "department": "Кафедра",
        "birth_year": "Год рождения",
        "has_children": "Есть дети",
        "salary": "Зарплата",
        "gender": "Пол",
        "is_phd": "Кандидат наук",
        "is_doctor": "Доктор наук",
        "is_postgraduate_student": "Аспирант",

        # StudentGroup
        "year_of_admission": "Год поступления",

        # Student
        "student_group": "Группа студентов",
        "course": "Курс",
        "scholarship": "Размер стипендии",

        # Curriculum
        "subject": "Предмет",
        "semester": "Семестр",
        "lecture_hours": "Часы лекций",
        "seminar_hours": "Часы семинаров",
        "lab_hours": "Часы лабораторных работ",
        "consultation_hours": "Часы консультаций",
        "coursework_hours": "Часы на курсовую работу",
        "independent_work_hours": "Часы самостоятельной работы",
        "control_form": "Форма контроля",

        # TeachingAssignment
        "student_group": "Группа студентов",

        # InstructorLoad
        "teaching_assignment": "Учебное поручение",

        # ExamRecord
        "student": "Студент",
        "grade": "Оценка",
        "date": "Дата",

        # Thesis
        "title": "Тема работы",
        "defense_date": "Дата защиты"
    }

    _user_data = {}

    def main(self):
        print('Бот запущен!')
        self.bot.message_handler(commands=['start'])(self.command_start)
        self.bot.message_handler(content_types=['text'])(self.task)
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
        self.bot.send_message(chat_id, f'Нажимайте на кнопку!',
                              reply_markup=keyboard)
        self.bot.register_next_step_handler(message, self.task)

    def task(self, message):
        chat_id = message.chat.id
        title = list(self._commands[message.text].keys())[0]
        self._user_data[message.text] = {
            title: ''
        }
        self.bot.send_message(chat_id,
                              f'Укажите данные (или отправьте знак -) для параметра {self._commands[message.text][title].lower()}')
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
                                      f'Укажите данные для параметра {v.lower()}:')
                break
        self.bot.register_next_step_handler(message, self.get_data)

    def finale(self, message):
        chat_id = message.chat.id
        self.bot.send_message(chat_id, '✅ Все данные успешно получены!')
        number = list(self._user_data.keys())[0]
        clear_dict = {}
        for k, v in self._user_data[number].items():
            if v != '-':
                clear_dict[k] = v

        args = ''
        for k, v in clear_dict.items():
            args += f'{k}={v}&'

        # try:
        request_data = json.loads(requests.get(
            f'{API_URL}{self.__apis[int(number) - 1]}/?{args}').text)
        total_students = list(request_data.values())[0]
        self.bot.send_message(chat_id,
                              f'Всего студентов: {total_students}')

        if not total_students:
            return

        objs = list(request_data.values())[1]

        results = ''

        for i in objs:
            for k in i:
                if k.count('_id') == 0:
                    results += f'{self.__models_params[k]}: {i[k]}\n'
            results += '-'*32+'\n'
        self.bot.send_message(chat_id, f'Результат:\n{results}')
        # except:
        #     self.bot.send_message(chat_id,
        #                           f'Введены неверные данные!')

        self.command_start(message)


if __name__ == '__main__':
    bot = Bot()
    bot.main()
