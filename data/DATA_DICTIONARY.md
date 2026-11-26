# فرهنگ داده (Data Dictionary) — بانک آریا: نمای ۳۶۰° مشتری و تحلیل ریزش

این سند شرح کامل ستون‌ها، نوع داده، دامنهٔ مقادیر و قواعد تبدیل را برای فایل خام (`data/raw/Churn_Modelling.csv`) و ۶ جدول مدل ستاره‌ای در پوشهٔ `data/processed/` ارائه می‌دهد.

---

## ۱. جدول منبع خام: `data/raw/Churn_Modelling.csv` (۱۰٬۰۰۰ ردیف × ۱۴ ستون)

| نام ستون در منبع | نوع داده | دامنه / نمونه مقادیر | وضعیت در پایپ‌لاین بومی‌سازی |
| :--- | :--- | :--- | :--- |
| `RowNumber` | Integer | `1` تا `10,000` | حفظ‌شده در `row_number` و `snapshot_id` |
| `CustomerId` | Integer | ۸ رقمی یکتا (`15565701` تا `15815690`) | حفظ ۱۰۰٪ در کلید اصلی `customer_id` |
| `Surname` | Text | نام خانوادگی انگلیسی/اروپایی | حفظ برای ردیابی در `original_surname` + جایگزینی با نام کامل فارسی ساختگی (`full_name_fa`) |
| `CreditScore` | Integer | `350` تا `850` (میانگین: `650.53`) | **دست‌نخورده ۱۰۰٪** در `credit_score` + گروه‌بندی در `credit_band` |
| `Geography` | Text | `France` (5,014), `Germany` (2,509), `Spain` (2,477) | نگاشت ۱:۱ قطعی: `France→تهران`، `Germany→اصفهان`، `Spain→خراسان رضوی` |
| `Gender` | Text | `Female` (4,543), `Male` (5,457) | نگاشت ۱:۱: `Female→زن`، `Male→مرد` |
| `Age` | Integer | `18` تا `92` (میانگین: `38.92`) | **دست‌نخورده ۱۰۰٪** در `age` + گروه‌بندی در `age_group` |
| `Tenure` | Integer | `0` تا `10` سال (میانگین: `5.01`) | **دست‌نخورده ۱۰۰٪** در `tenure` + استخراج تاریخ عضویت شمسی (`acquisition_jalali`) از مرجع `۱۴۰۳/۱۲/۲۹` |
| `Balance` | Float | `0.00` تا `250,898.09` (۳۶٫۱۷٪ مانده صفر) | مقیاس‌بندی نمایشی `×۲۵۰٬۰۰۰` و گرد شدن به ریال در `balance_irr` |
| `NumOfProducts` | Integer | `1` تا `4` (میانگین: `1.5302`، مجموع: `15,302`) | **دست‌نخورده ۱۰۰٪** در `num_of_products` + مبنای مشتق‌سازی `fact_product_holding` |
| `HasCrCard` | Integer (0/1) | `0` (29.45%), `1` (70.55%) | **دست‌نخورده ۱۰۰٪** در `has_cr_card` |
| `IsActiveMember` | Integer (0/1) | `0` (48.49%), `1` (51.51%) | **دست‌نخورده ۱۰۰٪** در `is_active_member` |
| `EstimatedSalary` | Float | `11.58` تا `199,992.48` | مقیاس‌بندی نمایشی `×۲۵۰٬۰۰۰` و گرد شدن به ریال در `estimated_salary_irr` |
| `Exited` | Integer (0/1) | `0` (7,963 — 79.63%), `1` (2,037 — 20.37%) | **دست‌نخورده ۱۰۰٪** (متغیر هدف ریزش مشتری) |

---

## ۲. جدول بُعد تقویم شمسی: `data/processed/dim_date.csv` (۴٬۳۸۲ ردیف)

