from bottle import Bottle, run

app = Bottle()
@app.route('/login')
def login():
    return {'jsession': 'hello'}

if __name__ == "__main__":
    run(app, host='localhost', port='8088')