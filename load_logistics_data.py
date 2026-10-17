import pandas as pd
import sqlite3
from reconcile_lr import reconcile_lr

booking = pd.read_excel("booking_report.xlsx")
billing = pd.read_excel("bill_register.xlsx")

conn = sqlite3.connect("phoenix.db")

booking.to_sql("booking", conn, if_exists="replace", index=False)
billing.to_sql("billing", conn, if_exists="replace", index=False)

print(booking.columns.to_list())
print(billing.columns.to_list())

# query = """
# SELECT * FROM BOOKING LIMIT 10;
# """

# result = pd.read_sql_query(query,conn)
# print(result)

print("\n\n\n $$$$$$$$$$$$ DAY 1 $$$$$$$$$$$$")
query1b = """
SELECT CONSIGNOR, SUM(Total_Booking) AS TOTAL_AMOUNT FROM BOOKING 
GROUP BY CONSIGNOR
ORDER BY TOTAL_AMOUNT DESC;
"""

result1b = pd.read_sql_query(query1b, conn)
print(result1b)

query1c = """
SELECT FROM_, TO_, SUM(Total_Booking) AS TOTAL_AMOUNT FROM BOOKING
GROUP BY FROM_, TO_
ORDER BY TOTAL_AMOUNT DESC;
"""

result1c = pd.read_sql_query(query1c, conn)
print(result1c)

print(f"The highest-value customer is {result1b['CONSIGNOR'][0]} with value {result1b['TOTAL_AMOUNT'][0]}")
print(f"The highest-value route from {result1c['FROM_'][0]} to {result1c['TO_'][0]} with value {result1c['TOTAL_AMOUNT'][0]}")

print("\n\n\n $$$$$$$$$$$$ DAY 2 2.0pm $$$$$$$$$$$$")

query2a = """
SELECT FROM_, TO_, SUM(Margin) AS TOTAL_MARGIN FROM BOOKING
GROUP BY FROM_, TO_
ORDER BY TOTAL_MARGIN DESC
"""

result2a = pd.read_sql_query(query2a, conn)
print(result2a)

print(f"The highest-margin route is from {result2a['FROM_'][0]} to {result2a['TO_'][0]} with value {result2a['TOTAL_MARGIN'][0]}")


query2b = """
SELECT FROM_, TO_, AVG(Margin) AS AVG_MARGIN FROM BOOKING 
GROUP BY FROM_, TO_
ORDER BY AVG_MARGIN DESC"""

result2b = pd.read_sql_query(query2b, conn)
print(result2b)
print(f"The highest-avg-margin route is from {result2b['FROM_'][0]} to {result2b['TO_'][0]} with value {result2b['AVG_MARGIN'][0]}")


print("\n\n\n $$$$$$$$$$$$ DAY 3 12.10pm $$$$$$$$$$$$")


query3a = """
SELECT LR_NO FROM BILLING 
LIMIT 3"""

result3a = pd.read_sql_query(query3a, conn)

print(billing['LR_NO'])
billing_normalised = billing.copy()
billing_normalised['LR_NO'] = billing_normalised['LR_NO'].str.split("/")
billing_normalised = billing_normalised.explode("LR_NO")

print("=============== 1 ==============")
print(billing.shape)
print(billing_normalised.shape)

print("=============== 2 ==============")
missing_lr = billing_normalised["LR_NO"].isna().sum()
print("missing LR",missing_lr)

print("============== 3 ==============")
missing_lr_bills = billing_normalised[
    billing_normalised["LR_NO"].isna()
]
print("missing LR bills")
print(
    missing_lr_bills[
        ["BILL_NO","LR_NO","PARTY_NAME","TOTAL_AMOUNT"]
    ]
)
print("============= 4 =============")
duplicates_bills_lr = billing_normalised[
    billing_normalised.duplicated(
        subset = ["BILL_NO","LR_NO"],
        keep = False
    )
]
print("duplicates bills and LR", duplicates_bills_lr[["BILL_NO","LR_NO","PARTY_NAME","TOTAL_AMOUNT"]])
print(
    billing_normalised[
        ["BILL_NO","LR_NO","PARTY_NAME","TOTAL_AMOUNT"]
    ].head(15)
)


