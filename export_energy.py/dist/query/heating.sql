SELECT Tag, Value, Timestamp
FROM {table}
WHERE
  Tag IN ('1期累计热量','2期累计热量',
    '1期供水温度','1期回水温度','1期流量',
    '2期供水温度','2期回水温度','2期流量')
  AND Timestamp >= %(start_date)s
  AND Timestamp <  %(end_date)s
ORDER BY Timestamp;