# 📊 Customer Segmentation & CLTV Analysis (RFM + BG/NBD + Gamma-Gamma)

---

## 📂 Dataset

This project uses the **Online Retail II dataset**, which is publicly available on Kaggle:

https://www.kaggle.com/datasets/mashlyn/online-retail-ii-uci

The dataset includes:
- Invoice data  
- Product details  
- Customer transactions  
- Quantity and price information  

---

## 📌 Project Overview

This project focuses on **customer segmentation** and **Customer Lifetime Value (CLTV) prediction** using real retail transaction data.

RFM analysis and probabilistic models (BG/NBD & Gamma-Gamma) are applied to understand customer behavior and predict future customer value.

---

## 🧠 Objectives

- Segment customers using RFM analysis  
- Identify high-value customers  
- Detect at-risk and inactive customers  
- Predict future purchase behavior  
- Estimate Customer Lifetime Value (CLTV)  

---

## ⚙️ Methods Used

### 1. Data Preprocessing
- Missing value handling  
- Removal of canceled invoices  
- Filtering invalid values (Quantity & Price > 0)  
- Feature engineering (TotalPrice = Quantity × Price)  

---

### 2. RFM Analysis
Customers are segmented based on:

- **Recency** → time since last purchase  
- **Frequency** → number of purchases  
- **Monetary** → total spending  

Customer segments include:
- Champions  
- Loyal Customers  
- At Risk  
- Need Attention  
- New Customers  

---

### 3. CLTV Prediction

Customer Lifetime Value is estimated using probabilistic models:

- **BG/NBD Model** → predicts future purchase frequency  
- **Gamma-Gamma Model** → estimates average profit per transaction  

Final CLTV combines:
- expected purchases  
- expected profit  
- customer lifetime value estimation  

---

## 📊 Key Insights

- High-value customers were successfully identified  
- Customer base segmented into actionable groups  
- Future purchase behavior estimated  
- Marketing targeting strategies can be improved using results  
- Customer churn risk can be reduced using segmentation  

---

## 🛠️ Technologies Used

- Python  
- Pandas  
- NumPy  
- Matplotlib  
- Seaborn  
- Lifetimes (BG/NBD & Gamma-Gamma models)  

---

## 📈 Output Examples

(Add your visualizations here)

- RFM segment distribution  
- CLTV distribution plot  
- Customer value insights  

---

## 🚀 Business Value

This project helps businesses to:

- Increase customer retention  
- Improve marketing targeting  
- Identify profitable customer groups  
- Reduce churn rate  
- Optimize revenue strategies  

---

## 👤 Author

Ahmet İnce  
Data Science Portfolio Project
