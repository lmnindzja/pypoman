import subprocess
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
from data_collector import collect_server_data, parse_powershell_datetime, get_iis_state
from mock_data import generate_mock_services, generate_mock_web_services, generate_mock_network_connections
import json
from PyQt5.QtGui import QColor


def load_data(ui):
    """Загрузка данных в таблицу."""
    mask = ui.search_input.text().strip()
    if not mask:
        QMessageBox.warning(ui, "Ошибка", "Введите маску для поиска!")
        return

    try:
        if ui.demo_mode_checkbox.isChecked():
            # Используем моковые данные
            data = generate_mock_services()
        else:
            # Собираем реальные данные
            data = collect_server_data(mask)
            print("Собранные данные:", data)  # Отладочный вывод

        ui.table.setRowCount(0)  # Очистить таблицу
        for row in data:
            row_position = ui.table.rowCount()
            ui.table.insertRow(row_position)
            for col, key in enumerate([
                "PSComputerName", "Port", "Type", "Name", "Version", "State", "PID",
                "User", "StartTime", "LastBootTime", "RMQConnCount"
            ]):
                value = row.get(key, "")
                if key == "StartTime":
                    value = parse_powershell_datetime(value)  # Преобразуем дату
                elif key == "State" and row.get("Type", "").lower() == "iis":
                    # Если тип IIS, получаем состояние пула приложений
                    value = get_iis_state(row["PSComputerName"], row["Name"])
                elif key == "Version" and isinstance(value, dict):
                    # Если версия — словарь, извлекаем значение
                    value = value.get("value", value)
                item = QTableWidgetItem(str(value))

                # Раскрашиваем строку в зависимости от состояния
                if key == "State":
                    if value == "Running":
                        item.setBackground(QColor("green"))
                        item.setForeground(QColor("white"))
                    elif value == "Stopped":
                        item.setBackground(QColor("red"))
                        item.setForeground(QColor("white"))
                    else:
                        item.setBackground(QColor("yellow"))
                        item.setForeground(QColor("black"))

                ui.table.setItem(row_position, col, item)

        update_stats(ui)
        QMessageBox.information(ui, "Успех", "Данные успешно загружены!")
    except Exception as e:
        QMessageBox.critical(ui, "Ошибка", f"Ошибка загрузки данных: {e}")


def open_disc(ui):
    """Открытие проводника Windows на выбранных серверах."""
    selected_rows = ui.table.selectionModel().selectedRows()
    if not selected_rows:
        QMessageBox.information(ui, "Информация", "Пожалуйста, выберите хотя бы одну строку для открытия проводника.")
        return

    for row in selected_rows:
        server = ui.table.item(row.row(), 0).text()
        try:
            unc_path = f"\\\\{server}\\c$"
            subprocess.Popen(["explorer", unc_path], shell=True)
        except Exception as e:
            QMessageBox.critical(ui, "Ошибка", f"Не удалось открыть проводник для сервера {server}.\n{e}")


import subprocess
from PyQt5.QtWidgets import QMessageBox


def restart_selected(ui):
    """Перезапуск выделенных служб или веб-сервисов IIS."""
    selected_rows = ui.table.selectionModel().selectedRows()
    if not selected_rows:
        QMessageBox.information(ui, "Информация", "Пожалуйста, выберите хотя бы одну строку для перезапуска.")
        return

    for row in selected_rows:
        service_type = ui.table.item(row.row(), 2).text()  # Тип службы (например, IIS)
        service_name = ui.table.item(row.row(), 3).text()  # Имя службы
        server = ui.table.item(row.row(), 0).text()  # Сервер

        try:
            if service_type.lower() == "iis":
                # PowerShell-скрипт для перезапуска IIS
                ps_script = f"""
                Invoke-Command -ComputerName {server} -ScriptBlock {{
                    Import-Module WebAdministration
                    Restart-WebAppPool -Name {service_name}
                }}
                """
                subprocess.run(["powershell", "-Command", ps_script], check=True)
                QMessageBox.information(ui, "Успех", f"Веб-сервис {service_name} на сервере {server} успешно перезапущен.")
            else:
                # Перезапуск обычной службы
                ps_script = f"Restart-Service -Name {service_name} -ComputerName {server}"
                subprocess.run(["powershell", "-Command", ps_script], check=True)
                QMessageBox.information(ui, "Успех", f"Служба {service_name} на сервере {server} успешно перезапущена.")
        except Exception as e:
            QMessageBox.critical(ui, "Ошибка", f"Не удалось перезапустить {service_name} на сервере {server}.\n{e}")


