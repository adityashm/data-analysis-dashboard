from flask import Flask, render_template, jsonify, request
import plotly.graph_objects as go
import plotly.express as px
import json
import sqlite3
from datetime import datetime, timedelta
from functools import wraps
import logging
import os
import random
import csv
from io import StringIO

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
DATABASE = 'analytics.db'

# ============ Database Setup ============
def get_db_connection():
    """Get database connection with row factory"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with sample data"""
    if not os.path.exists(DATABASE):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                product_category TEXT NOT NULL,
                sales REAL NOT NULL,
                expenses REAL NOT NULL,
                units_sold INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Generate 12 months of realistic data with multiple categories
        categories = ['Electronics', 'Clothing', 'Home & Garden', 'Sports']
        base_date = datetime.now() - timedelta(days=365)
        
        sample_data = []
        for i in range(365):
            current_date = base_date + timedelta(days=i)
            for category in categories:
                base_sales = random.randint(2000, 8000)
                # Add seasonal trend
                seasonal_factor = 100 * (0.5 * (i % 30) / 30)
                sales = base_sales + seasonal_factor
                expenses = sales * random.uniform(0.5, 0.7)
                units = random.randint(10, 100)
                sample_data.append((current_date.strftime('%Y-%m-%d'), category, sales, expenses, units))
        
        cursor.executemany('INSERT INTO sales_data (date, product_category, sales, expenses, units_sold) VALUES (?, ?, ?, ?, ?)', sample_data)
        conn.commit()
        conn.close()
        logger.info("Database initialized with sample data")

# ============ Data Analysis Functions ============
def get_monthly_data(start_date=None, end_date=None):
    """Get aggregated monthly data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = '''
        SELECT 
            strftime('%Y-%m', date) as month,
            SUM(sales) as total_sales,
            SUM(expenses) as total_expenses,
            SUM(units_sold) as total_units,
            COUNT(DISTINCT product_category) as categories
        FROM sales_data
    '''
    
    if start_date or end_date:
        conditions = []
        if start_date:
            conditions.append(f"date >= '{start_date}'")
        if end_date:
            conditions.append(f"date <= '{end_date}'")
        query += " WHERE " + " AND ".join(conditions)
    
    query += " GROUP BY month ORDER BY month"
    
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    
    data = {
        'months': [],
        'sales': [],
        'expenses': [],
        'profit_margin': [],
        'units': []
    }
    
    for row in results:
        profit = row['total_sales'] - row['total_expenses']
        margin = (profit / row['total_sales'] * 100) if row['total_sales'] > 0 else 0
        data['months'].append(row['month'])
        data['sales'].append(round(row['total_sales'], 2))
        data['expenses'].append(round(row['total_expenses'], 2))
        data['profit_margin'].append(round(margin, 2))
        data['units'].append(row['total_units'])
    
    return data

def get_category_breakdown():
    """Get sales breakdown by category"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            product_category,
            SUM(sales) as total_sales,
            SUM(expenses) as total_expenses,
            COUNT(*) as transactions
        FROM sales_data
        GROUP BY product_category
        ORDER BY total_sales DESC
    ''')
    
    results = cursor.fetchall()
    conn.close()
    
    return [{
        'category': row['product_category'],
        'sales': round(row['total_sales'], 2),
        'expenses': round(row['total_expenses'], 2),
        'profit': round(row['total_sales'] - row['total_expenses'], 2),
        'transactions': row['transactions']
    } for row in results]

def get_advanced_stats():
    """Calculate advanced statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            SUM(sales) as total_sales,
            SUM(expenses) as total_expenses,
            AVG(sales) as avg_sales,
            MAX(sales) as max_sales,
            MIN(sales) as min_sales,
            COUNT(*) as total_records,
            SUM(units_sold) as total_units,
            COUNT(DISTINCT DATE(date)) as trading_days
        FROM sales_data
    ''')
    
    result = cursor.fetchone()
    conn.close()
    
    total_sales = result['total_sales']
    total_expenses = result['total_expenses']
    profit = total_sales - total_expenses
    margin = (profit / total_sales * 100) if total_sales > 0 else 0
    trading_days = result['trading_days'] if result['trading_days'] > 0 else 1
    
    return {
        'total_sales': round(total_sales, 2),
        'total_expenses': round(total_expenses, 2),
        'total_profit': round(profit, 2),
        'profit_margin': round(margin, 2),
        'avg_daily_sales': round(result['avg_sales'], 2),
        'max_daily_sales': round(result['max_sales'], 2),
        'min_daily_sales': round(result['min_sales'], 2),
        'total_units': result['total_units'],
        'trading_days': trading_days,
        'avg_units_per_day': round(result['total_units'] / trading_days, 2)
    }