print("\n\n\n $$$$$$$$$$$$ DAY 4 16.15pm $$$$$$$$$$$$")


print("\n =========== LR DATA TYPES ===========")

print("Booking LR types : ")
print(booking["LR_NO"].dtype)

print("Billing LR types : ")
print(billing_normalised["LR_NO"].dtype)

booking["LR_NO"] = booking["LR_NO"].astype(str)
billing_normalised["LR_NO"] = billing_normalised["LR_NO"].astype(str)

print("Booking LR type : ", booking["LR_NO"].dtype)
print("Billing LR type : ", billing_normalised["LR_NO"].dtype)

print("\n ============ MISSING LR AFTER TYPE CONVERSION ============")
print(
    billing_normalised[
        billing_normalised["LR_NO"] == "nan"
    ][
        ["BILL_NO","LR_NO","PARTY_NAME","TOTAL_AMOUNT"]
    ]
)

billing_for_join = billing_normalised[
    billing_normalised["LR_NO"] != "nan"
].copy()

print("billing rows before join : ", billing_normalised.shape[0])
print("billing rows after join : ", billing_for_join.shape[0])

print(
    billing_for_join[
        ["BILL_NO","LR_NO","PARTY_NAME","TOTAL_AMOUNT"]
    ].head(10)
)

booking_billing = booking.merge(
    billing_for_join,
    on = "LR_NO",
    how = "left",
    suffixes = ("_BOOKING","_BILLING")
)

print("\n =========== BILLING + BOOKING JOINED ==========")
print("Booking rows : ", booking.shape[0])
print("joined rows : ", booking_billing.shape[0])

print(
    booking_billing[
        ["BILL_NO","LR_NO","PARTY_NAME","TOTAL_AMOUNT"]
    ].head(20)
)

print("\n========== BOOKING LR VALUES ==========")
print(booking["LR_NO"].tolist())

print("\n========== BILLING LR VALUES ==========")
print(billing_for_join["LR_NO"].tolist())

print("\n========== COMMON LR VALUES ==========")
common_lr = set(booking["LR_NO"]) & set(billing_for_join["LR_NO"])
print(common_lr)

print("\n========== BOOKING DATE RANGE ==========")

print("Booking minimum date:")
print(booking["DATE"].min())

print("Booking maximum date:")
print(booking["DATE"].max())


print("\n========== BILLING DATE RANGE ==========")

print("Billing minimum date:")
print(billing["BILL_DATE"].min())

print("Billing maximum date:")
print(billing["BILL_DATE"].max())

if len(common_lr) == 0:
    print("WARNING: No common LR numbers found.")
    print("Booking and Billing datasets may represent different periods.")




print("\n\n\n $$$$$$$$$$$$ DAY 5 16.11pm $$$$$$$$$$$$")

booking_lr = set(booking["LR_NO"]) #using set to get the unique LR no.s from booking dataframe
billing_lr = set(billing_for_join["LR_NO"]) #using set to get the unique LR from billing dataframe

booking_only_lr = booking_lr - billing_lr #applying the difference operator to get the booking only LRs
billing_only_lr = billing_lr - booking_lr #applying the difference operator to get the billing only LRs

print("=============== LR RECONCILIATION ==================")

print("COMMON LR COUNT : ", len(common_lr))
print("BOOKING-ONLY LR COUNT : ", len(booking_only_lr))
print("BILLING ONLY LR COUNT  :", len(billing_only_lr))

print("BOOKING-ONLY LR  : ", booking_only_lr)
print("BILLING ONLY LR  : ", billing_only_lr)

duplicates_billing_lr = billing_for_join[
    billing_for_join["LR_NO"].duplicated(keep = False)
]

print("============ DUPLICATE BILLING LR ============")

print(duplicates_billing_lr[
    ["BILL_NO","LR_NO","PARTY_NAME","TOTAL_AMOUNT"]
])


duplicate_lr_count = billing_for_join["LR_NO"].value_counts()

