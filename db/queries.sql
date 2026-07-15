-- ============================================================
-- NIFTY 100 FINANCIAL INTELLIGENCE
-- DAY 5 - SQLITE ANALYTICS QUERIES
-- ============================================================


-- QUERY 01
-- List all companies

SELECT
    id,
    company_name
FROM companies
ORDER BY company_name;


-- QUERY 02
-- Total number of companies

SELECT
    COUNT(*) AS total_companies
FROM companies;


-- QUERY 03
-- Companies with highest ROCE

SELECT
    id,
    company_name,
    roce_percentage
FROM companies
WHERE roce_percentage IS NOT NULL
ORDER BY roce_percentage DESC
LIMIT 10;


-- QUERY 04
-- Companies with highest ROE

SELECT
    id,
    company_name,
    roe_percentage
FROM companies
WHERE roe_percentage IS NOT NULL
ORDER BY roe_percentage DESC
LIMIT 10;


-- QUERY 05
-- Highest sales records

SELECT
    company_id,
    year,
    sales
FROM profitandloss
WHERE sales IS NOT NULL
ORDER BY sales DESC
LIMIT 10;


-- QUERY 06
-- Highest net profit records

SELECT
    company_id,
    year,
    net_profit
FROM profitandloss
WHERE net_profit IS NOT NULL
ORDER BY net_profit DESC
LIMIT 10;


-- QUERY 07
-- Average operating profit by company

SELECT
    company_id,
    AVG(operating_profit) AS average_operating_profit
FROM profitandloss
WHERE operating_profit IS NOT NULL
GROUP BY company_id
ORDER BY average_operating_profit DESC;


-- QUERY 08
-- Highest EPS records

SELECT
    company_id,
    year,
    eps
FROM profitandloss
WHERE eps IS NOT NULL
ORDER BY eps DESC
LIMIT 10;


-- QUERY 09
-- Highest total assets

SELECT
    company_id,
    year,
    total_assets
FROM balancesheet
WHERE total_assets IS NOT NULL
ORDER BY total_assets DESC
LIMIT 10;


-- QUERY 10
-- Highest borrowings

SELECT
    company_id,
    year,
    borrowings
FROM balancesheet
WHERE borrowings IS NOT NULL
ORDER BY borrowings DESC
LIMIT 10;


-- QUERY 11
-- Highest operating cash flow

SELECT
    company_id,
    year,
    operating_activity
FROM cashflow
WHERE operating_activity IS NOT NULL
ORDER BY operating_activity DESC
LIMIT 10;


-- QUERY 12
-- Highest net cash flow

SELECT
    company_id,
    year,
    net_cash_flow
FROM cashflow
WHERE net_cash_flow IS NOT NULL
ORDER BY net_cash_flow DESC
LIMIT 10;


-- QUERY 13
-- Company growth analytics

SELECT
    company_id,
    compounded_sales_growth,
    compounded_profit_growth,
    stock_price_cagr,
    roe
FROM analysis
ORDER BY roe DESC;


-- QUERY 14
-- Best stock price CAGR

SELECT
    company_id,
    stock_price_cagr
FROM analysis
WHERE stock_price_cagr IS NOT NULL
ORDER BY stock_price_cagr DESC
LIMIT 10;


-- QUERY 15
-- Company pros and cons

SELECT
    company_id,
    pros,
    cons
FROM prosandcons
ORDER BY company_id;


-- QUERY 16
-- Available annual reports

SELECT
    company_id,
    year,
    annual_report
FROM documents
WHERE annual_report IS NOT NULL
ORDER BY company_id, year DESC;


-- QUERY 17
-- Database table row count summary

SELECT 'analysis' AS table_name, COUNT(*) AS row_count
FROM analysis

UNION ALL

SELECT 'balancesheet', COUNT(*)
FROM balancesheet

UNION ALL

SELECT 'cashflow', COUNT(*)
FROM cashflow

UNION ALL

SELECT 'companies', COUNT(*)
FROM companies

UNION ALL

SELECT 'documents', COUNT(*)
FROM documents

UNION ALL

SELECT 'financial_ratios', COUNT(*)
FROM financial_ratios

UNION ALL

SELECT 'market_cap', COUNT(*)
FROM market_cap

UNION ALL

SELECT 'peer_groups', COUNT(*)
FROM peer_groups

UNION ALL

SELECT 'profitandloss', COUNT(*)
FROM profitandloss

UNION ALL

SELECT 'prosandcons', COUNT(*)
FROM prosandcons

UNION ALL

SELECT 'sectors', COUNT(*)
FROM sectors

UNION ALL

SELECT 'stock_prices', COUNT(*)
FROM stock_prices

ORDER BY table_name;


-- ============================================================
-- END OF DAY 5 SQL ANALYTICS QUERIES
-- ============================================================