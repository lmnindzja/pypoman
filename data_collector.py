import subprocess
import json
import logging
from datetime import datetime
import re

# Настройка логирования
logging.basicConfig(
    filename="data_collector.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


def parse_powershell_datetime(value):
    """
    Преобразует значение PowerShell даты (/Date(timestamp)/) в человекочитаемый формат.
    :param value: Строка формата /Date(timestamp)/ или None.
    :return: Преобразованная дата в виде строки или "None".
    """
    if not value or not isinstance(value, str):
        return "None"

    match = re.match(r"/Date\((\d+)\)/", value)
    if match:
        timestamp = int(match.group(1)) // 1000  # Конвертируем миллисекунды в секунды
        return datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

    return value


def collect_server_data(mask):
    """
    Собирает данные с серверов по заданной маске.

    :param mask: Маска имени хоста для поиска серверов.
    :return: Список словарей с данными для заполнения таблицы.
    """
    logging.info(f"Начало сбора данных с серверами для маски: {mask}")
    try:
        # PowerShell-скрипт
        ps_script = f"""
        [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
        $results = @()
        $servers = (Get-ADComputer -Filter "Name -like '*{mask}*'").Name

        $results = Invoke-Command -ComputerName $servers -ScriptBlock {{

            # Получить информацию о веб-сервисах на хосте
            Get-Website | Where-Object {{ $_.Name -ne "Default Web Site" }} | 
            Select-Object @{{Name="Name"; Expression={{$_.Name}}}}, State,
                @{{
                    Name="User"; Expression={{(Get-ItemProperty "IIS:\\AppPools\\$($_.ApplicationPool)").ProcessModel.UserName}}
                }},
                @{{
                    Name="Port"; Expression={{$_.Bindings.Collection.BindingInformation}}
                }},
                @{{
                    Name="Type"; Expression={{'IIS'}}
                }},
                @{{
                    Name="Version"; Expression={{if (Test-Path -Path "C:\\$($_.Name)\\Version.txt" -PathType Leaf) {{
                        Get-Content "C:\\$($_.Name)\\Version.txt" -Raw
                    }}}}
                }},
                @{{
                    Name="LastBootTime"; Expression={{(Get-CimInstance -ClassName Win32_OperatingSystem).LastBootUpTime}}
                }}

            # Получить информацию о сервисах
            Get-WmiObject Win32_Service  | 
            Select-Object Name, State,
                @{{
                    Name="Port";Expression={{if ($_.ProcessId ) {{Get-NetTCPConnection -OwningProcess $_.ProcessId | Select-Object -ExpandProperty LocalPort -Unique}} 
                    else {{
                            ""
                        }}
                    }}                
                }},

                @{{
                    Name="Type";Expression={{'WS'}}
                    }},
                @{{
                    Name="Version";Expression={{if (Test-Path -Path C:\\$($_.Name)\\Version.txt -PathType Leaf) {{Get-Content C:\\$($_.Name)\\Version.txt -Raw}}
                       else {{
                            ""
                        }}
                    }}
                }},    
                @{{
                    Name="PID"; Expression={{$_.ProcessId}}
                }},
                @{{
                    Name="User"; Expression={{$_.StartName}}
                }},
                @{{
                    Name="StartTime"; Expression={{if ($_.State -eq 'Running') {{(Get-CimInstance Win32_Process -Filter "ProcessId=$($_.ProcessId)").CreationDate}}
                       else {{
                            ""
                        }}                    
                    }}
                }},
                @{{
                    Name="RMQConnCount"; Expression={{((Get-NetTCPConnection -OwningProcess $_.ProcessId | Where-Object {{$_.RemotePort -eq 5672}}).Count)}}
                }}
        }} | Select-Object PSComputerName, Port, Type, Name, Version, State, PID, User, StartTime, LastBootTime, RMQConnCount

        $results | ConvertTo-Json -Depth 3
        """

        logging.debug("PowerShell-скрипт для выполнения:\n" + ps_script)

        # Запуск PowerShell с явной кодировкой UTF-8
        process = subprocess.run(
            ["powershell", "-Command", ps_script],
            capture_output=True,
            text=True,  # Принудительно задаём текстовый вывод
            encoding="cp1251"  # Используем UTF-8
        )

        # Логирование stdout и stderr
        logging.debug(f"STDOUT: {process.stdout}")
        logging.debug(f"STDERR: {process.stderr}")

        # Проверка на ошибки
        if process.returncode != 0:
            error_message = f"PowerShell завершился с ошибкой: {process.stderr.strip()}"
            logging.error(error_message)
            raise RuntimeError(error_message)

        if not process.stdout.strip():
            error_message = "PowerShell вернул пустой результат. Проверьте скрипт."
            logging.warning(error_message)
            raise RuntimeError(error_message)

        # Парсинг JSON
        try:
            server_data = json.loads(process.stdout)

            # Если PowerShell возвращает одиночный объект, преобразуем его в список
            if isinstance(server_data, dict):
                server_data = [server_data]

            logging.info("Сбор данных завершён успешно.")
            return server_data
        except json.JSONDecodeError as e:
            logging.error(f"Ошибка парсинга JSON: {e}")
            raise RuntimeError("Получен некорректный JSON.")

    except Exception as e:
        logging.error(f"Ошибка сбора данных: {e}")
        return []

import subprocess


def get_iis_state(server, pool_name):
    """Получение состояния пула приложений IIS."""
    try:
        ps_script = f"""
        Invoke-Command -ComputerName {server} -ScriptBlock {{
            Import-Module WebAdministration
            (Get-WebAppPoolState -Name '{pool_name}').Value
        }}
        """
        result = subprocess.run(
            ["powershell", "-Command", ps_script],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"Error: {result.stderr.strip()}"
    except Exception as e:
        return f"Error: {e}"
