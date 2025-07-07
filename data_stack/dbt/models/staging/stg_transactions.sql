{{
  config(
    materialized='view',
    docs={
      'description': 'Staging model for transaction data with automated EDA and data quality transformations'
    }
  )
}}

WITH raw_transactions AS (
  SELECT * FROM {{ source('raw_data', 'transactions') }}
),

cleaned_transactions AS (
  SELECT
    -- Generate unique transaction ID
    {{ dbt_utils.generate_surrogate_key(['date', 'name', 'amount', 'account']) }} AS transaction_id,

    -- Parse and clean date field
    CASE
      WHEN date IS NOT NULL AND date != ''
      THEN TRY_CAST(date AS DATE)
      ELSE NULL
    END AS transaction_date,

    -- Clean and standardize transaction name
    CASE
      WHEN TRIM(name) IS NOT NULL AND TRIM(name) != ''
      THEN TRIM(UPPER(name))
      ELSE 'UNKNOWN_TRANSACTION'
    END AS transaction_name,

    -- Clean amount field and handle negatives
    CASE
      WHEN amount IS NOT NULL AND amount != ''
      THEN CAST(amount AS DECIMAL(15,2))
      ELSE 0.00
    END AS amount,

    -- Derive absolute amount for analysis
    ABS(CASE
      WHEN amount IS NOT NULL AND amount != ''
      THEN CAST(amount AS DECIMAL(15,2))
      ELSE 0.00
    END) AS amount_abs,

    -- Categorize transaction flow
    CASE
      WHEN CAST(amount AS DECIMAL(15,2)) > 0 THEN 'INFLOW'
      WHEN CAST(amount AS DECIMAL(15,2)) < 0 THEN 'OUTFLOW'
      ELSE 'NEUTRAL'
    END AS transaction_flow,

    -- Clean status field
    CASE
      WHEN TRIM(LOWER(status)) IN ('posted', 'pending', 'cleared')
      THEN TRIM(LOWER(status))
      ELSE 'unknown'
    END AS status,

    -- Clean and standardize category
    CASE
      WHEN TRIM(category) IS NOT NULL AND TRIM(category) != ''
      THEN TRIM(LOWER(category))
      ELSE 'uncategorized'
    END AS category,

    -- Clean and standardize parent category
    CASE
      WHEN TRIM("parent category") IS NOT NULL AND TRIM("parent category") != ''
      THEN TRIM(LOWER("parent category"))
      ELSE 'other'
    END AS parent_category,

    -- Convert excluded flag
    CASE
      WHEN LOWER(TRIM(excluded)) IN ('true', '1', 'yes') THEN TRUE
      WHEN LOWER(TRIM(excluded)) IN ('false', '0', 'no') THEN FALSE
      ELSE FALSE
    END AS is_excluded,

    -- Clean tags field
    CASE
      WHEN TRIM(tags) IS NOT NULL AND TRIM(tags) != ''
      THEN TRIM(tags)
      ELSE NULL
    END AS tags,

    -- Clean and standardize transaction type
    CASE
      WHEN TRIM(LOWER(type)) IN ('regular', 'internal transfer', 'check', 'debit', 'credit')
      THEN TRIM(LOWER(type))
      ELSE 'other'
    END AS transaction_type,

    -- Clean account information
    CASE
      WHEN TRIM(account) IS NOT NULL AND TRIM(account) != ''
      THEN TRIM(account)
      ELSE 'UNKNOWN_ACCOUNT'
    END AS account_name,

    -- Clean account mask
    CASE
      WHEN TRIM("account mask") IS NOT NULL AND TRIM("account mask") != ''
      THEN TRIM("account mask")
      ELSE NULL
    END AS account_mask,

    -- Clean note field
    CASE
      WHEN TRIM(note) IS NOT NULL AND TRIM(note) != ''
      THEN TRIM(note)
      ELSE NULL
    END AS note,

    -- Clean recurring field
    CASE
      WHEN TRIM(recurring) IS NOT NULL AND TRIM(recurring) != ''
      THEN TRIM(recurring)
      ELSE NULL
    END AS recurring_pattern,

    -- Derive analysis fields for EDA
    EXTRACT(YEAR FROM TRY_CAST(date AS DATE)) AS transaction_year,
    EXTRACT(MONTH FROM TRY_CAST(date AS DATE)) AS transaction_month,
    EXTRACT(DAY FROM TRY_CAST(date AS DATE)) AS transaction_day,
    EXTRACT(DAYOFWEEK FROM TRY_CAST(date AS DATE)) AS day_of_week,

    -- Create amount buckets for analysis
    CASE
      WHEN ABS(CAST(amount AS DECIMAL(15,2))) < 10 THEN 'MICRO'
      WHEN ABS(CAST(amount AS DECIMAL(15,2))) < 100 THEN 'SMALL'
      WHEN ABS(CAST(amount AS DECIMAL(15,2))) < 1000 THEN 'MEDIUM'
      WHEN ABS(CAST(amount AS DECIMAL(15,2))) < 10000 THEN 'LARGE'
      ELSE 'VERY_LARGE'
    END AS amount_bucket,

    -- Flag high-value transactions
    CASE
      WHEN ABS(CAST(amount AS DECIMAL(15,2))) > 1000 THEN TRUE
      ELSE FALSE
    END AS is_high_value,

    -- Flag internal transfers
    CASE
      WHEN LOWER(TRIM(type)) = 'internal transfer' THEN TRUE
      ELSE FALSE
    END AS is_internal_transfer,

    -- Create weekend flag
    CASE
      WHEN EXTRACT(DAYOFWEEK FROM TRY_CAST(date AS DATE)) IN (1, 7) THEN TRUE
      ELSE FALSE
    END AS is_weekend,

    -- Add data quality flags
    CASE
      WHEN date IS NULL OR date = '' THEN FALSE
      WHEN name IS NULL OR TRIM(name) = '' THEN FALSE
      WHEN amount IS NULL OR amount = '' THEN FALSE
      ELSE TRUE
    END AS has_complete_data,

    -- Row metadata
    CURRENT_TIMESTAMP AS processed_at,
    '{{ run_started_at }}' AS dbt_run_timestamp,
    '{{ invocation_id }}' AS dbt_invocation_id

  FROM raw_transactions
),

