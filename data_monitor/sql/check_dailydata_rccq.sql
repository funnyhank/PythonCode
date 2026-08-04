SELECT COUNT(*) AS record_count
FROM dailydata_rccq
WHERE DATE(Record_time) = CURDATE();