duplicate_lr_count = duplicate_lr_count[duplicate_lr_count > 1]

print("======= LR DUPLICATE SUMMARY ========")
print(duplicate_lr_count)

print("\n========== RECONCILIATION SUMMARY ==========")

print("Booking rows:", booking.shape[0])
print("Billing rows:", billing_for_join.shape[0])

print("Common LR:", len(common_lr))
print("Booking-only LR:", len(booking_only_lr))
print("Billing-only LR:", len(billing_only_lr))

print("Duplicate LR groups:", len(duplicate_lr_count))

if len(common_lr) == 0:
    print("JOIN STATUS: NOT RECOMMENDED")
else:
    print("JOIN STATUS: POSSIBLE")


print("============= DAY 6 1.40PM ===============")

reconciliation_lr = reconcile_lr(booking, billing_for_join)

print("========= LR RECONCILIATION USING FUNCTION =========")
print("\n Common LR : ", len(reconciliation_lr["common_lr"]))
print("Booking-only LR:", len(reconciliation_lr["booking_only_lr"]))
print("Billing-only LR:", len(reconciliation_lr["billing_only_lr"]))
print(
    "Duplicate LR groups:",
    len(reconciliation_lr["duplicate_lr_count"])
)
print("Join status:", reconciliation_lr["join_status"])

print("=========== DAY 7 11.50AM ============")

report = pd.DataFrame({
    "Metric": [
        "Booking Rows",
        "Billing Rows",
        "Common LR",
        "Booking-only LR",
        "Billing-only LR",
        "Duplicate LR Groups",
        "Join Status"
    ],
    "Value": [
        booking.shape[0],
        billing_for_join.shape[0],
        len(reconciliation_lr["common_lr"]),
        len(reconciliation_lr["booking_only_lr"]),
        len(reconciliation_lr["billing_only_lr"]),
        len(reconciliation_lr["duplicate_lr_count"]),
        reconciliation_lr["join_status"]
    ]
})
print(report)
report.to_csv("reconciliation_report.csv", index=False)
print("Report saved to reconciliation_report.csv")

saved_report = pd.read_csv("reconciliation_report.csv")
print("\n ============== SAVED REPORT =============")
print(saved_report)

print("========== DAY 8 10.50AM ===========")

exceptions = []

for lr in reconciliation_lr["booking_only_lr"]:
    exceptions.append({
        "Exception_type" : "BOOKING_ONLY",
        "LR_NO": lr,
        "Occurrence_Count" : 1
    })

for lr in reconciliation_lr["billing_only_lr"]:
    exceptions.append({
        "Exception_type" : "BILLING_ONLY",
        "LR_NO": lr,
        "Occurrence_Count" : 1
    })

for lr, count in reconciliation_lr["duplicate_lr_count"].items():
    exceptions.append({
        "Exception_type" : "DUPLICATE_BILLING",
        "LR_NO": lr,
        "Occurrence_Count" : count
    })

data_quality_report = pd.DataFrame(exceptions)

data_quality_report.to_csv("data_quality_report.csv", index=False)

print("\n Data Quality Report")
print(data_quality_report)

print("Data Quality Report saved successfully")


print("========== DAY 9 12.10PM ===========")

print("========== DAY 10 11.43PM ===========")

exception_summary = (
    data_quality_report
    .groupby("Exception_type")
    .size()
    .reset_index(name="Exception_count")
)

exception_summary.to_csv("exception_summary.csv", index=False)
print("\n Exception Summary")
print(exception_summary)

print("========== DAY 11 01.09PM ===========")

filtered_df = data_quality_report[
    data_quality_report["Exception_type"] != "DUPLICATE_BILLING"
]

summary = (
    filtered_df
    .groupby("Exception_type")["Occurrence_Count"]
    .sum()
)

print(summary)


print("========== DAY 12 12.32PM ===========")

filtered_df_2 = data_quality_report[
    (data_quality_report["Exception_type"] == "BILLING_ONLY") | (data_quality_report["Exception_type"] == "BOOKING_ONLY") 
]

