# 📊 Column Requirements and Conditional Formatting Specification

**Document Version:** 1.0  
**Last Updated:** September 11, 2025  
**Author:** The Loremaster - PolyChronos Guild  
**Status:** ✅ **COMPLETE & CURRENT**

---

## 🎯 Executive Summary

This document provides the definitive specification for all column requirements and conditional formatting rules in the YouTube2Sheets system. It serves as the single source of truth for developers, testers, and users to understand the complete data structure and visual formatting applied to Google Sheets.

---

## 📋 Complete Column Specification

### **Column Structure (A-K)**

| Column | Header | Data Type | Description | Source |
|--------|--------|-----------|-------------|---------|
| **A** | YT Channel | String | YouTube channel name/title | `channel_title` |
| **B** | Date of Video | DateTime | Video publication date (YYYY-MM-DD format) | `published_at` |
| **C** | Short_Long | String | Video duration category ("Short" or "Long") | Calculated from `duration_seconds` |
| **D** | Video Length | String | Human-readable duration (e.g., "5:30", "1h 23m") | Calculated from `duration_seconds` |
| **E** | Video Title | String | YouTube video title | `title` |
| **F** | Video Link | URL | Direct YouTube video URL | `url` |
| **G** | Views | Integer | View count (formatted as string) | `view_count` |
| **H** | Likes | Integer | Like count (formatted as string) | `like_count` |
| **I** | Comments | Integer | Comment count (formatted as string) | `comment_count` |
| **J** | NotebookLM | Boolean | Checkbox for NotebookLM processing | Default: `FALSE` |
| **K** | Date Added | DateTime | When video was added to sheet | Current timestamp |

### **Data Processing Rules**

- **Short_Long Logic**: Videos < 60 seconds = "Short", ≥ 60 seconds = "Long"
- **Duration Format**: 
  - < 1 hour: "MM:SS" (e.g., "5:30")
  - ≥ 1 hour: "Hh MMm SSs" (e.g., "1h 23m 45s")
- **Date Format**: YYYY-MM-DD format (e.g., "2024-07-09")
- **Numeric Values**: Stored as strings for Google Sheets compatibility

---

## 🔍 Keyword Filtering System

### **Filter Configuration**

The YouTube2Sheets system supports advanced keyword filtering with the following specifications:

#### **Filter Types**
- **Include Mode**: Videos must contain ALL specified keywords (AND logic)
- **Exclude Mode**: Videos containing ANY specified keywords are filtered out (OR logic)

#### **Keyword Format**
- **Comma-Separated**: Multiple keywords separated by commas
- **Case-Insensitive**: All matching is performed in lowercase
- **Phrase Support**: Keywords can be single words or phrases
- **Whitespace Handling**: Leading/trailing whitespace is automatically trimmed

#### **Example Configurations**
```python
# Include videos with both "Godly" and "Josh"
FilterConfig(
    keyword_filter="Godly, Josh",
    keyword_filter_mode="include"
)

# Exclude videos with "politics" or "news"
FilterConfig(
    keyword_filter="politics, news",
    keyword_filter_mode="exclude"
)
```

#### **Search Scope**
Keywords are searched in:
- **Video Title**: Primary search field
- **Video Description**: Secondary search field
- **Combined Text**: Title + Description for comprehensive matching

#### **Filtering Logic**
```python
# Include Mode (AND logic)
if filter_config.keyword_filter_mode == 'include':
    matched_keywords = [kw for kw in keywords if kw in text]
    if len(matched_keywords) != len(keywords):
        return None  # Filter out video

# Exclude Mode (OR logic)  
elif filter_config.keyword_filter_mode == 'exclude':
    matched_keywords = [kw for kw in keywords if kw in text]
    if matched_keywords:
        return None  # Filter out video
```

#### **Performance Considerations**
- **Efficient Processing**: Keywords are parsed once per filter configuration
- **Early Exit**: Filtering stops at first non-matching keyword in include mode
- **Memory Efficient**: No intermediate storage of filtered results

---

## 🎨 Complete Conditional Formatting Specification

### **Rule 1: Date of Video (Column B) - Year-Based Colors**

| Year | Color | RGB Values | Condition |
|------|-------|------------|-----------|
| **2026** | Pink | `red: 1.0, green: 0.7, blue: 0.8` | `=YEAR($B2)=2026` |
| **2025** | Green | `red: 0.7, green: 1.0, blue: 0.7` | `=YEAR($B2)=2025` |
| **2024** | Purple | `red: 0.8, green: 0.7, blue: 1.0` | `=YEAR($B2)=2024` |
| **2023** | Orange | `red: 1.0, green: 0.8, blue: 0.4` | `=YEAR($B2)=2023` |

**Range:** `B2:B{num_videos + 2}`

### **Rule 2: Short_Long (Column C) - Duration Category Colors**

