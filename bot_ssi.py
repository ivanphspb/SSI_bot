from sqlalchemy import engine
from telebot import asyncio_filters
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateMemoryStorage
from telebot.asyncio_handler_backends import State, StatesGroup
from sqlalchemy.sql import insert, select, func, update, delete
from sqlalchemy import and_

import asyncio

from db_utils import session_scope, prepare_db
import models

API_TOKEN = ''

bot = AsyncTeleBot(API_TOKEN)


class FormStates(StatesGroup):
    fullname = State()
    faculty = State()
    gruppa = State()
    studnumber = State()

@bot.message_handler(commands=['get_me'])
async def get_me(message):

    print(message.from_user.id, 'запрос инфы из бота')

    print(message.from_user.id, 'считываем инфу')

    async with session_scope() as session:
        q = select(models.Students.userid,
                   models.Students.fullname,
                   models.Students.faculty,
                   models.Students.gruppa,
                   models.Students.studnumber) \
            .where(models.Students.userid == message.from_user.id)
        user = (await session.execute(q)).one()

    print(message.from_user.id, 'считали, публикуем')

    await bot.send_message(message.from_user.id, f"\nИмя: {user[1]}"
                                                 f"\nФакультет: {user[2]}"
                                                 f"\nГруппа: {user[3]}"
                                                 f"\nНомер студенческого билета: {user[4]}\n")

    print(message.from_user.id, 'инфа ушла')

@bot.message_handler(commands=['start'])
async def start(message):
    async with session_scope() as session:
        # Проверка, что юзера еще нет в базе
        c = (
            (await session.execute(select(func.count()).select_from(select(models.Students.userid)
                                                                    .where(
                models.Students.userid == message.from_user.id)
                                                                    .subquery()))).scalar_one()
        )

        # Если юзера нет в базе, то добавим
        if not c:
            await session.execute(insert(models.Students).values(userid=message.from_user.id,
                                                                 fname=message.from_user.first_name,
                                                                 lname=message.from_user.last_name,
                                                                 uname=message.from_user.username))
            print(message.from_user.id, 'в базе нет, добавили')
        else:
            print(message.from_user.id, 'в базе есть')

    await bot.send_message(message.from_user.id,
                           "Вас приветствует Студенческая Изибирательная комиссия СЗИУ РАНХиГС. "
                           "Чтобы получить доступ к тесту и творческому заданию, пройдите регистрацию")
    print(message.from_user.id, 'приветсвие ушло')
    await bot.send_message(message.from_user.id, "Ваше полное ФИО (Пример: Петров Иван Сергеевич):")

    print(message.from_user.id, 'вопрос про фио ушёл')

    # выставляем следующий шаг
    await bot.set_state(message.from_user.id, "fullname", message.chat.id)

    print(message.from_user.id, 'отправились к факу')


@bot.message_handler(content_types=['text'], state="fullname")
async def get_faculty(message):  # получаем факультет

    print(message.from_user.id, 'дошли до фака')

    # Обновляем юзеру имя

    async with session_scope() as session:
        await session.execute(update(models.Students).where(models.Students.userid == message.from_user.id)
                              .values(fullname=message.text))

    print(message.from_user.id, 'внесли имя')

    await bot.send_message(message.from_user.id, 'Ваш факультет (Пример: ФМОПИ):')

    print(message.from_user.id, 'вопрос про фак ушёл')

    await bot.set_state(message.from_user.id, "faculty", message.chat.id)

    print(message.from_user.id, 'отправились к группе')


@bot.message_handler(content_types=['text'], state="faculty")
async def get_group(message):  # получаем группу

    print(message.from_user.id, 'дошли до группы')

    # Обновляем юзеру факультет
    async with session_scope() as session:
        await session.execute(update(models.Students).where(models.Students.userid == message.from_user.id)
                              .values(faculty=message.text))

    print(message.from_user.id, 'внесли фак')

    await bot.send_message(message.from_user.id, 'Ваша группа (Пример: ПЛ-3-20-02):')

    print(message.from_user.id, 'вопрос про группу ушёл')

    await bot.set_state(message.from_user.id, "gruppa", message.chat.id)

    print(message.from_user.id, 'пошли к студаку')


