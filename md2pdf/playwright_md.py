import os
import re
import uuid
import logging
import zipfile
import urllib.request
import time
from os import PathLike
from pathlib import Path

import markdown
from pygments.formatters.html import HtmlFormatter

logger = logging.getLogger(__name__)

ASSETS_DIR = Path(__file__).parent / "assets"

# 全局浏览器实例（异步）
_playwright_instance = None
_browser_instance = None


async def _get_browser():
    """获取全局浏览器实例（懒加载）"""
    global _playwright_instance, _browser_instance
    if _browser_instance is None:
        from playwright.async_api import async_playwright
        _playwright_instance = await async_playwright().start()
        _browser_instance = await _playwright_instance.chromium.launch()
        logger.info("浏览器实例已初始化")
    return _browser_instance


async def close_browser():
    """关闭全局浏览器实例"""
    global _playwright_instance, _browser_instance
    if _browser_instance:
        await _browser_instance.close()
        _browser_instance = None
    if _playwright_instance:
        await _playwright_instance.stop()
        _playwright_instance = None
        logger.info("浏览器实例已关闭")


CDN_URLS = {
    "katex.min.js": "https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js",
    "katex.min.css": "https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css",
    "mermaid.min.js": "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js",
}


def init_assets():
    """下载本地资源文件"""
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    katex_dir = ASSETS_DIR / "katex"
    if not katex_dir.exists():
        print("Downloading KaTeX...")
        zip_path = ASSETS_DIR / "katex.zip"
        urllib.request.urlretrieve(
            "https://github.com/KaTeX/KaTeX/releases/download/v0.16.9/katex.zip",
            zip_path,
        )
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(ASSETS_DIR)
        zip_path.unlink()

    mermaid_path = ASSETS_DIR / "mermaid.min.js"
    if not mermaid_path.exists():
        print("Downloading Mermaid...")
        urllib.request.urlretrieve(CDN_URLS["mermaid.min.js"], mermaid_path)

    print("Assets initialized")


def get_asset_path(name: str) -> str:
    """获取资源路径，优先本地"""
    local_paths = {
        "katex.min.js": ASSETS_DIR / "katex" / "katex.min.js",
        "katex.min.css": ASSETS_DIR / "katex" / "katex.min.css",
        "mermaid.min.js": ASSETS_DIR / "mermaid.min.js",
    }
    local = local_paths.get(name)
    if local and local.exists():
        return f"file://{local.absolute()}"
    return CDN_URLS.get(name, name)


