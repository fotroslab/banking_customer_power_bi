# راهنمای گام‌به‌گام ساخت گزارش در Power BI Desktop (`POWER_BI_BUILD_GUIDE.md`)

این راهنما مسیر دقیق ساخت فایل `.pbix` پروژه **«بانک آریا — نمای ۳۶۰ درجه مشتری و تحلیل ریزش»** را در نرم‌افزار **Microsoft Power BI Desktop** از روی خروجی‌های آماده در پوشهٔ `data/processed/` شرح می‌دهد.

> **یادداشت صداقت تحلیلی:** این مخزن شامل فایل باینری `.pbix` نیست (زیرا در محیط لینوکس تولید شده است). تمامی جداول ستاره‌ای، تم JSON، فرمول‌های DAX و اپ پیش‌نمایش ۵ صفحه‌ای (`app.py`) به‌طور کامل آماده و تست شده‌اند تا ساخت `.pbix` در کمتر از ۲۰ دقیقه انجام شود.

---

## گام ۱: پیش‌نیازها و نصب فونت فارسی `Vazirmatn FD`

1. پیش از باز کردن Power BI Desktop، فایل‌های فونت موجود در مسیر `assets/fonts/Vazirmatn-FD-Regular.ttf` و `assets/fonts/Vazirmatn-FD-Bold.ttf` را در ویندوز نصب کنید (`Right Click → Install for all users`).
2. نصب نسخهٔ `FD` (Farsi Digits) باعث می‌شود تمام اعداد در کارت‌ها، جداول و محورهای نمودارهای Power BI به‌صورت خودکار با ارقام فارسی (`۰۱۲۳۴۵۶۷۸۹`) نمایش داده شوند.

---

## گام ۲: بارگذاری جداول ستاره‌ای در Power Query (UTF-8)

1. در Power BI Desktop از منوی **Home → Get Data → Text/CSV**، ۶ فایل زیر را از مسیر `data/processed/` بارگذاری کنید:
   - `dim_date.csv`
   - `dim_customer.csv`
   - `dim_branch.csv`
   - `dim_product.csv`
   - `fact_snapshot.csv`
   - `fact_product_holding.csv`
2. در پنجره پیش‌نمایش هر فایل، مطمئن شوید گزینهٔ **File Origin** روی **`65001: Unicode (UTF-8)`** قرار دارد تا حروف فارسی بدون به‌هم‌ریختگی خوانده شوند.
3. وارد **Transform Data (Power Query Editor)** شوید و نوع داده‌ها (Data Types) را کنترل کنید:
   - ستون‌های کلید و تاریخ شمسی (`date_jalali`, `snapshot_date_jalali`, `acquisition_jalali`, `opened_date_jalali`): از نوع **Text** (فرمت `YYYY/MM/DD`).
   - ستون‌های مبالغ ریالی (`balance_irr`, `estimated_salary_irr`, `allocated_balance_irr`): از نوع **Whole Number (Int64)**.
   - ستون‌های شمارشی و پرچم‌ها (`customer_id`, `exited`, `num_of_products`, `is_active_member`, `has_cr_card`, `credit_score`, `age`, `tenure`): از نوع **Whole Number**.
4. برای مرتب‌سازی صحیح ماه‌های شمسی در نمودارها:
   - در جدول `dim_date`، ستون `jalali_month_name` را انتخاب کرده و از منوی **Column tools → Sort by column**، آن را بر اساس ستون عددی `jalali_month` مرتب کنید.
   - ستون `day_of_week_name` را بر اساس `day_of_week_num` مرتب کنید.

---

## گام ۳: تنظیم روابط مدل ستاره‌ای (Model View)

در نمای **Model View**، گزینهٔ *Autodetect new relationships* را غیرفعال کرده و روابط زیر را دقیقاً مطابق تصویر `assets/model_diagram.svg` و سند `model/MODEL.md` ایجاد کنید:

