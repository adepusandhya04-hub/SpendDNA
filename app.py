import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="SpendDNA", page_icon="💰", layout="wide")


def categorize_expense(description):
    text = str(description).upper()

    if any(x in text for x in ["ZERODHA", "GROWW", "UPSTOX", "MUTUAL FUND"]):
        return "Investments"
    if "RENT" in text or "LANDLORD" in text:
        return "Rent"
    if "ATM-WDL" in text or "ATM WITHDRAWAL" in text:
        return "Cash Withdrawal"
    if any(x in text for x in [
        "SWIGGY", "ZOMATO", "MEGHANA FOODS", "DINEOUT", "TRUFFLES",
        "STARBUCKS", "DOMINOS", "PIZZA", "RESTAURANT", "CAFE",
        "COFFEE DAY", "THIRDWAVE", "THIRD WAVE COFFEE", "TWC INDIA", "BUNDL TECH"
    ]):
        return "Food"
    if any(x in text for x in [
        "UBER", "OLA", "RAPIDO", "ANI TECHNOLOGIES", "BMTC", "TUMMOC",
        "BUS PASS", "INDIAN OIL", "IOC", "PETROL", "FUEL"
    ]):
        return "Transport"
    if any(x in text for x in [
        "ZEPTO", "BLINKIT", "DMART", "BIGBASKET", "GROCERY", "GROFERS",
        "INSTAMART", "KIRANAKART", "AVENUE SUPERMARTS"
    ]):
        return "Groceries"
    if any(x in text for x in [
        "AMAZON", "AMZN", "FLIPKART", "FKART", "MYNTRA", "NYKAA",
        "FSN E-COMMERCE", "AJIO", "MEESHO", "INNOVATIVE RETAIL", "SHOPPING"
    ]):
        return "Shopping"
    if any(x in text for x in [
        "BESCOM", "ELECTRICITY", "ELEC SUPPLY", "WATER BILL", "BWSSB",
        "BILL PAYMENT", "RECHARGE", "BROADBAND", "JIOFIBER", "JIO FIBER",
        "RELIANCE JIO", "AIRTEL", "VI POSTPAID", "VODAFONE IDEA"
    ]):
        return "Bills and Utilities"
    if any(x in text for x in [
        "HOTSTAR", "STAR INDIA", "BMS MOVIE", "BOOKMYSHOW",
        "BIGTREE ENTERTAINMENT", "NETFLIX", "SPOTIFY"
    ]):
        return "Entertainment"
    if any(x in text for x in ["COLLEGE", "UNIVERSITY", "COURSE", "BOOKS", "EDUCATION"]):
        return "Education"
    if any(x in text for x in ["HOSPITAL", "PHARMACY", "MEDICAL", "CLINIC", "DOCTOR"]):
        return "Healthcare"
    return "Other"


