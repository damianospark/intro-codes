import logging
import re
import time

import pandas as pd
from logdecorator import log_on_end, log_on_error, log_on_start
from logging_config import configure_logging
from sqlalchemy import (MetaData, Table, UniqueConstraint, create_engine,
                        inspect, text, update)
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
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
    query = query.replace(f"FROM {SCHEMA}.AGE", "FROM AGE")
    return query


@log_on_start(logging.INFO, f"{callable.__name__} : Function started", logger=logger)  # type: ignore
@log_on_error(logging.ERROR, f"{callable.__name__} : An error occurred", logger=logger)  # type: ignore
@log_on_end(logging.INFO, f"{callable.__name__} : Function finished", logger=logger)  # type: ignore
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


@log_on_start(logging.INFO, f"{callable.__name__} : Function started", logger=logger)  # type: ignore
@log_on_error(logging.ERROR, f"{callable.__name__} : An error occurred", logger=logger)  # type: ignore
@log_on_end(logging.INFO, f"{callable.__name__} : Function finished", logger=logger)  # type: ignore
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


@log_on_start(logging.INFO, f"{callable.__name__} : Function started", logger=logger)  # type: ignore
@log_on_end(logging.INFO, f"{callable.__name__} : Function finished", logger=logger)  # type: ignore
@log_on_error(logging.ERROR, f"{callable.__name__} : An error occurred", logger=logger)  # type: ignore
def insert_dataframe_into_table(df, table_name, if_exists='replace', index=False, dtype=None, session=None, index_elements=None):
    close_session = False
    if session is None:
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        close_session = True

    try:
        if if_exists == 'append':
            metadata = MetaData(schema=SCHEMA)
            metadata.reflect(bind=engine)

            # 테이블이 존재하지 않으면 생성
            if f"{SCHEMA}.{table_name}" not in metadata.tables:
                df.to_sql(table_name, con=session.bind, if_exists='replace', index=index, dtype=dtype, schema=SCHEMA)
                logger.info(f"Table {SCHEMA}.{table_name} does not exist and will be created")
            else:
                if not index_elements or not set(index_elements).issubset(df.columns):
                    raise Exception(f"index_elements must be a subset of the columns in the dataframe\n{df.columns}\n{index_elements}")
                table = Table(table_name, metadata, autoload_with=engine, schema=SCHEMA)
                constraints = table.constraints

                # 유니크 제약 조건 추가
                if not any(isinstance(constraint, UniqueConstraint) and set(index_elements).issubset(
                    set(constraint.columns.keys())) for constraint in constraints):
                    unique_constraint_name = f'{table_name}_{"_".join(index_elements)}_unique'
                    unique_columns = ", ".join(index_elements)
                    alter_table_query = f'ALTER TABLE {SCHEMA}.{table_name} ADD CONSTRAINT {unique_constraint_name} UNIQUE ({unique_columns});'
                    session.execute(text(alter_table_query))
                    session.commit()

                # Upsert 문장 생성 및 실행
                stmt = insert(table).values(df.to_dict(orient='records'))
                upsert_stmt = stmt.on_conflict_do_nothing(index_elements=index_elements)
                session.execute(upsert_stmt)
                session.commit()
                logger.info(f"Upsert into {SCHEMA}.{table_name} completed successfully")
        else:
            logger.info(f'to_sql : {SCHEMA}.{table_name}')
            ret = df.to_sql(table_name, con=session.bind, if_exists=if_exists, index=index, dtype=dtype, schema=SCHEMA)
            session.commit()
            print(f"Data inserted successfully into {table_name}")
            print(f'ret : {ret}')
    except IntegrityError as e:
        session.rollback()
        logger.error(f"Integrity error during upsert: {e}")
        raise
    except Exception as e:
        session.rollback()
        print(f"An error occurred: {e}")
        raise
    finally:
        if close_session:
            session.close()


@log_on_start(logging.INFO, f"{callable.__name__} : Function started", logger=logger)  # type: ignore
@log_on_end(logging.INFO, f"{callable.__name__} : Function finished", logger=logger)  # type: ignore
@log_on_error(logging.ERROR, f"{callable.__name__} : An error occurred", logger=logger)  # type: ignore
def upsert_dataframe_into_table(df, table_name, index_elements, session=None):
    if session is None:
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        close_session = True

    try:
        metadata = MetaData(schema=SCHEMA)
        metadata.reflect(bind=engine)
        if f"{SCHEMA}.{table_name}" not in metadata.tables:
            insert_dataframe_into_table(df, table_name, if_exists='replace', index=False, session=session)
            logger.info(f"Table {SCHEMA}.{table_name} does not exist and will be created")

        table = Table(table_name, metadata, autoload_with=engine, schema=SCHEMA)
        constraints = table.constraints  # 테이블의 모든 제약 조건을 로드
        # print(table.constraints)
        # Constraint 확인 및 생성
        if not any(isinstance(constraint, UniqueConstraint) and set(index_elements).issubset(
            set(constraint.columns.keys())) for constraint in constraints):
            # 유니크 제약 조건 추가를 위한 SQL 쿼리 문자열 생성
            unique_constraint_name = f'{table_name}_{"_".join(index_elements)}_unique'
            unique_columns = ", ".join(index_elements)
            alter_table_query = f'ALTER TABLE {SCHEMA}.{table_name} ADD CONSTRAINT {unique_constraint_name} UNIQUE ({unique_columns});'
            # SQL 쿼리 실행
            session.execute(alter_table_query)  # type: ignore
            session.commit()

        # Upsert 작업
        stmt = insert(table).values(df.to_dict(orient='records'))
        upsert_stmt = stmt.on_conflict_do_update(
            index_elements=index_elements,
            set_={c.name: c for c in stmt.excluded}
        )

        session.execute(upsert_stmt)
        session.commit()
        logger.info(f"Upsert into {SCHEMA}.{table_name} completed successfully")

    except IntegrityError as e:
        session.rollback()
        logger.error(f"Integrity error during upsert: {e}")
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"An error occurred during upsert: {e}")
        raise
    finally:
        if close_session:
            session.close()


@log_on_start(logging.INFO, f"{callable.__name__} : Function started", logger=logger)  # type: ignore
@log_on_end(logging.INFO, f"{callable.__name__} : Function finished", logger=logger)  # type: ignore
@log_on_error(logging.ERROR, f"{callable.__name__} : An error occurred", logger=logger)  # type: ignore
def update_dataframe_into_table(df, table_name, index_elements, session=None):
    if session is None:
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        close_session = True

    batch_size = 200  # 한 번에 처리할 행의 수
    num_batches = len(df) // batch_size + (1 if len(df) % batch_size else 0)
    for i in range(num_batches):
        batch = df.iloc[i * batch_size:(i + 1) * batch_size]
        for idx, row in batch.iterrows():
            stmt = update(table_name).where(index_elements == idx).values(**row.to_dict())
            session.execute(stmt)
    session.commit()
    if close_session:
        session.close()
