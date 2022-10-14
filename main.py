import gdown
import re
import tabulate

import numpy as np
import pandas as pd

download_pattern = 'https://drive.google.com/uc?id='
filenames = [
    'tr_mcc_codes.csv',
    'tr_types.csv',
    'transactions.csv',
    'gender_train.csv'
]
share_urls = [
    'https://drive.google.com/file/d/10J8RzMIhoYHiad49r-oWNMAk-V5lo3OE/view?usp=sharing',
    'https://drive.google.com/file/d/1EP3KrATWS1I_qYdpRhYnSDl-eoBiOBQc/view?usp=sharing',
    'https://drive.google.com/file/d/1lEpoRKczv5EvZhff9O2I-0JkdHnbe_Mq/view?usp=sharing',
    'https://drive.google.com/file/d/1FG1fopcmvMZ7GBaBOqQipccSeFoMUvNT/view?usp=sharing'
]

ids = []
for link in share_urls:
    ids.append(re.search('/d/(.+?)/view', link).group(1))

download_links = []
for file_id in ids:
    dwnld_link = download_pattern + file_id
    download_links.append(dwnld_link)

# files = []
# for i in range(len(download_links)):
#     files.append(gdown.download(download_links[i], filenames[i]))

files_info = pd.DataFrame(dtype=str,
                          index=filenames,
                          columns=[
                              'file_name',
                              'share_url',
                              'id',
                              'download_url',
                              'file'
                          ])

files_info['file_name'] = filenames
files_info['share_url'] = share_urls
files_info['id'] = ids
files_info['download_url'] = download_links
# files_info['file'] = files

filenames.clear()
share_urls.clear()
ids.clear()
download_links.clear()


# files.clear()

def print_dataframe(dataframe):
    print(tabulate.tabulate(dataframe, headers='keys', numalign='center', stralign='left', tablefmt='fancy_grid', ))


print_dataframe(files_info)

##################################### Reading Files ######################################################

tr_mcc_codes = pd.read_csv(filepath_or_buffer=files_info['file_name']['tr_mcc_codes.csv'],
                           sep=';',
                           index_col='mcc_code',
                           usecols=['mcc_code', 'mcc_description'])

tr_types = pd.read_csv(filepath_or_buffer=files_info['file_name']['tr_types.csv'],
                       sep=';',
                       index_col='tr_type',
                       usecols=['tr_type', 'tr_description'])

transactions = pd.read_csv(filepath_or_buffer=files_info['file_name']['transactions.csv'],
                           sep=',',
                           nrows=1000000,
                           index_col='customer_id',
                           usecols=['customer_id', 'tr_datetime', 'mcc_code', 'tr_type', 'amount', 'term_id'])

gender_train = pd.read_csv(filepath_or_buffer=files_info['file_name']['gender_train.csv'],
                           sep=',',
                           index_col='customer_id',
                           usecols=['customer_id', 'gender'])

# ############################################### Task 1 #########################################################
# Для столбца tr_type датафрейма transactions выберите произвольные 1000 строк с помощью метода sample
# В полученной на предыдущем этапе подвыборке найдите долю транзакций 
# (стобец tr_description в датасете tr_types), в которой содержится подстрока 'POS' или 'ATM'.

subsample = transactions['tr_type'].sample(1000)  # Series of types
subsample_info = pd.DataFrame(
    index=subsample,
    columns=['tr_description']
)
subsample_info.update(tr_types.tr_description)

pattern = 'POS|АТМ'
tr_types_contained_pattern = subsample_info[(subsample_info.tr_description.str.contains(pattern)) == True]

print("\nСоотношение имеющих в описании типа транзакции POS|АТМ ко всем типам транзакции в случайной выборке = ",
      tr_types_contained_pattern.size / subsample_info.size)

# ############################################### Task 2 #########################################################
# Для столбца tr_type датафрейма transactions посчитайте частоту встречаемости всех типов
# транзакций tr_type в transactions. 
# Выведите топ-10 транзакций по частоте встречаемости (вывести для них tr_description тоже). 


types_frequency = pd.DataFrame(
    index=tr_types.index,
    columns=['occurrence', 'tr_description'],
)

