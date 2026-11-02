import io

ECOMMERCE_SALES_CSV = """order_id,order_date,customer_segment,region,category,sales,profit,discount,quantity
ORD-1001,2026-01-15,Consumer,North,Electronics,450.00,85.50,0.05,2
ORD-1002,2026-01-16,Corporate,West,Furniture,820.50,140.20,0.10,3
ORD-1003,2026-01-17,Home Office,East,Office Supplies,45.20,12.30,0.00,5
ORD-1004,2026-01-18,Consumer,South,Electronics,1200.00,310.00,0.15,1
ORD-1005,2026-01-20,Corporate,North,Furniture,650.00,95.00,0.05,2
ORD-1006,2026-01-22,Consumer,West,Office Supplies,78.90,24.50,0.00,6
ORD-1007,2026-01-25,Home Office,South,Electronics,340.00,62.00,0.10,1
ORD-1008,2026-01-27,Corporate,East,Furniture,1450.00,280.00,0.20,4
ORD-1009,2026-01-28,Consumer,North,Office Supplies,112.50,38.10,0.05,8
ORD-1010,2026-01-30,Corporate,South,Electronics,890.00,195.00,0.10,2
ORD-1011,2026-02-02,Home Office,West,Office Supplies,65.00,18.00,0.00,4
ORD-1012,2026-02-05,Consumer,East,Furniture,980.00,165.00,0.15,3
ORD-1013,2026-02-07,Corporate,North,Electronics,1500.00,420.00,0.05,2
ORD-1014,2026-02-09,Consumer,South,Office Supplies,34.00,9.50,0.00,3
ORD-1015,2026-02-12,Home Office,East,Electronics,720.00,150.00,0.10,1
ORD-1016,2026-02-15,Corporate,West,Furniture,1120.00,210.00,0.10,3
ORD-1017,2026-02-18,Consumer,North,Office Supplies,88.00,26.00,0.00,5
ORD-1018,2026-02-20,Home Office,South,Furniture,540.00,82.00,0.05,2
ORD-1019,2026-02-22,Corporate,East,Electronics,2100.00,580.00,0.15,3
ORD-1020,2026-02-25,Consumer,West,Office Supplies,95.00,28.50,0.00,7
ORD-1021,2026-02-26,Consumer,North,Electronics,680.00,145.00,0.08,2
ORD-1022,2026-02-27,Corporate,South,Furniture,890.00,135.00,0.12,2
ORD-1023,2026-02-28,Home Office,East,Office Supplies,120.00,36.00,0.00,6
ORD-1024,2026-03-01,Consumer,West,Electronics,1350.00,340.00,0.10,2
ORD-1025,2026-03-02,Corporate,North,Furniture,780.00,115.00,0.05,2
"""

CUSTOMER_CHURN_CSV = """customer_id,tenure_months,monthly_charges,total_charges,contract_type,tech_support,churn
CUST-001,12,65.50,786.00,Month-to-month,No,Yes
CUST-002,48,89.90,4315.20,Two year,Yes,No
CUST-003,6,74.20,445.20,Month-to-month,No,Yes
CUST-004,36,55.00,1980.00,One year,Yes,No
CUST-005,2,95.40,190.80,Month-to-month,No,Yes
CUST-006,60,105.00,6300.00,Two year,Yes,No
CUST-007,18,80.10,1441.80,One year,No,No
CUST-008,3,70.50,211.50,Month-to-month,No,Yes
CUST-009,24,62.30,1495.20,One year,Yes,No
CUST-010,4,85.00,340.00,Month-to-month,No,Yes
CUST-011,52,110.20,5730.40,Two year,Yes,No
CUST-012,8,92.00,736.00,Month-to-month,No,Yes
CUST-013,30,58.40,1752.00,One year,Yes,No
CUST-014,1,69.90,69.90,Month-to-month,No,Yes
CUST-015,40,78.50,3140.00,Two year,Yes,No
CUST-016,14,88.20,1234.80,Month-to-month,No,Yes
CUST-017,65,115.00,7475.00,Two year,Yes,No
CUST-018,9,72.40,651.60,Month-to-month,No,Yes
CUST-019,28,64.00,1792.00,One year,Yes,No
CUST-020,5,82.50,412.50,Month-to-month,No,Yes
"""

MARKETING_CAMPAIGNS_CSV = """campaign_name,channel,impressions,clicks,conversions,spend_usd,revenue_usd,roi_pct
Spring Launch,Google Search,120000,4800,320,3500.00,9600.00,174.3
Brand Awareness,Meta Ads,250000,6250,210,4200.00,6300.00,50.0
Retargeting Q1,Email,45000,3150,450,850.00,13500.00,1488.2
Product Spotlight,TikTok Ads,180000,5400,195,2900.00,5850.00,101.7
Influencer Push,Instagram,95000,3800,260,3100.00,7800.00,151.6
Affiliate Promo,Partner Network,60000,2400,180,1200.00,5400.00,350.0
B2B Enterprise,LinkedIn Ads,40000,960,85,4500.00,10200.00,126.7
Holiday Preview,YouTube Ads,160000,3200,140,3800.00,4200.00,10.5
Summer Kickoff,Google Search,140000,5880,410,4100.00,12300.00,200.0
Newsletter Blast,Email,38000,2850,390,700.00,11700.00,1571.4
"""

SAMPLE_DATASETS = {
    "ecommerce": {
        "id": "ecommerce",
        "name": "E-Commerce Global Sales & Profit",
        "filename": "ecommerce_sales.csv",
        "description": "25 retail orders tracking sales, profit margins, product categories, and discounts across regions.",
        "csv_text": ECOMMERCE_SALES_CSV.strip()
    },
    "churn": {
        "id": "churn",
        "name": "Customer Churn & Retention",
        "filename": "customer_churn.csv",
        "description": "20 customer accounts assessing tenure, monthly billing, contract formats, and churn probability.",
        "csv_text": CUSTOMER_CHURN_CSV.strip()
    },
    "marketing": {
        "id": "marketing",
        "name": "Digital Marketing Campaign ROI",
        "filename": "marketing_campaigns.csv",
        "description": "10 multi-channel marketing campaigns comparing spend, click rates, conversions, and ROI metrics.",
        "csv_text": MARKETING_CAMPAIGNS_CSV.strip()
    }
}
