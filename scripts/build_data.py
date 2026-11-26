#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
پایپ‌لاین بازتولید داده — پروژه ۱: بانک آریا (نمای ۳۶۰ درجه مشتری و تحلیل ریزش)
تبدیل قطعی (Deterministic) دیتاست عمومی Churn_Modelling.csv به مدل ستاره‌ای بومی‌سازی‌شده (فارسی/شمسی/ریال نمایشی)
بدون تغییر در سیگنال‌های آماری، توزیع‌ها و هم‌بستگی‌های اصلی.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

import jdatetime
import numpy as np
import pandas as pd

SEED = 42
SCALE_FACTOR_IRR = 250_000
REF_JALALI_STR = "1403/12/29"
REF_JALALI_DATE = jdatetime.date(1403, 12, 29)
START_JALALI_DATE = jdatetime.date(1392, 1, 1)

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_PATH = BASE_DIR / "data" / "raw" / "Churn_Modelling.csv"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

JALALI_MONTH_NAMES = {
    1: "فروردین",
    2: "اردیبهشت",
    3: "خرداد",
    4: "تیر",
    5: "مرداد",
    6: "شهریور",
    7: "مهر",
    8: "آبان",
    9: "آذر",
    10: "دی",
    11: "بهمن",
    12: "اسفند",
}

# در jdatetime.date.weekday(): شنبه=0 ... جمعه=6
JALALI_WEEKDAY_NAMES = {
    0: "شنبه",
    1: "یکشنبه",
    2: "دوشنبه",
    3: "سه‌شنبه",
    4: "چهارشنبه",
    5: "پنجشنبه",
    6: "جمعه",
}

GEOGRAPHY_MAP = {
    "France": "تهران",
    "Germany": "اصفهان",
    "Spain": "خراسان رضوی",
}

GENDER_MAP = {
    "Female": "زن",
    "Male": "مرد",
}

FEMALE_FIRST_NAMES = [
    "سارا", "مریم", "نگار", "زهرا", "فاطمه", "نیلوفر", "الهام", "پریسا",
    "مینا", "بهاره", "شیرین", "نازنین", "مهسا", "غزاله", "آرزو", "ریحانه",
    "سمانه", "هدی", "یاسمن", "نرگس", "ستاره", "یلدا", "فرزانه", "سپیده",
    "کیانا", "باران", "ترانه", "رویا", "سمیرا", "شیما", "آناهیتا", "مرجان",
]

MALE_FIRST_NAMES = [
    "آرش", "علی", "محمد", "حسین", "رضا", "مهدی", "امیر", "سعید",
    "کاوه", "پویا", "بهرام", "فرهاد", "احسان", "امید", "بابک", "سهراب",
    "کیوان", "دارا", "پارسا", "نیما", "سینا", "شایان", "عرفان", "پیمان",
    "حمید", "جواد", "مسعود", "میلاد", "فرزاد", "مازیار", "کوروش", "اشکان",
]

LAST_NAMES = [
    "محمدی", "حسینی", "رضایی", "احمدی", "کریمی", "موسوی", "جعفری", "صادقی",
    "حیدری", "مرادی", "ابراهیمی", "رحیمی", "هاشمی", "قاسمی", "اکبری", "زارعی",
    "کاظمی", "سلیمانی", "طاهری", "نجفی", "تبریزی", "شریفی", "منصوری", "فرهادی",
    "بهرامی", "نوری", "پارسایی", "فتحی", "عزیزی", "کمالی", "رستمی", "صالحی",
    "مهدوی", "توکلی", "ملکی", "دهقانی", "باقرپور", "خلج", "نعمتی", "یزدانی",
]