types_frequency.occurrence = transactions.tr_type.value_counts()
types_frequency.update(tr_types.tr_description)
top10 = types_frequency.sort_values(by='occurrence', ignore_index=False, ascending=False).head(10)

print("\nТоп 10 встерчаемых типов транзакций, их частота и описание: ")
print_dataframe(top10)

# ############################################### Task 3 #########################################################
# В датафрейме transactions найдите клиента с максимальной суммой приходов на карту.
# В датафрейме transactions найдите клиента с максимальной суммой расходов по карте.
# Найдите модуль разницы для этих клиентов между суммой расходов и суммой приходов.

customer_info = pd.DataFrame(
    index=transactions.index.unique(),
    columns=['expenses', 'deposits']
)

groups_of_customer = transactions.groupby(level='customer_id')

for customer_id, operations in groups_of_customer:
    positive_sum = operations.amount[operations.amount > 0.0].sum()
    negative_sum = operations.amount[operations.amount < 0.0].sum()

    customer = pd.Series(data={
        'expenses': round(negative_sum, 3),
        'deposits': round(positive_sum, 3)
    })
    customer_info.loc[customer_id] = customer

customer_info['difference'] = np.abs(customer_info.deposits + customer_info.expenses)

min_customer = customer_info.sort_values(by='expenses', ignore_index=False, ascending=True).head(1)
max_customer = customer_info.sort_values(by='deposits', ignore_index=False, ascending=False).head(1)

print("\nКлиент с максимальной суммой приходов на карту: ")
print_dataframe(max_customer)

print("\nКлиент с максимальной суммой расходов на карту: ")
print_dataframe(min_customer)

# ############################################### Task 4 #########################################################
# Найдите среднее арифметическое и медиану по amount по всем типам транзакций из топ 10 из задания 2
# Найдите среднее арифметическое и медиану по amount по всем типам транзакций для клиентов из задания 3

tr_types_top10_info = pd.DataFrame(
    index=top10.index,
)

all_top10_tr_groups = transactions[transactions.tr_type.isin(top10.index)].groupby('tr_type')

tr_types_top10_info['mean'] = all_top10_tr_groups.amount.mean()
tr_types_top10_info['median'] = all_top10_tr_groups.amount.median()

print("\nИнформация о amount по всем типам транзакций из топ 10 (результат задания 2):")
print_dataframe(tr_types_top10_info)


def get_mean_and_median_for_each_tr_type_of_customer(id_of_cus):
    all_customer_transactions = transactions.loc[id_of_cus].groupby(by='tr_type', as_index=True)
    mean = all_customer_transactions.amount.mean()
    median = all_customer_transactions.amount.median()
    return mean, median


min_customer_id = min_customer.index[0]
max_customer_id = max_customer.index[0]
tr_types_min_customer_info = pd.DataFrame(index=transactions.loc[min_customer_id].tr_type.unique())
tr_types_max_customer_info = pd.DataFrame(index=transactions.loc[max_customer_id].tr_type.unique())

tr_types_min_customer_info['mean'], tr_types_min_customer_info['median'] = \
    get_mean_and_median_for_each_tr_type_of_customer(min_customer_id)

if min_customer_id == max_customer_id:
    print("\nТ.к. идентификаторы клиента с максимальной суммой приходов на карту и "
          "клиента с максимальной суммой расходов по карте совпадают, таблица для одного человека только одна:")
    print_dataframe(tr_types_min_customer_info)
else:
    print("\nИнформация о amount по всем типам транзакций для клиента с максимальной суммой расходов по карте"
          " (результат задания 3):")
    print_dataframe(tr_types_min_customer_info)

    tr_types_max_customer_info['mean'], tr_types_min_customer_info['median'] = \
        get_mean_and_median_for_each_tr_type_of_customer(min_customer_id)

    print("\nИнформация о amount по всем типам транзакций для клиента с максимальной суммой приходов на карту"
          " (результат задания 3):")
    print_dataframe(tr_types_max_customer_info)

# ############################################### Task 5 #########################################################

transactions = pd.merge(transactions.reset_index(), gender_train.reset_index(), how='left')
transactions = pd.merge(transactions.reset_index(), tr_mcc_codes.reset_index(), how='inner')
transactions = pd.merge(transactions.reset_index(), tr_types.reset_index(), how='inner')
print_dataframe(transactions.sample(10))
print("Размеры соединённой матрицы:", transactions.shape)

