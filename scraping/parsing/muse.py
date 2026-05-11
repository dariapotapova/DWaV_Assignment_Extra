import requests
import time
import random
from datetime import datetime
import pandas as pd
import json
from fake_useragent import UserAgent

def scrape_themuse_api(api_key=None, target_count=5000):

    vacancies = []
    seen_ids = set()

    API_URL = "https://www.themuse.com/api/public/jobs"

    categories = [
        "Software Engineering",
        "Data and Analytics",
        "Science and Engineering",
        "Computer and IT",
        "Product Management",
        "Design and UX",
        "DevOps and Sysadmin",
        "Security",
        "Quality Assurance",
        "Systems Administration",
        "Network Engineering",
        "Cloud Computing",
        "Mobile Development",
        "Frontend Development",
        "Backend Development",
        "Full Stack Development",
        "Game Development",
        "Embedded Systems",
        "Hardware Engineering"
    ]

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"themuse_vacancies_{timestamp}.csv"

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'application/json',
    })

    stats = {
        'pages_requested': 0,
        'pages_success': 0,
        'jobs_fetched': 0,
        'categories_processed': 0
    }

    for category in categories:
        if len(vacancies) >= target_count:
            break

        stats['categories_processed'] += 1
        print(f"\n[{stats['categories_processed']}/{len(categories)}] Категория: {category}")
        print(f"   Уже собрано: {len(vacancies)} / {target_count}")

        page = 1
        max_pages = 50
        empty_pages = 0

        while page <= max_pages and len(vacancies) < target_count and empty_pages < 3:
            params = {
                'category': category,
                'page': page
            }

            stats['pages_requested'] += 1

            try:
                time.sleep(random.uniform(0.3, 0.6))

                response = session.get(API_URL, params=params, timeout=30)

                if response.status_code == 200:
                    stats['pages_success'] += 1
                    data = response.json()
                    jobs = data.get('results', [])

                    if not jobs:
                        empty_pages += 1
                        print(f"  Страница {page}: нет вакансий (empty_pages={empty_pages})")
                        if empty_pages >= 3:
                            break
                        page += 1
                        continue
                    else:
                        empty_pages = 0

                    print(f"  Страница {page}: найдено {len(jobs)} вакансий")

                    page_count = 0
                    for job in jobs:
                        job_id = str(job.get('id'))
                        if not job_id or job_id in seen_ids:
                            continue

                        seen_ids.add(job_id)
                        stats['jobs_fetched'] += 1

                        company_data = job.get('company', {})
                        company = company_data.get('name', 'Не указана') if company_data else 'Не указана'

                        # Зарплата
                        salary = None
                        salary_min = job.get('salary_min')
                        salary_max = job.get('salary_max')

                        if salary_min and salary_max:
                            salary = f"${salary_min:,} - ${salary_max:,}"
                            salary_avg = (salary_min + salary_max) / 2
                        elif salary_min:
                            salary = f"от ${salary_min:,}"
                            salary_avg = salary_min
                        elif salary_max:
                            salary = f"до ${salary_max:,}"
                            salary_avg = salary_max
                        else:
                            salary_avg = None

                        # Локации
                        locations = job.get('locations', [])
                        cities = [loc.get('name', '') for loc in locations if loc.get('name')]
                        city = cities[0] if cities else 'Remote'
                        is_remote = 'Remote' in city or any('remote' in str(loc).lower() for loc in locations)

                        # Уровни
                        levels = job.get('levels', [])
                        level_names = [level.get('name', '') for level in levels if level.get('name')]
                        level = level_names[0] if level_names else 'Not specified'

                        # Категории вакансии
                        job_categories = job.get('categories', [])
                        cat_names = [cat.get('name', '') for cat in job_categories if cat.get('name')]

                        vacancies.append({
                            'source': 'TheMuse',
                            'id': job_id,
                            'title': job.get('name', 'Не указано'),
                            'company': company,
                            'salary': salary,
                            'salary_avg_usd': salary_avg,
                            'city': city,
                            'remote': is_remote,
                            'level': level,
                            'categories': ', '.join(cat_names),
                            'search_category': category,
                            'url': job.get('refs', {}).get('landing_page', ''),
                            'publication_date': job.get('publication_date', ''),
                            'collected_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                        page_count += 1

                        # Промежуточное сохранение
                        if len(vacancies) % 200 == 0:
                            temp_df = pd.DataFrame(vacancies)
                            temp_df.to_csv(output_file, index=False, encoding='utf-8-sig')
                            print(f" Сохранено: {len(vacancies)} вакансий")

                    print(f"  +{page_count} новых (всего {len(vacancies)})")

                    if len(jobs) < 20:
                        break

                    page += 1

                elif response.status_code == 400:
                    print(f"  Страница {page}: вышли за пределы (HTTP 400)")
                    break

                elif response.status_code in (429, 403, 500, 502, 503, 504):
                    print(f"  Ошибка {response.status_code}, ждём 5 секунд...")
                    time.sleep(5)
                    continue

                else:
                    print(f"  Неожиданный статус: {response.status_code}")
                    break

            except requests.exceptions.Timeout:
                print(f"  Таймаут на странице {page}, пробуем дальше...")
                continue
            except Exception as e:
                print(f"  Ошибка: {e}")
                break

    # Финальное сохранение
    if vacancies:
        df = pd.DataFrame(vacancies)
        df = df.drop_duplicates(subset=['id'])
        df.to_csv(output_file, index=False, encoding='utf-8-sig')

        print(f"\nТоп-10 категорий по количеству:")
        for cat in df['search_category'].value_counts().head(10).index:
            count = len(df[df['search_category'] == cat])
            print(f"   • {cat}: {count}")

        print(f"\nТоп-10 компаний:")
        for company, count in df['company'].value_counts().head(10).items():
            print(f"   • {company[:30]}: {count}")

        print(f"\nГорода:")
        for city, count in df['city'].value_counts().head(10).items():
            print(f"   • {city}: {count}")

        return df
    else:
        print("\nНе удалось собрать вакансии")
        return pd.DataFrame()


if __name__ == "__main__":
    result = scrape_themuse_api(target_count=5000)