from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any


class AnycubicError(Exception):
    def __init__(self, message: str, error_type: int) -> None:
        self.type = error_type
        super().__init__(message)


@dataclass
class AnycubicPrinter:
    ip: str
    port: int

    async def _send_message(self, message: str) -> str:
        """Connect to the printer and send a single command over socket"""
        future = asyncio.open_connection(self.ip, self.port)
        reader, writer = await asyncio.wait_for(future, timeout=10)
        writer.write(message.encode())
        data = ''
        try:
            while True:
                if not (line := await reader.read(10)):
                    break
                data += line.decode()
                if data.endswith(',end'):
                    break
        finally:
            writer.write_eof()
            writer.close()
            await writer.wait_closed()
        return data

    async def send_cmd(self, *commands: str, flatten: bool = True) -> str | list[str]:
        """Send a command to the Printer."""
        data = await self._send_message(','.join(commands) + ',')
        response = data.split(',')[len(commands):-1]
        if response and response[0].startswith('ERROR'):
            raise AnycubicError(f'Failed to run command "{",".join(commands)}" ({response[0]})', int(response[0][5]))
        if flatten is True and len(response) == 1:
            response = response[0]
        return response

    async def get_status(self) -> dict[str, Any]:
        code, *extra = await self.send_cmd('getstatus', flatten=False)
        response = {'code': code}
        if code in ("print", "pause"):
            response['name'], response['number'] = extra[0].split('/', 1)
        return response

    async def get_wifi(self) -> str:
        """get WiFi name."""
        wifi_name: str = await self.send_cmd('getwifi')
        return wifi_name.encode('gbk').decode('utf8')  # printer uses GBK

    async def get_name(self) -> str:
        name: str = await self.send_cmd('getname')
        return name.encode('gbk').decode('utf8')  # printer uses GBK

    async def set_name(self, name: str) -> bool:
        """Set the printer name"""
        try:
            await self.send_cmd("setname", name.encode("utf8").decode("gbk"))
            return True
        except AnycubicError:
            return False

    async def get_mode(self) -> int:
        return int(await self.send_cmd('getmode'))

    async def get_history(self):
        try:
            return await self.send_cmd('gethistory')
        except AnycubicError as e:
            if e.type == 2:
                print('No history')
        return None

    async def get_sys_info(self) -> dict[str, str]:
        model, version, identifier, wifi = await self.send_cmd('getsysinfo')
        return {'model': model, 'firmware_version': version, 'identifier': identifier, 'wifi_ssid': wifi}
