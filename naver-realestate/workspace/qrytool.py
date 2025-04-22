import logging
import re

import pandas as pd
from logdecorator import log_on_end, log_on_error, log_on_start
from logging_config import configure_logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

SCHEMA = 'da'


engine = create_engine(DATABASE_URL)
logger = configure_logging(__file__)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# logger = configure_logging(__file__)


def add_schema_prefix(query):
    query = re.sub(r"(FROM\s+)(\w+)", rf"\1{SCHEMA}.\2", query, flags=re.IGNORECASE)
    query = re.sub(r"(JOIN\s+)(\w+)", rf"\1{SCHEMA}.\2", query, flags=re.IGNORECASE)
    query = re.sub(r"(CREATE TABLE\s+)(\w+)", rf"\1{SCHEMA}.\2", query, flags=re.IGNORECASE)
    query = re.sub(r"(DROP TABLE IF EXISTS\s+)(\w+)", rf"\1{SCHEMA}.\2", query, flags=re.IGNORECASE)
    return query


@log_on_start(logging.INFO, "{callable.__name__} : Function started", logger=logger)
@log_on_error(logging.ERROR, "{callable.__name__} : An error occurred", logger=logger)
@log_on_end(logging.INFO, "{callable.__name__} : Function finished", logger=logger)
def execute_query(query, session=None):
    if session is None:
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        close_session = True
    query = add_schema_prefix(query)
    logger.info(query)
    try:
        result = session.execute(text(query))
        session.commit()
        logger.info("Query executed successfully")
        return result
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        session.rollback()
        raise
    finally:
        if close_session:
            session.close()


@log_on_start(logging.INFO, "{callable.__name__} : Function started", logger=logger)
@log_on_error(logging.ERROR, "{callable.__name__} : An error occurred", logger=logger)
@log_on_end(logging.INFO, "{callable.__name__} : Function finished", logger=logger)
def load_data_into_dataframe(query, session=None):
    if session is None:
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        close_session = True
    try:
        query = add_schema_prefix(query)
        logger.info(query)
        with session.bind.connect() as connection:
            result = pd.read_sql_query(text(query), connection)
            logger.info(f'Data loaded successfully from query: {query}')
            return result
    except Exception as e:
        logger.error(f'An error occurred while loading data: {e}')
        raise
    finally:
        if close_session:
            session.close()


@log_on_start(logging.INFO, "{callable.__name__} : Function started", logger=logger)
@log_on_end(logging.INFO, "{callable.__name__} : Function finished", logger=logger)
@log_on_error(logging.ERROR, "{callable.__name__} : An error occurred", logger=logger)
def insert_dataframe_into_table(df, table_name, if_exists='replace', index=False, dtype=None, session=None):
    close_session = False
    if session is None:
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        close_session = True

    try:
        logger.info(f'to_sql : {SCHEMA}.{table_name}')
        ret = df.to_sql(table_name, con=session.bind, if_exists=if_exists, index=index, dtype=dtype, schema=SCHEMA)
        session.commit()
        print(f"Data inserted successfully into {table_name}")
        print(f'ret : {ret}')
    except Exception as e:
        session.rollback()
        print(f"An error occurred: {e}")
        raise
    finally:
        if close_session:
            session.close()
