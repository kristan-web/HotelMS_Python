-- =============================================================
--  Hotel Management System — Full Database Schema
--  Database : hotel_ms
--  Engine   : InnoDB  |  Charset: utf8mb4
-- =============================================================

CREATE DATABASE IF NOT EXISTS hotel_ms
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE hotel_ms;

-- -------------------------------------------------------------
-- 1. USERS  (admins & staff, with soft-delete)
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    user_id     INT             NOT NULL AUTO_INCREMENT,
    first_name  VARCHAR(100)    NOT NULL,
    last_name   VARCHAR(100)    NOT NULL,
    email       VARCHAR(255)    NOT NULL UNIQUE,
    phone       VARCHAR(20)     NOT NULL,
    password    VARCHAR(255)    NOT NULL,          -- bcrypt hash
    role        ENUM('Admin','Staff') NOT NULL DEFAULT 'Staff',
    is_deleted  TINYINT(1)      NOT NULL DEFAULT 0,
    created_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id)
) ENGINE=InnoDB;

-- -------------------------------------------------------------
-- 2. ADMIN LOGS
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS admin_logs (
    log_id      INT             NOT NULL AUTO_INCREMENT,
    user_id     INT             NOT NULL,
    action      VARCHAR(255)    NOT NULL,
    description TEXT            NULL,
    logged_at   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (log_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- -------------------------------------------------------------
-- 3. GUESTS  (with soft-delete)
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS guests (
    guest_id    INT             NOT NULL AUTO_INCREMENT,
    first_name  VARCHAR(100)    NOT NULL,
    last_name   VARCHAR(100)    NOT NULL,
    email       VARCHAR(255)    NOT NULL UNIQUE,
    phone       VARCHAR(20)     NOT NULL,
    address     VARCHAR(255)    NOT NULL,
    is_deleted  TINYINT(1)      NOT NULL DEFAULT 0,
    created_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (guest_id)
) ENGINE=InnoDB;

-- -------------------------------------------------------------
-- 4. ROOMS
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS rooms (
    room_id     INT             NOT NULL AUTO_INCREMENT,
    room_number VARCHAR(20)     NOT NULL UNIQUE,
    room_type   ENUM('SINGLE','DOUBLE','DELUXE','SUITE') NOT NULL,
    price       DECIMAL(10,2)   NOT NULL,
    capacity    INT             NOT NULL DEFAULT 1,
    status      ENUM('AVAILABLE','OCCUPIED','MAINTENANCE') NOT NULL DEFAULT 'AVAILABLE',
    description TEXT            NULL,
    created_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (room_id)
) ENGINE=InnoDB;

-- -------------------------------------------------------------
-- 5. SERVICES  (with soft-delete)
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS services (
    service_id  INT             NOT NULL AUTO_INCREMENT,
    name        VARCHAR(150)    NOT NULL,
    price       DECIMAL(10,2)   NOT NULL,
    duration    INT             NOT NULL DEFAULT 0,   -- in minutes
    status      ENUM('Active','Inactive','Maintenance') NOT NULL DEFAULT 'Active',
    is_deleted  TINYINT(1)      NOT NULL DEFAULT 0,
    created_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (service_id)
) ENGINE=InnoDB;

-- -------------------------------------------------------------
-- 6. RESERVATIONS
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reservations (
    reservation_id  INT         NOT NULL AUTO_INCREMENT,
    guest_id        INT         NOT NULL,
    room_id         INT         NOT NULL,
    user_id         INT         NOT NULL,             -- staff who created it
    check_in        DATE        NOT NULL,
    check_out       DATE        NOT NULL,
    nights          INT         GENERATED ALWAYS AS
                                (DATEDIFF(check_out, check_in)) STORED,
    total_price     DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    notes           TEXT        NULL,
    status          ENUM('CONFIRMED','CHECKED_IN','CHECKED_OUT','CANCELLED')
                                NOT NULL DEFAULT 'CONFIRMED',
    created_at      DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP
                                ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (reservation_id),
    FOREIGN KEY (guest_id)  REFERENCES guests(guest_id),
    FOREIGN KEY (room_id)   REFERENCES rooms(room_id),
    FOREIGN KEY (user_id)   REFERENCES users(user_id)
) ENGINE=InnoDB;

-- -------------------------------------------------------------
-- 7. RESERVATION SERVICES  (services booked per reservation)
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reservation_services (
    res_service_id  INT         NOT NULL AUTO_INCREMENT,
    reservation_id  INT         NOT NULL,
    service_id      INT         NOT NULL,
    quantity        INT         NOT NULL DEFAULT 1,
    unit_price      DECIMAL(10,2) NOT NULL,
    discount        DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    tax             DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    total           DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    scheduled_at    DATETIME    NULL,
    duration        INT         NOT NULL DEFAULT 0,  -- in minutes
    status          ENUM('PENDING','COMPLETED','CANCELLED')
                                NOT NULL DEFAULT 'PENDING',
    PRIMARY KEY (res_service_id),
    FOREIGN KEY (reservation_id) REFERENCES reservations(reservation_id)
        ON DELETE CASCADE,
    FOREIGN KEY (service_id)     REFERENCES services(service_id)
) ENGINE=InnoDB;

-- -------------------------------------------------------------
-- 8. RECEIPTS
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS receipts (
    receipt_id      INT         NOT NULL AUTO_INCREMENT,
    reservation_id  INT         NOT NULL UNIQUE,
    receipt_number  VARCHAR(20) NOT NULL UNIQUE,
    subtotal        DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    tax             DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    total           DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    issued_at       DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (receipt_id),
    FOREIGN KEY (reservation_id) REFERENCES reservations(reservation_id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- =============================================================
--  SEED DATA — default admin account
--  Password: Admin@123  (bcrypt hash — change after first login)
-- =============================================================
INSERT IGNORE INTO users
    (first_name, last_name, email, phone, password, role)
VALUES
    ('Super', 'Admin',
     'admin@hotelms.com',
     '09000000000',
     '$2b$12$KIX1x3z1z1z1z1z1z1z1zuQwP5jHkHkHkHkHkHkHkHkHkHkHkHkHu',
     'Admin');