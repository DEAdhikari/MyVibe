import streamlit as st
import pandas as pd
import altair as alt

# Modular pages
import AddingUser
import ActualsVsForecast
import UpdatingActualsWithFilter
import ActualsByMonth

# ---- Sidebar Navigation ----
st.set_page_config(page_title="Revenue Dashboard", layout="wide")
st.sidebar.title("📁 Navigation")
page = st.sidebar.radio("Go to", [
    "Home",
    "Add User",
    "Actuals Vs Forecast",
    "Update Actuals",
    "Actuals By Month",
    "Settings"
])

# ---- Page Routing ----
if page == "Home":
    st.title("🏠 Welcome to the Dashboard")
    st.markdown("---")

    # 🔹 Load Data from Sheet1
    excel_file = "BaseDatasheet.xlsx"
    df = pd.read_excel(excel_file, sheet_name="Sheet1")

    # 🔹 Filter Active Associates
    df = df[df["Active"].astype(str).str.lower() == "yes"]

    # 🔹 Identify Actuals Columns
    actual_cols = [col for col in df.columns if "Actuals" in col]
    df[actual_cols] = df[actual_cols].fillna(0)
    df["Actuals_YTD"] = df[actual_cols].sum(axis=1)

    # === 📊 Revenue by Service Line ===
    summary_df = df.groupby("ServiceLine", as_index=False)["Actuals_YTD"].sum()
    summary_df["RevenueLabel"] = summary_df["Actuals_YTD"].apply(lambda x: f"${x:,.0f}")
    total_revenue = summary_df["Actuals_YTD"].sum()

    st.markdown(
        f"<h3 style='color:#1f77b4; font-weight:bold;'>Total YTD Revenue: <b>${total_revenue:,.0f}</b></h3>",
        unsafe_allow_html=True
    )

    base = alt.Chart(summary_df).encode(
        y=alt.Y("ServiceLine:N", sort="-x", title="Service Line"),
        x=alt.X("Actuals_YTD:Q", title="YTD Revenue", axis=alt.Axis(format="$,.0f"))
    )

    bars = base.mark_bar(size=30, cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
        color=alt.Color("ServiceLine:N", scale=alt.Scale(scheme="pastel1"), legend=None)
    )

    labels = base.mark_text(
        align="left", baseline="middle", dx=5, fontSize=13, color="white"
    ).encode(text="RevenueLabel:N")

    chart = (bars + labels).properties(
        title="💰 YTD Actual Revenue by Service Line",
        height=300,
        width="container"
    ).configure_title(
        fontSize=20,
        font="Segoe UI",
        fontWeight="bold",
        anchor="start",
        color="#1f77b4"
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14,
        grid=True
    ).configure_view(stroke=None)

    st.altair_chart(chart, use_container_width=True)

    with st.expander("📄 View Service Line Table"):
        st.dataframe(summary_df.sort_values("Actuals_YTD", ascending=False), use_container_width=True)

    # === 📊 Revenue by Region ===
    region_df = df.groupby("Region", as_index=False)["Actuals_YTD"].sum()
    region_df["RevenueLabel"] = region_df["Actuals_YTD"].apply(lambda x: f"${x:,.0f}")

    st.markdown("---")

    base_region = alt.Chart(region_df).encode(
        y=alt.Y("Region:N", sort="-x", title="Region"),
        x=alt.X("Actuals_YTD:Q", title="YTD Revenue", axis=alt.Axis(format="$,.0f"))
    )

    bars_region = base_region.mark_bar(size=30, cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
        color=alt.Color("Region:N", scale=alt.Scale(scheme="pastel2"), legend=None)
    )

    labels_region = base_region.mark_text(
        align="left", baseline="middle", dx=5, fontSize=13, color="white"
    ).encode(text="RevenueLabel:N")

    region_chart = (bars_region + labels_region).properties(
        title="🌐 YTD Actual Revenue by Region",
        height=280,
        width="container"
    ).configure_title(
        fontSize=20,
        font="Segoe UI",
        fontWeight="bold",
        anchor="start",
        color="#1f77b4"
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14,
        grid=True
    ).configure_view(stroke=None)

    st.altair_chart(region_chart, use_container_width=True)

    with st.expander("📄 View Region Table"):
        st.dataframe(region_df.sort_values("Actuals_YTD", ascending=False), use_container_width=True)

# === Modular Pages ===
elif page == "Add User":
    AddingUser.show_page()

elif page == "Actuals Vs Forecast":
    ActualsVsForecast.show_page()

elif page == "Update Actuals":
    UpdatingActualsWithFilter.show_page()

elif page == "Actuals By Month":
    ActualsByMonth.show_page()

elif page == "Settings":
    st.title("⚙️ Settings")
    st.write("Control app preferences, theme options, or configuration.")
