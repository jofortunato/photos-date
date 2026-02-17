# Photo Date Fixer 📸

A Python utility to synchronize image EXIF metadata with the dates found in their filenames. 

This tool is designed for situations where moving photos between external hard drives or different operating systems has caused the "Date Created" metadata to reset to the transfer date, breaking chronological sorting in apps like Google Photos, Windows Gallery, or Apple Photos.

## Features

- **Smart Filename Parsing:** Extracts dates from filenames using patterns like `YYYYMMDD`, `YYYY-MM-DD`, or `YYYY_MM_DD`.
- **Validation Engine:** Prevents "false positives" (like random numbers in social media files) by validating that the numbers form a real calendar date.
- **Year Range Guard:** Only processes years between 1980 and the current year to ensure data integrity.
- **Extensive Comparison:** Option to identify mismatches based on Year only or a full Year/Month/Day check.
- **OS Timestamp Sync:** Optionally updates the file system "Date Modified" (`os.utime`) to match the new EXIF date.
- **Format Safety:** Automatically skips PNGs and non-image files to prevent metadata corruption.

## Installation

1. Clone the repository:
   ```bash
   git clone [https://github.com/jofortunato/photos-date.git](https://github.com/jofortunato/photos-date.git)
   cd photos-date

2. Install the required exif library:

    ```bash
    pip install exif

## Usage
1. Scan for Mismatches (Dry Run)
Identify files where the metadata date is newer than the date in the filename (or missing entirely):

    ```bash
    python photos-date-check.py /path/to/photos --extensive

2. Fix Metadata and Timestamps
Apply the filename date to the internal EXIF and the file system:

    ```bash
    python main.py /path/to/photos --extensive --fix

3. Reset Incorrectly Tagged Files
If files were previously tagged with "impossible" dates (e.g., years like 1476), use the reset utility to remove the DateTimeOriginal tag:

    ```bash
    python reset.py /path/to/photos --execute