| Value | Color | RGB Values | Condition |
|-------|-------|------------|-----------|
| **Short** | Light Red/Pink | `red: 1.0, green: 0.8, blue: 0.8` | `Text is exactly 'Short'` |
| **Long** | Light Green | `red: 0.8, green: 1.0, blue: 0.8` | `Text is exactly 'Long'` |

**Range:** `C2:C{num_videos + 2}`

### **Rule 3: Video Length (Column D) - Based on Short_Long**

| Short_Long Value | Color | RGB Values | Condition |
|------------------|-------|------------|-----------|
| **Long** | Light Blue | `red: 0.9, green: 0.9, blue: 1.0` | `=$C2="Long"` |
| **Short** | Light Red/Pink | `red: 1.0, green: 0.8, blue: 0.8` | `=$C2="Short"` |

**Range:** `D2:D{num_videos + 2}`

### **Rule 4: Views (Column G) - High Views Highlight**

| Condition | Color | RGB Values | Condition |
|-----------|-------|------------|-----------|
| **High Views** | Light Blue | `red: 0.9, green: 0.9, blue: 1.0` | `Number greater than 10000` |

**Range:** `G2:G{num_videos + 2}`

### **Rule 5: Likes (Column H) - All Likes Highlighted**

| Condition | Color | RGB Values | Condition |
|-----------|-------|------------|-----------|
| **Any Likes** | Light Green + Bold | `red: 0.8, green: 1.0, blue: 0.8` | `Number greater than 0` |

**Range:** `H2:H{num_videos + 2}`

### **Rule 6: NotebookLM (Column J) - Checked Items**

| Condition | Color | RGB Values | Condition |
|-----------|-------|------------|-----------|
| **Checked** | Light Red + Bold | `red: 1.0, green: 0.8, blue: 0.8` | `=$J2=TRUE` |

**Range:** `J2:J{num_videos + 2}`

---

## 🔧 Implementation Details

### **Conditional Formatting Application Process**

1. **Header Row**: Row 1 contains headers with dark blue background
2. **Data Rows**: Rows 2+ contain video data with conditional formatting
3. **Range Calculation**: All ranges use `num_videos + 2` to account for header row
4. **Rule Order**: Rules are applied in sequence with proper indexing

### **Google Sheets API Requirements**

- **Condition Types**: `CUSTOM_FORMULA`, `TEXT_EQ`, `NUMBER_GREATER`
- **Format Properties**: `backgroundColor`, `textFormat`
- **Range Format**: `{"sheetId": sheet_id_num, "startRowIndex": 1, "endRowIndex": num_videos + 2, "startColumnIndex": X, "endColumnIndex": Y}`

### **Checkbox Formatting**

- **Column J (NotebookLM)**: Formatted as checkboxes
- **Default Value**: `FALSE` (unchecked)
- **Conditional Formatting**: Red background when `TRUE` (checked)

---

## 🧪 Testing Requirements

### **Column Data Validation**

- ✅ All 11 columns (A-K) present with correct headers
- ✅ Data types match specification
- ✅ Date formatting consistent (YYYY-MM-DD format)
- ✅ Duration formatting readable
- ✅ Numeric values properly formatted as strings

### **Conditional Formatting Validation**

- ✅ Date colors: 2026=Pink, 2025=Green, 2024=Purple, 2023=Orange
- ✅ Short_Long colors: Short=Red, Long=Green
- ✅ Video Length colors: Matches Short_Long values
- ✅ Views highlighting: Blue for >10k views
- ✅ Likes highlighting: Green for all likes
- ✅ NotebookLM highlighting: Red for checked items

### **Edge Cases**

- ✅ Empty cells: No formatting applied
- ✅ Invalid dates: No year-based formatting
- ✅ Zero values: Proper handling
- ✅ Large numbers: Proper display

---

## 📚 Related Documentation

- **DeltaReport_ColumnHeaders.md**: Column header implementation details
- **DeltaReport_ConditionalFormatting.md**: Conditional formatting implementation
- **DeltaReport_FilteringAndFormattingFixes.md**: Recent fixes and improvements
- **Architecture.md**: Overall system architecture
- **TestPlan.md**: Comprehensive testing strategy

---

## 🔄 Maintenance and Updates

### **Version Control**

- **v1.0**: Initial comprehensive specification
- **Future Updates**: Document all changes with version numbers
- **Change Log**: Maintain detailed change history

### **Review Process**

- **Monthly Review**: Verify all formatting rules still work
- **User Feedback**: Incorporate user-requested changes
- **Testing**: Validate all rules with sample data

---

## ✅ **Conclusion**

This document provides the complete, authoritative specification for all column requirements and conditional formatting in the YouTube2Sheets system. It serves as the single source of truth for developers, testers, and users to understand the complete data structure and visual formatting applied to Google Sheets.

**Status**: 🏆 **DOCUMENTATION COMPLETE** - All column requirements and conditional formatting rules fully specified

---

*This document serves as the definitive specification for all column requirements and conditional formatting in the YouTube2Sheets project. For any questions or updates, contact The Loremaster.*