| نام ستون | نوع داده | نقش کلید | شرح و نمونه مقدار |
| :--- | :--- | :--- | :--- |
| `date_key` | Integer | AK | کلید عددی تاریخ شمسی با فرمت `YYYYMMDD` (مثلاً `14031229`) |
| `date_jalali` | Text | **PK** | تاریخ شمسی استاندارد با فرمت `YYYY/MM/DD` (`1392/01/01` تا `1403/12/29`) |
| `date_gregorian` | Text | — | معادل میلادی با فرمت `YYYY-MM-DD` |
| `jalali_year` | Integer | — | سال شمسی (`1392` تا `1403`) |
| `jalali_quarter` | Integer | — | شماره فصل (`1` تا `4`) |
| `jalali_quarter_name` | Text | — | نام فصل (`فصل ۱` تا `فصل ۴`) |
| `jalali_month` | Integer | — | شماره ماه شمسی (`1` تا `12`) |
| `jalali_month_name` | Text | — | نام ماه شمسی (`فروردین` تا `اسفند`) |
| `jalali_year_month` | Text | — | ترکیب سال و ماه (`YYYY/MM`) |
| `jalali_day` | Integer | — | روز ماه (`1` تا `31`) |
| `day_of_week_num` | Integer | — | شماره روز هفته ایرانی (`1`=شنبه تا `7`=جمعه) |
| `day_of_week_name` | Text | — | نام روز هفته (`شنبه` تا `جمعه`) |
| `is_weekend` | Integer (0/1) | — | پرچم آخر هفته (`1` برای پنجشنبه و جمعه، `0` سایر روزها) |

---

## ۳. جدول بُعد مشتری: `data/processed/dim_customer.csv` (۱۰٬۰۰۰ ردیف)

| نام ستون | نوع داده | نقش کلید | شرح و قاعده ساخت |
| :--- | :--- | :--- | :--- |
| `customer_id` | Integer | **PK** | شناسه یکتای مشتری (عیناً برابر با `CustomerId` منبع) |
| `row_number` | Integer | — | شماره ردیف اصلی در فایل منبع (`1..10000`) |
| `full_name_fa` | Text | — | نام و نام خانوادگی فارسی ساختگی (مشتق قطعی از `customer_id` و جنسیت) |
| `first_name_fa` | Text | — | نام کوچک فارسی ساختگی |
| `last_name_fa` | Text | — | نام خانوادگی فارسی ساختگی |
| `original_surname` | Text | — | نام خانوادگی اصلی در فایل منبع جهت قابلیت ردیابی |
| `gender` | Text | — | جنسیت فارسی (`زن` / `مرد`) |
| `gender_raw` | Text | — | جنسیت اصلی منبع (`Female` / `Male`) |
| `age` | Integer | — | سن مشتری (دست‌نخورده از منبع) |
| `age_group` | Text | — | گروه سنی (`زیر ۳۰ سال`، `۳۰ تا ۳۹ سال`، `۴۰ تا ۴۹ سال`، `۵۰ تا ۵۹ سال`، `۶۰ سال به بالا`) |
| `province` | Text | — | استان بومی‌سازی‌شده (`تهران`، `اصفهان`، `خراسان رضوی`) |
| `source_geography` | Text | — | کشور اصلی در منبع (`France`، `Germany`، `Spain`) |
| `branch_id` | Text | FK | کد شعبه مشتری (`BR-101` تا `BR-302`) |
| `tenure_years` | Integer | — | سنوات حضور مشتری به سال (`0..10`) |
| `tenure_group` | Text | — | گروه سابقه (`کمتر از ۲ سال`، `۲ تا ۵ سال`، `۶ تا ۸ سال`، `بیش از ۸ سال`) |
| `acquisition_jalali` | Text | FK | تاریخ عضویت شمسی (`YYYY/MM/DD`) مشتق از `۱۴۰۳/۱۲/۲۹` منهای `Tenure` با jitter ثابت |
| `acquisition_date_key` | Integer | FK | کلید عددی تاریخ عضویت (`YYYYMMDD`) |
| `credit_score` | Integer | — | امتیاز اعتباری مشتری (`350..850`) |
| `credit_band` | Text | — | رده اعتباری (`ضعیف (<۵۸۰)`، `متوسط (۵۸۰-۶۶۹)`، `خوب (۶۷۰-۷۳۹)`، `عالی (۷۴۰-۷۹۹)`، `ممتاز (۸۰۰+)`) |
| `has_credit_card` | Integer (0/1) | — | وضعیت داشتن کارت اعتباری (`0`/`1`) |
| `has_credit_card_label` | Text | — | برچسب کارت اعتباری (`دارای کارت اعتباری` / `فاقد کارت اعتباری`) |
| `is_active_member` | Integer (0/1) | — | وضعیت فعالیت (`0`/`1`) |
| `activity_status_label` | Text | — | برچسب وضعیت فعالیت (`فعال` / `غیرفعال`) |
| `estimated_salary_irr` | Int64 | — | حقوق تخمینی ریالی نمایشی (`round(EstimatedSalary × 250,000)`) |

