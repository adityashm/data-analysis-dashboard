from flask import Flask, render_template, jsonify
import plotly.graph_objects as go
import json

app = Flask(__name__)

def generate_sample_data():
    return {
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        'Sales': [45000, 52000, 48000, 61000, 55000, 67000, 72000, 68000, 75000, 82000, 88000, 95000],
        'Expenses': [30000, 32000, 31000, 38000, 35000, 42000, 45000, 43000, 48000, 52000, 55000, 60000],
        'Profit_Margin': [33.3, 38.5, 35.4, 37.7, 36.4, 37.3, 37.5, 36.8, 36.0, 36.6, 37.5, 36.8]
    }

def create_sales_chart(data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Month'], y=data['Sales'], mode='lines+markers', name='Sales', line=dict(color='#3B82F6', width=3), marker=dict(size=8)))
    fig.add_trace(go.Scatter(x=data['Month'], y=data['Expenses'], mode='lines+markers', name='Expenses', line=dict(color='#EF4444', width=3), marker=dict(size=8)))
    fig.update_layout(title='Monthly Sales vs Expenses', xaxis_title='Month', yaxis_title='Amount ($)', hovermode='x unified', template='plotly_white', height=400)
    return fig

def create_profit_margin_chart(data):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=data['Month'], y=data['Profit_Margin'], marker=dict(color=data['Profit_Margin'], colorscale='Viridis', showscale=True), name='Profit Margin (%)', text=[f"{x:.1f}" for x in data['Profit_Margin']], textposition='outside'))
    fig.update_layout(title='Monthly Profit Margin %', xaxis_title='Month', yaxis_title='Profit Margin (%)', template='plotly_white', height=400)
    return fig

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    data = generate_sample_data()
    records = [{'Month': data['Month'][i], 'Sales': data['Sales'][i], 'Expenses': data['Expenses'][i], 'Profit_Margin': data['Profit_Margin'][i]} for i in range(len(data['Month']))]
    return jsonify(records)

@app.route('/api/charts')
def get_charts():
    data = generate_sample_data()
    return jsonify({'sales_chart': json.loads(create_sales_chart(data).to_json()), 'margin_chart': json.loads(create_profit_margin_chart(data).to_json())})

@app.route('/api/stats')
def get_stats():
    data = generate_sample_data()
    total_sales = sum(data['Sales'])
    total_expenses = sum(data['Expenses'])
    return jsonify({'total_sales': float(total_sales), 'total_expenses': float(total_expenses), 'total_profit': float(total_sales - total_expenses), 'avg_margin': float(sum(data['Profit_Margin']) / len(data['Profit_Margin'])), 'max_sales': float(max(data['Sales'])), 'min_sales': float(min(data['Sales']))})

if __name__ == '____':
    app.run(debug=True, host='0.0.0.0', port=5000)
