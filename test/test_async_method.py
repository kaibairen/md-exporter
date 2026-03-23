"""
Test script for asynchronous DOCX conversion
"""

import asyncio
import logging
import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from md2docx.docx_md import PandocMdDocxConverter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

async def test_async_conversion():
    """Test asynchronous conversion method"""
    input_file = "files/md_test_files/test_report.md"
    output_file = "files/docx/test_report_async.docx"

    logger.info("=" * 60)
    logger.info("Testing ASYNCHRONOUS conversion method")
    logger.info("=" * 60)

    # Create converter with template
    converter = PandocMdDocxConverter(
        use_default_template=True,  # Use template from templates/docx_template.docx
        mermaid_dpi=600,
    )
    logger.info(f"Using template: {converter.template_path}")

    # Measure time
    start_time = time.time()

    try:
        # Use async method
        result = await converter.convert_file_to_docx_async(
            input_file=input_file,
            output_file=output_file,
            process_mermaid=True,
            cleanup_temp=False,
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
        return False, elapsed_time

async def main():
    """Main async function"""
    success, duration = await test_async_conversion()
    return 0 if success else 1

if __name__ == "__main__":
    exit(asyncio.run(main()))
