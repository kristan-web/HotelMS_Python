Hotel Management System: Project Inventory and Architectural Context
I. Complete File Inventory
The Hotel Management System comprises twenty-seven Python files organized into distinct functional modules. Below is the comprehensive list of all existing views and utilities:

Core Application Views
Mainframe.py – The main application container with tabbed navigation for Reservations, Guests, Services, and Rooms.

ReservationPanel.py – Manages room bookings with date selection, guest assignment, and availability checking.

GuestPanel.py – Handles guest management interface with search, add, edit, and delete operations.

ServicesPanel.py – Manages service bookings and displays service history.

RoomPanel.py – Controls room inventory with add, delete, and status update capabilities.

ReceiptView.py – Generates and displays transaction receipts with itemized breakdowns.

DatePicker.py – A reusable calendar dialog for date selection across the application.

AdminLogsView.py – Displays audit logs with filtering by action type and affected tables.

Service Management Module
ServiceView.py – Main service management interface with add, edit, delete, and view deleted services.

AddServiceView.py – Modal dialog for creating new services.

EditServiceView.py – Modal dialog for modifying existing service details.

DeletedServicesView.py – Displays soft-deleted services with restore functionality.

Guest Management Module
GuestView.py – Main guest management interface with CRUD operations and search.

AddGuestView.py – Modal dialog for registering new guests.

EditGuestView.py – Modal dialog for updating guest information.

DeletedGuestView.py – Displays soft-deleted guests with restore functionality.

Account Management Module
StaffAndAdminAccountView.py – Main user management interface for Admins and Staff accounts.

EditUserView.py – Modal dialog for editing user details and roles.

DeletedUserView.py – Displays deleted user accounts with restore functionality.

AdminRegistrationView.py – Registration form for creating new admin accounts.

StaffRegistrationView.py – Registration form for creating new staff accounts.

AdminLoginView.py – Authentication interface for admin users.

StaffLoginView.py – Authentication interface for staff users.

ForgotPasswordView.py – Initiates password recovery via email.

EnterOTPview.py – Verifies one-time password for password reset.

NewPasswordView.py – Sets a new password after OTP verification.

II. Project Context and Scope
The Hotel Management System is a comprehensive desktop application developed using PyQt6 for the graphical user interface and MySQL for data persistence. The system is designed to streamline hotel operations by providing integrated modules for managing reservations, guest information, room inventory, service bookings, and user accounts. The application supports two distinct user roles: Administrators, who have full system access including user management and audit logs, and Staff members, who can manage daily operations such as reservations and guest check-ins.

The architecture follows the Model-View-Controller (MVC) pattern to ensure separation of concerns, maintainability, and scalability. Currently, the View layer is fully implemented across all twenty-seven files. Each view is designed as a pure UI component that contains no business logic, exposes getter methods for retrieving form data, emits signals for user actions, and provides methods for loading data into tables. This design positions the system for seamless integration with the Model and Controller layers.

The application's core functionality revolves around five primary entities: Guests, who can be registered and assigned to reservations; Rooms, which have types, capacities, and availability statuses; Services, which are offered to guests during their stay; Reservations, which link guests to rooms with check-in and check-out dates; and Users, who authenticate with role-based permissions. The system also includes an audit logging mechanism that records all create, update, and delete operations for accountability and security.

III. MVC Architecture Implementation Strategy
The Model layer will consist of classes that encapsulate database operations for each entity. Each model will inherit from a BaseModel that provides common CRUD functionality using a shared MySQL connection pool. The models will handle data validation, soft deletion (marking records as deleted rather than physically removing them), and audit logging. Key models include ServiceModel, GuestModel, UserModel, RoomModel, ReservationModel, and AuditLogModel.

The Controller layer will serve as the intermediary between views and models. Each controller will instantiate its corresponding view and model, connect view signals to controller methods, and execute model operations based on user actions. For example, the ServiceController will connect ServiceView's add_requested signal to a method that validates input, calls ServiceModel.create(), and refreshes the table. Controllers will also handle navigation between views and manage the main application flow.

The integration between existing views and the MVC structure requires several modifications. Views that currently use hasattr(self, 'add_requested') checks must define explicit pyqtSignal instances. Dialog views such as AddGuestView and EditGuestView need their Save and Update buttons connected to the accept() method. Registration views require signals to communicate success back to parent controllers. All view navigation methods must be refactored to delegate to controllers rather than directly instantiating new views.

Hotel Management System/
│
├── main.py
├── test_db.py
├── readme.txt
├── database.sql
│
├── config/
│   ├── __init__.py
│   └── database.py
│
├── models/
│   ├── __init__.py
│   ├── base_model.py
│   └── service_model.py
│
├── controllers/
│   ├── __init__.py
│   └── service_controller.py
│
├── views/
│   ├── Receipt/
│   │   └── ReceiptView.py
│   │
│   ├── Dashboard/
│   │   ├── AdminDashboardView.py
│   │   └── StaffDashboardView.py
│   │
│   ├── AccountManagement/
│   │   ├── AccountCreation/
│   │   │   ├── AdminLoginView.py
│   │   │   ├── AdminRegistrationView.py
│   │   │   ├── ForgotPasswordView.py
│   │   │   ├── StaffLoginView.py
│   │   │   └── StaffRegistrationView.py
│   │   │
│   │   └── AccountAdministration/
│   │       ├── EditUserView.py
│   │       ├── StaffAndAdminAccountView.py
│   │       ├── DeletedUserView.py
│   │       └── AdminLogsView.py
│   │
│   ├── GuestManagement/
│   │   ├── GuestView.py
│   │   ├── AddGuestView.py
│   │   ├── EditGuestView.py
│   │   └── DeletedGuestView.py
│   │
│   ├── ReservationManagement/
│   │   ├── Mainframe.py
│   │   ├── ReservationPanel.py
│   │   ├── GuestPanel.py
│   │   ├── RoomPanel.py
│   │   ├── ServicesPanel.py
│   │   └── DatePicker.py
│   │
│   └── ServiceManagement/
│       ├── ServiceView.py
│       ├── AddServiceView.py
│       ├── EditServiceView.py
│       └── DeletedServicesView.py
│
└── resources/
    ├── admin_logo.jpg
    ├── reserved.png
    ├── check.png
    ├── money.png
    ├── briefcase.png
    ├── calendar.png
    ├── amenities.png
    ├── services.png
    ├── account-management.png
    └── performance-review.png