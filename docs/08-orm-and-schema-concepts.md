# ORM and Schema Concepts

## ORM

ORM stands for:
Object Relational Mapping

Purpose:
- map Python objects to relational database tables
- abstract raw SQL interactions
- provide application-level database modeling

Current ORM framework:
- SQLAlchemy

---

## Database Models

Current model:
- Asset

Purpose:
- define relational table structure
- define columns/types/constraints
- contribute to overall database schema

Example concepts:
- hostname
- owner
- status
- primary keys
- indexes

---

## Database Schema

Schema represents:
- overall relational data structure
- table definitions
- column types
- constraints
- relationships

Current schema includes:
- assets table

Schema generated through:
Base.metadata.create_all(bind=engine)

---

## API Schemas

API schemas are separate from database models.

Current framework:
- Pydantic

Purpose:
- validate incoming API requests
- structure API responses
- enforce data consistency

---

## Current Application Data Flow

Client JSON
    ↓
Pydantic schema validation
    ↓
FastAPI route
    ↓
SQLAlchemy ORM
    ↓
PostgreSQL relational storage