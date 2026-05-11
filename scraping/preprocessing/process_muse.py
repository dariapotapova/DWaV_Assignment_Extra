import pandas as pd
import re

def detect_category(title):
    if pd.isna(title):
        return 'Other IT'

    title_lower = str(title).lower()

    if any(word in title_lower for word in ['data scientist', 'data science', 'ml engineer', 'machine learning', 'ai engineer']):
        return 'Data Science'
    elif any(word in title_lower for word in ['data analyst', 'analyst', 'bi analyst', 'business intelligence']):
        return 'Data Analytics'
    elif any(word in title_lower for word in ['data engineer', 'etl', 'data pipeline', 'data warehouse']):
        return 'Data Engineering'
    elif any(word in title_lower for word in ['python', 'java', 'c++', 'backend', 'frontend', 'fullstack', 'developer', 'software engineer']):
        return 'Software Development'
    elif any(word in title_lower for word in ['devops', 'sre', 'infrastructure', 'cloud', 'kubernetes', 'docker']):
        return 'DevOps'
    elif any(word in title_lower for word in ['qa', 'test', 'quality assurance', 'automation test']):
        return 'QA'
    elif any(word in title_lower for word in ['product', 'manager', 'product manager']):
        return 'Product Management'
    else:
        return 'Other IT'

