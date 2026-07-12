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


def _column_exists(conn, table_name, column_name):
    result = conn.execute(
        text(
            """
            SELECT 1
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = :table_name
              AND COLUMN_NAME = :column_name
            """
        ),
        {"table_name": table_name, "column_name": column_name},
    ).first()
    return result is not None


def main():
    app = create_app()
    with app.app_context():
        engine = app.extensions["sqlalchemy"].engine
        with engine.begin() as conn:
            if not _column_exists(conn, "reportes", "detalle"):
                conn.execute(text("ALTER TABLE reportes ADD COLUMN detalle TEXT NULL AFTER motivo"))
                print("OK: columna reportes.detalle creada")
            else:
                print("OK: columna reportes.detalle ya existia")

            if not _table_exists(conn, "reporte_evidencias"):
                conn.execute(
                    text(
                        """
                        CREATE TABLE reporte_evidencias (
                            id INT UNSIGNED NOT NULL AUTO_INCREMENT,
                            reporte_id INT UNSIGNED NOT NULL,
                            tipo_archivo ENUM('IMAGEN') NOT NULL DEFAULT 'IMAGEN',
                            ruta_relativa VARCHAR(500) NOT NULL,
                            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                            PRIMARY KEY (id),
                            INDEX idx_reporte_evidencias_reporte (reporte_id),
                            INDEX idx_reporte_evidencias_tipo (tipo_archivo),
                            INDEX idx_reporte_evidencias_created_at (created_at),
                            CONSTRAINT fk_reporte_evidencias_reporte
                                FOREIGN KEY (reporte_id) REFERENCES reportes (id)
                                ON DELETE CASCADE ON UPDATE CASCADE
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                        """
                    )
                )
                print("OK: tabla reporte_evidencias creada")
            else:
                print("OK: tabla reporte_evidencias ya existia")


if __name__ == "__main__":
    main()
