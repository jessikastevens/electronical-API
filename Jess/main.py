import gradio as gr
import random
import matplotlib.pyplot as plt
import requests
import json
from dotenv import load_dotenv
import os
from datetime import datetime


load_dotenv()

# Dropdown options for the first interface
options_1 = ['Fridges & Freezers', 'TVs', 'Hi-Fi systems (with CD players)', 'Laptops', 'Computer stations','Incandescent lamps' , 
             'Compact fluorescent lamps', 'Microwaves', 'Coffee machines', 'Mobile phones', 'Printers']

# Function to filter options for dropdown interface
def filter_options(option_1):
    return f"You selected '{option_1}' in the dropdown."

# Handling single datetime input
def handle_single_datetime(datetime_value):
    return f"Selected Date and Time: {datetime_value}"

# Handling date range (start and end datetime)
def handle_date_range(start_datetime, end_datetime):
    return f"Selected Date Range: {start_datetime} to {end_datetime}"

# Combine Dropdown and Date inputs in a single function


def handle_combined_input(option_1, start_datetime, end_datetime):
    print('Predict')
    url = os.environ.get('Logic_API_URL_CSV')

    # Convert the timestamp format
    start_datetime_str = datetime.fromtimestamp(start_datetime).strftime("%Y-%m-%d %H:%M:%S")
    end_datetime_str = datetime.fromtimestamp(end_datetime).strftime("%Y-%m-%d %H:%M:%S")

    payload = {
        "Appliance": option_1,
        "start": start_datetime_str,
        "end": end_datetime_str,
    }

    print("API URL:", url)
    print("Payload:", json.dumps(payload, indent=4))

    headers = {
        "Content-Type": "application/json",
    }
    response = requests.post(url, json=payload, headers=headers)

    print('Response Status Code:', response.status_code)
    print('Response Text:', response.text)  # Log full response for debugging

    return response



def predict(real_power_slider, reactive_power_slider, rms_current_slider, frequency_slider, rms_voltage_slider, 
            phase_angle_slider, single_datetime):
    print('')
    url = os.environ.get('Logic_API_URL_AI')

    # Parse the single_datetime into a Date (YYYY-MM-DD) and Time (HH:MM:SS)
    try:
        dt_object = datetime.strptime(single_datetime, '%Y-%m-%d %H:%M:%S')
        date_str = dt_object.strftime('%Y-%m-%d')
        time_str = dt_object.strftime('%H:%M:%S')
    except ValueError as e:
        print(f"Error parsing datetime: {e}")
        return None

    # Create the payload with separated Date and Time
    payload = {
        "Real power": real_power_slider,
        "Reactive power": reactive_power_slider,
        "RMS current": rms_current_slider,
        "Frequency": frequency_slider,
        "RMS voltage": rms_voltage_slider,
        "Phase angle": phase_angle_slider,
        "Date": date_str,
        "Time": time_str,
    }
    print("API URL:", url)
    print("Payload:", json.dumps(payload, indent=4))

    headers = {
        "Content-Type": "application/json",
    }
    response = requests.post(url, json=payload, headers=headers)

    print('Response Status Code:', response.status_code)
    print('Response Text:', response.text)  # Log full response for debugging

    return response


# Tab 1: Dropdown and Date Range Inputs
with gr.Blocks() as input_tab:
    with gr.Row():
        with gr.Column():
            # Dropdown for appliance selection
            dropdown = gr.Dropdown(choices=options_1, label="Appliance Type")

            # Date Range Picker
            start_datetime = gr.DateTime(label="Start Date and Time")
            end_datetime = gr.DateTime(label="End Date and Time")

            # Button to submit selections
            submit_button = gr.Button("Submit")

        # Output Textbox to display results
        result_output = gr.Textbox(label="Output")

    # Bind the function to the submit button
    submit_button.click(fn=handle_combined_input, 
                        inputs=[dropdown, start_datetime, end_datetime],
                        outputs=result_output)

# Tab 2: Prediction Interface with DateTime Input
with gr.Blocks() as prediction_tab:
    # Prediction Interface
    with gr.Row():
        with gr.Column():
            real_power_slider = gr.Slider(minimum=0, maximum=4000, step=50, value=1550, label="Real Power (W)")
            reactive_power_slider = gr.Slider(minimum=0, maximum=500, step=10, value=250, label="Reactive Power (var)")
            rms_current_slider = gr.Slider(minimum=0, maximum=100, step=0.1, value=7.75, label="RMS Current (A)")
            frequency_slider = gr.Slider(minimum=0, maximum=100, step=10, value=50, label="Frequency (Hz)")
            rms_voltage_slider = gr.Slider(minimum=0, maximum=300, step=10, value=220, label="RMS Voltage (V)")
            phase_angle_slider = gr.Slider(minimum=-100, maximum=100, step=5, value=0, label="Phase Angle (φ)")

            # Single DateTime Picker on Prediction Tab
            single_datetime = gr.DateTime(label="Select a Date and Time")

            predict_button = gr.Button("Predict")

        # Output for Prediction
        prediction_plot = gr.Plot()
        prediction_image = gr.Image(type="filepath")
        prediction_text = gr.Textbox(label="Appliance")

    # Bind the predict function to the predict button
    predict_button.click(fn=predict, 
                         inputs=[real_power_slider, reactive_power_slider, rms_current_slider, frequency_slider, 
                                 rms_voltage_slider, phase_angle_slider,  single_datetime],
                         outputs=[prediction_plot, prediction_image, prediction_text])

# Combine into a Tabbed Interface
demo = gr.TabbedInterface(
    [input_tab, prediction_tab],
    ["Dropdown & Date Range", "AI Device Prediction & Date Selection"]
)

# theme = gr.themes.Soft(
#     primary_hue="cyan",
#     secondary_hue="pink",
#     neutral_hue="violet",
# )
# with gr.Blocks(theme=theme) as demo:
#        demo = gr.TabbedInterface(
#         [input_tab, prediction_tab],
#         ["Dropdown & Date Range", "AI Device Prediction & Date Selection"]
#     )

demo.launch(share=True)
