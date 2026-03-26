Hotel Management System – Project Overview and Implementation Plan
Project Context
This is a Hotel Management System built with Python using PyQt6 for the graphical user interface and MySQL for data persistence. The application follows a Model-View-Controller architecture where models handle database operations, controllers contain business logic, and views manage the user interface. The system supports two user roles: Admin, who has full system access including user management and audit logs, and Staff, who handles day-to-day operations like reservations, guest management, and check-ins. The database schema includes tables for users, guests, rooms, services, reservations, reservation services, receipts, and admin logs.

Step-by-Step Implementation Plan
Phase 1: Core Controllers
First, create GuestController in controllers/guest_controller.py. This singleton class will implement get_all_active, get_all_deleted, get_by_id, and search methods that call the corresponding GuestModel methods. For create, update, soft_delete, and restore, add validation and call AdminLogModel.log to record actions with the current user from AuthController.

Second, create RoomController in controllers/room_controller.py. Implement get_all, get_available, get_by_id, create, update, update_status, and delete. The get_available method must accept check-in and check-out dates to find rooms not booked in that range.

Third, create ReservationController in controllers/reservation_controller.py. Implement create to insert a reservation and calculate nights automatically. Implement get_all with optional status filter, get_by_id, and get_today_stats. Implement update_status to handle check-in, check-out, and cancellation. When checking out, automatically generate a receipt by calculating total from room price plus any booked services, then call ReceiptModel.create.

Fourth, create ReceiptController in controllers/receipt_controller.py. Implement generate_receipt to format receipt data for display, and get_by_reservation to retrieve receipt details including guest name, room details, and services.

Phase 2: Dashboard and User Controllers
Create DashboardController in controllers/dashboard_controller.py. Implement get_admin_stats to return total reservations count, active services count, staff user count, and total revenue from receipts. Implement get_staff_today_stats to return today’s reservations count, check-ins, check-outs, and revenue from reservations where check_out equals current date.

Create UserController in controllers/user_controller.py for account management. Implement get_all_active, get_all_deleted, get_by_id, create, update, soft_delete, and restore. Add email uniqueness validation and log all actions to admin_logs.

Phase 3: Guest Management Integration
Modify GuestView.py to connect to GuestController. In the init method, initialize self.controller = get_guest_controller(). Replace load_sample_data with load_guests that calls self.controller.get_all_active and populates the table. Connect the add button to open AddGuestView, and when the dialog accepts, call self.controller.create with the entered data then refresh the table. Connect the edit button to open EditGuestView with the selected guest’s data, call self.controller.update on accept, then refresh. Connect the delete button to call self.controller.soft_delete after confirmation. Connect the deleted button to open DeletedGuestView. In DeletedGuestView, connect restore button to call self.controller.restore.

Modify GuestPanel.py similarly to use GuestController for the form panel and table.

Phase 4: Room Management Integration
Modify RoomPanel.py to connect to RoomController. Initialize self.controller = get_room_controller(). Replace static_rooms with load_rooms that calls self.controller.get_all. For add room, validate input and call self.controller.create. For delete, call self.controller.delete after confirmation. For status update, call self.controller.update_status with the selected room. For edit, when a row is selected, populate the form and use update method.

Phase 5: Reservation Management Integration
Modify ReservationPanel.py to connect to ReservationController. Initialize self.controller = get_reservation_controller() and self.room_controller = get_room_controller() for room availability. When find available rooms is clicked, use selected dates to call self.room_controller.get_available and populate the room combo box. Load guests from GuestController.get_all_active into the guest combo box. When confirm reservation is clicked, call self.controller.create with guest_id, room_id, current user_id, dates, total price, and notes. After creation, refresh the table.

Load the reservation table by calling self.controller.get_all. Connect check-in, check-out, and cancel buttons to call self.controller.update_status. For check-out, also open ReceiptView with the receipt data.

Phase 6: Dashboard Integration
Modify AdminDashboardView.py to connect to DashboardController. In the show method or after login, call self.controller.get_admin_stats and update the stat labels with the returned values. Connect the reservation card to open MainframeView with the reservations tab selected. Connect the guest card to open GuestView. Connect the service card to open ServiceView. Connect the account management card to open StaffAndAdminAccountView. Connect the reports card to open AdminLogsView.

Modify StaffDashboardView.py similarly using get_staff_today_stats. Connect the manage reservations card to open MainframeView with reservations tab selected.

Phase 7: Account Management Integration
Modify StaffAndAdminAccountView.py to connect to UserController. Initialize self.controller = get_user_controller(). Replace sample data with load_users that calls self.controller.get_all_active. Connect the create admin and create staff buttons to open AdminRegistrationView and StaffRegistrationView respectively, which should call AuthController.register_admin and register_staff. Connect the edit button to open EditUserView and call self.controller.update. Connect the delete button to call self.controller.soft_delete. Connect the deleted button to open DeletedUserView with self.controller.get_all_deleted.

Phase 8: Admin Logs Fix
Modify AdminLogModel.py to store logs in a structured JSON format. Change the log method to accept table_name, record_id, old_values, and new_values as parameters, storing them in the description field as JSON. Alternatively, alter the database schema to add these columns. Then modify AdminLogsView.py to parse the JSON from description and display it in the table columns. The view expects keys table_name, record_id, action, changed_by, timestamp, old_values, new_values. Either adjust the model to return this structure or adjust the view to match what the model returns.

Phase 9: Mainframe Navigation Integration
Modify Mainframe.py to accept user_role and user_id parameters. When the back button is clicked, navigate to the appropriate dashboard based on role. Ensure the tabs are loaded with the correct panels that are already integrated with their controllers. Pass the main_window reference to each panel so they can navigate back correctly.

Phase 10: Testing and Validation
Test each module sequentially starting from Phase 1. Verify that guest CRUD operations work and logs are created. Verify room management creates, updates, and deletes rooms correctly. Verify reservations can be created, checked in, checked out, and cancelled, and that receipts generate on check-out. Verify dashboard stats match the database. Verify user account management works for both admin and staff. Verify admin logs display correctly with proper formatting.