summary_without_duplicate = (
    filtered_df_2
    .groupby("Exception_type")["Occurrence_Count"]
    .sum()
) 

print("\n SUMMARY REPORT WITHOUT DUPLICATE BILLING ------------->")
print(summary_without_duplicate)

print("========== DAY 13 12.56PM ===========")

print("\n ============ EXCEPTION COUNT COMPARISON ===========")

row_summary = (
    data_quality_report
    .groupby("Exception_type")
    .size()
)

occurence_summary = (
    data_quality_report
    .groupby("Exception_type")["Occurrence_Count"]
    .sum()
)

print("\n Row Count :")
print(row_summary)

print("\n Total Occurences :")
print(occurence_summary)

print("========== DAY 14 06.08PM ===========")

# row_summary = (
#     data_quality_report
#     .groupby("Exception_type")
#     .size()
#     .reset_index(name="Row_Count")
# )

# occurrence_summary = (
#     data_quality_report
#     .groupby("Exception_type")["Occurrence_Count"]
#     .sum()
#     .reset_index(name="Total_Occurrences")

# )

# final_summary = row_summary.merge(
#     occurrence_summary,
#     on="Exception_type"
# )

final_summary = (
    data_quality_report
    .groupby("Exception_type")
    .agg(
        Row_Count = ("Occurrence_Count", "size"),
        Total_Occurrence = ("Occurrence_Count", "sum"),
        Maximum_Occurrence = ("Occurrence_Count", "max")
    )
)

print("\n =========== DAY 14 FINAL EXCEPTION SUMMARY ==========")
print(final_summary)

print("========== DAY 15 1.00PM =========")


print("\n========== DAY 15: JOIN READINESS ==========")

print("\n--- BILLING SCHEMA ---")
print("Shape:", billing.shape)
print("Columns:", billing.columns.tolist())
print("\nSample Billing Records:")
print(billing.head(3).to_string(index=False))

# Normalize LR numbers for comparison
booking_lr = (
    booking["LR_NO"]
    .astype("string")
    .str.strip()
)

billing_lr = (
    billing["LR_NO"]
    .astype("string")
    .str.strip()
)

# Exclude missing and blank LR values
booking_lr = booking_lr[booking_lr.notna() & booking_lr.ne("")]
billing_lr = billing_lr[billing_lr.notna() & billing_lr.ne("")]

common_lr = set(booking_lr) & set(billing_lr)

print("\n--- JOIN KEY CHECK ---")
print("Booking rows:", len(booking))
print("Billing rows:", len(billing))
print("Booking valid LR count:", len(booking_lr))
print("Billing valid LR count:", len(billing_lr))
print("Common unique LRs:", len(common_lr))

print("\nBooking duplicate LR values:")
print(booking_lr[booking_lr.duplicated(keep=False)].tolist())

print("\nBilling duplicate LR values:")
print(billing_lr[billing_lr.duplicated(keep=False)].tolist())



# Split slash-separated LRs into individual rows
billing_normalized = billing.copy()

billing_normalized["LR_NO"] = (
    billing_normalized["LR_NO"]
    .astype("string")
    .str.split("/")
)

billing_normalized = billing_normalized.explode("LR_NO")

billing_normalized["LR_NO"] = (
    billing_normalized["LR_NO"].str.strip()
)

# Remove missing or blank LR values
billing_normalized = billing_normalized[
    billing_normalized["LR_NO"].notna()
    & billing_normalized["LR_NO"].ne("")
].copy()

# Normalize Booking LR values for comparison
booking_normalized = booking.copy()

booking_normalized["LR_NO"] = (
    booking_normalized["LR_NO"]
    .astype("string")
    .str.strip()
)

booking_normalized = booking_normalized[
    booking_normalized["LR_NO"].notna()
    & booking_normalized["LR_NO"].ne("")
].copy()

# Compare individual LRs
booking_lr_set = set(booking_normalized["LR_NO"])
billing_lr_set = set(billing_normalized["LR_NO"])

common_lr = booking_lr_set & billing_lr_set

