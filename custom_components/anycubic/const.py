"""Constants for integration."""
DOMAIN = "anycubic"
DEFAULT_PORT = 6000
DEFAULT_NAME = "Anycubic Printer"

STATUS_PRINTING = "print"
STATUS_FINISHED = "finish"
STATUS_STOP = "stop"
STATUS_PAUSED = "pause"

STATUS_LABELS = {
    STATUS_PRINTING: "Printing",
    STATUS_FINISHED: "Finished",
    STATUS_STOP: "Stopped",
    STATUS_PAUSED: "Paused",
}

COMMAND_PRINT = "print"
COMMAND_PAUSE = "pause"
COMMAND_STOP = "stop"
COMMAND_RESUME = "resume"

EXPOSED_COMMANDS = (COMMAND_PRINT, COMMAND_PAUSE, COMMAND_RESUME, COMMAND_STOP)

CONF_PRINT_FILE_NAME = "file_name"
CONF_PRINT_CMD = "command"

SERVICE_SET_PRINTER_NAME = "set_printer_name"
SERVICE_SEND_COMMAND = "send_command"
