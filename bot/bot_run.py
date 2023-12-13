from bot_app import create_app
from bot_routes import init_routes

app = create_app()
init_routes(app)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5000)
