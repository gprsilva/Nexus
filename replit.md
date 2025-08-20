# Overview

Nexus is a professional social network designed specifically for developers to showcase their projects, share knowledge, and build connections. The platform functions as a developer-focused portfolio and networking site where users can publish projects, interact through likes and comments, follow other developers, and receive notifications about their network activity.

The system provides both public browsing capabilities for visitors and comprehensive user management features for registered developers, including project creation with rich media support, social interactions, and professional profile management.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Template Engine**: Jinja2 templating with Flask for server-side rendering
- **CSS Framework**: Bootstrap 5 for responsive design and component styling
- **JavaScript**: Vanilla JavaScript for interactive features including AJAX-powered like functionality, image previews, and form validation
- **Responsive Design**: Mobile-first approach with professional dark theme using CSS custom properties
- **File Organization**: Modular template structure with base template inheritance and component-based CSS

## Backend Architecture
- **Web Framework**: Flask with blueprints pattern for route organization
- **Database ORM**: SQLAlchemy with declarative base for database operations
- **Authentication**: Flask-Login for session management with user authentication
- **Form Handling**: WTForms with Flask-WTF for form validation and CSRF protection
- **File Management**: Custom utility functions for image processing and file uploads with PIL
- **Security**: Password hashing with Werkzeug, session management, and CSRF token validation

## Data Storage Solutions
- **Primary Database**: SQLAlchemy ORM with support for multiple database backends (configured via DATABASE_URL environment variable)
- **File Storage**: Local file system storage in uploads directory with organized folder structure
- **Session Storage**: Flask session management with configurable session secrets
- **Database Features**: Connection pooling, automatic reconnection, and optimized query handling

## Authentication and Authorization
- **User Management**: Flask-Login integration with user loader functions
- **Password Security**: Werkzeug password hashing with salt
- **Session Handling**: Remember me functionality and secure session configuration
- **Access Control**: Login required decorators for protected routes
- **Profile Management**: Comprehensive user profile system with social media integration

## External Dependencies
- **Image Processing**: PIL (Pillow) for image resizing and optimization
- **Email Validation**: WTForms email validators for user registration
- **File Upload**: Flask file upload handling with size limits and type validation
- **Proxy Support**: ProxyFix middleware for deployment behind reverse proxies
- **Frontend Libraries**: Bootstrap 5 CDN, Font Awesome icons, and custom CSS framework

The application follows a traditional MVC pattern with clear separation between models (SQLAlchemy), views (Jinja2 templates), and controllers (Flask routes). The notification system enables real-time user engagement tracking, while the social features (follow/unfollow, likes, comments) create a comprehensive developer networking experience.