import os
import re
import pandas as pd

RAW_DATA_PATH = "raw_data.csv"
PROCESSED_DIR = "data_processed"
PROCESSED_FILE_PATH = os.path.join(PROCESSED_DIR, "wages_cleaned.csv")

def clean_data():
    print("--- 1. Читання та первинне очищення заголовків ---")
    try:
        df = pd.read_csv(RAW_DATA_PATH, sep=None, engine="python", encoding="utf-8-sig")
    except UnicodeDecodeError:
        df = pd.read_csv(RAW_DATA_PATH, sep=None, engine="python", encoding="cp1251")

    # Видаляємо зайві лапки та пробіли з назв усіх колонок
    df.columns = [col.replace('"', '').strip() for col in df.columns]
    print(f"Початкові колонки: {df.columns.tolist()[:8]}...")

    # Ідентифікаційні колонки (все, що не є датами типу YYYY-MXX)
    id_vars = [
        'Показник', 
        'Територіальний розріз', 
        'Вид економічної діяльності', 
        'Категорія розрізу', 
        'Розріз', 
        'Періодичність'
    ]
    
    # Стовпці з датами (наприклад, 2021-M01, 2021-M02...)
    value_vars = [col for col in df.columns if re.match(r'^\d{4}-M\d{2}$', col)]

    print(f"\n--- 2. Трансформація таблиці (wide -> long / melt) ---")
    df_long = pd.melt(
        df,
        id_vars=id_vars,
        value_vars=value_vars,
        var_name='period_raw',
        value_name='salary_uah'
    )

    print(f"Кількість рядків після розгортання: {len(df_long)}")

    print("\n--- 3. Обробка та типізація даних ---")
    # Перетворюємо період '2021-M01' -> '2021-01-01'
    df_long['date'] = df_long['period_raw'].str.replace('-M', '-').apply(lambda x: f"{x}-01")
    df_long['year'] = df_long['date'].str[:4].astype(int)
    df_long['month'] = df_long['date'].str[5:7].astype(int)

    # Очищення числових значень: видалення пробілів, заміна коми на крапку, конвертація у float
    df_long['salary_uah'] = (
        df_long['salary_uah']
        .astype(str)
        .str.replace(r'\s+', '', regex=True)
        .str.replace(',', '.')
        .replace(['nan', 'None', '', '...'], pd.NA)
    )
    df_long['salary_uah'] = pd.to_numeric(df_long['salary_uah'], errors='coerce')

    # Перейменування та відбір колонок для фінального датасету
    df_clean = df_long.rename(columns={
        'Показник': 'indicator',
        'Територіальний розріз': 'region',
        'Вид економічної діяльності': 'industry',
        'Категорія розрізу': 'category',
        'Розріз': 'subcategory'
    })[['date', 'year', 'month', 'region', 'industry', 'salary_uah']]

    # Видаляємо пропуски, якщо Держстат не надав даних за певні місяці
    df_clean = df_clean.dropna(subset=['salary_uah']).reset_index(drop=True)

    print(f"Фінальна кількість валідних спостережень: {len(df_clean)}")
    print("\n--- Перші 5 рядків очищеного датасету: ---")
    print(df_clean.head())

    # Створення папки та збереження
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    df_clean.to_csv(PROCESSED_FILE_PATH, index=False, encoding='utf-8')
    print(f"\n Очищений файл збережено у: {PROCESSED_FILE_PATH}")

if __name__ == "__main__":
    clean_data()