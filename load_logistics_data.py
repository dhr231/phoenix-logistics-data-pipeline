import pandas as pd
import sqlite3

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