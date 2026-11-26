# Portfolio Case Study — Bank Aria: Customer 360° & Churn Analytics (Persian RTL BI Package)

* **Domain:** Retail & Commercial Banking — Customer 360° & Churn Intelligence
* **Target Stack:** Power BI Star Schema (`MODEL.md`, `measures.dax`, `theme.json`, `POWER_BI_BUILD_GUIDE.md`) + Interactive 5-Page RTL Streamlit Preview App (`app.py`)
* **Dataset:** Public `Churn_Modelling.csv` (10,000 customers × 14 columns) deterministically localized into Persian/Jalali/IRR while preserving 100% of underlying statistical distributions and correlations.
* **Reference Snapshot Date:** `1403/12/29` (Jalali Calendar)

---

## 1. Executive Summary & Objective

Financial institutions in Persian-speaking markets require native Right-to-Left (RTL) Business Intelligence solutions that combine rigorous dimensional modeling (Star Schema), Persian typography (`Vazirmatn FD` with Farsi numerals), and Jalali (`Shamsi`) calendar support.

This portfolio project builds an end-to-end **Customer 360° & Churn Analysis** solution for a fictional Iranian bank (**"Bank Aria" / بانک آریا**). Because the build environment is Linux-based, this repository delivers the complete data engineering pipeline, processed Star Schema tables, Power BI DAX measure library, Power BI JSON theme (`Bank Aria Fa`), a step-by-step Power BI Desktop build guide, and a live 5-page RTL Streamlit preview application tested with 15 automated unit and UI tests.

---

## 2. Data Engineering & Deterministic Localization Pipeline (`scripts/build_data.py`)

Starting from the untouched raw dataset (`data/raw/Churn_Modelling.csv`, 10,000 rows × 14 columns, zero nulls/duplicates), `scripts/build_data.py` executes a reproducible (`SEED = 42`) transformation into a 6-table Star Schema:

1. **100% Untouched Core Features & Target:**
   - `CustomerId` (`customer_id`), `Exited` (`20.37%` churn / `79.63%` retained), `CreditScore`, `Age`, `Tenure`, `NumOfProducts` (`15,302` total holdings across 10,000 customers), `IsActiveMember` (`51.51%`), and `HasCrCard` (`70.55%`) are preserved without alteration.
2. **1:1 Geography Label Mapping (Statistical Signal Preservation):**
   - `France` (5,014 customers, `16.15%` churn) $\rightarrow$ **Tehran (`تهران`)**
   - `Germany` (2,509 customers, `32.44%` churn) $\rightarrow$ **Isfahan (`اصفهان`)**
   - `Spain` (2,477 customers, `16.67%` churn) $\rightarrow$ **Khorasan Razavi (`خراسان رضوی`)**
   - *Methodological Transparency:* Both the Persian label (`province`) and original label (`source_geography`) are stored side-by-side so analysts never mistake the `32.44%` German churn rate for real-world macroeconomic behavior in Isfahan.
3. **Illustrative Currency Scaling (`× 250,000` IRR):**
   - `Balance` and `EstimatedSalary` are multiplied by a constant display factor of `250,000` and rounded to integer Rials (`balance_irr`, `estimated_salary_irr`), yielding a total portfolio balance of `191,214,723,220,000` illustrative IRR and a mean balance of `19,121,472,322` illustrative IRR (`36.17%` zero-balance customers).
4. **Continuous Jalali Calendar (`dim_date.csv`):**
   - Generated using `jdatetime` from `1392/01/01` through the reference snapshot date `1403/12/29` (`4,382` consecutive days, `YYYY/MM/DD` format).
   - Customer acquisition dates (`acquisition_jalali`) are deterministically derived by subtracting `Tenure` years from `1403/12/29` with seeded day/month jitter.
5. **Multi-Fact Enrichment (`fact_product_holding.csv`):**
   - Deterministically expands each customer's `NumOfProducts` (`1..4`) into `15,302` product-holding records linked to `dim_product` (`4` core banking products) such that each customer's allocated product balances sum exactly to their `balance_irr`.

---

## 3. Star Schema Architecture & DAX Layer

* **Dimensions:** `dim_date` (Role-Playing on Snapshot Date, Acquisition Date, and Product Opened Date), `dim_customer` (10,000 rows), `dim_branch` (7 fictional branches across 3 provinces), `dim_product` (4 products).
* **Facts:** `fact_snapshot` (10,000 customer snapshot rows) and `fact_product_holding` (15,302 derived product rows).
* **Cardinality & Filter Direction:** Strict `1 -> *` single-direction filtering from dimensions to facts, documented in `model/MODEL.md` and illustrated in `assets/model_diagram.svg`.
* **DAX Measures (`model/measures.dax`):** 30+ standard measures organized into 6 display folders (Core Churn KPIs, Deposit Balances, Engagement & Credit, Product Cross-Sell, Role-Playing Cohort Measures via `USERELATIONSHIP`, and Province Benchmarks).
* **Row-Level Security (RLS):** Documented province-based roles (`Province_Tehran`, `Province_Isfahan`, `Province_Khorasan_Razavi`).

---

## 4. Interactive 5-Page RTL Preview App (`app.py`)

The Streamlit application (`app.py`, port `8502`) provides an immediate, interactive preview of all 5 report pages:
1. **Executive Overview (`نمای کلی`):** Top-level KPI cards, provincial churn comparison, U-shaped product count churn curve, age distribution, and active vs. inactive retention.
2. **Customer Churn Drivers (`تحلیل ریزش مشتری`):** Age × Gender churn breakdown, Credit Score band analysis, Deposit Balance distributions (box plots), and Tenure churn curve.
3. **Provinces & Branches (`استان‌ها و شعب`):** Explicit methodological disclosure banner + deposit volume and churn rate across the 7 fictional branches.
4. **Product Portfolio (`سبد محصولات`):** Cross-sell retention analysis (`2` products optimal at `7.58%` churn vs. `3+` products high risk) and product category breakdown across all `15,302` holdings.
5. **Customer 360° Inspector (`جستجوی مشتریان`):** Instant search by `customer_id`, synthetic Persian name, or source surname, with an interactive 360° customer profile card and product holding table.

### Key Technical Highlights in `app.py`:
* **Offline Local Font Embedding:** `Vazirmatn FD` (`woff2`) is base64-embedded directly into CSS `@font-face` rules so the app makes **zero external network requests** at runtime.
* **Plotly LTR Isolation in RTL Layout:** Applies `.js-plotly-plot, .js-plotly-plot * { direction: ltr !important; }` to prevent SVG axis/label reversal inside the RTL page container, paired with `cliponaxis=False` and custom margins via `style_fig(..., margin=...)`.

---

## 5. Automated Testing & Honest Validation (`VALIDATION.md` & `LIMITATIONS.md`)

* **15 Automated Tests (`python3 -m unittest discover -s tests -v`):** Verifies raw data integrity, row-by-row `×250,000` currency scaling parity, untouched numeric/target columns, 1:1 geography/gender mappings, foreign key referential integrity across all 8 Star Schema relationships, continuous Jalali calendar dates, `summary_stats.json` accuracy, and `streamlit.testing.v1.AppTest` execution across all 5 pages and filters without exception.
* **Honest Disclosure of Untested Items:** Because this package is built in a Linux environment, no `.pbix` binary is included, DAX formulas have not been executed inside a Windows VertiPaq engine, and RLS roles have not been tested via Power BI Desktop's `View as` UI. No real-world business impact or ROI is claimed.
