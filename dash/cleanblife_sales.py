import traceback

import mysql.connector
import numpy as np
import pandas as pd
from loguru import logger
from sqlalchemy import Float, Integer, String, create_engine, text


def fetch_cleanb_data():
    try:
        logger.info('get in -------------------------------')

        # PostgreSQL 데이터베이스 연결 설정

        engine = create_engine(DATABASE_URL)
        connection = engine.connect()
        print('Postgresql connection open')

        q = """
            SELECT
                c."ID",s.*,
                CASE WHEN c.gender IS NOT NULL AND TRIM(c.gender) != '' THEN c.gender || '자'
                ELSE NULL
                END AS 성별,
                c.user_email AS "주문자 이메일'",
                CASE
                    WHEN c.birthyear IS NOT NULL AND TRIM(c.birthyear) not in  ('','0') THEN
                        TO_CHAR(TO_DATE(c.birthyear || '-02-01', 'YYYY-MM-DD'), 'YYYY-MM-DD')
                    ELSE
                        NULL
                END AS 연령
            FROM da.sales02 s
            JOIN
                da.cust03 c ON s."고객ID" = c."ID";
        """
        # TO_CHAR(TO_DATE(c.birthyear || '-02-01', 'YYYY-MM-DD'), 'YYYY-MM-DD')

        df = pd.read_sql(text(q), connection)
        # Infinity와 -Infinity 값을 NaN으로 대체
        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.fillna("")  # NaN 값을 "NA" 문자열로 대체
        # data = [df.columns.tolist()] + df.values.tolist()
        df["결제일시"] = pd.to_datetime(df["결제일시"])

        connection.close()
        logger.info('new data => ', df)
    except Exception as e:
        traceback.print_exc()
        raise e

    # Close the MySQL connection
    # cursor.close()
    # conn.close()

    # Apply address modifications
    # df['배송주소'] = df['배송주소'].apply(replace_address_sido)
    # df['시도_군구'] = df['배송주소'].apply(extract_region)
    return df[df['정산'] == '합산']


# def main():
#     # Fetch data from MySQL and create pandas DataFrame
#     data_frame = fetch_data_from_mysql()

#     # Print the pandas DataFrame
#     print(data_frame)


# if __name__ == "__main__":
#     main()
