from __future__ import annotations

import asyncio
from collections import namedtuple
from dataclasses import dataclass
from datetime import timedelta
import logging
from typing import Any

_LOGGER = logging.getLogger(__name__)
# Not sure about `other`
PrinterSatus = namedtuple(
    'PrinterStatus',
    'file total_layers progress current_layer time_total time_remaining resin_label type resin layer_height other'
)


class AnycubicError(Exception):
    def __init__(self, message: str, error_type: int) -> None:
        self.type = error_type
        super().__init__(message)


@dataclass
class AnycubicPrinter:
    ip: str
    port: int

    async def _send_message(self, message: str) -> bytes:
        """Connect to the printer and send a single command over socket"""
        future = asyncio.open_connection(self.ip, self.port)
        reader, writer = await asyncio.wait_for(future, timeout=10)
        writer.write(message.encode())
        data = b''
        try:
            while True:
                data += await asyncio.wait_for(reader.read(8192), timeout=1.0)
                if data.endswith(b',end'):
                    break
        except asyncio.TimeoutError:
            # Reading preview will simply time out as it does not terminate with `,end` like others
            pass
        finally:
            writer.close()
            await writer.wait_closed()
        return data

    async def send_cmd(self, *commands: str, flatten: bool = True) -> str | list[bytes]:
        """Send a command to the Printer."""
        data = await self._send_message(','.join(commands) + ',')
        response = data.split(b',')[len(commands):-1]
        if response and response[0].startswith(b'ERROR'):
            error_type = int(response[0][5]) if len(response[0]) == 6 else 0
            raise AnycubicError(f'Failed to run command "{",".join(commands)}" ({response[0]})', error_type)
        if flatten is True and len(response) == 1:
            response = response[0]
        return response

    async def get_status(self) -> dict[str, Any]:
        code, *extra = await self.send_cmd('getstatus', flatten=False)
        response = {'code': code}
        if code in ("print", "pause"):
            status = PrinterSatus(*extra)
            response['file_name'], response['file_number'] = status.file.split('/', 1)
            _LOGGER.debug(f'{status}')
            response.update(
                progress=int(status.progress),
                current_layer=int(status.current_layer),
                total_layers=int(status.total_layers),
                time_total=str(timedelta(seconds=status.time_total)),
                time_remaining=str(timedelta(seconds=status.time_remaining)),
                resin=f'{status.resin}mL',
                type=status.type,
                layer_height=float(status.layer_height)
            )
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

    async def get_files(self) -> list[tuple[str, str]]:
        try:
            files = await self.send_cmd('getfile', flatten=False)
            return [tuple(f.split('/')) for f in files]  # type: ignore
        except AnycubicError as e:
            if e.type == 2:
                print('No files')
        return []

    async def get_params(self) -> list[str]:
        """
        Not sure what these mean yet.
        ['6', '0.5', '25.0', '1.7', '6.0', '4.0', '6.0', '8']
        """
        return await self.send_cmd('getpara')

    async def get_preview(self, file_name: str) -> bytes:
        """
        Binary data for preview.
        TODO: Haven't figured out how to process it
        """
        return await self._send_message(f'getPreview2,{file_name},')

    async def get_sys_info(self) -> dict[str, str]:
        """Get printer system information"""
        model, version, identifier, wifi = await self.send_cmd('getsysinfo')
        return {'model': model, 'firmware_version': version, 'identifier': identifier, 'wifi_ssid': wifi}
