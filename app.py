# -*- coding: utf-8 -*-
import base64
import os
import pandas as pd
from urllib.parse import quote as urlquote
from flask import Flask, send_from_directory
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
import MergePDFs


# Set tmp and pdf file directories
# make sure to have the slash at the end
temp_dir = os.path.join('./static/TempDirForPdfs/')
input_dir = os.path.join('./static/examplepdfs/')
if not os.path.exists(input_dir):
    os.makedirs(input_dir)

# using external css for now
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#initiate flask server and app 
server = Flask(__name__)
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, server=server)
app.title = 'SJC PDF Merger'

#Meta
colors = {
    'background': '#FFFFFF',
    'text0': '#0000CD',
    'text1': '#FF0000',
    'text_white': '#FFFFFF',
    }

#SJC image
image_filename = './static/SJC_logo.png' 
encoded_image = base64.b64encode(open(image_filename, 'rb').read()).decode('ascii')

#initializing empty data frame
df = pd.DataFrame(columns=['File Name'])

#Initializing functions
def initialize_files(temp_dir, input_dir):
    pdf_lst = MergePDFs.initialize_and_retrieve(temp_dir, input_dir)
    return pdf_lst

def retrieve_files(input_dir):
    pdf_lst = MergePDFs.retrieve_files(input_dir)
    return pdf_lst



#Begin Dash app layout
app.layout = html.Div([ 

                html.Div([
                    html.H1(children='PDF Merger', style={ 'color': colors['text0']}), 

                    html.Img(src='data:image/png;base64,{}'.format(encoded_image),
                             style={'width': '40%', 'float':'right'}),
                           ],style={'columnCount': 2}),

                html.Div([
                    html.Div(children='''A web application for customized pdf merging.''',
                             style={'textAlign': 'center'}),
                    html.H3("Upload"),
                    html.Div(dcc.Upload(
                                        id='upload-data',
                                        children=html.Div([
                                            'Drag and Drop or ',
                                            html.A('Select Files')
                                        ]),
                                        style={
                                            'width': '95%',
                                            'height': '60px',
                                            'lineHeight': '60px',
                                            'borderWidth': '1px',
                                            'borderStyle': 'dashed',
                                            'borderRadius': '5px',
                                            'textAlign': 'center',
                                            'margin': '10px'},
                                        # Allow multiple files to be uploaded
                                        multiple=True
                                    )
                            ),
                    html.Div(html.Br()),
                    html.H3("File Selection"),
                    html.Div("Select a File"),
                    html.Div([
                            dcc.Dropdown(id='file_choice', 
                                        options=[{'label': i, 'value': i} for i in reversed(initialize_files(temp_dir, input_dir))], value=None
                                        ),
                            ], style={'width':'70%'}),
                    
                    html.Div([
                        html.Button('Refresh File List', id='reload_files_button', n_clicks = 0, n_clicks_timestamp='0',
                                    style={
                                            'textAlign': 'center',
                                            'color': colors['text1']}
                                    ),
                        html.Button('Confirm This File', id='submit_button', n_clicks = 0, n_clicks_timestamp='0', style={ 'color': colors['text0']})
                        
                        ]),
                    html.Div(id = "chosen_file"),
                    html.Div([
                            html.Br(),
                            html.H3(children = "Files to Merge"),
                            html.Div(
                                    dt.DataTable(id='table',
                                                columns=[{'id': 'File Name', 'name': 'File Name'}],
                                                data=df.to_dict("rows"),
                                                style_cell={'textAlign': 'left'}
                                                ), style = {'width':'70%'}
                                    ),
                            html.Br(),
                            html.Div('Enter Name of Output File'),
                            html.Div([
                                    dcc.Input(id='merged_id', value='Merged_File', type='text'),
                                    html.Button('Clear Files', id='reset_button', n_clicks = 0, n_clicks_timestamp='0', style={ 'color': colors['text1']}),
                                    html.Button('Execute Merge', id='confirm_button', n_clicks = 0, n_clicks_timestamp='0', style={ 'color': colors['text0']})
                                ], style={'columnCount': 1}),
                            html.Br(),
                            ]),
                    

                    html.Div(id = 'merge_id'),
                    html.Div(id='merged_name', style={ 'color' : colors['text_white']}),
                    html.Br(),

                    html.Div([
                            html.H3("Downloadable File List"),
                            html.Button('Refresh', id='reload_dl_files_button', n_clicks = 0, n_clicks_timestamp='0',
                                            style={
                                                    'textAlign': 'center',
                                                    'color': colors['text1']}
                                        ),
                                    
                                 
                            html.Ul(id="file-list"),

                            html.Br(),
                            ]),

                    html.Div([
                            html.H3('Delete Files From App Server'),
                            dcc.Dropdown(id='delete_drop', 
                                        options=[{'label': i, 'value': i} for i in reversed(initialize_files(temp_dir, input_dir))], value=None
                                        ),
                            ], style={'width':'70%'}),
                    
                    html.Div([
                        html.Button('Refresh Dropdown List', id='refresh_delete', n_clicks = 0, n_clicks_timestamp='0',
                                    style={
                                            'textAlign': 'center',
                                            'color': colors['text0']}
                                    ),
                        html.Button('Permanently Delete This File', id='delete_button', n_clicks = 0, n_clicks_timestamp='0',
                                    style={ 'color': colors['text1']}),
                        html.Div(id = "deleted_file"),
                        html.Br(),
                        ]),
                    
                    html.Div(''),
                    html.Br()


                ]),
                      
                ], #close layout square
                style={'backgroundColor': colors['background']},
            ) #close layout Div


