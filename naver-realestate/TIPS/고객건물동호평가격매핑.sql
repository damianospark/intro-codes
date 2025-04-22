

DROP INDEX IF EXISTS idx_address_with_extracted;
DROP MATERIALIZED VIEW IF EXISTS address_with_extracted;
DROP TABLE IF EXISTS alladdr_naver_joins;

CREATE MATERIALIZED VIEW address_with_extracted AS
SELECT old_addr,new_addr,building_name,sub_building_no,lati,longi,hcode,r1,r2,r3,bcode, substring(old_addr FROM '[동가리] ([0-9]+[-]*[0-9]*)' ) AS extracted_number
FROM addressalls;

CREATE INDEX idx_address_with_extracted ON address_with_extracted(extracted_number);


CREATE TABLE alladdr_naver_joins AS
SELECT a.*, n.*
FROM address_with_extracted a
JOIN naver_complexes n
ON n.detail_address = a.extracted_number
AND 6371000 * 2 * ASIN(SQRT(
    POWER(SIN((RADIANS(n.latitude) - RADIANS(a.lati)) / 2), 2) +
    COS(RADIANS(a.lati)) * COS(RADIANS(n.latitude)) *
    POWER(SIN((RADIANS(n.longitude) - RADIANS(a.longi)) / 2), 2)
)) <= 3000;


-- customatrix 에서 건물,동,호 정보 분리한 값과 네이버 집합건물 정보를 조인
-- customatrix의 all_id 가 중요하며 naver_complex에서는 complex_no가 중요.

DROP INDEX IF EXISTS idx_customatrix_complex_dong_ho_old_addr_extracted;
DROP MATERIALIZED VIEW IF EXISTS address_with_extracted;
DROP TABLE IF EXISTS customatrix_complex_dong_ho_joins;

CREATE MATERIALIZED VIEW customatrix_complex_dong_ho_old_addr_extracted AS
SELECT all_id,회원주소,회원lati,회원longi,회원주소1,회원주소2,회원주소1_old,동,호,회원주소_reduced,동네,건물명,잔여문자열, substring(회원주소1_old FROM '[동가리] ([0-9]+[-]*[0-9]*)' ) AS extracted_number
FROM customatrix_complex_dong_ho;

CREATE INDEX idx_customatrix_complex_dong_ho_old_addr_extracted ON customatrix_complex_dong_ho_old_addr_extracted(extracted_number);

CREATE TABLE customatrix_complex_dong_ho_joins AS
SELECT a.*, n.*
FROM customatrix_complex_dong_ho_old_addr_extracted a
JOIN naver_complexes n
ON n.detail_address = a.extracted_number
AND 6371000 * 2 * ASIN(SQRT(
    POWER(SIN((RADIANS(n.latitude) - RADIANS(a.회원lati)) / 2), 2) +
    COS(RADIANS(a.회원lati)) * COS(RADIANS(n.latitude)) *
    POWER(SIN((RADIANS(n.longitude) - RADIANS(a.회원longi)) / 2), 2)
)) <= 3000;


CREATE TABLE tmp_complex_dong_ho_pyeong AS
SELECT
  ccdh.all_id,
  ccdh.건물명,
  COALESCE(NULLIF(ccdh.동, ''), '1동') 동,
  ccdh.호,
  ccdh.동네,
  ccdh.complex_name,
  ccdh.complex_no,
  ncd.build_name,
  ncd.ho_name,
  ncd.ho_floor, ncd.pyeong_no,ncd.pyeong_name
FROM
  customatrix_complex_dong_ho_joins ccdh
  LEFT JOIN naver_complex_dongho ncd ON
  ncd.complex_no = ccdh.complex_no
  AND ncd.build_name || '동' = COALESCE(NULLIF(ccdh.동, ''), '1동')
  AND ncd.ho_name||'호' = ccdh.호;

CREATE TABLE tmp_complex_realprices AS
SELECT
  ccdh.all_id,
  ccdh.건물명,
  ccdh.동,
  ccdh.호,
  ccdh.동네,
  ccdh.complex_name,
  ccdh.complex_no,
  ccdh.build_name,
  ccdh.ho_name,
  ccdh.ho_floor,
  ncp1.pyeong_no, ccdh.pyeong_name, ncp1.trade_type,ncp1.deal_price,ncp1.formatted_price,
  ncp1.formatted_trade_year_month
FROM
  tmp_complex_dong_ho_pyeong ccdh
  LEFT JOIN naver_complex_realprices ncp1 ON ncp1.complex_no = ccdh.complex_no AND ncp1.pyeong_no = ccdh.pyeong_no ;

CREATE TABLE tmp_complex_realprices_max AS
SELECT *
FROM (
  SELECT
    all_id,
    건물명,
    동,
    호,
    동네,
    complex_name 네이버_건물명,
    complex_no,
    build_name 네이버_동,
    ho_name 네이버_호,
    ho_floor 층,
    pyeong_no,
    pyeong_name 평수,
    trade_type 거래유형,
    deal_price 매매가,
    formatted_price 매매가_한글,
    formatted_trade_year_month 거래일,
    ROW_NUMBER() OVER (PARTITION BY complex_no, build_name, ho_name ORDER BY formatted_trade_year_month DESC) AS rn
  FROM
    tmp_complex_realprices
) subquery
WHERE rn = 1;

