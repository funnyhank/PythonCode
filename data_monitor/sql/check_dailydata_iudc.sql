SELECT COUNT(*) AS record_count
FROM dailydata_iudc
WHERE DATE(Record_time) = CURDATE();
