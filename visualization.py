import plotly.graph_objects as go
import plotly.express as px
import random

def create_bpm_chart(bpm_data):
    """Create a chart for BPM range visualization.
    
    Args:
        bpm_data (dict): Dictionary with BPM data (min, max, most_common)
        
    Returns:
        plotly.graph_objects.Figure: A plotly figure object
    """
    try:
        # Handle case where data isn't available
        if not bpm_data or not isinstance(bpm_data, dict):
            print("Invalid BPM data format")
            return go.Figure().add_annotation(
                text="BPM data not available",
                showarrow=False,
                font=dict(size=16, color="#1DB954")
            )
        
        # Extract values with defaults
        min_bpm = int(bpm_data.get('min', 0))
        max_bpm = int(bpm_data.get('max', 0))
        most_common = int(bpm_data.get('most_common', 0))
        
        # Check for valid values
        if min_bpm == 0 and max_bpm == 0 and most_common == 0:
            print("All BPM values are zero")
            # Create a default gauge with no data
            return go.Figure().add_annotation(
                text="Tempo information not available",
                showarrow=False,
                font=dict(size=16, color="#1DB954")
            )
        
        # Ensure min <= most_common <= max
        if min_bpm > most_common:
            min_bpm = most_common - 20
        if max_bpm < most_common:
            max_bpm = most_common + 20
        if min_bpm == max_bpm:
            min_bpm = max(0, min_bpm - 20)
            max_bpm = max_bpm + 20
        
        # Create a gauge chart for BPM
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=most_common,
            title={'text': "Most Common BPM", 'font': {'color': 'white'}},
            number={'font': {'color': 'white'}},
            gauge={
                'axis': {
                    'range': [min_bpm - 10 if min_bpm > 10 else 0, max_bpm + 10], 
                    'tickwidth': 1,
                    'tickfont': {'color': 'white'}
                },
                'bar': {'color': "#1DB954"},
                'bgcolor': 'rgba(50, 50, 50, 0.2)',
                'borderwidth': 2,
                'bordercolor': "#191414",
                'steps': [
                    {'range': [min_bpm - 10 if min_bpm > 10 else 0, min_bpm], 'color': "rgba(200, 200, 200, 0.2)"},
                    {'range': [min_bpm, max_bpm], 'color': "#1DB954", 'thickness': 0.75},
                    {'range': [max_bpm, max_bpm + 10], 'color': "rgba(200, 200, 200, 0.2)"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': most_common
                }
            }
        ))
        
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=50, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': 'white'}
        )
        
        return fig
    
    except Exception as e:
        print(f"Error creating BPM chart: {str(e)}")
        # Return an error figure
        return go.Figure().add_annotation(
            text="Unable to create tempo visualization",
            showarrow=False,
            font=dict(size=16, color="#1DB954")
        )

def create_key_chart(key_data):
    """Create a chart for musical key distribution.
    
    Args:
        key_data (dict): Dictionary mapping keys to frequency
        
    Returns:
        plotly.graph_objects.Figure: A plotly figure object
    """
    try:
        # Handle case where data isn't available
        if not key_data or not isinstance(key_data, dict) or len(key_data) == 0:
            print("Invalid key data format")
            return go.Figure().add_annotation(
                text="Key distribution data not available",
                showarrow=False,
                font=dict(size=16, color="#1DB954")
            )
        
        # Sort by frequency, handling non-numeric values
        sorted_keys = []
        for key, value in key_data.items():
            try:
                # Try to convert to int if it's a string number
                if isinstance(value, str) and value.isdigit():
                    value = int(value)
                # If it's not a number at all, set to 1
                if not isinstance(value, (int, float)):
                    value = 1
                sorted_keys.append((key, value))
            except:
                sorted_keys.append((key, 1))
        
        sorted_keys = sorted(sorted_keys, key=lambda x: x[1], reverse=True)
        
        # Ensure we have at least some data
        if not sorted_keys:
            print("No valid key data found")
            return go.Figure().add_annotation(
                text="Key distribution data not available",
                showarrow=False,
                font=dict(size=16, color="#1DB954")
            )
        
        keys = [item[0] for item in sorted_keys]
        values = [item[1] for item in sorted_keys]
        
        # Limit to top 7 keys
        display_count = min(7, len(keys))
        
        # Create bar chart
        fig = go.Figure(go.Bar(
            x=keys[:display_count],
            y=values[:display_count],
            marker_color='#1DB954'
        ))
        
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=30, b=40),
            xaxis_title="Musical Key",
            yaxis_title="Frequency",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': 'white'},
            xaxis={'gridcolor': 'rgba(80, 80, 80, 0.2)', 'tickfont': {'color': 'white'}},
            yaxis={'gridcolor': 'rgba(80, 80, 80, 0.2)', 'tickfont': {'color': 'white'}}
        )
        
        return fig
    
    except Exception as e:
        print(f"Error creating key chart: {str(e)}")
        # Return an error figure
        return go.Figure().add_annotation(
            text="Unable to create key distribution visualization",
            showarrow=False,
            font=dict(size=16, color="#1DB954")
        )

