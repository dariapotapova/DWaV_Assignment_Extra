
import time
from datetime import datetime
import pandas as pd

from scraping.parsing.habr import scrape_habr_all_it

def save_vacancies(vacancies, filename):
    if not vacancies:
        print(f"Нет вакансий для {filename}")
        return False

    df = pd.DataFrame(vacancies)
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    return True

def main():
    start_time = time.time()

    try:
        habr_vacancies = scrape_habr_all_it(target_count=2000)
        habr_time = time.time() - start_time
        print(f"Habr парсер завершён за {habr_time:.1f} сек. Найдено: {len(habr_vacancies)} вакансий")

        save_vacancies(habr_vacancies, f"habr_vacancies_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    except Exception as e:
        print(f"Ошибка Habr парсера: {e}")

if __name__ == "__main__":
    main()