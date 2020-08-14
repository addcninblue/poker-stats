from flask import Flask, render_template, request, redirect
import codecs
from poker_analysis.library import read_csv
from poker_analysis.analysis import plot_stack_counts, get_statistics

app = Flask(__name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() == "csv"

def handle_file(file):
    csv = read_csv(codecs.iterdecode(file, 'utf-8'))
    return get_statistics(csv)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            # No file part
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            # No selected file
            return redirect(request.url)
        if file and allowed_file(file.filename):
            return handle_file(file)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