BRANCHES = [
    {
        "branch_id": "BR-101",
        "branch_code": 101,
        "branch_name": "شعبه مرکزی تهران",
        "province": "تهران",
        "source_geography": "France",
        "city": "تهران",
        "branch_tier": "درجه ممتاز",
        "region_manager": "حوزه شمال و مرکز تهران",
    },
    {
        "branch_id": "BR-102",
        "branch_code": 102,
        "branch_name": "شعبه ونک تهران",
        "province": "تهران",
        "source_geography": "France",
        "city": "تهران",
        "branch_tier": "درجه یک",
        "region_manager": "حوزه شمال و مرکز تهران",
    },
    {
        "branch_id": "BR-103",
        "branch_code": 103,
        "branch_name": "شعبه سعادت‌آباد تهران",
        "province": "تهران",
        "source_geography": "France",
        "city": "تهران",
        "branch_tier": "درجه یک",
        "region_manager": "حوزه غرب تهران",
    },
    {
        "branch_id": "BR-201",
        "branch_code": 201,
        "branch_name": "شعبه چهارباغ اصفهان",
        "province": "اصفهان",
        "source_geography": "Germany",
        "city": "اصفهان",
        "branch_tier": "درجه ممتاز",
        "region_manager": "حوزه مرکزی اصفهان",
    },
    {
        "branch_id": "BR-202",
        "branch_code": 202,
        "branch_name": "شعبه نقش‌جهان اصفهان",
        "province": "اصفهان",
        "source_geography": "Germany",
        "city": "اصفهان",
        "branch_tier": "درجه یک",
        "region_manager": "حوزه مرکزی اصفهان",
    },
    {
        "branch_id": "BR-301",
        "branch_code": 301,
        "branch_name": "شعبه سجاد مشهد",
        "province": "خراسان رضوی",
        "source_geography": "Spain",
        "city": "مشهد",
        "branch_tier": "درجه ممتاز",
        "region_manager": "حوزه شمال‌شرق",
    },
    {
        "branch_id": "BR-302",
        "branch_code": 302,
        "branch_name": "شعبه احمدآباد مشهد",
        "province": "خراسان رضوی",
        "source_geography": "Spain",
        "city": "مشهد",
        "branch_tier": "درجه یک",
        "region_manager": "حوزه شمال‌شرق",
    },
]

PRODUCTS = [
    {
        "product_id": "PRD-01",
        "product_code": 1,
        "product_name": "سپرده قرض‌الحسنه جاری و کارت نقدی",
        "product_category": "سپرده‌های دیداری و پرداخت",
        "is_credit_product": 0,
        "annual_rate_pct": 0.0,
        "description": "حساب تراکنشی روزمره متصل به کارت بانکی و همراه بانک آریا",
    },
    {
        "product_id": "PRD-02",
        "product_code": 2,
        "product_name": "سپرده سرمایه‌گذاری کوتاه‌مدت روزشمار",
        "product_category": "سپرده‌های سرمایه‌گذاری",
        "is_credit_product": 0,
        "annual_rate_pct": 12.0,
        "description": "سپرده سودده کوتاه‌مدت با قابلیت واریز و برداشت آنی",
    },
    {
        "product_id": "PRD-03",
        "product_code": 3,
        "product_name": "کارت اعتباری و تسهیلات مرابحه آریا",
        "product_category": "تسهیلات و اعتبارات",
        "is_credit_product": 1,
        "annual_rate_pct": 23.0,
        "description": "خط اعتباری خرید کالا و خدمات با بازپرداخت اقساطی",
    },
    {
        "product_id": "PRD-04",
        "product_code": 4,
        "product_name": "سپرده سرمایه‌گذاری بلندمدت ویژه",
        "product_category": "مدیریت ثروت و سرمایه‌گذاری",
        "is_credit_product": 0,
        "annual_rate_pct": 22.5,
        "description": "سپرده بلندمدت یک‌ساله و دوساله ویژه مشتریان با مانده بالا",
    },
]


def build_dim_date() -> pd.DataFrame:
    """ساخت جدول تقویم شمسی پیوسته از ۱۳۹۲/۰۱/۰۱ تا ۱۴۰۳/۱۲/۲۹."""
    rows = []
    cur = START_JALALI_DATE
    while cur <= REF_JALALI_DATE:
        g_date = cur.togregorian()
        y, m, d = cur.year, cur.month, cur.day
        wd = cur.weekday()  # 0=Shanbeh .. 6=Jomeh
        quarter = (m - 1) // 3 + 1
        rows.append(
            {
                "date_key": int(f"{y:04d}{m:02d}{d:02d}"),
                "date_jalali": f"{y:04d}/{m:02d}/{d:02d}",
                "date_gregorian": g_date.strftime("%Y-%m-%d"),
                "jalali_year": y,
                "jalali_quarter": quarter,
                "jalali_quarter_name": f"فصل {quarter}",
                "jalali_month": m,
                "jalali_month_name": JALALI_MONTH_NAMES[m],
                "jalali_year_month": f"{y:04d}/{m:02d}",
                "jalali_day": d,
                "day_of_week_num": wd + 1,
                "day_of_week_name": JALALI_WEEKDAY_NAMES[wd],
                "is_weekend": 1 if wd in (5, 6) else 0,
            }
        )
        cur = cur + jdatetime.timedelta(days=1)
    return pd.DataFrame(rows)


