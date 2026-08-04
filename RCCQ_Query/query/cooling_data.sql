SELECT Tag, Value, Timestamp
FROM dailydata_sdzx
WHERE
  Tag IN ('1期累计热量', '2期累计热量','1期供水温度','1期回水温度','1期流量','2期供水温度','2期回水温度','2期流量')
--     Tag IN ('1期热量', '2期热量')
  AND Timestamp >= DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 1 MONTH), '%Y-%m-01')
  AND Timestamp <  DATE_FORMAT(CURDATE(), '%Y-%m-01')
ORDER BY Timestamp;

-- SELECT
--   Tag,
--   Value,
--   Timestamp
-- FROM
--   dailydata_sdzx
-- WHERE
--     Tag IN ('1期累计冷量', '2期累计冷量','1期供水温度','1期回水温度','1期流量','2期供水温度','2期回水温度','2期流量')
--  AND Timestamp >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
--   AND Timestamp <= CURDATE()
-- ORDER BY
--   Timestamp;