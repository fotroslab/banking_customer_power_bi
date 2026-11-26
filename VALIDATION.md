# گزارش اعتبارسنجی و تست (`VALIDATION.md`)

این سند با رویکرد شفافیت کامل مهندسی مشخص می‌کند چه بخش‌هایی از پروژه **«بانک آریا — نمای ۳۶۰ درجه مشتری و تحلیل ریزش»** به‌صورت خودکار و بصری در این محیط تست و تأیید شده‌اند و چه بخش‌هایی نیازمند تست در محیط ویندوز / Power BI Desktop هستند.

---

## ۱. موارد تست‌شده و تأییدشده در این محیط (Verified ✅)

### الف) پایپ‌لاین داده و مدل ستاره‌ای (`python3 -m unittest discover -s tests -v`)
تمامی **۱۵ تست خودکار** در فایل `tests/test_data_quality.py` با موفقیت (`OK`) اجرا شده‌اند:

1. **صحت فایل منبع (`test_01_raw_file_integrity`):** بررسی ابعاد دقیق `10,000 × 14`، عدم وجود مقدار خالی (`Null = 0`) و یکتایی کامل `CustomerId`.
2. **شمار ردیف‌ها و کلیدهای اصلی (`test_02_processed_row_counts_and_uniqueness`):** تأیید `dim_date` (`4,382` ردیف)، `dim_customer` (`10,000` ردیف)، `dim_branch` (`7` ردیف)، `dim_product` (`4` ردیف)، `fact_snapshot` (`10,000` ردیف) و `fact_product_holding` (`15,302` ردیف).
3. **برابری دقیق مقیاس ریالی (`test_03_exact_currency_scaling_250000`):** تطبیق ردیف‌به‌ردیف `balance_irr == round(Balance × 250,000)` و `estimated_salary_irr == round(EstimatedSalary × 250,000)` برای هر ۱۰٬۰۰۰ مشتری.
4. **دست‌نخورده ماندن متغیرهای اصلی (`test_04_untouched_numeric_and_target_columns`):** تطبیق ۱۰۰٪ ستون‌های `Exited`، `CreditScore`، `Age`، `Tenure`، `NumOfProducts`، `IsActiveMember` و `HasCrCard` با فایل خام.
5. **نگاشت ۱:۱ جغرافیا و جنسیت (`test_05_geography_and_gender_1to1_mapping`):** تأیید تعداد مشتریان و نرخ ریزش دقیق هر استان (`تهران: ۵٬۰۱۴ نفر / ۱۶٫۱۵٪`، `اصفهان: ۲٬۵۰۹ نفر / ۳۲٫۴۴٪`، `خراسان رضوی: ۲٬۴۷۷ نفر / ۱۶٫۶۷٪`).
6. **توزیع محصولات و جدول مشتق (`test_06_product_distribution_and_holding_derivation`):** تأیید برابری تعداد ردیف‌های `fact_product_holding` هر مشتری با `num_of_products` و برابری مجموع `allocated_balance_irr` هر مشتری با `balance_irr`.
7. **یکپارچگی ارجاعی مدل ستاره‌ای (`test_07_star_schema_foreign_keys`):** تأیید اینکه ۱۰۰٪ کلیدهای خارجی در `fact_snapshot` و `fact_product_holding` در جداول بُعد متناظر (`dim_customer`, `dim_branch`, `dim_product`, `dim_date`) وجود دارند.
8. **پیوستگی تقویم شمسی (`test_08_dim_date_continuity_and_jalali_format`):** تأیید فرمت `YYYY/MM/DD`، پایان تقویم در `1403/12/29` و پیوستگی روزانه بدون حتی یک روز افتادگی (`diff == 1 day`).
9. **ساختگی بودن نام‌های فارسی (`test_09_farsi_names_are_synthetic`):** تأیید اینکه تمامی نام‌های `full_name_fa` از حروف فارسی تشکیل شده و هیچ نام خانوادگی واقعی از منبع در ستون نام فارسی باقی نمانده است.
10. **سازگاری `summary_stats.json` (`test_10_summary_stats_json_consistency`):** تطبیق کامل فایل خلاصه آماری با محاسبات مستقیم روی جداول پردازش‌شده.
11. **اعتبارسنجی تم Power BI (`test_11_theme_and_deliverable_files_exist`):** تأیید ساختار JSON فایل `report/theme.json` با نام `Bank Aria Fa` و پالت رنگی `#0b6e4f` / `#d4a017` روی `#f7faf7`.
12. **قواعد CSS راست‌چین و محافظ LTR نمودارها (`test_12_app_css_and_plotly_ltr_guard`):** تأیید وجود قاعدهٔ `.js-plotly-plot, .js-plotly-plot * { direction: ltr !important; }`، تابع `style_fig` و `cliponaxis=False`.
13. **تست خودکار صفحات ۱ تا ۳ اپ (`test_13_streamlit_apptest_pages_1_to_3`):** اجرای `streamlit.testing.v1.AppTest` روی صفحات «نمای کلی»، «تحلیل ریزش مشتری» و «استان‌ها و شعب» بدون هیچ استثنا (`exception = []`).
14. **تست خودکار صفحات ۴ و ۵ اپ (`test_14_streamlit_apptest_pages_4_and_5`):** اجرای `AppTest` روی صفحات «سبد محصولات» و «جستجوی مشتریان» بدون هیچ استثنا.
15. **تست تعاملی فیلترها و جستجو (`test_15_streamlit_apptest_filters_and_search`):** تغییر فیلتر استان و جستجوی شناسه مشتری `15634602` در `AppTest` بدون خطا.