eda_enhanced AS (
  SELECT *,
    -- Calculate percentile rankings for amounts
    PERCENT_RANK() OVER (ORDER BY amount_abs) AS amount_percentile,

    -- Calculate running totals by account
    SUM(amount) OVER (
      PARTITION BY account_name
      ORDER BY transaction_date
      ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_balance,

    -- Count transactions per day
    COUNT(*) OVER (
      PARTITION BY transaction_date
    ) AS daily_transaction_count,

    -- Flag outliers using IQR method
    CASE
      WHEN amount_abs > (
        PERCENTILE_CONT(0.75) OVER () +
        1.5 * (PERCENTILE_CONT(0.75) OVER () - PERCENTILE_CONT(0.25) OVER ())
      ) THEN TRUE
      ELSE FALSE
    END AS is_amount_outlier,

    -- Create business day flag
    CASE
      WHEN EXTRACT(DAYOFWEEK FROM transaction_date) BETWEEN 2 AND 6 THEN TRUE
      ELSE FALSE
    END AS is_business_day,

    -- Lag analysis for spending patterns
    LAG(amount, 1) OVER (
      PARTITION BY account_name
      ORDER BY transaction_date
    ) AS previous_transaction_amount,

    -- Calculate days since last transaction
    COALESCE(
      transaction_date - LAG(transaction_date, 1) OVER (
        PARTITION BY account_name
        ORDER BY transaction_date
      ),
      0
    ) AS days_since_last_transaction

  FROM cleaned_transactions
)

SELECT
  transaction_id,
  transaction_date,
  transaction_name,
  amount,
  amount_abs,
  transaction_flow,
  status,
  category,
  parent_category,
  is_excluded,
  tags,
  transaction_type,
  account_name,
  account_mask,
  note,
  recurring_pattern,
  transaction_year,
  transaction_month,
  transaction_day,
  day_of_week,
  amount_bucket,
  is_high_value,
  is_internal_transfer,
  is_weekend,
  is_business_day,
  has_complete_data,
  amount_percentile,
  running_balance,
  daily_transaction_count,
  is_amount_outlier,
  previous_transaction_amount,
  days_since_last_transaction,
  processed_at,
  dbt_run_timestamp,
  dbt_invocation_id

FROM eda_enhanced
WHERE has_complete_data = TRUE  -- Filter out incomplete records
