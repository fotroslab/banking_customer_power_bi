# معماری مدل داده ستاره‌ای (Star Schema) — بانک آریا: نمای ۳۶۰° مشتری و تحلیل ریزش

این سند مشخصات فنی مدل داده ستاره‌ای پروژه **«بانک آریا — نمای ۳۶۰ درجه مشتری و تحلیل ریزش»** را تشریح می‌کند. تمامی جداول توسط اسکریپت `scripts/build_data.py` به‌صورت قطعی (Deterministic) از فایل خام `data/raw/Churn_Modelling.csv` تولید شده و در پوشه `data/processed/` ذخیره می‌شوند.

---

## ۱. خلاصه جداول مدل ستاره‌ای

| نام جدول | نوع جدول | دانه (Grain) | تعداد ردیف | کلید اصلی (PK) | توضیح کاربرد |
| :--- | :--- | :--- | ---: | :--- | :--- |
| `dim_date` | بُعد تقویم (نقش‌گذاری) | یک ردیف به‌ازای هر روز تقویم شمسی (`۱۳۹۲/۰۱/۰۱` تا `۱۴۰۳/۱۲/۲۹`) | ۴٬۳۸۲ | `date_jalali` (`YYYY/MM/DD`) / `date_key` (`YYYYMMDD`) | فیلتر و گروه‌بندی زمانی بر اساس تاریخ اسنپ‌شات، تاریخ عضویت و تاریخ بازگشایی محصول |
| `dim_customer` | بُعد مشتری | یک ردیف به‌ازای هر مشتری یکتا | ۱۰٬۰۰۰ | `customer_id` (از `CustomerId` منبع) | ویژگی‌های جمعیت‌شناختی، استان (نگاشت ۱:۱ منبع)، رده اعتباری، گروه سنی و وضعیت فعالیت |
| `dim_branch` | بُعد شعبه | یک ردیف به‌ازای هر شعبه ساختگی بانک آریا | ۷ | `branch_id` (`BR-101` تا `BR-302`) | تحلیل عملکرد شعب هفت‌گانه در سه استان تهران، اصفهان و خراسان رضوی |
| `dim_product` | بُعد محصول بانکی | یک ردیف به‌ازای هر محصول بانکی پایه | ۴ | `product_id` (`PRD-01` تا `PRD-04`) | دسته‌بندی سبد محصولات بانکی (جاری، کوتاه‌مدت، کارت اعتباری/مرابحه، بلندمدت ویژه) |
| `fact_snapshot` | فکت اسنپ‌شات مشتری | یک ردیف به‌ازای هر مشتری در تاریخ مرجع `۱۴۰۳/۱۲/۲۹` | ۱۰٬۰۰۰ | `snapshot_id` (`1..10000`) | جدول فکت اصلی شامل وضعیت ریزش (`exited`)، مانده سپرده ریالی نمایشی، امتیاز اعتباری، سنوات و شمار محصول |
| `fact_product_holding` | فکت نگهداری محصول (مشتق) | یک ردیف به‌ازای هر فقره محصول در سبد مشتری | ۱۵٬۳۰۲ | `holding_id` (`1..15302`) | جدول فکت مشتق‌شده از `NumOfProducts` برای تحلیل نفوذ محصول و سبد چندمحصولی (Cross-Sell) |

---

## ۲. نمودار روابط مدل (Star Schema Relationships)

تمامی روابط در Power BI Desktop از نوع **یک‌به‌چند (`1 → *`)** و با جهت فیلتر **یک‌طرفه (Single Direction: Dimension Filters Fact)** تعریف می‌شوند تا از ابهام مسیر فیلتر (Ambiguity) و افت کارایی در موتور VertiPaq جلوگیری شود.

