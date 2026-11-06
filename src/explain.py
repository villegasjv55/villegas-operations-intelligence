"""Plain-English explanations shown inside the app."""
import streamlit as st

# ---------- Every number in the app, defined once ----------
KPIS = [
    ("Revenue", "All the money customers paid for products.",
     "Sum of every item's price",
     "Shipping is not included. This is not profit: Olist does not share product costs."),
    ("Orders", "How many separate purchases were made.",
     "Count of distinct order IDs",
     "One order can contain several items, so each order is counted once."),
    ("Average order value", "What a typical order is worth.",
     "Revenue ÷ orders that contain items",
     "Canceled orders with no items are left out."),
    ("Freight cost", "What customers paid for shipping.",
     "Sum of every item's freight value",
     "Also shown as a % of revenue."),
    ("On-time delivery rate", "Share of delivered orders that arrived by the promised date.",
     "On-time delivered orders ÷ all delivered orders",
     "Arriving any time on the promised day counts as on time. Undelivered orders are excluded."),
    ("Average review", "How happy customers were, from 1 to 5 stars.",
     "Average of each order's review score",
     "Orders with two reviews are averaged first so they don't count twice."),
    ("Days late", "How many days after the promised date an order arrived.",
     "Delivery day − promised day",
     "Only calculated for late orders."),
    ("% 1-2 stars (detractor rate)", "Share of customers who were clearly unhappy.",
     "1 and 2 star reviews ÷ all reviews", ""),
    ("Delivery time", "How long the customer waited in total.",
     "Delivery date − purchase date", "Delivered orders only."),
    ("Seller handoff time", "How long sellers take to ship after payment is approved.",
     "Carrier pickup date − payment approval date", ""),
    ("Missed handoff rate", "How often sellers gave the package to the carrier after their deadline.",
     "Items handed over after the shipping limit ÷ all items handed over",
     "Measured per item, because each item has its own seller."),
]


def kpi_table_markdown():
    lines = ["| Number | What it means | How it is calculated | Good to know |",
             "|---|---|---|---|"]
    for name, meaning, formula, note in KPIS:
        lines.append(f"| **{name}** | {meaning} | {formula} | {note} |")
    return "\n".join(lines)


# ---------- How It Works page ----------
WHAT_IT_IS = """
**Villegas Operations Intelligence** is an operations analytics app. Think of it as the screen a
marketplace's operations team would open every morning to see how the business is doing:
sales, deliveries, sellers, and customer happiness.

It is built on **real, anonymized data from Olist**, a Brazilian online marketplace, and it is designed
to answer one business question:

> **Late deliveries are hurting customer satisfaction. Where, why, and what should we fix first?**

Every page, chart and number in the app helps answer that question.
"""

THE_DATA = """
- **Source:** the Olist Brazilian E-Commerce Public Dataset, published free on Kaggle.
- **Size:** about **100,000 orders** placed between **2016 and 2018**.
- **Real but private:** customer and seller names were removed (anonymized). Seller IDs look like
  random codes for that reason.
- **Money:** all values are in **Brazilian reais (R$)**, not US dollars.
- **Nine connected tables:** orders, order items, customers, sellers, products, payments, reviews,
  zip-code locations, and an English translation of product categories. They are loaded into a
  SQLite database and connected through shared ID columns.
- **Fixed snapshot:** the data does not update. It is a historical record, which makes every number
  reproducible.
"""

ORDER_FLOW = """
Every order passes through five steps, and each one has a date in the data.
**The gap between any two steps is a place a delay can happen.**

1. **Purchase:** the customer buys and is shown a **promised delivery date**.
2. **Payment approved.**
3. **Handoff:** the seller gives the package to the shipping company before a **shipping deadline**.
4. **Delivery:** the shipping company brings it to the customer.
5. **Review:** the customer rates the experience from 1 to 5 stars.

The app compares the **actual delivery date** to the **promised date** to decide whether an order was
late, then connects that to the customer's review.
"""