def process_themuse_data(input_file, output_file):

    df = pd.read_csv(input_file)

    print(f"Исходное количество: {len(df)}")
    print(f"Колонки: {list(df.columns)}")

    initial_count = len(df)
    print(f"\nНачинаем удаление дубликатов...")

    df = df.drop_duplicates(subset=['id'], keep='first')
    after_id = len(df)
    print(f"  После удаления по id: {after_id} (-{initial_count - after_id})")

    df = df.drop_duplicates(subset=['title', 'company'], keep='first')
    after_title_company = len(df)
    print(f"  После удаления по title+company: {after_title_company} (-{after_id - after_title_company})")

    if 'url' in df.columns:
        df = df.drop_duplicates(subset=['title', 'url'], keep='first')
        print(f"  После удаления по title+url: {len(df)} (-{after_title_company - len(df)})")

    df['category'] = df['title'].apply(detect_category)

    df['remote_clean'] = False

    def clean_city_and_remote(city_val, current_remote):
        if pd.isna(city_val):
            return 'Не указан', False

        city_str = str(city_val).strip()

        remote_keywords = [
            'Remote', 'remote', 'REMOTE',
            'Flexible / Remote', 'Flexible/Remote',
            'Remote / Flexible', 'Remote/Flexible',
            'Worldwide', 'Anywhere', 'Anywhere in the World',
            'Flexible', 'flexible'
        ]

        is_remote = any(kw in city_str for kw in remote_keywords)

        if is_remote:
            return None, True

        city_clean = re.sub(r',\s*[A-Z]{2}(?:\s+USA)?$', '', city_str)
        city_clean = re.sub(r',\s*[A-Za-z\s]+$', '', city_clean)
        city_clean = re.sub(r'\s*\([^)]+\)$', '', city_clean)
        city_clean = re.sub(r'\s+City$', '', city_clean)

        return city_clean.strip(), False

    result = df['city'].apply(lambda x: clean_city_and_remote(x, False))
    df['city_clean'] = result.apply(lambda x: x[0])
    df['remote_clean'] = result.apply(lambda x: x[1])

    if 'remote' in df.columns:
        df['remote_clean'] = df['remote_clean'] | df['remote'].fillna(False).astype(bool)

    def extract_country(city_str):
        if pd.isna(city_str):
            return 'Не указана'

        city_lower = str(city_str).lower()

        country_map = {
            'USA': ['el segundo', 'new york', 'rogers', 'san francisco', 'lockhart',
                    'chicago', 'woodinville', 'redmond', 'austin', 'seattle',
                    'boston', 'denver', 'atlanta', 'los angeles', 'san jose',
                    'palo alto', 'mountain view', 'portland', 'las vegas',
                    'san diego', 'philadelphia', 'dallas', 'houston', 'miami',
                    'orlando', 'raleigh', 'salt lake city', 'st. louis'],
            'India': ['bangalore', 'chennai', 'mumbai', 'delhi', 'hyderabad',
                      'pune', 'kolkata', 'gurgaon', 'noida', 'ahmedabad'],
            'UK': ['london', 'manchester', 'edinburgh', 'birmingham', 'bristol',
                   'leeds', 'liverpool', 'newcastle', 'cambridge', 'oxford'],
            'Canada': ['toronto', 'vancouver', 'montreal', 'ottawa', 'calgary',
                       'edmonton', 'quebec', 'winnipeg'],
            'Germany': ['berlin', 'munich', 'hamburg', 'frankfurt', 'cologne',
                        'stuttgart', 'dusseldorf', 'leipzig', 'dresden'],
            'France': ['paris', 'lyon', 'marseille', 'toulouse', 'nice',
                       'nantes', 'strasbourg', 'montpellier'],
            'Netherlands': ['amsterdam', 'rotterdam', 'utrecht', 'the hague',
                            'eindhoven', 'groningen'],
            'Singapore': ['singapore'],
            'Australia': ['sydney', 'melbourne', 'brisbane', 'perth', 'adelaide',
                          'canberra', 'hobart'],
            'Spain': ['madrid', 'barcelona', 'valencia', 'sevilla', 'zaragoza'],
            'Italy': ['rome', 'milan', 'turin', 'naples', 'florence', 'bologna'],
            'Switzerland': ['zurich', 'geneva', 'bern', 'basel', 'lausanne'],
            'Sweden': ['stockholm', 'gothenburg', 'malmo', 'uppsala'],
            'Israel': ['tel aviv', 'haifa', 'jerusalem', 'ramat gan'],
            'UAE': ['dubai', 'abu dhabi', 'sharjah'],
            'Japan': ['tokyo', 'osaka', 'yokohama', 'nagoya', 'sapporo'],
            'China': ['beijing', 'shanghai', 'shenzhen', 'guangzhou', 'hangzhou'],
        }

        for country, cities in country_map.items():
            if any(city in city_lower for city in cities):
                return country

        return 'Other'

    df['country'] = df['city_clean'].apply(extract_country)

    df.loc[df['remote_clean'] & (df['country'] == 'Other'), 'country'] = 'Remote'

    df['city_clean'] = df['city_clean'].fillna('Не указан')
    df['city_clean'] = df['city_clean'].replace('None', 'Не указан')

    df = df.drop_duplicates(subset=['id', 'title', 'company'], keep='first')

    final_columns = ['source', 'id', 'title', 'company', 'city_clean', 'country',
                     'remote_clean', 'salary', 'salary_avg_usd', 'level', 'category',
                     'url', 'publication_date', 'collected_at']

    for col in final_columns:
        if col not in df.columns:
            if col == 'source':
                df[col] = 'TheMuse'
            elif col == 'collected_at':
                df[col] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            elif col == 'level':
                df[col] = 'Not specified'
            else:
                df[col] = None

    df_final = df[final_columns].copy()
    df_final.columns = ['source', 'id', 'title', 'company', 'city', 'country',
                        'remote', 'salary', 'salary_avg_usd', 'level', 'category',
                        'url', 'publication_date', 'collected_at']

    df_final = df_final.drop_duplicates(subset=['title'], keep='first')


    df_final.to_csv(output_file, index=False, encoding='utf-8-sig')

    print(f"\nСтатистика:")
    print(f"   Удалённых вакансий: {df_final['remote'].sum()}")
    print(f"   Городов: {df_final['city'].nunique()}")
    print(f"   Стран: {df_final['country'].nunique()}")

    print(f"\nТоп-10 стран:")
    country_counts = df_final['country'].value_counts().head(10)
    for country, count in country_counts.items():
        print(f"   {country}: {count}")

    print(f"\nТоп-10 категорий:")
    cat_counts = df_final['category'].value_counts().head(10)
    for cat, count in cat_counts.items():
        print(f"   {cat}: {count}")

    return df_final


def inspect_raw_data(input_file):
    df = pd.read_csv(input_file)
    print("Уникальные значения в колонке city (первые 30):")
    unique_cities = df['city'].unique()[:30]
    for city in unique_cities:
        print(f"  - {city}")

    print(f"\nОбщее количество записей: {len(df)}")
    print(f"Уникальных id: {df['id'].nunique()}")


if __name__ == "__main__":

    inspect_raw_data('../../data/raw/themuse_vacancies.csv')

    print("\n" + "="*50)
    print("ЗАПУСК ОБРАБОТКИ")
    print("="*50)
    result = process_themuse_data('../../data/raw/themuse_vacancies.csv', '../../data/clean/themuse_clean.csv')
