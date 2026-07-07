import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Sales by Product Type & Country", page_icon="📊", layout="centered")

# ─────────────────────────────────────────────
# Category keywords (from your existing categorisation work)
# ─────────────────────────────────────────────
CATEGORY_KEYWORDS = {
    'BAGS': ['BAG'],
    'SIGNS': ['SIGN'],
    'HOME DECOR': ['T-LIGHT', 'HOLDER', 'DECORATION', 'FRAME', 'ORNAMENT', 'HANGING', 'BOWL', 'DOORMAT', 'CUSHION'],
    'KITCHEN & DINING': ['MUG', 'PLATE', 'TEA', 'CUTLERY', 'TIN', 'JAR', 'BOTTLE', 'CAKE', 'BAKING', 'LUNCH'],
    'CHRISTMAS': ['CHRISTMAS', 'SANTA', 'XMAS'],
    'CARDS & WRAP': ['CARD', 'WRAP', 'GIFT TAG', 'RIBBON'],
    'STORAGE': ['BOX', 'STORAGE', 'DRAWER', 'CHEST'],
    'JEWELLERY & ACCESSORIES': ['NECKLACE', 'BRACELET', 'EARRING', 'RING'],
    'CHILDRENS & TOYS': ['CHILD', 'DOLLY', 'RABBIT', 'TREASURE', 'TOY'],
    'GARDEN & OUTDOOR': ['GARDEN', 'PARASOL', 'PLANT', 'NESTING'],
}


def categorise(desc, cats):
    if pd.isna(desc):
        return 'OTHER'
    d = desc.lower()
    for cat, kws in cats.items():
        for kw in kws:
            if kw.lower() in d:
                return cat
    return 'OTHER'


@st.cache_data
def load_and_prepare(file):
    df = pd.read_csv(file, skiprows=1)
    df['Total'] = df['Quantity'] * df['UnitPrice']
    df['Item Type'] = df['Description'].apply(lambda d: categorise(d, CATEGORY_KEYWORDS))
    return df


# ─────────────────────────────────────────────
# App
# ─────────────────────────────────────────────
st.title("📊 Sales by Product Type & Country")
st.markdown("Filter total sales by product type and/or country.")

uploaded_file = st.file_uploader("Upload sales CSV", type=["csv"])

if uploaded_file is None:
    st.info("Upload your sales CSV to get started.")
    st.stop()

df = load_and_prepare(uploaded_file)

# ── Dropdowns ─────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    product_options = ["All"] + sorted(df["Item Type"].unique().tolist())
    selected_product = st.selectbox("Product Type", product_options)

with col2:
    country_options = ["All"] + sorted(df["Country"].dropna().unique().tolist())
    selected_country = st.selectbox("Country", country_options)

# ── Filter data ───────────────────────────────
filtered = df.copy()
if selected_product != "All":
    filtered = filtered[filtered["Item Type"] == selected_product]
if selected_country != "All":
    filtered = filtered[filtered["Country"] == selected_country]

if filtered.empty:
    st.warning("No data matches this combination of filters.")
    st.stop()

# ── Chart ─────────────────────────────────────
st.subheader(f"Total Sales — {selected_product} / {selected_country}")

if selected_product == "All":
    # Show breakdown by product type
    chart_data = (filtered.groupby("Item Type")["Total"]
                  .sum()
                  .sort_values(ascending=False))
    x_label = "Item Type"
else:
    # Single product selected — show breakdown by country instead, for context
    chart_data = (filtered.groupby("Country")["Total"]
                  .sum()
                  .sort_values(ascending=False))
    x_label = "Country"

fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(chart_data.index, chart_data.values, color="steelblue")
ax.set_ylabel("Total Sales (£)")
ax.set_xlabel(x_label)
ax.set_title(f"Total Sales: {selected_product} / {selected_country}")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
st.pyplot(fig)

st.metric("Total Sales (£)", f"£{filtered['Total'].sum():,.2f}")
