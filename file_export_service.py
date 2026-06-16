"""
File Export Service — lets users download previously generated report files.
"""

import os
import logging

logger = logging.getLogger(__name__)

EXPORT_ROOT = "/var/app/exports"


class FileExportService:

    def __init__(self, export_root=EXPORT_ROOT):
        self.export_root = export_root

    def list_exports(self):
        return sorted(os.listdir(self.export_root))

    def get_export(self, filename):
        """Return the contents of an export file by name."""
        path = os.path.join(self.export_root, filename)
        with open(path, "rb") as f:
            return f.read()

    def export_size(self, filename):
        path = os.path.join(self.export_root, filename)
        return os.path.getsize(path)
