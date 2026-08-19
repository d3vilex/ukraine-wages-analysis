import pandas as pd

RAW_DATA_PATH = "raw_data.csv"

def inspect():
    print("--- 1. Завантаження файлу ---")
    try:
        # Автоматичне визначення роздільника (кома, крапка з комою, табуляція)
        df = pd.read_csv(RAW_DATA_PATH, sep=None, engine="python", encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(RAW_DATA_PATH, sep=None, engine="python", encoding="cp1251")

    print(f"\nРозмірність (рядків, колонок): {df.shape}")
    
    print("\n--- 2. Назви всіх колонок ---")
    print(df.columns.tolist())

    print("\n--- 3. Перші 3 рядки ---")
    print(df.head(3))

    print("\n--- 4. Загальна інформація про типи та пропуски ---")
    df.info()

if __name__ == "__main__":
    inspect()