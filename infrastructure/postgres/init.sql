-- PostgreSQL initialization script
-- Runs once when the Docker volume is first created.
-- Creates the test database alongside the main database.

-- Create the test database for pytest
CREATE DATABASE eauction_test
    WITH OWNER eauction
    ENCODING 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    TEMPLATE template0;

-- Grant all privileges on test DB to the application user
GRANT ALL PRIVILEGES ON DATABASE eauction_test TO eauction;

-- Enable UUID extension on main database
\connect eauction_db
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable UUID extension on test database
\connect eauction_test
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
