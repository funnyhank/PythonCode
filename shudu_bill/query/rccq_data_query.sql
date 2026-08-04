SELECT Tag, Value, Record_time
FROM dailydata_rccq
WHERE
  Tag IN ('east11A', 'east11B','west21A','west21B','D1_QQ_1150_BTU','D2_QQ_1150_BTU',
    'D3_QQ_1150_BTU','D4_QQ_1150_BTU','D5_QQ_1150_BTU','D6_QQ_1150_BTU','D7_QQ_1150_BTU','D8_QQ_1150_BTU',
    'QI_120A','QI_120B','QI_120D','QI_120E','QI_120F','QI_120H','QI_120K','QI_120M')

  AND Record_time >= '2025-01-01 00:00:00'

ORDER BY Record_time;

