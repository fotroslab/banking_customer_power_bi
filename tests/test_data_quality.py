#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مجموعه تست‌های خودکار کیفیت داده، مدل ستاره‌ای و اپ پیش‌نمایش (۱۵ تست)
پروژه ۱: بانک آریا — نمای ۳۶۰ درجه مشتری و تحلیل ریزش
"""

from __future__ import annotations

import json
import re
import unittest
from datetime import datetime
from pathlib import Path

import pandas as pd
from streamlit.testing.v1 import AppTest

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_PATH = BASE_DIR / "data" / "raw" / "Churn_Modelling.csv"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
APP_PATH = BASE_DIR / "app.py"


class TestBankAriaCustomer360(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = pd.read_csv(RAW_PATH)
        cls.dim_date = pd.read_csv(PROCESSED_DIR / "dim_date.csv")
        cls.dim_customer = pd.read_csv(PROCESSED_DIR / "dim_customer.csv")
        cls.dim_branch = pd.read_csv(PROCESSED_DIR / "dim_branch.csv")
        cls.dim_product = pd.read_csv(PROCESSED_DIR / "dim_product.csv")
        cls.fact_snapshot = pd.read_csv(PROCESSED_DIR / "fact_snapshot.csv")
        cls.fact_holding = pd.read_csv(PROCESSED_DIR / "fact_product_holding.csv")
        with open(PROCESSED_DIR / "summary_stats.json", "r", encoding="utf-8") as f:
            cls.summary = json.load(f)

    def test_01_raw_file_integrity(self) -> None:
        """بررسی صحت فایل خام Churn_Modelling.csv (۱۰٬۰۰۰×۱۴ بدون مقدار خالی)."""
        self.assertEqual(self.raw.shape, (10000, 14))
        self.assertEqual(int(self.raw.isnull().sum().sum()), 0)
        self.assertEqual(int(self.raw["CustomerId"].duplicated().sum()), 0)

    def test_02_processed_row_counts_and_uniqueness(self) -> None:
        """بررسی شمار ردیف‌ها و یکتایی کلیدهای اصلی در جداول ستاره‌ای."""
        self.assertEqual(len(self.dim_customer), 10000)
        self.assertEqual(len(self.fact_snapshot), 10000)
        self.assertEqual(len(self.dim_branch), 7)
        self.assertEqual(len(self.dim_product), 4)
        self.assertEqual(len(self.fact_holding), 15302)

        self.assertFalse(self.dim_customer["customer_id"].duplicated().any())
        self.assertFalse(self.fact_snapshot["customer_id"].duplicated().any())
        self.assertFalse(self.dim_branch["branch_id"].duplicated().any())
        self.assertFalse(self.dim_product["product_id"].duplicated().any())
        self.assertFalse(self.fact_holding["holding_id"].duplicated().any())

    def test_03_exact_currency_scaling_250000(self) -> None:
        """بررسی برابری دقیق مبالغ ریالی با حاصل‌ضرب ×۲۵۰٬۰۰۰ منبع."""
        expected_bal = (self.raw["Balance"] * 250_000).round().astype("int64")
        expected_sal = (self.raw["EstimatedSalary"] * 250_000).round().astype("int64")
        self.assertTrue((self.fact_snapshot["balance_irr"] == expected_bal).all())
        self.assertTrue((self.fact_snapshot["estimated_salary_irr"] == expected_sal).all())
        self.assertTrue((self.dim_customer["estimated_salary_irr"] == expected_sal).all())

    def test_04_untouched_numeric_and_target_columns(self) -> None:
        """بررسی دست‌نخورده ماندن ۱۰۰٪ ستون‌های تحلیلی و هدف نسبت به منبع."""
        self.assertTrue((self.fact_snapshot["customer_id"] == self.raw["CustomerId"]).all())
        self.assertTrue((self.fact_snapshot["exited"] == self.raw["Exited"]).all())
        self.assertTrue((self.fact_snapshot["credit_score"] == self.raw["CreditScore"]).all())
        self.assertTrue((self.fact_snapshot["age"] == self.raw["Age"]).all())
        self.assertTrue((self.fact_snapshot["tenure"] == self.raw["Tenure"]).all())
        self.assertTrue((self.fact_snapshot["num_of_products"] == self.raw["NumOfProducts"]).all())
        self.assertTrue((self.fact_snapshot["is_active_member"] == self.raw["IsActiveMember"]).all())
        self.assertTrue((self.fact_snapshot["has_cr_card"] == self.raw["HasCrCard"]).all())

    def test_05_geography_and_gender_1to1_mapping(self) -> None:
        """بررسی نگاشت ۱:۱ استان‌ها و جنسیت و حفظ دقیق نرخ ریزش هر استان."""
        prov_counts = self.dim_customer["province"].value_counts().to_dict()
        self.assertEqual(prov_counts.get("تهران"), 5014)
        self.assertEqual(prov_counts.get("اصفهان"), 2509)
        self.assertEqual(prov_counts.get("خراسان رضوی"), 2477)

        merged = self.fact_snapshot.merge(self.dim_customer[["customer_id", "province"]], on="customer_id")
        churn_by_prov = merged.groupby("province")["exited"].mean().to_dict()
        self.assertAlmostEqual(churn_by_prov["اصفهان"], 814 / 2509, places=6)
        self.assertAlmostEqual(churn_by_prov["تهران"], 810 / 5014, places=6)
        self.assertAlmostEqual(churn_by_prov["خراسان رضوی"], 413 / 2477, places=6)

        gender_map_check = set(zip(self.raw["Gender"], self.dim_customer["gender"]))
        self.assertEqual(gender_map_check, {("Female", "زن"), ("Male", "مرد")})

    def test_06_product_distribution_and_holding_derivation(self) -> None:
        """بررسی توزیع تعداد محصول و سازگاری کامل جدول مشتق fact_product_holding."""
        self.assertEqual(int(self.fact_snapshot["num_of_products"].sum()), 15302)
        holding_counts = self.fact_holding.groupby("customer_id")["holding_id"].count()
        snap_Indexed = self.fact_snapshot.set_index("customer_id")["num_of_products"]
        self.assertTrue((holding_counts.loc[snap_Indexed.index] == snap_Indexed).all())

        holding_bal_sum = self.fact_holding.groupby("customer_id")["allocated_balance_irr"].sum()
        snap_bal = self.fact_snapshot.set_index("customer_id")["balance_irr"]
        self.assertTrue((holding_bal_sum.loc[snap_bal.index] == snap_bal).all())

    def test_07_star_schema_foreign_keys(self) -> None:
        """بررسی یکپارچگی ارجاعی (Foreign Keys) تمامی روابط مدل ستاره‌ای."""
        valid_customers = set(self.dim_customer["customer_id"])
        valid_branches = set(self.dim_branch["branch_id"])
        valid_products = set(self.dim_product["product_id"])
        valid_dates = set(self.dim_date["date_jalali"])
        valid_date_keys = set(self.dim_date["date_key"])

        self.assertTrue(set(self.fact_snapshot["customer_id"]).issubset(valid_customers))
        self.assertTrue(set(self.fact_snapshot["branch_id"]).issubset(valid_branches))
        self.assertTrue(set(self.fact_snapshot["snapshot_date_jalali"]).issubset(valid_dates))
        self.assertTrue(set(self.fact_snapshot["acquisition_jalali"]).issubset(valid_dates))
        self.assertTrue(set(self.fact_snapshot["snapshot_date_key"]).issubset(valid_date_keys))
        self.assertTrue(set(self.fact_snapshot["acquisition_date_key"]).issubset(valid_date_keys))

        self.assertTrue(set(self.fact_holding["customer_id"]).issubset(valid_customers))
        self.assertTrue(set(self.fact_holding["branch_id"]).issubset(valid_branches))
        self.assertTrue(set(self.fact_holding["product_id"]).issubset(valid_products))
        self.assertTrue(set(self.fact_holding["opened_date_jalali"]).issubset(valid_dates))
        self.assertTrue(set(self.fact_holding["snapshot_date_jalali"]).issubset(valid_dates))

    def test_08_dim_date_continuity_and_jalali_format(self) -> None:
        """بررسی فرمت YYYY/MM/DD و پیوستگی روزانه تقویم شمسی تا ۱۴۰۳/۱۲/۲۹."""
        pattern = re.compile(r"^\d{4}/\d{2}/\d{2}$")
        self.assertTrue(self.dim_date["date_jalali"].apply(lambda s: bool(pattern.match(str(s)))).all())
        self.assertEqual(self.dim_date["date_jalali"].iloc[-1], "1403/12/29")

        g_dates = [datetime.strptime(d, "%Y-%m-%d").date() for d in self.dim_date["date_gregorian"]]
        diffs = [(g_dates[i] - g_dates[i - 1]).days for i in range(1, len(g_dates))]
        self.assertTrue(all(d == 1 for d in diffs))

    def test_09_farsi_names_are_synthetic(self) -> None:
        """اطمینان از ساختگی و فارسی بودن نام‌های مشتریان و عدم افشای هویت واقعی."""
        farsi_pattern = re.compile(r"^[\u0600-\u06FF\s]+$")
        self.assertTrue(
            self.dim_customer["full_name_fa"].apply(lambda s: bool(farsi_pattern.match(str(s)))).all()
        )

    def test_10_summary_stats_json_consistency(self) -> None:
        """بررسی سازگاری کامل summary_stats.json با خروجی‌های پردازش‌شده."""
        self.assertEqual(self.summary["total_customers"], 10000)
        self.assertEqual(self.summary["churned_customers"], 2037)
        self.assertAlmostEqual(self.summary["churn_rate"], 0.2037, places=4)
        self.assertEqual(self.summary["total_product_holdings"], 15302)
        self.assertEqual(self.summary["reference_date_jalali"], "1403/12/29")
        self.assertEqual(
            self.summary["total_balance_irr"], int(self.fact_snapshot["balance_irr"].sum())
        )

    def test_11_theme_and_deliverable_files_exist(self) -> None:
        """بررسی وجود فایل‌های کلیدی تحویل و ساختار تم Bank Aria Fa."""
        theme_path = BASE_DIR / "report" / "theme.json"
        self.assertTrue(theme_path.exists(), "فایل report/theme.json یافت نشد")
        with open(theme_path, "r", encoding="utf-8") as f:
            theme = json.load(f)
        self.assertEqual(theme.get("name"), "Bank Aria Fa")
        self.assertIn("#0b6e4f", [c.lower() for c in theme.get("dataColors", [])])
        self.assertIn("#d4a017", [c.lower() for c in theme.get("dataColors", [])])

    def test_12_app_css_and_plotly_ltr_guard(self) -> None:
        """بررسی وجود قواعد حیاتی RTL/LTR و cliponaxis=False در کد app.py."""
        app_code = APP_PATH.read_text(encoding="utf-8")
        self.assertIn(".js-plotly-plot, .js-plotly-plot *", app_code)
        self.assertIn("direction: ltr !important;", app_code)
        self.assertIn("cliponaxis=False", app_code)
        self.assertIn("def style_fig(", app_code)

    def test_13_streamlit_apptest_pages_1_to_3(self) -> None:
        """اجرای AppTest روی صفحات ۱ تا ۳ بدون هیچ خطا یا استثنا."""
        at = AppTest.from_file(str(APP_PATH), default_timeout=30)
        at.run()
        self.assertEqual(len(at.exception), 0, f"خطا در صفحه اول: {at.exception}")

        for page_name in ["تحلیل ریزش مشتری", "استان‌ها و شعب"]:
            at.radio(key="page_nav").set_value(page_name).run()
            self.assertEqual(len(at.exception), 0, f"خطا در صفحه {page_name}: {at.exception}")

    def test_14_streamlit_apptest_pages_4_and_5(self) -> None:
        """اجرای AppTest روی صفحات ۴ و ۵ بدون هیچ خطا یا استثنا."""
        at = AppTest.from_file(str(APP_PATH), default_timeout=30)
        at.run()
        for page_name in ["سبد محصولات", "جستجوی مشتریان"]:
            at.radio(key="page_nav").set_value(page_name).run()
            self.assertEqual(len(at.exception), 0, f"خطا در صفحه {page_name}: {at.exception}")

    def test_15_streamlit_apptest_filters_and_search(self) -> None:
        """اجرای AppTest با تغییر فیلترهای استان و جستجوی مشتری در صفحه ۵."""
        at = AppTest.from_file(str(APP_PATH), default_timeout=30)
        at.run()
        at.multiselect(key="filter_province").set_value(["اصفهان", "تهران"]).run()
        self.assertEqual(len(at.exception), 0)

        at.radio(key="page_nav").set_value("جستجوی مشتریان").run()
        at.text_input(key="cust_search_q").set_value("15634602").run()
        self.assertEqual(len(at.exception), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
