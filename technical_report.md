# Технічний звіт: Архітектура та пайплайн обробки даних

## 1. Архітектура репозиторію
```text
ukraine-wages-analysis/
├── data_processed/
│   └── wages_cleaned.csv        # Очищений датасет у форматі Tidy Data (2475 рядків)
├── reports/
│   ├── regional_comparison.png  # Візуалізація географічних відхилень
│   └── top_bottom_industries.png# Візуалізація галузевого рейтингу
├── raw_data.csv                 # Первинне вивантаження з Держстату
├── inspect_raw_data.py          # Скрипт первинного аудиту структури
├── clean_data.py                # Пайплайн ETL та типізації
├── analyze_data.py              # Статистичні розрахунки та візуалізація
├── README.md                    # Основний аналітичний звіт
└── technical_report.md          # Технічна документація