@bot.message_handler(content_types=['text'], state="gruppa")
async def get_studnumber(message):  # получаем студак

    print(message.from_user.id, 'пришли к студаку')

    # Обновляем юзеру группу

    async with session_scope() as session:
        await session.execute(update(models.Students).where(models.Students.userid == message.from_user.id)
                              .values(gruppa=message.text))

    print(message.from_user.id, 'записали группу')

    await bot.send_message(message.from_user.id, 'Номер вашего студенческого билета (Как в самом билете!!!):')

    print(message.from_user.id, 'вопрос про билет ушёл')

    await bot.set_state(message.from_user.id, "studnumber", message.chat.id)

    print(message.from_user.id, 'пошли к записи студака')


@bot.message_handler(content_types=['text'], state="studnumber")
async def get_studreg(message):  # Обновляем юзеру студак # ищем в списке кандидатов

    print(message.from_user.id, 'пришли к записи студака')

    async with session_scope() as session:
        await session.execute(update(models.Students).where(models.Students.userid == message.from_user.id)
                              .values(studnumber=message.text))

    print(message.from_user.id, 'записали студак')

    await bot.send_message(message.from_user.id, 'Напишите "проверка" ')

    print(message.from_user.id, 'вопрос про запрос проверки ушёл')

    await bot.set_state(message.from_user.id, "anal", message.chat.id)

    print(message.from_user.id, 'пошли к проверке')

    print(await bot.get_state(message.from_user.id, message.chat.id))


