# YouTube2Sheets Column Mapping Reference

**Last Updated:** September 30, 2025  
**Version:** 2.0 (Updated for full Google Sheets compatibility)

## Column Structure (12 Columns)

| Column # | Header | Data Type | Description | Source |
|----------|--------|-----------|-------------|--------|
| **A (1)** | ChannelID | Text | YouTube channel unique identifier | `snippet.channelId` |
| **B (2)** | YT Channel | Text | Channel display name | `snippet.channelTitle` |
| **C (3)** | Date of Video | Date | Video publish date (YYYY-MM-DD) | `snippet.publishedAt` |
| **D (4)** | Short_Long | Text | "Short" (< 60s) or "Long" (≥ 60s) | Calculated from duration |
| **E (5)** | Video Length | Duration | Formatted duration (HH:MM:SS or MM:SS) | `contentDetails.duration` |
| **F (6)** | Video Title | Text | Full video title | `snippet.title` |
| **G (7)** | Video Link | URL | YouTube watch URL | Constructed from video ID |
| **H (8)** | Views | Number | View count (formatted with commas) | `statistics.viewCount` |
| **I (9)** | Likes | Number | Like count or "N/A" if disabled | `statistics.likeCount` |
| **J (10)** | Comments | Number | Comment count or "0" if disabled | `statistics.commentCount` |
| **K (11)** | NotebookLM | Checkbox | Default unchecked checkbox (☐) | Static default |
| **L (12)** | Date Added | DateTime | Timestamp when row was added | Auto-generated (YYYY-MM-DD HH:MM) |

## Sample Data Row

```
UCBJycsmduvYEL83R_U4JriQ | Marques Brownlee | 2025-09-26 | Long | 12:22 | iPhone 17 Pro Review: Paradox in a Box! | https://www.youtube.com/watch?v=q0aFOxT6TNw | 4,149,875 | 115,713 | 4,688 | ☐ | 2025-09-30 15:18
```

## Data Formatting Rules

### Numbers
- **Views:** Comma-separated (e.g., `1,234,567`)
- **Likes:** Comma-separated or `N/A` if creator disabled likes
- **Comments:** Plain number or `0` if comments disabled

### Dates
- **Date of Video:** `YYYY-MM-DD` format
- **Date Added:** `YYYY-MM-DD HH:MM` format

### Duration
- **Under 1 hour:** `MM:SS` (e.g., `12:22`)
- **Over 1 hour:** `H:MM:SS` (e.g., `1:30:45`)

### Type Classification
- **Short:** Videos under 60 seconds
- **Long:** Videos 60 seconds or longer

## API Mapping

### YouTube Data API v3

**Search Endpoint (`search().list`):**
- Used to find videos in a channel
- Returns: `snippet` only

**Videos Endpoint (`videos().list`):**
- Used to fetch full video details
- Returns: `snippet`, `statistics`, `contentDetails`

### Field Mapping

| Sheet Column | API Field | Endpoint |
|--------------|-----------|----------|
| ChannelID | `snippet.channelId` | videos().list |
| YT Channel | `snippet.channelTitle` | videos().list |
| Date of Video | `snippet.publishedAt` | videos().list |
| Video Title | `snippet.title` | videos().list |
| Video Length | `contentDetails.duration` | videos().list |
| Views | `statistics.viewCount` | videos().list |
| Likes | `statistics.likeCount` | videos().list |
| Comments | `statistics.commentCount` | videos().list |

## Version History

### v2.0 (2025-09-30)
- ✅ Added `ChannelID` column (Column A)
- ✅ Added `Comments` column (Column J)
- ✅ Added `Date Added` column (Column L)
- ✅ Renamed "Likes_Dislikes" to "Likes" (YouTube removed dislikes)
- ✅ Total columns: 9 → 12

### v1.0 (Initial)
- Original 9-column structure
- Missing ChannelID, Comments, Date Added
