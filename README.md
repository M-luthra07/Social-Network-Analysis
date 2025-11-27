# Social Network Analysis Dashboard

A comprehensive web application for analyzing and visualizing startup ecosystems. This tool processes company data to generate interactive network graphs, statistical plots, and social network analysis (SNA) metrics.

## 🚀 Features

- **Interactive Network Visualization**: Explore connections between companies and industries using a dynamic graph (powered by Vis.js).
- **Data Dashboard**: Visual insights including:
  - Companies founded per year.
  - Top startup cities and industries.
  - Word clouds from company descriptions.
  - City-Industry trends.
- **SNA Metrics**: Deep dive into network properties:
  - **Degree Centrality**: Identify the most connected hubs.
  - **Betweenness Centrality**: Find key bridges in the network.
  - **K-Core Decomposition**: Analyze network resilience.
- **Company Details**: Click on any node in the network to view detailed company information (Founders, Funding, Year Founded, etc.).
- **Search**: Quickly find specific companies within the dataset.

## 🛠️ Tech Stack

- **Backend**: Python (Flask)
- **Data Processing**: Pandas, NetworkX
- **Visualization**: Matplotlib, WordCloud, Vis.js
- **Frontend**: HTML5, CSS3, JavaScript (Bootstrap)

## 📦 Installation

1.  **Clone the repository**
    ```bash
    git clone <repository-url>
    cd "Social Network Analysis"
    ```

2.  **Install Dependencies**
    Ensure you have Python installed. It is recommended to use a virtual environment.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Prepare Data**
    Ensure `data.csv` is present in the root directory. The CSV should contain columns like:
    - `Company_Name`
    - `Founder_Name`
    - `Funding_Type`
    - `Year_Founded`
    - `Industry_Type`
    - `Short_Desription`
    - `City`
    - `Size_of_Company`

## 🏃 Usage

1.  **Run the Application**
    ```bash
    python app.py
    ```

2.  **Access the Dashboard**
    Open your web browser and navigate to:
    `http://localhost:5000`

## 📂 Project Structure

```
Social Network Analysis/
├── app.py                 # Main Flask application and logic
├── data.csv               # Input dataset
├── requirements.txt       # Python dependencies
├── static/
│   ├── css/               # Stylesheets
│   ├── js/                # JavaScript files (Network viz, interactions)
│   └── plots/             # Generated static plots (saved by Matplotlib)
└── templates/
    ├── dashboard.html     # Main dashboard template
    └── summarize.html     # Summary view template
```

## 📊 Methodology

- **Network Construction**: The graph is constructed by linking companies within the same industry (sampled for performance).
- **Metrics Calculation**:
  - *Degree*: Number of direct connections.
  - *Betweenness*: Frequency of a node acting as a bridge along the shortest path between two other nodes.
  - *K-Core*: A maximal subgraph where every node has at least degree k.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
