Hotel Management System — Project Context & Implementation Roadmap
Project Context
You are developing a comprehensive Hotel Management System with a MySQL backend and a PyQt6 graphical user interface. The system is designed to streamline hotel operations by managing guests, rooms, reservations, services, user accounts, and financial transactions.

System Architecture
The application follows a three-tier architecture:

Database Layer (MySQL) — Complete schema with tables for users, guests, rooms, services, reservations, reservation_services, receipts, and admin_logs. The schema includes soft-delete functionality, generated columns (nights), and proper foreign key constraints.

Model Layer (Python) — Data access objects in the models/ directory. Each model (UserModel, GuestModel, RoomModel, ServiceModel, ReservationModel, ReceiptModel, AdminLogModel) provides CRUD operations with error handling and database connection management via a singleton pattern.

View Layer (PyQt6) — A complete set of GUI views organized by module:

Authentication (AdminLoginView, StaffLoginView, ForgotPasswordView, EnterOTPView, NewPasswordView)

Registration (AdminRegistrationView, StaffRegistrationView)

Account Management (StaffAndAdminAccountView, DeletedUserView, EditUserView)

Guest Management (GuestView, GuestPanelView, AddGuestView, EditGuestView, DeletedGuestView)

Room Management (RoomPanel)

Service Management (ServiceView, AddServiceView, EditServiceView, DeletedServicesView, ServicesPanel)

Reservation Management (ReservationPanel, ReceiptView, DatePicker)

Dashboard (AdminDashboardView, StaffDashboardView)

Navigation (Mainframe with tabbed interface)

Audit (AdminLogsView)

Controller Layer (To be completed) — Currently only AuthController exists. The remaining controllers (UserController, GuestController, RoomController, ServiceController, ReservationController, ReceiptController) need to be created to bridge views with models.

Current State
Database schema — Complete and ready

Models — Fully implemented with all CRUD operations

Views — All GUI screens are built with consistent styling

Controllers — Only authentication controller exists

Integration — Views currently use static/demo data; no database connections

Technology Stack
Python 3.x with PyQt6 for GUI

MySQL with mysql-connector-python

bcrypt for password hashing

SMTP for OTP email delivery

Singleton pattern for database connection management



Step-by-Step Implementation Process
Phase 1: Foundation Setup
Step 1 — Database Initialization

Execute schema.sql to create the database and all tables

Verify the default admin account (admin@hotelms.com / Admin@123) is inserted

Test database connection using utils/db_connection.py

Step 2 — Environment Configuration

Set up SMTP credentials in utils/otp_utils.py for password reset functionality

Configure database credentials in config/db_config.py

Create a .env file for sensitive information (optional but recommended)

Step 3 — Core Utilities Testing

Test password_utils.py with hash and verify functions

Test otp_utils.py OTP generation (without actual email sending initially)

Verify db_connection.py connects and reconnects properly

Phase 2: Authentication Layer Completion
Step 4 — Complete Admin Login Integration

Modify AdminLoginView.py to call AuthController.login_admin()

Add proper error handling for invalid credentials

After successful login, retrieve user data and pass to AdminDashboardView

Store current user in AuthController singleton for session management

Step 5 — Complete Staff Login Integration

Connect StaffLoginView.py to AuthController.login_staff()

Route to StaffDashboardView on success

Ensure role-based access control is enforced

Step 6 — Complete Password Reset Flow

Connect ForgotPasswordView to AuthController.request_password_reset()

Connect EnterOTPView to AuthController.verify_otp()

Connect NewPasswordView to AuthController.reset_password()

Test the full flow with actual email sending

Add validation for OTP expiration and retry limits

Step 7 — Registration Integration

Connect AdminRegistrationView to AuthController.register_admin()

Connect StaffRegistrationView to AuthController.register_staff()

Add validation for duplicate emails and password strength

Show appropriate success/error messages

Phase 3: User Management (Staff & Admin Accounts)
Step 8 — Load Users in StaffAndAdminAccountView

Create UserController with methods: get_all_active(), get_by_id(), update(), soft_delete(), restore()

Connect StaffAndAdminAccountView to UserController.get_all_active()

Populate table with real user data from database

Step 9 — Edit User Functionality

Connect EditUserView to UserController.update()

Load existing data into edit form

Validate email uniqueness before updating

Show success/failure messages

Step 10 — Delete and Restore Users

Connect Delete button to UserController.soft_delete()

Connect DeletedUserView to UserController.get_all_deleted()

Connect Restore button to UserController.restore()

Add confirmation dialogs before destructive actions

Step 11 — Audit Logging for User Actions

Implement AdminLogModel.log() calls for create, update, delete, restore operations

Log user_id of the acting admin, action type, and relevant details

Phase 4: Guest Management
Step 12 — Create GuestController

Implement methods: get_all_active(), get_all_deleted(), create(), update(), soft_delete(), restore(), search()

Add validation for required fields and unique email

Step 13 — Connect GuestView

Load active guests into table on view initialization

Connect Add button to open AddGuestView and call controller

Connect Edit button to open EditGuestView and update

Connect Delete button to soft delete with confirmation

Implement search functionality filtering

Step 14 — Connect DeletedGuestView

Load deleted guests on view initialization

Connect Restore button to controller.restore()

Refresh both active and deleted views after operations

Step 15 — Add Audit Logging for Guest Operations

Log all create, update, delete, restore actions with old and new values (JSON format)

Phase 5: Room Management
Step 16 — Create RoomController