# ============ Chart Generation ============
def create_sales_trend_chart(data):
    """Create sales vs expenses trend chart"""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data['months'], y=data['sales'], 
        mode='lines+markers', name='Sales',
        line=dict(color='#3B82F6', width=3),
        marker=dict(size=8, symbol='circle'),
        hovertemplate='<b>%{x}</b><br>Sales: $%{y:,.0f}<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=data['months'], y=data['expenses'],
        mode='lines+markers', name='Expenses',
        line=dict(color='#EF4444', width=3),
        marker=dict(size=8, symbol='diamond'),
        hovertemplate='<b>%{x}</b><br>Expenses: $%{y:,.0f}<extra></extra>'
    ))
    fig.update_layout(
        title='Sales vs Expenses Trend',
        xaxis_title='Month',
        yaxis_title='Amount ($)',
        hovermode='x unified',
        template='plotly_white',
        height=450,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    return fig

def create_profit_margin_chart(data):
    """Create profit margin trend chart"""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data['months'], y=data['profit_margin'],
        mode='lines+markers', name='Profit Margin %',
        line=dict(color='#10B981', width=3),
        fill='tozeroy',
        marker=dict(size=8),
        hovertemplate='<b>%{x}</b><br>Margin: %{y:.2f}%<extra></extra>'
    ))
    fig.update_layout(
        title='Profit Margin Trend',
        xaxis_title='Month',
        yaxis_title='Profit Margin (%)',
        template='plotly_white',
        height=450,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    return fig

def create_category_chart(categories):
    """Create category breakdown chart"""
    fig = go.Figure()
    cat_names = [c['category'] for c in categories]
    cat_sales = [c['sales'] for c in categories]
    
    fig.add_trace(go.Bar(
        x=cat_names, y=cat_sales,
        marker=dict(color=cat_sales, colorscale='Viridis', showscale=True),
        text=[f'${x:,.0f}' for x in cat_sales],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Sales: $%{y:,.0f}<extra></extra>'
    ))
    fig.update_layout(
        title='Sales by Product Category',
        xaxis_title='Category',
        yaxis_title='Sales ($)',
        template='plotly_white',
        height=450,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    return fig

def create_daily_units_chart(data):
    """Create units sold trend"""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=data['months'], y=data['units'],
        marker=dict(color='#8B5CF6'),
        hovertemplate='<b>%{x}</b><br>Units: %{y:,.0f}<extra></extra>'
    ))
    fig.update_layout(
        title='Units Sold by Month',
        xaxis_title='Month',
        yaxis_title='Units Sold',
        template='plotly_white',
        height=450,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    return fig

# ============ API Routes ============
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats')
def get_stats_api():
    """Get comprehensive statistics"""
    try:
        stats = get_advanced_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error fetching stats: {str(e)}")
        return jsonify({'error': 'Failed to fetch statistics'}), 500

@app.route('/api/charts')
def get_charts_api():
    """Get all visualization charts"""
    try:
        data = get_monthly_data()
        categories = get_category_breakdown()
        
        return jsonify({
            'sales_trend': json.loads(create_sales_trend_chart(data).to_json()),
            'profit_margin': json.loads(create_profit_margin_chart(data).to_json()),
            'categories': json.loads(create_category_chart(categories).to_json()),
            'units': json.loads(create_daily_units_chart(data).to_json())
        })
    except Exception as e:
        logger.error(f"Error generating charts: {str(e)}")
        return jsonify({'error': 'Failed to generate charts'}), 500

@app.route('/api/data')
def get_data_api():
    """Get detailed data records"""
    try:
        data = get_monthly_data()
        records = []
        for i in range(len(data['months'])):
            margin = data['profit_margin'][i]
            records.append({
                'month': data['months'][i],
                'sales': round(data['sales'][i], 2),
                'expenses': round(data['expenses'][i], 2),
                'profit_margin': margin,
                'units': data['units'][i]
            })
        return jsonify(records)
    except Exception as e:
        logger.error(f"Error fetching data: {str(e)}")
        return jsonify({'error': 'Failed to fetch data'}), 500

@app.route('/api/categories')
def get_categories_api():
    """Get category breakdown"""
    try:
        categories = get_category_breakdown()
        return jsonify(categories)
    except Exception as e:
        logger.error(f"Error fetching categories: {str(e)}")
        return jsonify({'error': 'Failed to fetch categories'}), 500

@app.route('/api/export', methods=['GET'])
def export_data():
    """Export data as CSV"""
    try:
        data = get_monthly_data()
        
        # Create CSV in memory
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Month', 'Sales', 'Expenses', 'Profit_Margin', 'Units'])
        
        for i in range(len(data['months'])):
            writer.writerow([
                data['months'][i],
                data['sales'][i],
                data['expenses'][i],
                data['profit_margin'][i],
                data['units'][i]
            ])
        
        csv_data = output.getvalue()
        return csv_data, 200, {'Content-Disposition': 'attachment; filename=analytics_data.csv', 'Content-Type': 'text/csv'}
    except Exception as e:
        logger.error(f"Error exporting data: {str(e)}")
        return jsonify({'error': 'Failed to export data'}), 500

# ============ Error Handlers ============
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
