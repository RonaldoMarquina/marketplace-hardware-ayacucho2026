from app import create_app

app = create_app()

if __name__ == '__main__':
    # Esto es lo que mantiene al servidor activo "escuchando" peticiones
    app.run(debug=True)
