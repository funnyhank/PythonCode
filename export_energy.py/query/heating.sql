SELECT Tag, Value, Timestamp
FROM {table}
WHERE
  Tag IN ('1期累计热量','2期累计热量')
  AND Timestamp >= %(start_date)s
  AND Timestamp <  %(end_date)s
ORDER BY Timestamp;