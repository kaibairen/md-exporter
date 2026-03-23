"""
Test script for LaTeX to DOCX conversion (Synchronous)
"""

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


def test_latex_to_docx_sync():
    """Test synchronous LaTeX to DOCX conversion"""
    # For now, test with a markdown file that contains LaTeX formulas
    # In real use, you would use a .tex file
    input_file = "files/md_test_files/test_zh_latex.md"
    output_file = "files/docx/test_latex_to_docx_sync.docx"

    logger.info("=" * 60)
    logger.info("Testing LaTeX to DOCX conversion (SYNCHRONOUS)")
    logger.info("=" * 60)

    # Create converter
    converter = PandocMdDocxConverter(
        use_default_template=True,
    )
    logger.info(f"Using template: {converter.template_path}")

    # Measure time
    start_time = time.time()

    try:
        # Use sync method
        result = converter.convert_file_to_docx(
            input_file=input_file,
            output_file=output_file,
            process_mermaid=False,  # No mermaid in this file
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
    success, duration = test_latex_to_docx_sync()
    exit(0 if success else 1)