@bot.message_handler(content_types=['text'], state="anal")
async def do_anal(message):  # ищем в списке кандидатов

    print(message.from_user.id, 'пришли к проверке')

    async with session_scope() as session:
        # Получение данных о юзере

        print(message.from_user.id, 'получаем данные о юзере')

        q = select(models.Students.userid,
                   models.Students.fullname,
                   models.Students.faculty,
                   models.Students.gruppa,
                   models.Students.studnumber) \
            .where(models.Students.userid == message.from_user.id)
        user = (await session.execute(q)).one()

        # Проверка, есть ли юзер в базе кандидатов

        print(message.from_user.id, 'проверка имени')

        c = (   # Проверка имени
            (await session.execute(select(func.count()).select_from(select(models.Candidates.fullname)
                                                                    .where(
                models.Candidates.fullname == user[1])
                                                                    .subquery()))).scalar_one()
        )

        if not c:
            await bot.send_message(message.from_user.id, 'Вас нет в базе кандидатов. Доступ запрещён. Либо вы не были '
                                                         'зарегистрированы Избирательной комиссией, либо неверно указали '
                                                         'данные. Для того, чтобы проверить правильность информации, '
                                                         'записанной в бот, введите команду "/get_me". Если данные '
                                                         'указаны неверно, введите "/start" и пройдите повторную '
                                                         'регистрацию в боте'
            )
            print(message.from_user.id, 'ФИО в базе нет')
            return
        else:
            print(message.from_user.id, 'ФИО в базе есть')

        print(message.from_user.id, 'проверка фака')

        c1 = (  # Проверка факультета
            (await session.execute(select(func.count()).select_from(select(models.Candidates.faculty)
                                                                    .where(
                and_(
                    models.Candidates.fullname == user[1],
                    models.Candidates.faculty == user[2]
                )
            )
                                                                    .subquery()))).scalar_one()
        )

        if not c1:
            await bot.send_message(message.from_user.id, 'Вас нет в базе кандидатов. Доступ запрещён. Либо вы не были '
                                                         'зарегистрированы Избирательной комиссией, либо неверно указали '
                                                         'данные. Для того, чтобы проверить правильность информации, '
                                                         'записанной в бот, введите команду "/get_me". Если данные '
                                                         'указаны неверно, введите "/start" и пройдите повторную '
                                                         'регистрацию в боте')
            print(message.from_user.id, 'фак не совпадает')
            return
        else:
            print(message.from_user.id, 'фак совпадает')

        print(message.from_user.id, 'проверка группы')

        c2 = (  # Проверка группы
            (await session.execute(select(func.count()).select_from(select(models.Candidates.gruppa)
                                                                    .where(
                and_(
                    models.Candidates.fullname == user[1],
                    models.Candidates.faculty == user[2],
                    models.Candidates.gruppa == user[3]
                )
            )
                                                                    .subquery()))).scalar_one()
        )

        if not c2:
            await bot.send_message(message.from_user.id, 'Вас нет в базе кандидатов. Доступ запрещён. Либо вы не были '
                                                         'зарегистрированы Избирательной комиссией, либо неверно указали '
                                                         'данные. Для того, чтобы проверить правильность информации, '
                                                         'записанной в бот, введите команду "/get_me". Если данные '
                                                         'указаны неверно, введите "/start" и пройдите повторную '
                                                         'регистрацию в боте')
            print(message.from_user.id, 'группа не совпадает')
            return
        else:
            print(message.from_user.id, 'группа совпадает')

        print(message.from_user.id, 'проверка студака')

        c3 = (
            (await session.execute(select(func.count()).select_from(select(models.Candidates.studnumber)
                                                                    .where(
                and_(
                    models.Candidates.fullname == user[1],
                    models.Candidates.faculty == user[2],
                    models.Candidates.gruppa == user[3],
                    models.Candidates.studnumber == user[4]
                )
            )
                                                                    .subquery()))).scalar_one()
        )


        if not c3:
            await bot.send_message(message.from_user.id, 'Вас нет в базе кандидатов. Доступ запрещён. Либо вы не были '
                                                         'зарегистрированы Избирательной комиссией, либо неверно указали '
                                                         'данные. Для того, чтобы проверить правильность информации, '
                                                         'записанной в бот, введите команду "/get_me". Если данные '
                                                         'указаны неверно, введите "/start" и пройдите повторную '
                                                         'регистрацию в боте')
            print(message.from_user.id, 'студак не совпадает')
            return

        else:
            await bot.send_message(message.from_user.id, 'Уважаемый кандидат! \n'
                                                         'Перед прохождением теста обязательно прочитайте инструкцию, '
                                                         'которую Вы увидите после того, как перейдете по ссылке. \n'
                                                         'Результаты, отправленные после 23:59 05.04.2022 г., '
                                                         'приниматься не будут, в противном случае результат за тест '
                                                         'будет «0» баллов. Система автоматически будет оповещать '
                                                         'Рабочую группу по отбору в ССИ XVIII созыва о том, что Вы '
                                                         'завершили прохождение теста. \n'
                                                         'Тест, как и все этапы отбора, проходится кандидатом '
                                                         'самостоятельно: без помощи других лиц и не за других лиц. \n'
                                                         '\n'
                                                         'Творческое задание будет приниматься Председателем СИК СЗИУ '
                                                         'РАНХиГС в личных сообщениях в социальной сети «VK»: '
                                                         'https://vk.com/alexander_dobak до 23:59 08.04.2022 г. '
                                                         'Творческие задания, отправленные после 23:59 08.04.2022 г., '
                                                         'приниматься не будут, в противном случае результат за '
                                                         'творческое задание будет «0» баллов. \n'
                                                         'Для того, чтобы творческое задание было принято, необходимо '
                                                         'направить его в WORD-формате. \n'
                                                         'Творческое задание, как и все этапы отбора, выполняется '
                                                         'кандидатом самостоятельно: без помощи других лиц и не за '
                                                         'других лиц. \n'
                                                         '\n'
                                                         'Желаем удачи!')
            print(message.from_user.id, 'всё совпало, задание ушло')


bot.add_custom_filter(asyncio_filters.StateFilter(bot))
asyncio.run(prepare_db())
asyncio.run(bot.polling())
