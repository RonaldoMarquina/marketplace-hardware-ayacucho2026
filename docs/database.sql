-- ============================================================
--  HardwareAyacucho â€” Esquema de Base de Datos MySQL
--  Respaldo consistente del backend implementado hasta HU-21
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
                        'EN_REVISION',
                        'RECHAZADO',
                        'ACTIVO',
                        'BLOQUEADO',
                        'BLOQUEADO_TEMP'
                    )               NOT NULL DEFAULT 'PENDIENTE_VERIFICACION',
    intentos_fallidos TINYINT UNSIGNED NOT NULL DEFAULT 0,
    calificacion_promedio_vendedor DECIMAL(3,1) NULL,
    total_calificaciones_vendedor  INT UNSIGNED NOT NULL DEFAULT 0,
    calificacion_promedio_comprador DECIMAL(3,1) NULL,
    total_calificaciones_comprador INT UNSIGNED NOT NULL DEFAULT 0,
    bloqueado_hasta DATETIME       NULL,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                    ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE  KEY uq_usuarios_correo (correo),
    UNIQUE  KEY uq_usuarios_telefono (telefono)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ------------------------------------------------------------
-- 2. TIENDAS
-- HU-02 (registro de tienda verificada)
-- ------------------------------------------------------------
CREATE TABLE tiendas (
    id                  INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    usuario_id          INT UNSIGNED    NOT NULL,
    nombre_comercial    VARCHAR(100)    NOT NULL,
    ruc                 CHAR(11)        NOT NULL,
    direccion           VARCHAR(200)    NOT NULL,
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
    UNIQUE  KEY uq_tiendas_nombre_comercial (nombre_comercial),
    UNIQUE  KEY uq_tiendas_ruc             (ruc),
    UNIQUE  KEY uq_tiendas_usuario         (usuario_id),
    CONSTRAINT fk_tiendas_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ------------------------------------------------------------
-- 3. TOKENS DE VERIFICACIÃ“N
-- HU-03 (verificaciÃ³n de correo electrÃ³nico), HU-21 (reset de password)
-- ------------------------------------------------------------
CREATE TABLE tokens_verificacion (
    id          INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    usuario_id  INT UNSIGNED    NOT NULL,
    token       CHAR(64)        NOT NULL,                   -- secrets.token_hex(32) â†’ 64 hex chars
    tipo        ENUM(
                    'EMAIL_VERIFICATION',
                    'PASSWORD_RESET'
                )               NOT NULL DEFAULT 'EMAIL_VERIFICATION',
    expira_en   DATETIME        NOT NULL,                   -- verify=24h / reset=1h
    usado       TINYINT(1)      NOT NULL DEFAULT 0,
    created_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY  uq_tokens_token       (token),
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
    comprador_id        INT UNSIGNED        NULL,
    vendido_at          DATETIME            NULL,
    created_at          DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP
                                            ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_anuncios_estado       (estado),               -- HU-09: requerido
    INDEX idx_anuncios_created_at   (created_at),           -- HU-09: requerido
    INDEX idx_anuncios_usuario      (usuario_id),
    INDEX idx_anuncios_comprador    (comprador_id),
    INDEX idx_anuncios_categoria    (categoria),
    INDEX idx_anuncios_subcategoria (subcategoria),         -- HU-05/HU-10: busqueda por producto visible

    CONSTRAINT fk_anuncios_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_anuncios_comprador
        FOREIGN KEY (comprador_id) REFERENCES usuarios (id)
        ON DELETE SET NULL ON UPDATE CASCADE,

    CONSTRAINT chk_precio_positivo CHECK (precio > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Ãndice funcional para filtrado por spec socket (HU-10, activar si BD > 1000 registros)
-- ALTER TABLE anuncios ADD INDEX idx_spec_socket ((JSON_UNQUOTE(JSON_EXTRACT(especificaciones, '$.socket'))));

-- Migraciones para bases ya existentes creadas antes de HU-07 / HU-14.
-- ALTER TABLE anuncios
-- ADD COLUMN reactivaciones_count INT UNSIGNED NOT NULL DEFAULT 0 AFTER estado;
-- ALTER TABLE anuncios
-- ADD COLUMN comprador_id INT UNSIGNED NULL AFTER reactivaciones_count,
-- ADD COLUMN vendido_at DATETIME NULL AFTER comprador_id,
-- ADD INDEX idx_anuncios_comprador (comprador_id),
-- ADD CONSTRAINT fk_anuncios_comprador
--     FOREIGN KEY (comprador_id) REFERENCES usuarios (id)
--     ON DELETE SET NULL ON UPDATE CASCADE;


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
-- 6. REPORTES DE ANUNCIOS
-- HU-13 (moderacion)
-- ------------------------------------------------------------
CREATE TABLE reportes (
    id              INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    comprador_id    INT UNSIGNED    NOT NULL,
    anuncio_id      INT UNSIGNED    NOT NULL,
    motivo          ENUM(
                        'FRAUDE',
                        'PRECIO_ENGANOSO',
                        'PRODUCTO_FALSO',
                        'CONTENIDO_INAPROPIADO',
                        'DUPLICADO',
                        'OTRO'
                    )               NOT NULL,
    estado          ENUM(
                        'PENDIENTE',
                        'REVISADO'
                    )               NOT NULL DEFAULT 'PENDIENTE',
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_reportes_comprador   (comprador_id),
    INDEX idx_reportes_anuncio     (anuncio_id),
    INDEX idx_reportes_estado      (estado),
    INDEX idx_reportes_created_at  (created_at),

    CONSTRAINT fk_reportes_comprador
        FOREIGN KEY (comprador_id) REFERENCES usuarios (id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_reportes_anuncio
        FOREIGN KEY (anuncio_id) REFERENCES anuncios (id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ------------------------------------------------------------
-- 7. AUDITORIA DE MODERACION
-- HU-13 (moderacion admin)
-- ------------------------------------------------------------
CREATE TABLE moderacion_log (
    id              INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    admin_id        INT UNSIGNED    NOT NULL,
    anuncio_id      INT UNSIGNED    NOT NULL,
    accion          ENUM(
                        'BLOQUEADO',
                        'DESBLOQUEADO'
                    )               NOT NULL,
    motivo_admin    TEXT            NOT NULL,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_moderacion_admin      (admin_id),
    INDEX idx_moderacion_anuncio    (anuncio_id),
    INDEX idx_moderacion_accion     (accion),
    INDEX idx_moderacion_created_at (created_at),

    CONSTRAINT fk_moderacion_admin
        FOREIGN KEY (admin_id) REFERENCES usuarios (id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_moderacion_anuncio
        FOREIGN KEY (anuncio_id) REFERENCES anuncios (id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ------------------------------------------------------------
-- 8. AUDITORIA ADMIN UNIFICADA
-- HU-13 (moderacion anuncios), HU-20 (gestion de usuarios)
-- ------------------------------------------------------------
CREATE TABLE admin_log (
    id              INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    admin_id        INT UNSIGNED    NOT NULL,
    usuario_id      INT UNSIGNED    NULL,
    anuncio_id      INT UNSIGNED    NULL,
    accion          ENUM(
                        'USUARIO_ACTIVADO',
                        'TIENDA_RECHAZADA',
                        'USUARIO_BLOQUEADO',
                        'USUARIO_DESBLOQUEADO',
                        'BLOQUEADO',
                        'DESBLOQUEADO'
                    )               NOT NULL,
    motivo          TEXT            NULL,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_admin_log_admin      (admin_id),
    INDEX idx_admin_log_usuario    (usuario_id),
    INDEX idx_admin_log_anuncio    (anuncio_id),
    INDEX idx_admin_log_accion     (accion),
    INDEX idx_admin_log_created_at (created_at),

    CONSTRAINT fk_admin_log_admin
        FOREIGN KEY (admin_id) REFERENCES usuarios (id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_admin_log_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_admin_log_anuncio
        FOREIGN KEY (anuncio_id) REFERENCES anuncios (id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ------------------------------------------------------------
-- 9. TRANSACCIONES
-- HU-14 (marcar vendido)
-- ------------------------------------------------------------
CREATE TABLE transacciones (
    id                              INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    anuncio_id                      INT UNSIGNED    NOT NULL,
    vendedor_id                     INT UNSIGNED    NOT NULL,
    comprador_id                    INT UNSIGNED    NOT NULL,
    calificacion_vendedor_pending   TINYINT(1)      NOT NULL DEFAULT 1,
    calificacion_comprador_pending  TINYINT(1)      NOT NULL DEFAULT 1,
    created_at                      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_transacciones_anuncio    (anuncio_id),
    INDEX idx_transacciones_vendedor   (vendedor_id),
    INDEX idx_transacciones_comprador  (comprador_id),
    INDEX idx_transacciones_vendedor_created_at  (vendedor_id, created_at),
    INDEX idx_transacciones_comprador_created_at (comprador_id, created_at),
    INDEX idx_transacciones_created_at (created_at),

    CONSTRAINT fk_transacciones_anuncio
        FOREIGN KEY (anuncio_id) REFERENCES anuncios (id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_transacciones_vendedor
        FOREIGN KEY (vendedor_id) REFERENCES usuarios (id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_transacciones_comprador
        FOREIGN KEY (comprador_id) REFERENCES usuarios (id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ------------------------------------------------------------
-- 10. CALIFICACIONES
-- HU-15 (calificar vendedor), HU-16 (calificar comprador)
-- ------------------------------------------------------------
CREATE TABLE calificaciones (
    id              INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    transaccion_id  INT UNSIGNED    NOT NULL,
    calificador_id  INT UNSIGNED    NOT NULL,
    calificado_id   INT UNSIGNED    NOT NULL,
    tipo            ENUM(
                        'COMPRADOR_A_VENDEDOR',
                        'VENDEDOR_A_COMPRADOR'
                    )               NOT NULL,
    puntaje         TINYINT UNSIGNED NOT NULL,
    comentario      TEXT            NULL,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_calificaciones_transaccion (transaccion_id),
    INDEX idx_calificaciones_calificador (calificador_id),
    INDEX idx_calificaciones_calificado  (calificado_id),
    INDEX idx_calificaciones_tipo        (tipo),
    INDEX idx_calificaciones_created_at  (created_at),

    CONSTRAINT fk_calificaciones_transaccion
        FOREIGN KEY (transaccion_id) REFERENCES transacciones (id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_calificaciones_calificador
        FOREIGN KEY (calificador_id) REFERENCES usuarios (id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_calificaciones_calificado
        FOREIGN KEY (calificado_id) REFERENCES usuarios (id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_calificaciones_puntaje CHECK (puntaje BETWEEN 1 AND 5)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ------------------------------------------------------------
-- 11. LOG DE CONTACTOS (WhatsApp)
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
-- tokens_verificacion â†’ HU-03, HU-21
-- anuncios            â†’ HU-05, HU-07, HU-08, HU-09, HU-10, HU-11
-- media_anuncio       â†’ HU-06, HU-11
-- reportes            â†’ HU-13
-- moderacion_log      â†’ HU-13
-- admin_log           â†’ HU-13, HU-20
-- transacciones       â†’ HU-14
-- calificaciones      â†’ HU-15, HU-16
-- contactos_log       â†’ HU-12
-- ============================================================