def get_age_group(age: int) -> str:
    if age < 30:
        return "زیر ۳۰ سال"
    elif age < 40:
        return "۳۰ تا ۳۹ سال"
    elif age < 50:
        return "۴۰ تا ۴۹ سال"
    elif age < 60:
        return "۵۰ تا ۵۹ سال"
    return "۶۰ سال به بالا"


def get_tenure_group(tenure: int) -> str:
    if tenure <= 1:
        return "کمتر از ۲ سال"
    elif tenure <= 5:
        return "۲ تا ۵ سال"
    elif tenure <= 8:
        return "۶ تا ۸ سال"
    return "بیش از ۸ سال"


def get_credit_band(score: int) -> str:
    if score < 580:
        return "ضعیف (<۵۸۰)"
    elif score < 670:
        return "متوسط (۵۸۰-۶۶۹)"
    elif score < 740:
        return "خوب (۶۷۰-۷۳۹)"
    elif score < 800:
        return "عالی (۷۴۰-۷۹۹)"
    return "ممتاز (۸۰۰+)"


def compute_acquisition_jalali(customer_id: int, tenure: int) -> tuple[jdatetime.date, str, int]:
    """
    محاسبه قطعی تاریخ عضویت شمسی بر اساس تاریخ مرجع ۱۴۰۳/۱۲/۲۹، سنوات حضور (Tenure)
    و جابه‌جایی (jitter) روز/ماه با seed ثابت مبتنی بر customer_id.
    """
    rng = random.Random(SEED + int(customer_id))
    base_year = REF_JALALI_DATE.year - int(tenure)
    if tenure == 0:
        # عضویت در همان سال ۱۴۰۳
        month = rng.randint(1, 12)
        max_day = 30 if month <= 6 else (29 if month == 12 else 30)
        day = rng.randint(1, max_day)
    else:
        month = rng.randint(1, 12)
        max_day = 31 if month <= 6 else (29 if month == 12 else 30)
        day = rng.randint(1, max_day)
    acq_date = jdatetime.date(base_year, month, day)
    if acq_date > REF_JALALI_DATE:
        acq_date = REF_JALALI_DATE
    acq_str = f"{acq_date.year:04d}/{acq_date.month:02d}/{acq_date.day:02d}"
    acq_key = int(f"{acq_date.year:04d}{acq_date.month:02d}{acq_date.day:02d}")
    return acq_date, acq_str, acq_key


def assign_branch_id(customer_id: int, province: str) -> str:
    """تخصیص قطعی شعبه در همان استان بر اساس customer_id."""
    if province == "تهران":
        # نسبت قطعی: ۴۵٪ شعبه مرکزی، ۳۰٪ ونک، ۲۵٪ سعادت‌آباد
        mod = int(customer_id) % 20
        if mod < 9:
            return "BR-101"
        elif mod < 15:
            return "BR-102"
        return "BR-103"
    elif province == "اصفهان":
        mod = int(customer_id) % 10
        return "BR-201" if mod < 6 else "BR-202"
    else:  # خراسان رضوی
        mod = int(customer_id) % 10
        return "BR-301" if mod < 6 else "BR-302"


