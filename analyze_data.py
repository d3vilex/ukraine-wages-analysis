import os
import textwrap
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns

# Налаштування шляхів до файлів та папок
PROCESSED_FILE_PATH = os.path.join("data_processed", "wages_cleaned.csv")
REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

# Загальна стилізація графіків
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.family'] = 'DejaVu Sans'


def load_data():
    """Завантажує очищений датасет та приводить дати до формату datetime."""
    df = pd.read_csv(PROCESSED_FILE_PATH)
    df['date'] = pd.to_datetime(df['date'])
    return df


def wrap_labels(labels, max_chars=32):
    """Переносить довгі назви галузей на кілька рядків."""
    return ['\n'.join(textwrap.wrap(label, max_chars)) for label in labels]


def analyze_industries(df):
    """Галузевий аналіз: ТОП-5 лідерів та аутсайдерів із подвійним сабплотом."""
    print("==================================================")
    print("1. ГАЛУЗЕВИЙ АНАЛІЗ (ПО ВСІЙ УКРАЇНІ)")
    print("==================================================")

    df_ind = df[(df['region'] == 'Україна') & (df['industry'] != 'Усього')].copy()
    latest_year = df_ind['year'].max()
    df_latest = df_ind[df_ind['year'] == latest_year]

    avg_by_ind = (
        df_latest.groupby('industry')['salary_uah']
        .mean()
        .reset_index()
        .sort_values(by='salary_uah', ascending=False)
    )

    top_5 = avg_by_ind.head(5).copy()
    bottom_5 = avg_by_ind.tail(5).copy().sort_values(by='salary_uah', ascending=True)

    print(f"\nТОП-5 галузей за середньою зарплатою у {latest_year} році (грн):")
    for idx, row in top_5.iterrows():
        print(f"  * {row['industry']}: {row['salary_uah']:,.2f} грн")

    print(f"\nТОП-5 аутсайдерів за середньою зарплатою у {latest_year} році (грн):")
    for idx, row in bottom_5.sort_values(by='salary_uah', ascending=False).iterrows():
        print(f"  * {row['industry']}: {row['salary_uah']:,.2f} грн")

    gap_ratio = top_5.iloc[0]['salary_uah'] / bottom_5.iloc[0]['salary_uah']
    print(f"\nРозрив між абсолютним лідером і аутсайдером: у {gap_ratio:.2f} раза")

    # Створюємо фігуру з двома графіками поруч
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), sharex=False)
    fig.suptitle(f"Рейтинг галузей України за середньою заробітною платою ({latest_year})", 
                 fontsize=14, fontweight='bold', y=0.98)

    # 1. ТОП-5 Лідерів
    bars1 = ax1.barh(wrap_labels(top_5['industry']), top_5['salary_uah'], color='#10b981', height=0.55)
    ax1.set_title("ТОП-5 Галузей-лідерів", fontsize=12, fontweight='bold', pad=12)
    ax1.invert_yaxis()
    ax1.set_xlabel("Заробітна плата (грн)", fontsize=10)
    ax1.xaxis.set_major_locator(ticker.MultipleLocator(20000))
    ax1.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
    ax1.set_xlim(0, top_5['salary_uah'].max() * 1.25)
    ax1.grid(axis='y', linestyle='')
    ax1.spines[['top', 'right']].set_visible(False)

    for bar in bars1:
        w = bar.get_width()
        ax1.annotate(f"{w:,.0f} грн",
                     xy=(w, bar.get_y() + bar.get_height() / 2),
                     xytext=(6, 0), textcoords="offset points",
                     va='center', fontsize=9, fontweight='bold', color='#065f46')

    # 2. ТОП-5 Аутсайдерів
    bars2 = ax2.barh(wrap_labels(bottom_5['industry']), bottom_5['salary_uah'], color='#ef4444', height=0.55)
    ax2.set_title("ТОП-5 Найменш оплачуваних галузей", fontsize=12, fontweight='bold', pad=12)
    ax2.set_xlabel("Заробітна плата (грн)", fontsize=10)
    ax2.xaxis.set_major_locator(ticker.MultipleLocator(5000))
    ax2.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
    ax2.set_xlim(0, bottom_5['salary_uah'].max() * 1.3)
    ax2.grid(axis='y', linestyle='')
    ax2.spines[['top', 'right']].set_visible(False)

    for bar in bars2:
        w = bar.get_width()
        ax2.annotate(f"{w:,.0f} грн",
                     xy=(w, bar.get_y() + bar.get_height() / 2),
                     xytext=(6, 0), textcoords="offset points",
                     va='center', fontsize=9, fontweight='bold', color='#991b1b')

    plt.tight_layout()
    plt.savefig(os.path.join(REPORTS_DIR, "top_bottom_industries.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print(f" Графік галузей оновлено: {REPORTS_DIR}/top_bottom_industries.png")


def analyze_regions(df):
    """Регіональний аналіз: розрахунок відхилень від бенчмарку та візуалізація."""
    print("\n==================================================")
    print("2. РЕГІОНАЛЬНИЙ АНАЛІЗ")
    print("==================================================")

    df_reg = df[df['industry'] == 'Усього'].copy()
    latest_year = df_reg['year'].max()
    df_reg_latest = df_reg[df_reg['year'] == latest_year]

    avg_by_reg = (
        df_reg_latest.groupby('region')['salary_uah']
        .mean()
        .reset_index()
        .sort_values(by='salary_uah', ascending=True)
    )

    ukraine_benchmark = avg_by_reg[avg_by_reg['region'] == 'Україна']['salary_uah'].values[0]
    avg_by_reg = avg_by_reg[avg_by_reg['region'] != 'Україна'].copy()
    avg_by_reg['diff_pct'] = ((avg_by_reg['salary_uah'] - ukraine_benchmark) / ukraine_benchmark) * 100

    print(f"\nБенчмарк по Україні ({latest_year} рік): {ukraine_benchmark:,.2f} грн")
    print("\nВідхилення зарплат у регіонах від середнього рівня по країні:")
    for idx, row in avg_by_reg.sort_values(by='salary_uah', ascending=False).iterrows():
        sign = "+" if row['diff_pct'] > 0 else ""
        print(f"  * {row['region']}: {row['salary_uah']:,.2f} грн ({sign}{row['diff_pct']:.1f}%)")

    # Побудова графіка регіональних відхилень
    plt.figure(figsize=(11, 7))
    colors = ['#2563eb' if x > 0 else '#64748b' for x in avg_by_reg['diff_pct']]

    bars = plt.barh(avg_by_reg['region'], avg_by_reg['diff_pct'], color=colors, height=0.6)
    plt.axvline(0, color='#dc2626', linestyle='--', linewidth=1.5, label='Середній рівень по Україні (0%)')

    plt.title(f"Відхилення заробітної плати регіонів від середнього показника по Україні ({latest_year})", 
              fontsize=13, fontweight='bold', pad=15)
    plt.xlabel("Відхилення від середнього рівня (%)", fontsize=10)
    plt.gca().xaxis.set_major_formatter(ticker.PercentFormatter())
    plt.grid(axis='y', linestyle='')
    plt.gca().spines[['top', 'right']].set_visible(False)
    plt.legend(frameon=True, loc='lower right')

    for bar in bars:
        w = bar.get_width()
        text_sign = f"+{w:.1f}%" if w > 0 else f"{w:.1f}%"
        x_offset = 6 if w >= 0 else -6
        ha_align = 'left' if w >= 0 else 'right'
        plt.annotate(text_sign,
                     xy=(w, bar.get_y() + bar.get_height() / 2),
                     xytext=(x_offset, 0), textcoords="offset points",
                     va='center', ha=ha_align, fontsize=9, fontweight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(REPORTS_DIR, "regional_comparison.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print(f" Графік регіонів оновлено: {REPORTS_DIR}/regional_comparison.png")


def calculate_descriptive_stats(df):
    """Розрахунок описової статистики та індикаторів нерівності."""
    print("\n==================================================")
    print("3. ОПИСОВА СТАТИСТИКА ТА НЕРІВНІСТЬ ДОХОДІВ")
    print("==================================================")

    salaries = df[df['industry'] != 'Усього']['salary_uah']
    mean_val = salaries.mean()
    median_val = salaries.median()
    std_val = salaries.std()
    cv_val = (std_val / mean_val) * 100
    q25 = salaries.quantile(0.25)
    q75 = salaries.quantile(0.75)
    iqr_val = q75 - q25

    print(f"Середнє арифметичне: {mean_val:,.2f} грн")
    print(f"Медіана:              {median_val:,.2f} грн")
    print(f"Стандартне відхилення:{std_val:,.2f} грн")
    print(f"Коефіцієнт варіації:  {cv_val:.2f}% (рівень розкиду даних)")
    print(f"25-й перцентиль (Q1): {q25:,.2f} грн")
    print(f"75-й перцентиль (Q3): {q75:,.2f} грн")
    print(f"Міжквартильний розмах:{iqr_val:,.2f} грн")


if __name__ == "__main__":
    df_clean = load_data()
    analyze_industries(df_clean)
    analyze_regions(df_clean)
    calculate_descriptive_stats(df_clean)