def stop_selected(ui):
    """Остановка выделенных служб или веб-сервисов IIS."""
    selected_rows = ui.table.selectionModel().selectedRows()
    if not selected_rows:
        QMessageBox.information(ui, "Информация", "Пожалуйста, выберите хотя бы одну строку для остановки.")
        return

    for row in selected_rows:
        service_type = ui.table.item(row.row(), 2).text()  # Тип службы (например, IIS)
        service_name = ui.table.item(row.row(), 3).text()  # Имя службы
        server = ui.table.item(row.row(), 0).text()  # Сервер

        try:
            if service_type.lower() == "iis":
                # PowerShell-скрипт для остановки IIS
                ps_script = f"""
                Invoke-Command -ComputerName {server} -ScriptBlock {{
                    Import-Module WebAdministration
                    Stop-WebAppPool -Name {service_name}
                }}
                """
                subprocess.run(["powershell", "-Command", ps_script], check=True)
                QMessageBox.information(ui, "Успех", f"Веб-сервис {service_name} на сервере {server} успешно остановлен.")
            else:
                # Остановка обычной службы
                ps_script = f"Stop-Service -Name {service_name} -ComputerName {server}"
                subprocess.run(["powershell", "-Command", ps_script], check=True)
                QMessageBox.information(ui, "Успех", f"Служба {service_name} на сервере {server} успешно остановлена.")
        except Exception as e:
            QMessageBox.critical(ui, "Ошибка", f"Не удалось остановить {service_name} на сервере {server}.\n{e}")


def start_selected(ui):
    """Запуск выделенных служб или веб-сервисов IIS."""
    selected_rows = ui.table.selectionModel().selectedRows()
    if not selected_rows:
        QMessageBox.information(ui, "Информация", "Пожалуйста, выберите хотя бы одну строку для запуска.")
        return

    for row in selected_rows:
        service_type = ui.table.item(row.row(), 2).text()  # Тип службы (например, IIS)
        service_name = ui.table.item(row.row(), 3).text()  # Имя службы
        server = ui.table.item(row.row(), 0).text()  # Сервер

        try:
            if service_type.lower() == "iis":
                # PowerShell-скрипт для запуска IIS
                ps_script = f"""
                Invoke-Command -ComputerName {server} -ScriptBlock {{
                    Import-Module WebAdministration
                    Start-WebAppPool -Name {service_name}
                }}
                """
                subprocess.run(["powershell", "-Command", ps_script], check=True)
                QMessageBox.information(ui, "Успех", f"Веб-сервис {service_name} на сервере {server} успешно запущен.")
            else:
                # Запуск обычной службы
                ps_script = f"Start-Service -Name {service_name} -ComputerName {server}"
                subprocess.run(["powershell", "-Command", ps_script], check=True)
                QMessageBox.information(ui, "Успех", f"Служба {service_name} на сервере {server} успешно запущена.")
        except Exception as e:
            QMessageBox.critical(ui, "Ошибка", f"Не удалось запустить {service_name} на сервере {server}.\n{e}")

def show_network_results(ui):
    """Сбор сетевой информации для выбранных строк."""
    selected_rows = ui.table.selectionModel().selectedRows()
    if not selected_rows:
        QMessageBox.information(ui, "Информация", "Пожалуйста, выберите хотя бы одну строку для сбора сетевой информации.")
        return

    try:
        if ui.demo_mode_checkbox.isChecked():
        # Используем моковые данные
            network_data = generate_mock_network_connections()
        else:
            network_data = []
            for row in selected_rows:
                server = ui.table.item(row.row(), 0).text()
                process_id = ui.table.item(row.row(), 6).text()

                ps_script = f"""
                $p_id = {process_id}
                $server = "{server}"
                Invoke-Command -ComputerName $server -ScriptBlock {{
                    Get-NetTCPConnection -OwningProcess $using:p_id |
                    Select-Object State, LocalAddress, @{{
                        Name='LocalHostName'; Expression={{ (Resolve-DnsName $_.LocalAddress).NameHost }}
                    }}, LocalPort, RemoteAddress, @{{
                        Name='RemoteHostName'; Expression={{ (Resolve-DnsName $_.RemoteAddress).NameHost }}
                    }}, RemotePort |
                    Sort-Object State, LocalAddress
                }} | ConvertTo-Json -Depth 3
                """

                process = subprocess.run(
                    ["powershell", "-Command", ps_script],
                    capture_output=True,
                    text=True,
                    encoding="utf-8"
                )

                if process.returncode != 0:
                    raise RuntimeError(f"Ошибка выполнения PowerShell на сервере {server}: {process.stderr.strip()}")

                stdout = process.stdout.strip()
                if stdout:
                    row_data = json.loads(stdout)
                    if isinstance(row_data, dict):  # Если вернулся одиночный объект
                        row_data = [row_data]
                    network_data.extend(row_data)

        from network_info_window import NetworkInfoWindow  # Импортируем окно сетевой информации
        ui.network_window = NetworkInfoWindow(network_data, ui)
        ui.network_window.exec_()
    except Exception as e:
        QMessageBox.critical(ui, "Ошибка", f"Ошибка сбора сетевой информации: {e}")


def open_zabbix(ui):
    """Открытие панели Zabbix."""
    QMessageBox.information(ui, "Информация", "Функция открытия Zabbix пока не реализована.")


def update_stats(ui):
    """Обновление статистики таблицы."""
    total_rows = ui.table.rowCount()
    selected_rows = len(ui.table.selectionModel().selectedRows())
    visible_rows = sum(not ui.table.isRowHidden(row) for row in range(total_rows))
    ui.stats_label.setText(
        f"Выделено строк: {selected_rows} / Всего строк: {total_rows} / Видимых строк: {visible_rows}"
    )


def on_selection_changed(ui):
    """Обновление статистики при изменении выделения."""
    update_stats(ui)