print("\n===== DAY 15: NORMALIZED LR CHECK =====")
print("Original Billing rows:", len(billing))
print("Normalized Billing rows:", len(billing_normalized))
print("Booking valid rows:", len(booking_normalized))
print("Common unique LRs:", len(common_lr))
print("Common LRs:", sorted(common_lr))

print("\nBooking-only LRs:")
print(sorted(booking_lr_set - billing_lr_set))

print("\nBilling-only LR count:", len(billing_lr_set - booking_lr_set))



print("\n===== DAY 15: MISMATCH DIAGNOSIS =====")

print("\n--- BOOKING LR AND DATE ---")
print(
    booking_normalized[["LR_NO", "DATE"]]
    .sort_values("LR_NO")
    .to_string(index=False)
)

print("\n--- BILLING LR AND DATE SAMPLE ---")
print(
    billing_normalized[["LR_NO", "BILL_DATE"]]
    .head(10)
    .to_string(index=False)
)

booking_dates = __import__("pandas").to_datetime(
    booking_normalized["DATE"], errors="coerce", dayfirst=True
)

billing_dates = __import__("pandas").to_datetime(
    billing_normalized["BILL_DATE"], errors="coerce"
)

print("\nBooking date range:", booking_dates.min(), "to", booking_dates.max())
print("Billing date range:", billing_dates.min(), "to", billing_dates.max())



master_table = booking_normalized.merge(
    billing_normalized,
    on="LR_NO",
    how="outer",
    suffixes=("_Booking", "_Billing"),
    indicator=True
)

master_table["Reconciliation_Status"] = (
    master_table["_merge"]
    .map({
        "both": "MATCHED",
        "left_only": "BOOKING_ONLY",
        "right_only": "BILLING_ONLY"
    })
)

master_table = master_table.drop(columns=["_merge"])

master_table.to_csv(
    "master_reconciliation.csv",
    index=False
)

print("\n===== DAY 15: MASTER RECONCILIATION =====")
print("Master rows:", len(master_table))
print("\nStatus counts:")
print(master_table["Reconciliation_Status"].value_counts())
print("\nSample output:")
print(master_table.head(5).to_string(index=False))
print("\nSaved: master_reconciliation.csv")


print("\n ========== DAY 16 4.00PM =========")

print("\n =========== BILLING RECORD IDENTITY ===========")

billing_source = billing.copy()

billing_source["Billing_Record_ID"] = range(
    1, len(billing_source) + 1
)

print("Original billing rows : ", len(billing_source))
print(
    billing_source[
        ["Billing_Record_ID", "BILL_NO", "LR_NO", "FINAL_AMOUNT"]
    ].head(5).to_string(index = False)
)

billing_normalized = billing_source.copy()

billing_normalized["LR_NO"] = (
    billing_normalized["LR_NO"]
    .astype("string")
    .str.split("/")
)

billing_normalized = billing_normalized.explode("LR_NO")

billing_normalized["LR_NO"] = (
    billing_normalized["LR_NO"].str.strip()
)

# Remove missing or blank LR values
billing_normalized = billing_normalized[
    billing_normalized["LR_NO"].notna()
    & billing_normalized["LR_NO"].ne("")
].copy()

# Normalize Booking LR values for comparison
booking_normalized = booking.copy()

booking_normalized["LR_NO"] = (
    booking_normalized["LR_NO"]
    .astype("string")
    .str.strip()
)

booking_normalized = booking_normalized[
    booking_normalized["LR_NO"].notna()
    & booking_normalized["LR_NO"].ne("")
].copy()



print("\n--- BILLING EXPANSION CHECK ---")
print("Original billing rows:", len(billing_source))
print("Expanded billing rows:", len(billing_normalized))

print("\nRows per original billing record:")
print(
    billing_normalized
    .groupby("Billing_Record_ID")
    .size()
    .sort_values(ascending=False)
    .head(10)
)

print("\nSample expanded records:")
print(
    billing_normalized[
        ["Billing_Record_ID", "BILL_NO", "LR_NO", "FINAL_AMOUNT"]
    ].head(12).to_string(index=False)
)




print("\n===== DAY 16: FINANCIAL GRAIN CHECK =====")

