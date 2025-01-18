import numpy as np
import plotly.graph_objs as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
from scipy.special import sph_harm

def validate_quantum_numbers(l: int, m: int) -> None:
    """
    Validate quantum numbers l and m based on physical constraints.
    """
    if l < 0:
        raise ValueError(f"l must be non-negative, got {l}")
    if abs(m) > l:
        raise ValueError(f"Invalid quantum numbers: |m| ({abs(m)}) must be ≤ l ({l})")


def calculate_spherical_harmonics(l: int, m: int, resolution: int = 100) -> dict:
    """
    Calculate spherical harmonics surface with increased resolution.
    """
    validate_quantum_numbers(l, m)
    
    n_theta = resolution
    n_phi = int(2 * resolution)
    
    theta = np.linspace(0, np.pi, n_theta)
    phi = np.linspace(0, 2*np.pi, n_phi)
    theta, phi = np.meshgrid(theta, phi)
    
    Y_lm = np.real(sph_harm(m, l, phi, theta))
    
    max_val = np.max(np.abs(Y_lm))
    scaling_factor = 2.0 / (1 + np.exp(-2 * np.abs(Y_lm) / max_val)) - 1
    r = scaling_factor
    
    x = r * np.sin(theta) * np.cos(phi)
    y = r * np.sin(theta) * np.sin(phi)
    z = r * np.cos(theta)
    
    return {
        'x': x,
        'y': y,
        'z': z,
        'color': Y_lm,
        'theta': theta,
        'phi': phi
    }

# Create Dash app
app = dash.Dash(__name__)

