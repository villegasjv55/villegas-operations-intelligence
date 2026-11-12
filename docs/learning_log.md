# Learning Log

## Day 1-2 (Nov 5, 2026)

**Concepts learned**
- Virtual environments (.venv) keep project packages separate
- .gitignore keeps raw data and secrets out of GitHub
- Loading CSVs into SQLite with pandas `to_sql`
- Summarize before joining, or joins duplicate rows and inflate revenue
- Verifying a metric by calculating it in both SQL and Pandas

**Errors and fixes**
- `invalid refspec`: two commands pasted on one line. Fix: run one command per line.
- `Password authentication is not supported`: GitHub needs a personal access token, not the account password.
- Commands did nothing while Streamlit was running. Fix: stop the app with Control + C first.

**What I can explain on my own**
- (fill in)


## Module 03: Seller & Logistics (Nov 5, 2026)

**Findings**
- Marketplace missed handoff rate: 9.4% of items reached the carrier after the seller's deadline.
- 634 sellers have 30+ orders. Median seller late rate: ___%. Bottom 10: ___% to ___%.
- Sellers missing the deadline on 10%+ of items: ___% late vs ___% for the rest.
- Slow is not the same as late: Amapá and Amazonas wait 26-27 days but only ~3% arrive late
  (promised dates are realistic, reviews stay at 4.24).
- Alagoas is the real problem: 24.5 days AND 21% late, reviews 3.85. Its promised dates are too optimistic.

**Concepts learned**
- Seller metrics are calculated per item, customer metrics per order
- Minimum sample size (30+ orders) so tiny sellers don't look extreme
- Streamlit turns files in pages/ into sidebar pages
- If code shows up twice in a file, Python fails with SyntaxError: clear and paste once