| شماره | جدول بُعد (طرف ۱) | ستون کلید در بُعد | جدول فکت (طرف `*`) | ستون کلید خارجی (FK) | وضعیت رابطه | جهت فیلتر |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- |
| ۱ | `dim_customer` | `customer_id` | `fact_snapshot` | `customer_id` | **فعال (Active)** | یک‌طرفه (`dim → fact`) |
| ۲ | `dim_branch` | `branch_id` | `fact_snapshot` | `branch_id` | **فعال (Active)** | یک‌طرفه (`dim → fact`) |
| ۳ | `dim_date` | `date_jalali` | `fact_snapshot` | `snapshot_date_jalali` | **فعال (Active)** | یک‌طرفه (`dim → fact`) |
| ۴ | `dim_date` | `date_jalali` | `fact_snapshot` | `acquisition_jalali` | **غیرفعال (Inactive — Role-Playing)** | یک‌طرفه (`dim → fact` با `USERELATIONSHIP`) |
| ۵ | `dim_customer` | `customer_id` | `fact_product_holding` | `customer_id` | **فعال (Active)** | یک‌طرفه (`dim → fact`) |
| ۶ | `dim_branch` | `branch_id` | `fact_product_holding` | `branch_id` | **فعال (Active)** | یک‌طرفه (`dim → fact`) |
| ۷ | `dim_product` | `product_id` | `fact_product_holding` | `product_id` | **فعال (Active)** | یک‌طرفه (`dim → fact`) |
| ۸ | `dim_date` | `date_jalali` | `fact_product_holding` | `opened_date_jalali` | **فعال (Active)** | یک‌طرفه (`dim → fact`) |

> **نکته درباره کلید جایگزین تقویم (`date_key`):** در هر دو جدول فکت، علاوه بر ستون متنی استاندارد `YYYY/MM/DD` (`snapshot_date_jalali` و `acquisition_jalali`)، ستون عددی `YYYYMMDD` (`snapshot_date_key` و `acquisition_date_key`) نیز تعبیه شده است تا در صورت تمایل مهندس BI، اتصال روی کلید صحیح عددی (`Integer Key`) نیز بدون هیچ تغییری در Power Query امکان‌پذیر باشد.

---

## ۳. نقش‌گذاری بُعد زمان (Role-Playing `dim_date`)

از آنجا که منبع اصلی (`Churn_Modelling.csv`) یک اسنپ‌شات مقطعی است و سری زمانی روزانه از مانده حساب‌ها ندارد:
1. **تاریخ اسنپ‌شات (`snapshot_date_jalali`):** برای همهٔ ۱۰٬۰۰۰ ردیف برابر با تاریخ مرجع ثابت `۱۴۰۳/۱۲/۲۹` است.
2. **تاریخ عضویت مشتری (`acquisition_jalali`):** از تفاضل سنوات حضور (`Tenure`) از سال مرجع `۱۴۰۳` به‌همراه جابه‌جایی قطعی (Jitter) روز و ماه با `seed=42` ساخته شده است. با استفاده از رابطهٔ غیرفعال بین `dim_date[date_jalali]` و `fact_snapshot[acquisition_jalali]` و تابع `USERELATIONSHIP` در DAX، می‌توان تحلیل «تعداد مشتریان جذب‌شده بر حسب سال شمسی ورود (Cohort)» را انجام داد.
3. **هشدار صداقت تحلیلی:** هرگز نباید از این مدل برای ترسیم «روند ماهانهٔ مانده سپرده» استفاده کرد، زیرا دادهٔ منبع تنها ماندهٔ لحظهٔ اسنپ‌شات را دارد.

---

## ۴. طراحی امنیت سطح ردیف (Row-Level Security — RLS)

در محیط Power BI Desktop، سه نقش امنیتی استانی روی جدول `dim_branch` و `dim_customer` تعریف می‌شود تا مدیران هر استان تنها به داده‌های شعب و مشتریان استان خود دسترسی داشته باشند:

* **نقش `Province_Tehran`:**
  ```dax
  'dim_customer'[province] = "تهران"
  ```
* **نقش `Province_Isfahan`:**
  ```dax
  'dim_customer'[province] = "اصفهان"
  ```
* **نقش `Province_Khorasan_Razavi`:**
  ```dax
  'dim_customer'[province] = "خراسان رضوی"
  ```

> **شفافیت اجرایی:** قواعد RLS بالا به‌صورت کامل مستندسازی شده‌اند، اما از آنجا که این پروژه در محیط لینوکس و بدون فایل باینری `.pbix` و سرویس ابری کارفرما تولید شده است، آزمون عملی `View as Role` در Power BI Desktop / Service باید در گام بعدی توسط تیم BI بانک اجرا شود.
