#!/usr/bin/env python3
# PDF to Markdown converter using Marker
# Requires Python 3.8+ and pip

import os
import sys
import argparse
import time
import subprocess
import gc
import threading
import concurrent.futures
from pathlib import Path
from dotenv import load_dotenv

def process_single_pdf(pdf_path, output_dir, max_pages=None, languages=None, use_llm=False):
    """
    Process a single PDF file using marker_single
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Build command arguments
    cmd = ["marker_single", pdf_path, "--output_dir", output_dir]
    
    # Add optional parameters
    if max_pages:
        cmd.extend(["--max_pages", str(max_pages)])
    if languages:
        cmd.extend(["--langs", languages])
    if use_llm:
        cmd.append("--use_llm")
    
    # Execute the command
    pdf_name = Path(pdf_path).name
    print(f"Processing: {pdf_name}")
    
    try:
        subprocess.run(cmd, check=True)
        
        # Force garbage collection to clean up memory
        gc.collect()
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except (ImportError, AttributeError):
            pass
            
        base_name = Path(pdf_path).stem
        output_file = f"{base_name}.md"
        if any(os.path.exists(os.path.join(root, output_file)) for root, _, _ in os.walk(output_dir)):
            print(f"✓ Completed: {pdf_name} -> {output_file}")
            return True
        else:
            print(f"✗ Failed: {pdf_name} (output file not found)")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed: {pdf_name} (exit code: {e.returncode})")
        return False
    except Exception as e:
        print(f"✗ Failed: {pdf_name} ({str(e)})")
        return False

def convert_pdf_to_markdown(input_path, output_dir, max_pages=None, languages=None, workers=1, max_files=None, min_length=0, use_llm=False):
    """
    Convert PDF(s) to Markdown using the Marker library via command line
    Works for both single files and directories by calling marker_single on each file
    """
    try:
        # Load environment variables from .env file
        if use_llm:
            print("Loading environment variables for API keys...")
            load_dotenv(override=True)
            
        # Determine if input is a file or directory
        is_file = os.path.isfile(input_path)
        is_dir = os.path.isdir(input_path)
        
        if not (is_file or is_dir):
            print(f"Error: Input path '{input_path}' is neither a file nor a directory")
            return False
            
        if is_file and not input_path.lower().endswith('.pdf'):
            print(f"Error: Input file '{input_path}' is not a PDF file")
            return False
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Set environment variables to help with memory management
        os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:128"
        
        if is_file:
            # Single file mode
            print(f"Converting single PDF: {input_path}")
            if languages:
                print(f"Using OCR languages: {languages}")
            if use_llm:
                print("Using LLM enhancement for improved conversion quality")
            if max_pages:
                print(f"Processing maximum {max_pages} pages")
                
            start_time = time.time()
            result = process_single_pdf(input_path, output_dir, max_pages, languages, use_llm)
            elapsed_time = time.time() - start_time
            
            print(f"Conversion completed in {elapsed_time:.2f} seconds")
            return result
            
        else:
            # Directory mode - process each PDF individually
            print(f"Processing directory: {input_path}")
            
            # Find all PDF files in the directory
            pdf_files = list(Path(input_path).glob("**/*.pdf"))
            
            if not pdf_files:
                print(f"No PDF files found in {input_path}")
                return False
                
            # Apply max_files limit if specified
            if max_files and len(pdf_files) > max_files:
                print(f"Limiting to {max_files} files out of {len(pdf_files)} found")
                pdf_files = pdf_files[:max_files]
            else:
                print(f"Found {len(pdf_files)} PDF files")
                
            if languages:
                print(f"Using OCR languages: {languages}")
            if use_llm:
                print("Using LLM enhancement for improved conversion quality")
            if max_pages:
                print(f"Processing maximum {max_pages} pages per PDF")
                
            # Process files
            start_time = time.time()
            successful = 0
            failed = 0
            
            # Determine if we should use parallel processing
            if workers > 1:
                print(f"Processing with {workers} parallel workers")
                with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
                    futures = []
                    for pdf_path in pdf_files:
                        # Skip files smaller than min_length if specified
                        if min_length > 0:
                            file_size = os.path.getsize(pdf_path)
                            if file_size < min_length:
                                print(f"Skipping {pdf_path.name} (size: {file_size} bytes < minimum {min_length} bytes)")
                                continue
                                
                        futures.append(
                            executor.submit(
                                process_single_pdf, 
                                str(pdf_path), 
                                output_dir, 
                                max_pages, 
                                languages, 
                                use_llm
                            )
                        )
                    
                    for future in concurrent.futures.as_completed(futures):
                        if future.result():
                            successful += 1
                        else:
                            failed += 1
            else:
                # Process files sequentially
                print("Processing files sequentially")
                for pdf_path in pdf_files:
                    # Skip files smaller than min_length if specified
                    if min_length > 0:
                        file_size = os.path.getsize(pdf_path)
                        if file_size < min_length:
                            print(f"Skipping {pdf_path.name} (size: {file_size} bytes < minimum {min_length} bytes)")
                            continue
                            
                    if process_single_pdf(str(pdf_path), output_dir, max_pages, languages, use_llm):
                        successful += 1
                    else:
                        failed += 1
            
            elapsed_time = time.time() - start_time
            print(f"\nConversion summary:")
            print(f"- Total files: {len(pdf_files)}")
            print(f"- Successfully converted: {successful}")
            print(f"- Failed: {failed}")
            print(f"- Total time: {elapsed_time:.2f} seconds")
            
            # Count actual Markdown files created
            md_files = len(list(Path(output_dir).rglob("*.md")))
            print(f"\nFound {md_files} Markdown files in {output_dir}")
            
            return failed == 0
        
    except ImportError:
        print("Error: marker package not found. Please install with:")
        print("pip install marker-pdf")
        return False
    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Final memory cleanup
        gc.collect()
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except (ImportError, AttributeError):
            pass

def main():
    parser = argparse.ArgumentParser(description="Convert PDF to Markdown using Marker")
    parser.add_argument("input_path", help="Path to the input PDF file or directory containing PDFs")
    parser.add_argument("output_dir", help="Directory to save the Markdown files")
    parser.add_argument("--max_pages", type=int, 
                        help="Maximum number of pages to process per PDF")
    parser.add_argument("--langs", 
                        help="Comma-separated list of languages for OCR (e.g., 'en,fr,de')")
    parser.add_argument("--workers", type=int, default=1,
                        help="Number of PDFs to process in parallel (when processing a directory)")
    parser.add_argument("--max_files", type=int,
                        help="Maximum number of PDF files to process from directory")
    parser.add_argument("--min_length", type=int, default=0,
                        help="Minimum file size in bytes to process (smaller PDFs will be skipped)")
    parser.add_argument("--use_llm", action="store_true",
                        help="Use LLM to enhance conversion quality (requires Google API key in .env file)")
    
    args = parser.parse_args()
    
    result = convert_pdf_to_markdown(
        args.input_path,
        args.output_dir,
        args.max_pages,
        args.langs,
        args.workers,
        args.max_files,
        args.min_length,
        args.use_llm
    )
    
    # Exit with appropriate status code
    sys.exit(0 if result else 1)

if __name__ == "__main__":
    main() 