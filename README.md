# Data Analysis & Visualization Dashboard

A professional data analysis and visualization dashboard built with Flask, Pandas, and Plotly. Perfect for business intelligence and real-time analytics.

## Features

- 📊 **Interactive Charts** - Line charts, bar charts, and more using Plotly
- 📈 **Real-time Analytics** - Live statistics and KPI cards
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile
- 🎨 **Modern UI** - Beautiful gradient design with smooth animations
- 🔌 **REST API** - Easy-to-use API endpoints for data
- 📦 **Production Ready** - Built with best practices

## Tech Stack

- **Backend**: Flask (Python)
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly
- **Frontend**: HTML5, CSS3, JavaScript
- **Deployment**: Gunicorn

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/adityashm/data-analysis-dashboard.git
   cd data-analysis-dashboard
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open in browser**
   Navigate to `http://localhost:5000`

## Project Structure

```
data-analysis-dashboard/
├── app.py              # Main Flask application
├── requirements.txt    # Project dependencies
├── templates/
│   └── index.html     # Dashboard HTML template
└── README.md          # Project documentation
```

## API Endpoints

- `GET /` - Dashboard homepage
- `GET /api/data` - Get raw data (JSON)
- `GET /api/charts` - Get all charts data
- `GET /api/stats` - Get statistics and KPIs

## Example Response

```json
{
  "total_sales": 940000,
  "total_expenses": 501000,
  "total_profit": 439000,
  "avg_margin": 36.9,
  "max_sales": 95000,
  "min_sales": 45000
}
```

## Customization

Edit the `generate_sample_data()` function in `app.py` to connect your own data source:

```python
# Replace with your database/API calls
df = pd.read_csv('your_data.csv')
# or
df = pd.read_sql('SELECT * FROM your_table', connection)
```

## Deployment

### Deploy to Heroku

```bash
heroku create your-app-name
heroku login
git push heroku main
```

### Deploy to Railway

```bash
railway login
railway init
railway up
```

## License

MIT License - feel free to use this project for your portfolio!

## Author

Aditya Sharma
- GitHub: https://github.com/adityashm
- Portfolio: https://adityashm.tech

## Live Demo

Visit: [Live Dashboard](https://data-analysis-dashboard-demo.herokuapp.com)
