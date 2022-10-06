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

# В цикле по типам найти этот тип в другой таблице и проверить его описание. Если описание содержит нужный паттерн - 
# увеличить количество. 
def count_strs_contained_pattern(sample, sub_sample, pattern):
    count = 0
    for item in sub_sample:
        if re.search(pattern, sample.loc[item]) is not None:
            count += 1
    return count


subsample = transactions['tr_type'].sample(1000)  # Series of types

# Иногда выдает ошибку, но работает!
# types_contained_condition = count_strs_contained_pattern(sample=tr_types.tr_description,
#                                                          sub_sample=subsample,
#                                                          pattern='POS|АТМ')

# print("Соотношение имеющих в описании типа транзакции POS|АТМ ко всем типам транзакции в случайной выборке = ",
#       types_contained_condition / subsample.size)

# ############################################### Task 2 #########################################################

# Для столбца tr_type датафрейма transactions посчитайте частоту встречаемости всех типов
# транзакций tr_type в transactions. 
# Выведите топ-10 транзакций по частоте встречаемости (вывести для них tr_description тоже). 

# most_frequent = pd.DataFrame(
#     index=tr_types.index,
#     columns=['occurrence', 'tr_description'],
# )

# for type_of_transaction in tr_types.index:
#     most_frequent.occurrence[type_of_transaction]     = transactions.tr_type[(transactions.tr_type == type_of_transaction)].size
#     most_frequent.tr_description[type_of_transaction] = tr_types.tr_description[type_of_transaction]
# 
# sorted_occurrence = most_frequent.sort_values(by='occurrence', ignore_index=False, ascending=False).head(10)
# print_dataframe(sorted_occurrence)

# ############################################### Task 3 #########################################################
# В датафрейме transactions найдите клиента с максимальной суммой приходов на карту.
# В датафрейме transactions найдите клиента с максимальной суммой расходов по карте.
# Найдите модуль разницы для этих клиентов между суммой расходов и суммой приходов.

# customer_info = pd.DataFrame(
#     index=transactions.index.unique(),
#     columns=['expenses', 'deposits']
# )
# 
# groups_of_customer = transactions.groupby(level='customer_id')
# 
# for customer_id, operations in groups_of_customer:
#     positive_sum = 0
#     negative_sum = 0
# 
#     for number in operations.amount:
#         if number > 0:
#             positive_sum += number
#         else:
#             negative_sum -= number
# 
#     customer = pd.Series(data={
#         'expenses': round(negative_sum, 3),
#         'deposits': round(positive_sum, 3)
#     })
#     customer_info.loc[customer_id] = customer
# 
# customer_info['difference'] = np.abs(customer_info.deposits - customer_info.expenses)
# max_customer = customer_info.sort_values(by='deposits', ignore_index=False, ascending=False).head(1)
# min_customer = customer_info.sort_values(by='expenses', ignore_index=False, ascending=False).head(1)
# 
# print("\nКлиент с максимальной суммой приходов на карту: \n")
# print_dataframe(max_customer)
# 
# print("\nКлиент с максимальной суммой расходов на карту: \n")
# print_dataframe(min_customer)

# ############################################### Task 4 #########################################################

