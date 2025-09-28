from flask import Blueprint, abort, Response, current_app
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import os
import mimetypes
from datetime import datetime, timedelta
from aws.aws import get_conection  # Asumiendo que está en aws/aws.py


bucket_s3_bp = Blueprint('bucket_s3', __name__)


def is_valid_bucket(bucket_name: str) -> bool:
    """Valida que el bucket sea el permitido (igual al de la app)"""
    allowed_bucket = os.getenv('AWS_BUCKET')  # Asegúrate de tener esta variable
    return bucket_name == allowed_bucket



@bucket_s3_bp.route('/bucket-s3/ver/<bucket>/<path:imagen>')
def bucket_s3_ver(bucket, imagen):
    """
    Proxy para servir imágenes desde S3 de forma segura.
    Usa <path:imagen> para permitir slashes en la URL.
    """
    # 1. Validar bucket
    if not is_valid_bucket(bucket):
        current_app.logger.warning(f"Intento de acceso a bucket no autorizado: {bucket}")
        abort(404)

    

    s3_client = get_conection()

    try:
        # 3. Verificar que el objeto existe (sin descargarlo)
        s3_client.head_object(Bucket=bucket, Key=imagen)
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            current_app.logger.warning(f"Archivo no encontrado en S3: {imagen}")
            abort(404)
        else:
            current_app.logger.error(f"Error al acceder a S3: {e}")
            abort(500)
    except NoCredentialsError:
        current_app.logger.error("Credenciales de AWS no configuradas")
        abort(500)

    try:
        # 4. Obtener el objeto
        response = s3_client.get_object(Bucket=bucket, Key=imagen)
        file_data = response['Body'].read()
        content_type = response.get('ContentType')

        # Si no hay ContentType, adivinar por extensión
        if not content_type:
            content_type, _ = mimetypes.guess_type(imagen)
            if not content_type:
                content_type = 'application/octet-stream'

        # 5. Configurar headers
        last_modified = response.get('LastModified')
        if last_modified:
            last_modified_str = last_modified.strftime('%a, %d %b %Y %H:%M:%S GMT')
        else:
            last_modified_str = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')

        headers = {
            'Content-Type': content_type,
            'Content-Length': str(len(file_data)),
            'Content-Disposition': 'inline',
            'Last-Modified': last_modified_str,
            'Cache-Control': 'public, max-age=3600',
            'Expires': (datetime.utcnow() + timedelta(hours=1)).strftime('%a, %d %b %Y %H:%M:%S GMT'),
        }

        # 6. Devolver la respuesta
        return Response(file_data, headers=headers)

    except ClientError as e:
        current_app.logger.error(f"Error al obtener archivo de S3: {e}")
        abort(404)
    except Exception as e:
        current_app.logger.error(f"Error inesperado: {e}")
        abort(500)

"""
from flask import Blueprint

bucket_s3_bp = Blueprint('bucket_s3', __name__)

@bucket_s3_bp.route('/bucket-s3/ver/<bucket>/<imagen>')
def bucket_s3_ver(bucket, imagen):
    return "ver imágeness bucket"
"""