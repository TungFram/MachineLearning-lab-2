import gdown
import re
import tabulate

import numpy as np
import pandas as pd

download_pattern = 'https://drive.google.com/uc?id='
filenames = [
    'tr_mcc_codes.scv',
    'tr_types.scv',
    'transactions.scv',
    'gender_train.scv'
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

files = []
for i in range(len(download_links)):
    files.append(gdown.download(download_links[i], filenames[i]))

files_info = pd.DataFrame(dtype=str,
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
files_info['file'] = files

filenames.clear()
share_urls.clear()
ids.clear()
download_links.clear()
files.clear()

print(tabulate.tabulate(files_info, headers='keys', tablefmt='fancy_grid'))
