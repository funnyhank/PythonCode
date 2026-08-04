SELECT COUNT(*) AS count
FROM dailydata_sdzx
WHERE Timestamp >= NOW() - INTERVAL %(interval)s MINUTE;
