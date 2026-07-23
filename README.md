# 🏥 Healthcare Data Pipeline & Analytics

## 🎯 Business Case
This project was designed to simulate a real-world healthcare analytics environment, focusing not only on data visualization but also on building a robust and scalable data pipeline.

The main objective was to transform raw, consolidated datasets into a structured analytical model capable of generating actionable insights.

<img width="1255" height="703" alt="image" src="https://github.com/user-attachments/assets/a58efe7e-df97-45cd-8578-66f067045dcc" />

## 🛠️ Data Source & Challenge

The dataset was sourced from Kaggle using Python.

However, the data was originally provided as a **fully consolidated dataset**, which does not reflect how data is typically ingested in real-world systems.

To address this, I:

* Split the dataset into **incremental monthly files**
* Simulated a real-world scenario where new data arrives periodically
* Designed the pipeline to handle **continuous ingestion and updates**

<img width="1533" height="598" alt="image" src="https://github.com/user-attachments/assets/453f9908-6169-4d03-83b8-9fea023f2339" />



## ⚙️ ETL Pipeline (Python)

A complete ETL pipeline was developed using Python, with modular architecture:

## 🔹Extract

* Integration with Google Drive API
* Automated file detection (new and updated files)
* Support for multiple file formats (CSV, Excel, Google Sheets)

<img width="1069" height="426" alt="image" src="https://github.com/user-attachments/assets/c350c7ac-ecab-403a-85bc-138c3d818f0b" />


## 🔹Transform

### Using Pandas, the pipeline applies:

* Data cleaning and normalization
* Column alignment fixes
* Standardization of text fields
* Creation of unique identifiers
* Feature engineering:
    - Age clusters
    - Billing tiers
    - Admission weekday
    - Length of stay

<img width="1036" height="561" alt="image" src="https://github.com/user-attachments/assets/89ca94b6-9d5d-4fdc-944e-cc296eb3d0d6" />

## 🔹Load

* Processed files are uploaded back to Google Drive
* Smart overwrite logic (update vs new file)
* Fully automated and scalable structure

![image.png](attachment:518d3dc0-d8f4-4111-a71c-a3fd817399d5:image.png)

## 🔁 Automation Layer

Initially, n8n was considered for orchestration.

However, due to limitations in executing local Python scripts, I implemented the automation using **Power Automate Desktop**, ensuring:

* Reliable execution
* Local environment control
* Easy scheduling and triggering

<img width="783" height="493" alt="image" src="https://github.com/user-attachments/assets/58ee74b6-2078-4968-b635-5ee6e5641c59" />

## 📊 Data Visualization (Power BI)

Power BI dashboards were designed with a strong focus on business decision-making.

<img width="1341" height="770" alt="image" src="https://github.com/user-attachments/assets/8bde740a-2c7f-4c81-bf06-68a0ff73edea" />

<img width="1341" height="750" alt="image" src="https://github.com/user-attachments/assets/bebcf0a4-0700-4bf7-b1ec-7824a55e827e" />

### Key Analysis Areas:

 **Revenue Analysis**
  * By hospital *
  * By insurance provider *
  * Monthly trends *

 **Patient Behavior**
  * Admission type distribution (Emergency, Urgent, Elective) *
  * Admission patterns by weekday *

 **Demographics**
  * Age group segmentation *
  * Gender distribution *

 **Operational Metrics**
  * Length of stay analysis *
  * Medical condition distribution *
  * Test result categorization *


## 💡 Value Delivered

This project demonstrates:

* End-to-end **data pipeline development (ETL)**
* Real-world **incremental data processing strategy**
* Integration between **Python, cloud storage, and BI tools**
* Strong focus on **data quality and transformation**
* Creation of **decision-oriented dashboards**

Ultimately, it bridges the gap between raw data and business insights, showcasing both **data engineering and data analytics capabilities**.

https://github.com/user-attachments/assets/55a084b5-fb3a-4044-8169-b6d29c09599f


## 🚀 Tech Stack

* Python (Pandas, Google Drive API)
* Power BI
* Power Automate Desktop
* Google Drive (Cloud Storage)

## 📌 Final Thoughts

This project reflects a practical approach to solving real-world data problems, combining automation, data engineering, and analytics into a single workflow.

Future improvements could include:

* Migration to cloud-based orchestration (e.g., Airflow)
* Deployment as a scalable data service


## 📂 Project Files

* [Python ETL scripts.](./scripts)
* [Power BI (.pbix) file and dashboard.](./dashboard)
