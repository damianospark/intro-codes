conda create -n naver_crawl python=3.9
conda activate naver_crawl
pip install requests asyncio proxybroker nest_asyncio
conda install pandas sqlalchemy google-auth-oauthlib
conda install selenium==3.141.0 urllib3==1.26.18
pip install logdecorator psycopg2-binary icecream chardet beautifulsoup4 webdriver-manager
conda install -c anaconda beautifulsoup4
conda install -c conda-forge webdriver-manager

naver-realestate
conda env list
conda remove --name naver_crawl
conda activate naver_crawl