# App layout remains the same
app.layout = html.Div([
    html.H1("Interactive Spherical Harmonics Visualizer", 
            style={'textAlign': 'center', 'color': '#1E90FF'}),
    
    html.Div([
        html.Label('Visualization Type:'),
        dcc.Dropdown(
            id='viz-type',
            options=[
                {'label': 'Points', 'value': 'points'},
                {'label': 'Surface', 'value': 'surface'},
                {'label': 'Wireframe', 'value': 'wireframe'},
                {'label': 'Contour', 'value': 'contour'}
            ],
            value='points',
            style={'width': '200px'}
        )
    ], style={'margin': '10px'}),
    
    html.Div([
        html.Div([
            html.Label('Degree (l):'),
            dcc.Slider(
                id='l-slider',
                min=0,
                max=5,
                value=1,
                marks={i: str(i) for i in range(6)},
                step=1
            ),
            html.Div([
                dcc.Input(
                    id='l-input',
                    type='number',
                    value=1,
                    min=0,
                    max=5,
                    style={'width': '60px', 'margin': '5px'}
                ),
                html.Button('→', id='l-button', n_clicks=0)
            ])
        ], style={'width': '48%', 'display': 'inline-block'}),
        
        html.Div([
            html.Label('Order (m):'),
            dcc.Slider(
                id='m-slider',
                min=-1,
                max=1,
                value=0,
                marks={-1: '-1', 0: '0', 1: '1'},
                step=1
            ),
            html.Div([
                dcc.Input(
                    id='m-input',
                    type='number',
                    value=0,
                    min=-1,
                    max=1,
                    style={'width': '60px', 'margin': '5px'}
                ),
                html.Button('→', id='m-button', n_clicks=0)
            ])
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ]),
    
    html.Div([
        html.Label('Point Density:'),
        dcc.Slider(
            id='density-slider',
            min=50,
            max=200,
            value=100,
            marks={50: 'Low', 100: 'Medium', 150: 'High', 200: 'Very High'},
            step=25
        )
    ], style={'margin': '20px 0'}),
    
    dcc.Graph(id='spherical-harmonics-plot'),
    
    html.Div(id='quantum-numbers-warning', 
             style={'color': 'red', 'textAlign': 'center'})
])

# Combined callback for m-slider and m-input updates
@app.callback(
    [Output('m-slider', 'min'),
     Output('m-slider', 'max'),
     Output('m-slider', 'marks'),
     Output('m-slider', 'value'),
     Output('m-input', 'min'),
     Output('m-input', 'max'),
     Output('m-input', 'value')],
    [Input('l-slider', 'value'),
     Input('l-input', 'value'),
     Input('m-button', 'n_clicks')],
    [State('m-input', 'value'),
     State('m-slider', 'value')]
)
def update_m_controls(l_slider, l_input, m_button_clicks, m_input_value, m_slider_value):
    """Update m-controls based on various inputs"""
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    
    # Use l_input if available, otherwise use l_slider
    l = l_input if l_input is not None else l_slider
    
    # Create marks for the slider
    marks = {i: str(i) for i in range(-l, l+1)}
    
    # Determine the new m value based on which input triggered the callback
    if triggered_id == 'm-button' and m_input_value is not None:
        new_m = max(-l, min(l, m_input_value))
    else:
        new_m = min(max(m_slider_value, -l), l) if m_slider_value is not None else 0
    
    return -l, l, marks, new_m, -l, l, new_m

@app.callback(
    Output('l-slider', 'value'),
    [Input('l-button', 'n_clicks')],
    [State('l-input', 'value')]
)
def update_l_slider(n_clicks, l_input):
    """Update l-slider from input box"""
    if l_input is not None:
        return max(0, min(5, l_input))
    return 1

@app.callback(
    [Output('spherical-harmonics-plot', 'figure'),
     Output('quantum-numbers-warning', 'children')],
    [Input('l-slider', 'value'),
     Input('m-slider', 'value'),
     Input('viz-type', 'value'),
     Input('density-slider', 'value')]
)
def update_graph(l, m, viz_type, density):
    """Update the visualization based on all parameters"""
    try:
        data = calculate_spherical_harmonics(l, m, resolution=density)
        
        traces = []
        
        if viz_type == 'points':
            traces.append(go.Scatter3d(
                x=data['x'].flatten(),
                y=data['y'].flatten(),
                z=data['z'].flatten(),
                mode='markers',
                marker=dict(
                    size=2,
                    color=data['color'].flatten(),
                    colorscale='RdBu',
                    opacity=0.8,
                    colorbar=dict(title='Y_lm')
                )
            ))
        
        elif viz_type == 'surface':
            traces.append(go.Surface(
                x=data['x'],
                y=data['y'],
                z=data['z'],
                surfacecolor=data['color'],
                colorscale='RdBu',
                colorbar=dict(title='Y_lm')
            ))
        
        elif viz_type == 'wireframe':
            for i in range(data['x'].shape[1]):
                traces.append(go.Scatter3d(
                    x=data['x'][:, i],
                    y=data['y'][:, i],
                    z=data['z'][:, i],
                    mode='lines',
                    line=dict(color='blue', width=1),
                    showlegend=False
                ))
            for i in range(data['x'].shape[0]):
                traces.append(go.Scatter3d(
                    x=data['x'][i, :],
                    y=data['y'][i, :],
                    z=data['z'][i, :],
                    mode='lines',
                    line=dict(color='red', width=1),
                    showlegend=False
                ))
        
        elif viz_type == 'contour':
            traces.append(go.Contour(
                z=data['color'],
                x=np.linspace(0, 2*np.pi, data['phi'].shape[1]),
                y=np.linspace(0, np.pi, data['theta'].shape[0]),
                colorscale='RdBu',
                colorbar=dict(title='Y_lm')
            ))

        fig = go.Figure(data=traces)
        
        if viz_type == 'contour':
            fig.update_layout(
                title=dict(
                    text=f'Spherical Harmonic Y_{{{l},{m}}} (φ-θ projection)',
                    x=0.5,
                    font=dict(size=20)
                ),
                xaxis_title='φ (azimuthal angle)',
                yaxis_title='θ (polar angle)',
                height=700,
                width=800
            )
        else:
            fig.update_layout(
                title=dict(
                    text=f'Spherical Harmonic Y_{{{l},{m}}}',
                    x=0.5,
                    font=dict(size=20)
                ),
                scene=dict(
                    xaxis_title='X',
                    yaxis_title='Y',
                    zaxis_title='Z',
                    camera=dict(
                        eye=dict(x=1.5, y=1.5, z=1.5)
                    ),
                    aspectmode='data'
                ),
                height=700,
                width=800
            )
        
        return fig, ""
        
    except ValueError as e:
        return go.Figure(), str(e)

if __name__ == '__main__':
    app.run_server(debug=True)