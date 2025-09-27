from flask import Flask
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde el archivo .env
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Registrar blueprints
    from routes.main import main_bp
    from routes.ejemplo import ejemplo_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(ejemplo_bp)
    # app.register_blueprint(ejemplo_bp, url_prefix='/api')  # opcional
    
    return app

if __name__ == '__main__':
    app = create_app()
    #print(f"puerto={os.getenv('FLASK_PORT', 8080)}")
    # Leer el puerto desde .env, con valor por defecto 5000 si no está definido
    port = int(os.getenv('FLASK_PORT', 8080))
    
    app.run(
        debug=True,
        host='0.0.0.0',
        port=port
    )