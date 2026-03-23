"""
MD Exporter - Universal Markdown Export Tool

Support for converting Markdown to PDF and DOCX formats.
"""

import argparse
import sys
from pathlib import Path


def get_output_path(filename, format_type):
    """
    Generate output path in the appropriate directory.

    Args:
        filename: Output filename (e.g., "output.pdf" or "output.docx")
        format_type: Either "pdf" or "docx"

    Returns:
        Full path to the output file
    """
    base_dir = Path(__file__).parent
    output_dir = base_dir / "files" / format_type
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir / filename


def main():
    parser = argparse.ArgumentParser(
        description="MD Exporter - Convert Markdown to PDF or DOCX",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 转换为 PDF (使用 Playwright)
  python main.py pdf -i input.md -o output.pdf

  # 转换为 PDF (使用自定义 CSS)
  python main.py pdf -i input.md -o output.pdf -c custom_style.css

  # 转换为 DOCX (默认三线表样式)
  python main.py docx -i input.md -o output.docx

  # 转换为 DOCX (条纹表样式)
  python main.py docx -i input.md -o output.docx --table-style academic_striped

  # 转换为 DOCX (高质量 Mermaid + 图片边框)
  python main.py docx -i input.md -o output.docx --mermaid-dpi 600 --add-image-border

  # 转换为 DOCX (使用自定义模板)
  python main.py docx -i input.md -o output.docx -t custom_template.docx
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="转换格式")

    # ========== PDF 转换 (Playwright) ==========
    pdf_parser = subparsers.add_parser("pdf", help="转换为 PDF (Playwright, 支持 LaTeX/Mermaid)")
    pdf_parser.add_argument("-i", "--input", required=True, help="输入 Markdown 文件")
    pdf_parser.add_argument("-o", "--output", required=True, help="输出 PDF 文件")
    pdf_parser.add_argument("-c", "--css", help="自定义 CSS 样式文件路径")
    pdf_parser.add_argument("--timeout", type=int, default=60000, help="渲染超时时间（毫秒）")

    # ========== DOCX 转换 ==========
    docx_parser = subparsers.add_parser("docx", help="转换为 DOCX (支持 Mermaid/表格样式)")
    docx_parser.add_argument("-i", "--input", required=True, help="输入 Markdown 文件")
    docx_parser.add_argument("-o", "--output", help="输出 DOCX 文件（可选，自动生成）")
    docx_parser.add_argument("-t", "--template", help="自定义 DOCX 模板路径")
    docx_parser.add_argument("--use-default-template", action="store_true", help="使用默认模板")

    # 表格样式选项
    docx_parser.add_argument(
        "--table-style",
        type=str,
        default="academic_three_line",
        choices=["academic_three_line", "academic_striped", "simple_grid", "minimal"],
        help="表格样式（默认：academic_three_line）"
    )
    docx_parser.add_argument("--no-table-enhance", action="store_true", help="禁用表格样式化")

    # Mermaid 图片选项
    docx_parser.add_argument("--mermaid-images-dir", default="files/temp_mermaid_images", help="Mermaid 图片保存目录")
    docx_parser.add_argument("--mermaid-dpi", type=int, default=600, choices=range(96, 601), help="Mermaid 图表 DPI (96-600, 默认：600)")
    docx_parser.add_argument("--no-mermaid", action="store_true", help="禁用 Mermaid 处理")

    # 图片控制选项
    docx_parser.add_argument("--max-image-width-cm", type=float, default=16.0, help="图片最大宽度（厘米）")
    docx_parser.add_argument("--max-image-height-cm", type=float, default=25.0, help="图片最大高度（厘米）")
    docx_parser.add_argument("--add-image-border", action="store_true", help="添加图片边框")

    # 其他选项
    docx_parser.add_argument("--cleanup", action="store_true", help="转换后清理临时文件")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # ========== PDF 转换 ==========
    if args.command == "pdf":
        from md2pdf.playwright_md import main_helper as pdf_main_helper

        output_path = args.output
        pdf_main_helper(
            input_file=args.input,
            output_file=output_path,
            css_path=args.css,
            timeout=args.timeout
        )

        print(f"\n[OK] PDF 已保存到: {output_path}")

    # ========== DOCX 转换 ==========
    elif args.command == "docx":
        from md2docx.docx_md import main_helper as docx_main_helper

        # 生成输出路径
        if args.output:
            output_path = args.output
        else:
            input_path = Path(args.input)
            output_path = str(input_path.with_suffix(".docx"))

        docx_main_helper(
            input_file=args.input,
            output_file=output_path,
            template=args.template,
            use_default_template=args.use_default_template,
            mermaid_dpi=args.mermaid_dpi,
            no_mermaid=args.no_mermaid,
            max_image_width_cm=args.max_image_width_cm,
            max_image_height_cm=args.max_image_height_cm,
            add_image_border=args.add_image_border,
            enhance_tables=not args.no_table_enhance,
            table_style=args.table_style,
            cleanup_temp=args.cleanup
        )

        print(f"\n[OK] DOCX 已保存到: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
