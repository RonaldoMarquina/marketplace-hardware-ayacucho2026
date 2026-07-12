from app import create_app  # pylint: disable=cyclic-import


def build_app():
    return create_app()


app = build_app()

if __name__ == "__main__":
    # Esto es lo que mantiene al servidor activo "escuchando" peticiones
    app.run(debug=True)
