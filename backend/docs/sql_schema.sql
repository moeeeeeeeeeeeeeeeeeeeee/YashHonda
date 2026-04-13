CREATE TABLE roles (
    id UUID PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE users (
    id UUID PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    mobile VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_roles (
    user_id UUID NOT NULL REFERENCES users(id),
    role_id UUID NOT NULL REFERENCES roles(id),
    PRIMARY KEY (user_id, role_id)
);

CREATE TABLE company_profile (
    id UUID PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(120) NOT NULL,
    address TEXT NOT NULL,
    bank_name VARCHAR(120) NOT NULL,
    account_number VARCHAR(64) NOT NULL,
    upi_id VARCHAR(120) NOT NULL,
    qr_code_ref TEXT NOT NULL,
    gst_number VARCHAR(32) NOT NULL
);

CREATE TABLE vehicle_groups (
    id UUID PRIMARY KEY,
    code VARCHAR(30) UNIQUE NOT NULL,
    display_name VARCHAR(80) NOT NULL
);

CREATE TABLE vehicle_models (
    id UUID PRIMARY KEY,
    group_id UUID NOT NULL REFERENCES vehicle_groups(id),
    model_code VARCHAR(60) UNIQUE NOT NULL,
    display_name VARCHAR(120) NOT NULL,
    effective_from DATE NOT NULL,
    effective_to DATE
);

CREATE TABLE vehicle_variants (
    id UUID PRIMARY KEY,
    model_id UUID NOT NULL REFERENCES vehicle_models(id),
    variant_code VARCHAR(60) UNIQUE NOT NULL,
    display_name VARCHAR(120) NOT NULL,
    ex_showroom NUMERIC(12, 2) NOT NULL,
    rto NUMERIC(12, 2) NOT NULL,
    insurance NUMERIC(12, 2) NOT NULL,
    standard_charges NUMERIC(12, 2) NOT NULL,
    pdi NUMERIC(12, 2) NOT NULL DEFAULT 0,
    extended_warranty NUMERIC(12, 2) NOT NULL DEFAULT 0,
    rsa NUMERIC(12, 2) NOT NULL DEFAULT 0,
    optional_accessories NUMERIC(12, 2) NOT NULL DEFAULT 0,
    helmet NUMERIC(12, 2) NOT NULL DEFAULT 0,
    ceramic NUMERIC(12, 2) NOT NULL DEFAULT 0,
    effective_from DATE NOT NULL,
    effective_to DATE
);

CREATE TABLE colors (
    id UUID PRIMARY KEY,
    code VARCHAR(30) UNIQUE NOT NULL,
    color_name VARCHAR(80) NOT NULL
);

CREATE TABLE model_colors (
    variant_id UUID NOT NULL REFERENCES vehicle_variants(id),
    color_id UUID NOT NULL REFERENCES colors(id),
    PRIMARY KEY (variant_id, color_id)
);

CREATE TABLE finance_providers (
    id UUID PRIMARY KEY,
    code VARCHAR(30) UNIQUE NOT NULL,
    name VARCHAR(120) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE finance_plans (
    id UUID PRIMARY KEY,
    variant_id UUID NOT NULL REFERENCES vehicle_variants(id),
    provider_id UUID NOT NULL REFERENCES finance_providers(id),
    down_payment NUMERIC(12, 2) NOT NULL,
    emi_24 NUMERIC(12, 2) NOT NULL,
    emi_36 NUMERIC(12, 2) NOT NULL,
    emi_48 NUMERIC(12, 2) NOT NULL,
    effective_from DATE NOT NULL,
    effective_to DATE
);

CREATE TABLE sales_executives (
    id UUID PRIMARY KEY,
    employee_code VARCHAR(30) UNIQUE NOT NULL,
    full_name VARCHAR(120) NOT NULL,
    mobile VARCHAR(20),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE areas (
    id UUID PRIMARY KEY,
    code VARCHAR(30) UNIQUE NOT NULL,
    area_name VARCHAR(120) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE purchase_modes (
    id UUID PRIMARY KEY,
    code VARCHAR(30) UNIQUE NOT NULL,
    description VARCHAR(80) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE customers (
    id UUID PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    mobile VARCHAR(20) NOT NULL,
    email VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE inquiries (
    id UUID PRIMARY KEY,
    customer_id UUID NOT NULL REFERENCES customers(id),
    source VARCHAR(80) NOT NULL,
    area_id UUID REFERENCES areas(id),
    vehicle_type VARCHAR(60) NOT NULL,
    variant_id UUID NOT NULL REFERENCES vehicle_variants(id),
    color_id UUID REFERENCES colors(id),
    purchase_mode_id UUID REFERENCES purchase_modes(id),
    finance_provider_id UUID REFERENCES finance_providers(id),
    exchange_flag BOOLEAN NOT NULL DEFAULT FALSE,
    old_vehicle TEXT,
    kms INTEGER,
    owner_count VARCHAR(30),
    sales_executive_id UUID REFERENCES sales_executives(id),
    buying_when VARCHAR(80),
    status VARCHAR(30) NOT NULL,
    remarks TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE quotes (
    id UUID PRIMARY KEY,
    inquiry_id UUID NOT NULL REFERENCES inquiries(id),
    quote_number VARCHAR(40) UNIQUE NOT NULL,
    status VARCHAR(30) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'INR',
    subtotal NUMERIC(12, 2) NOT NULL,
    grand_total NUMERIC(12, 2) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE quote_line_items (
    id UUID PRIMARY KEY,
    quote_id UUID NOT NULL REFERENCES quotes(id),
    line_code VARCHAR(60) NOT NULL,
    description VARCHAR(120) NOT NULL,
    charge_type VARCHAR(30) NOT NULL,
    amount NUMERIC(12, 2) NOT NULL
);

CREATE TABLE quote_documents (
    id UUID PRIMARY KEY,
    quote_id UUID NOT NULL REFERENCES quotes(id),
    storage_key TEXT NOT NULL,
    checksum VARCHAR(128),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY,
    entity_type VARCHAR(60) NOT NULL,
    entity_id UUID NOT NULL,
    action VARCHAR(60) NOT NULL,
    actor VARCHAR(120) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_inquiries_status_created_at ON inquiries (status, created_at);
CREATE INDEX idx_quotes_inquiry_id ON quotes (inquiry_id);
CREATE INDEX idx_quote_line_items_quote_id ON quote_line_items (quote_id);
