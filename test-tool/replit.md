# Overview

**登分小工具 (Score Entry Tool)** - A Streamlit-based web application for managing student scores. The application provides a simple interface for teachers to quickly enter and manage scores for a predefined set of student seat numbers. Data is persisted to a JSON file (`numbers_dict.json`) for session continuity.

## Purpose
This tool is designed for teachers to efficiently record student scores by entering combined seat number and score values (e.g., "1025" means seat 10, score 25).

## Recent Changes
- **November 22, 2025**: Deployed to Streamlit Community Cloud
  - Modified authentication to support both Replit and Streamlit Cloud environments
  - Added support for Google service account authentication (JSON key files)
  - Created detailed setup guide (SETUP_GUIDE.md) for Streamlit Cloud users
  - Added quick reference guide in the upload dialog
  - Fixed configuration for Streamlit Cloud compatibility
  - Supports two access methods for Google Sheets (by ID or by name)
  
- **November 22, 2025**: Google Sheets integration
  - Integrated Google Sheets API for cloud storage
  - Added upload functionality to save scores to Google Sheets
  - Users can now upload current scores with custom column titles
  - Automatic spreadsheet creation and column management
  - Supports unlimited columns (properly handles AA, AB, etc. beyond column Z)
  
- **November 22, 2025**: Initially configured for Replit environment
  - Installed Python 3.11 and all dependencies via uv
  - Configured Streamlit to run on port 5000 with 0.0.0.0 binding
  - Set up deployment configuration for autoscale deployment
  - Created .streamlit/config.toml for proper Replit proxy handling

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture

**Framework**: Streamlit
- Single-page web application built with Streamlit
- Uses Streamlit's session state for managing application state between reruns
- Main application logic resides in `app.py`

**State Management**:
- Session state (`st.session_state`) stores the numbers dictionary and startup messages
- Dictionary is initialized on first load and persists throughout the session
- Auto-clear mechanism resets all values to `None` on application startup

## Data Storage

**File-Based Persistence**:
- Uses local JSON file (`numbers_dict.json`) for data persistence
- No database required - simple file I/O operations
- Data structure: Dictionary with integer keys (stored as strings in JSON) mapping to integer values or `None`

**Data Model**:
- Fixed set of 54 valid keys (non-sequential integers between 1-64)
- Values can be integers or `None`
- JSON serialization handles conversion between integer keys and string keys for storage

## Application Logic

**Initialization Strategy**:
- Application automatically clears all stored values on startup
- Ensures clean state for each new session
- All valid keys are initialized to `None` by default

**Key Constraints**:
- Only predefined keys from `VALID_KEYS` list are allowed
- Keys are: 1, 2, 5, 8, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 23, 24, 25, 26, 27, 28, 30, 31, 32, 33, 34, 35, 36, 37, 38, 40, 41, 42, 43, 44, 45, 46, 47, 49, 50, 51, 52, 53, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64
- Missing keys from 1-64 sequence: 3, 4, 6, 7, 9, 16, 21, 22, 29, 39, 48, 54

**Error Handling**:
- Try-except blocks protect file operations
- Graceful fallback to empty/initialized dictionary on load failures
- Boolean return values indicate success/failure of save operations

# External Dependencies

## Python Libraries

**Streamlit**: Web application framework
- Primary UI framework for the application
- Provides session state management and interactive widgets

**gspread**: Google Sheets API client
- Authenticates and interacts with Google Sheets API
- Creates and updates spreadsheets programmatically
- Used for cloud-based score storage

**google-auth**: Google authentication libraries
- `google.oauth2.credentials`: Manages OAuth2 credentials for Google API access
- `google.oauth2.service_account`: Handles service account authentication for Streamlit Cloud
- `google.auth.transport.requests`: Handles OAuth2 token refresh
- Used for both Replit connector and Streamlit Cloud service account authentication

**google-auth-oauthlib**: OAuth2 library for Google APIs
- Supports service account authentication flows

**google-auth-httplib2**: HTTP transport for Google authentication
- Provides HTTP client integration with Google auth

**requests**: HTTP client library
- Used to fetch Google Sheets access tokens from Replit's connector API (when on Replit)
- Handles authentication with Replit services

**Standard Library**:
- `json`: JSON serialization/deserialization for file persistence
- `os`: File system operations and environment variable access

## File System

**Local Storage**:
- `numbers_dict.json`: Primary data storage file
- UTF-8 encoding for file operations
- No external database or cloud storage dependencies