-- ====================================================================
-- MSME Credit Improvement Coach — Production Database Schema
-- Target: MySQL Server 8.0+
-- ====================================================================

CREATE DATABASE IF NOT EXISTS msme_credit_coach
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE msme_credit_coach;

-- 1. USERS TABLE
CREATE TABLE IF NOT EXISTS users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    owner_id VARCHAR(64) NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    business_name VARCHAR(150) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(120) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    target_rank TINYINT UNSIGNED DEFAULT 3,
    industry_category ENUM('low', 'medium', 'high') DEFAULT 'medium',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_users_phone UNIQUE (phone),
    CONSTRAINT uq_users_email UNIQUE (email),
    INDEX idx_users_owner_id (owner_id),
    INDEX idx_users_phone (phone),
    INDEX idx_users_email (email)
) ENGINE=InnoDB;

-- 2. BUSINESS CREDIT PROFILES TABLE
CREATE TABLE IF NOT EXISTS business_credit_profiles (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    owner_id VARCHAR(64) NOT NULL UNIQUE,
    on_time_payment_pct DECIMAL(5,4) DEFAULT NULL,
    has_recent_delinquency BOOLEAN DEFAULT NULL,
    credit_utilization DECIMAL(5,4) DEFAULT NULL,
    credit_tenure_years DECIMAL(5,2) DEFAULT NULL,
    business_age_years DECIMAL(5,2) DEFAULT NULL,
    industry_risk_category ENUM('low', 'medium', 'high') DEFAULT 'medium',
    estimated_cmr_rank TINYINT UNSIGNED DEFAULT NULL,
    overall_proxy_score DECIMAL(4,1) DEFAULT NULL,
    source ENUM('cibil_pdf', 'manual_sandbox', 'unranked') DEFAULT 'unranked',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_profiles_owner FOREIGN KEY (owner_id) 
        REFERENCES users(owner_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 3. CIBIL CIR REPORTS TABLE
CREATE TABLE IF NOT EXISTS cibil_cir_reports (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    owner_id VARCHAR(64) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    rcn VARCHAR(64) DEFAULT NULL,
    company_name VARCHAR(200) DEFAULT NULL,
    pan VARCHAR(20) DEFAULT NULL,
    gstin VARCHAR(30) DEFAULT NULL,
    cmr_rank TINYINT UNSIGNED NOT NULL,
    total_sanctioned DECIMAL(14,2) DEFAULT 0.00,
    total_balance DECIMAL(14,2) DEFAULT 0.00,
    total_overdue DECIMAL(14,2) DEFAULT 0.00,
    extracted_payload JSON DEFAULT NULL,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_reports_owner FOREIGN KEY (owner_id) 
        REFERENCES users(owner_id) ON DELETE CASCADE,
    INDEX idx_reports_owner (owner_id),
    INDEX idx_reports_rcn (rcn)
) ENGINE=InnoDB;

-- 4. LOGGED ACTIONS TABLE
CREATE TABLE IF NOT EXISTS logged_actions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    owner_id VARCHAR(64) NOT NULL,
    factor ENUM('payment_history', 'credit_utilization', 'credit_tenure', 'firm_profile') NOT NULL,
    description TEXT NOT NULL,
    logged_at DATETIME NOT NULL,
    CONSTRAINT fk_actions_owner FOREIGN KEY (owner_id) 
        REFERENCES users(owner_id) ON DELETE CASCADE,
    INDEX idx_actions_owner_time (owner_id, logged_at)
) ENGINE=InnoDB;

-- 5. ALTERNATE DATA SIGNALS TABLE
CREATE TABLE IF NOT EXISTS alternate_data_signals (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    owner_id VARCHAR(64) NOT NULL UNIQUE,
    gst_filing_regularity DECIMAL(4,3) DEFAULT 0.800,
    upi_inflow_stability DECIMAL(4,3) DEFAULT 0.800,
    signal_tier VARCHAR(50) DEFAULT 'Moderate Cash-Flow Stability',
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_signals_owner FOREIGN KEY (owner_id) 
        REFERENCES users(owner_id) ON DELETE CASCADE
) ENGINE=InnoDB;
