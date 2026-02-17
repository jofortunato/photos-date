import os
from exif import Image
import argparse

def reset_invalid_metadata(directory, dry_run=True):
    print(f"{'Action':<12} | {'Filename':<35} | {'Detected Year'}")
    print("-" * 65)

    for filename in os.listdir(directory):
        if not filename.lower().endswith(('.jpg', '.jpeg')):
            continue

        filepath = os.path.join(directory, filename)
        
        try:
            with open(filepath, 'rb') as img_file:
                img = Image(img_file)
            
            if img.has_exif and 'datetime_original' in img.list_all():
                meta_date_raw = img.get('datetime_original')
                # Extract the year: "1476:46:99..." -> "1476"
                meta_year = int(meta_date_raw.split(':')[0])

                # Identify "impossible" dates (e.g., before 1980)
                if meta_year < 1980:
                    if dry_run:
                        print(f"{'[WOULD RESET]':<12} | {filename:<35} | {meta_year}")
                    else:
                        # Delete the specific tag
                        del img.datetime_original
                        with open(filepath, 'wb') as new_img_file:
                            new_img_file.write(img.get_file())
                        print(f"{'[RESET DONE]':<12} | {filename:<35} | {meta_year}")
        
        except Exception as e:
            # Skip files that are already corrupted or unreadable
            continue

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reset impossible EXIF dates")
    parser.add_argument("dir", help="Directory to clean")
    parser.add_argument("--execute", action="store_true", help="Actually delete the metadata")
    
    args = parser.parse_args()
    
    if not args.execute:
        print("RUNNING IN DRY-RUN MODE. Use --execute to apply changes.\n")
    
    reset_invalid_metadata(args.dir, dry_run=not args.execute)