def answer_question(question, df, debits, monthly_summary, total_income, net_cash_flow):
    q = question.lower().strip().rstrip("?!., ")

    if any(x in q for x in [
        "highest month", "most expensive month", "spent the most",
        "spend the most", "highest outflow", "monthly outflows",
        "highest spending month", "which month"
    ]):
        if monthly_summary.empty:
            return "There is no monthly data available yet."
        row = monthly_summary.loc[monthly_summary["Debit Outflows"].idxmax()]
        return (
            f"Your highest spending month was {row['Month']}, with "
            f"recorded debit outflows of ₹{row['Debit Outflows']:,.2f}."
        )

    if any(x in q for x in [
        "lowest month", "least spending month", "spent the least", "lowest outflow"
    ]):
        if monthly_summary.empty:
            return "There is no monthly data available yet."
        row = monthly_summary.loc[monthly_summary["Debit Outflows"].idxmin()]
        return (
            f"Your lowest spending month was {row['Month']}, with "
            f"recorded debit outflows of ₹{row['Debit Outflows']:,.2f}."
        )

    category_words = {
        "shopping": "Shopping", "food": "Food", "restaurant": "Food",
        "groceries": "Groceries", "grocery": "Groceries",
        "transport": "Transport", "travel": "Transport", "rent": "Rent",
        "investment": "Investments", "investments": "Investments",
        "entertainment": "Entertainment", "bills": "Bills and Utilities",
        "utilities": "Bills and Utilities", "cash withdrawal": "Cash Withdrawal",
        "education": "Education", "healthcare": "Healthcare",
        "medical": "Healthcare", "other": "Other",
    }

    if any(x in q for x in [
        "how much", "amount", "spend on", "spent on", "spending on",
        "expenses on", "expense on", "total for"
    ]):
        for keyword, category in category_words.items():
            if keyword in q:
                total = debits.loc[debits["Category"] == category, "Amount"].sum()
                return f"Your recorded {category} outflows total ₹{total:,.2f}."

    if any(x in q for x in [
        "where did most", "largest category", "biggest expense", "top category",
        "where most of my money", "category highest", "most of my money go",
        "largest expense"
    ]):
        totals = debits.groupby("Category")["Amount"].sum()
        if totals.empty:
            return "No debit category data is available."
        return (
            f"Your largest category by recorded debit amount is "
            f"{totals.idxmax()}: ₹{totals.max():,.2f}."
        )

    if any(x in q for x in [
        "category breakdown", "all categories", "breakdown", "spending categories"
    ]):
        totals = debits.groupby("Category")["Amount"].sum().sort_values(ascending=False)
        if totals.empty:
            return "No debit category data is available."
        return "Recorded debit outflows by category:\n" + "\n".join(
            f"- {cat}: ₹{amount:,.2f}" for cat, amount in totals.items()
        )

    if any(x in q for x in ["income", "money received", "credit", "received", "earnings"]):
        return f"Your recorded income is ₹{total_income:,.2f}."

    if any(x in q for x in [
        "cash flow", "net balance", "net cash", "income minus", "financial balance"
    ]):
        return f"Your recorded net cash flow is ₹{net_cash_flow:,.2f}."

    if any(x in q for x in [
        "transaction count", "number of transactions", "how many transactions",
        "transaction total", "how many records"
    ]):
        return f"Your dataset contains {len(df):,} valid transactions."

    if any(x in q for x in ["help", "what can you do", "examples"]):
        return (
            "Try asking:\n"
            "- Where did most of my money go?\n"
            "- How much did I spend on transport?\n"
            "- Which month did I spend the most?\n"
            "- How much income did I receive?\n"
            "- Show my category breakdown.\n"
            "- How many transactions do I have?"
        )

    return (
        "I don't recognize that question yet. Try asking about shopping, food, "
        "income, cash flow, transaction count, monthly outflows, or category breakdown."
    )


st.title("💰 SpendDNA")
st.subheader("Your Wallet's Financial Story")
st.write(
    "Upload a transaction CSV to explore your financial patterns, monthly outflows, "
    "and spending categories."
)
st.info(
    "Privacy tip: Use a copy of your transaction file with account numbers and other "
    "sensitive details removed."
)

uploaded_file = st.file_uploader("Upload your transaction CSV", type=["csv"])
if uploaded_file is None:
    st.info("Upload a CSV file to generate your dashboard.")
    st.stop()

try:
    df = pd.read_csv(uploaded_file)
except Exception as error:
    st.error(f"Unable to read this CSV file: {error}")
    st.stop()

df.columns = df.columns.astype(str).str.strip()
required_columns = {"Date", "Description", "Type", "Amount"}
missing_columns = required_columns - set(df.columns)
if missing_columns:
    st.error("Missing required columns: " + ", ".join(sorted(missing_columns)))
    st.write("Required columns are Date, Description, Type, and Amount.")
    st.stop()

original_count = len(df)

df["Date"] = pd.to_datetime(
    df["Date"].astype("string").str.strip(),
    format="mixed", dayfirst=True, errors="coerce"
)
df["Amount"] = (
    df["Amount"].astype("string")
    .str.replace(r"(?i)^rs\.?\s*", "", regex=True)
    .str.replace("₹", "", regex=False)
    .str.replace(",", "", regex=False)
    .str.strip()
)
df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
df["Type"] = (
    df["Type"].astype("string").str.strip().str.upper()
    .replace({"DR": "Debit", "DEBIT": "Debit", "CR": "Credit", "CREDIT": "Credit"})
)
df["Description"] = df["Description"].fillna("Unknown").astype(str)

