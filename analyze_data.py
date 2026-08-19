import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Налаштування шляхів та стилів графіків
PROCESSED_FILE_PATH = os.path.join("data_processed", "wages_cleaned.csv")
REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({'font.sans-serif': 'DejaVu Sans', 'font.size': 10})

def load_data():
    df = pd.read_csv(PROCESSED_FILE_PATH)
    df['date'] = pd.to_datetime(df['date'])
    return df

def analyze_industries(df):
    print("==================================================")
    print("1. ГАЛУЗЕВИЙ АНАЛІЗ (ПО ВСІЙ УКРАЇНІ)")
    print("==================================================")
    
    # Фільтруємо лише загальнонаціональні дані по галузях (виключаємо підсумковий рядок 'Усього')
    df_ind = df[(df['region'] == 'Україна') & (df['industry'] != 'Усього')].copy()
    
    # Знаходимо останній повний рік у датасеті
    latest_year = df_ind['year'].max()
    df_latest = df_ind[df_ind['year'] == latest_year]
    
    # Середня зарплата за останній рік за галузями
    avg_by_ind = (
        df_latest.groupby('industry')['salary_uah']
        .mean()
        .reset_index()
        .sort_values(by='salary_uah', ascending=False)
    )
    
    top_5 = avg_by_ind.head(5)
    bottom_5 = avg_by_ind.tail(5)
    
    print(f"\nТОП-5 галузей за середньою зарплатою у {latest_year} році (грн):")
    for idx, row in top_5.iterrows():
        print(f"  * {row['industry']}: {row['salary_uah']:,.2f} грн")
        
    print(f"\nТОП-5 аутсайдерів за середньою зарплатою у {latest_year} році (грн):")
    for idx, row in bottom_5.iterrows():
        print(f"  * {row['industry']}: {row['salary_uah']:,.2f} грн")
        
    # Співвідношення розриву
    gap_ratio = top_5.iloc[0]['salary_uah'] / bottom_5.iloc[-1]['salary_uah']
    print(f"\nРозрив між абсолютним лідером і аутсайдером: у {gap_ratio:.2f} раза")

    # Візуалізація рейтингу
    plt.figure(figsize=(12, 8))
    chart_data = pd.concat([top_5, bottom_5])
    palette = ['#2ecc71' if i < 5 else '#e74c3c' for i in range(len(chart_data))]
    
    ax = sns.barplot(
        data=chart_data,
        x='salary_uah',
        y='industry',
        palette=palette
    )
    plt.title(f"ТОП-5 найбільш та найменш оплачуваних галузей України ({latest_year})", fontsize=14, pad=15)
    plt.xlabel("Середня заробітна плата (грн)", fontsize=11)
    plt.ylabel("Галузь (КВЕД)", fontsize=11)
    
    for p in ax.patches:
        width = p.get_width()
        ax.annotate(f"{width:,.0f} грн", (width + 500, p.get_y() + p.get_height() / 2.),
                    va='center', fontsize=9)
        
    plt.tight_layout()
    plt.savefig(os.path.join(REPORTS_DIR, "top_bottom_industries.png"), dpi=300)
    plt.close()
    print(f" Графік збережено: {REPORTS_DIR}/top_bottom_industries.png")


def analyze_regions(df):
    print("\n==================================================")
    print("2. РЕГІОНАЛЬНИЙ АНАЛІЗ")
    print("==================================================")
    
    # Фільтруємо агреговані зарплати по регіонах
    df_reg = df[df['industry'] == 'Усього'].copy()
    latest_year = df_reg['year'].max()
    df_reg_latest = df_reg[df_reg['year'] == latest_year]
    
    avg_by_reg = (
        df_reg_latest.groupby('region')['salary_uah']
        .mean()
        .reset_index()
        .sort_values(by='salary_uah', ascending=False)
    )
    
    # Знаходимо середнє по Україні як бенчмарк
    ukraine_benchmark = avg_by_reg[avg_by_reg['region'] == 'Україна']['salary_uah'].values[0]
    avg_by_reg['diff_pct'] = ((avg_by_reg['salary_uah'] - ukraine_benchmark) / ukraine_benchmark) * 100
    
    print(f"\nБенчмарк по Україні ({latest_year} рік): {ukraine_benchmark:,.2f} грн")
    print("\nВідхилення зарплат у регіонах від середнього рівня по країні:")
    for idx, row in avg_by_reg.iterrows():
        if row['region'] != 'Україна':
            sign = "+" if row['diff_pct'] > 0 else ""
            print(f"  * {row['region']}: {row['salary_uah']:,.2f} грн ({sign}{row['diff_pct']:.1f}%)")
            
    # Візуалізація регіонів
    plt.figure(figsize=(10, 6))
    reg_plot_data = avg_by_reg[avg_by_reg['region'] != 'Україна']
    colors = ['#3498db' if x > 0 else '#95a5a6' for x in reg_plot_data['diff_pct']]
    
    sns.barplot(data=reg_plot_data, x='diff_pct', y='region', palette=colors)
    plt.axvline(0, color='red', linestyle='--', linewidth=1.5, label='Середній рівень по Україні')
    plt.title(f"Відхилення заробітної плати регіонів від середнього по Україні ({latest_year})", fontsize=13, pad=15)
    plt.xlabel("Відхилення від середнього рівня (%)", fontsize=10)
    plt.ylabel("Регіон", fontsize=10)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(REPORTS_DIR, "regional_comparison.png"), dpi=300)
    plt.close()
    print(f" Графік збережено: {REPORTS_DIR}/regional_comparison.png")


def calculate_descriptive_stats(df):
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