def create_instruments_chart(instruments_data):
    """Create a chart for common instruments.
    
    Args:
        instruments_data (dict): Dictionary mapping instruments to frequency (high/medium/low)
        
    Returns:
        plotly.graph_objects.Figure: A plotly figure object
    """
    try:
        # Handle case where data isn't available
        if not instruments_data or not isinstance(instruments_data, dict) or len(instruments_data) == 0:
            print("Invalid instruments data format")
            return go.Figure().add_annotation(
                text="Instrument data not available",
                showarrow=False,
                font=dict(size=16, color="#1DB954")
            )
        
        # Convert frequency text to numeric values
        freq_map = {"high": 3, "medium": 2, "low": 1}
        
        # Prepare data with error handling
        instruments = []
        frequency_text = []
        frequency_numeric = []
        
        for instrument, freq in instruments_data.items():
            if not isinstance(instrument, str) or not instrument.strip():
                continue
                
            if isinstance(freq, str) and freq.lower() in freq_map:
                numeric_freq = freq_map[freq.lower()]
            elif isinstance(freq, (int, float)) and 1 <= freq <= 3:
                numeric_freq = freq
            else:
                # Default to medium if invalid
                freq = "medium"
                numeric_freq = 2
                
            instruments.append(instrument)
            frequency_text.append(freq)
            frequency_numeric.append(numeric_freq)
        
        # If no valid data, return empty chart
        if not instruments:
            print("No valid instrument data")
            return go.Figure().add_annotation(
                text="Instrument data not available",
                showarrow=False,
                font=dict(size=16, color="#1DB954")
            )
        
        # Sort by frequency (high to low)
        sorted_indices = sorted(range(len(frequency_numeric)), key=lambda i: frequency_numeric[i], reverse=True)
        instruments = [instruments[i] for i in sorted_indices]
        frequency_text = [frequency_text[i] for i in sorted_indices]
        frequency_numeric = [frequency_numeric[i] for i in sorted_indices]
        
        # Limit to top 7 instruments
        display_count = min(7, len(instruments))
        
        # Create horizontal bar chart
        fig = go.Figure(go.Bar(
            y=instruments[:display_count],
            x=frequency_numeric[:display_count],
            orientation='h',
            marker_color='#1DB954',
            text=frequency_text[:display_count],
            textposition='inside',
            textfont={'color': 'black', 'size': 14},
        ))
        
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=30, b=20),
            xaxis=dict(
                tickvals=[1, 2, 3],
                ticktext=["Low", "Medium", "High"],
                title="Frequency",
                gridcolor='rgba(80, 80, 80, 0.2)',
                tickfont={'color': 'white'}
            ),
            yaxis=dict(
                title="Instrument",
                tickfont={'color': 'white'}
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': 'white'}
        )
        
        return fig
    
    except Exception as e:
        print(f"Error creating instruments chart: {str(e)}")
        # Return an error figure
        return go.Figure().add_annotation(
            text="Unable to create instruments visualization",
            showarrow=False,
            font=dict(size=16, color="#1DB954")
        )

def create_mood_and_genre_chart(text_data):
    """Create a clean, text-only display for mood and genre analysis with better text wrapping.
    
    Args:
        text_data (str): Text describing mood or genre
        
    Returns:
        plotly.graph_objects.Figure: A plotly figure object with text only
    """
    try:
        if not text_data or not isinstance(text_data, str) or text_data.lower() in ["analysis unavailable.", "analysis incomplete"]:
            text_data = "Analysis not available"
        
        # Create a completely blank figure with no axes
        fig = go.Figure()
        
        # Create a background box for the text
        fig.add_shape(
            type="rect",
            x0=0, y0=0, 
            x1=1, y1=1,
            line=dict(width=1, color="#333333"),
            fillcolor="rgba(30, 30, 30, 0.5)",
            layer="below",
            xref="paper", yref="paper"
        )
        
        # Add the text as a centered annotation with word wrapping
        # Split into multiple lines if needed
        words = text_data.split()
        max_words_per_line = 10
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            if len(current_line) >= max_words_per_line:
                lines.append(' '.join(current_line))
                current_line = []
                
        if current_line:  # Add any remaining words
            lines.append(' '.join(current_line))
            
        wrapped_text = '<br>'.join(lines)
        
        fig.add_annotation(
            text=wrapped_text,
            x=0.5, y=0.5,
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=14, color="#1DB954"),
            align="center",
            width=600,  # Add width to enable text wrapping
            height=150
        )
        
        # Remove all axes, gridlines, and other elements
        fig.update_layout(
            height=120,  # Increased height for better text display
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis={
                'showgrid': False,
                'zeroline': False,
                'showticklabels': False,
                'showline': False
            },
            yaxis={
                'showgrid': False,
                'zeroline': False,
                'showticklabels': False,
                'showline': False
            }
        )
        
        # Explicitly turn off all traces and axes
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)
        
        return fig
        
    except Exception as e:
        print(f"Error creating text visualization: {str(e)}")
        # Return a simple error figure with no axes
        fig = go.Figure()
        fig.add_shape(
            type="rect",
            x0=0, y0=0, 
            x1=1, y1=1,
            line=dict(width=1, color="#333333"),
            fillcolor="rgba(30, 30, 30, 0.5)",
            layer="below",
            xref="paper", yref="paper"
        )
        fig.add_annotation(
            text="Unable to display analysis",
            x=0.5, y=0.5,
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=14, color="#1DB954"),
            align="center"
        )
        fig.update_layout(
            height=120,
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)
        return fig
