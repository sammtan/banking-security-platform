from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QFrame, QPushButton, QLineEdit, QComboBox,
                             QMessageBox, QSpinBox, QFileDialog, QMenu)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QColor
from core.theme_manager import ThemeManager
from core.database import DatabaseManager
from core.report_generator import ReportGenerator
from datetime import datetime

class TransactionsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.db.connect()
        
        # Pagination settings
        self.current_page = 1
        self.rows_per_page = 15
        self.total_transactions = 0
        self.all_transactions = []  # Cache all transactions for pagination
        
        self.setup_ui()
        
        # Connect to database updates
        self.db.data_updated.connect(self.refresh_transactions)
        
        # Auto-refresh timer - only for new transactions
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.add_new_transactions)
        self.refresh_timer.start(5000)  # Check for new transactions every 5 seconds
        
        # Track last transaction ID to avoid full refresh
        self.last_transaction_id = None
        
        # Load initial data
        self.refresh_transactions()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Header
        header = QLabel("Transaction Monitor")
        header.setObjectName("heading")
        layout.addWidget(header)
        
        # Filters section
        filters_frame = QFrame()
        filters_layout = QHBoxLayout(filters_frame)
        filters_layout.setContentsMargins(0, 0, 0, 0)
        
        # Search box
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search transactions...")
        self.search_input.textChanged.connect(self.filter_transactions)
        filters_layout.addWidget(self.search_input, 2)
        
        # Risk filter
        self.risk_filter = QComboBox()
        self.risk_filter.addItems(["All Risk Levels", "Low Risk", "Medium Risk", "High Risk", "Fraud Only"])
        self.risk_filter.currentTextChanged.connect(self.filter_transactions)
        filters_layout.addWidget(self.risk_filter)
        
        # Status filter
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All Status", "Completed", "Blocked", "Pending"])
        self.status_filter.currentTextChanged.connect(self.filter_transactions)
        filters_layout.addWidget(self.status_filter)
        
        # Export current page button
        self.export_page_btn = QPushButton("Export Page")
        self.export_page_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ThemeManager.COLORS['surface-variant']};
                padding: 8px 16px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {ThemeManager.COLORS['border']};
            }}
        """)
        self.export_page_btn.clicked.connect(self.show_export_page_menu)
        filters_layout.addWidget(self.export_page_btn)
        
        # Export all button
        self.export_all_btn = QPushButton("Export All")
        self.export_all_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ThemeManager.COLORS['primary']};
                padding: 8px 16px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {ThemeManager.COLORS['primary-hover']};
            }}
        """)
        self.export_all_btn.clicked.connect(self.show_export_all_menu)
        filters_layout.addWidget(self.export_all_btn)
        
        layout.addWidget(filters_frame)
        
        # Transactions table
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setShowGrid(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # Make table read-only
        self.table.verticalHeader().setDefaultSectionSize(40)  # Increased row height
        
        # Set columns
        columns = ["Time", "Transaction ID", "Amount", "Type", "Merchant", "Location", 
                  "Risk Score", "Status", "Action"]
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Time
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Amount
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Type
        header.setSectionResizeMode(4, QHeaderView.Stretch)          # Merchant
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Location
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Risk
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Status
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)  # Action
        
        layout.addWidget(self.table)
        
        # Pagination controls
        pagination_frame = QFrame()
        pagination_layout = QHBoxLayout(pagination_frame)
        pagination_layout.setContentsMargins(0, 8, 0, 0)
        
        # Summary label
        self.summary_label = QLabel("Loading transactions...")
        self.summary_label.setObjectName("caption")
        pagination_layout.addWidget(self.summary_label)
        
        pagination_layout.addStretch()
        
        # Page size selector
        page_size_label = QLabel("Rows per page:")
        page_size_label.setStyleSheet(f"color: {ThemeManager.COLORS['text-secondary']}; font-size: 12px;")
        pagination_layout.addWidget(page_size_label)
        
        self.page_size_spin = QSpinBox()
        self.page_size_spin.setRange(10, 200)
        self.page_size_spin.setSingleStep(10)
        self.page_size_spin.setValue(15)
        self.page_size_spin.valueChanged.connect(self.on_page_size_changed)
        pagination_layout.addWidget(self.page_size_spin)
        
        # Warning label for large page sizes
        self.warning_label = QLabel("⚠️ Large page sizes may cause lag")
        self.warning_label.setStyleSheet(f"color: {ThemeManager.COLORS['warning']}; font-size: 11px; margin-left: 8px;")
        self.warning_label.hide()
        pagination_layout.addWidget(self.warning_label)
        
        # Page navigation
        self.prev_btn = QPushButton("◀")
        self.prev_btn.setFixedSize(30, 30)
        self.prev_btn.clicked.connect(self.prev_page)
        self.prev_btn.setEnabled(False)
        pagination_layout.addWidget(self.prev_btn)
        
        self.page_label = QLabel("Page 1 of 1")
        self.page_label.setStyleSheet(f"color: {ThemeManager.COLORS['text-primary']}; font-size: 12px; margin: 0 8px;")
        pagination_layout.addWidget(self.page_label)
        
        self.next_btn = QPushButton("▶")
        self.next_btn.setFixedSize(30, 30)
        self.next_btn.clicked.connect(self.next_page)
        self.next_btn.setEnabled(False)
        pagination_layout.addWidget(self.next_btn)
        
        layout.addWidget(pagination_frame)
        
    def refresh_transactions(self):
        """Refresh the transactions table"""
        if not self.db.conn:
            return
            
        # Get all transactions (we'll paginate in memory)
        self.all_transactions = self.db.get_recent_transactions(10000)  # Get all available transactions
        self.total_transactions = len(self.all_transactions)
        
        # Track latest ID
        if self.all_transactions:
            self.last_transaction_id = self.all_transactions[0]['id']
            
        # Update pagination
        self.update_pagination()
        
        # Display current page
        self.display_current_page()
        
    def add_transaction_row(self, transaction):
        """Add a transaction to the table"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # Time
        timestamp = datetime.fromisoformat(str(transaction['timestamp']))
        time_item = QTableWidgetItem(timestamp.strftime("%H:%M:%S"))
        time_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 0, time_item)
        
        # Transaction ID
        id_item = QTableWidgetItem(transaction['transaction_id'])
        id_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 1, id_item)
        
        # Amount
        amount_item = QTableWidgetItem(f"${transaction['amount']:,.2f}")
        amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table.setItem(row, 2, amount_item)
        
        # Type
        type_item = QTableWidgetItem(transaction['transaction_type'].title())
        type_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 3, type_item)
        
        # Merchant
        merchant_item = QTableWidgetItem(transaction['merchant_name'])
        merchant_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table.setItem(row, 4, merchant_item)
        
        # Location
        location_item = QTableWidgetItem(transaction['location'])
        location_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table.setItem(row, 5, location_item)
        
        # Risk Score
        risk_score = transaction['risk_score']
        risk_item = QTableWidgetItem(f"{risk_score:.2f}")
        risk_item.setTextAlignment(Qt.AlignCenter)
        
        # Color code risk score
        if risk_score < 0.3:
            risk_item.setForeground(QColor(ThemeManager.COLORS['success']))
        elif risk_score < 0.7:
            risk_item.setForeground(QColor(ThemeManager.COLORS['warning']))
        else:
            risk_item.setForeground(QColor(ThemeManager.COLORS['danger']))
            
        self.table.setItem(row, 6, risk_item)
        
        # Status with emoji only
        if transaction['blocked']:
            status_emoji = "🚫"
            status_color = ThemeManager.COLORS['danger']
        elif transaction['fraud_detected']:
            status_emoji = "⚠️"
            status_color = ThemeManager.COLORS['warning']
        else:
            status_emoji = "✅"
            status_color = ThemeManager.COLORS['success']
            
        status_item = QTableWidgetItem(status_emoji)
        status_item.setTextAlignment(Qt.AlignCenter)
        status_item.setForeground(QColor(status_color))
        self.table.setItem(row, 7, status_item)
        
        # Action button
        view_btn = QPushButton("View")
        view_btn.setFixedSize(60, 24)  # Fixed size for consistent alignment
        view_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ThemeManager.COLORS['primary']};
                color: white;
                border: none;
                padding: 0px;
                border-radius: 3px;
                font-size: 11px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {ThemeManager.COLORS['primary-hover']};
            }}
        """)
        view_btn.clicked.connect(lambda: self.view_transaction_details(transaction))
        
        # Create container widget to center the button
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 2, 0, 2)
        button_layout.addWidget(view_btn)
        button_layout.setAlignment(Qt.AlignCenter)
        
        self.table.setCellWidget(row, 8, button_container)
        
    def filter_transactions(self):
        """Filter transactions based on search and filters"""
        search_text = self.search_input.text().lower()
        risk_filter = self.risk_filter.currentText()
        status_filter = self.status_filter.currentText()
        
        for row in range(self.table.rowCount()):
            show_row = True
            
            # Search filter
            if search_text:
                found = False
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item and search_text in item.text().lower():
                        found = True
                        break
                if not found:
                    show_row = False
                    
            # Risk filter
            if show_row and risk_filter != "All Risk Levels":
                risk_item = self.table.item(row, 6)
                if risk_item:
                    risk_score = float(risk_item.text())
                    if risk_filter == "Low Risk" and risk_score >= 0.3:
                        show_row = False
                    elif risk_filter == "Medium Risk" and (risk_score < 0.3 or risk_score >= 0.7):
                        show_row = False
                    elif risk_filter == "High Risk" and risk_score < 0.7:
                        show_row = False
                    elif risk_filter == "Fraud Only":
                        status_item = self.table.item(row, 7)
                        if status_item and "blocked" not in status_item.text().lower():
                            show_row = False
                            
            # Status filter
            if show_row and status_filter != "All Status":
                status_item = self.table.item(row, 7)
                if status_item and status_filter.lower() not in status_item.text().lower():
                    show_row = False
                    
            self.table.setRowHidden(row, not show_row)
            
    def view_transaction_details(self, transaction):
        """Show transaction details in a dialog"""
        details = f"""
Transaction Details:

ID: {transaction['transaction_id']}
Time: {transaction['timestamp']}
Amount: ${transaction['amount']:,.2f}
Type: {transaction['transaction_type'].title()}
Merchant: {transaction['merchant_name']}
Category: {transaction['merchant_category'].replace('_', ' ').title()}
Location: {transaction['location']}
Account: {transaction['account_number']}

Risk Assessment:
Risk Score: {transaction['risk_score']:.3f}
Fraud Detected: {'Yes' if transaction['fraud_detected'] else 'No'}
Status: {transaction['status'].title()}
Blocked: {'Yes' if transaction['blocked'] else 'No'}
        """.strip()
        
        QMessageBox.information(self, "Transaction Details", details)
        
    def add_new_transactions(self):
        """Add only new transactions without refreshing entire table"""
        if not self.db.conn:
            return
            
        # Get only new transactions
        cursor = self.db.conn.cursor()
        cursor.row_factory = self.db.dict_factory
        
        if self.last_transaction_id:
            cursor.execute("""
                SELECT * FROM transactions 
                WHERE id > ?
                ORDER BY timestamp DESC
                LIMIT 15
            """, (self.last_transaction_id,))
        else:
            # First time - get latest ID
            cursor.execute("SELECT MAX(id) FROM transactions")
            max_id = cursor.fetchone()
            if max_id and max_id['MAX(id)']:
                self.last_transaction_id = max_id['MAX(id)']
            return
            
        new_transactions = cursor.fetchall()
        
        if new_transactions:
            # Update last transaction ID
            self.last_transaction_id = new_transactions[0]['id']
            
            # Add new rows at the top
            for transaction in reversed(new_transactions):
                self.table.insertRow(0)
                self.add_transaction_row_at(0, dict(transaction))
                
            # Remove old rows if table is too large (keep max 500 rows)
            while self.table.rowCount() > 500:
                self.table.removeRow(self.table.rowCount() - 1)
                
            # Update summary
            self.update_summary()
            
    def add_transaction_row_at(self, row, transaction):
        """Add a transaction at specific row index"""
        # Time
        timestamp = datetime.fromisoformat(str(transaction['timestamp']))
        time_item = QTableWidgetItem(timestamp.strftime("%H:%M:%S"))
        time_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 0, time_item)
        
        # Transaction ID
        id_item = QTableWidgetItem(transaction['transaction_id'])
        id_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 1, id_item)
        
        # Amount
        amount_item = QTableWidgetItem(f"${transaction['amount']:,.2f}")
        amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table.setItem(row, 2, amount_item)
        
        # Type
        type_item = QTableWidgetItem(transaction['transaction_type'].title())
        type_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 3, type_item)
        
        # Merchant
        merchant_item = QTableWidgetItem(transaction['merchant_name'])
        merchant_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table.setItem(row, 4, merchant_item)
        
        # Location
        location_item = QTableWidgetItem(transaction['location'])
        location_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table.setItem(row, 5, location_item)
        
        # Risk Score
        risk_score = transaction['risk_score']
        risk_item = QTableWidgetItem(f"{risk_score:.2f}")
        risk_item.setTextAlignment(Qt.AlignCenter)
        
        # Color code risk score
        if risk_score < 0.3:
            risk_item.setForeground(QColor(ThemeManager.COLORS['success']))
        elif risk_score < 0.7:
            risk_item.setForeground(QColor(ThemeManager.COLORS['warning']))
        else:
            risk_item.setForeground(QColor(ThemeManager.COLORS['danger']))
            
        self.table.setItem(row, 6, risk_item)
        
        # Status with emoji only
        if transaction['blocked']:
            status_emoji = "🚫"
            status_color = ThemeManager.COLORS['danger']
        elif transaction['fraud_detected']:
            status_emoji = "⚠️"
            status_color = ThemeManager.COLORS['warning']
        else:
            status_emoji = "✅"
            status_color = ThemeManager.COLORS['success']
            
        status_item = QTableWidgetItem(status_emoji)
        status_item.setTextAlignment(Qt.AlignCenter)
        status_item.setForeground(QColor(status_color))
        self.table.setItem(row, 7, status_item)
        
        # Action button
        view_btn = QPushButton("View")
        view_btn.setFixedSize(60, 24)  # Fixed size for consistent alignment
        view_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ThemeManager.COLORS['primary']};
                color: white;
                border: none;
                padding: 0px;
                border-radius: 3px;
                font-size: 11px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {ThemeManager.COLORS['primary-hover']};
            }}
        """)
        view_btn.clicked.connect(lambda: self.view_transaction_details(transaction))
        
        # Create container widget to center the button
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 2, 0, 2)
        button_layout.addWidget(view_btn)
        button_layout.setAlignment(Qt.AlignCenter)
        
        self.table.setCellWidget(row, 8, button_container)
        
    def update_summary(self):
        """Update summary label without full refresh"""
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN fraud_detected = 1 THEN 1 ELSE 0 END) as fraud,
                SUM(CASE WHEN blocked = 1 THEN 1 ELSE 0 END) as blocked
            FROM transactions
        """)
        stats = cursor.fetchone()
        
        self.summary_label.setText(
            f"Total: {stats[0]} transactions | {stats[1]} fraud detected | {stats[2]} blocked"
        )
        
    def display_current_page(self):
        """Display transactions for current page"""
        # Clear table
        self.table.setRowCount(0)
        
        # Calculate page boundaries
        start_idx = (self.current_page - 1) * self.rows_per_page
        end_idx = min(start_idx + self.rows_per_page, self.total_transactions)
        
        # Ensure we have transactions to display
        if self.all_transactions and start_idx < len(self.all_transactions):
            # Add transactions for current page
            for i in range(start_idx, min(end_idx, len(self.all_transactions))):
                self.add_transaction_row(self.all_transactions[i])
            
        # Update summary
        fraud = sum(1 for t in self.all_transactions if t.get('fraud_detected'))
        blocked = sum(1 for t in self.all_transactions if t.get('blocked'))
        
        self.summary_label.setText(
            f"Showing {start_idx + 1}-{end_idx} of {self.total_transactions} | {fraud} fraud | {blocked} blocked"
        )
        
    def update_pagination(self):
        """Update pagination controls"""
        total_pages = max(1, (self.total_transactions + self.rows_per_page - 1) // self.rows_per_page)
        
        # Update page label
        self.page_label.setText(f"Page {self.current_page} of {total_pages}")
        
        # Update button states
        self.prev_btn.setEnabled(self.current_page > 1)
        self.next_btn.setEnabled(self.current_page < total_pages)
        
    def prev_page(self):
        """Go to previous page"""
        if self.current_page > 1:
            self.current_page -= 1
            self.update_pagination()
            self.display_current_page()
            
    def next_page(self):
        """Go to next page"""
        total_pages = max(1, (self.total_transactions + self.rows_per_page - 1) // self.rows_per_page)
        if self.current_page < total_pages:
            self.current_page += 1
            self.update_pagination()
            self.display_current_page()
            
    def on_page_size_changed(self, value):
        """Handle page size change"""
        self.rows_per_page = value
        self.current_page = 1  # Reset to first page
        
        # Show warning for large page sizes
        if value >= 100:
            self.warning_label.show()
        else:
            self.warning_label.hide()
            
        self.update_pagination()
        self.display_current_page()
        
    def show_export_page_menu(self):
        """Show export format options for current page"""
        menu = self._create_export_menu()
        menu.exec_(self.export_page_btn.mapToGlobal(self.export_page_btn.rect().bottomLeft()))
        
    def show_export_all_menu(self):
        """Show export format options for all transactions"""
        menu = self._create_export_menu(export_all=True)
        menu.exec_(self.export_all_btn.mapToGlobal(self.export_all_btn.rect().bottomLeft()))
        
    def _create_export_menu(self, export_all=False):
        """Create export format menu"""
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {ThemeManager.COLORS['surface']};
                border: 1px solid {ThemeManager.COLORS['border']};
                padding: 4px;
            }}
            QMenu::item {{
                padding: 8px 24px;
                color: {ThemeManager.COLORS['text-primary']};
            }}
            QMenu::item:selected {{
                background-color: {ThemeManager.COLORS['primary']};
                color: white;
            }}
        """)
        
        # Add export options
        pdf_action = menu.addAction("Export as PDF")
        pdf_action.triggered.connect(lambda: self.export_transactions('pdf', export_all))
        
        csv_action = menu.addAction("Export as CSV")
        csv_action.triggered.connect(lambda: self.export_transactions('csv', export_all))
        
        excel_action = menu.addAction("Export as Excel")
        excel_action.triggered.connect(lambda: self.export_transactions('excel', export_all))
        
        return menu
        
    def export_transactions(self, format, export_all=False):
        """Export transactions in selected format"""
        if not self.db.conn:
            QMessageBox.warning(self, "Export Error", "Database not connected")
            return
            
        # Get file extension
        ext_map = {'pdf': 'pdf', 'csv': 'csv', 'excel': 'xlsx'}
        extension = ext_map.get(format, 'pdf')
        
        # Determine what to export
        scope = "all" if export_all else f"page{self.current_page}"
        
        # Get file path from user
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            f"Export {'All' if export_all else 'Current Page'} Transactions as {format.upper()}",
            f"transactions_{scope}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extension}",
            f"{format.upper()} Files (*.{extension})"
        )
        
        if not file_path:
            return
            
        try:
            # Get transactions to export
            if export_all:
                transactions = self.all_transactions
            else:
                # Get current page transactions
                start_idx = (self.current_page - 1) * self.rows_per_page
                end_idx = min(start_idx + self.rows_per_page, self.total_transactions)
                transactions = self.all_transactions[start_idx:end_idx]
            
            # Create custom report generator for specific transactions
            generator = ReportGenerator(self.db)
            
            # Override the generator's get_transactions method temporarily
            original_get_transactions = generator._get_transactions
            generator._get_transactions = lambda start_date=None, end_date=None: transactions
            
            # Generate report
            report_buffer = generator.generate_transaction_report(format=format)
            
            # Restore original method
            generator._get_transactions = original_get_transactions
            
            # Save to file
            mode = 'wb' if format in ['pdf', 'excel'] else 'w'
            with open(file_path, mode) as f:
                if format in ['pdf', 'excel']:
                    f.write(report_buffer.read())
                else:
                    f.write(report_buffer.getvalue())
                    
            count = len(transactions)
            QMessageBox.information(self, "Export Complete", 
                f"{count} transactions exported to:\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export transactions:\n{str(e)}")