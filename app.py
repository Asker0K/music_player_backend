from app import create_app

app = create_app('dev')

if __name__ == '__main__':
    # app.run()
    app.run(host='localhost', port=5001, debug=False)