df = df.drop_duplicates().dropna(subset=["Date", "Amount", "Type"]).copy()
df = df[df["Type"].isin(["Debit", "Credit"])].copy()
if df.empty:
    st.error("No valid Debit or Credit transactions were found.")
    st.stop()

df["Category"] = "Income"
debit_mask = df["Type"] == "Debit"
df.loc[debit_mask, "Category"] = df.loc[debit_mask, "Description"].apply(categorize_expense)

debits = df[df["Type"] == "Debit"].copy()
credits = df[df["Type"] == "Credit"].copy()
total_income = credits["Amount"].sum()
total_outflows = debits["Amount"].sum()
net_cash_flow = total_income - total_outflows

st.divider()
st.header("Financial Overview")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Recorded Income", f"₹{total_income:,.0f}")
col2.metric("Debit Outflows", f"₹{total_outflows:,.0f}")
col3.metric("Net Cash Flow", f"₹{net_cash_flow:,.0f}")
col4.metric("Transactions", f"{len(df):,}")
st.caption(
    f"Loaded {original_count:,} rows; {len(df):,} rows remain after cleaning and deduplication."
)

st.divider()
st.header("Spending Analysis")
if debits.empty:
    st.warning("No debit transactions are available to analyze.")
    category_summary = pd.DataFrame(columns=["Category", "Total_Spent", "Transaction_Count"])
else:
    category_summary = (
        debits.groupby("Category")
        .agg(Total_Spent=("Amount", "sum"), Transaction_Count=("Amount", "size"))
        .sort_values("Total_Spent", ascending=False)
        .reset_index()
    )
    left, right = st.columns(2)
    with left:
        st.subheader("Debit Outflows by Category")
        fig_category = px.bar(
            category_summary.sort_values("Total_Spent"),
            x="Total_Spent", y="Category", orientation="h",
            labels={"Total_Spent": "Amount (₹)", "Category": "Category"},
            title="Where the money went",
        )
        st.plotly_chart(fig_category, use_container_width=True)
    with right:
        st.subheader("Transaction Frequency")
        fig_frequency = px.pie(
            category_summary, names="Category", values="Transaction_Count",
            hole=0.45, title="Share of debit transactions",
        )
        st.plotly_chart(fig_frequency, use_container_width=True)
    st.subheader("Category Details")
    st.dataframe(
        category_summary.style.format({
            "Total_Spent": "₹{:,.2f}", "Transaction_Count": "{:,.0f}"
        }),
        use_container_width=True, hide_index=True,
    )

st.divider()
st.header("Monthly Trends")
df["Month"] = df["Date"].dt.to_period("M").astype(str)
monthly_summary = (
    df.pivot_table(index="Month", columns="Type", values="Amount", aggfunc="sum", fill_value=0)
    .reindex(columns=["Credit", "Debit"], fill_value=0)
    .rename(columns={"Credit": "Income", "Debit": "Debit Outflows"})
)
monthly_summary["Net Cash Flow"] = monthly_summary["Income"] - monthly_summary["Debit Outflows"]
monthly_summary = monthly_summary.reset_index()

left, right = st.columns(2)
with left:
    fig_month = px.bar(
        monthly_summary, x="Month", y=["Income", "Debit Outflows"], barmode="group",
        title="Monthly Income vs Debit Outflows",
        labels={"value": "Amount (₹)", "Month": "Month"},
    )
    st.plotly_chart(fig_month, use_container_width=True)
with right:
    fig_net = px.line(
        monthly_summary, x="Month", y="Net Cash Flow", markers=True,
        title="Monthly Net Cash Flow", labels={"Net Cash Flow": "Amount (₹)"},
    )
    fig_net.add_hline(y=0, line_dash="dash")
    st.plotly_chart(fig_net, use_container_width=True)

st.subheader("Monthly Summary")
st.dataframe(
    monthly_summary.style.format({
        "Income": "₹{:,.2f}", "Debit Outflows": "₹{:,.2f}",
        "Net Cash Flow": "₹{:,.2f}",
    }),
    use_container_width=True, hide_index=True,
)

