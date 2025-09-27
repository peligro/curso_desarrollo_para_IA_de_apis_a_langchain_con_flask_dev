from flask import Flask, render_template
from dotenv import load_dotenv
import os
from http import HTTPStatus
from flask_wtf.csrf import CSRFProtect  # ← Importa CSRFProtect


# Cargar variables de entorno desde el archivo .env
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv('FLASK_KEY')
    # Activa la protección CSRF
    csrf = CSRFProtect(app)
    # Registrar blueprints
    from routes.main.main import main_bp
    from routes.ejemplo.ejemplo import ejemplo_bp
    from routes.parametros.main import parametros_bp
    from routes.diseno.main import diseno_bp
    from routes.health.main import health_bp
    from routes.formularios.main import formularios_bp
    from routes.mistral.main import mistral_bp
    from routes.gemini.main import gemini_bp

    
    app.register_blueprint(main_bp)
    app.register_blueprint(ejemplo_bp)
    # app.register_blueprint(ejemplo_bp, url_prefix='/api')  # opcional
    app.register_blueprint(parametros_bp)
    app.register_blueprint(diseno_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(formularios_bp)
    app.register_blueprint(mistral_bp)
    app.register_blueprint(gemini_bp)


    # Manejador personalizado para error 404
    @app.errorhandler(HTTPStatus.NOT_FOUND)
    def not_found(error):
        return render_template('errors/404.html'), HTTPStatus.NOT_FOUND
    

    # Manejador personalizado para error 500
    @app.errorhandler(Exception)
    @app.errorhandler(HTTPStatus.INTERNAL_SERVER_ERROR)
    def internal_error(error):
        # Si estás en modo debug, muestra el error real
        if app.debug:
            #return f"<h1>500 - Error interno</h1><pre>{error}</pre>", HTTPStatus.INTERNAL_SERVER_ERROR
            error=f"Error:{error}"
        else:
            error=''
        return render_template('errors/500.html', **{'error': error}), HTTPStatus.INTERNAL_SERVER_ERROR
    

    return app





if __name__ == '__main__':
    app = create_app()
    #print(f"puerto={os.getenv('FLASK_PORT', 8080)}")
    # Leer el puerto desde .env, con valor por defecto 5000 si no está definido
    port = int(os.getenv('FLASK_PORT', 8080))
    debug = True if os.getenv('FLASK_DEBUG') == 'True' else False
    app.run(
        debug=debug,
        host='0.0.0.0',
        port=port
    )