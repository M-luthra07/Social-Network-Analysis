import os
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import networkx as nx
from wordcloud import WordCloud
from flask import Flask, render_template, url_for

app = Flask(__name__)

# ---------------- CONFIG ----------------
DATA_PATH = "data.csv"
PLOT_DIR = os.path.join("static", "plots")
os.makedirs(PLOT_DIR, exist_ok=True)

# Performance knobs
MAX_NETWORK_NODES = 300  # nodes for drawn network
PER_INDUSTRY_LIMIT = 12  # sample per industry for graph
BETWEENNESS_K = 200      # for approximate betweenness if needed
TOP_N = 10
TOP_CITIES_FOR_TRENDS = 6


# ---------------- HELPERS ----------------
def save_fig(fig, filename, tight=True):
    path = os.path.join(PLOT_DIR, filename)
    if tight:
        fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_exists(name):
    return os.path.exists(os.path.join(PLOT_DIR, name))


def ensure_col(df, col):
    if col not in df.columns:
        df[col] = pd.NA
    return df


# ---------------- LOAD DATA ----------------
df = pd.read_csv(DATA_PATH, low_memory=False)

# Ensure columns exist we expect
for c in [
    "Company_Name", "Founder_Name", "Funding_Type", "Year_Founded",
    "Industry_Type", "Short_Desription", "City", "Size_of_Company"
]:
    ensure_col(df, c)

df["Company_Name"] = df["Company_Name"].astype(str).str.strip()
df["Founder_Name"] = df["Founder_Name"].astype(str).str.strip()
df["Funding_Type"] = df["Funding_Type"].fillna("Unknown").astype(str).str.strip()
df["Industry_Type"] = df["Industry_Type"].fillna("Unknown").astype(str).str.strip()
df["City"] = df["City"].fillna("Unknown").astype(str).str.strip()
df["Year_Founded"] = pd.to_numeric(df["Year_Founded"], errors="coerce").astype("Int64")

# KPIs
TOTAL_COMPANIES = df["Company_Name"].nunique()
TOTAL_FOUNDERS = df["Founder_Name"].nunique()
MOST_COMMON_CITY = df["City"].mode().iloc[0] if not df["City"].mode().empty else "Unknown"
MOST_COMMON_INDUSTRY = df["Industry_Type"].mode().iloc[0] if not df["Industry_Type"].mode().empty else "Unknown"


# ---------------- PLOTS & CALCULATIONS ----------------
# 1) Companies Founded Per Year
def plot_companies_per_year():
    fname = "founded_per_year.png"
    if plot_exists(fname):
        return fname

    yearly = df["Year_Founded"].dropna().astype(int).value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(9, 3.8))
    ax.plot(yearly.index, yearly.values, marker="o", linewidth=1.5)
    ax.set_title("Companies Founded Per Year")
    ax.set_xlabel("Year")
    ax.set_ylabel("Count")
    ax.grid(alpha=0.2)
    return save_fig(fig, fname)


# 2) Top Cities
def plot_top_cities():
    fname = "top_10_cities.png"
    if plot_exists(fname):
        return fname

    counts = df["City"].value_counts().nlargest(TOP_N)
    fig, ax = plt.subplots(figsize=(8, 3.6))
    counts.plot(kind="bar", ax=ax)
    ax.set_title(f"Top {TOP_N} Startup Cities")
    ax.set_ylabel("Company Count")
    return save_fig(fig, fname)


# 3) Top Industries
def plot_top_industries():
    fname = "top_10_industries.png"
    if plot_exists(fname):
        return fname

    counts = df["Industry_Type"].value_counts().nlargest(TOP_N)
    fig, ax = plt.subplots(figsize=(8, 3.6))
    counts.plot(kind="bar", ax=ax)
    ax.set_title(f"Top {TOP_N} Industries")
    ax.set_ylabel("Company Count")
    return save_fig(fig, fname)


# Build light sampled graph
def build_light_graph(max_nodes=MAX_NETWORK_NODES):
    G = nx.Graph()
    added = 0
    for industry, group in df.groupby("Industry_Type"):
        companies = group["Company_Name"].dropna().unique().tolist()[:PER_INDUSTRY_LIMIT]
        for comp in companies:
            if added >= max_nodes:
                break
            G.add_node(comp, industry=industry)
            added += 1
        for i in range(len(companies)):
            for j in range(i + 1, len(companies)):
                G.add_edge(companies[i], companies[j])
            if added >= max_nodes:
                break
    return G


