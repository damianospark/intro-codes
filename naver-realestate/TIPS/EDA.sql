
-- 학습데이터 생성 쿼리

CREATE TABLE train_base_data AS
SELECT
  nc.complex_no,
  nc.complex_name,
    nc.latitude,
  nc.longitude,
  nc.total_household_count,
  nc.total_building_count,
  nc.use_approve_ymd,
  nc.cortar_address,
  nc.real_estate_type_name,
  ncd.pyeong_name,
  ncd.pyeong_name_decimal,
  ncd.pyeong_content,
  ncr.floor,
  ncr.trade_year,
  ncr.trade_month,
  ncr.formatted_trade_year_month,
  ncr.deal_price
FROM naver_complexes nc
LEFT JOIN (
SELECT DISTINCT ON (complex_no, pyeong_no)
    complex_no,
    pyeong_no,
    pyeong_name,
    pyeong_name_decimal,
    pyeong_content
FROM naver_complex_dongho
ORDER BY complex_no, pyeong_no
) ncd ON nc.complex_no =ncd.complex_no
LEFT JOIN naver_complex_realprices ncr ON ncd.pyeong_no =ncr.pyeong_no AND ncd.complex_no = ncr.complex_no;

# 학습용 데이터 추출
SELECT
    complex_name 아파트명,
    cortar_address 동네,
    real_estate_type_name 건물종류,
    latitude 위도,
    longitude 경도,
    CAST(REPLACE(pyeong_content, '공급 ', '') AS DECIMAL) AS 면적,
    floor 층,
    formatted_trade_year_month 거래년월일,
    total_household_count 가구수,
    total_building_count 동수,
    use_approve_ymd 사용승인년월일,
    deal_price 거래가
FROM train_base_data

# 거래일 패턴 오류 찾기 위한 쿼리
SELECT * FROM train_base_data WHERE formatted_trade_year_month !~ '^[0-9]{4}\.[0-9]{2}\.[0-9]{2}$';
