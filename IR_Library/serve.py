from vector_space import *
from flask import Flask, request, render_template, url_for, redirect
from forms import *
import json

with open('Book_info.json', 'r', encoding='utf-8') as json_file:
    data = json.load(json_file)

global model
model = None
# Khởi tạo flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'any string works here'
app.static_folder = 'static'

# Create Categories
categories = ['AUTHOR', 'TOPIC', 'CONTENT']


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = SearchForm()
    query = form.data['search']
    selected = request.form.get('comp_select')
    checkbox = request.form.get('rating')
    if checkbox is not None:
        f = open("rating/rating.txt", "a")
        f.write(checkbox+'\n')
        f.close()
        return render_template('index.html', form=form, categories=categories)
    if query and selected is not None:
        results = {
            'query': query,
            'category': selected,
            'checkbox': checkbox
        }
        results = predict(results)
        return render_template('index.html', form=form, query=query, results=results, data=data, categories=categories)
    return render_template('index.html', form=form, categories=categories)


@app.route("/search", methods=["POST"])
def predict(res):
    data = {'rank': []}
    if res['query']:
        # Lấy query
        query = res['query']
        # dự báo rank
        rank = Search(res['query'], res['category'])
        # argmax 5
        data["rank"] = rank[:5]
    return data["rank"]


@app.route("/redirect", methods=["POST"])
def redirect():
    form = SearchForm()
    return render_template('index.html', form=form, categories=categories)


if __name__ == "__main__":
    print("App run!")
    # Load model
    app.run(debug=False, threaded=False)