# 4) Network PNG
def plot_network():
    fname = "network_sampled_color.png"
    if plot_exists(fname):
        return fname

    G = build_light_graph()
    if G.number_of_nodes() == 0:
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.text(0.5, 0.5, "No network data", ha="center", va="center")
        ax.axis("off")
        return save_fig(fig, fname)

    pos = nx.spring_layout(G, seed=42)
    degrees = dict(nx.degree(G))
    industries = [G.nodes[n]["industry"] for n in G.nodes()]
    unique = sorted(set(industries))
    cmap = plt.get_cmap("tab20")
    color_map = {k: cmap(i / len(unique)) for i, k in enumerate(unique)}
    node_colors = [color_map[G.nodes[n]["industry"]] for n in G.nodes()]
    node_sizes = [50 + 5 * degrees.get(n, 0) for n in G.nodes()]

    fig, ax = plt.subplots(figsize=(7, 7))
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors, alpha=0.85, ax=ax)
    nx.draw_networkx_edges(G, pos, alpha=0.15, ax=ax)
    ax.set_title("Company Network (sampled) — Color = Industry")
    ax.axis("off")
    return save_fig(fig, fname)


# 5) Wordcloud
def plot_wordcloud():
    fname = "wordcloud.png"
    if plot_exists(fname):
        return fname

    texts = df["Short_Desription"].dropna().astype(str)
    if texts.empty:
        fig, ax = plt.subplots(figsize=(8, 3.8))
        ax.text(0.5, 0.5, "No descriptions", ha="center", va="center")
        ax.axis("off")
        return save_fig(fig, fname)

    text = " ".join(texts.tolist())
    wc = WordCloud(width=900, height=400, background_color="white", collocations=False).generate(text)
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    ax.set_title("Common Keywords in Company Descriptions")
    return save_fig(fig, fname)


# 6) Top City + Industry combinations
def plot_city_industry_combos():
    fname = "top_city_industry.png"
    if plot_exists(fname):
        return fname

    combos = df.groupby(["City", "Industry_Type"]).size().reset_index(name="count")
    top = combos.sort_values("count", ascending=False).head(12)
    labels = top.apply(lambda r: f"{r['City']} — {r['Industry_Type']}", axis=1)

    fig, ax = plt.subplots(figsize=(9, 3.8))
    ax.barh(range(len(top)), top["count"].values, color="#4e79a7")
    ax.set_yticks(range(len(top)))
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_title("Top City + Industry combinations")
    return save_fig(fig, fname)


# 7) Year by city trends
def plot_year_by_city_trends():
    fname = "year_by_city_trends.png"
    if plot_exists(fname):
        return fname

    ydf = df.dropna(subset=["Year_Founded"])
    top_cities = df["City"].value_counts().nlargest(TOP_CITIES_FOR_TRENDS).index.tolist()
    if not top_cities:
        return plot_companies_per_year()

    pivot = (
        ydf[ydf["City"].isin(top_cities)]
        .groupby(["Year_Founded", "City"])
        .size()
        .unstack(fill_value=0)
    )

    fig, ax = plt.subplots(figsize=(9, 4))
    for city in pivot.columns:
        ax.plot(pivot.index, pivot[city], marker="o", linewidth=1, label=city)
    ax.set_title("Companies Founded Per Year — Top Cities")
    ax.set_xlabel("Year")
    ax.set_ylabel("Count")
    ax.legend(ncol=2, fontsize="small")
    return save_fig(fig, fname)


# 8) Compute SNA metrics
def compute_sna_metrics():
    G = build_light_graph(max_nodes=1000)

    # Degree centrality
    deg_c = nx.degree_centrality(G) if G.number_of_nodes() > 0 else {}
    deg_sorted = sorted(deg_c.items(), key=lambda x: x[1], reverse=True)[:TOP_N]
    degree_labels = [x[0] for x in deg_sorted]
    degree_values = [x[1] for x in deg_sorted]

    # Betweenness
    btw_c = {}
    if G.number_of_nodes() > 0:
        try:
            if G.number_of_nodes() <= 300:
                btw_c = nx.betweenness_centrality(G)
            else:
                k = min(BETWEENNESS_K, G.number_of_nodes())
                btw_c = nx.betweenness_centrality(G, k=k, seed=42)
        except Exception:
            btw_c = deg_c

    btw_sorted = sorted(btw_c.items(), key=lambda x: x[1], reverse=True)[:TOP_N]
    btw_labels = [x[0] for x in btw_sorted]
    btw_values = [x[1] * 1000 for x in btw_sorted]  # scaled

    # K-core
    kcore_dict = {}
    try:
        if G.number_of_nodes() > 0:
            kcore_dict = nx.core_number(G)
    except Exception:
        kcore_dict = {}
    kcore_sorted = sorted(kcore_dict.items(), key=lambda x: x[1], reverse=True)[:TOP_N]
    kcore_labels = [x[0] for x in kcore_sorted]
    kcore_values = [x[1] for x in kcore_sorted]

    # Industry neighbor diversity
    industry_neighbor_count = {}
    for n in G.nodes():
        nbrs = list(G.neighbors(n))
        nbr_ind = set([G.nodes[x].get("industry", "Unknown") for x in nbrs])
        industry_neighbor_count[n] = len(nbr_ind)

    bridges_points = []
    for n in G.nodes():
        deg = deg_c.get(n, 0)
        nind = industry_neighbor_count.get(n, 0)
        industry = G.nodes[n].get("industry", "Unknown")
        bridges_points.append({
            "company": n,
            "degree": deg,
            "neighbor_industry_count": nind,
            "industry": industry
        })

    # Funding vs influence
    centrality_df = pd.DataFrame(list(deg_c.items()), columns=["Company_Name", "deg_c"]).set_index("Company_Name")
    unique_companies = df.drop_duplicates(subset=["Company_Name"]).set_index("Company_Name")
    merged = unique_companies.join(centrality_df, how="left").fillna({"deg_c": 0})
    funding_group = merged.groupby("Funding_Type")["deg_c"].mean().sort_values(ascending=False).head(12)
    funding_labels = funding_group.index.tolist()
    funding_values = funding_group.values.tolist()

    # Top dropdowns
    top_cities = df["City"].value_counts().nlargest(TOP_CITIES_FOR_TRENDS).index.tolist()
    top_industries = df["Industry_Type"].value_counts().nlargest(20).index.tolist()

    return {
        "degree": {"labels": degree_labels, "values": degree_values},
        "betweenness": {"labels": btw_labels, "values": btw_values},
        "kcore": {"labels": kcore_labels, "values": kcore_values},
        "bridges_scatter": bridges_points,
        "funding_vs_influence": {"labels": funding_labels, "values": funding_values},
        "top_cities": top_cities,
        "top_industries": top_industries
    }


