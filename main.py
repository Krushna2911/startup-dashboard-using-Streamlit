import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Page config
st.set_page_config(layout="wide", page_title="Startup Analysis")


df = pd.read_csv("startup_cleaned.csv")
df["date"] = pd.to_datetime(df["date"])
df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.strftime("%b")   # Jan, Feb, Mar...
df["month_num"] = df["date"].dt.month

#function
def format_inr(amount):
    return f"₹{amount/10000000:.2f} Cr"


def load_overall_analysis():
    st.title("Overall Analysis")

    #total invested Amount
    total = df["amount"].sum()

    # Maximum funding received by a startup
    max_funding =df.groupby("startup")["amount"].max().max()
    # Average investment amount
    avg_funding = df["amount"].mean()
    # Total Funded Startup
    num_startup = df["startup"].nunique()

    col1, col2, col3 , col4 = st.columns(4)
    col1.metric("Total Funding", format_inr(total))
    col2.metric("Maximum Funding", format_inr(max_funding))
    col3.metric("Average Funding", format_inr(avg_funding))
    col4.metric("Total Startups", num_startup)

    # Month-On-Month Graph
    st.header("Month-On-Month Graph")
    selected_option = st.selectbox("Select Type", ["Total", "Count"])

    if selected_option == "Total":
        temp_df = (
            df.groupby(["year", "month_num", "month"])["amount"]
            .sum()
            .reset_index()
            .sort_values(["year", "month_num"])
        )

    else:
         temp_df = (
            df.groupby(["year", "month_num", "month"])["amount"]
            .count()
            .reset_index()
            .sort_values(["year", "month_num"])
        )
    temp_df["x_axis"] = (
         temp_df["month"].astype(str) + "-" + temp_df["year"].astype(str)
)

    fig5, ax5 = plt.subplots(figsize=(10, 5))

    ax5.plot(
  temp_df["x_axis"],
        temp_df["amount"],
        marker="o",
        linewidth=2,
        color="#1f77b4",

    )

    ax5.set_title("Month-on-Month Investment Trend",fontsize=14, fontweight="bold")
    ax5.set_xlabel("Month-Year", fontsize=12)
    ax5.set_ylabel("Investment (₹ Cr)", fontsize=12)
    plt.xticks(rotation=45, ha="right")
    ax5.grid(True, alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig5)

# ─────────────────────────────────────────────
# STARTUP DETAILS
# ─────────────────────────────────────────────
def load_startup_details(startup_name):
    st.title(f"Startup: {startup_name}")

    startup_df = df[df["startup"] == startup_name].sort_values("date", ascending=False)

    if startup_df.empty:
        st.warning("No data found for this startup.")
        return

    # Recent Investments
    st.subheader("Recent Funding Rounds")
    display_df = startup_df[["date", "investors", "vertical", "city", "round", "amount"]].head(5)
    display_df = display_df.copy()
    display_df["amount"] = display_df["amount"].apply(format_inr)
    st.dataframe(display_df, use_container_width=True)

    # Funding Timeline
    st.subheader("Funding Timeline")
    timeline_df = startup_df.groupby("year")["amount"].sum().sort_index()

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(timeline_df.index, timeline_df.values / 10000000, marker="o", linewidth=2, color="#2ca02c")
    ax.set_title("Year-wise Funding Received", fontsize=14, fontweight="bold")
    ax.set_xlabel("Year", fontsize=12)
    ax.set_ylabel("Amount (₹ Cr)", fontsize=12)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)

    # Investors in this startup
    st.subheader("Key Investors")
    investor_list = startup_df["investors"].dropna().astype(str).str.split(",").explode().str.strip().unique()
    if len(investor_list) > 0:
        st.write(", ".join(investor_list))
    else:
        st.write("No investor data available.")

    # Total funding received
    total_funding = startup_df["amount"].sum()
    st.metric("Total Funding Received", format_inr(total_funding))