1. `dim_customer[customer_id]` **(1)** longrightarrow `fact_snapshot[customer_id]` **(*)** — **Active**, Single Direction.
2. `dim_branch[branch_id]` **(1)** longrightarrow `fact_snapshot[branch_id]` **(*)** — **Active**, Single Direction.
3. `dim_date[date_jalali]` **(1)** longrightarrow `fact_snapshot[snapshot_date_jalali]` **(*)** — **Active**, Single Direction.
4. `dim_date[date_jalali]` **(1)** - - - - - - `fact_snapshot[acquisition_jalali]` **(*)** — **Inactive (غیرفعال — نقش‌گذاری تاریخ عضویت)**, Single Direction.
5. `dim_customer[customer_id]` **(1)** longrightarrow `fact_product_holding[customer_id]` **(*)** — **Active**, Single Direction.
6. `dim_branch[branch_id]` **(1)** longrightarrow `fact_product_holding[branch_id]` **(*)** — **Active**, Single Direction.
7. `dim_product[product_id]` **(1)** longrightarrow `fact_product_holding[product_id]` **(*)** — **Active**, Single Direction.
8. `dim_date[date_jalali]` **(1)** longrightarrow `fact_product_holding[opened_date_jalali]` **(*)** — **Active**, Single Direction.

> **بهینه‌سازی مدل:** پس از برقراری روابط، ستون‌های کلید خارجی (FK) در جداول `fact_snapshot` و `fact_product_holding` را در نمای Report مخفی کنید (`Hide in report view`) تا کاربران نهایی فقط از ستون‌های جداول بُعد (`dim_*`) برای فیلتر و برش استفاده کنند.

---

## گام ۴: اعمال تم «Bank Aria Fa» و چیدمان راست‌چین (RTL)

1. از منوی **View → Themes → Browse for themes**، فایل `report/theme.json` را انتخاب و بارگذاری کنید.
   - رنگ اصلی برند: سبز زمردی تیره (`#0b6e4f`)
   - رنگ تأکید: طلایی (`#d4a017`)
   - پس‌زمینه بوم: سبز-سفید ملایم (`#f7faf7`)
   - رنگ هشدار ریزش: قرمز آجری (`#c93b2b`)
2. تنظیمات راست‌چین (RTL) در هر صفحه:
   - پنل فیلترها و اسلایسرها (استان، گروه سنی، تعداد محصول، وضعیت فعالیت) را در **سمت راست بوم (Right Sidebar)** قرار دهید.
   - در کارت‌های KPI و عناوین نمودارها، تراز افقی متن (Horizontal Alignment) را روی **Right** تنظیم کنید.

---

## گام ۵: ایجاد جدول `_Measures` و افزودن فرمول‌های DAX

1. از منوی **Home → Enter Data** یک جدول خالی با نام `_Measures` بسازید.
2. فرمول‌های موجود در فایل `model/measures.dax` را به‌ترتیب در جدول `_Measures` ایجاد کرده و در پوشه‌های نمایشی (Display Folders) زیر دسته‌بندی کنید:
   - `01_Customer_Churn_KPIs` (`[Total Customers]`, `[Churned Customers]`, `[Churn Rate]`, `[Retention Rate]`)
   - `02_Deposits_IRR` (`[Total Balance (IRR)]`, `[Total Balance (Billion IRR)]`, `[Average Balance per Customer (IRR)]`, `[Zero Balance Share]`)
   - `03_Engagement_Credit` (`[Active Member Share]`, `[Credit Card Penetration]`, `[Average Credit Score]`)
   - `04_Product_CrossSell` (`[Average Products per Customer]`, `[Total Product Holdings]`, `[Multi-Product Share]`)
   - `05_RolePlaying_Cohort` (`[Customers Acquired by Period]`, `[Cohort Churn Rate]`)
