# The MIT License (MIT)
#
# Copyright (c) 2018 Dan Halbert for Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`adafruit_ble.uart_server`
====================================================

UART-style communication: Peripheral acting as a GATT Server.

* Author(s): Dan Halbert for Adafruit Industries

"""
from bleio import Characteristic, Service, Peripheral
from .advertising import ServerAdvertisement
from .uart import UART

class UARTServer(UART):
    """
    Provide UART-like functionality via the Nordic NUS service.

    :param int timeout:  the timeout in seconds to wait
      for the first character and between subsequent characters.
    :param int buffer_size: buffer up to this many bytes.
      If more bytes are received, older bytes will be discarded.
    :param str name: Name to advertise for server. If None, use default Peripheral name.

    Example::

        from adafruit_ble.uart_server import UARTServer
        uart = UARTServer()
        uart.start_advertising()

        # Wait for a connection.
        while not uart.connected:
            pass

        uart.write('abc')
    """

    def __init__(self, *, timeout=1.0, buffer_size=64, name=None):
        read_char = Characteristic(UART.NUS_RX_CHAR_UUID, write=True, write_no_response=True)
        write_char = Characteristic(UART.NUS_TX_CHAR_UUID, notify=True)
        super().__init__(read_characteristic=read_char, write_characteristic=write_char,
                         timeout=timeout, buffer_size=buffer_size)

        nus_uart_service = Service(UART.NUS_SERVICE_UUID, (read_char, write_char))

        self._periph = Peripheral((nus_uart_service,), name=name)
        self._advertisement = ServerAdvertisement(self._periph)

    def start_advertising(self):
        """Start advertising the service. When a client connects, advertising will stop.
        When the client disconnects, restart advertising by calling ``start_advertising()`` again.
        """
        self._periph.start_advertising(self._advertisement.advertising_data_bytes,
                                       scan_response=self._advertisement.scan_response_bytes)

    def stop_advertising(self):
        """Stop advertising the service."""
        self._periph.stop_advertising()

    @property
    def connected(self):
        """True if someone connected to the server."""
        return self._periph.connected