amount_check = (
    billing_normalized
    .groupby("Billing_Record_ID")
    .agg(
        LR_Row_Count=("LR_NO", "size"),
        Distinct_LRs=("LR_NO", "nunique"),
        Invoice_Amount=("FINAL_AMOUNT", "first"),
        Repeated_Amount_Sum=("FINAL_AMOUNT", "sum")
    )
    .reset_index()
)

amount_check["Amount_Repeated"] = (
    amount_check["LR_Row_Count"] > 1
)

print(
    amount_check.sort_values(
        "LR_Row_Count", ascending=False
    ).head(10).to_string(index=False)
)

print("\nRecords with repeated amounts:")
print(amount_check["Amount_Repeated"].sum())



# One row per original billing record
billing_level = billing_source.copy()

# One row per individual LR occurrence
lr_level = billing_normalized[
    [
        "Billing_Record_ID",
        "BILL_NO",
        "LR_NO",
        "FINAL_AMOUNT"
    ]
].copy()

print("\n===== DAY 16: TABLE GRAIN VALIDATION =====")

print("Billing-level rows:", len(billing_level))
print("LR-level rows:", len(lr_level))

print(
    "Billing-level FINAL_AMOUNT total:",
    billing_level["FINAL_AMOUNT"].sum()
)

print(
    "Expanded LR-level FINAL_AMOUNT total:",
    lr_level["FINAL_AMOUNT"].sum()
)

print("\nBilling-level sample:")
print(
    billing_level[
        ["Billing_Record_ID", "BILL_NO", "FINAL_AMOUNT"]
    ].head(5).to_string(index=False)
)


print("\n========== DAY 17: SAFE MASTER DESIGN ==========")

# 1. Invoice-level financial table: one row per original billing record
billing_financials = billing_source[
    [
        "Billing_Record_ID",
        "BILL_NO",
        "BILL_DATE",
        "FINAL_AMOUNT",
        "TOTAL_AMOUNT"
    ]
].copy()

# 2. LR-level detail: one row per exploded LR occurrence
billing_lr_detail = billing_normalized[
    [
        "Billing_Record_ID",
        "BILL_NO",
        "LR_NO"
    ]
].copy()

# Keep financial amounts out of the LR-level table
print("Invoice-level rows:", len(billing_financials))
print("LR-level rows:", len(billing_lr_detail))

print("\nInvoice-level financial total:")
print(billing_financials["FINAL_AMOUNT"].sum())

print("\nLR-level sample:")
print(billing_lr_detail.head(10).to_string(index=False))


master_table = booking_normalized.merge(
    billing_lr_detail,
    on="LR_NO",
    how="outer",
    suffixes=("_Booking", "_Billing"),
    indicator=True
)

master_table["Reconciliation_Status"] = (
    master_table["_merge"]
    .map({
        "both": "MATCHED",
        "left_only": "BOOKING_ONLY",
        "right_only": "BILLING_ONLY"
    })
)

master_table = master_table.drop(columns=["_merge"])

# Save the two outputs separately
master_table.to_csv("master_reconciliation.csv", index=False)
billing_financials.to_csv("billing_financials.csv", index=False)

print("\n===== DAY 17: VALIDATION =====")
print("Master rows:", len(master_table))
print("Invoice financial rows:", len(billing_financials))

print("\nReconciliation status:")
print(master_table["Reconciliation_Status"].value_counts())

print("\nOriginal invoice total:")
print(billing_financials["FINAL_AMOUNT"].sum())

print("\nSaved: master_reconciliation.csv")
print("Saved: billing_financials.csv")



print("\n===== DAY 17: INVOICE TOTAL VALIDATION =====")

source_total = billing_source["FINAL_AMOUNT"].sum()
output_total = billing_financials["FINAL_AMOUNT"].sum()

print("Source total:", round(source_total, 2))
print("Output total:", round(output_total, 2))
print("Totals match:", round(source_total, 2) == round(output_total, 2))

print(
    "Unique billing record IDs:",
    billing_financials["Billing_Record_ID"].nunique()
)