genders = {
    'male': 0,
    'female': 1
}

# Определите модуль разницы между средними тратами женщин и мужчин (трата - отрицательное значение amount).
# Определите модуль разницы между средними поступлениями у мужчин и женщин.

diff_expenses = np.abs(
    transactions[(transactions.gender == genders['female']) & (transactions.amount < 0.0)].amount.mean() -
    transactions[(transactions.gender == genders['male']) & (transactions.amount < 0.0)].amount.mean())

diff_deposits = (
    np.abs(transactions[(transactions.gender == genders['male']) & (transactions.amount > 0.0)].amount.mean() -
           transactions[(transactions.gender == genders['female']) & (transactions.amount > 0.0)].amount.mean()))

print("\nМодуль разницы между средними тратами женщин и мужчин = ", round(diff_expenses, 3))
print("Модуль разницы между средними поступлениями у мужчин и женщин = ", round(diff_deposits, 3))

# ############################################### Task 6 #########################################################
# По всем типам транзакций рассчитайте максимальную сумму прихода на карту 
# (из строго положительных сумм по столбцу amount) отдельно для мужчин и женщин 
# (назовите ее "max_income"). Оставьте по 10 типов транзакций для мужчин и для женщин, 
# наименьших среди всех типов транзакций по полученным значениям "max_income".

# Выделите среди них те типы транзакций, которые встречаются одновременно и у мужчин, и у женщин.

male_max_incomes = transactions[(transactions.amount > 0.0) & (transactions.gender == genders['male'])]. \
    groupby('tr_type').amount.max()
female_max_incomes = transactions[(transactions.amount > 0.0) & (transactions.gender == genders['female'])]. \
    groupby('tr_type').amount.max()

top10_lowest_male_max_incomes = male_max_incomes.sort_values(ignore_index=False, ascending=True).head(10)
top10_lowest_female_max_incomes = female_max_incomes.sort_values(ignore_index=False, ascending=True).head(10)

intersected_values = pd.DataFrame(
    index=pd.Series(np.intersect1d(top10_lowest_male_max_incomes.index, top10_lowest_female_max_incomes.index)),
    columns=['max_income_male', 'max_income_female'],
)

intersected_values['max_income_male'] = \
    top10_lowest_male_max_incomes[top10_lowest_male_max_incomes.index.isin(intersected_values.index)]
intersected_values['max_income_female'] = \
    top10_lowest_female_max_incomes[top10_lowest_female_max_incomes.index.isin(intersected_values.index)]

print("\nТоп 10 типов транзакций с наименьшей максимальной суммой прихода среди мужчин:")
print_dataframe(pd.DataFrame(top10_lowest_male_max_incomes))

print("\nТоп 10 типов транзакций с наименьшей максимальной суммой прихода среди женщин:")
print_dataframe(pd.DataFrame(top10_lowest_female_max_incomes))

print("\n Типы транзакций, которые встречаются одновременно и у мужчин, и у женщин:")
print_dataframe(intersected_values)

# ############################################### Task 7 #########################################################
# Найдите суммы затрат по каждой категории (mcc) для мужчин и для женщин.
# Найдите топ 10 категорий с самыми большими относительными модулями разности в тратах для разных полов
# (в ответе должны присутствовать описания mcc кодов).

sum_expenses_for_mcc_codes = pd.DataFrame(
    index=transactions.mcc_code.unique(),
)

sum_expenses_for_mcc_codes['male_sum_expenses'] = \
    transactions[(transactions.gender == genders['male']) & (transactions.amount < 0.0)].groupby('mcc_code').amount.sum()

sum_expenses_for_mcc_codes['female_sum_expenses'] = \
    transactions[(transactions.gender == genders['female']) & (transactions.amount < 0.0)].groupby('mcc_code').amount.sum()

sum_expenses_for_mcc_codes['diff_between_gender_expenses'] = \
    np.abs(sum_expenses_for_mcc_codes.male_sum_expenses - sum_expenses_for_mcc_codes.female_sum_expenses)

