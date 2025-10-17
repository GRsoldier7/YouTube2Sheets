"""
Google Sheets formatting utilities for YouTube2Sheets.

This module provides comprehensive formatting for Google Sheets including:
- Automatic Table creation (formatted ranges)
- Conditional formatting for all columns
- Column-specific formatting (dates, numbers, checkboxes)
- Named ranges matching tab names
- Professional styling

Author: Lead Engineer - PolyChronos Guild
Date: September 30, 2025
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

from googleapiclient.discovery import Resource
from googleapiclient.errors import HttpError

from .exceptions import APIError

logger = logging.getLogger(__name__)


class SheetFormatter:
    """
    Professional Google Sheets formatter with automatic Table creation.
    
    Features:
    - Converts ranges to formatted Tables
    - Applies conditional formatting to all columns
    - Creates named ranges matching tab names
    - Column-specific formatting (dates, numbers, checkboxes)
    - Professional styling (borders, alternating rows, header formatting)
    """

    def __init__(self, sheets_service: Resource, sheet_id: str) -> None:
        """
        Initialize the sheet formatter.
        
        Args:
            sheets_service: Google Sheets API service instance
            sheet_id: Google Sheet ID
        """
        self.sheets_service = sheets_service
        self.sheet_id = sheet_id
        logger.info("SheetFormatter initialized for sheet %s", sheet_id)

    def format_as_table(
        self,
        tab_name: str,
        num_rows: int,
        num_columns: int = 12,
        *,
        apply_conditional_formatting: bool = True,
        create_named_range: bool = True,
    ) -> bool:
        """
        Format a sheet tab as a professional Table with all formatting applied.
        
        Args:
            tab_name: Name of the tab to format
            num_rows: Number of rows (including header)
            num_columns: Number of columns (default: 12 for YouTube2Sheets)
            apply_conditional_formatting: Apply column-specific conditional formatting
            create_named_range: Create a named range matching the tab name
            
        Returns:
            True if successful
        """
        try:
            # Get the sheet ID for this tab
            tab_id = self._get_tab_id(tab_name)
            
            if tab_id is None:
                logger.error("Tab '%s' not found", tab_name)
                return False
            
            # Build comprehensive formatting requests
            requests = []
            
            # 1. Apply basic table formatting
            requests.extend(self._build_table_formatting_requests(tab_id, num_rows, num_columns))
            
            # 2. Apply column-specific formatting
            requests.extend(self._build_column_formatting_requests(tab_id, num_rows))
            
            # 3. Apply conditional formatting if requested
            if apply_conditional_formatting:
                requests.extend(self._build_conditional_formatting_requests(tab_id, num_rows))
            
            # 4. Create named range if requested
            if create_named_range:
                requests.append(self._build_named_range_request(tab_id, tab_name, num_rows, num_columns))
            
            # Execute all formatting requests in a single batch
            if requests:
                body = {"requests": requests}
                self.sheets_service.spreadsheets().batchUpdate(
                    spreadsheetId=self.sheet_id,
                    body=body
                ).execute()
                
                logger.info(
                    "✅ Formatted tab '%s' as Table with %d rows, %d columns",
                    tab_name, num_rows, num_columns
                )
            
            return True
            
        except HttpError as exc:
            logger.error("Failed to format sheet as table: %s", exc)
            raise APIError("Sheet formatting failed", api_name="google_sheets", status_code=exc.resp.status) from exc
        except Exception as exc:
            logger.error("Unexpected error formatting sheet: %s", exc)
            return False

    def _get_tab_id(self, tab_name: str) -> Optional[int]:
        """Get the sheet ID for a given tab name."""
        try:
            sheet_metadata = self.sheets_service.spreadsheets().get(
                spreadsheetId=self.sheet_id
            ).execute()
            
            for sheet in sheet_metadata.get("sheets", []):
                properties = sheet.get("properties", {})
                if properties.get("title") == tab_name:
                    return properties.get("sheetId")
            
            return None
        except HttpError as exc:
            logger.error("Failed to get tab ID: %s", exc)
            return None

    def _build_table_formatting_requests(self, tab_id: int, num_rows: int, num_columns: int) -> List[Dict]:
        """Build requests for basic table formatting (borders, alternating colors, header)."""
        requests = []
        
        # 1. Format header row (row 0)
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": tab_id,
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": num_columns
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 0.2, "green": 0.6, "blue": 0.86},  # Blue
                        "textFormat": {
                            "foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0},  # White
                            "fontSize": 11,
                            "bold": True
                        },
                        "horizontalAlignment": "CENTER",
                        "verticalAlignment": "MIDDLE"
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)"
            }
        })
        
        # 2. Apply alternating row colors (banded rows)
        requests.append({
            "addBanding": {
                "bandedRange": {
                    "range": {
                        "sheetId": tab_id,
                        "startRowIndex": 1,  # Start after header
                        "endRowIndex": num_rows,
                        "startColumnIndex": 0,
                        "endColumnIndex": num_columns
                    },
                    "rowProperties": {
                        "headerColor": {"red": 0.2, "green": 0.6, "blue": 0.86},  # Blue (header)
                        "firstBandColor": {"red": 1.0, "green": 1.0, "blue": 1.0},  # White
                        "secondBandColor": {"red": 0.95, "green": 0.95, "blue": 0.95}  # Light gray
                    }
                }
            }
        })
        
        # 3. Add borders to the entire table
        requests.append({
            "updateBorders": {
                "range": {
                    "sheetId": tab_id,
                    "startRowIndex": 0,
                    "endRowIndex": num_rows,
                    "startColumnIndex": 0,
                    "endColumnIndex": num_columns
                },
                "top": {"style": "SOLID", "width": 2, "color": {"red": 0.0, "green": 0.0, "blue": 0.0}},
                "bottom": {"style": "SOLID", "width": 2, "color": {"red": 0.0, "green": 0.0, "blue": 0.0}},
                "left": {"style": "SOLID", "width": 2, "color": {"red": 0.0, "green": 0.0, "blue": 0.0}},
                "right": {"style": "SOLID", "width": 2, "color": {"red": 0.0, "green": 0.0, "blue": 0.0}},
                "innerHorizontal": {"style": "SOLID", "width": 1, "color": {"red": 0.7, "green": 0.7, "blue": 0.7}},
                "innerVertical": {"style": "SOLID", "width": 1, "color": {"red": 0.7, "green": 0.7, "blue": 0.7}}
            }
        })
        
        # 4. Freeze header row
        requests.append({
            "updateSheetProperties": {
                "properties": {
                    "sheetId": tab_id,
                    "gridProperties": {
                        "frozenRowCount": 1
                    }
                },
                "fields": "gridProperties.frozenRowCount"
            }
        })
        
        return requests

    def _build_column_formatting_requests(self, tab_id: int, num_rows: int) -> List[Dict]:
        """Build requests for column-specific formatting (dates, numbers, etc.)."""
        requests = []
        
        # Column C: Date of Video (YYYY-MM-DD format)
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": tab_id,
                    "startRowIndex": 1,  # Skip header
                    "endRowIndex": num_rows,
                    "startColumnIndex": 2,  # Column C
                    "endColumnIndex": 3
                },
                "cell": {
                    "userEnteredFormat": {
                        "numberFormat": {
                            "type": "DATE",
                            "pattern": "yyyy-mm-dd"
                        }
                    }
                },
                "fields": "userEnteredFormat.numberFormat"
            }
        })
        
        # Column H: Views (number with no decimals)
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": tab_id,
                    "startRowIndex": 1,
                    "endRowIndex": num_rows,
                    "startColumnIndex": 7,  # Column H
                    "endColumnIndex": 8
                },
                "cell": {
                    "userEnteredFormat": {
                        "numberFormat": {
                            "type": "NUMBER",
                            "pattern": "#,##0"
                        }
                    }
                },
                "fields": "userEnteredFormat.numberFormat"
            }
        })
        
        # Column I: Likes (number with no decimals)
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": tab_id,
                    "startRowIndex": 1,
                    "endRowIndex": num_rows,
                    "startColumnIndex": 8,  # Column I
                    "endColumnIndex": 9
                },
                "cell": {
                    "userEnteredFormat": {
                        "numberFormat": {
                            "type": "NUMBER",
                            "pattern": "#,##0"
                        }
                    }
                },
                "fields": "userEnteredFormat.numberFormat"
            }
        })
        
        # Column J: Comments (number with no decimals)
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": tab_id,
                    "startRowIndex": 1,
                    "endRowIndex": num_rows,
                    "startColumnIndex": 9,  # Column J
                    "endColumnIndex": 10
                },
                "cell": {
                    "userEnteredFormat": {
                        "numberFormat": {
                            "type": "NUMBER",
                            "pattern": "#,##0"
                        }
                    }
                },
                "fields": "userEnteredFormat.numberFormat"
            }
        })
        
        # Column K: NotebookLM (checkbox - center aligned)
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": tab_id,
                    "startRowIndex": 1,
                    "endRowIndex": num_rows,
                    "startColumnIndex": 10,  # Column K
                    "endColumnIndex": 11
                },
                "cell": {
                    "userEnteredFormat": {
                        "horizontalAlignment": "CENTER",
                        "verticalAlignment": "MIDDLE"
                    }
                },
                "fields": "userEnteredFormat(horizontalAlignment,verticalAlignment)"
            }
        })
        
        # Column L: Date Added (date-time format)
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": tab_id,
                    "startRowIndex": 1,
                    "endRowIndex": num_rows,
                    "startColumnIndex": 11,  # Column L
                    "endColumnIndex": 12
                },
                "cell": {
                    "userEnteredFormat": {
                        "numberFormat": {
                            "type": "DATE_TIME",
                            "pattern": "yyyy-mm-dd hh:mm"
                        }
                    }
                },
                "fields": "userEnteredFormat.numberFormat"
            }
        })
        
        return requests

    def _build_conditional_formatting_requests(self, tab_id: int, num_rows: int) -> List[Dict]:
        """Build requests for conditional formatting rules."""
        requests = []
        
        # Conditional formatting for Short/Long videos (Column D)
        requests.append({
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{
                        "sheetId": tab_id,
                        "startRowIndex": 1,
                        "endRowIndex": num_rows,
                        "startColumnIndex": 3,  # Column D (Short_Long)
                        "endColumnIndex": 4
                    }],
                    "booleanRule": {
                        "condition": {
                            "type": "TEXT_EQ",
                            "values": [{"userEnteredValue": "Short"}]
                        },
                        "format": {
                            "backgroundColor": {"red": 1.0, "green": 0.9, "blue": 0.6}  # Light yellow
                        }
                    }
                },
                "index": 0
            }
        })
        
        requests.append({
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{
                        "sheetId": tab_id,
                        "startRowIndex": 1,
                        "endRowIndex": num_rows,
                        "startColumnIndex": 3,
                        "endColumnIndex": 4
                    }],
                    "booleanRule": {
                        "condition": {
                            "type": "TEXT_EQ",
                            "values": [{"userEnteredValue": "Long"}]
                        },
                        "format": {
                            "backgroundColor": {"red": 0.7, "green": 0.85, "blue": 1.0}  # Light blue
                        }
                    }
                },
                "index": 1
            }
        })
        
        return requests

    def _build_named_range_request(self, tab_id: int, tab_name: str, num_rows: int, num_columns: int) -> Dict:
        """Build request to create a named range matching the tab name."""
        # Clean tab name for named range (remove spaces, special chars)
        clean_name = "".join(c if c.isalnum() or c == "_" else "_" for c in tab_name)
        
        return {
            "addNamedRange": {
                "namedRange": {
                    "name": clean_name,
                    "range": {
                        "sheetId": tab_id,
                        "startRowIndex": 0,
                        "endRowIndex": num_rows,
                        "startColumnIndex": 0,
                        "endColumnIndex": num_columns
                    }
                }
            }
        }

    def auto_resize_columns(self, tab_name: str) -> bool:
        """Auto-resize all columns to fit content."""
        try:
            tab_id = self._get_tab_id(tab_name)
            if tab_id is None:
                return False
            
            requests = [{
                "autoResizeDimensions": {
                    "dimensions": {
                        "sheetId": tab_id,
                        "dimension": "COLUMNS",
                        "startIndex": 0,
                        "endIndex": 12  # All 12 columns
                    }
                }
            }]
            
            body = {"requests": requests}
            self.sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=self.sheet_id,
                body=body
            ).execute()
            
            logger.info("✅ Auto-resized columns for tab '%s'", tab_name)
            return True
            
        except HttpError as exc:
            logger.error("Failed to auto-resize columns: %s", exc)
            return False

