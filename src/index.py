import os
from flask import Flask, render_template


app = Flask(__name__)

print(os.listdir(os.getcwd()))

@app.route('/')
def home():
   
    return render_template("index.html")


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/contact')
def portfolio():
    
    return render_template("contact.html")


@app.route('/listing-page')
def contact():
    return render_template("listing-page.html")



@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


if __name__ == '__main__':
    #port = int(os.environ.get('PORT', 5000))
    print(os.getcwd())
    app.run(debug=True)