Implement methods: get_all(), get_by_id(), create(), update(), update_status(), delete(), get_available(check_in, check_out)

Add validation for room number uniqueness

Step 17 — Connect RoomPanel

Replace static self.static_rooms with RoomController.get_all()

Connect Add Room button to controller.create()

Connect Delete button to controller.delete()

Connect Set Status button to controller.update_status()

Connect Clear Form button to reset form fields

Step 18 — Add Room Availability Search

Ensure RoomController.get_available() correctly filters rooms not booked in date range

Test with overlapping reservation scenarios

Phase 6: Service Management
Step 19 — Create ServiceController

Implement methods: get_all_active(), get_all_deleted(), create(), update(), soft_delete(), restore()

Add validation for price (positive) and duration (positive integer)

Step 20 — Connect ServiceView

Load active services into table

Connect Add button to AddServiceView and controller.create()

Connect Edit button to EditServiceView and controller.update()

Connect Delete button to controller.soft_delete()

Implement search functionality

Step 21 — Connect DeletedServicesView

Load deleted services

Connect Restore button to controller.restore()

Update both views after operations

Step 22 — Connect ServicesPanel (Booking)

Load services into dropdown from controller.get_all_active()

Calculate total price based on selected service and duration

Connect Book button to create reservation service entry

Phase 7: Reservation Management (Core Feature)
Step 23 — Create ReservationController

Implement methods: create(), get_all(), get_by_id(), update_status(), add_service(), get_services()

Add night calculation and total price computation

Implement date validation (check_out > check_in)

Step 24 — Load Dropdowns in ReservationPanel

Populate guest dropdown from GuestController.get_all_active()

Load rooms only after date selection (Find Available Rooms button)

Step 25 — Implement Room Availability Search

Connect Find Available Rooms button to RoomController.get_available(check_in, check_out)

Validate that both dates are selected

Populate room dropdown with available rooms and display prices

Step 26 — Create New Reservation

Get selected guest, room, dates, notes

Calculate nights and total price

Call ReservationController.create() with current user_id from session

Clear form and refresh table on success

Step 27 — Load Reservations Table

Call ReservationController.get_all() on view initialization

Add status filter functionality

Implement color-coding for different reservation statuses

Step 28 — Reservation Status Updates

Connect Check-In button to ReservationController.update_status(reservation_id, 'CHECKED_IN')

Connect Check-Out button to update status and potentially generate receipt

Connect Cancel button to update status to 'CANCELLED'

Refresh table after each operation

Phase 8: Receipt Generation
Step 29 — Create ReceiptController

Implement methods: generate_receipt(reservation_id), get_by_reservation(reservation_id), get_by_id()

Calculate subtotal (room total + service totals)

Calculate tax (e.g., 5% of subtotal)

Call ReceiptModel.create() to store receipt

Step 30 — Connect Receipt Generation

On Check-Out, generate receipt automatically

Display receipt in ReceiptView

Provide option to view receipt from reservation table

Add print functionality (optional)

Phase 9: Dashboard Statistics
Step 31 — Connect AdminDashboardView

Call ReservationModel.get_today_stats() for today's check-ins, check-outs, reservations

Call UserModel.get_all_active() for total staff count

Call ServiceModel.get_all_active() for available services count

Calculate total revenue from completed reservations

Step 32 — Connect StaffDashboardView

Display today's reservations, check-ins, check-outs, revenue

Filter for staff-accessible data only

Phase 10: Audit Logs
Step 33 — Create AdminLogController

Implement methods: get_all(), get_by_user(), log_action()

Connect AdminLogsView to controller for display

Add action and table filtering

Step 34 — Add Logging Throughout Application

Log user login/logout

Log all create, update, delete operations across all modules

Store old and new values as JSON for update operations

Phase 11: Navigation and Session Management
Step 35 — Create Main Application Entry Point

Create main.py with application initialization

Set up database connection on startup

Show appropriate login screen

Pass session user data to all subsequent views

Step 36 — Implement Logout Functionality

Connect Logout buttons to AuthController.logout()

Return to login screen on logout

Clear session data

Step 37 — Role-Based Navigation

Admin dashboard shows all management options

Staff dashboard shows only reservation, guest, and service views

Restrict access to admin-only features (user management, audit logs)

Phase 12: Testing and Refinement
Step 38 — End-to-End Testing

Test complete user flows:

Admin creates staff account

Staff creates reservation

Staff checks in guest

Staff adds services during stay

Staff checks out guest and generates receipt

Admin views audit logs

Step 39 — Error Handling

Add try-catch blocks in all controller methods

Display user-friendly error messages in views

Log database errors for debugging

Step 40 — Performance Optimization

Implement connection pooling if needed

Add pagination for large tables

Optimize database queries with proper indexes

Phase 13: Final Integration and Deployment
Step 41 — Complete All Module Connections

Ensure no view uses static/demo data

Verify all signals are properly connected

Test all CRUD operations across modules

Step 42 — Documentation

Write user manual for hotel staff

Document installation and setup process

Create API documentation for future maintenance

Step 43 — Deployment Preparation

Package application with PyInstaller for Windows

Create database backup and restore scripts

Prepare installation guide for production environment

This roadmap provides a structured, incremental approach to building the complete Hotel Management System. Each phase builds upon the previous one, allowing for continuous testing and validation. The priority is to first establish a solid foundation (authentication, database connectivity), then build out core business features (reservations, guests), followed by administrative features (user management, audit logs), and finally polish the application with dashboards and navigation.

