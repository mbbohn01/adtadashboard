import pandas as pd

file_path = 'BSS Retail Data.csv'
df = pd.read_csv(file_path)

# Convert salesdate to datetime
df['salesdate'] = pd.to_datetime(df['salesdate'])

# Fill missing competitor prices with a placeholder (e.g., -1 or NaN depending on use-case)
competitor_cols = [col for col in df.columns if 'comp_' in col and 'price' in col]
df[competitor_cols] = df[competitor_cols].fillna(-1)

# Fill missing stock levels with 0 (or could use forward-fill if time-based logic is required)
df['managed_fba_stock_level'] = df['managed_fba_stock_level'].fillna(0)

# Fill comp_data_min_price and max_price with -1 to indicate no competitor data
df['comp_data_min_price'] = df['comp_data_min_price'].fillna(-1)
df['comp_data_max_price'] = df['comp_data_max_price'].fillna(-1)

# Create price difference feature
df['price_diff_vs_comp_min'] = df['price'] - df['comp_data_min_price']

from dash import Dash, dcc, html, Input, Output, callback, jupyter_dash
import plotly.express as px

app = Dash()
app.config.suppress_callback_exceptions = True

app.layout = html.Div([
    html.Div([
        dcc.Dropdown(['All'] + df['sku'].unique().tolist(), 'All', id='dropdown'),
        html.Div([
            dcc.Graph(id="chart1", figure=px.scatter(df, x='price_diff_vs_comp_min', y='unitsordered',
                                      title="Units Ordered vs. Price Difference b/w Competitors",
                                      color_discrete_sequence=['#FF6B6B']))
        ], style={'width': '50%', 'display': 'inline-block'}),

        html.Div([
          dcc.Graph(id="chart2", figure=px.histogram(df, x='adspend', y='profit', histfunc='avg',
                          title="Average Profit vs. Adspend",
                          color_discrete_sequence=['#4ECDC4']))
        ], style={'width': '50%', 'display': 'inline-block'})
    ]),

    html.Div([
        html.Div([
            dcc.Graph(id="chart3", figure=px.line(df.groupby('salesdate').sum().reset_index(),
                                   x="salesdate", y="profit",
                                   title="Profit over Time",
                                   color_discrete_sequence=['#FFD166']))
        ], style={'width': '50%', 'display': 'inline-block'}),

        html.Div([
        ], style={'width': '50%', 'display': 'inline-block'})
    ])
])

@callback(
    Output(component_id='chart1', component_property='figure'),
    Output(component_id='chart2', component_property='figure'),
    Output(component_id='chart3', component_property='figure'),
    Input(component_id='dropdown', component_property='value')
)
def update_output_div(input_value):
    if input_value == 'All':
        filtered_df = df
    else:
        filtered_df = df[df.sku == input_value]

    fig=px.scatter(filtered_df, x='price_diff_vs_comp_min', y='unitsordered',
                      title="Units Ordered vs. Price Difference b/w Competitors",color_discrete_sequence=['#FF6B6B'])

    fig2=px.histogram(filtered_df, x='adspend', y='profit', histfunc='avg',
                          title="Average Profit vs. Adspend",
                          color_discrete_sequence=['#4ECDC4'])

    fig3=px.line(filtered_df.groupby('salesdate').sum().reset_index(),
                                   x="salesdate", y="profit",
                                   title="Profit over Time",
                                   color_discrete_sequence=['#FFD166'])

    return fig, fig2, fig3

    app.run()
