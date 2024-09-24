from flask import Flask, render_template
from data_sources.reddit import collect_data

# Flask app initialization
app = Flask(__name__)

@app.route('/')
def index():
    company_name = 'google'
    posts_data = collect_data(company_name)

    return render_template('index.html', company_name=company_name, posts_data=posts_data)

if __name__ == "__main__":
    app.run(debug=True)
