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
    print(tabulate.tabulate(dataframe, headers='keys', tablefmt='fancy_grid'))


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

# # ############################################### Task 4 #########################################################
# # Найдите среднее арифметическое и медиану по amount по всем типам транзакций из топ 10 из задания 2
# # Найдите среднее арифметическое и медиану по amount по всем типам транзакций для клиентов из задания 3

tr_types_top10_info = pd.DataFrame(
    index=top10.index,
    columns=['mean', 'median']
)

all_top10_trs = transactions[transactions.tr_type.isin(top10.index)]
all_top10_tr_groups = all_top10_trs.groupby('tr_type')

tr_types_top10_info['mean'] = all_top10_tr_groups.amount.mean()
tr_types_top10_info['median'] = all_top10_tr_groups.amount.median()

print("\nИнформация о amount по всем типам транзакций из топ 10 (результат задания 2):")
print_dataframe(tr_types_top10_info)

# надо написать функцию, которая дает все типы транзакций с их описанием у клиента. 

# tr_types_min_customer_info = pd.DataFrame()
# tr_types_max_customer_info = pd.DataFrame()
# min_customer_id = min_customer.index[0]
# max_customer_id = max_customer.index[0]
# 
# for type_of_transaction in transactions.loc[min_customer_id].tr_type.unique():
#     this_cus_operations = transactions.loc[min_customer_id]
#     tr_types_min_customer_info[type_of_transaction] = \
#         this_cus_operations[this_cus_operations.tr_type == type_of_transaction].amount.describe()

# if min_customer_id == max_customer_id:
#     print("\nТ.к. идентификаторы клиента с максимальной суммой приходов на карту и "
#           "клиента с максимальной суммой расходов по карте совпадают, таблица для одного человека только одна:")
#     print_dataframe(tr_types_min_customer_info)
# else:
#     print("\nИнформация о amount по всем типам транзакций для клиента с максимальной суммой расходов по карте"
#           " (результат задания 3):")
#     print_dataframe(tr_types_min_customer_info)
# 
#     for type_of_transaction in transactions.loc[max_customer_id].tr_type.unique():
#         this_cus_operations = transactions.loc[max_customer_id]
#         tr_types_max_customer_info[type_of_transaction] = \
#             this_cus_operations[this_cus_operations.tr_type == type_of_transaction].amount.describe()
# 
#     print("\nИнформация о amount по всем типам транзакций для клиента с максимальной суммой приходов на карту"
#           " (результат задания 3):")
#     print_dataframe(tr_types_max_customer_info)
# 
# # ############################################### Task 5 #########################################################
# 
# transactions = pd.merge(transactions, gender_train, how='left')
# transactions = pd.merge(transactions, tr_mcc_codes, how='inner')
# transactions = pd.merge(transactions, tr_types, how='inner')
# transactions.shape
