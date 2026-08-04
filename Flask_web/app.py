from flask import Flask, render_template
app = Flask(__name__)
@app.route('/<name>')
def hello(name):
    if name == 'ethan':
        return render_template('index.html', name=name)
    else:
        return render_template('index.html', name='world')
if __name__ == "__main__":
    app.run()