sum_expenses_for_mcc_codes['mcc_description'] = \
    tr_mcc_codes.loc[sum_expenses_for_mcc_codes.index].mcc_description

# print_dataframe(sum_expenses_for_mcc_codes)

top10_diff_between_male_and_female_expenses = \
    sum_expenses_for_mcc_codes.sort_values(by='diff_between_gender_expenses', ignore_index=False, ascending=False).head(10)

print("\n Топ 10 категорий с самыми большими модулями разности в тратах для разных полов:")
print_dataframe(top10_diff_between_male_and_female_expenses)


# ############################################### Task 8 #########################################################
# Из поля tr_datetime выделите час tr_hour, в который произошла транзакция, как первые 2 цифры до ":".
# Посчитайте количество транзакций с amount<0 в ночное время для мужчин и женщин. Ночное время - это примерно 00-06 часов.

# Не работает, т.к. в некоторых строчках 60 секунд, например 15:42:60. (Гениально, конечно).
# Из-за этого не может нормально конвертировать в datetime.
def get_tr_hour(tr_datetime):
    print(tr_datetime, type(tr_datetime))
    tr_hour = pd.to_datetime(transactions.tr_datetime[-8:]).dt.hour
    print(tr_hour, type(tr_hour))
    return tr_hour


# Не хочет применяться в отсеивании таблицы, воспринимается как обычный массив вместо конкретного значения в строчке
def check_tr_hour_for_night_time(tr_hour):
    begin_night = 0
    end_night = 6
    return (int(tr_hour) >= begin_night) & (int(tr_hour) <= end_night)


night_expenses = transactions[(transactions.amount < 0.0)]
night_expenses['tr_hour'] = pd.Series(int(tr_datetime[-8:-6]) for tr_datetime in transactions.tr_datetime)
night_expenses = night_expenses[(night_expenses.tr_hour >= 0) & (night_expenses.tr_hour < 6)]

male_night_expenses = night_expenses[(night_expenses.gender == genders['male'])]
female_night_expenses = night_expenses[(night_expenses.gender == genders['female'])]

male_number_of_transactions = len(male_night_expenses)
female_number_of_transactions = len(female_night_expenses)

print("Количество операций по снятию средств среди мужчин в ночное время суток:", male_number_of_transactions)
print("Количество операций по снятию средств среди женщин в ночное время суток:", female_number_of_transactions)

# ####################################### One of the additional tasks #######################################
# По каждой категории (mcc) найдите сумму трат в ночное время и в остальное время.

# Найдите соотношение одного к другому. Выведите список 10 категорий с описаниями,
# упорядоченных по убыванию отношения ночных трат к остальным тратам.

mcc_codes_info = pd.DataFrame(
    index=transactions.mcc_code.unique(),
    columns=['mmc_codes_expenses',
             'night_expenses',
             'day_expenses',
             'ratio_of_night_to_day',
             'mcc_description']
)

expenses = transactions[(transactions.amount < 0.0)]
expenses['tr_hour'] = pd.Series(int(tr_datetime[-8:-6]) for tr_datetime in expenses.tr_datetime)

mcc_codes_info['mmc_codes_expenses'] = expenses.groupby('mcc_code').amount.sum()
mcc_codes_info['night_expenses'] = expenses[(expenses.tr_hour >= 0) & (expenses.tr_hour < 6)].groupby('mcc_code').amount.sum()
mcc_codes_info['day_expenses']   = expenses[(expenses.tr_hour >= 6) & (expenses.tr_hour <= 23)].groupby('mcc_code').amount.sum()
mcc_codes_info['ratio_of_night_to_day'] = mcc_codes_info.night_expenses / mcc_codes_info.day_expenses
mcc_codes_info.update(tr_mcc_codes)

top10_highest_ratio_of_night_to_day = \
    mcc_codes_info.sort_values(by='ratio_of_night_to_day', ignore_index=False, ascending=False).head(10)

# import tabulate
print("Топ 10 mcc категорий с наибольшим отношением ночных трат к остальным тратам: ")
print(tabulate.tabulate(top10_highest_ratio_of_night_to_day, headers='keys', numalign='center', stralign='left', tablefmt='fancy_grid', ))


