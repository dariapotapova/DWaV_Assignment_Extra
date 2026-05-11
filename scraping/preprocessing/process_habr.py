import pandas as pd
import re

def clean_habr_data(input_file, output_file):

    try:
        df = pd.read_csv(input_file, encoding='utf-8')
    except:
        try:
            df = pd.read_csv(input_file, encoding='utf-8', on_bad_lines='skip')
        except:
            try:
                data = []
                with open(input_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                headers = lines[0].strip().split(',')
                for line in lines[1:]:
                    values = []
                    current = ''
                    in_quotes = False
                    for char in line:
                        if char == '"':
                            in_quotes = not in_quotes
                        elif char == ',' and not in_quotes:
                            values.append(current.strip())
                            current = ''
                        else:
                            current += char
                    values.append(current.strip())

                    if len(values) >= len(headers):
                        data.append(values[:len(headers)])

                df = pd.DataFrame(data, columns=headers)
            except Exception as e:
                print(f"Ошибка при чтении: {e}")
                return None

    print(f"Исходное количество строк: {len(df)}")
    print(f"Колонки: {list(df.columns)}")

    df = df.dropna(subset=['title', 'id'])

    initial_count = len(df)

    df = df.drop_duplicates(subset=['id'], keep='first')
    after_id = len(df)
    print(f"  После удаления по id: {after_id} (-{initial_count - after_id})")

    df = df.drop_duplicates(subset=['title', 'company'], keep='first')
    after_title_company = len(df)
    print(f"  После удаления по title+company: {after_title_company} (-{after_id - after_title_company})")

    if 'city' in df.columns:
        df = df.drop_duplicates(subset=['title', 'city'], keep='first')
        print(f"  После удаления по title+city: {len(df)} (-{after_title_company - len(df)})")

    df_clean = df.copy()

    def extract_salary_range(salary_str):
        if pd.isna(salary_str) or salary_str == 'None' or salary_str == '':
            return None, None

        salary_str = str(salary_str)

        if 'Похожие специалисты получают' in salary_str:
            salary_str = salary_str.split('Похожие специалисты получают')[0]

        salary_str = salary_str.strip()
        patterns = [
            r'от\s*(\d{1,3}(?:[ \d]{0,3})*)\s*(?:до\s*(\d{1,3}(?:[ \d]{0,3})*))?\s*₽',
            r'(\d{1,3}(?:[ \d]{0,3})*)\s*-\s*(\d{1,3}(?:[ \d]{0,3})*)\s*₽',
            r'до\s*(\d{1,3}(?:[ \d]{0,3})*)\s*₽',
            r'(\d{1,3}(?:[ \d]{0,3})*)\s*₽'
        ]

        for pattern in patterns:
            match = re.search(pattern, salary_str)
            if match:
                groups = [g for g in match.groups() if g is not None]
                if len(groups) == 2:
                    try:
                        min_val = int(re.sub(r'\s', '', groups[0]))
                        max_val = int(re.sub(r'\s', '', groups[1]))
                        return min_val, max_val
                    except:
                        continue
                elif len(groups) == 1:
                    try:
                        val = int(re.sub(r'\s', '', groups[0]))
                        if 'до' in salary_str or 'до' in match.group(0):
                            return None, val
                        elif 'от' in salary_str or 'от' in match.group(0):
                            return val, None
                        else:
                            return val, val
                    except:
                        continue
        return None, None

    salary_data = df_clean['salary'].apply(extract_salary_range)
    df_clean['salary_min'] = salary_data.apply(lambda x: x[0])
    df_clean['salary_max'] = salary_data.apply(lambda x: x[1])

    def get_salary_avg(row):
        if pd.notna(row['salary_min']) and pd.notna(row['salary_max']):
            return (row['salary_min'] + row['salary_max']) / 2
        elif pd.notna(row['salary_min']):
            return row['salary_min']
        elif pd.notna(row['salary_max']):
            return row['salary_max']
        return None

    df_clean['salary_avg_rub'] = df_clean.apply(get_salary_avg, axis=1)

    def clean_skills(skills_str):
        if pd.isna(skills_str) or skills_str == '':
            return ''
        skills_str = str(skills_str).strip('"').strip("'")
        skills_list = [s.strip() for s in skills_str.split(',') if s.strip()]
        skills_list = list(dict.fromkeys(skills_list))
        return ', '.join(skills_list[:10])

    df_clean['skills_clean'] = df_clean['skills'].apply(clean_skills)

    def detect_level(title):
        title_lower = str(title).lower()
        if any(word in title_lower for word in ['junior', 'стажер', 'intern', 'entry', 'beginner', 'jun', 'джун', 'джуниор']):
            return 'Junior'
        elif any(word in title_lower for word in ['senior', 'lead', 'team lead', 'principal', 'sen', 'сеньор']):
            return 'Senior'
        elif any(word in title_lower for word in ['middle', 'mid', 'миддл']):
            return 'Middle'
        else:
            return 'Not specified'

    df_clean['level'] = df_clean['title'].apply(detect_level)

    def detect_category(title):
        title_lower = str(title).lower()
        if any(word in title_lower for word in ['data scientist', 'data science', 'ml engineer', 'machine learning', 'ai engineer']):
            return 'Data Science'
        elif any(word in title_lower for word in ['data analyst', 'analyst', 'bi analyst', 'business intelligence', 'аналитик данных']):
            return 'Data Analytics'
        elif any(word in title_lower for word in ['data engineer', 'etl', 'data pipeline', 'data warehouse', 'инженер данных']):
            return 'Data Engineering'
        elif any(word in title_lower for word in ['python', 'java', 'c++', 'backend', 'frontend', 'fullstack', 'developer', 'software engineer', 'разработчик', 'программист']):
            return 'Software Development'
        elif any(word in title_lower for word in ['devops', 'sre', 'infrastructure', 'cloud', 'kubernetes', 'docker']):
            return 'DevOps'
        elif any(word in title_lower for word in ['qa', 'test', 'quality assurance', 'automation test', 'тестировщик']):
            return 'QA'
        else:
            return 'Other IT'

    df_clean['category'] = df_clean['title'].apply(detect_category)

    if 'city' in df_clean.columns:
        df_clean['city'] = df_clean['city'].fillna('Не указан')
        df_clean['city'] = df_clean['city'].replace('', 'Не указан')
    else:
        df_clean['city'] = 'Не указан'

    if 'remote' in df_clean.columns:
        df_clean['remote'] = df_clean['remote'].astype(bool)
    else:
        df_clean['remote'] = False

    df_clean['currency'] = 'RUB'

    expected_columns = ['source', 'id', 'title', 'company', 'city', 'remote',
                        'salary_min', 'salary_max', 'salary_avg_rub', 'currency',
                        'skills_clean', 'level', 'category', 'collected_at']

    for col in ['source', 'collected_at']:
        if col not in df_clean.columns:
            if col == 'source':
                df_clean['source'] = 'Habr'
            elif col == 'collected_at':
                df_clean['collected_at'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')

    df_final = df_clean[expected_columns].copy()
    df_final.columns = ['source', 'id', 'title', 'company', 'city', 'remote',
                        'salary_min', 'salary_max', 'salary_avg', 'currency',
                        'skills', 'level', 'category', 'collected_at']

    df_final = df_final.drop_duplicates(subset=['title', 'company'], keep='first')
    df_final = df_final.dropna(subset=['title'])

    df_final.to_csv(output_file, index=False, encoding='utf-8-sig')

    return df_final


if __name__ == "__main__":
    input_filename = '../../data/raw/habr_vacancies.csv'  # Замени на твой файл

    try:
        result = clean_habr_data(input_filename, '../../data/clean/habr_clean.csv')

        if result is not None:
            print("\nСтатистика по категориям:")
            print(result['category'].value_counts())
    except FileNotFoundError:
        print(f"Файл {input_filename} не найден!")
        print("Доступные файлы в директории:")
        import os
        for f in os.listdir('../../src'):
            if 'habr' in f.lower():
                print(f"  - {f}")