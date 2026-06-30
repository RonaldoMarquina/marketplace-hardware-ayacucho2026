-- ============================================================
--  HardwareAyacucho â€” Esquema de Base de Datos MySQL
--  Generado desde HU-01 al HU-13
-- ============================================================

CREATE DATABASE IF NOT EXISTS hardware_ayacucho
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE hardware_ayacucho;

SET FOREIGN_KEY_CHECKS = 0;
SET SQL_MODE = 'STRICT_TRANS_TABLES,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO';

-- ------------------------------------------------------------
-- 1. USUARIOS
-- HU-01 (registro estÃ¡ndar), HU-02 (tienda), HU-04 (login)
-- ------------------------------------------------------------
CREATE TABLE usuarios (
    id              INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    nombre          VARCHAR(100)    NOT NULL,
    correo          VARCHAR(150)    NOT NULL,
    password_hash   VARCHAR(255)    NOT NULL,               -- bcrypt, salt=10
    telefono        CHAR(9)         NULL,                   -- 9 dÃ­gitos, puede ser NULL
    rol             ENUM(
                        'USER_ESTANDAR',
                        'TIENDA_VERIFICADA',
                        'ADMIN'
                    )               NOT NULL DEFAULT 'USER_ESTANDAR',
    estado          ENUM(
                        'PENDIENTE_VERIFICACION',
                        'ACTIVO',
                        'BLOQUEADO'
                    )               NOT NULL DEFAULT 'PENDIENTE_VERIFICACION',
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                    ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE  KEY uq_usuarios_correo (correo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ------------------------------------------------------------
-- 2. TIENDAS
-- HU-02 (registro de tienda verificada)
-- ------------------------------------------------------------
CREATE TABLE tiendas (
    id                  INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    usuario_id          INT UNSIGNED    NOT NULL,
    nombre_comercial    VARCHAR(150)    NOT NULL,
    ruc                 CHAR(11)        NOT NULL,
    direccion           VARCHAR(255)    NOT NULL,
    documento_identidad VARCHAR(255)    NOT NULL,           -- ruta relativa, nombre UUID
    estado              ENUM(
                            'EN_REVISION',
                            'ACTIVO',
                            'RECHAZADO'
                        )               NOT NULL DEFAULT 'EN_REVISION',
    created_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE  KEY uq_tiendas_ruc       (ruc),
    UNIQUE  KEY uq_tiendas_usuario   (usuario_id),
    CONSTRAINT fk_tiendas_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ------------------------------------------------------------
-- 3. TOKENS DE VERIFICACIÃ“N
-- HU-03 (verificaciÃ³n de correo electrÃ³nico)
-- ------------------------------------------------------------
CREATE TABLE tokens_verificacion (
    id          INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    usuario_id  INT UNSIGNED    NOT NULL,
    token       CHAR(64)        NOT NULL,                   -- secrets.token_hex(32) â†’ 64 hex chars
    tipo        ENUM(
                    'EMAIL_VERIFICATION'
                )               NOT NULL DEFAULT 'EMAIL_VERIFICATION',
    expira_en   DATETIME        NOT NULL,                   -- NOW() + 24h
    usado       TINYINT(1)      NOT NULL DEFAULT 0,
    created_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX       idx_tokens_token      (token),              -- HU-03: Ã­ndice requerido
    INDEX       idx_tokens_usuario    (usuario_id),
    CONSTRAINT fk_tokens_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ------------------------------------------------------------
-- 4. ANUNCIOS
-- HU-05 (publicar), HU-07 (editar), HU-08 (estados),
-- HU-09 (feed), HU-10 (filtrado), HU-11 (detalle)
-- ------------------------------------------------------------
CREATE TABLE anuncios (
    id                  INT UNSIGNED        NOT NULL AUTO_INCREMENT,
    usuario_id          INT UNSIGNED        NOT NULL,
    titulo              VARCHAR(100)        NOT NULL,
    descripcion         TEXT                NOT NULL,

    -- Categoria: grupo macro interno para organizar grandes secciones del marketplace.
    categoria           ENUM(
                            'COMPONENTES',
                            'REFRIGERACION',
                            'GABINETES',
                            'PERIFERICOS',
                            'MONITORES',
                            'REDES',
                            'MOBILIARIO',
                            'ALMACENAMIENTO_EXTERNO',
                            'ACCESORIOS',
                            'PORTATILES'
                        )                   NOT NULL,

    -- Subcategoria: clasificacion visible/buscable/filtrable por el usuario.
    -- Ejemplos: PROCESADOR, GPU, TECLADO, ROUTER, LAPTOP.
    subcategoria        VARCHAR(80)         NOT NULL,

    condicion           ENUM(
                            'NUEVO',
                            'COMO_NUEVO',
                            'USADO',
                            'PARA_REPUESTOS'
                        )                   NOT NULL,
    precio              DECIMAL(10, 2)      NOT NULL,       -- > 0, max 2 decimales

    -- Especificaciones: solo atributos tecnicos puros, variables por subcategoria.
    -- No guardar aqui categoria/subcategoria/tipo_componente.
    especificaciones    JSON                NULL,

    estado              ENUM(
                            'ACTIVO',
                            'INACTIVO',
                            'VENDIDO',
                            'BLOQUEADO'
                        )                   NOT NULL DEFAULT 'ACTIVO',
    reactivaciones_count INT UNSIGNED       NOT NULL DEFAULT 0,
    created_at          DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP
                                            ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_anuncios_estado       (estado),               -- HU-09: requerido
    INDEX idx_anuncios_created_at   (created_at),           -- HU-09: requerido
    INDEX idx_anuncios_usuario      (usuario_id),
    INDEX idx_anuncios_categoria    (categoria),
    INDEX idx_anuncios_subcategoria (subcategoria),         -- HU-05/HU-10: busqueda por producto visible

    CONSTRAINT fk_anuncios_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT chk_precio_positivo CHECK (precio > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Ãndice funcional para filtrado por spec socket (HU-10, activar si BD > 1000 registros)
-- ALTER TABLE anuncios ADD INDEX idx_spec_socket ((JSON_UNQUOTE(JSON_EXTRACT(especificaciones, '$.socket'))));

-- Migracion para bases ya existentes creadas antes de HU-07.
-- Ejecutar solo si la tabla anuncios ya existe y aun no tiene reactivaciones_count.
-- ALTER TABLE anuncios
-- ADD COLUMN reactivaciones_count INT UNSIGNED NOT NULL DEFAULT 0 AFTER estado;


-- ------------------------------------------------------------
-- 5. MEDIA DE ANUNCIO
-- HU-06 (carga de imagenes/videos), HU-11 (detalle)
-- ------------------------------------------------------------
CREATE TABLE media_anuncio (
    id              INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    anuncio_id      INT UNSIGNED    NOT NULL,
    tipo_media      ENUM('imagen', 'video') NOT NULL,
    ruta_relativa   VARCHAR(500)    NOT NULL,               -- relativa, nunca absoluta
    es_principal    TINYINT(1)      NOT NULL DEFAULT 0,     -- solo imagen puede ser principal
    orden           TINYINT UNSIGNED NULL,                  -- solo aplica a imagenes; video = NULL
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_media_anuncio      (anuncio_id),
    INDEX idx_media_tipo         (tipo_media),

    CONSTRAINT fk_media_anuncio
        FOREIGN KEY (anuncio_id) REFERENCES anuncios (id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ------------------------------------------------------------
-- 6. REPORTES
-- HU-13 (panel de moderaciÃ³n â€” reportar anuncio)
-- ------------------------------------------------------------
CREATE TABLE reportes (
    id          INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    anuncio_id  INT UNSIGNED    NOT NULL,
    usuario_id  INT UNSIGNED    NOT NULL,               -- quien reporta
    motivo      ENUM(
                    'FRAUDE',
                    'PRECIO_ENGAÃ‘OSO',
                    'PRODUCTO_FALSO',
                    'CONTENIDO_INAPROPIADO',
                    'DUPLICADO',
                    'OTRO'
                )               NOT NULL,
    estado      ENUM(
                    'PENDIENTE',
                    'REVISADO'
                )               NOT NULL DEFAULT 'PENDIENTE',
    created_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_reportes_anuncio  (anuncio_id),
    INDEX idx_reportes_usuario  (usuario_id),
    INDEX idx_reportes_estado   (estado),

    -- Un usuario no puede tener dos reportes PENDIENTE sobre el mismo anuncio
    UNIQUE KEY uq_reporte_pendiente (anuncio_id, usuario_id, estado),

    CONSTRAINT fk_reportes_anuncio
        FOREIGN KEY (anuncio_id) REFERENCES anuncios (id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_reportes_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ------------------------------------------------------------
-- 7. LOG DE MODERACIÃ“N
-- HU-13 (bloquear / desbloquear â€” auditorÃ­a permanente)
-- ------------------------------------------------------------
CREATE TABLE moderacion_log (
    id              INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    anuncio_id      INT UNSIGNED    NOT NULL,
    admin_id        INT UNSIGNED    NOT NULL,
    accion          ENUM(
                        'BLOQUEADO',
                        'DESBLOQUEADO'
                    )               NOT NULL,
    motivo_admin    TEXT            NULL,                   -- requerido al bloquear
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_modlog_anuncio (anuncio_id),
    INDEX idx_modlog_admin   (admin_id),

    -- AuditorÃ­a permanente: sin DELETE ni CASCADE
    CONSTRAINT fk_modlog_anuncio
        FOREIGN KEY (anuncio_id) REFERENCES anuncios (id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_modlog_admin
        FOREIGN KEY (admin_id) REFERENCES usuarios (id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ------------------------------------------------------------
-- 8. LOG DE CONTACTOS (WhatsApp)
-- HU-12 (contacto directo)
-- ------------------------------------------------------------
CREATE TABLE contactos_log (
    id              INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    comprador_id    INT UNSIGNED    NOT NULL,
    vendedor_id     INT UNSIGNED    NOT NULL,
    anuncio_id      INT UNSIGNED    NOT NULL,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_contactos_comprador (comprador_id),
    INDEX idx_contactos_vendedor  (vendedor_id),
    INDEX idx_contactos_anuncio   (anuncio_id),

    CONSTRAINT fk_contactos_comprador
        FOREIGN KEY (comprador_id) REFERENCES usuarios (id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_contactos_vendedor
        FOREIGN KEY (vendedor_id) REFERENCES usuarios (id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_contactos_anuncio
        FOREIGN KEY (anuncio_id) REFERENCES anuncios (id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
--  RESUMEN DE TABLAS
-- ============================================================
-- usuarios            â†’ HU-01, HU-02, HU-04
-- tiendas             â†’ HU-02, HU-11
-- tokens_verificacion â†’ HU-03
-- anuncios            â†’ HU-05, HU-07, HU-08, HU-09, HU-10, HU-11
-- imagenes_anuncio    â†’ HU-06, HU-11
-- reportes            â†’ HU-13
-- moderacion_log      â†’ HU-13
-- contactos_log       â†’ HU-12
-- ============================================================