###Functions

def save_file(name, content):
    """Decode and store a file uploaded with Plotly Dash."""
    data = content.encode("utf8").split(b";base64,")[1]
    with open(os.path.join(input_dir, name), "wb") as fp:
        fp.write(base64.decodebytes(data))


def uploaded_files():
    """List the files in the upload directory."""
    files = []
    for filename in os.listdir(input_dir):
        if filename.endswith('.pdf'):
            path = os.path.join(input_dir, filename)
            if os.path.isfile(path):
                files.append(filename)
    return files


def file_download_link(filename):
    """Create a Plotly Dash 'A' element that downloads a file from the app."""
#    absolute_filename = os.path.join(os.getcwd(), relative_filename)
    location = "/download/{}".format(urlquote(filename))
    return html.A(filename, href=location)



###Callbacks:


@app.callback(
    dash.dependencies.Output("file-list", "children"),
    [dash.dependencies.Input("upload-data", "filename"),
    dash.dependencies.Input("upload-data", "contents"),
     dash.dependencies.Input('reload_dl_files_button', 'n_clicks')],
    )
def update_downloadable_list(uploaded_filenames, uploaded_file_contents, n_clicks):
#    Save uploaded files and regenerate the file list.

    if uploaded_filenames is not None and uploaded_file_contents is not None:
        for name, data in zip(uploaded_filenames, uploaded_file_contents):
            save_file(name, data)

    files = uploaded_files()
    if len(files) == 0:
        return [html.Div("No files yet!")]
    else:
        return [html.Div(file_download_link(filename)) for filename in files]

"""
# Refresh downloadable files list
@app.callback(
    dash.dependencies.Output('file-list', 'children'),
    [dash.dependencies.Input('reload_dl_files_button', 'n_clicks')]
    )
def refresh_downloadable_files_dropdown(reload_dl_files_button):
    return [html.Div(file_download_link(filename)) for filename in reversed(retrieve_files(input_dir))]
"""


# Refresh files list
@app.callback(
    dash.dependencies.Output('file_choice', 'options'),
    [dash.dependencies.Input('reload_files_button', 'n_clicks')]
    )
def reload_files_dropdown(reload_files_button):
    return [{'label': i, 'value': i} for i in reversed(retrieve_files(input_dir))]

# Update chosen file text blurb
@app.callback(
    dash.dependencies.Output('chosen_file', 'children'),
    [dash.dependencies.Input('submit_button', 'n_clicks')],
    [dash.dependencies.State('file_choice', 'value')]
    )
def set_chosen_file(submit_button, file_choice):
    return 'You\'ve selected "{}"'.format(file_choice)


# Update files in the table once submit button is pressed
@app.callback(
    dash.dependencies.Output('table', 'data'),
    [dash.dependencies.Input('submit_button', 'n_clicks_timestamp'),
    dash.dependencies.Input('reset_button', 'n_clicks_timestamp')],
    [dash.dependencies.State('table', 'data'),
     dash.dependencies.State('table', 'columns'),
     dash.dependencies.State('table', 'data_previous'),
     dash.dependencies.State('file_choice', 'value')])
def update_table(submit_button, reset_button, data, columns, data_previous, file_choice):
    if file_choice and (int(submit_button)>int(reset_button)):
        data.append({c['id']: file_choice for c in columns})
    elif int(reset_button)>int(submit_button):
        data = df.to_dict("rows")
    return data

@app.callback(
    dash.dependencies.Output('merged_name', 'children'),
    [dash.dependencies.Input('merged_id', 'value')]
)
def update_output_div(value):
    return value



# Merge once confirm button is pressed.
@app.callback(
    dash.dependencies.Output('merge_id', 'children'),
    [dash.dependencies.Input('confirm_button', 'n_clicks_timestamp'),
    dash.dependencies.Input('reset_button', 'n_clicks_timestamp')],
    [dash.dependencies.State('table', 'data'),
     dash.dependencies.State('merged_name', 'children')]
    )
def merge(confirm_button, reset_button, data, merged_name):
    pdfs = [x['File Name'] for x in data]
    if int(reset_button)>int(confirm_button):
        pdfs=[]
    if len(pdfs)>1:
        file_name = merged_name
        MergePDFs.execute_merge(pdfs, temp_dir, input_dir, file_name)
        tmp_lst = pdfs[:]
        pdfs=[]
        return 'You\'ve merged "{}"'.format(tmp_lst)
    else: 
        return 'Please chose at least two files; "{}".'.format(pdfs)



# Refresh delete dropdown
@app.callback(
    dash.dependencies.Output('delete_drop', 'options'),
    [dash.dependencies.Input('refresh_delete', 'n_clicks')]
    )
def reload_delete_dropdown(reload_files_button):
    return [{'label': i, 'value': i} for i in reversed(retrieve_files(input_dir))]

# Delete a file
@app.callback(
    dash.dependencies.Output('deleted_file', 'children'),
    [dash.dependencies.Input('delete_button', 'n_clicks')],
    [dash.dependencies.State('delete_drop', 'value')]
    )
def set_chosen_file(submit_button, delete_drop):
    if os.path.exists(input_dir):
        if delete_drop:
            os.remove(str(delete_drop))
    return 'You\'ve deleted "{}"'.format(delete_drop)


if __name__ == '__main__':
    app.run_server(debug=True)