class PlaywrightMdPdfConverter:
    def __init__(self, css_path: str | PathLike = None, timeout: int = 60000, output_folder: str | PathLike = None):
        """
        初始化转换器
        :param css_path: CSS 样式文件路径
        :param timeout: 渲染超时时间（毫秒）
        :param output_folder: 输出目录
        """
        self.timeout = timeout
        css_file_path = Path(css_path) if css_path else Path(__file__).parent / "style.css"
        self.css = self._generate_css(css_file_path)

        self.output_folder = Path(output_folder) if output_folder else Path(__file__).parent / "output"
        self.output_folder.mkdir(parents=True, exist_ok=True)

    def _generate_css(self, user_css_path: Path) -> str:
        """生成最终合并的 CSS"""
        pygment_css = HtmlFormatter(style="default").get_style_defs(".codehilite")

        user_css = ""
        if user_css_path and user_css_path.exists():
            try:
                user_css = user_css_path.read_text(encoding="utf-8")
                fonts_dir = user_css_path.parent / "fonts"
                if fonts_dir.exists():
                    user_css = user_css.replace(
                        'url("./fonts/', f'url("file://{fonts_dir.absolute()}/'
                    )
            except (OSError, UnicodeDecodeError) as e:
                logger.warning("Failed to read CSS file %s: %s", user_css_path, e)

        override_css = f"""
        {pygment_css}
        .codehilite {{ background: #f6f8fa; border: 1px solid #e1e4e8; border-radius: 6px; padding: 12px; margin: 1em 0; overflow-x: auto; }}
        .codehilite pre {{ margin: 0; font-family: 'Consolas', 'Monaco', monospace; font-size: 12px; }}
        .mermaid {{
            text-align: center;
            margin: 1em 0;
        }}
        .mermaid svg {{
            display: inline-block;
            max-width: 90%;
            height: auto;
        }}
        .markdown-body {{ margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif; font-size: 12px; line-height: 1.5; }}
        """
        return user_css + "\n" + override_css

    def _get_scripts(self, has_latex: bool, has_mermaid: bool) -> str:
        """生成 KaTeX/Mermaid 脚本"""
        scripts = ""
        if has_latex:
            scripts += f'''
    <script src="{get_asset_path('katex.min.js')}"></script>
    <link rel="stylesheet" href="{get_asset_path('katex.min.css')}">
    <script>
        document.addEventListener('DOMContentLoaded', () => {{
            document.querySelectorAll('.arithmatex').forEach(el => {{
                const tex = el.textContent.replace(/^\\\\[\\[(]|\\\\[\\])]$/g, '');
                katex.render(tex, el, {{ displayMode: el.tagName === 'DIV', throwOnError: false }});
            }});
            window.mathReady = true;
        }});
    </script>'''

        if has_mermaid:
            scripts += f'''
    <script src="{get_asset_path('mermaid.min.js')}"></script>
    <script>
        mermaid.initialize({{
            startOnLoad: false,
            theme: "neutral",
            securityLevel: 'loose',
            fontSize: 12,
            flowchart: {{
                useMaxWidth: false,
                htmlLabels: true,
                curve: 'basis',
                nodeSpacing: 20,
                rankSpacing: 30,
                padding: 10
            }},
            sequence: {{
                useMaxWidth: false
            }},
            gantt: {{
                useMaxWidth: false,
                fontSize: 11
            }}
        }});

        // 动态调整图表尺寸：大图放宽限制，小图保持原样
        function adjustMermaidSize() {{
            document.querySelectorAll('.mermaid svg').forEach(svg => {{
                const h = parseFloat(svg.getAttribute('height') || 0);
                // 只有超大图 (>1500px) 才缩放，缩放到 1200px
                if (h > 1500) {{
                    const scale = 1200 / h;
                    svg.style.transform = `scale(${{scale}})`;
                    svg.style.transformOrigin = 'top center';
                    svg.parentElement.style.height = '1200px';
                    svg.parentElement.style.overflow = 'hidden';
                }} else {{
                    // 小图保持原样，只限制最大宽度
                    svg.style.maxWidth = '100%';
                }}
            }});
        }}

        window.addEventListener('load', async () => {{
            try {{
                const elements = document.querySelectorAll('.mermaid');
                for (let i = 0; i < elements.length; i++) {{
                    try {{
                        await mermaid.run({{ nodes: [elements[i]] }});
                    }} catch (e) {{}}
                }}
                adjustMermaidSize();
                window.mermaidReady = true;
            }} catch (e) {{
                window.mermaidReady = true;
            }}
        }});
    </script>'''
        return scripts

    def assemble_page(self, body_html: str, has_latex: bool, has_mermaid: bool) -> str:
        """组合 CSS, JS 和 HTML"""
        scripts = self._get_scripts(has_latex, has_mermaid)
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <style>{self.css}</style>
    {scripts}
</head>
<body>
    <div class="markdown-body">{body_html}</div>
