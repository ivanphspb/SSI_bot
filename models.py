import asyncio
import csv

from sqlalchemy import Column, Integer, String
from sqlalchemy.sql import insert

import db_utils
from db_utils import Base as BaseModel
from db_utils import session_scope

from numpy import genfromtxt


# from time import time
# from datetime import datetime
# from sqlalchemy import Column, Integer, Float, Date
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker


class Students(BaseModel):
    __tablename__ = 'students'
    userid = Column(Integer, nullable=False, unique=True, primary_key=True)
    fname = Column(String, nullable=True)
    lname = Column(String, nullable=True)
    uname = Column(String, nullable=True)
    fullname = Column(String, nullable=True)
    faculty = Column(String, nullable=True)
    gruppa = Column(String, nullable=True)
    studnumber = Column(String, nullable=True)


class Candidates(BaseModel):
    __tablename__ = 'candidates'
    candidateid = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    fullname = Column(String, nullable=False)
    faculty = Column(String, nullable=False)
    gruppa = Column(String, nullable=True)
    studnumber = Column(String, nullable=False)


async def load_data(file_name):
    with open(file_name, 'r', encoding='UTF-8') as file:  # Открываем файл для чтения
        csv_file = csv.reader(file)   # Читаем файл как csvшку
        async with session_scope() as session:  # Открываем сессию для работы с базой
            for c in csv_file:  # Для каждого студента в цсшке
                print(f"{c[0]} добавлен в базу")    # Просто принт для понятности во время работы скрипта
                await session.execute(insert(Candidates).values(fullname=c[0],  # Добавляем прочитаного студента в базы
                                                                faculty=c[1],
                                                                gruppa=c[2],
                                                                studnumber=c[3]))


if __name__ == "__main__":
    asyncio.run(load_data('candidates.csv'))  # Запускаем асинхронную функцию