import streamlit as st
import pandas as pd
import altair as alt

def show_page():
    st.markdown(
        """
        <style>
        .card {
            background-color: #90caf9;
            padding: 20px;
            margin-bottom: 25px;
            border-radius: 12px;
            box-shadow: 1px 1px 6px rgba(0,0,0,0.07);
        }
        .card-header {
            background-color: #90caf9;
            padding: 10px 15px;
            font-size: 20px;
            font-weight: bold;
            color: #1f3b57;
            border-radius: 8px;
            margin-bottom: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("📅 Actuals By Year")
    st.markdown("---")

    excel_file = "BaseDatasheet.xlsx"
    sheet3_df = pd.read_excel(excel_file, sheet_name="Sheet3")
    df_melted = sheet3_df.melt(id_vars=["Total Revenue ($)"], var_name="Year", value_name="Revenue")
    df_melted = df_melted.rename(columns={"Total Revenue ($)": "Month"})
    df_melted["Revenue_M"] = df_melted["Revenue"] / 1_000_000
    df_melted["RevenueLabel"] = df_melted["Revenue_M"].apply(lambda x: f"{x:.1f}M")

    month_to_quarter = {
        "January": "Q1", "February": "Q1", "March": "Q1",
        "April": "Q2", "May": "Q2", "June": "Q2",
        "July": "Q3", "August": "Q3", "September": "Q3",
        "October": "Q4", "November": "Q4", "December": "Q4"
    }
    df_melted["Quarter"] = df_melted["Month"].map(month_to_quarter)

    # Sidebar filters
    st.sidebar.header("🔍 Filter Options")
    available_years = sorted(df_melted["Year"].unique())
    available_months = list(df_melted["Month"].unique())

    st.sidebar.markdown("**Select Year(s):**")
    selected_years = []
    for i in range(0, len(available_years), 3):
        cols = st.sidebar.columns(3)
        for j in range(3):
            if i + j < len(available_years):
                year = available_years[i + j]
                if cols[j].checkbox(f"{year}", value=(year == available_years[-1])):
                    selected_years.append(year)

    st.sidebar.markdown("**Select Month(s):**")
    selected_months = []
    for i in range(0, len(available_months), 3):
        cols = st.sidebar.columns(3)
        for j in range(3):
            if i + j < len(available_months):
                month = available_months[i + j]
                if cols[j].checkbox(f"{month}", value=True):
                    selected_months.append(month)

    filtered_df = df_melted[
        df_melted["Year"].isin(selected_years) & df_melted["Month"].isin(selected_months)
    ]

    if not filtered_df.empty:

        # MINI DASHBOARD SECTION
        with st.container():
            st.markdown('<div class="card"><div class="card-header">🧭 ActualsByYear_Mini Dashboard Comparison</div>', unsafe_allow_html=True)

            comparison_df = df_melted[df_melted["Month"].isin(selected_months)]
            year_summary = comparison_df.groupby("Year")["Revenue"].sum().reset_index()
            year_summary["Revenue_M"] = year_summary["Revenue"] / 1_000_000

            comp_cols = st.columns(len(year_summary))
            previous_rev = None
            for i, row in year_summary.iterrows():
                with comp_cols[i]:
                    current_rev = row["Revenue_M"]
                    delta_val = None if previous_rev is None else current_rev - previous_rev
                    delta_display = "N/A" if delta_val is None else f"{delta_val:+.1f}M"
                    st.metric(
                        label=f"📅 {row['Year']}",
                        value=f"{current_rev:.1f}M",
                        delta=delta_display,
                        delta_color="normal"
                    )
                    previous_rev = current_rev

            st.markdown('</div>', unsafe_allow_html=True)

        # KPI SUMMARY & BAR CHART SECTION
        with st.container():
            st.markdown('<div class="card"><div class="card-header">📊 Revenue Performance Summary</div>', unsafe_allow_html=True)

            total_revenue = filtered_df["Revenue"].sum()
            avg_revenue = filtered_df["Revenue"].mean()
            max_row = filtered_df.loc[filtered_df["Revenue"].idxmax()]
            peak_month = max_row["Month"]

            filtered_df["ShareOfTotal"] = (filtered_df["Revenue"] / total_revenue) * 100
            filtered_df["MonthRank"] = filtered_df["Revenue"].rank(method="min", ascending=False).astype(int)

            col1, col2, col3 = st.columns(3)
            col1.metric("📊 Total Revenue", f"${total_revenue:,.0f}")
            col2.metric("📈 Avg Monthly", f"${avg_revenue:,.0f}")
            col3.metric("🏆 Peak Month", f"{peak_month} ({max_row['Year']})")

            st.markdown(f"""
            > Across **{len(selected_months)} months** and **{len(selected_years)} year(s)**,  
            total revenue was **${total_revenue:,.0f}**, peaking in **{peak_month} {max_row['Year']}** with  
            **{max_row['RevenueLabel']}**.  
            Average monthly revenue: **${avg_revenue:,.0f}**.
            """)

            view_mode = st.radio("📊 Choose View Mode:", ["Monthly View", "Quarterly View"])
            revenue_target = 5.0
            target_df = filtered_df.copy()
            target_df["Target"] = revenue_target
            chart_x = "Month:N" if view_mode == "Monthly View" else "Quarter:N"

            base = alt.Chart(filtered_df).encode(
                x=alt.X(chart_x, sort=available_months),
                xOffset="Year:N",
                y=alt.Y("Revenue_M:Q", title="Revenue (Millions)", axis=alt.Axis(format="~s")),
                color=alt.Color("Year:N", legend=alt.Legend(title="Year")),
                tooltip=[
                    alt.Tooltip("Year:N"),
                    alt.Tooltip("Month:N"),
                    alt.Tooltip("Revenue_M:Q", title="Revenue (M)", format=".2f"),
                    alt.Tooltip("ShareOfTotal:Q", title="% of Total", format=".1f"),
                    alt.Tooltip("MonthRank:N", title="Rank")
                ]
            )

            bars = base.mark_bar(size=30, cornerRadius=4)
            labels = base.mark_text(
                align="center", baseline="bottom", dy=-5,
                fontSize=12, color="black"
            ).encode(text="RevenueLabel:N")

            line = base.mark_line(point=True, strokeDash=[3, 3], strokeWidth=2).encode(y="Revenue_M:Q")
            zero_line = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(strokeDash=[2, 2], color='gray').encode(y='y:Q')
            target_line = alt.Chart(target_df).mark_line(color="orange", strokeDash=[6, 3]).encode(x=chart_x, y="Target:Q")
            rule = alt.Chart(filtered_df[filtered_df["Month"] == peak_month]).mark_rule(color="gold", strokeDash=[4, 2], strokeWidth=2).encode(x="Month:N")

            chart = (bars + labels + line + zero_line + target_line + rule).properties(
                title="💰 Total Revenue by Month and Year (Millions)",
                height=420,
                width="container"
            ).configure_title(
                fontSize=18,
                fontWeight="bold",
                color="#1f77b4"
            ).configure_view(stroke=None)

            st.altair_chart(chart, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # PIVOT SECTION
        with st.container():
            show_pivot = st.checkbox("🧮 Show Raw Pivot Table")
            if show_pivot:
                st.markdown('<div class="card"><div class="card-header">🔍 Revenue Pivot View</div>', unsafe_allow_html=True)
                pivot = filtered_df.pivot_table(index=["Month"], columns="Year", values="Revenue_M")
                st.dataframe(pivot.style.format("{:.2f}M"))
                st.markdown('</div>', unsafe_allow_html=True)

        st.download_button(
            label="📥 Download Filtered Data",
            data=filtered_df.to_csv(index=False),
            file_name="Filtered_Revenue_By_Year.csv",
            mime="text/csv"
        )