VERIFY = """
Numbers in a business report are only useful if they are right, so every key number is checked:

- **Calculated two different ways.** Each main number is calculated once in **SQL** from the raw
  tables and once in **Python (Pandas)** from the cleaned tables. The two answers must match.
- **Automated tests.** A set of tests re-checks the numbers every time the code changes: that both
  methods agree, that no order is counted twice, and that every group adds up to the total.
- **Data quality checks.** Before any calculation, the raw data is scanned for problems such as
  missing dates, impossible dates, duplicate records and orders with more than one review or payment.
- **No double counting.** Items, payments and reviews are summarized per order *before* being joined,
  so an order with three items is never counted three times.
"""

FILTERS = """
- **Purchase months (slider):** pick the range of months to analyze. Every number, chart and summary
  on every page updates to match, and the choice stays the same when you switch pages.
- **Exclude incomplete months (checkbox):** the very first and very last months of the data have only
  a handful of orders. Including them makes trends look like crashes, so they are hidden by default.
  A month needs at least 500 orders to count as complete.
- **"What this shows" boxes:** these are written automatically from the numbers on screen, so they
  change when you change the filters.
"""

LIMITS = """
Being upfront about what data cannot tell you is part of the job:

- **No profit.** Olist does not share product costs, so the app reports revenue and shipping costs,
  not profit.
- **No inventory.** There is no stock data, so stock levels cannot be analyzed.
- **Reviews are optional.** A small share of orders have no review, and review comments are in
  Portuguese, so the app uses the 1-5 star score.
- **Correlation, not proof.** The app shows that late orders get worse reviews and that some sellers
  miss deadlines more. Those patterns are strong evidence, but a real company would confirm causes
  before acting.
- **Historical data.** The numbers describe 2016-2018, not today.
"""

ABOUT = """
Built by **Juan Villegas** under **Villegas Analytics**, as a portfolio project combining eight years of
operations and project management experience with Information Systems studies.

**Built with:** Python, SQL, SQLite, Pandas, Streamlit, Plotly, pydeck, pytest, and Git/GitHub.

**Data credit:** Olist Brazilian E-Commerce Public Dataset (Kaggle), licensed CC BY-NC-SA 4.0.
"""

# ---------- "How to read this page" panels ----------
PAGE_HELP = {
    "Executive Dashboard": """
**What this page is for:** a quick morning check of the whole business: sales, deliveries and
customer happiness.

- **Top cards:** the six headline numbers for the months chosen in the sidebar.
- **Monthly revenue:** each bar is one month of sales. The **amber bar** is the best month.
- **On-time delivery rate by month:** the share of orders that arrived by their promised date.
  Dips mean delivery problems that month.
- **Late deliveries vs. customer satisfaction:** delivered orders grouped by how late they arrived,
  with the average star rating for each group. **This is the main finding of the project:** the later
  the order, the lower the rating.
- **"What this shows" boxes:** written automatically from the numbers, so they change with the filters.

All money is in Brazilian reais (R$). Exact definitions are on the **How It Works** page.
""",
    "Seller & Logistics": """
**What this page is for:** finding which sellers and which regions cause late deliveries.

- **Top cards:** how many sellers are active, how often they miss their shipping deadline, how fast
  they hand packages to the carrier, and how long customers wait in total.
- **3D map:** each column is one Brazilian state, placed where its customers live.
  **Taller = longer wait. Redder = more orders arrive late.** Hover a column for its numbers,
  scroll to zoom, hold Ctrl and drag to tilt.
- **Slow is not the same as late:** a tall but cyan column means customers wait a long time but were
  told to expect it. A red column means the promised date is often missed.
- **Bubble chart:** each bubble is one seller with 30+ orders. Further right = misses the shipping
  deadline more often. Higher = more late deliveries. Bigger = more orders. Red = low reviews.
- **Bottom 10 list:** the sellers with the highest late-delivery rate, the list an operations team
  would follow up with first.

Sellers need at least 30 orders to be ranked, so a seller with 2 orders and 1 late one is not
treated as the worst on the platform.
""",
    "How It Works": """
This page explains the app itself: the data, every number, how the numbers are checked,
and what the data cannot tell you.
""",
}


def how_to_read(page_title):
    """Collapsible guide shown at the top of each page."""
    text = PAGE_HELP.get(page_title)
    if text:
        with st.expander("How to read this page", icon=":material/info:"):
            st.markdown(text)