def generate_farsi_name(customer_id: int, gender_raw: str) -> tuple[str, str, str]:
    """ساخت نام کامل فارسی ساختگی به‌صورت قطعی از روی customer_id و جنسیت."""
    cid = int(customer_id)
    if gender_raw == "Female":
        first = FEMALE_FIRST_NAMES[cid % len(FEMALE_FIRST_NAMES)]
    else:
        first = MALE_FIRST_NAMES[cid % len(MALE_FIRST_NAMES)]
    last = LAST_NAMES[(cid // 37) % len(LAST_NAMES)]
    return first, last, f"{first} {last}"


def select_customer_products(customer_id: int, num_products: int, has_cr_card: int, balance_irr: int) -> list[str]:
    """
    انتخاب قطعی لیست محصولات مشتری به تعداد دقیق NumOfProducts.
    مجموع ردیف‌ها برای کل مشتریان دقیقاً برابر مجموع NumOfProducts (۱۵٬۳۰۲ ردیف) خواهد بود.
    """
    if num_products == 4:
        return ["PRD-01", "PRD-02", "PRD-03", "PRD-04"]

    selected = ["PRD-01"]  # حساب پایه
    remaining_candidates = []
    if has_cr_card == 1:
        remaining_candidates.append("PRD-03")
    if balance_irr > 0:
        remaining_candidates.extend(["PRD-02", "PRD-04"])
    for p in ["PRD-02", "PRD-03", "PRD-04"]:
        if p not in remaining_candidates:
            remaining_candidates.append(p)

    # چرخش قطعی بر اساس customer_id برای تنوع واقع‌گرایانه
    shift = (int(customer_id) // 13) % len(remaining_candidates)
    ordered = remaining_candidates[shift:] + remaining_candidates[:shift]
    for p in ordered:
        if len(selected) < num_products and p not in selected:
            selected.append(p)
    return sorted(selected)


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    raw_df = pd.read_csv(RAW_PATH)

    # ۱) ساخت جداول ابعاد ثابت
    dim_date = build_dim_date()
    dim_branch = pd.DataFrame(BRANCHES)
    dim_product = pd.DataFrame(PRODUCTS)

    # ۲) ساخت dim_customer، fact_snapshot و fact_product_holding
    customer_rows = []
    snapshot_rows = []
    holding_rows = []
    holding_id_counter = 1

    ref_date_key = 14031229

    for row in raw_df.itertuples(index=False):
        cid = int(row.CustomerId)
        row_num = int(row.RowNumber)
        geo_raw = str(row.Geography)
        province = GEOGRAPHY_MAP[geo_raw]
        gender_raw = str(row.Gender)
        gender_fa = GENDER_MAP[gender_raw]
        age = int(row.Age)
        tenure = int(row.Tenure)
        credit_score = int(row.CreditScore)
        has_cr = int(row.HasCrCard)
        is_active = int(row.IsActiveMember)
        exited = int(row.Exited)
        num_prod = int(row.NumOfProducts)

        balance_raw = float(row.Balance)
        salary_raw = float(row.EstimatedSalary)
        balance_irr = int(round(balance_raw * SCALE_FACTOR_IRR))
        salary_irr = int(round(salary_raw * SCALE_FACTOR_IRR))

        first_fa, last_fa, full_name_fa = generate_farsi_name(cid, gender_raw)
        branch_id = assign_branch_id(cid, province)
        acq_date, acq_jalali_str, acq_date_key = compute_acquisition_jalali(cid, tenure)

        customer_rows.append(
            {
                "customer_id": cid,
                "row_number": row_num,
                "full_name_fa": full_name_fa,
                "first_name_fa": first_fa,
                "last_name_fa": last_fa,
                "original_surname": str(row.Surname),
                "gender": gender_fa,
                "gender_raw": gender_raw,
                "age": age,
                "age_group": get_age_group(age),
                "province": province,
                "source_geography": geo_raw,
                "branch_id": branch_id,
                "tenure_years": tenure,
                "tenure_group": get_tenure_group(tenure),
                "acquisition_jalali": acq_jalali_str,
                "acquisition_date_key": acq_date_key,
                "credit_score": credit_score,
                "credit_band": get_credit_band(credit_score),
                "has_credit_card": has_cr,
                "has_credit_card_label": "دارای کارت اعتباری" if has_cr == 1 else "فاقد کارت اعتباری",
                "is_active_member": is_active,
                "activity_status_label": "فعال" if is_active == 1 else "غیرفعال",
                "estimated_salary_irr": salary_irr,
            }
        )

        snapshot_rows.append(
            {
                "snapshot_id": row_num,
                "customer_id": cid,
                "branch_id": branch_id,
                "snapshot_date_jalali": REF_JALALI_STR,
                "snapshot_date_key": ref_date_key,
                "acquisition_jalali": acq_jalali_str,
                "acquisition_date_key": acq_date_key,
                "credit_score": credit_score,
                "age": age,
                "tenure": tenure,
                "balance_eur_raw": balance_raw,
                "balance_irr": balance_irr,
                "is_zero_balance": 1 if balance_irr == 0 else 0,
                "estimated_salary_eur_raw": salary_raw,
                "estimated_salary_irr": salary_irr,
                "num_of_products": num_prod,
                "has_cr_card": has_cr,
                "is_active_member": is_active,
                "exited": exited,
                "churn_status_label": "ریزش‌کرده" if exited == 1 else "مانده",
            }
        )

        # ساخت ردیف‌های fact_product_holding (مشتق از NumOfProducts با seed ثابت)
        held_products = select_customer_products(cid, num_prod, has_cr, balance_irr)
        rng_hold = random.Random(SEED * 100 + cid)
        days_span = max(0, (REF_JALALI_DATE.togregorian() - acq_date.togregorian()).days)

        # تخصیص مانده بین محصولات مشتری به‌گونه‌ای که جمع آن دقیقاً برابر balance_irr باشد
        if balance_irr == 0:
            allocations = [0] * num_prod
        elif num_prod == 1:
            allocations = [balance_irr]
        else:
            weights = [rng_hold.uniform(0.2, 1.0) for _ in range(num_prod)]
            total_w = sum(weights)
            allocations = [int(round(balance_irr * (w / total_w))) for w in weights[:-1]]
            allocations.append(balance_irr - sum(allocations))

        for seq_idx, (prod_id, alloc_irr) in enumerate(zip(held_products, allocations), start=1):
            if seq_idx == 1 or days_span == 0:
                opened_date = acq_date
            else:
                offset_days = rng_hold.randint(0, days_span)
                opened_date = acq_date + jdatetime.timedelta(days=offset_days)
                if opened_date > REF_JALALI_DATE:
                    opened_date = REF_JALALI_DATE
            opened_str = f"{opened_date.year:04d}/{opened_date.month:02d}/{opened_date.day:02d}"
            opened_key = int(f"{opened_date.year:04d}{opened_date.month:02d}{opened_date.day:02d}")

            holding_rows.append(
                {
                    "holding_id": holding_id_counter,
                    "customer_id": cid,
                    "branch_id": branch_id,
                    "product_id": prod_id,
                    "opened_date_jalali": opened_str,
                    "opened_date_key": opened_key,
                    "snapshot_date_jalali": REF_JALALI_STR,
                    "product_sequence": seq_idx,
                    "allocated_balance_irr": alloc_irr,
                    "holding_status": "بسته/ریزش" if exited == 1 else "فعال",
                    "is_synthetic_derivation": 1,
                }
            )
            holding_id_counter += 1

    dim_customer = pd.DataFrame(customer_rows)
    fact_snapshot = pd.DataFrame(snapshot_rows)
    fact_product_holding = pd.DataFrame(holding_rows)

    # ذخیره جداول پردازش‌شده
    dim_date.to_csv(PROCESSED_DIR / "dim_date.csv", index=False, encoding="utf-8")
    dim_branch.to_csv(PROCESSED_DIR / "dim_branch.csv", index=False, encoding="utf-8")
    dim_product.to_csv(PROCESSED_DIR / "dim_product.csv", index=False, encoding="utf-8")
    dim_customer.to_csv(PROCESSED_DIR / "dim_customer.csv", index=False, encoding="utf-8")
    fact_snapshot.to_csv(PROCESSED_DIR / "fact_snapshot.csv", index=False, encoding="utf-8")
    fact_product_holding.to_csv(PROCESSED_DIR / "fact_product_holding.csv", index=False, encoding="utf-8")

    # محاسبه و ذخیره summary_stats.json
    merged = fact_snapshot.merge(
        dim_customer[["customer_id", "province", "source_geography", "gender", "age_group"]],
        on="customer_id",
        how="left",
    )

    province_stats = {}
    for prov, grp in merged.groupby("province"):
        province_stats[prov] = {
            "source_geography": str(grp["source_geography"].iloc[0]),
            "customer_count": int(len(grp)),
            "churned_count": int(grp["exited"].sum()),
            "churn_rate": round(float(grp["exited"].mean()), 6),
            "churn_rate_pct": round(float(grp["exited"].mean() * 100), 2),
            "total_balance_irr": int(grp["balance_irr"].sum()),
            "avg_balance_irr": round(float(grp["balance_irr"].mean()), 2),
            "active_rate_pct": round(float(grp["is_active_member"].mean() * 100), 2),
        }

    product_count_stats = {}
    for nprod, grp in merged.groupby("num_of_products"):
        product_count_stats[str(int(nprod))] = {
            "customer_count": int(len(grp)),
            "churned_count": int(grp["exited"].sum()),
            "churn_rate": round(float(grp["exited"].mean()), 6),
            "churn_rate_pct": round(float(grp["exited"].mean() * 100), 2),
            "avg_balance_irr": round(float(grp["balance_irr"].mean()), 2),
        }

    activity_stats = {}
    for act_val, grp in merged.groupby("is_active_member"):
        label = "فعال" if int(act_val) == 1 else "غیرفعال"
        activity_stats[label] = {
            "is_active_member": int(act_val),
            "customer_count": int(len(grp)),
            "churned_count": int(grp["exited"].sum()),
            "churn_rate": round(float(grp["exited"].mean()), 6),
            "churn_rate_pct": round(float(grp["exited"].mean() * 100), 2),
        }

    summary_stats = {
        "project_name": "بانک آریا — نمای ۳۶۰ درجه مشتری و تحلیل ریزش",
        "reference_date_jalali": REF_JALALI_STR,
        "scale_factor_irr": SCALE_FACTOR_IRR,
        "total_customers": int(len(fact_snapshot)),
        "churned_customers": int(fact_snapshot["exited"].sum()),
        "retained_customers": int((fact_snapshot["exited"] == 0).sum()),
        "churn_rate": round(float(fact_snapshot["exited"].mean()), 4),
        "churn_rate_pct": round(float(fact_snapshot["exited"].mean() * 100), 2),
        "retention_rate_pct": round(float((1.0 - fact_snapshot["exited"].mean()) * 100), 2),
        "total_balance_irr": int(fact_snapshot["balance_irr"].sum()),
        "avg_balance_irr": round(float(fact_snapshot["balance_irr"].mean()), 2),
        "total_estimated_salary_irr": int(fact_snapshot["estimated_salary_irr"].sum()),
        "avg_estimated_salary_irr": round(float(fact_snapshot["estimated_salary_irr"].mean()), 2),
        "avg_credit_score": round(float(fact_snapshot["credit_score"].mean()), 2),
        "avg_age": round(float(fact_snapshot["age"].mean()), 2),
        "avg_tenure": round(float(fact_snapshot["tenure"].mean()), 2),
        "avg_products_per_customer": round(float(fact_snapshot["num_of_products"].mean()), 4),
        "total_product_holdings": int(len(fact_product_holding)),
        "active_member_share": round(float(fact_snapshot["is_active_member"].mean()), 4),
        "active_member_share_pct": round(float(fact_snapshot["is_active_member"].mean() * 100), 2),
        "credit_card_holder_share_pct": round(float(fact_snapshot["has_cr_card"].mean() * 100), 2),
        "zero_balance_count": int(fact_snapshot["is_zero_balance"].sum()),
        "zero_balance_share": round(float(fact_snapshot["is_zero_balance"].mean()), 4),
        "zero_balance_share_pct": round(float(fact_snapshot["is_zero_balance"].mean() * 100), 2),
        "by_province": province_stats,
        "by_num_of_products": product_count_stats,
        "by_activity_status": activity_stats,
        "row_counts": {
            "dim_date": int(len(dim_date)),
            "dim_customer": int(len(dim_customer)),
            "dim_branch": int(len(dim_branch)),
            "dim_product": int(len(dim_product)),
            "fact_snapshot": int(len(fact_snapshot)),
            "fact_product_holding": int(len(fact_product_holding)),
        },
        "honesty_notes": {
            "currency_scaling": "مبالغ ریالی صرفاً حاصل ضرب نمایشی ×۲۵۰٬۰۰۰ در مقادیر منبع هستند و ریال واقعی بانک نیستند.",
            "geography_mapping": "نگاشت France→تهران، Germany→اصفهان و Spain→خراسان رضوی صرفاً برچسب‌گذاری ۱:۱ است؛ نرخ ریزش ۳۲٫۴۴٪ اصفهان ویژگی دادهٔ آلمان در منبع اصلی است، نه واقعیت اقتصادی اصفهان.",
            "product_holding_derivation": "جدول fact_product_holding با seed ثابت از روی NumOfProducts مشتق شده است؛ زمان بازگشایی محصول در منبع وجود ندارد.",
        },
    }

    with open(PROCESSED_DIR / "summary_stats.json", "w", encoding="utf-8") as f:
        json.dump(summary_stats, f, ensure_ascii=False, indent=2)

    print("✅ ساخت داده‌های پردازش‌شده با موفقیت انجام شد:")
    for k, v in summary_stats["row_counts"].items():
        print(f"  - {k}: {v:,} ردیف")


if __name__ == "__main__":
    main()
