import gdown
import re

import gdown as gdown
import numpy as np
import pandas as pd

download_pattern = 'https://drive.google.com/uc?id='
filenames = [
    'tr_mcc_codes',
    'tr_types',
    'transactions',
    'gender_train'
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

filenames.clear()
share_urls.clear()
ids.clear()
download_links.clear()

files = []
for i in range(len(files_info.download_url)):
    files.append(gdown.download(files_info.download_url[i], files_info.file_name[i]))


