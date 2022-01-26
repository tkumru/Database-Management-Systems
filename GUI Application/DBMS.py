from PyQt5 import QtWidgets
import sys
from app import Ui_KFAUManagementSystem
import pypyodbc as mssql
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
import threading
import time

global database
database = None

class App(QtWidgets.QMainWindow):
    def __init__(self):
        super(App, self).__init__()
        self.ui = Ui_KFAUManagementSystem()
        self.ui.setupUi(self)

        self.ui.connectButton.clicked.connect(self.connectDBMS)
        self.ui.disconnectButton.clicked.connect(self.disconnectDBMS)
        self.ui.getTable.clicked.connect(self.setTableInListview)
        self.ui.getTableInfo.clicked.connect(self.getTableInfo)
        self.ui.clearListWidget.clicked.connect(self.clearList)
        self.ui.addRow.clicked.connect(self.addRow)
        self.ui.deleteRow.clicked.connect(self.deleteRow)
        self.ui.clearTable.clicked.connect(self.clearTable)
        self.ui.insertRowButton.clicked.connect(self.insert)
        self.ui.updateRowButton.clicked.connect(self.update)
        self.ui.DeleteRowButton.clicked.connect(self.delete)
        self.ui.pushButton.clicked.connect(self.getProcedure)
        self.ui.getProcedureInfo.clicked.connect(self.getProcedureInfo)

        self.ui.progressBar.setVisible(0)
        self.ui.getTableInfo.setVisible(0)
        self.ui.clearListWidget.setVisible(0)
        self.ui.selectedTableInfo.setVisible(0)
        self.ui.insertRowButton.setVisible(0)
        self.ui.DeleteRowButton.setVisible(0)
        self.ui.updateRowButton.setVisible(0)
        self.ui.label_4.setVisible(0)
        self.ui.addRow.setVisible(0)
        self.ui.deleteRow.setVisible(0)
        self.ui.clearTable.setVisible(0)
        self.ui.line.setVisible(0)
        self.ui.getProcedureInfo.setVisible(0)

        control = threading.Thread(target=self.control)
        control.start()

        self.getTableName()
        self.getColumnNames()
        self.getRowVariables()

    def connectDBMS(self):
        server_name = self.ui.serverNameInput.text() # DESKTOP-IHR8K8V\SQLEXPRESS
        database_name = self.ui.databaseNameInput.text() # KFAUManagementSystem

        result = QMessageBox.question(self, "Connection", f"Is connection to {database_name} in {server_name} server true?", 
        QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)

        if result == QMessageBox.Ok:
            try:
                global database   
                database = mssql.connect(
                            'Driver={SQL Server};'
                            f'Server={server_name};'
                            f'Database={database_name};'
                            'Trusted_Connection=True;'
                        )

                result = QMessageBox.information(self, "Information", f"Connected is successful.")
            except Exception as error:
                result = QMessageBox.warning(self, "Connection", "Database connection is failed!" + f"\n{error}")

    def disconnectDBMS(self):
        try:
            database.close()
            result = QMessageBox.information(self, "Information", f"Connection is closed.")
        except Exception as error:
            result = QMessageBox.critical(self, "Error", f"Error: '{error}'")

    def setTableInListview(self):
        try:
            self.ui.getTableInfo.setVisible(1)
            self.ui.clearListWidget.setVisible(1)
            self.ui.getProcedureInfo.setVisible(1)
            # Get table name from database
            cursor = database.cursor()

            cursor.execute("SELECT * FROM INFORMATION_SCHEMA.TABLES ")

            table_names = list()
            for eleman in cursor.fetchall():
                table_names.append(eleman[2])

            # List view add table names
            self.ui.listTable.addItems(table_names)
        except AttributeError as at:
            result = QMessageBox.critical(self, "Error", "Please connect to database and server")
            self.ui.getTableInfo.setVisible(0)
            self.ui.clearListWidget.setVisible(0)
        except Exception as error:
            result = QMessageBox.critical(self, "Error", f"Error: '{error}'")
            self.ui.getTableInfo.setVisible(0)
            self.ui.clearListWidget.setVisible(0)

    def getTableInfo(self):
        try:
            self.ui.selectedTableInfo.setVisible(1)
            self.ui.selectedTableInfo.horizontalHeader().setVisible(1)
            self.ui.addRow.setVisible(1)
            self.ui.deleteRow.setVisible(1)
            self.ui.clearTable.setVisible(1)
            self.ui.label_4.setVisible(1)
            self.ui.updateRowButton.setVisible(1)
            self.ui.line.setVisible(1)
            self.ui.DeleteRowButton.setVisible(1)

            index = self.ui.listTable.currentRow()
            item = self.ui.listTable.item(index).text()

            cursor = database.cursor()

            
            column_names = self.getColumnNames()
            column_names = tuple(column_names)

            table = self.ui.selectedTableInfo

            table.setColumnCount(len(column_names))
            table.setHorizontalHeaderLabels(column_names)

            cursor.execute(f"SELECT COUNT(*) FROM {item}")
            row_number = cursor.fetchall()[0][0]
            table.setRowCount(row_number)
            cursor.execute(f"SELECT * FROM {item}")

            row_tuples = cursor.fetchall()
            
            for i in range(row_number):
                for y in range(len(column_names)):
                    table.setItem(i, y, QTableWidgetItem("{}".format(row_tuples[i][y])))

        except Exception as error:
            result = QMessageBox.critical(self, "Error", f"Error: '{error}'")
            self.ui.selectedTableInfo.setVisible(0)
            self.ui.selectedTableInfo.horizontalHeader().setVisible(0)
            self.ui.addRow.setVisible(0)
            self.ui.deleteRow.setVisible(0)
            self.ui.clearTable.setVisible(0)
            self.ui.label_4.setVisible(0)
            self.ui.updateRowButton.setVisible(0)
            self.ui.line.setVisible(0)
            self.ui.DeleteRowButton.setVisible(0)

    def getProcedureInfo(self):
        try:
            self.ui.getProcedureInfo.setVisible(1)
            self.ui.selectedTableInfo.setVisible(1)
            self.ui.selectedTableInfo.horizontalHeader().setVisible(1)
            
            procedure_name = self.getTableName()
            print(procedure_name)
            cursor = database.cursor()

            column_names = list()
            cursor.execute(f"SELECT * FROM sys.dm_exec_describe_first_result_set_for_object(OBJECT_ID('{procedure_name}'), 1)")
            for column_name in cursor.fetchall():
                column_names.append(column_name[2])
            column_names = tuple(column_names)
            print(column_names)

            cursor.execute(f"EXEC {procedure_name}")
            row_count = len(cursor.fetchall())
            print(row_count)
            
            table = self.ui.selectedTableInfo
            
            table.setColumnCount(len(column_names))
            table.setHorizontalHeaderLabels(column_names)
            table.setRowCount(row_count)
            row_tuples = cursor.execute(f"EXEC {procedure_name}").fetchall()
            print(row_tuples)
            for i in range(row_count):
                    for y in range(len(column_names)):
                        table.setItem(i, y, QTableWidgetItem("{}".format(row_tuples[i][y])))
        except Exception as error:
            result = QMessageBox.critical(self, "Error", f"Error: '{error}'")
            self.ui.selectedTableInfo.setVisible(0)
            self.ui.selectedTableInfo.horizontalHeader().setVisible(0)
            self.ui.addRow.setVisible(0)
            self.ui.deleteRow.setVisible(0)
            self.ui.clearTable.setVisible(0)
            self.ui.label_4.setVisible(0)
            self.ui.updateRowButton.setVisible(0)
            self.ui.line.setVisible(0)
            self.ui.DeleteRowButton.setVisible(0)
            self.ui.getProcedureInfo.setVisible(0)
            

    def clearList(self):
        self.ui.listTable.clear()
        self.ui.getTableInfo.setVisible(0)
        self.ui.clearListWidget.setVisible(0)
        self.ui.addRow.setVisible(0)
        self.ui.deleteRow.setVisible(0)
        self.ui.clearTable.setVisible(0)
        self.ui.selectedTableInfo.setVisible(0)
        self.ui.label_4.setVisible(0)
        self.ui.updateRowButton.setVisible(0)
        self.ui.line.setVisible(0)
        self.ui.insertRowButton.setVisible(0)
        self.ui.DeleteRowButton.setVisible(0)
        self.ui.progressBar.setVisible(0)
        self.ui.progressBar.setValue(0)
        self.ui.getProcedureInfo.setVisible(0)

    def addRow(self):
        self.ui.insertRowButton.setVisible(1)

        table = self.ui.selectedTableInfo.rowCount()
        self.ui.selectedTableInfo.insertRow(table)
        self.ui.selectedTableInfo.setItem(table, 0, QTableWidgetItem("Don't Edit!"))

    def deleteRow(self):
        self.ui.DeleteRowButton.setVisible(1)

        table = self.ui.selectedTableInfo.rowCount()
        self.ui.selectedTableInfo.removeRow(table - 1)

    def clearTable(self):
        table = self.ui.selectedTableInfo.rowCount()
        for del_ in range(table, -1, -1):
            self.ui.selectedTableInfo.removeRow(del_)
        self.ui.selectedTableInfo.horizontalHeader().setVisible(0)
        self.ui.addRow.setVisible(0)
        self.ui.deleteRow.setVisible(0)
        self.ui.clearTable.setVisible(0)
        self.ui.label_4.setVisible(0)
        self.ui.updateRowButton.setVisible(0)
        self.ui.line.setVisible(0)
        self.ui.insertRowButton.setVisible(0)
        self.ui.progressBar.setVisible(0)
        self.ui.progressBar.setValue(0)
        self.ui.DeleteRowButton.setVisible(0)

    def insert(self):
        try:
            self.ui.progressBar.setVisible(1)

            # Get table name
            table_name = self.getTableName()

            # Get selected row values 
            row_values = self.getRowVariables()
            row_values.pop(0)

            row_values = tuple(row_values)

            cursor = database.cursor()

            if len(row_values) == 1:
                cursor.execute(f"INSERT INTO {table_name} VALUES ('{row_values[0]}')")
            else:
                cursor.execute(f"INSERT INTO {table_name} VALUES {row_values}")
            database.commit()

            for t in range(0, 101):
                time.sleep(0.01)
                self.ui.progressBar.setValue(t)
            
            result = QMessageBox.information(self, "Information", f"Inputs added in {table_name}.")
        except Exception as error:
            result = QMessageBox.critical(self, "Error", f"Error: {error}.\nBe sure! Clicked row number not to many or one cell.")

    def update(self):
        try:
            self.ui.progressBar.setVisible(1)
            # Get Column name and number        
            cursor = database.cursor()

            column_names = self.getColumnNames()

            # Get table name
            table_name = self.getTableName()

            # Get selected row values 
            row_values = self.getRowVariables()

            # update
            id_value = row_values[0]
            id_column_name = column_names[0]
            column_names.pop(0)
            row_values.pop(0)

            suffix = ' = '
            column_names = [m + suffix for m in column_names]
        
            combine = list()
            
            for x in range(len(column_names)):
                combine.append(column_names[x] + f"'{row_values[x]}'")

            update_ = ", ".join(combine)
            
            if update_[-2] == ", ":
                update_ = update_[: -2] + " "

            cursor.execute(f"UPDATE {table_name} SET {update_} WHERE {id_column_name}={id_value}")
            database.commit()

            for t in range(0, 101):
                time.sleep(0.01)
                self.ui.progressBar.setValue(t)

            result = QMessageBox.information(self, "Information", f"{table_name} updated with editing.")
        
        except Exception as error:
            result = QMessageBox.critical(self, "Error", f"Error: {error}.\nBe sure! Clicked row number not to many or one cell.")
    
        
    def delete(self):
        try:
            self.ui.progressBar.setVisible(1)

            # Get table name
            table_name = self.getTableName()

            # Get row variables
            row_values = self.getRowVariables()

            # Get Column name and number        
            column_names = self.getColumnNames()

            cursor = database.cursor()
            cursor.execute(f"DELETE FROM {table_name} WHERE {column_names[0]} = {row_values[0]}")
            database.commit()

            for t in range(0, 101):
                time.sleep(0.01)
                self.ui.progressBar.setValue(t)

            result = QMessageBox.information(self, "Information", f"Selected row deleted from {table_name}.")
        
        except Exception as error:
            result = QMessageBox.critical(self, "Error", f"Error: {error}.\nBe sure! Clicked row number not to many or one cell.")

    def control(self):
        while True:
            ui = self.ui
            if(ui.updateRowButton.isVisible() == 1 and ui.insertRowButton.isVisible() == 0 and ui.DeleteRowButton.isVisible() == 1):
                ui.progressLabel.setText("UPDATE:  You can update row to table but one row by one row after select row number.\nDELETE:  You can delete row to table but one row by one row after select row number.")
            elif(ui.updateRowButton.isVisible() == 1 and ui.insertRowButton.isVisible() == 1 and ui.DeleteRowButton.isVisible() == 1):
                ui.progressLabel.setText("UPDATE:  You can update row to table but one row by one row after select row number.\nINSERT: You can insert row to table but one row by one row after select row number.\nDELETE: You can delete row to table but one row by one row after select row number.")
            else:
                ui.progressLabel.setText("")

            time.sleep(1)

    def getTableName(self):
        index_table = self.ui.listTable.currentRow()
        if self.ui.listTable.item(index_table) != None:
            table_name = self.ui.listTable.item(index_table).text()
            return table_name
        return None

    def getColumnNames(self):
        item = None
        index = self.ui.listTable.currentRow()
        if self.ui.listTable.item(index) != None:
            item = self.ui.listTable.item(index).text()

        column_names = list()
        if database != None:
            cursor = database.cursor()
            cursor.execute(f"SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME=N'{item}'")
            
            for column in cursor.fetchall():
                column_names.append(column[3])

        return column_names

    def getRowVariables(self):
        row_values = list()
        selected_row = self.ui.selectedTableInfo.currentRow()
        header_count = self.ui.selectedTableInfo.columnCount()

        for i in range(header_count):
            if self.ui.selectedTableInfo.item(selected_row, i) is not None:
                row_values.append(self.ui.selectedTableInfo.item(selected_row, i).text())
            else:
                row_values.append(self.ui.selectedTableInfo.item(selected_row, i))

        return row_values

    def getProcedure(self):
        try:
            self.ui.getProcedureInfo.setVisible(1)
            self.ui.getTableInfo.setVisible(1)
            self.ui.clearListWidget.setVisible(1)

            cursor = database.cursor()
            
            cursor.execute("SELECT * FROM INFORMATION_SCHEMA.ROUTINES WHERE ROUTINE_TYPE = 'PROCEDURE'")

            procedure_names = list()
            for eleman in cursor.fetchall():
                procedure_names.append(eleman[2])

            self.ui.listTable.addItems(procedure_names)

            return procedure_names

        except Exception as error:
            result = QMessageBox.critical(self, "Error", f"Error: '{error}'")
            self.ui.getProcedureInfo.setVisible(0)
            self.ui.getTableInfo.setVisible(0)
            self.ui.clearListWidget.setVisible(0)

def imShow():
    application = QtWidgets.QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(application.exec_())

imShow()