### ب) اعتبارسنجی بصری (`assets/preview.png`)
* اجرای زندهٔ اپ روی پورت `8502` و ثبت اسکرین‌شات تمام‌صفحه با مرورگر Headless Chromium (Playwright) در ابعاد `1600 × 1800` پیکسل.
* بازبینی چشمی تصویر خروجی: فونت فارسی `Vazirmatn FD`، چیدمان راست‌چین، کارت‌های KPI، عدم بریدگی برچسب‌های بیرونی نمودارها (`cliponaxis=False`) و جهت صحیح محورهای Plotly تأیید شدند.

---

## ۲. موارد تست‌نشده در این محیط (Not Tested — Honest Disclosure ⚠️)

1. **اجرای مستقیم کدهای DAX در موتور VertiPaq:**
   - فرمول‌های فایل `model/measures.dax` بر اساس سینتکس استاندارد Power BI نوشته شده‌اند، اما از آنجا که محیط فعلی لینوکس است و Power BI Desktop در آن اجرا نمی‌شود، این فرمول‌ها داخل موتور VertiPaq کامپایل و اجرا نشده‌اند.
2. **رندر نهایی فایل تم (`report/theme.json`) در Power BI Desktop:**
   - ساختار JSON تم معتبر است، اما ظاهر نهایی ویژوال‌های بومی Power BI Desktop پس از ایمپورت تم نیازمند بازبینی در محیط ویندوز است.
3. **آزمون عملی امنیت سطح ردیف (RLS View-as):**
   - عبارات فیلتر استانی RLS در `model/MODEL.md` و `report/POWER_BI_BUILD_GUIDE.md` مستند شده‌اند، اما تست عملی `Modeling → View as` در محیط کارفرما / Power BI Service انجام نشده است.
4. **تعمیم‌پذیری اقتصادی به ایران:**
   - اعداد و الگوهای جغرافیایی (مانند نرخ ریزش ۳۲٫۴۴٪ در «اصفهان=آلمان») ویژگی دیتاست اروپایی منبع هستند و به اقتصاد واقعی ایران یا بانک‌های ایرانی قابل تعمیم نیستند.
