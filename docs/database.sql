-- ============================================================
-- HardwareAyacucho - Esquema maestro de base de datos
-- Fuente de verdad para recrear la BD en local o en nube
-- Compatibilidad objetivo: MySQL / TiDB
-- ============================================================

CREATE DATABASE IF NOT EXISTS hardware_ayacucho
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE hardware_ayacucho;

SET FOREIGN_KEY_CHECKS = 0;

SET SQL_MODE = 'STRICT_TRANS_TABLES,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO';

-- Ejecuta este archivo completo cuando necesites crear la base desde cero.
-- Para una base ya existente, usa solo los ALTER TABLE documentados al final.

-- ------------------------------------------------------------
-- 1. USUARIOS
-- HU-01 (registro estandar), HU-02 (tienda), HU-04 (login)
-- ------------------------------------------------------------
CREATE TABLE usuarios (
    id              INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    nombre          VARCHAR(100)    NOT NULL,
    correo          VARCHAR(150)    NOT NULL,
    password_hash   VARCHAR(255)    NOT NULL,               -- bcrypt, salt=10
    telefono        CHAR(9)         NULL,                   -- 9 digitos, puede ser NULL
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
    UNIQUE  KEY uq_usuarios_telefono (telefono),
    INDEX   idx_usuarios_rol (rol),
    INDEX   idx_usuarios_estado (estado)
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
-- 3. TOKENS DE VERIFICACION
-- HU-03 (verificacion de correo electronico), HU-21 (reset de password)
-- ------------------------------------------------------------
CREATE TABLE tokens_verificacion (
    id          INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    usuario_id  INT UNSIGNED    NOT NULL,
    token       CHAR(64)        NOT NULL,                   -- secrets.token_hex(32) -> 64 hex chars
    tipo        ENUM(
                    'EMAIL_VERIFICATION',
                    'PASSWORD_RESET'
                )               NOT NULL DEFAULT 'EMAIL_VERIFICATION',
    expira_en   DATETIME        NOT NULL,                   -- verify=24h / reset=1h
    usado       TINYINT(1)      NOT NULL DEFAULT 0,
    created_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY  uq_tokens_token       (token),
    INDEX       idx_tokens_token      (token),              -- HU-03: indice requerido
    INDEX       idx_tokens_usuario    (usuario_id),
    INDEX       idx_tokens_tipo       (tipo),
    INDEX       idx_tokens_usuario_tipo (usuario_id, tipo, usado),
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

    -- Subcategoria: clasificacion visible, buscable y filtrable por el usuario.
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
    -- No guardar aqui categoria, subcategoria ni tipo_componente.
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

-- ------------------------------------------------------------
-- 5. MEDIA DE ANUNCIO
-- HU-06 (carga de imagenes/videos), HU-11 (detalle)
-- ------------------------------------------------------------
CREATE TABLE media_anuncio (
    id              INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    anuncio_id      INT UNSIGNED    NOT NULL,
    tipo_media      ENUM('imagen', 'video') NOT NULL,
    ruta_relativa   VARCHAR(500)    NOT NULL,               -- URL segura Cloudinary o ruta relativa local
    public_id       VARCHAR(255)    NULL,                   -- identificador remoto en Cloudinary
    resource_type   VARCHAR(20)     NULL,                   -- image o video segun proveedor
    formato         VARCHAR(20)     NULL,                   -- extension/formato reportado por Cloudinary
    bytes_size      INT UNSIGNED    NULL,                   -- peso del archivo en bytes
    width           INT UNSIGNED    NULL,                   -- ancho si aplica
    height          INT UNSIGNED    NULL,                   -- alto si aplica
    version         VARCHAR(50)     NULL,                   -- version remota para cache busting
    es_principal    TINYINT(1)      NOT NULL DEFAULT 0,     -- solo imagen puede ser principal
    orden           TINYINT UNSIGNED NULL,                  -- solo aplica a imagenes; video = NULL
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_media_anuncio      (anuncio_id),
    INDEX idx_media_tipo         (tipo_media),
    INDEX idx_media_public_id    (public_id),

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
    detalle         TEXT            NULL,
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

CREATE TABLE reporte_evidencias (
    id              INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    reporte_id      INT UNSIGNED    NOT NULL,
    tipo_archivo    ENUM('IMAGEN')  NOT NULL DEFAULT 'IMAGEN',
    ruta_relativa   VARCHAR(500)    NOT NULL,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_reporte_evidencias_reporte      (reporte_id),
    INDEX idx_reporte_evidencias_tipo         (tipo_archivo),
    INDEX idx_reporte_evidencias_created_at   (created_at),

    CONSTRAINT fk_reporte_evidencias_reporte
        FOREIGN KEY (reporte_id) REFERENCES reportes (id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ------------------------------------------------------------
-- 7. APELACIONES Y DESCARGOS
-- HU-13 (moderacion fase 2)
-- ------------------------------------------------------------
CREATE TABLE apelaciones_moderacion (
    id                  INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    anuncio_id          INT UNSIGNED    NOT NULL,
    usuario_id          INT UNSIGNED    NOT NULL,
    mensaje             TEXT            NOT NULL,
    estado              ENUM(
                            'PENDIENTE',
                            'ACEPTADA',
                            'RECHAZADA'
                        )               NOT NULL DEFAULT 'PENDIENTE',
    respuesta_admin     TEXT            NULL,
    created_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at         DATETIME        NULL,

    PRIMARY KEY (id),
    INDEX idx_apelaciones_anuncio      (anuncio_id),
    INDEX idx_apelaciones_usuario      (usuario_id),
    INDEX idx_apelaciones_estado       (estado),
    INDEX idx_apelaciones_created_at   (created_at),
    INDEX idx_apelaciones_resolved_at  (resolved_at),

    CONSTRAINT fk_apelaciones_anuncio
        FOREIGN KEY (anuncio_id) REFERENCES anuncios (id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_apelaciones_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE apelacion_evidencias (
    id              INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    apelacion_id    INT UNSIGNED    NOT NULL,
    tipo_archivo    ENUM('IMAGEN')  NOT NULL DEFAULT 'IMAGEN',
    ruta_relativa   VARCHAR(500)    NOT NULL,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_apelacion_evidencias_apelacion    (apelacion_id),
    INDEX idx_apelacion_evidencias_tipo         (tipo_archivo),
    INDEX idx_apelacion_evidencias_created_at   (created_at),

    CONSTRAINT fk_apelacion_evidencias_apelacion
        FOREIGN KEY (apelacion_id) REFERENCES apelaciones_moderacion (id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ------------------------------------------------------------
-- 8. AUDITORIA DE MODERACION
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
-- 9. AUDITORIA ADMIN UNIFICADA
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
-- 10. TRANSACCIONES
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
-- 11. CALIFICACIONES
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
-- 12. LOG DE CONTACTOS (WhatsApp)
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
-- usuarios            -> HU-01, HU-02, HU-04
-- tiendas             -> HU-02, HU-11
-- tokens_verificacion -> HU-03, HU-21
-- anuncios            -> HU-05, HU-07, HU-08, HU-09, HU-10, HU-11
-- media_anuncio       -> HU-06, HU-11
-- reportes            -> HU-13
-- reporte_evidencias  -> HU-13
-- apelaciones_moderacion -> HU-13
-- apelacion_evidencias   -> HU-13
-- moderacion_log      -> HU-13
-- admin_log           -> HU-13, HU-20
-- transacciones       -> HU-14
-- calificaciones      -> HU-15, HU-16
-- contactos_log       -> HU-12
-- ============================================================
