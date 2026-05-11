import requests
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime
from fake_useragent import UserAgent
import pandas as pd

def scrape_habr_all_it(target_count=2000):
    vacancies = []
    seen_ids = set()

    it_keywords = [
        # Языки (базовые)
        "python", "python junior", "python middle", "python senior",
        "javascript", "js", "typescript",
        "java", "spring",
        "c++", "cpp", "qt",
        "go", "golang",
        "rust", "c#", ".net", "php", "laravel",
        "ruby", "rails", "kotlin", "swift",

        # Фреймворки и технологии
        "django", "flask", "fastapi",
        "react", "vue", "angular", "node.js",
        "docker", "kubernetes", "k8s",
        "postgresql", "mongodb", "redis",

        # Направления
        "frontend", "front-end",
        "backend", "back-end",
        "fullstack", "full-stack",
        "devops", "sre",
        "data scientist", "data science",
        "data analyst", "data analysis",
        "data engineer", "data engineering",
        "ml engineer", "machine learning",
        "qa", "qa automation", "manual qa",
        "game developer", "unity", "unreal",
        "security", "information security", "pentest",
        "product manager", "project manager",
        "system administrator", "sysadmin", "linux admin",

        # Грейды (чтобы собрать разные страницы)
        "junior", "junior developer",
        "middle", "middle developer",
        "senior", "senior developer",
        "lead", "team lead", "tech lead",

    ]

    ua = UserAgent()

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"habr_vacancies_{timestamp}.csv"

    for idx, keyword in enumerate(it_keywords, 1):
        if len(vacancies) >= target_count:
            break

        print(f"\n[{idx}/{len(it_keywords)}] Habr: Поиск '{keyword}'")

        for page in range(1, 8):
            if len(vacancies) >= target_count:
                break

            params = f"page={page}&q={keyword.replace(' ', '+')}&type=all"
            url = f"https://career.habr.com/vacancies?{params}"

            try:
                headers = {
                    'User-Agent': ua.random,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Referer': 'https://career.habr.com/'
                }
                response = requests.get(url, headers=headers, timeout=15)
                soup = BeautifulSoup(response.content, 'html.parser')
                job_cards = soup.find_all('div', class_='vacancy-card')

                if not job_cards:
                    if page == 1:
                        print(f"  Страница {page}: вакансии не найдены")
                    break

                print(f"  Страница {page}: найдено {len(job_cards)} карточек")
                page_count = 0

                for card in job_cards:
                    try:
                        if len(vacancies) >= target_count:
                            break

                        title_elem = card.find('a', class_='vacancy-card__title-link')
                        if not title_elem:
                            continue
                        title = title_elem.text.strip()

                        non_it = ['дизайнер', 'designer', 'маркетолог', 'marketing',
                                  'hr', 'бухгалтер', 'accountant']
                        if any(word in title.lower() for word in non_it):
                            continue

                        href = title_elem.get('href', '')
                        vacancy_id = f"habr_{href.split('/')[-1]}" if href else f"habr_{hash(title)}"

                        if vacancy_id in seen_ids:
                            continue
                        seen_ids.add(vacancy_id)

                        company_elem = card.find('div', class_='vacancy-card__company')
                        company = company_elem.find('a').text.strip() if company_elem and company_elem.find('a') else "Не указана"

                        salary_elem = card.find('div', class_='vacancy-card__salary')
                        salary = salary_elem.get_text(strip=True) if salary_elem else None

                        meta_elem = card.find('div', class_='vacancy-card__meta')
                        city = "Не указан"
                        remote = False
                        if meta_elem:
                            chips = meta_elem.find_all('div', class_='basic-chip')
                            for chip in chips:
                                chip_text = chip.get_text(strip=True)
                                if 'удалённо' in chip_text.lower() or 'remote' in chip_text.lower():
                                    remote = True
                                elif chip_text and len(chip_text) < 50:
                                    if not any(level in chip_text for level in ['Middle', 'Senior', 'Junior', 'Lead', 'Intern']):
                                        city = chip_text

                        skills_elem = card.find('div', class_='vacancy-card__skills')
                        skills = []
                        if skills_elem:
                            skill_chips = skills_elem.find_all('a', class_='basic-chip')
                            skills = [chip.get_text(strip=True) for chip in skill_chips]

                        vacancies.append({
                            'source': 'Habr',
                            'id': vacancy_id,
                            'title': title,
                            'company': company,
                            'city': city,
                            'remote': remote,
                            'salary': salary,
                            'skills': ', '.join(skills[:5]),
                            'collected_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'search_keyword': keyword
                        })
                        page_count += 1

                        # Сохраняем каждые 100 новых
                        if len(vacancies) % 100 == 0:
                            temp_df = pd.DataFrame(vacancies)
                            temp_df.to_csv(output_file, index=False, encoding='utf-8-sig')
                            print(f"Сохранено: {len(vacancies)} вакансий")

                    except Exception as e:
                        continue

                pd.DataFrame(vacancies).to_csv(output_file, index=False, encoding='utf-8-sig')

                time.sleep(random.uniform(1.5, 2.5))

            except Exception as e:
                print(f"  Ошибка: {e}")
                break

    if vacancies:
        df = pd.DataFrame(vacancies)
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
    else:
        print("\nВакансии не найдены!")

    return vacancies


if __name__ == "__main__":
    result = scrape_habr_all_it(target_count=2500)
    if result:
        print(f"Пример вакансии:")
        example = result[0]
        for key, value in example.items():
            if value:
                print(f"  {key}: {str(value)[:100]}")