3. پس از ساخت اولین Measure، ستون خالی `Column1` را از جدول `_Measures` حذف کنید تا به یک Measure Group استاندارد تبدیل شود.

---

## گام ۶: طراحی ۵ صفحه گزارش (هماهنگ با `app.py`)

| شماره صفحه | نام صفحه (Tab) | ویژوال‌های اصلی صفحه |
| :---: | :--- | :--- |
| **۱** | **نمای کلی** | ۴ کارت KPI در بالا (`[Total Balance (Billion IRR)]`, `[Churn Rate]`, `[Average Products per Customer]`, `[Active Member Share]`) + نمودار میله‌ای افقی نرخ ریزش به تفکیک استان + نمودار میله‌ای نرخ ریزش بر اساس تعداد محصول + توزیع سنی + مقایسه ریزش فعال/غیرفعال |
| **۲** | **تحلیل ریزش مشتری** | نمودار گروهی نرخ ریزش بر اساس گروه سنی و جنسیت + نرخ ریزش بر اساس رده اعتباری (`credit_band`) + توزیع مانده سپرده در مشتریان مانده و ریزش‌کرده + نمودار خطی نرخ ریزش بر حسب سنوات حضور (`tenure`) |
| **۳** | **استان‌ها و شعب** | کادر متنی شفافیت روش‌شناختی (توضیح نگاشت ۱:۱ `Germany→اصفهان` و نرخ ریزش ۳۲٫۴۴٪) + نمودار افقی مانده سپرده شعب هفت‌گانه + نمودار نرخ ریزش شعب + جدول ماتریسی عملکرد شعب |
| **۴** | **سبد محصولات** | کادر توضیح مشتق بودن `fact_product_holding` + نمودار مقایسه مشتریان مانده/ریزش‌کرده بر حسب تعداد محصول (۱ تا ۴) + نمودار افقی توزیع ۱۵٬۳۰۲ فقره محصول در ۴ گروه محصولی + جدول خلاصه ریسک سبد |
| **۵** | **جستجوی مشتریان** | اسلایسر جستجوی متنی روی `customer_id` و `full_name_fa` + کارت ۳۶۰ درجه مشخصات مشتری + جدول محصولات نگهداری‌شده مشتری انتخابی + جدول جزئیات مشتریان |

---

## گام ۷: پیاده‌سازی امنیت سطح ردیف (RLS) و انتشار در Power BI Service

1. از منوی **Modeling → Manage roles** سه نقش زیر را ایجاد کنید:
   - `Province_Tehran`: روی جدول `dim_customer` شرط `[province] = "تهران"` و روی جدول `dim_branch` شرط `[province] = "تهران"`.
   - `Province_Isfahan`: روی جدول `dim_customer` شرط `[province] = "اصفهان"` و روی جدول `dim_branch` شرط `[province] = "اصفهان"`.
   - `Province_Khorasan_Razavi`: روی جدول `dim_customer` شرط `[province] = "خراسان رضوی"` و روی جدول `dim_branch` شرط `[province] = "خراسان رضوی"`.
2. از گزینهٔ **Modeling → View as** برای تست هر نقش استفاده کنید:
   - نقش `Province_Tehran` باید دقیقاً **۵٬۰۱۴ مشتری** و نرخ ریزش **۱۶٫۱۵٪** را نشان دهد.
   - نقش `Province_Isfahan` باید دقیقاً **۲٬۵۰۹ مشتری** و نرخ ریزش **۳۲٫۴۴٪** را نشان دهد.
   - نقش `Province_Khorasan_Razavi` باید دقیقاً **۲٬۴۷۷ مشتری** و نرخ ریزش **۱۶٫۶۷٪** را نشان دهد.
3. پس از ذخیرهٔ فایل `.pbix`، گزارش را در **Power BI Service / Power BI Report Server** منتشر کرده و اعضای سازمانی هر منطقه را در بخش **Security** دیتاست به نقش استانی مربوطه منتسب کنید.
