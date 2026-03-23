"""
Test script for converting LaTeX/formula-heavy markdown files to PDF (Synchronous)
"""

import logging
import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from md2pdf.playwright_md import PlaywrightMdPdfConverter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def test_sync_conversion():
    """Test synchronous PDF conversion for LaTeX-heavy file"""
    input_file = "files/md_test_files/test_zh_latex.md"
    output_file = "files/pdf/test_zh_latex_sync.pdf"

    logger.info("=" * 60)
    logger.info("Testing LaTeX-heavy Markdown conversion (SYNCHRONOUS)")
    logger.info("=" * 60)

    # Create converter
    converter = PlaywrightMdPdfConverter(
        output_folder="files/pdf",
        timeout=120000,  # 2 minutes timeout for large file
    )
    logger.info(f"Output folder: {converter.output_folder}")
    logger.info(f"Timeout: {converter.timeout}ms")

    # Measure time
    start_time = time.time()

    try:
        # Use sync method
        result = converter.convert_file_to_pdf(
            input_file=input_file,
            output_file=output_file,
        )

        elapsed_time = time.time() - start_time

        logger.info(f"✅ Sync conversion completed in {elapsed_time:.2f} seconds")
        logger.info(f"Output file: {result}")

        # Verify output file exists
        if Path(result).exists():
            file_size = Path(result).stat().st_size / 1024  # KB
            logger.info(f"File size: {file_size:.2f} KB")
            return True, elapsed_time
        else:
            logger.error("Output file not found!")
            return False, elapsed_time

    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.error(f"❌ Sync conversion failed after {elapsed_time:.2f} seconds: {e}")
        import traceback
        traceback.print_exc()
        return False, elapsed_time


if __name__ == "__main__":
    success, duration = test_sync_conversion()
    exit(0 if success else 1)
