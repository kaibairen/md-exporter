"""
Test script for asynchronous PDF conversion
"""

import asyncio
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


async def test_async_conversion():
    """Test asynchronous PDF conversion method"""
    input_file = "files/md_test_files/test_report.md"
    output_file = "files/pdf/test_report_async.pdf"

    logger.info("=" * 60)
    logger.info("Testing ASYNCHRONOUS PDF conversion method")
    logger.info("=" * 60)

    # Create converter
    converter = PlaywrightMdPdfConverter(
        output_folder="files/pdf",
        timeout=60000,
    )
    logger.info(f"Output folder: {converter.output_folder}")
    logger.info(f"Timeout: {converter.timeout}ms")

    # Measure time
    start_time = time.time()

    try:
        # Use async method
        result = await converter.convert_file_to_pdf_async(
            input_file=input_file,
            output_file=output_file,
        )

        elapsed_time = time.time() - start_time

        logger.info(f"✅ Async conversion completed in {elapsed_time:.2f} seconds")
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
        logger.error(f"❌ Async conversion failed after {elapsed_time:.2f} seconds: {e}")
        import traceback
        traceback.print_exc()
        return False, elapsed_time


async def main():
    """Main async function"""
    try:
        success, duration = await test_async_conversion()
        return 0 if success else 1
    finally:
        # Clean up browser instance
        from md2pdf.playwright_md import close_browser
        await close_browser()


if __name__ == "__main__":
    exit(asyncio.run(main()))
