-- Schema verification queries
USE ecommerce_analytics;
SHOW TABLES;
SELECT TABLE_NAME, TABLE_ROWS
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'ecommerce_analytics';