</body>
</html>"""

    async def render_pdf(self, html_content: str, output_path: str, has_latex: bool, has_mermaid: bool):
        """使用 Playwright 渲染 PDF"""
        total_start = time.perf_counter()
        logger.info("render_pdf: 开始，has_latex=%s, has_mermaid=%s", has_latex, has_mermaid)

        html_path = Path(output_path).with_suffix(".html")
        html_path.write_text(html_content, encoding="utf-8")

        has_external = bool(re.search(r'src=["\']https?://', html_content))
        wait_strategy = "networkidle" if has_external else "domcontentloaded"

        try:
            t0 = time.perf_counter()
            browser = await _get_browser()
            logger.info("render_pdf: 浏览器实例 %.2fs", time.perf_counter() - t0)

            t0 = time.perf_counter()
            page = await browser.new_page()
            logger.info("render_pdf: 创建页面 %.2fs", time.perf_counter() - t0)

            t0 = time.perf_counter()
            await page.goto(f"file://{html_path.absolute()}", wait_until=wait_strategy, timeout=self.timeout)
            logger.info("render_pdf: 加载页面 %.2fs", time.perf_counter() - t0)

            # 等待渲染，失败则跳过（兜底策略）
            if has_latex:
                try:
                    t0 = time.perf_counter()
                    await page.wait_for_function("window.mathReady === true", timeout=10000)
                    logger.info("render_pdf: KaTeX渲染 %.2fs", time.perf_counter() - t0)
                except Exception as e:
                    logger.warning("render_pdf: KaTeX 渲染失败，跳过: %s", e)

            if has_mermaid:
                try:
                    t0 = time.perf_counter()
                    await page.wait_for_function("window.mermaidReady === true", timeout=10000)
                    logger.info("render_pdf: Mermaid渲染 %.2fs", time.perf_counter() - t0)
                except Exception as e:
                    logger.warning("render_pdf: Mermaid 渲染失败，跳过: %s", e)

            t0 = time.perf_counter()
            await page.pdf(
                path=output_path,
                format="A4",
                print_background=True,
                margin={"top": "15mm", "bottom": "15mm", "left": "10mm", "right": "10mm"},
            )
            logger.info("render_pdf: 生成PDF %.2fs", time.perf_counter() - t0)

            await page.close()
            logger.info("render_pdf: 总耗时 %.2fs -> %s", time.perf_counter() - total_start, output_path)
        except Exception as e:
            logger.error("render_pdf: 发生异常: %s", e)
            raise RuntimeError(f"PDF generation failed: {e}") from e

    def _fix_mermaid_syntax(self, content: str) -> str:
        """修复 Mermaid 语法：中文引号转英文引号"""
        content = content.replace(""", '"').replace(""", '"').replace("'", "'").replace("'", "'")
        return content

    def md_to_html(self, md_text: str) -> tuple[str, bool, bool]:
        """转换 Markdown，返回 HTML 片段、是否包含 LaTeX、是否包含 Mermaid"""
        import html
        import re

        # 预处理：确保 $$ 块级公式前后有空行（pymdownx.arithmatex要求）
        lines = md_text.split('\n')
        result = []
        i = 0
        while i < len(lines):
            line = lines[i]
            # 如果当前行是 $$
            if line.strip() == '$$':
                # 在 $$ 前添加空行（如果前一行不是空行）
                if result and result[-1].strip() != '':
                    result.append('')
                result.append(line)
                # 跳过 $$ 后面的内容行，直到遇到下一个 $$
                i += 1
                while i < len(lines) and lines[i].strip() != '$$':
                    result.append(lines[i])
                    i += 1
                if i < len(lines):
                    result.append(lines[i])  # 添加结束的 $$
                    # 在 $$ 后添加空行（如果还有下一行且不是空行）
                    if i + 1 < len(lines) and lines[i + 1].strip() != '':
                        result.append('')
                i += 1
            else:
                result.append(line)
                i += 1
        md_text = '\n'.join(result)

        def format_mermaid(source, language, css_class, options, md, **kwargs):
            source = source.replace('\\\"', '"')
            source = re.sub(r'\n[ \t]+\n', '\n\n', source)
            return f'<div class="{css_class}">{source}</div>'

        extensions = [
            "pymdownx.arithmatex",
            "markdown.extensions.extra",
            "markdown.extensions.toc",
            "markdown.extensions.codehilite",
            "pymdownx.superfences",
        ]
        extension_configs = {
            "pymdownx.arithmatex": {"generic": True},
            "markdown.extensions.codehilite": {"css_class": "codehilite", "linenums": False},
            "pymdownx.superfences": {
                "custom_fences": [
                    {
                        "name": "mermaid",
                        "class": "mermaid",
                        "format": format_mermaid
                    }
                ]
            }
        }

        body_html = markdown.markdown(md_text, extensions=extensions, extension_configs=extension_configs)
        has_latex = 'class="arithmatex"' in body_html
        has_mermaid = 'class="mermaid"' in body_html

        return body_html, has_latex, has_mermaid

    async def convert_to_pdf_async(self, text: str, output_file: str = None, save_md: bool = True) -> str:
        """异步版本：转换 Markdown 文本为 PDF"""
        import asyncio

        if not output_file:
            output_file = str(self.output_folder / f"{uuid.uuid4()}.pdf")

        # 保存原始 markdown 内容
        if save_md:
            md_path = Path(output_file).with_suffix(".md")
            md_path.write_text(text, encoding="utf-8")
            logger.info("Saved markdown source to: %s", md_path)

        html, has_latex, has_mermaid = self.md_to_html(text)
        logger.info("Converting markdown to PDF, content length: %d", len(text))

        full_html = self.assemble_page(html, has_latex, has_mermaid)

        try:
            await asyncio.wait_for(
                self.render_pdf(full_html, output_file, has_latex, has_mermaid),
                timeout=self.timeout / 1000  # 转换为秒
            )
        except asyncio.TimeoutError:
            logger.error("PDF generation timed out after %dms", self.timeout)
            raise RuntimeError(f"PDF generation timed out after {self.timeout}ms")

        logger.info("Successfully converted markdown to PDF: %s", output_file)
        return output_file

    async def convert_file_to_pdf_async(self, input_file: str | PathLike, output_file: str = None) -> str:
        """异步版本：转换 Markdown 文件为 PDF"""
        input_path = Path(input_file)
        if not input_path.is_file():
            raise FileNotFoundError(f"Input file not found: {input_file}")

        try:
            md_text = input_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            raise RuntimeError(f"Failed to read input file: {e}") from e

        return await self.convert_to_pdf_async(md_text, output_file)

    def convert_to_pdf(self, text: str, output_file: str = None) -> str:
        """同步版本：转换 Markdown 文本为 PDF"""
        import asyncio
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return pool.submit(asyncio.run, self.convert_to_pdf_async(text, output_file)).result()

    def convert_file_to_pdf(self, input_file: str | PathLike, output_file: str = None) -> str:
        """同步版本：转换 Markdown 文件为 PDF"""
        import asyncio
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return pool.submit(asyncio.run, self.convert_file_to_pdf_async(input_file, output_file)).result()


# 便利函数
_playwright_converter = None


def _get_converter() -> PlaywrightMdPdfConverter:
    global _playwright_converter
    if _playwright_converter is None:
        _playwright_converter = PlaywrightMdPdfConverter()
    return _playwright_converter


async def convert_md_to_pdf_playwright_async(text: str, output_file: str = None, save_md: bool = True) -> str:
    """异步版本：转换 Markdown 文本为 PDF 的便利函数"""
    return await _get_converter().convert_to_pdf_async(text, output_file, save_md)


async def convert_md_file_to_pdf_playwright_async(input_file: str | PathLike, output_file: str = None) -> str:
    """异步版本：转换 Markdown 文件为 PDF 的便利函数"""
    return await _get_converter().convert_file_to_pdf_async(input_file, output_file)


def convert_md_to_pdf_playwright(text: str, output_file: str = None) -> str:
    """同步版本：转换 Markdown 文本为 PDF 的便利函数"""
    return _get_converter().convert_to_pdf(text, output_file)


def convert_md_file_to_pdf_playwright(input_file: str | PathLike, output_file: str = None) -> str:
    """同步版本：转换 Markdown 文件为 PDF 的便利函数"""
    return _get_converter().convert_file_to_pdf(input_file, output_file)


def main_helper(input_file, output_file=None, css_path=None, timeout=60000, init_assets_flag=False):
    """
    Helper function for calling from main entry point.

    Args:
        input_file: Input Markdown file path
        output_file: Output PDF file path (optional, auto-generated if not provided)
        css_path: Custom CSS file path (optional)
        timeout: Rendering timeout in milliseconds (default: 60000)
        init_assets_flag: If True, initialize local assets and exit
    """
    if init_assets_flag:
        init_assets()
        return

    if not input_file:
        raise ValueError("input_file is required")

    if not output_file:
        output_file = os.path.splitext(input_file)[0] + ".pdf"

    converter = PlaywrightMdPdfConverter(css_path=css_path, timeout=timeout)
    converter.convert_file_to_pdf(input_file, output_file)


if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

    parser = argparse.ArgumentParser(description="Markdown转PDF (Playwright, 支持LaTeX/Mermaid)")
    parser.add_argument("-i", "--input", help="输入Markdown文件")
    parser.add_argument("-o", "--output", help="输出PDF路径")
    parser.add_argument("-c", "--css", help="CSS样式文件")
    parser.add_argument("--timeout", type=int, default=60000, help="渲染超时(毫秒)")
    parser.add_argument("--init", action="store_true", help="初始化下载本地资源")

    args = parser.parse_args()

    if args.init:
        init_assets()
    elif args.input:
        output = args.output or os.path.splitext(args.input)[0] + ".pdf"
        converter = PlaywrightMdPdfConverter(css_path=args.css, timeout=args.timeout)
        converter.convert_file_to_pdf(args.input, output)
    else:
        parser.print_help()
    