CREATE TABLE tmp_complex_realprices2 AS
SELECT
  ccdh.all_id,
  ccdh.건물명,
  ccdh.동,
  ccdh.호,
  ccdh.동네,
  ccdh.complex_name,
  ccdh.complex_no,
  ccdh.build_name,
  ccdh.ho_name,
  ccdh.ho_floor,
  ncp1.pyeong_no, ccdh.pyeong_name, ncp1.trade_type,ncp1.lease_price, ncp1.rent_price,ncp1.formatted_price,
  ncp1.formatted_trade_year_month
FROM
  tmp_complex_dong_ho_pyeong ccdh
  LEFT JOIN naver_complex_realprices2 ncp1 ON ncp1.complex_no = ccdh.complex_no AND ncp1.pyeong_no = ccdh.pyeong_no ;


CREATE TABLE tmp_complex_realprices2_max AS
SELECT *
FROM (
  SELECT
    all_id,
    건물명,
    동,
    호,
    동네,
    complex_name 네이버_건물명,
    complex_no,
    build_name 네이버_동,
    ho_name 네이버_호,
    ho_floor 층,
    pyeong_no,
    pyeong_name 평수,
    trade_type 거래유형,
    lease_price 전세가,
    rent_price 월세가,
    formatted_price 전월세가_한글,
    formatted_trade_year_month 거래일,
    ROW_NUMBER() OVER (PARTITION BY complex_no, build_name, ho_name ORDER BY formatted_trade_year_month DESC) AS rn
  FROM
    tmp_complex_realprices2
) subquery
WHERE rn = 1;



SELECT
  a.*,
  b.전세가,
  b.월세가,
  b.거래일 전월세_거래일
FROM tmp_complex_realprices_max a
LEFT JOIN tmp_complex_realprices2_max b ON a.all_id = b.all_id AND a.complex_no = b.complex_no AND a.pyeong_no = b.pyeong_no
ORDER BY a.매매가, b.전세가, b.월세가;



complex_no,pyeong_no,trade_type,trade_year,trade_month,trade_date,deal_price,            floor,representative_area,exclusive_area,formatted_price,formatted_trade_year_month,trade_base_year,trade_base_month,delete_yn
complex_no,pyeong_no,trade_type,trade_year,trade_month,trade_date,lease_price,rent_price,floor,representative_area,exclusive_area,formatted_price,formatted_trade_year_month,trade_base_year,trade_base_month,delete_yn





CREATE TABLE tmp_complex_callprices AS
SELECT
  ccdh.all_id,
  ccdh.건물명,
  ccdh.동,
  ccdh.호,
  ccdh.동네,
  ccdh.complex_name,
  ccdh.complex_no,
  ccdh.build_name,
  ccdh.ho_name,
  ccdh.ho_floor,
  ccdh.pyeong_no,ncp1.area_name, ncp1.trade_type_code,ncp1.deal_or_warrant_prc,
  ncp1.article_confirm_ymd
FROM
  tmp_complex_dong_ho_pyeong ccdh
  LEFT JOIN naver_complex_callprices ncp1 ON ncp1.complex_no = ccdh.complex_no AND ncp1.area_name = ccdh.pyeong_name ;

SELECT *
FROM (
  SELECT
  all_id,
  건물명,
  동,
  호,
  동네,
  complex_name 네이버_건물명,
  complex_no,
  build_name 네이버_동,
  ho_name 네이버_호,
  ho_floor 층,
  pyeong_no,
  area_name 평수,
  trade_type_code 거래유형,
  deal_or_warrant_prc 가격,
  article_confirm_ymd 등록일,
    ROW_NUMBER() OVER (PARTITION BY complex_no, build_name, ho_name ORDER BY article_confirm_ymd DESC) AS rn
  FROM
    tmp_complex_callprices
) subquery
WHERE rn = 1;






CREATE TABLE tmp_complex_callprices2 AS
SELECT
  ccdh.all_id,
  ccdh.건물명,
  ccdh.동,
  ccdh.호,
  ccdh.동네,
  ccdh.complex_name,
  ccdh.complex_no,
  ccdh.build_name,
  ccdh.ho_name,
  ccdh.ho_floor,
  ccdh.pyeong_no,ncp1.area_name, ncp1.trade_type_code,ncp1.deal_or_warrant_prc,
  ncp1.article_confirm_ymd
FROM
  tmp_complex_dong_ho_pyeong ccdh
  LEFT JOIN naver_complex_callprices2 ncp1 ON ncp1.complex_no = ccdh.complex_no AND ncp1.area_name = ccdh.pyeong_name ;

SELECT *
FROM (
  SELECT
  all_id,
  건물명,
  동,
  호,
  동네,
  complex_name 네이버_건물명,
  complex_no,
  build_name 네이버_동,
  ho_name 네이버_호,
  ho_floor 층,
  pyeong_no,
  area_name 평수,
  trade_type_code 거래유형,
  deal_or_warrant_prc 가격,
  article_confirm_ymd 등록일,
    ROW_NUMBER() OVER (PARTITION BY complex_no, build_name, ho_name ORDER BY article_confirm_ymd DESC) AS rn
  FROM
    tmp_complex_callprices2
) subquery
WHERE rn = 1;


