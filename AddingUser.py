import streamlit as st
from openpyxl import load_workbook, Workbook
import os

def show_page():

    #st.set_page_config(page_title="Add Associate", layout="wide")
    st.title("👥 Add Associate to Revenue Tracker")

    with st.form("add_user_form"):
        col1, col2 = st.columns(2)

        with col1:
            service_line = st.selectbox("Service Line", ["QEA", "SPE", "UI/UX"])
            project_name = st.selectbox("Project", [
                "QTest", "Ptest", "Rtest", "Srest", "Trest", "Urest",
                "Vrest", "Wrest", "Xrest", "Yrest", "Zrest"
            ])
            practice_line = st.selectbox("Practice Line", ["NFT", "SRE", "QTP"])

        with col2:
            associate_name = st.text_input("Associate Name")
            associate_id = st.text_input("Associate ID")
            region = st.selectbox("Region", ["North America", "APAC", "EU"])
            active_status = st.selectbox("Is Active", ["Yes", "No"])

        submitted = st.form_submit_button("Submit")

    excel_file = "BaseDatasheet.xlsx"

    if submitted:
        st.success(f"✅ Thanks, {associate_name} has been added!")

        # Create workbook and both sheets if file doesn't exist
        if not os.path.exists(excel_file):
            wb = Workbook()
            # Sheet1
            sheet1 = wb.active
            sheet1.title = "Sheet1"
            sheet1.append([
                "ServiceLine", "AssociateName", "AssociateID", "Project Name",
                "PracticeLine", "Region", "Active"
            ])
            # Sheet2
            sheet2 = wb.create_sheet("Sheet2")
            sheet2.append([
                "ServiceLine", "AssociateName", "AssociateID", "Project Name",
                "PracticeLine", "Region", "Active", "BillingRateByMonth"
            ])
            wb.save(excel_file)

        # Load workbook and sheets
        wb = load_workbook(excel_file)
        sheet1 = wb["Sheet1"]
        sheet2 = wb["Sheet2"]

        # Append data to Sheet1
        sheet1.append([
            service_line, associate_name, associate_id,
            project_name, practice_line, region, active_status
        ])

        # Append data to Sheet2 with default billing rate
        sheet2.append([
            service_line, associate_name, associate_id,
            project_name, practice_line, region, active_status
        ])

        wb.save(excel_file)

        #st.info("✅ Entry saved to both Sheet1 and Sheet2.")
