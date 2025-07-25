import streamlit as st

import pandas as pd
import altair as alt
import plotly.graph_objects as go

# Modular pages
import AddingUser
import ActualsVsForecast
import UpdatingActualsWithFilter
import UpdateForecast
import ActualsByMonth
import ActualsByYear
import BillingCalculator
import ForecastBillingHours
import ForecastBillingCostCalculator
import ForecastResult

st.set_page_config(page_title="Revenue Dashboard", layout="wide")

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.error("You must log in to access this page.")
    st.stop()

role = st.session_state.role
emp_id = st.session_state.emp_id

st.title(f"Welcome, {role.capitalize()} ({emp_id})")

# Example of role-based UI
if role == "Admin":
    st.success("You have full access.")
    # Show admin tools
elif role == "Contributor":
    st.info("You can view and update data.")
    # Show contributor tools
elif role == "Viewer":
    st.warning("You have read-only access.")
    # Disable inputs or restrict write access
else:
    st.error("Unknown role. Access denied.")
    st.stop()

allowed_pages = ["Home", "Actuals Vs Forecast", 
                 "Actuals By Month", "Billing Calculator", "Forecast Billing Hours", 
                 "Forecast Billing Cost Cal", "Forecast Graph", "Settings"]

# Only Admin and Contributor can access "Add User"
if role in ["Admin", "Contributor"]:
    allowed_pages.insert(1, "Add User")  # Insert where you want it to appear
    allowed_pages.insert(3, "Update Actuals")
    allowed_pages.insert(4, "Update Forecast")

# ---- Sidebar Navigation ----
st.sidebar.title("📁 Navigation")
page = st.sidebar.radio("Go to", allowed_pages)

# ---- Page Routing ----
if page == "Home":
    st.title("🏠 Welcome to the Dashboard")
    st.markdown("---")

    # 🔹 Load Data
    excel_file = "BaseDatasheet.xlsx"
    df = pd.read_excel(excel_file, sheet_name="Sheet1")
    df = df[df["Active"].astype(str).str.lower() == "yes"]

    actual_cols = [col for col in df.columns if "Actuals" in col]
    df[actual_cols] = df[actual_cols].fillna(0)
    df["Actuals_YTD"] = df[actual_cols].sum(axis=1)
    total_revenue = df["Actuals_YTD"].sum()

    st.markdown(
        f"<h3 style='color:#1f77b4; font-weight:bold; text-align:center;'>Total YTD Revenue: <b>${total_revenue:,.0f}</b></h3>",
        unsafe_allow_html=True
    )

    # === Bar Charts Side by Side ===
    col1, col2 = st.columns(2)

    # 📊 Revenue by Service Line
    summary_df = df.groupby("ServiceLine", as_index=False)["Actuals_YTD"].sum()
    summary_df["RevenueLabel"] = summary_df["Actuals_YTD"].apply(lambda x: f"${x:,.0f}")

    bar_base_1 = alt.Chart(summary_df).encode(
        y=alt.Y("ServiceLine:N", sort="-x"),
        x=alt.X("Actuals_YTD:Q", axis=alt.Axis(format="$,.0f"))
    )
    bars_1 = bar_base_1.mark_bar(size=25, cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
        color=alt.Color("ServiceLine:N", scale=alt.Scale(scheme="pastel1"), legend=None)
    )
    labels_1 = bar_base_1.mark_text(align="left", baseline="middle", dx=5, fontSize=13, color="white").encode(
        text="RevenueLabel:N"
    )
    with col1:
        st.altair_chart(
            (bars_1 + labels_1).properties(title="💰 YTD Revenue by Service Line", height=280).configure_title(
                fontSize=20, fontWeight="bold", color="#1f77b4", anchor="start", font="Segoe UI"
            ).configure_view(stroke=None),
            use_container_width=True
        )

    with st.expander("📄 View Service Line Table"):
        st.dataframe(summary_df.sort_values("Actuals_YTD", ascending=False), use_container_width=True)

    # 📊 Revenue by Region
    region_df = df.groupby("Region", as_index=False)["Actuals_YTD"].sum()
    region_df["RevenueLabel"] = region_df["Actuals_YTD"].apply(lambda x: f"${x:,.0f}")

    bar_base_2 = alt.Chart(region_df).encode(
        y=alt.Y("Region:N", sort="-x"),
        x=alt.X("Actuals_YTD:Q", axis=alt.Axis(format="$,.0f"))
    )
    bars_2 = bar_base_2.mark_bar(size=25, cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
        color=alt.Color("Region:N", scale=alt.Scale(scheme="pastel2"), legend=None)
    )
    labels_2 = bar_base_2.mark_text(align="left", baseline="middle", dx=5, fontSize=13, color="white").encode(
        text="RevenueLabel:N"
    )
    with col2:
        st.altair_chart(
            (bars_2 + labels_2).properties(title="🌐 YTD Revenue by Region", height=280).configure_title(
                fontSize=20, fontWeight="bold", color="#1f77b4", anchor="start", font="Segoe UI"
            ).configure_view(stroke=None),
            use_container_width=True
        )

    with st.expander("📄 View Region Table"):
        st.dataframe(region_df.sort_values("Actuals_YTD", ascending=False), use_container_width=True)

    # === 🥧 3D-Style Pie Charts Using Plotly ===
    st.markdown("---")
    pie_col1, pie_col2 = st.columns(2)

    with pie_col1:
        st.markdown("### 🥧 Revenue Contribution by Service Line")
        fig1 = go.Figure(data=[go.Pie(
            labels=summary_df["ServiceLine"],
            values=summary_df["Actuals_YTD"],
            textinfo="percent",
            textposition="outside",
            hole=0.3
        )])
        fig1.update_traces(marker=dict(line=dict(color="#000000", width=1)))
        fig1.update_layout(title_text="Service Line Contribution", title_font_size=16)
        st.plotly_chart(fig1, use_container_width=True)

    with pie_col2:
        st.markdown("### 🥧 Revenue Contribution by Region")
        fig2 = go.Figure(data=[go.Pie(
            labels=region_df["Region"],
            values=region_df["Actuals_YTD"],
            textinfo="percent",
            textposition="outside",
            hole=0.3
        )])
        fig2.update_traces(marker=dict(line=dict(color="#000000", width=1)))
        fig2.update_layout(title_text="Region Contribution", title_font_size=16)
        st.plotly_chart(fig2, use_container_width=True)

# ---- Modular Pages ----
elif page == "Add User":
    AddingUser.show_page()
elif page == "Actuals Vs Forecast":
    ActualsVsForecast.show_page()
elif page == "Update Actuals":
    UpdatingActualsWithFilter.show_page()
elif page == "Update Forecast":
    UpdateForecast.show_page()
elif page == "Actuals By Month":
    ActualsByMonth.show_page()
elif page == "Actuals By Year":
    ActualsByYear.show_page()
elif page == "Billing Calculator":
    BillingCalculator.show_page()
elif page == "Forecast Billing Hours":
    ForecastBillingHours.main()
elif page == "Forecast Billing Cost Cal":
    ForecastBillingCostCalculator.main()
elif page == "Forecast Result":
    ForecastResult.main()
elif page == "Settings":
    st.title("⚙️ Settings")
    st.write("Control app preferences, theme options, or configuration.")

if st.button("Logout"):
    st.session_state.authenticated = False
    st.session_state.role = None
    st.session_state.emp_id = None
    st.success("Logged out.")
    st.switch_page("Authenticate.py")
