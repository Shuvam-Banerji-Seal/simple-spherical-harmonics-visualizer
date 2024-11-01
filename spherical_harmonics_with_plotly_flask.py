import numpy as np
import plotly.graph_objs as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

def calculate_spherical_harmonics(l, m):
    """
    Calculate spherical harmonics surface for given l and m values.
    
    Parameters:
    -----------
    l : int
        Degree of the spherical harmonic
    m : int
        Order of the spherical harmonic
    
    Returns:
    --------
    dict containing x, y, z coordinates and color values
    """
    # Create grid of theta and phi values
    theta = np.linspace(0, np.pi, 100)
    phi = np.linspace(0, 2*np.pi, 100)
    theta, phi = np.meshgrid(theta, phi)
    
    # Calculate spherical harmonics
    Y_lm = np.real(np.abs(Y(l, m, phi, theta)))
    
    # Convert spherical coordinates to Cartesian coordinates
    r = Y_lm
    x = r * np.sin(theta) * np.cos(phi)
    y = r * np.sin(theta) * np.sin(phi)
    z = r * np.cos(theta)
    
    return {
        'x': x.flatten(), 
        'y': y.flatten(), 
        'z': z.flatten(), 
        'color': Y_lm.flatten()
    }

def Y(l, m, phi, theta):
    """
    Wrapper for scipy's spherical harmonics with more robust handling
    """
    from scipy.special import sph_harm
    return sph_harm(abs(m), l, phi, theta) * np.sign(m)**abs(m)

# Create Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div([
    html.H1("Interactive Spherical Harmonics Visualizer", 
            style={'textAlign': 'center', 'color': '#1E90FF'}),
    
    html.Div([
        html.Div([
            html.Label('Degree (l):'),
            dcc.Slider(
                id='l-slider',
                min=0,
                max=10,
                value=3,
                marks={i: str(i) for i in range(0, 11, 2)},
                step=1
            )
        ], style={'width': '48%', 'display': 'inline-block'}),
        
        html.Div([
            html.Label('Order (m):'),
            dcc.Slider(
                id='m-slider',
                min=-10,
                max=10,
                value=0,
                marks={i: str(i) for i in range(-10, 11, 5)},
                step=1
            )
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ]),
    
    dcc.Graph(id='spherical-harmonics-plot')
])

@app.callback(
    Output('spherical-harmonics-plot', 'figure'),
    [Input('l-slider', 'value'),
     Input('m-slider', 'value')]
)
def update_graph(l, m):
    """
    Update the 3D surface plot based on l and m parameters
    """
    # Calculate spherical harmonics data
    data = calculate_spherical_harmonics(l, m)
    
    # Create 3D scatter plot with color gradient
    fig = go.Figure(data=[go.Scatter3d(
        x=data['x'], 
        y=data['y'], 
        z=data['z'],
        mode='markers',
        marker=dict(
            size=3,
            color=data['color'],
            colorscale='Viridis',
            opacity=0.8,
            colorbar=dict(title='Magnitude')
        )
    )])
    
    # Customize layout
    fig.update_layout(
        title=f'Spherical Harmonics Y({l}, {m})',
        scene=dict(
            xaxis_title='X',
            yaxis_title='Y',
            zaxis_title='Z',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.5)
            )
        ),
        height=600,
        width=800
    )
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