# investor details
def load_investor_details(investor):
    st.title("investor")

    last5_df = (
        df[df["investors"].str.contains(investor, na=False)]
        .sort_values("date", ascending=False)
        .head(5)[["date", "startup", "vertical", "city", "round", "amount"]]
    )

    last5_df["amount"] = last5_df["amount"].apply(format_inr)

    st.dataframe(last5_df)

 # Biggest investments
    big_df = (
        df[df["investors"].str.contains(investor,na=False)]
        .groupby("startup" , as_index=False)["amount"]
        .sum()
        .sort_values("amount", ascending=False)
        .head()
    )
    #big_series["amount"] = big_series["amount"] / 10000000
    col1, col2, = st.columns(2)
    with col1:
        #plot in crores
        chart_df = big_df.copy()
        chart_df["amount"] = chart_df["amount"] / 10000000
       # Plot using numeric values
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(chart_df["startup"], chart_df["amount"])
        ax.set_title("Biggest Investments")
        ax.set_xlabel("Startup")
        ax.set_ylabel("Amount (Cr)")

        plt.xticks()

    # Labels above bars
        for i, value in enumerate(chart_df["amount"]):
            ax.text(i, value, f"{value:.2f} Cr",
                ha="center", va="bottom", fontsize=8)
        st.pyplot(fig)
    with col2:
        vertical_series = (
        df[df["investors"].str.contains(investor, na=False)]
        .groupby("vertical")["amount"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
    )
        fig1, ax1 = plt.subplots(figsize=(6, 4.4))
        ax1.set_title("Sector Invested")
        ax1.pie(
            vertical_series,
            labels=vertical_series.index,
            autopct="%1.1f%%",
            startangle=90
        )

        ax1.axis("equal")  # Makes the pie chart circular
        plt.tight_layout()
        st.pyplot(fig1)
    col3, col4 = st.columns(2)
    with col3:
    # Stage-wise (Investment Round) Pie Chart
        round_series = (
            df[df["investors"].str.contains(investor, na=False)]
                .groupby("round")["amount"]
                .sum()
                .sort_values(ascending=False)
                .head(5)

            )
        fig2, ax2 = plt.subplots(figsize=(6,4.5))
        ax2.pie(
            round_series,
            labels=round_series.index,
            autopct="%1.1f%%",
            startangle=90
        )

        ax2.set_title("Investment Stage Distribution")
        ax2.axis("equal")
        plt.tight_layout()
        st.pyplot(fig2)
    with col4:
        # City-wise pie chart (by number of investments)
        city_series = (
            df[df["investors"].str.contains(investor, na=False)]
            .groupby("city")
            .size()
            .sort_values(ascending=False)
            .head(5)
        )

        fig3, ax3 = plt.subplots(figsize=(6,4.5))

        ax3.pie(
            city_series,
            labels=city_series.index,
            autopct="%1.1f%%",
            startangle=90,
        )

        ax3.set_title("City-wise Investments")
        ax3.axis("equal")
        plt.tight_layout()
        st.pyplot(fig3)
    col5, col6 = st.columns(2)
    with col5:
    # Year-investment Trend
        year_series = (
            df[df["investors"].str.contains(investor, na=False)]
            .groupby("year")["amount"]
            .sum()
            .sort_index()
        )
        fig4, ax4 = plt.subplots(figsize=(12, 6))

        ax4.plot(
        year_series.index,
            year_series.values / 10000000,  # Convert INR to Crores
            marker="o",
            linewidth=2,
        )

        ax4.set_title("Year-wise Investment Trend")
        ax4.set_xlabel("Year")
        ax4.set_ylabel("Investment (₹ Cr)")

        ax4.grid(True)

        st.pyplot(fig4,use_container_width=True)

    with col6:
# Create a copy only for display
        display_df = big_df.copy()
        display_df["amount"] = display_df["amount"].apply(format_inr)

        st.subheader("Biggest Investments")
        st.dataframe(display_df)


st.sidebar.title("Startup Funding Analysis")

option = st.sidebar.selectbox("select one",["Overall Analysis","Startup","Investor"])

if option == "Overall Analysis":
#    btnn =st.sidebar.button("Show over all analysis")
#
# if btnn:
    load_overall_analysis()

elif option == "Startup":
    selected_startup = st.sidebar.selectbox(
    "Select Startup",
    sorted(df["startup"].unique().tolist())
    )
    btn1 = st.sidebar.button('Find Startup Details')
    load_startup_details(selected_startup)
    # st.title("Startup Analysis")
else:
    selected_investor = st.sidebar.selectbox(
    "Select Investor",
    sorted(df["investors"].dropna().astype(str).str.split(",").explode().str.strip().unique().tolist())
    )
    btn2 = st.sidebar.button('Find Investor Details')
    if btn2:
        load_investor_details(selected_investor)


