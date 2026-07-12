import sys
from pathlib import Path

from sqlalchemy import text

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "backend"))

from app import create_app


def _table_exists(conn, table_name):
    result = conn.execute(
        text(
            """
            SELECT 1
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :table_name
            """
        ),
        {"table_name": table_name},
    ).first()
    return result is not None


def main():
    app = create_app()
    with app.app_context():
        engine = app.extensions["sqlalchemy"].engine
        with engine.begin() as conn:
            if not _table_exists(conn, "apelaciones_moderacion"):
                conn.execute(
                    text(
                        """
                        CREATE TABLE apelaciones_moderacion (
                            id INT UNSIGNED NOT NULL AUTO_INCREMENT,
                            anuncio_id INT UNSIGNED NOT NULL,
                            usuario_id INT UNSIGNED NOT NULL,
                            mensaje TEXT NOT NULL,
                            estado ENUM('PENDIENTE', 'ACEPTADA', 'RECHAZADA')
                                NOT NULL DEFAULT 'PENDIENTE',
                            respuesta_admin TEXT NULL,
                            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                            resolved_at DATETIME NULL,
                            PRIMARY KEY (id),
                            INDEX idx_apelaciones_anuncio (anuncio_id),
                            INDEX idx_apelaciones_usuario (usuario_id),
                            INDEX idx_apelaciones_estado (estado),
                            INDEX idx_apelaciones_created_at (created_at),
                            INDEX idx_apelaciones_resolved_at (resolved_at),
                            CONSTRAINT fk_apelaciones_anuncio
                                FOREIGN KEY (anuncio_id) REFERENCES anuncios (id)
                                ON DELETE CASCADE ON UPDATE CASCADE,
                            CONSTRAINT fk_apelaciones_usuario
                                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
                                ON DELETE CASCADE ON UPDATE CASCADE
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                        """
                    )
                )
                print("OK: tabla apelaciones_moderacion creada")
            else:
                print("OK: tabla apelaciones_moderacion ya existia")

            if not _table_exists(conn, "apelacion_evidencias"):
                conn.execute(
                    text(
                        """
                        CREATE TABLE apelacion_evidencias (
                            id INT UNSIGNED NOT NULL AUTO_INCREMENT,
                            apelacion_id INT UNSIGNED NOT NULL,
                            tipo_archivo ENUM('IMAGEN') NOT NULL DEFAULT 'IMAGEN',
                            ruta_relativa VARCHAR(500) NOT NULL,
                            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                            PRIMARY KEY (id),
                            INDEX idx_apelacion_evidencias_apelacion (apelacion_id),
                            INDEX idx_apelacion_evidencias_tipo (tipo_archivo),
                            INDEX idx_apelacion_evidencias_created_at (created_at),
                            CONSTRAINT fk_apelacion_evidencias_apelacion
                                FOREIGN KEY (apelacion_id) REFERENCES apelaciones_moderacion (id)
                                ON DELETE CASCADE ON UPDATE CASCADE
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                        """
                    )
                )
                print("OK: tabla apelacion_evidencias creada")
            else:
                print("OK: tabla apelacion_evidencias ya existia")


if __name__ == "__main__":
    main()
