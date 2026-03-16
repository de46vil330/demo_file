# ClaimInformatics Standard Calculations Reference

**Version:** 3.2 (Consolidated + Pre & Post Mapping Validation)  
**Last Updated:** March 2026  
**Purpose:** Unified calculation definitions for SQL, DAX, and Power BI implementations  
**Consolidates:** CI_Calculations.docx + CI_Calculations_v2.md + Pre & Post Mapping Validation Portal v2.0

---

## Table of Contents

1. [Core Metrics](#core-metrics)
2. [Pre-Pay Metrics](#pre-pay-metrics)
3. [Post-Pay Metrics](#post-pay-metrics)
4. [Financial Calculations](#financial-calculations)
5. [Date & Time Metrics](#date-time-metrics)
6. [DAX Formula Reference](#dax-formula-reference)
7. [Power BI Implementation Guidelines](#power-bi-guidelines)
8. [Appendix: Field Reference](#appendix-field-reference)
9. [Field Profiler & Data Completeness Metrics](#field-profiler-metrics)
10. [Pre & Post Mapping Validation Metrics](#pre-post-mapping-metrics)

---

## Core Metrics

### 1. Number of Employees

**Definition:** Count of distinct employees/members in the claim data.

**SQL Query (Primary):**
```sql
SELECT COUNT(DISTINCT cl.cl_memid)
FROM claim cl
WHERE cl.cl_clientpk = :clientpk
  AND COALESCE(cl.cl_ci_ignore, 0) = 0;
```

**SQL Query (with Fallback Logic):**
```sql
SELECT COUNT(DISTINCT 
    COALESCE(cl_memid, cl_eessn, CONCAT(cl_eefn, cl_eeln, cl_eedob))
)
FROM claim cl
WHERE cl.cl_clientpk = :clientpk
  AND COALESCE(cl.cl_ci_ignore, 0) = 0;
```

**DAX Measure:**
```dax
Employee Count = 
CALCULATE(
    DISTINCTCOUNT(Claim[cl_memid]),
    Claim[cl_ci_ignore] = 0 || ISBLANK(Claim[cl_ci_ignore])
)
```

**DAX Measure (with Fallback Logic):**
```dax
Employee Count Fallback = 
VAR ByMemID = DISTINCTCOUNT(Claim[cl_memid])
VAR BySSN = DISTINCTCOUNT(Claim[cl_eessn])
VAR ByName = DISTINCTCOUNT(Claim[cl_eefn] & Claim[cl_eeln] & Claim[cl_eedob])
RETURN
    CALCULATE(
        COALESCE(ByMemID, BySSN, ByName),
        Claim[cl_ci_ignore] = 0 || ISBLANK(Claim[cl_ci_ignore])
    )
```

**Power BI Visual:** Card visual with formatted display

---

### 2. Number of Patients

**Definition:** Count of distinct patients across all claims.

**SQL Query (Primary):**
```sql
SELECT COUNT(DISTINCT cl.cl_ptid)
FROM claim cl
WHERE cl.cl_clientpk = :clientpk
  AND COALESCE(cl.cl_ci_ignore, 0) = 0;
```

**SQL Query (with Fallback Logic):**
```sql
SELECT COUNT(DISTINCT 
    COALESCE(cl_ptid, cl_ptssn, cl_ptacctno, CONCAT(cl_ptfn, cl_ptln, cl_ptdob))
)
FROM claim cl
WHERE cl.cl_clientpk = :clientpk
  AND COALESCE(cl.cl_ci_ignore, 0) = 0;
```

**DAX Measure:**
```dax
Patient Count = 
CALCULATE(
    DISTINCTCOUNT(Claim[cl_ptid]),
    Claim[cl_ci_ignore] = 0 || ISBLANK(Claim[cl_ci_ignore])
)
```

**DAX Measure (with Fallback Logic):**
```dax
Patient Count Fallback = 
VAR ByPtID = DISTINCTCOUNT(Claim[cl_ptid])
VAR BySSN = DISTINCTCOUNT(Claim[cl_ptssn])
VAR ByAcct = DISTINCTCOUNT(Claim[cl_ptacctno])
VAR ByName = DISTINCTCOUNT(Claim[cl_ptfn] & Claim[cl_ptln] & Claim[cl_ptdob])
RETURN
    CALCULATE(
        COALESCE(ByPtID, BySSN, ByAcct, ByName),
        Claim[cl_ci_ignore] = 0 || ISBLANK(Claim[cl_ci_ignore])
    )
```

**Power BI Visual:** Card visual with formatted display

---

### 3. Claim Count

**Definition:** Total number of distinct claims.

**SQL Query:**
```sql
SELECT COUNT(DISTINCT cl.cl_claimid)
FROM claim cl
WHERE cl.cl_clientpk = :clientpk
  AND COALESCE(cl.cl_ci_ignore, 0) = 0;
```

**DAX Measure:**
```dax
Claim Count = 
CALCULATE(
    DISTINCTCOUNT(Claim[cl_claimid]),
    Claim[cl_ci_ignore] = 0 || ISBLANK(Claim[cl_ci_ignore])
)
```

**Power BI Visual:** Card visual

---

### 4. Claimline Count

**Definition:** Total number of service lines across all claims.

**SQL Query:**
```sql
SELECT COUNT(*)
FROM claim cl
JOIN claimline ln 
    ON cl.cl_claimid = ln.ln_claimid 
    AND cl.cl_clientpk = ln.ln_clientpk
WHERE ln.ln_clientpk = :clientpk
  AND COALESCE(cl.cl_ci_ignore, 0) = 0
  AND COALESCE(ln.ln_ci_ignore, 0) = 0;
```

**DAX Measure:**
```dax
Claimline Count = 
CALCULATE(
    COUNTROWS(Claimline),
    FILTER(
        Claimline,
        (Claimline[ln_ci_ignore] = 0 || ISBLANK(Claimline[ln_ci_ignore]))
    ),
    FILTER(
        RELATEDTABLE(Claim),
        Claim[cl_ci_ignore] = 0 || ISBLANK(Claim[cl_ci_ignore])
    )
)
```

**Power BI Visual:** Card visual

---

### 5. Total Paid / Total Spend

**Definition:** Sum of all paid amounts across claim lines.

**SQL Query:**
```sql
SELECT SUM(ln.ln_paid)
FROM claim cl
JOIN claimline ln 
    ON cl.cl_claimid = ln.ln_claimid 
    AND cl.cl_clientpk = ln.ln_clientpk
WHERE ln.ln_clientpk = :clientpk
  AND COALESCE(cl.cl_ci_ignore, 0) = 0
  AND COALESCE(ln.ln_ci_ignore, 0) = 0;
```

**DAX Measure:**
```dax
Total Paid = 
CALCULATE(
    SUM(Claimline[ln_paid]),
    Claimline[ln_ci_ignore] = 0 || ISBLANK(Claimline[ln_ci_ignore]),
    FILTER(
        RELATEDTABLE(Claim),
        Claim[cl_ci_ignore] = 0 || ISBLANK(Claim[cl_ci_ignore])
    )
)
```

**DAX Measure (Formatted Display):**
```dax
Total Paid Formatted = 
VAR TotalAmount = [Total Paid]
RETURN
    IF(TotalAmount >= 1000000,
        FORMAT(TotalAmount / 1000000, "$#,##0.0") & "M",
        IF(TotalAmount >= 1000,
            FORMAT(TotalAmount / 1000, "$#,##0.0") & "K",
            FORMAT(TotalAmount, "$#,##0")
        )
    )
```

**Power BI Visual:** Card visual with currency formatting

---

### 6. Scope Begin Paid Date

**Definition:** Earliest payment date in the dataset.

**SQL Query:**
```sql
SELECT MIN(ln.ln_datepaid)
FROM claim cl
JOIN claimline ln 
    ON cl.cl_claimid = ln.ln_claimid 
    AND cl.cl_clientpk = ln.ln_clientpk
WHERE ln.ln_clientpk = :clientpk
  AND COALESCE(cl.cl_ci_ignore, 0) = 0
  AND COALESCE(ln.ln_ci_ignore, 0) = 0;
```

**DAX Measure:**
```dax
Scope Begin Date = 
CALCULATE(
    MIN(Claimline[ln_datepaid]),
    Claimline[ln_ci_ignore] = 0 || ISBLANK(Claimline[ln_ci_ignore])
)
```

**Power BI Visual:** Card visual with date formatting

---

### 7. Scope End Paid Date

**Definition:** Latest payment date in the dataset.

**SQL Query:**
```sql
SELECT MAX(ln.ln_datepaid)
FROM claim cl
JOIN claimline ln 
    ON cl.cl_claimid = ln.ln_claimid 
    AND cl.cl_clientpk = ln.ln_clientpk
WHERE ln.ln_clientpk = :clientpk
  AND COALESCE(cl.cl_ci_ignore, 0) = 0
  AND COALESCE(ln.ln_ci_ignore, 0) = 0;
```

**DAX Measure:**
```dax
Scope End Date = 
CALCULATE(
    MAX(Claimline[ln_datepaid]),
    Claimline[ln_ci_ignore] = 0 || ISBLANK(Claimline[ln_ci_ignore])
)
```

**Power BI Visual:** Card visual with date formatting

---

## Pre-Pay Metrics

### 8. Pre-Pay Savings Identified

**Definition:** Total savings identified through pre-payment review.

**SQL Query:**
```sql
SELECT SUM(ln.ln_savings_identified)
FROM claim cl
JOIN claimline ln 
    ON cl.cl_claimid = ln.ln_claimid 
    AND cl.cl_clientpk = ln.ln_clientpk
WHERE ln.ln_clientpk = :clientpk
  AND cl.cl_service_type = 'Pre-Payment'
  AND COALESCE(cl.cl_ci_ignore, 0) = 0
  AND COALESCE(ln.ln_ci_ignore, 0) = 0;
```

**DAX Measure:**
```dax
PrePay Savings = 
CALCULATE(
    SUM(Claimline[ln_savings_identified]),
    Claim[cl_service_type] = "Pre-Payment",
    Claimline[ln_ci_ignore] = 0 || ISBLANK(Claimline[ln_ci_ignore])
)
```

**Power BI Visual:** Card visual with currency formatting

---

### 9. Pre-Pay Savings Rate

**Definition:** Percentage of analyzed spend that resulted in savings.

**SQL Query:**
```sql
SELECT 
    CASE 
        WHEN SUM(ln.ln_charged) > 0 
        THEN (SUM(ln.ln_savings_identified) / SUM(ln.ln_charged)) * 100
        ELSE 0 
    END AS savings_rate
FROM claim cl
JOIN claimline ln 
    ON cl.cl_claimid = ln.ln_claimid 
    AND cl.cl_clientpk = ln.ln_clientpk
WHERE ln.ln_clientpk = :clientpk
  AND cl.cl_service_type = 'Pre-Payment'
  AND COALESCE(cl.cl_ci_ignore, 0) = 0
  AND COALESCE(ln.ln_ci_ignore, 0) = 0;
```

**DAX Measure:**
```dax
PrePay Savings Rate = 
VAR TotalCharged = [PrePay Total Charged]
VAR TotalSavings = [PrePay Savings]
RETURN
    IF(TotalCharged > 0,
        DIVIDE(TotalSavings, TotalCharged, 0) * 100,
        0
    )
```

**Supporting DAX Measure:**
```dax
PrePay Total Charged = 
CALCULATE(
    SUM(Claimline[ln_charged]),
    Claim[cl_service_type] = "Pre-Payment",
    Claimline[ln_ci_ignore] = 0 || ISBLANK(Claimline[ln_ci_ignore])
)
```

**Power BI Visual:** Gauge or KPI visual

---

### 10. Average Savings Per Claim

**Definition:** Average savings amount per claim.

**SQL Query:**
```sql
SELECT 
    CASE 
        WHEN COUNT(DISTINCT cl.cl_claimid) > 0 
        THEN SUM(ln.ln_savings_identified) / COUNT(DISTINCT cl.cl_claimid)
        ELSE 0 
    END
FROM claim cl
JOIN claimline ln 
    ON cl.cl_claimid = ln.ln_claimid 
    AND cl.cl_clientpk = ln.ln_clientpk
WHERE ln.ln_clientpk = :clientpk
  AND cl.cl_service_type = 'Pre-Payment'
  AND COALESCE(cl.cl_ci_ignore, 0) = 0
  AND COALESCE(ln.ln_ci_ignore, 0) = 0;
```

**DAX Measure:**
```dax
Avg Savings Per Claim = 
DIVIDE(
    [PrePay Savings],
    [PrePay Claim Count],
    0
)
```

**Supporting DAX Measure:**
```dax
PrePay Claim Count = 
CALCULATE(
    DISTINCTCOUNT(Claim[cl_claimid]),
    Claim[cl_service_type] = "Pre-Payment",
    Claim[cl_ci_ignore] = 0 || ISBLANK(Claim[cl_ci_ignore])
)
```

**Power BI Visual:** Card visual with currency formatting

---

## Post-Pay Metrics

### 11. Total Overpayments Identified

**Definition:** Sum of overpayments identified in post-payment review.

**SQL Query:**
```sql
SELECT SUM(r.recovery_amount)
FROM recovery r
JOIN claim cl ON r.cl_claimid = cl.cl_claimid
WHERE cl.cl_clientpk = :clientpk
  AND COALESCE(cl.cl_ci_ignore, 0) = 0;
```

**DAX Measure:**
```dax
Total Overpayments = 
CALCULATE(
    SUM(Recovery[recovery_amount]),
    FILTER(
        RELATEDTABLE(Claim),
        Claim[cl_ci_ignore] = 0 || ISBLANK(Claim[cl_ci_ignore])
    )
)
```

**Power BI Visual:** Card visual with currency formatting

---

### 12. Total Recovered

**Definition:** Sum of amounts actually recovered from overpayments.

**SQL Query:**
```sql
SELECT SUM(rp.payment_amount)
FROM recovery r
JOIN recovery_payment rp ON r.recovery_id = rp.recovery_id
JOIN claim cl ON r.cl_claimid = cl.cl_claimid
WHERE cl.cl_clientpk = :clientpk
  AND COALESCE(cl.cl_ci_ignore, 0) = 0;
```

**DAX Measure:**
```dax
Total Recovered = 
CALCULATE(
    SUM(Recovery_Payment[payment_amount]),
    FILTER(
        RELATEDTABLE(Recovery),
        NOT(ISBLANK(RELATED(Claim[cl_claimid])))
    ),
    FILTER(
        RELATEDTABLE(Claim),
        Claim[cl_ci_ignore] = 0 || ISBLANK(Claim[cl_ci_ignore])
    )
)
```

**Power BI Visual:** Card visual with currency formatting

---

### 13. Recovery Rate

**Definition:** Percentage of identified overpayments that were recovered.

**SQL Query:**
```sql
SELECT 
    CASE 
        WHEN SUM(r.recovery_amount) > 0 
        THEN (SUM(rp.payment_amount) / SUM(r.recovery_amount)) * 100
        ELSE 0 
    END AS recovery_rate
FROM recovery r
LEFT JOIN recovery_payment rp ON r.recovery_id = rp.recovery_id
JOIN claim cl ON r.cl_claimid = cl.cl_claimid
WHERE cl.cl_clientpk = :clientpk
  AND COALESCE(cl.cl_ci_ignore, 0) = 0;
```

**DAX Measure:**
```dax
Recovery Rate = 
VAR TotalIdentified = [Total Overpayments]
VAR TotalRecovered = [Total Recovered]
RETURN
    IF(TotalIdentified > 0,
        DIVIDE(TotalRecovered, TotalIdentified, 0) * 100,
        0
    )
```

**Power BI Visual:** Gauge or KPI visual

---

### 14. Average Days to Recovery

**Definition:** Average number of days between identification and recovery.

**SQL Query:**
```sql
SELECT AVG(DATEDIFF(rp.payment_date, r.identified_date))
FROM recovery r
JOIN recovery_payment rp ON r.recovery_id = rp.recovery_id
JOIN claim cl ON r.cl_claimid = cl.cl_claimid
WHERE cl.cl_clientpk = :clientpk
  AND rp.payment_date IS NOT NULL
  AND COALESCE(cl.cl_ci_ignore, 0) = 0;
```

**DAX Measure:**
```dax
Avg Days to Recovery = 
AVERAGEX(
    FILTER(
        Recovery_Payment,
        NOT(ISBLANK(Recovery_Payment[payment_date]))
    ),
    DATEDIFF(
        RELATED(Recovery[identified_date]),
        Recovery_Payment[payment_date],
        DAY
    )
)
```

**Power BI Visual:** Card visual

---

### 15. Outstanding Recoveries

**Definition:** Amount of identified overpayments not yet recovered.

**SQL Query:**
```sql
SELECT SUM(r.recovery_amount) - COALESCE(SUM(rp.payment_amount), 0)
FROM recovery r
LEFT JOIN recovery_payment rp ON r.recovery_id = rp.recovery_id
JOIN claim cl ON r.cl_claimid = cl.cl_claimid
WHERE cl.cl_clientpk = :clientpk
  AND COALESCE(cl.cl_ci_ignore, 0) = 0;
```

**DAX Measure:**
```dax
Outstanding Recoveries = 
[Total Overpayments] - [Total Recovered]
```

**Power BI Visual:** Card visual with currency formatting

---

## Financial Calculations

### 16. PMPM (Per Member Per Month)

**Definition:** Average cost per member per month.

**SQL Query:**
```sql
SELECT 
    SUM(ln.ln_paid) / 
    (COUNT(DISTINCT cl.cl_memid) * 
     (DATEDIFF(MAX(ln.ln_datepaid), MIN(ln.ln_datepaid)) / 30.44))
FROM claim cl
JOIN claimline ln 
    ON cl.cl_claimid = ln.ln_claimid 
    AND cl.cl_clientpk = ln.ln_clientpk
WHERE ln.ln_clientpk = :clientpk
  AND COALESCE(cl.cl_ci_ignore, 0) = 0
  AND COALESCE(ln.ln_ci_ignore, 0) = 0;
```

**DAX Measure:**
```dax
PMPM = 
VAR TotalPaid = [Total Paid]
VAR MemberCount = [Employee Count]
VAR MonthsInScope = 
    DATEDIFF([Scope Begin Date], [Scope End Date], MONTH) + 1
RETURN
    IF(MemberCount > 0 && MonthsInScope > 0,
        DIVIDE(TotalPaid, MemberCount * MonthsInScope, 0),
        0
    )
```

**Power BI Visual:** Card visual with currency formatting

---

### 17. PPPM (Per Patient Per Month)

**Definition:** Average cost per patient per month.

**SQL Query:**
```sql
SELECT 
    SUM(ln.ln_paid) / 
    (COUNT(DISTINCT cl.cl_ptid) * 
     (DATEDIFF(MAX(ln.ln_datepaid), MIN(ln.ln_datepaid)) / 30.44))
FROM claim cl
JOIN claimline ln 
    ON cl.cl_claimid = ln.ln_claimid 
    AND cl.cl_clientpk = ln.ln_clientpk
WHERE ln.ln_clientpk = :clientpk
  AND COALESCE(cl.cl_ci_ignore, 0) = 0
  AND COALESCE(ln.ln_ci_ignore, 0) = 0;
```

**DAX Measure:**
```dax
PPPM = 
VAR TotalPaid = [Total Paid]
VAR PatientCount = [Patient Count]
VAR MonthsInScope = 
    DATEDIFF([Scope Begin Date], [Scope End Date], MONTH) + 1
RETURN
    IF(PatientCount > 0 && MonthsInScope > 0,
        DIVIDE(TotalPaid, PatientCount * MonthsInScope, 0),
        0
    )
```

**Power BI Visual:** Card visual with currency formatting

---

### 18. Trend Variance (Month-over-Month)

**Definition:** Percentage change from previous month.

**DAX Measure:**
```dax
MoM Variance % = 
VAR CurrentMonth = [Total Paid]
VAR PreviousMonth = 
    CALCULATE(
        [Total Paid],
        DATEADD(Calendar[Date], -1, MONTH)
    )
RETURN
    IF(PreviousMonth > 0,
        DIVIDE(CurrentMonth - PreviousMonth, PreviousMonth, 0) * 100,
        0
    )
```

**Power BI Visual:** KPI visual with trend indicator

---

### 19. Year-over-Year Variance

**Definition:** Percentage change from same period last year.

**DAX Measure:**
```dax
YoY Variance % = 
VAR CurrentPeriod = [Total Paid]
VAR PriorYear = 
    CALCULATE(
        [Total Paid],
        SAMEPERIODLASTYEAR(Calendar[Date])
    )
RETURN
    IF(PriorYear > 0,
        DIVIDE(CurrentPeriod - PriorYear, PriorYear, 0) * 100,
        0
    )
```

**Power BI Visual:** KPI visual with trend indicator

---

### 20. Average Paid Per Claim

**Definition:** Average payment amount per claim.

**SQL Query:**
```sql
SELECT 
    CASE 
        WHEN COUNT(DISTINCT cl.cl_claimid) > 0 
        THEN SUM(ln.ln_paid) / COUNT(DISTINCT cl.cl_claimid)
        ELSE 0 
    END
FROM claim cl
JOIN claimline ln 
    ON cl.cl_claimid = ln.ln_claimid 
    AND cl.cl_clientpk = ln.ln_clientpk
WHERE ln.ln_clientpk = :clientpk
  AND COALESCE(cl.cl_ci_ignore, 0) = 0
  AND COALESCE(ln.ln_ci_ignore, 0) = 0;
```

**DAX Measure:**
```dax
Avg Paid Per Claim = 
DIVIDE(
    [Total Paid],
    [Claim Count],
    0
)
```

**Power BI Visual:** Card visual with currency formatting

---

### 21. Average Paid Per Claimline

**Definition:** Average payment amount per service line.

**SQL Query:**
```sql
SELECT 
    CASE 
        WHEN COUNT(*) > 0 
        THEN SUM(ln.ln_paid) / COUNT(*)
        ELSE 0 
    END
FROM claim cl
JOIN claimline ln 
    ON cl.cl_claimid = ln.ln_claimid 
    AND cl.cl_clientpk = ln.ln_clientpk
WHERE ln.ln_clientpk = :clientpk
  AND COALESCE(cl.cl_ci_ignore, 0) = 0
  AND COALESCE(ln.ln_ci_ignore, 0) = 0;
```

**DAX Measure:**
```dax
Avg Paid Per Claimline = 
DIVIDE(
    [Total Paid],
    [Claimline Count],
    0
)
```

**Power BI Visual:** Card visual with currency formatting

---

## Date & Time Metrics

### 22. Claims by Month

**Definition:** Monthly aggregation of claims and payments.

**SQL Query:**
```sql
SELECT 
    DATE_FORMAT(ln.ln_datepaid, '%Y-%m') AS month,
    COUNT(DISTINCT cl.cl_claimid) AS claim_count,
    SUM(ln.ln_paid) AS total_paid
FROM claim cl
JOIN claimline ln 
    ON cl.cl_claimid = ln.ln_claimid 
    AND cl.cl_clientpk = ln.ln_clientpk
WHERE ln.ln_clientpk = :clientpk
  AND COALESCE(cl.cl_ci_ignore, 0) = 0
  AND COALESCE(ln.ln_ci_ignore, 0) = 0
GROUP BY DATE_FORMAT(ln.ln_datepaid, '%Y-%m')
ORDER BY month;
```

**Power BI Visual:** Line chart or clustered column chart

---

### 23. Claims by Quarter

**Definition:** Quarterly aggregation of claims and payments.

**SQL Query:**
```sql
SELECT 
    CONCAT(YEAR(ln.ln_datepaid), '-Q', QUARTER(ln.ln_datepaid)) AS quarter,
    COUNT(DISTINCT cl.cl_claimid) AS claim_count,
    SUM(ln.ln_paid) AS total_paid
FROM claim cl
JOIN claimline ln 
    ON cl.cl_claimid = ln.ln_claimid 
    AND cl.cl_clientpk = ln.ln_clientpk
WHERE ln.ln_clientpk = :clientpk
  AND COALESCE(cl.cl_ci_ignore, 0) = 0
  AND COALESCE(ln.ln_ci_ignore, 0) = 0
GROUP BY YEAR(ln.ln_datepaid), QUARTER(ln.ln_datepaid)
ORDER BY quarter;
```

**Power BI Visual:** Bar chart or line chart

---

### 24. Days Since Last Claim

**Definition:** Number of days since the most recent claim payment.

**SQL Query:**
```sql
SELECT DATEDIFF(CURDATE(), MAX(ln.ln_datepaid))
FROM claim cl
JOIN claimline ln 
    ON cl.cl_claimid = ln.ln_claimid 
    AND cl.cl_clientpk = ln.ln_clientpk
WHERE ln.ln_clientpk = :clientpk
  AND COALESCE(cl.cl_ci_ignore, 0) = 0
  AND COALESCE(ln.ln_ci_ignore, 0) = 0;
```

**DAX Measure:**
```dax
Days Since Last Claim = 
DATEDIFF([Scope End Date], TODAY(), DAY)
```

**Power BI Visual:** Card visual

---

## DAX Formula Reference

### Date Table (Required for Time Intelligence)

```dax
Calendar = 
VAR MinDate = MIN(Claimline[ln_datepaid])
VAR MaxDate = MAX(Claimline[ln_datepaid])
RETURN
    ADDCOLUMNS(
        CALENDAR(MinDate, MaxDate),
        "Year", YEAR([Date]),
        "Month", MONTH([Date]),
        "MonthName", FORMAT([Date], "MMM"),
        "MonthNameFull", FORMAT([Date], "MMMM"),
        "Quarter", "Q" & QUARTER([Date]),
        "QuarterNum", QUARTER([Date]),
        "YearMonth", FORMAT([Date], "YYYY-MM"),
        "YearQuarter", YEAR([Date]) & "-Q" & QUARTER([Date]),
        "WeekNum", WEEKNUM([Date]),
        "DayOfWeek", WEEKDAY([Date]),
        "DayName", FORMAT([Date], "dddd"),
        "IsWeekend", IF(WEEKDAY([Date]) IN {1, 7}, TRUE, FALSE)
    )
```

### Running Totals

```dax
Running Total Paid = 
CALCULATE(
    [Total Paid],
    FILTER(
        ALL(Calendar[Date]),
        Calendar[Date] <= MAX(Calendar[Date])
    )
)
```

### Year-to-Date

```dax
YTD Total Paid = 
TOTALYTD([Total Paid], Calendar[Date])
```

### Prior Year Total

```dax
Prior Year Total Paid = 
CALCULATE(
    [Total Paid],
    SAMEPERIODLASTYEAR(Calendar[Date])
)
```

### Moving Average (3-Month)

```dax
3-Month Moving Avg = 
AVERAGEX(
    DATESINPERIOD(
        Calendar[Date],
        MAX(Calendar[Date]),
        -3,
        MONTH
    ),
    [Total Paid]
)
```

### Cumulative Count

```dax
Cumulative Claim Count = 
CALCULATE(
    [Claim Count],
    FILTER(
        ALL(Calendar[Date]),
        Calendar[Date] <= MAX(Calendar[Date])
    )
)
```

---

## Power BI Implementation Guidelines

### 1. Data Model Setup

**Required Tables:**
- Claim (fact table)
- Claimline (fact table)
- Recovery (fact table)
- Recovery_Payment (fact table)
- Calendar (dimension table)
- Client (dimension table, optional)

**Relationships:**
- `Claim[cl_claimid]` â†’ `Claimline[ln_claimid]` (1:Many)
- `Claim[cl_claimid]` â†’ `Recovery[cl_claimid]` (1:Many)
- `Recovery[recovery_id]` â†’ `Recovery_Payment[recovery_id]` (1:Many)
- `Calendar[Date]` â†’ `Claimline[ln_datepaid]` (1:Many)
- `Client[cl_clientpk]` â†’ `Claim[cl_clientpk]` (1:Many)

### 2. Visual Standards

**Color Palette:**

| Use | Color | Hex |
|-----|-------|-----|
| Primary | Purple | #77256C |
| Primary Dark | Dark Purple | #5a1d52 |
| Primary Light | Light Purple | #945F8D |
| Accent | Gold | #FBB75E |
| Success | Green | #28B296 |
| Warning | Orange | #FAAF4C |
| Danger | Red | #EC4273 |
| Info | Blue | #439BCB |
| Dark Text | Charcoal | #323232 |
| Gray | Gray | #9F9F9F |

**Font:** Segoe UI (Power BI default) or Inter

### 3. Report Page Layout

**Standard Page Structure:**

1. **Header Row:** Logo, Title, Date Slicer
2. **KPI Row:** 4-5 Card visuals with key metrics
3. **Chart Row:** 2 column charts/line charts
4. **Detail Row:** Table or Matrix visual

**Recommended Page Types:**

- **Overview Dashboard:** High-level KPIs and trends
- **Pre-Pay Analysis:** Pre-payment review metrics
- **Post-Pay Analysis:** Recovery and overpayment metrics
- **Trend Analysis:** Time-series comparisons
- **Detail/Drill-through:** Granular claim data

### 4. Performance Optimization

- Use DirectQuery only when necessary
- Implement aggregations for large datasets
- Limit visuals per page to 8-10
- Use measures instead of calculated columns
- Enable query reduction settings
- Use bookmarks for filtering instead of multiple slicers
- Avoid bidirectional relationships unless necessary

### 5. Deployment Checklist

- [ ] All measures using standard ignore flag logic
- [ ] Date table properly connected and marked as date table
- [ ] Row-level security configured for multi-tenant
- [ ] Color theme applied (ClaimInformatics brand)
- [ ] Bookmarks set up for navigation
- [ ] Tooltips configured for detailed views
- [ ] Mobile layout created
- [ ] Refresh schedule configured
- [ ] Data sensitivity labels applied
- [ ] Report documentation completed

---

## Appendix: Field Reference

### Ignore Flag Logic (Standard Pattern)

All calculations must exclude ignored records:

**SQL Pattern:**
```sql
AND COALESCE(cl.cl_ci_ignore, 0) = 0
AND COALESCE(ln.ln_ci_ignore, 0) = 0
```

**DAX Pattern:**
```dax
Claim[cl_ci_ignore] = 0 || ISBLANK(Claim[cl_ci_ignore])
Claimline[ln_ci_ignore] = 0 || ISBLANK(Claimline[ln_ci_ignore])
```

### Client Filtering

All queries support multi-tenant via `cl_clientpk`:

**SQL Pattern:**
```sql
WHERE cl.cl_clientpk = :clientpk
```

**DAX Pattern:**
```dax
FILTER(Claim, Claim[cl_clientpk] = SELECTEDVALUE(Client[ClientPK]))
```

### Key Field Mappings

| Entity | Primary Key | Foreign Keys |
|--------|-------------|--------------|
| Claim | cl_claimid | cl_clientpk, cl_memid, cl_ptid |
| Claimline | ln_lineid | ln_claimid, ln_clientpk |
| Recovery | recovery_id | cl_claimid |
| Recovery_Payment | payment_id | recovery_id |

### Common Field Prefixes

| Prefix | Table | Description |
|--------|-------|-------------|
| cl_ | Claim | Claim-level fields |
| ln_ | Claimline | Line-level fields |
| ee_ | Claim | Employee/Member fields |
| pt_ | Claim | Patient fields |
| prv_ | Claim/Claimline | Provider fields |

---

## Field Profiler & Data Completeness Metrics

**Portal:** Field Profiler & Data Completeness Explorer v1.1  
**Source:** Field_Profiler_Portal_v1_1.html  
**Data Source:** Staging extract (Thrasher_Custom_Extract_v3.xlsx — 37,169 rows × 93 columns)

---

### FP-1. Field Completeness Percentage (Per Column)

**Definition:** Percentage of non-null, non-empty values for a single column across all claimlines.

**SQL Query:**
```sql
SELECT
    'column_name' AS field_name,
    COUNT(*) AS total_rows,
    COUNT(column_name) AS filled_count,
    SUM(CASE WHEN column_name IS NULL
        OR TRIM(column_name::text) = ''
        THEN 1 ELSE 0 END) AS null_count,
    COUNT(DISTINCT column_name) AS distinct_count,
    ROUND(
        SUM(CASE WHEN column_name IS NULL
            OR TRIM(column_name::text) = ''
            THEN 1 ELSE 0 END)::numeric
        / COUNT(*)::numeric, 4
    ) AS pct_empty,
    ROUND(
        COUNT(column_name)::numeric
        / COUNT(*)::numeric, 4
    ) AS pct_filled
FROM claim cl
JOIN claimline ln ON cl.cl_claimid = ln.ln_claimid
    AND cl.cl_clientpk = ln.ln_clientpk
WHERE cl.cl_clientpk = :clientpk
    AND COALESCE(cl.cl_ci_ignore, 0) = 0
    AND COALESCE(ln.ln_ci_ignore, 0) = 0;
```

**DAX Measure:**
```dax
Field Completeness % = 
DIVIDE(
    COUNTROWS(
        FILTER(Data,
            NOT(ISBLANK(Data[SelectedColumn]))
            && (Data[cl_ci_ignore] = 0
                || ISBLANK(Data[cl_ci_ignore]))
        )
    ),
    COUNTROWS(
        FILTER(Data,
            Data[cl_ci_ignore] = 0
            || ISBLANK(Data[cl_ci_ignore])
        )
    ),
    0
)
```

**Power BI Visual:** Data bar in matrix visual with conditional formatting:
- ≥90%: #28B296 (success green)
- 50–90%: #FAAF4C (warning gold)
- <50%: #EC4273 (danger red)

---

### FP-2. Top Value Distribution (Per Column)

**Definition:** Top 30 most frequent values with frequency counts and percentage of total rows.

**SQL Query:**
```sql
SELECT column_name AS value,
    COUNT(*) AS frequency,
    ROUND(COUNT(*)::numeric /
        (SELECT COUNT(*) FROM claim cl
         JOIN claimline ln ON cl.cl_claimid = ln.ln_claimid
             AND cl.cl_clientpk = ln.ln_clientpk
         WHERE cl.cl_clientpk = :clientpk
             AND COALESCE(cl.cl_ci_ignore, 0) = 0
             AND COALESCE(ln.ln_ci_ignore, 0) = 0
        )::numeric, 4) AS pct_of_total
FROM claim cl
JOIN claimline ln ON cl.cl_claimid = ln.ln_claimid
    AND cl.cl_clientpk = ln.ln_clientpk
WHERE cl.cl_clientpk = :clientpk
    AND COALESCE(cl.cl_ci_ignore, 0) = 0
    AND COALESCE(ln.ln_ci_ignore, 0) = 0
    AND column_name IS NOT NULL
    AND TRIM(column_name::text) <> ''
GROUP BY 1
ORDER BY 2 DESC
LIMIT 30;
```

**DAX Measure:**
```dax
Value Frequency = 
CALCULATE(
    COUNTROWS(Data),
    Data[cl_ci_ignore] = 0 || ISBLANK(Data[cl_ci_ignore])
)
-- Used in matrix visual grouped by column value
```

**Power BI Visual:** Horizontal bar chart (top 30 values) in detail flyout / drillthrough page. Bars colored with `#945F8D` (primary light).

---

### FP-3. Distinct Value Count

**Definition:** Count of unique non-null values in a column.

**SQL Query:**
```sql
SELECT COUNT(DISTINCT column_name) AS distinct_count
FROM claim cl
JOIN claimline ln ON cl.cl_claimid = ln.ln_claimid
    AND cl.cl_clientpk = ln.ln_clientpk
WHERE cl.cl_clientpk = :clientpk
    AND COALESCE(cl.cl_ci_ignore, 0) = 0
    AND COALESCE(ln.ln_ci_ignore, 0) = 0
    AND column_name IS NOT NULL
    AND TRIM(column_name::text) <> '';
```

**DAX Measure:**
```dax
Distinct Value Count = 
CALCULATE(
    DISTINCTCOUNT(Data[SelectedColumn]),
    Data[cl_ci_ignore] = 0 || ISBLANK(Data[cl_ci_ignore])
)
```

**Power BI Visual:** Numeric column in matrix visual, styled with `#439BCB` (info blue) font color.

---

### FP-4. Cardinality Ratio

**Definition:** Distinct values / filled count. High cardinality (>50%) indicates unique identifiers; low (<1%) indicates categorical/lookup fields.

**SQL Query:**
```sql
SELECT
    COUNT(DISTINCT column_name)::numeric /
    NULLIF(COUNT(column_name), 0)::numeric AS cardinality_ratio
FROM claim cl
JOIN claimline ln ON cl.cl_claimid = ln.ln_claimid
    AND cl.cl_clientpk = ln.ln_clientpk
WHERE cl.cl_clientpk = :clientpk
    AND COALESCE(cl.cl_ci_ignore, 0) = 0
    AND COALESCE(ln.ln_ci_ignore, 0) = 0
    AND column_name IS NOT NULL
    AND TRIM(column_name::text) <> '';
```

**DAX Measure:**
```dax
Cardinality Ratio = 
DIVIDE(
    DISTINCTCOUNT(Data[SelectedColumn]),
    COUNTROWS(
        FILTER(Data,
            NOT(ISBLANK(Data[SelectedColumn]))
        )
    ),
    0
)
```

**Power BI Visual:** Percentage in Unique Values table. Conditional formatting:
- >50%: #28B296 (high cardinality — identifiers)
- 1–50%: #FAAF4C (medium — semi-unique)
- <1%: #6b6185 (low — categorical/lookup)

---

### FP-5. Weighted Overall Completeness

**Definition:** Total filled cells divided by total possible cells across all profiled columns. This is the true weighted average (not simple mean of per-column percentages).

**Formula:** `SUM(filled_count for all columns) / SUM(total_rows × column_count)`

**SQL Query:**
```sql
WITH field_stats AS (
    SELECT
        'cl_claimid' AS field_name,
        COUNT(*) AS total_rows,
        COUNT(cl.cl_claimid) AS filled_count
    FROM claim cl
    JOIN claimline ln ON cl.cl_claimid = ln.ln_claimid
        AND cl.cl_clientpk = ln.ln_clientpk
    WHERE cl.cl_clientpk = :clientpk
        AND COALESCE(cl.cl_ci_ignore, 0) = 0
        AND COALESCE(ln.ln_ci_ignore, 0) = 0
    UNION ALL
    SELECT 'ln_linenum', COUNT(*), COUNT(ln.ln_linenum)
    FROM claim cl
    JOIN claimline ln ON cl.cl_claimid = ln.ln_claimid
        AND cl.cl_clientpk = ln.ln_clientpk
    WHERE cl.cl_clientpk = :clientpk
        AND COALESCE(cl.cl_ci_ignore, 0) = 0
        AND COALESCE(ln.ln_ci_ignore, 0) = 0
    -- ... Repeat UNION ALL for each of the 93 columns
)
SELECT
    SUM(filled_count) AS total_filled_cells,
    SUM(total_rows) AS total_possible_cells,
    ROUND(SUM(filled_count)::numeric /
        NULLIF(SUM(total_rows), 0)::numeric, 4
    ) AS weighted_completeness
FROM field_stats;
```

**DAX Measure:**
```dax
Weighted Completeness = 
VAR TotalCells = COUNTROWS(Data) * [Column Count]
VAR FilledCells =
    SUMX(
        FieldMetadata,
        CALCULATE(
            COUNTROWS(
                FILTER(Data,
                    NOT(ISBLANK(Data[CurrentField])))
            )
        )
    )
RETURN DIVIDE(FilledCells, TotalCells, 0)
```

**Power BI Visual:** Hero card visual with gradient background `#77256C → #945F8D`. Display as percentage with 1 decimal. Subtitle shows filled/total cell counts.

**Note:** Simple average (sum of pctFilled / column count) may differ from weighted average when columns have different row counts. The portal uses true weighted calculation: `totalFilledCells / totalPossibleCells`.

---

### FP-6. Category Completeness Summary

**Definition:** Average completeness across all fields within a functional category. The portal groups 93 columns into 15 categories.

**Categories:**
| # | Category | Fields | Expected Fill Pattern |
|---|----------|--------|----------------------|
| 1 | Claim Identification | 5 | ≥99% — required on all claims |
| 2 | Service Details | 7 | Split: Professional (~71%) / Facility (~29%) |
| 3 | Procedure Codes | 5 | CPT Prof ~71%, Revenue ~29%, DRG ~3% |
| 4 | Modifiers & Units | 7 | Mod1 ~26%, Mod4 0% — expected decay |
| 5 | Diagnosis Codes | 10 | Dx1 99.8% → Dx10 4.2% — exponential decay |
| 6 | Financial | 9 | ≥99% — core financial fields always populated |
| 7 | Payment Details | 3 | Check# ~57% (EFT remainder) |
| 8 | Admission / Discharge | 7 | ~23% — facility claims only |
| 9 | Provider - Rendering | 10 | 0–100% — Tax ID empty, NPI ~59% |
| 10 | Provider - Billing | 8 | ≥92% — billing provider usually complete |
| 11 | Network | 2 | ≥99% — plan assignment data |
| 12 | Member / Patient | 9 | ≥99% — required member demographics |
| 13 | Enrollment | 3 | ≥99% — coverage dates |
| 14 | Address - Subscriber | 4 | ≥99% — subscriber demographics |
| 15 | Address - Patient | 4 | ≥99% — patient demographics |

**SQL Query:**
```sql
WITH category_fields AS (
    SELECT 'Claim Identification' AS category,
        ARRAY['cl_claimid','ln_linenum','cl_claimstatus',
              'cl_claimtype','cl_ptacctno'] AS fields
    UNION ALL
    SELECT 'Financial',
        ARRAY['ln_charged','ln_allowed','ln_paid',
              'ln_deductible','ln_copay','ln_coinsurance',
              'ln_notcovered','ln_notcovered_reason','ln_cobsavings']
    UNION ALL
    SELECT 'Diagnosis Codes',
        ARRAY['cl_diag1','cl_diag2','cl_diag3','cl_diag4',
              'cl_diag5','cl_diag6','cl_diag7','cl_diag8',
              'cl_diag9','cl_diag10']
    -- ... additional categories
)
SELECT category,
    AVG(pct_filled) AS avg_completeness,
    COUNT(*) AS field_count
FROM category_fields cf
CROSS JOIN LATERAL unnest(cf.fields) AS f(field_name)
JOIN field_completeness_stats fs
    ON fs.field_name = f.field_name
GROUP BY 1
ORDER BY 2 DESC;
```

**DAX Measure:**
```dax
Category Completeness = 
AVERAGEX(
    FILTER(
        FieldMetadata,
        FieldMetadata[Category] =
            SELECTEDVALUE(Categories[CategoryName])
    ),
    [Field Completeness %]
)
```

**Power BI Visual:** Matrix visual grouped by category with sparkline data bars. Color-coded category headers using conditional formatting thresholds.

---

### FP-7. Completeness Classification Band

**Definition:** Categorizes each field's completeness into actionable bands for filtering and dashboard display.

**Thresholds:**
| Band | Range | Color | Count (Thrasher Extract) |
|------|-------|-------|--------------------------|
| Complete | ≥99% | #28B296 | 56 fields |
| Partial | 50–99% | #FAAF4C | 10 fields |
| Sparse | >0% and <50% | #EC4273 | 25 fields |
| Empty | 0% | #EC4273 (dark) | 2 fields |

**DAX Measure:**
```dax
Completeness Band = 
SWITCH(TRUE(),
    [Field Completeness %] >= 0.99, "Complete",
    [Field Completeness %] >= 0.50, "Partial",
    [Field Completeness %] > 0, "Sparse",
    "Empty"
)
```

**Power BI Visual:** Filter chips / slicer with color-coded buttons. Also used as row conditional formatting in all field tables.

---

### FP-8. Null/Empty Count

**Definition:** Count of rows where a column value is NULL or empty string.

**SQL Query:**
```sql
SELECT SUM(CASE 
    WHEN column_name IS NULL 
        OR TRIM(column_name::text) = '' 
    THEN 1 ELSE 0 END) AS null_count
FROM claim cl
JOIN claimline ln ON cl.cl_claimid = ln.ln_claimid
    AND cl.cl_clientpk = ln.ln_clientpk
WHERE cl.cl_clientpk = :clientpk
    AND COALESCE(cl.cl_ci_ignore, 0) = 0
    AND COALESCE(ln.ln_ci_ignore, 0) = 0;
```

**DAX Measure:**
```dax
Null Count = 
CALCULATE(
    COUNTROWS(
        FILTER(Data, ISBLANK(Data[SelectedColumn]))
    ),
    Data[cl_ci_ignore] = 0 || ISBLANK(Data[cl_ci_ignore])
)
```

**Power BI Visual:** Numeric column in table. Conditional formatting: 0 = #28B296 (green), >0 = #EC4273 (red).

---

### Field Profiler — Complete Field-to-Database Mapping

All 93 columns with CI database field names, source tables, and EDI transaction references:

**Claim Identification:**
| Extract Column | DB Field | Table | EDI Source |
|---------------|----------|-------|------------|
| Claim Number | cl_claimid | claim | 837/835 |
| Claim Line Number | ln_linenum | claimline | 837 LX01 |
| Claim Status Code | cl_claimstatus | claim | 835 CLP02 |
| Claim Type | cl_claimtype | claim | 835 CLP06 |
| Patient Control/Patient Account Number | cl_ptacctno | claim | 837 CLM01 |

**Service Details:**
| Extract Column | DB Field | Table | EDI Source |
|---------------|----------|-------|------------|
| Place of Service | ln_pos | claimline | 837 SV105 |
| From Date of Service (Professional) | ln_dateserv | claimline | 837 DTP (472) |
| To Date of Service (Professional) | ln_dateserv_to | claimline | 837 DTP (472) |
| Statement Covers Period: From (UB04) | cl_dateadmit | claim | 837I DTP (096) |
| Statement Covers Period: Through (UB04) | cl_datedisch | claim | 837I DTP (097) |
| Type of Service | ln_tos | claimline | 837 SV101-1 |
| Type of Bill | cl_typeofbill | claim | 837I CLM05-1 |

**Procedure Codes:**
| Extract Column | DB Field | Table | EDI Source |
|---------------|----------|-------|------------|
| CPT / HCPCS Code (Professional) | ln_proc | claimline | 837P SV101-2 |
| Revenue Code | ln_revcode | claimline | 837I SV201 |
| CPT / HCPCS / HIPPS Code (Facility) | ln_proc_fac | claimline | 837I SV202 |
| DRG Code | cl_drg | claim | 837I HI (DRG) |
| NDC Number | ln_ndc | claimline | 837 LIN |

**Modifiers & Units:**
| Extract Column | DB Field | Table | EDI Source |
|---------------|----------|-------|------------|
| Units | ln_units | claimline | 837 SV104 |
| Modifier 1 | ln_mod1 | claimline | 837 SV101-3 |
| Modifier 2 | ln_mod2 | claimline | 837 SV101-4 |
| Modifier 3 | ln_mod3 | claimline | 837 SV101-5 |
| Modifier 4 | ln_mod4 | claimline | 837 SV101-6 |
| Anesthesia Minutes | ln_anesthmin | claimline | 837 SV104 |
| Quantity | ln_qty | claimline | 835 SVC |

**Diagnosis Codes (cl_diag1 through cl_diag10):**
| Extract Column | DB Field | Table | EDI Source |
|---------------|----------|-------|------------|
| Diagnosis 1 | cl_diag1 | claim | 837 HI (ABK/ABF) |
| Diagnosis 2–10 | cl_diag2–cl_diag10 | claim | 837 HI |

**Financial:**
| Extract Column | DB Field | Table | EDI Source |
|---------------|----------|-------|------------|
| Billed / Charged Amount | ln_charged | claimline | 837 SV102 / 835 SVC02 |
| Allowed Amount | ln_allowed | claimline | 835 SVC03 |
| Paid Amount | ln_paid | claimline | 835 SVC03 |
| Deductible Amount | ln_deductible | claimline | 835 CAS (1) |
| Copay Amount | ln_copay | claimline | 835 CAS (2) |
| Coinsurance Amount | ln_coinsurance | claimline | 835 CAS (3) |
| Not Covered Amount | ln_notcovered | claimline | 835 CAS |
| Not Covered Reason Code | ln_notcovered_reason | claimline | 835 CAS |
| COB Savings | ln_cobsavings | claimline | 835 |

**Payment Details:**
| Extract Column | DB Field | Table | EDI Source |
|---------------|----------|-------|------------|
| Payee | cl_payee | claim | 835 N1 (PE) |
| Claim Paid Date | ln_datepaid | claimline | 835 DTM (405) |
| Check Number | cl_checkno | claim | 835 TRN02 |

**Provider — Rendering:**
| Extract Column | DB Field | Table | EDI Source |
|---------------|----------|-------|------------|
| Service Provider Federal Tax ID | prv_taxid | claim | 837 REF (EI) |
| Service/Rendering Provider NPI | prv_npi | claimline | 837 NM109 (82) |
| Rendering Provider (Group) Name | prv_grpname | claim | 837 NM103 (77) |
| Rendering Provider Name | prv_name | claim | 837 NM103 (82) |
| Rendering Provider Address | prv_addr1 | claim | 837 N3 (82) |
| Rendering Provider Address 2 | prv_addr2 | claim | 837 N3 (82) |
| Rendering Provider City | prv_city | claim | 837 N4 (82) |
| Rendering Provider State | prv_state | claim | 837 N4 (82) |
| Rendering Provider Zip | prv_zip | claim | 837 N4 (82) |
| Taxonomy Code | prv_taxonomy | claim | 837 PRV03 |

**Provider — Billing:**
| Extract Column | DB Field | Table | EDI Source |
|---------------|----------|-------|------------|
| Billing Provider TAX ID | cl_billtaxid | claim | 837 REF (EI) (85) |
| Billing Provider NPI | cl_billnpi | claim | 837 NM109 (85) |
| Billing Provider Name | cl_billname | claim | 837 NM103 (85) |
| Billing Provider Address | cl_billaddr1 | claim | 837 N3 (85) |
| Billing Provider Address 2 | cl_billaddr2 | claim | 837 N3 (85) |
| Billing Provider City | cl_billcity | claim | 837 N4 (85) |
| Billing Provider State | cl_billstate | claim | 837 N4 (85) |
| Billing Provider Zip | cl_billzip | claim | 837 N4 (85) |

**Network:**
| Extract Column | DB Field | Table | EDI Source |
|---------------|----------|-------|------------|
| Network Name | cl_networkname | claim | Payer/TPA |
| Network Status | cl_networkstatus | claim | Payer/TPA |

**Member / Patient:**
| Extract Column | DB Field | Table | EDI Source |
|---------------|----------|-------|------------|
| Employee/Subscriber ID/SSN | cl_memid | claim | 837 NM109 (IL) |
| Subscriber First Name | cl_eefn | claim | 837 NM104 (IL) |
| Subscriber Last Name | cl_eeln | claim | 837 NM103 (IL) |
| Patient First Name | cl_ptfn | claim | 837 NM104 (QC) |
| Patient Last Name | cl_ptln | claim | 837 NM103 (QC) |
| Patient DOB | cl_ptdob | claim | 837 DMG02 (QC) |
| Patient Gender | cl_ptgender | claim | 837 DMG03 (QC) |
| Patient/Dependent Number | cl_depno | claim | Payer/TPA |
| Patient Relationship Code | cl_ptrelcode | claim | 837 SBR02 |

**Enrollment:**
| Extract Column | DB Field | Table | EDI Source |
|---------------|----------|-------|------------|
| Group Number | cl_groupno | claim | 837 SBR03 |
| Coverage Effective Date | cl_coveffdt | claim | 834 DTP (348) |
| Coverage Termination Date | cl_covtermdt | claim | 834 DTP (349) |

**Address — Subscriber:**
| Extract Column | DB Field | Table | EDI Source |
|---------------|----------|-------|------------|
| Subscriber Address | cl_eeaddr1 | claim | 837 N3 (IL) |
| Subscriber City | cl_eecity | claim | 837 N4 (IL) |
| Subscriber State | cl_eestate | claim | 837 N4 (IL) |
| Subscriber Zip Code | cl_eezip | claim | 837 N4 (IL) |

**Address — Patient:**
| Extract Column | DB Field | Table | EDI Source |
|---------------|----------|-------|------------|
| Patient Address | cl_ptaddr1 | claim | 837 N3 (QC) |
| Patient City | cl_ptcity | claim | 837 N4 (QC) |
| Patient State | cl_ptstate | claim | 837 N4 (QC) |
| Patient Zip Code | cl_ptzip | claim | 837 N4 (QC) |

---

### Pre & Post Mapping Validation — Power BI Implementation

**Report Pages (7):**
1. **Pre-Mapping Validation** — Source data quality checks, completeness/type/cardinality rules, pass/warn/fail badges
2. **Post-Mapping Validation** — Source→CI field mapping verification, type compatibility, EDI source tracing
3. **Field Emptiness** — Matrix with conditional data bars, sortable columns, drillthrough to detail
4. **Unique Values** — Matrix with cardinality, top value, click-through to value distribution
5. **Overview** — Hero card (Weighted Completeness), Top 30 Emptiest horizontal bar, Data Type doughnut, KPI row
6. **By Category** — Grouped matrix or small multiples, category-level KPIs
7. **Field Detail** (drillthrough) — Full stats, top 30 horizontal bars, completeness gauge

**Color Theme JSON:**
```json
{
  "name": "ClaimInformatics Pre & Post Mapping Validation",
  "dataColors": [
    "#77256C", "#FBB75E", "#28B296",
    "#439BCB", "#EC4273", "#945F8D"
  ],
  "background": "#eef0f4",
  "foreground": "#1a1a2e",
  "tableAccent": "#77256C"
}
```

**Conditional Formatting Rules:**
| Element | Thresholds | Format Type |
|---------|------------|-------------|
| Completeness Bar | ≥90%: #28B296, 50–90%: #FAAF4C, <50%: #EC4273 | Data bar with gradient |
| % Empty Text | ≥50%: #EC4273, 10–50%: #FAAF4C, <10%: #28B296 | Font color rule |
| Null Count | >0: #EC4273, 0: #28B296 | Font color rule |
| Cardinality | >50%: #28B296, 1–50%: #FAAF4C, <1%: #6b6185 | Font color rule |
| Type Badge | Text: #77256C, Numeric: #28B296, Date: #439BCB, Mixed: #FAAF4C, Unknown: #9F9F9F | Background color |

---

## Quick Reference Tables

### Core Metrics Summary

| # | Metric | SQL Function | DAX Function |
|---|--------|--------------|--------------|
| 1 | Employees | COUNT(DISTINCT cl_memid) | DISTINCTCOUNT(Claim[cl_memid]) |
| 2 | Patients | COUNT(DISTINCT cl_ptid) | DISTINCTCOUNT(Claim[cl_ptid]) |
| 3 | Claims | COUNT(DISTINCT cl_claimid) | DISTINCTCOUNT(Claim[cl_claimid]) |
| 4 | Claimlines | COUNT(*) | COUNTROWS(Claimline) |
| 5 | Total Paid | SUM(ln_paid) | SUM(Claimline[ln_paid]) |
| 6 | Scope Begin | MIN(ln_datepaid) | MIN(Claimline[ln_datepaid]) |
| 7 | Scope End | MAX(ln_datepaid) | MAX(Claimline[ln_datepaid]) |

### Field Profiler & Mapping Validation Metrics Summary

| # | Metric | SQL Function | DAX Function |
|---|--------|--------------|--------------|
| FP-1 | Field Completeness % | COUNT(col) / COUNT(*) | DIVIDE(COUNTROWS(FILTER(NOT ISBLANK)), COUNTROWS) |
| FP-2 | Top Values | GROUP BY col ORDER BY COUNT DESC LIMIT 30 | Matrix grouped by value |
| FP-3 | Distinct Count | COUNT(DISTINCT col) | DISTINCTCOUNT(Data[col]) |
| FP-4 | Cardinality Ratio | DISTINCT / FILLED | DIVIDE(DISTINCTCOUNT, COUNTROWS(NOT ISBLANK)) |
| FP-5 | Weighted Completeness | SUM(filled) / SUM(total) | SUMX(fields, filled) / total cells |
| FP-6 | Category Completeness | AVG(pct_filled) GROUP BY category | AVERAGEX(FILTER(category), %) |
| FP-7 | Completeness Band | CASE ≥99/≥50/>0/=0 | SWITCH(TRUE(), thresholds) |
| FP-8 | Null Count | SUM(CASE NULL/EMPTY THEN 1) | COUNTROWS(FILTER(ISBLANK)) |

### Standard Filters (Always Apply)

```sql
-- SQL
WHERE cl.cl_clientpk = :clientpk
  AND COALESCE(cl.cl_ci_ignore, 0) = 0
  AND COALESCE(ln.ln_ci_ignore, 0) = 0
```

```dax
-- DAX
CALCULATE(
    [Measure],
    Claim[cl_ci_ignore] = 0 || ISBLANK(Claim[cl_ci_ignore]),
    Claimline[ln_ci_ignore] = 0 || ISBLANK(Claimline[ln_ci_ignore])
)
```

---

**Document Control:**
- Created: December 2025
- Last Modified: February 2026
- Version: 3.2 — Added Pre & Post Mapping Validation metrics (MV-1 through MV-10)
- Owner: ClaimInformatics Development Team
- Review Cycle: Quarterly
- Change Log:
  - v3.0 (Dec 2025): Consolidated CI_Calculations.docx + v2.md
  - v3.1 (Feb 2026): Added Section 8 — Field Profiler metrics, 93-column field mapping, Power BI implementation
  - v3.2 (Mar 2026): Added Section 10 — Pre & Post Mapping Validation metrics; renamed portal; dark mode removed; performance refactor

---

## Pre & Post Mapping Validation Metrics

> Added in v3.2 (March 2026) for the renamed Pre & Post Mapping Validation Portal v2.0.

### MV-1. Mapping Coverage Rate

**Definition:** Percentage of source extract columns that have a defined CI database field mapping.

**SQL Query:**
```sql
SELECT 
    COUNT(CASE WHEN fm.ci_db_field IS NOT NULL THEN 1 END) AS mapped_columns,
    COUNT(*) AS total_columns,
    ROUND(
        COUNT(CASE WHEN fm.ci_db_field IS NOT NULL THEN 1 END) * 100.0 / COUNT(*), 1
    ) AS mapping_coverage_pct
FROM extract_column_profile ecp
LEFT JOIN field_mapping fm ON fm.source_column = ecp.column_name
WHERE ecp.extract_id = :extractId
  AND ecp.client_pk = :clientpk;
```

**DAX Measure:**
```dax
Mapping Coverage % = 
VAR MappedCount = COUNTROWS(FILTER(FieldMapping, NOT ISBLANK(FieldMapping[ci_db_field])))
VAR TotalCount = COUNTROWS(ExtractProfile)
RETURN DIVIDE(MappedCount, TotalCount, 0)
```

**Thresholds:** ≥95% = Pass, 80–95% = Warning, <80% = Fail

---

### MV-2. Required Field Readiness

**Definition:** Percentage of required CI fields whose source column has ≥95% population rate.

**SQL Query:**
```sql
SELECT
    COUNT(CASE WHEN ecp.pct_filled >= 0.95 THEN 1 END) AS ready_count,
    COUNT(*) AS required_count,
    ROUND(
        COUNT(CASE WHEN ecp.pct_filled >= 0.95 THEN 1 END) * 100.0 / COUNT(*), 1
    ) AS required_readiness_pct
FROM field_mapping fm
JOIN extract_column_profile ecp ON ecp.column_name = fm.source_column
WHERE fm.is_required = 1
  AND ecp.extract_id = :extractId
  AND ecp.client_pk = :clientpk;
```

**DAX Measure:**
```dax
Required Field Readiness % = 
VAR RequiredFields = FILTER(FieldMapping, FieldMapping[is_required] = TRUE())
VAR ReadyFields = FILTER(RequiredFields, 
    RELATED(ExtractProfile[pct_filled]) >= 0.95)
RETURN DIVIDE(COUNTROWS(ReadyFields), COUNTROWS(RequiredFields), 0)
```

**Thresholds:** 100% = Pass, 80–99% = Warning, <80% = Fail

---

### MV-3. Data Type Compatibility Score

**Definition:** Percentage of mapped fields where the source data type exactly matches the expected CI target type.

**SQL Query:**
```sql
SELECT
    COUNT(CASE WHEN ecp.detected_type = fm.expected_type THEN 1 END) AS exact_match,
    COUNT(CASE WHEN ecp.detected_type LIKE '%/%' OR ecp.detected_type = 'Unknown' THEN 1 END) AS ambiguous,
    COUNT(CASE WHEN ecp.detected_type <> fm.expected_type 
               AND ecp.detected_type NOT LIKE '%/%' 
               AND ecp.detected_type <> 'Unknown' THEN 1 END) AS mismatch,
    COUNT(*) AS total_mapped,
    ROUND(
        COUNT(CASE WHEN ecp.detected_type = fm.expected_type THEN 1 END) * 100.0 / COUNT(*), 1
    ) AS type_match_pct
FROM field_mapping fm
JOIN extract_column_profile ecp ON ecp.column_name = fm.source_column
WHERE ecp.extract_id = :extractId
  AND ecp.client_pk = :clientpk;
```

**DAX Measure:**
```dax
Type Match % = 
VAR Mapped = FILTER(FieldMapping, NOT ISBLANK(FieldMapping[ci_db_field]))
VAR Exact = FILTER(Mapped, 
    RELATED(ExtractProfile[detected_type]) = FieldMapping[expected_type])
RETURN DIVIDE(COUNTROWS(Exact), COUNTROWS(Mapped), 0)
```

**Classification:**
- **Exact:** Source type = expected type (e.g., `Numeric = Numeric`)
- **Ambiguous:** Source type is mixed (e.g., `Numeric/Text`) or `Unknown`
- **Mismatch:** Source type conflicts (e.g., source `Text` vs expected `Numeric`)

---

### MV-4. Pre-Mapping Validation Status (Per-Field)

**Definition:** Composite validation status for each source field before mapping, combining completeness, type consistency, cardinality, and mapping status.

**Rules Engine:**
| Check | Pass | Warning | Fail |
|-------|------|---------|------|
| Completeness (required) | ≥95% filled | 50–95% filled | <50% or required <95% |
| Completeness (optional) | ≥99% filled | 50–99% filled | <50% filled |
| Type Match | Exact match | Mixed/Unknown source type | Type mismatch |
| Cardinality | >1 distinct value | — | 1 distinct value (constant) |
| Mapping | CI mapping defined | — | No mapping defined |

**Composite Status:** `FAIL` if any check = FAIL; `WARN` if any check = WARN; else `PASS`.

**SQL Query (per field):**
```sql
SELECT
    ecp.column_name,
    ecp.pct_filled,
    ecp.detected_type,
    ecp.distinct_count,
    ecp.filled_count,
    fm.ci_db_field,
    fm.expected_type,
    fm.is_required,
    CASE
        WHEN fm.is_required = 1 AND ecp.pct_filled < 0.95 THEN 'FAIL'
        WHEN ecp.pct_filled = 0 THEN 'FAIL'
        WHEN ecp.detected_type <> fm.expected_type 
             AND ecp.detected_type NOT LIKE '%/%' THEN 'FAIL'
        WHEN ecp.pct_filled < 0.50 THEN 'WARN'
        WHEN ecp.detected_type LIKE '%/%' OR ecp.detected_type = 'Unknown' THEN 'WARN'
        WHEN ecp.distinct_count = 1 AND ecp.filled_count > 0 THEN 'WARN'
        WHEN fm.ci_db_field IS NULL THEN 'WARN'
        ELSE 'PASS'
    END AS validation_status
FROM extract_column_profile ecp
LEFT JOIN field_mapping fm ON fm.source_column = ecp.column_name
WHERE ecp.extract_id = :extractId
  AND ecp.client_pk = :clientpk
ORDER BY 
    CASE WHEN fm.is_required = 1 AND ecp.pct_filled < 0.95 THEN 0
         WHEN ecp.pct_filled = 0 THEN 1
         ELSE 2 END,
    ecp.pct_filled ASC;
```

**DAX Measure:**
```dax
Pre-Mapping Status = 
VAR PctFilled = ExtractProfile[pct_filled]
VAR IsRequired = RELATED(FieldMapping[is_required])
VAR SrcType = ExtractProfile[detected_type]
VAR ExpType = RELATED(FieldMapping[expected_type])
VAR DistinctCt = ExtractProfile[distinct_count]
RETURN SWITCH(TRUE(),
    IsRequired && PctFilled < 0.95, "FAIL",
    PctFilled = 0, "FAIL",
    SrcType <> ExpType && NOT CONTAINSSTRING(SrcType, "/"), "FAIL",
    PctFilled < 0.50, "WARN",
    CONTAINSSTRING(SrcType, "/") || SrcType = "Unknown", "WARN",
    DistinctCt = 1, "WARN",
    ISBLANK(ExpType), "WARN",
    "PASS"
)
```

---

### MV-5. Post-Mapping Field Validation (Per-Field)

**Definition:** Verification that each mapped source column correctly targets a CI database field, with type compatibility and population status.

**SQL Query:**
```sql
SELECT
    fm.source_column,
    fm.ci_db_field,
    fm.ci_db_field_2,
    fm.target_table,
    fm.target_table_2,
    fm.edi_source,
    fm.expected_type,
    fm.is_required,
    fm.field_description,
    ecp.detected_type AS source_type,
    ecp.pct_filled,
    ecp.filled_count,
    ecp.null_count,
    ecp.distinct_count,
    CASE 
        WHEN ecp.detected_type = fm.expected_type THEN 'EXACT'
        WHEN ecp.detected_type LIKE '%/%' OR ecp.detected_type = 'Unknown' THEN 'AMBIGUOUS'
        ELSE 'MISMATCH'
    END AS type_match_status,
    CASE 
        WHEN ecp.pct_filled > 0 AND fm.is_required = 1 THEN 'Required ✓'
        WHEN ecp.pct_filled > 0 THEN 'Mapped'
        WHEN fm.is_required = 1 THEN 'REQUIRED ✗'
        ELSE 'Empty'
    END AS mapping_status
FROM field_mapping fm
LEFT JOIN extract_column_profile ecp ON ecp.column_name = fm.source_column
WHERE ecp.extract_id = :extractId
  AND ecp.client_pk = :clientpk
ORDER BY fm.sort_order;
```

---

### MV-6. Dual-Mapped Field Count

**Definition:** Count of source columns that map to both the `claim` and `claimline` tables simultaneously (e.g., `Claim Number` → `cl_claimid` + `ln_claimid`).

**SQL Query:**
```sql
SELECT COUNT(*)
FROM field_mapping fm
WHERE fm.ci_db_field_2 IS NOT NULL
  AND fm.client_pk = :clientpk;
```

**DAX Measure:**
```dax
Dual-Mapped Fields = 
COUNTROWS(FILTER(FieldMapping, NOT ISBLANK(FieldMapping[ci_db_field_2])))
```

---

### MV-7. Table Distribution (Claim vs Claimline)

**Definition:** Count of fields targeting each CI database table.

**SQL Query:**
```sql
SELECT 
    fm.target_table,
    COUNT(*) AS field_count
FROM field_mapping fm
WHERE fm.client_pk = :clientpk
GROUP BY fm.target_table
ORDER BY field_count DESC;
```

**DAX Measure:**
```dax
Claim Table Fields = 
COUNTROWS(FILTER(FieldMapping, FieldMapping[target_table] = "claim"))

Claimline Table Fields = 
COUNTROWS(FILTER(FieldMapping, FieldMapping[target_table] = "claimline"))
```

---

### MV-8. Weighted Completeness (Overall)

**Definition:** Total filled cells divided by total possible cells across all profiled columns. More accurate than simple average because it weights by row count.

**Formula:** `Σ(filled_count) / Σ(total_count)` across all columns.

**SQL Query:**
```sql
SELECT
    SUM(ecp.filled_count) AS total_filled,
    SUM(ecp.total_count) AS total_cells,
    ROUND(SUM(ecp.filled_count) * 100.0 / SUM(ecp.total_count), 2) AS weighted_completeness_pct
FROM extract_column_profile ecp
WHERE ecp.extract_id = :extractId
  AND ecp.client_pk = :clientpk;
```

**DAX Measure:**
```dax
Weighted Completeness % = 
DIVIDE(
    SUMX(ExtractProfile, ExtractProfile[filled_count]),
    SUMX(ExtractProfile, ExtractProfile[total_count]),
    0
)
```

---

### MV-9. Completeness Band Distribution

**Definition:** Count of columns in each completeness tier.

| Band | Rule |
|------|------|
| Complete | ≥99% filled |
| Partial | 50–99% filled |
| Sparse | >0% and <50% filled |
| Empty | 0% filled |

**SQL Query:**
```sql
SELECT
    CASE
        WHEN pct_filled >= 0.99 THEN 'Complete'
        WHEN pct_filled >= 0.50 THEN 'Partial'
        WHEN pct_filled > 0 THEN 'Sparse'
        ELSE 'Empty'
    END AS completeness_band,
    COUNT(*) AS column_count
FROM extract_column_profile
WHERE extract_id = :extractId
  AND client_pk = :clientpk
GROUP BY 1
ORDER BY 
    CASE WHEN pct_filled >= 0.99 THEN 1
         WHEN pct_filled >= 0.50 THEN 2
         WHEN pct_filled > 0 THEN 3
         ELSE 4 END;
```

**DAX Measure:**
```dax
Complete Fields = 
COUNTROWS(FILTER(ExtractProfile, ExtractProfile[pct_filled] >= 0.99))

Partial Fields = 
COUNTROWS(FILTER(ExtractProfile, 
    ExtractProfile[pct_filled] >= 0.50 && ExtractProfile[pct_filled] < 0.99))

Sparse Fields = 
COUNTROWS(FILTER(ExtractProfile, 
    ExtractProfile[pct_filled] > 0 && ExtractProfile[pct_filled] < 0.50))

Empty Fields = 
COUNTROWS(FILTER(ExtractProfile, ExtractProfile[pct_filled] = 0))
```

---

### MV-10. Category-Level Completeness

**Definition:** Average completeness percentage across all columns within each field category (e.g., "Claim Identification", "Financial", "Provider - Billing").

**SQL Query:**
```sql
SELECT
    fc.category_name,
    COUNT(*) AS field_count,
    ROUND(AVG(ecp.pct_filled) * 100, 1) AS avg_completeness_pct,
    MIN(ecp.pct_filled) AS min_completeness,
    MAX(ecp.pct_filled) AS max_completeness
FROM extract_column_profile ecp
JOIN field_category fc ON fc.column_name = ecp.column_name
WHERE ecp.extract_id = :extractId
  AND ecp.client_pk = :clientpk
GROUP BY fc.category_name
ORDER BY avg_completeness_pct ASC;
```

**DAX Measure:**
```dax
Category Completeness = 
AVERAGEX(
    FILTER(ExtractProfile, 
        ExtractProfile[category] = SELECTEDVALUE(FieldCategory[category_name])),
    ExtractProfile[pct_filled]
)
```

---

### Pre & Post Mapping Validation — Metrics Summary

| # | Metric | SQL Function | DAX Function |
|---|--------|--------------|--------------|
| MV-1 | Mapping Coverage | COUNT(mapped) / COUNT(*) | DIVIDE(COUNTROWS(mapped), COUNTROWS(all)) |
| MV-2 | Required Readiness | COUNT(required & ≥95%) / COUNT(required) | DIVIDE(ready, total required) |
| MV-3 | Type Compatibility | COUNT(type match) / COUNT(mapped) | DIVIDE(exact, mapped) |
| MV-4 | Pre-Mapping Status | CASE WHEN rules engine | SWITCH(TRUE(), rules) |
| MV-5 | Post-Mapping Detail | JOIN mapping + profile | Related table lookup |
| MV-6 | Dual-Mapped Count | COUNT(field_2 IS NOT NULL) | COUNTROWS(FILTER(NOT ISBLANK)) |
| MV-7 | Table Distribution | GROUP BY target_table | COUNTROWS(FILTER(table)) |
| MV-8 | Weighted Completeness | SUM(filled) / SUM(total) | DIVIDE(SUMX(filled), SUMX(total)) |
| MV-9 | Completeness Bands | CASE ≥99/≥50/>0/=0 | COUNTROWS(FILTER(threshold)) |
| MV-10 | Category Completeness | AVG(pct_filled) GROUP BY category | AVERAGEX(FILTER(category)) |

