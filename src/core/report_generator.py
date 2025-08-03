"""
Report generation module for creating PDF and CSV exports
"""

from datetime import datetime
import csv
import io
import json
from typing import Dict, List, Any
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.widgets.markers import makeMarker
import pandas as pd
from core.database import DatabaseManager

class ReportGenerator:
    """Generate various types of reports from transaction and fraud data"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#0080ff'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#333333'),
            spaceAfter=20
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#0080ff'),
            spaceAfter=12
        ))
        
    def generate_transaction_report(self, start_date=None, end_date=None, format='pdf'):
        """Generate transaction report in PDF or CSV format"""
        # Get transactions
        transactions = self._get_transactions(start_date, end_date)
        
        if format == 'pdf':
            return self._generate_transaction_pdf(transactions, start_date, end_date)
        elif format == 'csv':
            return self._generate_transaction_csv(transactions)
        elif format == 'excel':
            return self._generate_transaction_excel(transactions)
        else:
            raise ValueError(f"Unsupported format: {format}")
            
    def generate_fraud_report(self, start_date=None, end_date=None, format='pdf'):
        """Generate fraud detection report"""
        # Get fraud data
        fraud_data = self._get_fraud_data(start_date, end_date)
        
        if format == 'pdf':
            return self._generate_fraud_pdf(fraud_data, start_date, end_date)
        elif format == 'csv':
            return self._generate_fraud_csv(fraud_data)
        else:
            raise ValueError(f"Unsupported format: {format}")
            
    def generate_risk_assessment_report(self, format='pdf'):
        """Generate risk assessment report"""
        # Get risk data
        risk_data = self._get_risk_data()
        
        if format == 'pdf':
            return self._generate_risk_pdf(risk_data)
        else:
            raise ValueError(f"Unsupported format: {format}")
            
    def _get_transactions(self, start_date=None, end_date=None):
        """Get transactions from database"""
        query = "SELECT * FROM transactions"
        params = []
        
        if start_date or end_date:
            query += " WHERE"
            if start_date:
                query += " timestamp >= ?"
                params.append(start_date)
            if start_date and end_date:
                query += " AND"
            if end_date:
                query += " timestamp <= ?"
                params.append(end_date)
                
        query += " ORDER BY timestamp DESC"
        
        cursor = self.db.conn.cursor()
        cursor.row_factory = self.db.dict_factory
        cursor.execute(query, params)
        return cursor.fetchall()
        
    def _get_fraud_data(self, start_date=None, end_date=None):
        """Get fraud detection data"""
        # Get fraud transactions
        query = """
            SELECT * FROM transactions 
            WHERE fraud_detected = 1
        """
        params = []
        
        if start_date or end_date:
            query += " AND"
            if start_date:
                query += " timestamp >= ?"
                params.append(start_date)
            if start_date and end_date:
                query += " AND"
            if end_date:
                query += " timestamp <= ?"
                params.append(end_date)
                
        cursor = self.db.conn.cursor()
        cursor.row_factory = self.db.dict_factory
        cursor.execute(query, params)
        fraud_transactions = cursor.fetchall()
        
        # Get fraud patterns
        cursor.execute("SELECT * FROM fraud_patterns WHERE enabled = 1")
        patterns = cursor.fetchall()
        
        # Get statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_transactions,
                SUM(CASE WHEN fraud_detected = 1 THEN 1 ELSE 0 END) as fraud_count,
                SUM(CASE WHEN blocked = 1 THEN 1 ELSE 0 END) as blocked_count,
                AVG(risk_score) as avg_risk_score,
                SUM(CASE WHEN fraud_detected = 1 THEN amount ELSE 0 END) as fraud_amount,
                SUM(amount) as total_amount
            FROM transactions
        """)
        stats = cursor.fetchone()
        
        return {
            'transactions': fraud_transactions,
            'patterns': patterns,
            'statistics': stats
        }
        
    def _get_risk_data(self):
        """Get risk assessment data"""
        cursor = self.db.conn.cursor()
        cursor.row_factory = self.db.dict_factory
        
        # Get risk distribution
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN risk_score < 0.3 THEN 'Low'
                    WHEN risk_score < 0.7 THEN 'Medium'
                    ELSE 'High'
                END as risk_level,
                COUNT(*) as count,
                AVG(amount) as avg_amount
            FROM transactions
            GROUP BY risk_level
        """)
        risk_distribution = cursor.fetchall()
        
        # Get top risk merchants
        cursor.execute("""
            SELECT 
                merchant_name,
                merchant_category,
                COUNT(*) as transaction_count,
                AVG(risk_score) as avg_risk,
                SUM(CASE WHEN fraud_detected = 1 THEN 1 ELSE 0 END) as fraud_count
            FROM transactions
            GROUP BY merchant_name
            ORDER BY avg_risk DESC
            LIMIT 10
        """)
        risky_merchants = cursor.fetchall()
        
        # Get temporal risk patterns
        cursor.execute("""
            SELECT 
                strftime('%H', timestamp) as hour,
                AVG(risk_score) as avg_risk,
                COUNT(*) as count
            FROM transactions
            GROUP BY hour
            ORDER BY hour
        """)
        hourly_risk = cursor.fetchall()
        
        return {
            'distribution': risk_distribution,
            'merchants': risky_merchants,
            'hourly': hourly_risk
        }
        
    def _generate_transaction_pdf(self, transactions, start_date, end_date):
        """Generate PDF transaction report"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Title
        title = Paragraph("Transaction Report", self.styles['CustomTitle'])
        story.append(title)
        
        # Date range
        date_text = "All Transactions"
        if start_date and end_date:
            date_text = f"From {start_date} to {end_date}"
        elif start_date:
            date_text = f"From {start_date}"
        elif end_date:
            date_text = f"Until {end_date}"
            
        story.append(Paragraph(date_text, self.styles['Normal']))
        story.append(Spacer(1, 0.5*inch))
        
        # Summary statistics
        story.append(Paragraph("Summary Statistics", self.styles['SectionHeader']))
        
        total = len(transactions)
        fraud_count = sum(1 for t in transactions if t['fraud_detected'])
        blocked_count = sum(1 for t in transactions if t['blocked'])
        total_amount = sum(t['amount'] for t in transactions)
        avg_risk = sum(t['risk_score'] for t in transactions) / total if total > 0 else 0
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total Transactions', f'{total:,}'],
            ['Total Amount', f'${total_amount:,.2f}'],
            ['Fraud Detected', f'{fraud_count:,} ({fraud_count/total*100:.1f}%)'],
            ['Blocked Transactions', f'{blocked_count:,} ({blocked_count/total*100:.1f}%)'],
            ['Average Risk Score', f'{avg_risk:.3f}']
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0080ff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.5*inch))
        
        # Add risk distribution chart
        if transactions:
            story.append(Paragraph("Risk Distribution", self.styles['SectionHeader']))
            risk_chart = self._create_risk_pie_chart(transactions)
            story.append(risk_chart)
            story.append(Spacer(1, 0.3*inch))
        
        # Transaction details
        story.append(Paragraph("Transaction Details", self.styles['SectionHeader']))
        
        # Prepare transaction data for table
        trans_data = [['Time', 'ID', 'Amount', 'Merchant', 'Risk', 'Status']]
        
        # Show all transactions but limit display for readability
        display_limit = min(len(transactions), 100)  # Show up to 100 in PDF
        
        for t in transactions[:display_limit]:
            time_str = datetime.fromisoformat(str(t['timestamp'])).strftime('%Y-%m-%d %H:%M')
            status = 'Blocked' if t['blocked'] else 'Fraud' if t['fraud_detected'] else 'OK'
            
            trans_data.append([
                time_str,
                t['transaction_id'][-8:],  # Last 8 chars
                f"${t['amount']:.2f}",
                t['merchant_name'][:20],  # Truncate long names
                f"{t['risk_score']:.2f}",
                status
            ])
            
        trans_table = Table(trans_data, colWidths=[1.5*inch, 1*inch, 1*inch, 2*inch, 0.8*inch, 0.8*inch])
        trans_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0080ff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),  # Amount column
            ('ALIGN', (4, 0), (5, -1), 'CENTER'),  # Risk and Status columns
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
        ]))
        
        # Color code status cells
        for i, t in enumerate(transactions[:display_limit], start=1):
            if t['blocked']:
                trans_table.setStyle(TableStyle([
                    ('BACKGROUND', (5, i), (5, i), colors.HexColor('#ff3333')),
                    ('TEXTCOLOR', (5, i), (5, i), colors.white)
                ]))
            elif t['fraud_detected']:
                trans_table.setStyle(TableStyle([
                    ('BACKGROUND', (5, i), (5, i), colors.orange),
                    ('TEXTCOLOR', (5, i), (5, i), colors.white)
                ]))
                
        story.append(trans_table)
        
        if len(transactions) > display_limit:
            story.append(Paragraph(f"Showing {display_limit} of {len(transactions)} transactions (see CSV/Excel for complete data)", self.styles['Normal']))
            
        # Add transaction volume chart
        story.append(PageBreak())
        story.append(Paragraph("Transaction Volume Analysis", self.styles['SectionHeader']))
        volume_chart = self._create_volume_chart(transactions)
        story.append(volume_chart)
            
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
        
    def _generate_transaction_csv(self, transactions):
        """Generate CSV transaction report"""
        buffer = io.StringIO()
        
        fieldnames = [
            'timestamp', 'transaction_id', 'account_number', 'amount',
            'transaction_type', 'merchant_name', 'merchant_category',
            'location', 'risk_score', 'fraud_detected', 'blocked', 'status'
        ]
        
        writer = csv.DictWriter(buffer, fieldnames=fieldnames)
        writer.writeheader()
        
        for t in transactions:
            writer.writerow({
                'timestamp': t['timestamp'],
                'transaction_id': t['transaction_id'],
                'account_number': t['account_number'],
                'amount': t['amount'],
                'transaction_type': t['transaction_type'],
                'merchant_name': t['merchant_name'],
                'merchant_category': t['merchant_category'],
                'location': t['location'],
                'risk_score': t['risk_score'],
                'fraud_detected': 'Yes' if t['fraud_detected'] else 'No',
                'blocked': 'Yes' if t['blocked'] else 'No',
                'status': t['status']
            })
            
        buffer.seek(0)
        return buffer
        
    def _generate_transaction_excel(self, transactions):
        """Generate Excel transaction report"""
        buffer = io.BytesIO()
        
        # Convert to DataFrame
        df = pd.DataFrame(transactions)
        
        # Format columns
        df['fraud_detected'] = df['fraud_detected'].map({1: 'Yes', 0: 'No'})
        df['blocked'] = df['blocked'].map({1: 'Yes', 0: 'No'})
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Create Excel writer
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            # Write main data
            df.to_excel(writer, sheet_name='Transactions', index=False)
            
            # Get workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Transactions']
            
            # Add formats
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#0080ff',
                'font_color': 'white',
                'border': 1
            })
            
            money_format = workbook.add_format({'num_format': '$#,##0.00'})
            risk_format = workbook.add_format({'num_format': '0.000'})
            
            # Format headers
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
                
            # Set column widths and formats
            worksheet.set_column('A:A', 20)  # timestamp
            worksheet.set_column('B:B', 15)  # transaction_id
            worksheet.set_column('D:D', 12, money_format)  # amount
            worksheet.set_column('I:I', 10, risk_format)  # risk_score
            
            # Add summary sheet
            summary_df = pd.DataFrame({
                'Metric': ['Total Transactions', 'Total Amount', 'Average Amount', 
                          'Fraud Count', 'Blocked Count', 'Average Risk Score'],
                'Value': [
                    len(df),
                    df['amount'].sum(),
                    df['amount'].mean(),
                    len(df[df['fraud_detected'] == 'Yes']),
                    len(df[df['blocked'] == 'Yes']),
                    df['risk_score'].mean()
                ]
            })
            
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
        buffer.seek(0)
        return buffer
        
    def _generate_fraud_pdf(self, fraud_data, start_date, end_date):
        """Generate PDF fraud detection report"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Title
        title = Paragraph("Fraud Detection Report", self.styles['CustomTitle'])
        story.append(title)
        
        # Date range
        date_text = "All Time Analysis"
        if start_date and end_date:
            date_text = f"Analysis Period: {start_date} to {end_date}"
            
        story.append(Paragraph(date_text, self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        
        stats = fraud_data['statistics']
        fraud_rate = (stats['fraud_count'] / stats['total_transactions'] * 100) if stats['total_transactions'] > 0 else 0
        fraud_loss_rate = (stats['fraud_amount'] / stats['total_amount'] * 100) if stats['total_amount'] > 0 else 0
        
        summary_text = f"""
        During the reporting period, the system processed {stats['total_transactions']:,} transactions 
        with a total value of ${stats['total_amount']:,.2f}. The fraud detection system identified 
        {stats['fraud_count']:,} fraudulent transactions ({fraud_rate:.2f}% of total), representing 
        ${stats['fraud_amount']:,.2f} in potential losses ({fraud_loss_rate:.2f}% of total value).
        
        The system successfully blocked {stats['blocked_count']:,} transactions, preventing significant 
        financial losses. The average risk score across all transactions was {stats['avg_risk_score']:.3f}.
        """
        
        story.append(Paragraph(summary_text, self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Fraud Detection Rules
        story.append(Paragraph("Active Fraud Detection Rules", self.styles['SectionHeader']))
        
        rules_data = [['Rule Name', 'Type', 'Parameters', 'Status']]
        for pattern in fraud_data['patterns']:
            params = json.loads(pattern['parameters'])
            param_str = ', '.join([f"{k}: {v}" for k, v in params.items()])[:50]
            
            rules_data.append([
                pattern['pattern_name'],
                pattern['pattern_type'].replace('_', ' ').title(),
                param_str,
                'Active' if pattern['enabled'] else 'Inactive'
            ])
            
        rules_table = Table(rules_data, colWidths=[2*inch, 1.5*inch, 2.5*inch, 1*inch])
        rules_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0080ff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
        ]))
        story.append(rules_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Add fraud trend chart
        story.append(Paragraph("Fraud Detection Trends", self.styles['SectionHeader']))
        trend_chart = self._create_fraud_trend_chart(fraud_data['transactions'])
        story.append(trend_chart)
        story.append(PageBreak())
        
        # Fraud Transactions
        story.append(Paragraph("Detected Fraud Transactions", self.styles['SectionHeader']))
        
        fraud_trans_data = [['Date/Time', 'Amount', 'Merchant', 'Risk Score', 'Action']]
        
        fraud_limit = min(len(fraud_data['transactions']), 50)  # Show up to 50 fraud transactions
        
        for t in fraud_data['transactions'][:fraud_limit]:
            time_str = datetime.fromisoformat(str(t['timestamp'])).strftime('%Y-%m-%d %H:%M')
            action = 'Blocked' if t['blocked'] else 'Flagged'
            
            fraud_trans_data.append([
                time_str,
                f"${t['amount']:.2f}",
                t['merchant_name'],
                f"{t['risk_score']:.3f}",
                action
            ])
            
        fraud_table = Table(fraud_trans_data, colWidths=[1.5*inch, 1*inch, 2.5*inch, 1*inch, 1*inch])
        fraud_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff3333')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('ALIGN', (3, 0), (4, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ffe6e6')])
        ]))
        story.append(fraud_table)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
        
    def _generate_fraud_csv(self, fraud_data):
        """Generate CSV fraud report"""
        buffer = io.StringIO()
        
        # Write statistics section
        buffer.write("FRAUD DETECTION STATISTICS\n")
        buffer.write("-" * 50 + "\n")
        
        stats = fraud_data['statistics']
        buffer.write(f"Total Transactions,{stats['total_transactions']}\n")
        buffer.write(f"Fraud Detected,{stats['fraud_count']}\n")
        buffer.write(f"Blocked Transactions,{stats['blocked_count']}\n")
        buffer.write(f"Total Amount,${stats['total_amount']:.2f}\n")
        buffer.write(f"Fraud Amount,${stats['fraud_amount']:.2f}\n")
        buffer.write(f"Average Risk Score,{stats['avg_risk_score']:.3f}\n")
        buffer.write("\n")
        
        # Write fraud transactions
        buffer.write("FRAUD TRANSACTIONS\n")
        buffer.write("-" * 50 + "\n")
        
        fieldnames = [
            'timestamp', 'transaction_id', 'amount', 'merchant_name',
            'merchant_category', 'location', 'risk_score', 'blocked'
        ]
        
        writer = csv.DictWriter(buffer, fieldnames=fieldnames)
        writer.writeheader()
        
        for t in fraud_data['transactions']:
            writer.writerow({
                'timestamp': t['timestamp'],
                'transaction_id': t['transaction_id'],
                'amount': t['amount'],
                'merchant_name': t['merchant_name'],
                'merchant_category': t['merchant_category'],
                'location': t['location'],
                'risk_score': t['risk_score'],
                'blocked': 'Yes' if t['blocked'] else 'No'
            })
            
        buffer.seek(0)
        return buffer
        
    def _generate_risk_pdf(self, risk_data):
        """Generate PDF risk assessment report"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Title
        title = Paragraph("Risk Assessment Report", self.styles['CustomTitle'])
        story.append(title)
        
        story.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}", self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Risk Distribution
        story.append(Paragraph("Risk Distribution Analysis", self.styles['SectionHeader']))
        
        dist_data = [['Risk Level', 'Transaction Count', 'Average Amount']]
        for item in risk_data['distribution']:
            dist_data.append([
                item['risk_level'],
                f"{item['count']:,}",
                f"${item['avg_amount']:.2f}"
            ])
            
        dist_table = Table(dist_data, colWidths=[2*inch, 2*inch, 2*inch])
        dist_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0080ff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        # Color code risk levels
        for i, item in enumerate(risk_data['distribution'], start=1):
            if item['risk_level'] == 'Low':
                color = colors.lightgreen
            elif item['risk_level'] == 'Medium':
                color = colors.yellow
            else:
                color = colors.pink
                
            dist_table.setStyle(TableStyle([
                ('BACKGROUND', (0, i), (0, i), color)
            ]))
            
        story.append(dist_table)
        story.append(Spacer(1, 0.3*inch))
        
        # High Risk Merchants
        story.append(Paragraph("High Risk Merchants", self.styles['SectionHeader']))
        
        merchant_data = [['Merchant', 'Category', 'Transactions', 'Avg Risk', 'Fraud Count']]
        for merchant in risk_data['merchants'][:10]:
            merchant_data.append([
                merchant['merchant_name'][:25],
                merchant['merchant_category'].replace('_', ' ').title(),
                str(merchant['transaction_count']),
                f"{merchant['avg_risk']:.3f}",
                str(merchant['fraud_count'])
            ])
            
        merchant_table = Table(merchant_data, colWidths=[2*inch, 1.5*inch, 1*inch, 1*inch, 1*inch])
        merchant_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff3333')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
        ]))
        story.append(merchant_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Add hourly risk chart
        story.append(Paragraph("Risk Patterns by Hour", self.styles['SectionHeader']))
        hourly_chart = self._create_hourly_risk_chart(risk_data['hourly'])
        story.append(hourly_chart)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
        
    def _create_risk_pie_chart(self, transactions):
        """Create pie chart for risk distribution"""
        # Calculate risk distribution
        risk_counts = {'Low': 0, 'Medium': 0, 'High': 0}
        for t in transactions:
            if t['risk_score'] < 0.3:
                risk_counts['Low'] += 1
            elif t['risk_score'] < 0.7:
                risk_counts['Medium'] += 1
            else:
                risk_counts['High'] += 1
                
        # Create drawing
        drawing = Drawing(400, 200)
        pie = Pie()
        pie.x = 150
        pie.y = 50
        pie.width = 100
        pie.height = 100
        pie.data = list(risk_counts.values())
        pie.labels = [f"{k}\n({v})" for k, v in risk_counts.items()]
        pie.slices.strokeWidth = 0.5
        pie.slices[0].fillColor = colors.green
        pie.slices[1].fillColor = colors.yellow
        pie.slices[2].fillColor = colors.red
        
        drawing.add(pie)
        return drawing
        
    def _create_volume_chart(self, transactions):
        """Create bar chart for transaction volume by type"""
        # Count by type
        type_counts = {}
        for t in transactions:
            ttype = t['transaction_type'].title()
            type_counts[ttype] = type_counts.get(ttype, 0) + 1
            
        # Create drawing
        drawing = Drawing(400, 200)
        bc = VerticalBarChart()
        bc.x = 50
        bc.y = 50
        bc.height = 125
        bc.width = 300
        bc.data = [list(type_counts.values())]
        bc.strokeColor = colors.black
        bc.valueAxis.valueMin = 0
        bc.valueAxis.valueMax = max(type_counts.values()) * 1.1
        bc.valueAxis.valueStep = max(type_counts.values()) // 5
        bc.categoryAxis.labels.boxAnchor = 'ne'
        bc.categoryAxis.labels.dx = 8
        bc.categoryAxis.labels.dy = -2
        bc.categoryAxis.labels.angle = 30
        bc.categoryAxis.categoryNames = list(type_counts.keys())
        bc.bars[(0,0)].fillColor = colors.HexColor('#0080ff')
        
        drawing.add(bc)
        return drawing
        
    def _create_fraud_trend_chart(self, fraud_transactions):
        """Create line chart showing fraud detection over time"""
        # Group by day
        from collections import defaultdict
        daily_counts = defaultdict(int)
        
        for t in fraud_transactions:
            date = datetime.fromisoformat(str(t['timestamp'])).date()
            daily_counts[date] += 1
            
        if not daily_counts:
            drawing = Drawing(400, 200)
            drawing.add(String(200, 100, "No fraud data available", textAnchor='middle'))
            return drawing
            
        # Sort by date
        sorted_dates = sorted(daily_counts.keys())
        values = [daily_counts[d] for d in sorted_dates]
        
        # Create drawing
        drawing = Drawing(400, 200)
        lp = LinePlot()
        lp.x = 50
        lp.y = 50
        lp.height = 125
        lp.width = 300
        lp.data = [[(i, v) for i, v in enumerate(values)]]
        lp.lines[0].strokeColor = colors.red
        lp.lines[0].strokeWidth = 2
        lp.xValueAxis.valueMin = 0
        lp.xValueAxis.valueMax = len(values) - 1
        lp.yValueAxis.valueMin = 0
        lp.yValueAxis.valueMax = max(values) * 1.1 if values else 1
        
        drawing.add(lp)
        return drawing
        
    def _create_hourly_risk_chart(self, hourly_data):
        """Create bar chart for risk by hour"""
        if not hourly_data:
            drawing = Drawing(400, 200)
            drawing.add(String(200, 100, "No hourly data available", textAnchor='middle'))
            return drawing
            
        # Prepare data
        hours = []
        risks = []
        for item in hourly_data:
            hours.append(f"{item['hour']}:00")
            risks.append(float(item['avg_risk']))
            
        # Create drawing
        drawing = Drawing(400, 200)
        bc = VerticalBarChart()
        bc.x = 50
        bc.y = 50
        bc.height = 125
        bc.width = 300
        bc.data = [risks]
        bc.strokeColor = colors.black
        bc.valueAxis.valueMin = 0
        bc.valueAxis.valueMax = 1.0
        bc.valueAxis.valueStep = 0.2
        bc.categoryAxis.labels.boxAnchor = 'ne'
        bc.categoryAxis.labels.dx = 8
        bc.categoryAxis.labels.dy = -2
        bc.categoryAxis.labels.angle = 45
        bc.categoryAxis.categoryNames = hours
        
        # Color bars based on risk level
        for i, risk in enumerate(risks):
            if risk < 0.3:
                bc.bars[(0,i)].fillColor = colors.green
            elif risk < 0.7:
                bc.bars[(0,i)].fillColor = colors.yellow
            else:
                bc.bars[(0,i)].fillColor = colors.red
                
        drawing.add(bc)
        return drawing