---

## ۴. جدول بُعد شعبه: `data/processed/dim_branch.csv` (۷ ردیف)

| نام ستون | نوع داده | نقش کلید | شرح |
| :--- | :--- | :--- | :--- |
| `branch_id` | Text | **PK** | کد یکتای شعبه (`BR-101` تا `BR-302`) |
| `branch_code` | Integer | — | کد عددی شعبه (`101` تا `302`) |
| `branch_name` | Text | — | نام فارسی شعبه ساختگی (مثلاً `شعبه مرکزی تهران`، `شعبه چهارباغ اصفهان`) |
| `province` | Text | — | استان محل شعبه (`تهران`، `اصفهان`، `خراسان رضوی`) |
| `source_geography` | Text | — | جغرافیای متناظر در منبع (`France`، `Germany`، `Spain`) |
| `city` | Text | — | شهر (`تهران`، `اصفهان`، `مشهد`) |
| `branch_tier` | Text | — | درجه شعبه (`درجه ممتاز` / `درجه یک`) |
| `region_manager` | Text | — | نام حوزه مدیریت منطقه |

---

## ۵. جدول بُعد محصول: `data/processed/dim_product.csv` (۴ ردیف)

| نام ستون | نوع داده | نقش کلید | شرح |
| :--- | :--- | :--- | :--- |
| `product_id` | Text | **PK** | کد یکتای محصول (`PRD-01` تا `PRD-04`) |
| `product_code` | Integer | — | کد عددی محصول (`1` تا `4`) |
| `product_name` | Text | — | عنوان فارسی محصول بانکی |
| `product_category` | Text | — | طبقه محصول (`سپرده‌های دیداری و پرداخت`، `سپرده‌های سرمایه‌گذاری`، `تسهیلات و اعتبارات`، `مدیریت ثروت و سرمایه‌گذاری`) |
| `is_credit_product` | Integer (0/1) | — | آیا محصول اعتباری/تسهیلاتی است؟ (`1` برای `PRD-03`، `0` برای سایرین) |
| `annual_rate_pct` | Float | — | نرخ سود/کارمزد سالانه نمایشی (`%`) |
| `description` | Text | — | شرح محصول |

---

## ۶. جدول فکت اسنپ‌شات مشتری: `data/processed/fact_snapshot.csv` (۱۰٬۰۰۰ ردیف)