# ---------------- GENERATE PLOTS ----------------
plot_companies_per_year()
plot_top_cities()
plot_top_industries()
network_png = plot_network()
wordcloud_png = plot_wordcloud()
plot_city_industry_combos()
plot_year_by_city_trends()

# Compute SNA metrics
sna_metrics = compute_sna_metrics()


# ---------------- FLASK ROUTE ----------------
@app.route("/")
def dashboard():
    chart_data = {
        "founded_per_year": {"img": url_for('static', filename="plots/founded_per_year.png")},
        "top_cities": {"img": url_for('static', filename="plots/top_10_cities.png")},
        "top_industries": {"img": url_for('static', filename="plots/top_10_industries.png")},
        "network_img": {"img": url_for('static', filename="plots/network_sampled_color.png")},
        "wordcloud_img": {"img": url_for('static', filename="plots/wordcloud.png")},
        "city_industry_img": {"img": url_for('static', filename="plots/top_city_industry.png")},
        "year_by_city_trends_img": {"img": url_for('static', filename="plots/year_by_city_trends.png")},
        "degree": sna_metrics["degree"],
        "betweenness": sna_metrics["betweenness"],
        "kcore": sna_metrics["kcore"],
        "bridges_scatter": sna_metrics["bridges_scatter"],
        "funding_vs_influence": sna_metrics["funding_vs_influence"],
        "top_cities_list": sna_metrics["top_cities"],
        "top_industries_list": sna_metrics["top_industries"]
    }

    kpi = {
        "total_companies": TOTAL_COMPANIES,
        "total_founders": TOTAL_FOUNDERS,
        "top_city": MOST_COMMON_CITY,
        "top_industry": MOST_COMMON_INDUSTRY
    }

    return render_template("dashboard.html", chart_data=chart_data, kpi=kpi)


# ---------------- API ROUTES ----------------
@app.route("/api/network")
def api_network():
    # Build a slightly larger graph for the interactive view
    G = build_light_graph(max_nodes=500)
    
    nodes = []
    for n in G.nodes():
        industry = G.nodes[n].get("industry", "Unknown")
        nodes.append({
            "id": n,
            "label": n,
            "group": industry,
            "title": f"{n} ({industry})" # Tooltip
        })
        
    edges = []
    for u, v in G.edges():
        edges.append({"from": u, "to": v})
        
    return {"nodes": nodes, "edges": edges}

@app.route("/api/search")
def api_search():
    from flask import request
    query = request.args.get("q", "").lower()
    if not query:
        return {"results": []}
        
    # Simple substring match
    matches = df[df["Company_Name"].str.lower().str.contains(query, na=False)]
    results = matches["Company_Name"].head(10).tolist()
    return {"results": results}

@app.route("/api/company/<name>")
def api_company_details(name):
    row = df[df["Company_Name"] == name]
    if row.empty:
        return {"error": "Company not found"}, 404
        
    data = row.iloc[0].to_dict()
    # Clean up NaN values
    clean_data = {k: (v if pd.notna(v) else "Unknown") for k, v in data.items()}
    
    # Add some computed metrics if available
    # (Re-computing centrality for just one node is expensive, so we'll skip or use pre-computed if we had it)
    
    return clean_data

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
