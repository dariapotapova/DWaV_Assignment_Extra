import pandas as pd
import re
import numpy as np

def prepare_for_dashboard():
    """Объединяет и подготавливает данные для дашборда"""

    # Загрузка
    habr = pd.read_csv('../../data/clean/habr_clean.csv')
    themuse = pd.read_csv('../../data/clean/themuse_clean.csv')

    # Добавляем регион
    habr['region'] = 'Russia'
    themuse['region'] = 'International'

    # Объединяем
    all_jobs = pd.concat([habr, themuse], ignore_index=True)

    # Удаляем дубликаты по названию и компании
    all_jobs = all_jobs.drop_duplicates(subset=['title', 'company'], keep='first')

    # Дата парсинга
    all_jobs['collected_at'] = pd.to_datetime(all_jobs['collected_at'])

    # Месяц для фильтрации
    all_jobs['month'] = all_jobs['collected_at'].dt.strftime('%Y-%m')

    # Конвертируем зарплату для сравнения (USD -> RUB по курсу ~90)
    def normalize_salary(row):
        if pd.isna(row['salary_avg']):
            return None
        if row['currency'] == 'USD':
            return row['salary_avg'] * 90  # Курс для сравнения
        return row['salary_avg']

    all_jobs['salary_avg_rub_norm'] = all_jobs.apply(normalize_salary, axis=1)

    # Сохраняем
    all_jobs.to_csv('all_vacancies_clean.csv', index=False, encoding='utf-8-sig')

    return all_jobs

# Запуск
final_df = prepare_for_dashboard()