| نام ستون | نوع داده | نقش کلید | شرح |
| :--- | :--- | :--- | :--- |
| `snapshot_id` | Integer | **PK** | کلید یکتای ردیف اسنپ‌شات (`1..10000`) |
| `customer_id` | Integer | FK | کلید خارجی به `dim_customer.customer_id` |
| `branch_id` | Text | FK | کلید خارجی به `dim_branch.branch_id` |
| `snapshot_date_jalali` | Text | FK | تاریخ مرجع اسنپ‌شات (`1403/12/29`) متصل به `dim_date.date_jalali` |
| `snapshot_date_key` | Integer | FK | کلید عددی تاریخ اسنپ‌شات (`14031229`) |
| `acquisition_jalali` | Text | FK (نقش) | تاریخ عضویت شمسی متصل به `dim_date.date_jalali` (رابطه غیرفعال Role-Playing) |
| `acquisition_date_key` | Integer | FK | کلید عددی تاریخ عضویت (`YYYYMMDD`) |
| `credit_score` | Integer | — | امتیاز اعتباری مشتری (دست‌نخورده از منبع) |
| `age` | Integer | — | سن مشتری (دست‌نخورده از منبع) |
| `tenure` | Integer | — | سنوات حضور (دست‌نخورده از منبع) |
| `balance_eur_raw` | Float | — | مانده اصلی در فایل منبع (جهت ممیزی و تطبیق) |
| `balance_irr` | Int64 | — | مانده سپرده ریالی نمایشی (`round(Balance × 250,000)`) |
| `is_zero_balance` | Integer (0/1) | — | پرچم مانده صفر (`1` اگر `balance_irr == 0` وگرنه `0`) |
| `estimated_salary_eur_raw` | Float | — | حقوق تخمینی اصلی در فایل منبع |
| `estimated_salary_irr` | Int64 | — | حقوق تخمینی ریالی نمایشی (`round(EstimatedSalary × 250,000)`) |
| `num_of_products` | Integer | — | تعداد محصولات مشتری (`1..4` — دست‌نخورده از منبع) |
| `has_cr_card` | Integer (0/1) | — | داشتن کارت اعتباری (`0`/`1` — دست‌نخورده از منبع) |
| `is_active_member` | Integer (0/1) | — | عضو فعال (`0`/`1` — دست‌نخورده از منبع) |
| `exited` | Integer (0/1) | — | شاخص هدف ریزش مشتری (`1`=ریزش‌کرده، `0`=مانده — دست‌نخورده از منبع) |
| `churn_status_label` | Text | — | برچسب وضعیت ریزش (`ریزش‌کرده` / `مانده`) |

---

## ۷. جدول فکت نگهداری محصول (مشتق): `data/processed/fact_product_holding.csv` (۱۵٬۳۰۲ ردیف)

| نام ستون | نوع داده | نقش کلید | شرح و محدودیت روش‌شناختی |
| :--- | :--- | :--- | :--- |
| `holding_id` | Integer | **PK** | شناسه یکتای ردیف نگهداری محصول (`1..15302`) |
| `customer_id` | Integer | FK | کلید خارجی به `dim_customer.customer_id` |
| `branch_id` | Text | FK | کلید خارجی به `dim_branch.branch_id` |
| `product_id` | Text | FK | کلید خارجی به `dim_product.product_id` |
| `opened_date_jalali` | Text | FK | تاریخ نمایشی بازگشایی محصول (`YYYY/MM/DD` بین `acquisition_jalali` و `1403/12/29`) |
| `opened_date_key` | Integer | FK | کلید عددی تاریخ بازگشایی محصول (`YYYYMMDD`) |
| `snapshot_date_jalali` | Text | FK | تاریخ اسنپ‌شات (`1403/12/29`) |
| `product_sequence` | Integer | — | شماره ترتیب محصول برای مشتری (`1` تا `num_of_products`) |
| `allocated_balance_irr` | Int64 | — | سهم مانده تخصیص‌یافته به محصول (مجموع برای هر مشتری دقیقاً برابر با `balance_irr` است) |
| `holding_status` | Text | — | وضعیت محصول (`فعال` برای مشتریان مانده، `بسته/ریزش` برای مشتریان ریزش‌کرده) |
| `is_synthetic_derivation` | Integer | — | مقدار ثابت `1` جهت تصریح مشتق بودن این جدول از روی `NumOfProducts` |