st.divider()
st.header("Your Financial Story")
if not debits.empty and not category_summary.empty:
    top_category_row = category_summary.iloc[0]
    most_frequent_row = category_summary.loc[category_summary["Transaction_Count"].idxmax()]
    st.write(
        f"**Largest debit category:** {top_category_row['Category']} "
        f"(₹{top_category_row['Total_Spent']:,.0f})."
    )
    st.write(
        f"**Most frequent category:** {most_frequent_row['Category']} "
        f"({int(most_frequent_row['Transaction_Count'])} transactions)."
    )
if not monthly_summary.empty:
    highest = monthly_summary.loc[monthly_summary["Debit Outflows"].idxmax()]
    lowest = monthly_summary.loc[monthly_summary["Debit Outflows"].idxmin()]
    st.write(f"**Highest-outflow month:** {highest['Month']} (₹{highest['Debit Outflows']:,.0f}).")
    st.write(f"**Lowest-outflow month:** {lowest['Month']} (₹{lowest['Debit Outflows']:,.0f}).")
if net_cash_flow < 0:
    st.warning(
        "Recorded debit outflows exceed recorded credits. Review investments, cash withdrawals, "
        "transfers, and whether the uploaded file includes all relevant accounts before drawing conclusions."
    )
st.caption(
    "Categories are estimated from transaction descriptions. Review them before relying on the results. "
    "Recorded credits may not represent all sources of income."
)

st.divider()
st.header("Download Your Results")
download_data = df.drop(columns=["Month"], errors="ignore")
st.download_button(
    label="Download Cleaned Transactions CSV",
    data=download_data.to_csv(index=False).encode("utf-8-sig"),
    file_name="spenddna_cleaned_transactions.csv",
    mime="text/csv",
)

st.divider()
st.header("💬 Ask SpendDNA")
st.write("Ask questions about your uploaded transaction data.")
if "spenddna_messages" not in st.session_state:
    st.session_state.spenddna_messages = [{
        "role": "assistant",
        "content": (
            "Hi! 👋 I can help you understand your transactions. Try asking about your "
            "highest-outflow month, shopping, food, income, cash flow, or transaction count."
        ),
    }]

for message in st.session_state.spenddna_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Ask about your financial data...")
if question:
    st.session_state.spenddna_messages.append({"role": "user", "content": question})
    response = answer_question(
        question, df, debits, monthly_summary, total_income, net_cash_flow
    )
    st.session_state.spenddna_messages.append({"role": "assistant", "content": response})
    st.rerun()

st.divider()
st.header("🤖 Personalized Recommendations")
recommendations = []
if not debits.empty:
    shopping_amount = debits.loc[debits["Category"] == "Shopping", "Amount"].sum()
    food_amount = debits.loc[debits["Category"] == "Food", "Amount"].sum()
    investment_amount = debits.loc[debits["Category"] == "Investments", "Amount"].sum()
    shopping_share = shopping_amount / total_outflows * 100 if total_outflows > 0 else 0
    food_share = food_amount / total_outflows * 100 if total_outflows > 0 else 0

    if shopping_share >= 25:
        recommendations.append(
            f"🛍️ Shopping accounts for {shopping_share:.1f}% of recorded debit outflows. "
            "Review purchases and consider setting a budget that suits your needs."
        )
    if food_share >= 15:
        recommendations.append(
            f"🍽️ Food accounts for {food_share:.1f}% of recorded debit outflows. "
            "Review frequent food transactions to identify any optional spending."
        )
    if investment_amount > 0:
        recommendations.append(
            f"📈 You recorded ₹{investment_amount:,.0f} in investment-related outflows. "
            "Track these separately from everyday consumption."
        )
    if net_cash_flow < 0:
        recommendations.append(
            "💡 Recorded debit outflows exceed recorded credits. Check for transfers between accounts, "
            "cash withdrawals, and missing income before interpreting this as overspending."
        )
    other_amount = debits.loc[debits["Category"] == "Other", "Amount"].sum()
    if other_amount > 0:
        recommendations.append(
            f"🔎 Review ₹{other_amount:,.0f} categorized as Other. "
            "Correct categorization can improve your financial insights."
        )

if recommendations:
    for recommendation in recommendations:
        st.markdown(f"- {recommendation}")
else:
    st.info("Upload more transaction data to generate personalized suggestions.")

st.caption(
    "Recommendations are generated from transaction rules, not from a trained AI model. "
    "Review them before making financial decisions."
)
st.success("SpendDNA analysis is ready.")

