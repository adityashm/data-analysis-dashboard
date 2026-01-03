from flask import Flask, render_template, jsonify
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
import json
import os

app = Flask(__name__)

# Sample data generation
def generate_sample_data():
    """Generate sample data for visualization"""
    data = {
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        'Sales': [45000, 52000, 48000, 61000, 55000, 67000, 72000, 68000, 75000, 82000, 88000, 95000],
        'Expenses': [30000, 32000, 31000, 38000, 35000, 42000, 45000, 43000, 48000, 52000, 55000, 60000],
        'Profit Margin': [33.3, 38.5, 35.4, 37.7, 36.4, 37.3, 37.5, 36.8, 36.0, 36.6, 37.5, 36.8]
    }
    return pd.DataFrame(data)

def create_sales_chart(df):
    """Create sales vs expenses chart"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['Month'],
        y=df['Sales'],
        mode='lines+markers',
        name='Sales',
        line=dict(color='#3B82F6', width=3),
        marker=dict(size=8)
    ))
    
    fig.add_trace(go.Scatter(
        x=df['Month'],
        y=df['Expenses'],
        mode='lines+markers',
        name='Expenses',
        line=dict(color='#EF4444', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title='Monthly Sales vs Expenses',
        xaxis_title='Month',
        yaxis_title='Amount ($)',
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    return fig

def create_profit_margin_chart(df):
    """Create profit margin chart"""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df['Month'],
        y=df['Profit Margin'],
        marker=dict(color=df['Profit Margin'], colorscale='Viridis', showscale=True),
        name='Profit Margin (%)',
        text=df['Profit Margin'].round(1),
        textposition='outside'
    ))
    
    fig.update_layout(
        title='Monthly Profit Margin %',
        xaxis_title='Month',
        yaxis_title='Profit Margin (%)',
        template='plotly_white',
        height=400
    )
    
    return fig

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    """API endpoint to get raw data"""
    df = generate_sample_data()
    return jsonify(df.to_dict('records'))

@app.route('/api/charts')
def get_charts():
    """API endpoint to get all charts"""
    df = generate_sample_data()
    
    sales_chart = create_sales_chart(df)
    margin_chart = create_profit_margin_chart(df)
    
    charts = {
        'sales_chart': json.loads(sales_chart.to_json()),
        'margin_chart': json.loads(margin_chart.to_json())
    }
    
    return jsonify(charts)

@app.route('/api/stats')
def get_stats():
    """API endpoint for statistics"""
    df = generate_sample_data()
    
    stats = {
        'total_sales': float(df['Sales'].sum()),
        'total_expenses': float(df['Expenses'].sum()),
        'total_profit': float((df['Sales'] - df['Expenses']).sum()),
        'avg_margin': float(df['Profit Margin'].mean()),
        'max_sales': float(df['Sales'].max()),
        'min_sales': float(df['Sales'].min())
    }
    
    return jsonify(stats)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
