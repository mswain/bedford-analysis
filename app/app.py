from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import FileField, FloatField, StringField
from wtforms.validators import DataRequired, NumberRange
import pandas as pd
import plotly.graph_objects as go
import os

app = Flask(__name__)
app.static_folder = 'static'

# Set a secret key for form CSRF protection
app.secret_key = os.getenv('SECRET_KEY')

@app.route('/static/css/styles.css')
def serve_css():
    return app.send_static_file('css/tailwind.css')

class UploadForm(FlaskForm):
    file = FileField('Select a file', validators=[DataRequired()])
    tolerance = FloatField('Tolerance', validators=[DataRequired(), NumberRange(min=0.0, max=5.0)])
    target_column = StringField('Target Column', default='7_2009', description='Leave blank for default (7_2009)')

def is_bedford_law_valid(observed_percentages, tolerance):
    # Expected percentage of digit 1 in the first position
    expected_percentage_1 = 30  

    # User defined tolerance from form
    tolerance = tolerance 

    # Percentage of digit 1 in the first position
    observed_percentage_1 = observed_percentages[0]

    # Difference between expected and observed  
    diff = abs(observed_percentage_1 - expected_percentage_1) 

    # Check if difference is within tolerance
    within_range = -tolerance <= diff <= tolerance 

    # Bedford's Law is valid if the difference is within tolerance
    valid_bedford = within_range  

    # Return validation result
    return valid_bedford

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    form = UploadForm()
    if form.validate_on_submit():
        file = form.file.data
        file_extension = os.path.splitext(file.filename)[1]

        # Determine the file type and read the data
        if file_extension == '.csv':
            try:
                df = pd.read_csv(file, sep='\t')
            except Exception as e:
                print(f"Error reading CSV file: {e}")
        elif file_extension in ['.xls', '.xlsx']:
            try:
                df = pd.read_excel(file)
            except Exception as e:
                print(f"Error reading Excel file: {e}")
        elif file_extension == '.parquet':
            try:
                df = pd.read_parquet(file)
            except Exception as e:
                print(f"Error reading Parquet file: {e}")
        elif file_extension == '.orc':
            try:
                df = pd.read_orc(file)
            except Exception as e:
                print(f"Error reading ORC file: {e}")
        elif file_extension == '.feather':
            try:
                df = pd.read_feather(file)
            except Exception as e:
                print(f"Error reading Feather file: {e}")
        elif file_extension == '.h5':
            try:
                df = pd.read_hdf(file)
            except Exception as e:
                print(f"Error reading HDF file: {e}")
        elif file_extension == '.json':
            try:
                df = pd.read_json(file)
            except Exception as e:
                print(f"Error reading JSON file: {e}")
        else:
            print("Unknown file type")
        

        # Extract the first digit from each number
        data = df['7_2009'].astype(str).str[0]

        # Calculate the count of each digit
        data = data[data.isin(['1', '2', '3', '4', '5', '6', '7', '8', '9'])]
        
        # Calculate the count of each unique value in data
        digit_counts = data.value_counts().sort_index()

        # Create a list of values 1-9
        x = list(range(1, 10))

        # Calculate the total of all digits
        total_count = digit_counts.sum()

        # Calculate the percentage of occurance for each digit
        observed_percentages = digit_counts / total_count * 100

        # Create the x axis labels
        digit_labels = [str(i) for i in x]

        # Get the tolerance from the form
        tolerance = form.tolerance.data
        
        # Create a list with the expected percentages
        expected_percentages = [30.1, 17.6, 12.5, 9.7, 7.9, 6.7, 5.8, 5.1, 4.6]

        # Create the bars for the chart
        trace_observed = go.Bar(
            x=x,
            y=observed_percentages,
            name='Observed',
            marker=dict(color='blue'),
            text=observed_percentages.round(2),
            textposition='auto'
        )

        trace_expected = go.Bar(
            x=x,
            y=expected_percentages,
            name='Expected',
            marker=dict(color='red'),
            text=[f'{p:.2f}%' for p in expected_percentages],
            textposition='auto'
        )

        # Create a list with the trace object
        data = [trace_observed, trace_expected]

        # Specify the settings for the chart
        layout = go.Layout(
            title='Observed Distribution / Expected Distribution',
            xaxis=dict(
                title='First Digit Percentage Totals',
                tickmode='array',
                tickvals=x,
                ticktext=digit_labels
            ),
            yaxis=dict(
                autorange=True,
                showticklabels=False
            ),
            width=800,
            height=600
        )

        # Use the data and layout objects to create the renderale chart
        fig = go.Figure(data=data, layout=layout)

        # Convert the fig object to embeddable HTML
        plot_html = fig.to_html(full_html=False, default_width='100%', default_height='100%')

        # Validate Bedford's Law
        valid_bedford = is_bedford_law_valid(observed_percentages, tolerance)

        # Return data to the template
        return render_template('index.html', form=form, plot_html=plot_html, valid_bedford=valid_bedford, tolerance=tolerance)

    # Return the template with the form
    return render_template('index.html', form=form)

if __name__ == '__main__':
    app.run()
