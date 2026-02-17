import os
import re
from exif import Image
from datetime import datetime
import argparse

# Regex to find dates in filenames (supports YYYYMMDD, YYYY-MM-DD, YYYY_MM_DD)
DATE_PATTERN = re.compile(r'(\d{4})[-_]?(\d{2})[-_]?(\d{2})')

def is_valid_date(y, m, d):
    """Checks if the year, month, and day form a real calendar date."""
    try:
        # This will fail if month > 12, day > 31, or if it's Feb 30th, etc.
        datetime(int(y), int(m), int(d))
        # Also, let's assume photos weren't taken before 1980 or in the future
        if not (1980 <= int(y) <= datetime.now().year):
            return False
        return True
    except ValueError:
        return False

def process_images(directory, fix_metadata=False, extensive=False):
    # Header for the output table
    print(f"{'Status':<12} | {'Filename':<35} | {'Filename Date':<15} | {'Metadata Date'}")
    print("-" * 95)

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        
        # Skip directories
        if os.path.isdir(filepath):
            continue

        # 1. Skip PNGs explicitly as requested
        if filename.lower().endswith('.png'):
            print(f"{'[SKIPPED]':<12} | {filename:<35} | {'-':<15} | PNG format ignored")
            continue

        # 2. Only process JPEGs
        if not filename.lower().endswith(('.jpg', '.jpeg')):
            continue

        # 3. Extract date from filename
        match = DATE_PATTERN.search(filename)
        if not match:
            print(f"{'[NO DATE]':<12} | {filename:<35} | {'N/A':<15} | No date in filename")
            continue
        
        f_year, f_month, f_day = match.groups()
        file_date_str = f"{f_year}:{f_month}:{f_day}"

        if not is_valid_date(f_year, f_month, f_day):
            # This skips files like 'received_1476469...'
            continue

        # 4. Extract date from Metadata
        try:
            with open(filepath, 'rb') as img_file:
                img = Image(img_file)
            
            if not img.has_exif or 'datetime_original' not in img.list_all():
                meta_date_str = "None"
                meta_year, meta_month, meta_day = (None, None, None)
            else:
                meta_date_raw = img.get('datetime_original')
                # Format: "YYYY:MM:DD HH:MM:SS"
                meta_date_str = meta_date_raw.split(' ')[0]
                meta_year, meta_month, meta_day = meta_date_str.split(':')

        except Exception:
            print(f"{'[ERROR]':<12} | {filename:<35} | {file_date_str:<15} | Could not read EXIF")
            continue

        # 5. Comparison Logic
        mismatch = False
        no_date = False
        if meta_year:
            if extensive:
                # Identify if metadata date is greater (later) than filename date
                if (meta_year, meta_month, meta_day) > (f_year, f_month, f_day):
                    mismatch = True
            else:
                # Compare Year only
                if meta_year > f_year:
                    mismatch = True
        else:
            # Identify when the metadata date is None
            no_date = True

        # 6. Action
        status = "[OK]"
        if mismatch or no_date:
            if mismatch: status = "[MISMATCH]"
            if no_date: status = "[NO DATE]"

            if fix_metadata:
                try:
                    img.datetime_original = f"{f_year}:{f_month}:{f_day} 00:00:00"
                    with open(filepath, 'wb') as new_img_file:
                        new_img_file.write(img.get_file())
                    status = "[FIXED]"
                except Exception:
                    status = "[ERR-FIX]"
            
            print(f"{status:<12} | {filename:<35} | {file_date_str:<15} | {meta_date_str}")

        else:
            # Optional: uncomment the line below if you want to see files that match
            print(f"{status:<12} | {filename:<35} | {file_date_str:<15} | {meta_date_str}")
            pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync Image Metadata with Filename Dates")
    parser.add_argument("dir", help="Directory containing images")
    parser.add_argument("--fix", action="store_true", help="Write filename date to metadata")
    parser.add_argument("--extensive", action="store_true", help="Compare Year, Month, and Day")
    
    args = parser.parse_args()
    process_images(args.dir, fix_metadata=args.fix, extensive=args.extensive)