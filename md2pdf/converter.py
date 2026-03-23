import argparse
import os
import platform
import time
from functools import wraps
from typing import Tuple

import markdown
import pdfkit
from dotenv import load_dotenv
from pygments.formatters.html import HtmlFormatter

load_dotenv()

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"⏱️ 函数 '{func.__name__}' 开始执行...")
        start_time = time.perf_counter()
        
        result = func(*args, **kwargs)
        
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        
        print(f"✅ 函数 '{func.__name__}' 执行完毕。")
        print(f"⏳ 总执行时间: {execution_time:.4f} 秒")
        return result
    return wrapper

def get_default_wkhtmltopdf_path():
    """获取默认的wkhtmltopdf路径"""
    # 首先尝试从环境变量获取
    env_path = os.environ.get('WKHTMLTOPDF_PATH')
    if env_path and os.path.exists(env_path):
        return env_path

    # 根据操作系统返回常见安装路径
    system = platform.system().lower()
    if system == 'windows':
        # Windows常见路径
        possible_paths = [
            r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe",
            r"C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe"
        ]
    elif system == 'linux':
        # Linux常见路径
        possible_paths = [
            '/usr/bin/wkhtmltopdf',
            '/usr/local/bin/wkhtmltopdf',
            '/opt/wkhtmltopdf/bin/wkhtmltopdf'
        ]
    elif system == 'darwin':
        # macOS常见路径
        possible_paths = [
            '/usr/local/bin/wkhtmltopdf',
            '/opt/homebrew/bin/wkhtmltopdf'
        ]
    else:
        return None

    # 检查路径是否存在
    for path in possible_paths:
        if os.path.exists(path):
            return path

    # 如果都不存在，尝试在PATH中查找
    try:
        import shutil
        path = shutil.which('wkhtmltopdf')
        if path:
            return path
    except:
        pass

    return None


class MdPdfConverter:
    def __init__(self, wkhtmltopdf_path: str = None, mathjax_path: str = None):
        """
        初始化转换器
        :param wkhtmltopdf_path: wkhtmltopdf 二进制文件路径 (None 则自动查找)
        :param mathjax_path: 本地 MathJax.js 文件的绝对路径
        """
        self.wkhtmltopdf_path = wkhtmltopdf_path or os.environ.get("WKHTMLTOPDF_PATH")
        default_mathjax = os.environ.get("MATHJAX_URL")
    
        self.mathjax_path = mathjax_path or default_mathjax

        if not self.mathjax_path:
            raise FileNotFoundError("Mathjax must be set. Please set MATHJAX_URL environment variable.")
     
        self.base_options = {
            'encoding': 'UTF-8',
            'enable-local-file-access': None,
            'quiet': '',
            'no-stop-slow-scripts': None,
        }
    
    def saveHtml(self, html_content : str, output_file) :
        html_file = os.path.splitext(output_file)[0] + '.html'
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("save html to {}".format(html_file))
    
    @timer 
    def convert(self, input_path: str, output_path: str, css_path: str):
        filename = os.path.basename(input_path)
        print(f"🚀 开始处理: {filename}")

        try:
            body_html, has_latex = self._prepare_content(input_path)
            print("body_html:", body_html[:100])

            full_html, has_mathjax = self._assemble_page(body_html, css_path, has_latex)
            
            # 中间结果
            self.saveHtml(full_html, output_path)
            
            self._render_pdf(full_html, output_path, has_latex and has_mathjax)
            
            print(f"✅ 转换完成: {output_path}")

        except Exception as e:
            print(f"❌ 转换出错 ({filename}): {str(e)}")

    def _prepare_content(self, input_path: str) -> Tuple[str, bool]:
        """读取文件并解析 Markdown，返回 HTML 片段和是否包含 Latex"""
        with open(input_path, 'r', encoding='utf-8') as f:
            md_text = f.read()
    
        extensions = [
            'pymdownx.arithmatex',       # 数学公式
            'markdown.extensions.extra', # 表格代码
            'markdown.extensions.toc',   # 目录
            'markdown.extensions.codehilite' # 代码高亮
        ]
        
        extension_configs = {
            'pymdownx.arithmatex': {
                'generic': True, 'preview': False, 'smart_dollar': False 
            },
            'markdown.extensions.codehilite': {
                'css_class': 'codehilite', 'linenums': False, 'guess_lang': True
            }
        }
        
        body_html = markdown.markdown(md_text, extensions=extensions, extension_configs=extension_configs)
        
        # 是否包含公式类名
        has_latex = 'class="arithmatex"' in body_html
        return body_html, has_latex

    def _assemble_page(self, body_html: str, css_path: str, has_latex: bool) -> tuple[str, bool]:
        """组合 CSS, JS 和 HTML"""
        full_css = self._generate_css(css_path)
        print("full_css:", full_css[:100])
        mathjax_script = self._get_mathjax_script() if has_latex else ""
        
        return f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <style>{full_css}</style>
            {mathjax_script}
        </head>
        <body>
            <div class="markdown-body">
                {body_html}
            </div>
        </body>
        </html>
        """, mathjax_script != ""

    def _render_pdf(self, html_content: str, output_path: str, has_latex: bool):
        """配置参数并写入 PDF"""
        options = self.base_options.copy()
        
        if has_latex:
            print("  ⚡ 识别到公式，注入渲染引擎并等待...")
            options['window-status'] = 'mathjax_finished'
        else:
            print("  💨 纯文本模式，快速渲染")

        config = pdfkit.configuration(wkhtmltopdf=self.wkhtmltopdf_path) if self.wkhtmltopdf_path else None
        
        pdfkit.from_string(html_content, output_path, configuration=config, options=options)

    def _generate_css(self, user_css_path: str) -> str:
        """生成最终合并的 CSS"""
        print("user_css_path:", user_css_path)
        pygment_css = HtmlFormatter(style='default').get_style_defs('.codehilite')
        
        user_css = ""
        if user_css_path and os.path.exists(user_css_path):
            with open(user_css_path, 'r', encoding='utf-8') as f:
                user_css = f.read()

        override_css = f"""
        {pygment_css}
        
        /* 修复代码块背景和字体 */
        .codehilite {{ 
            background-color: #f6f8fa; 
            border: 1px solid #bfbfbf;
            border-radius: 4px; 
            padding: 12px 15px; 
            margin: 1.5em 0; 
            page-break-inside: avoid;
        }}
        .codehilite pre {{ 
            margin: 0; 
            white-space: pre-wrap; 
            word-wrap: break-word; 
            font-family: "Consolas", "Courier New", monospace; 
            font-size: 14px; 
            line-height: 1.6; 
        }}
        .codehilite pre code {{ 
            background-color: transparent !important; 
            border: none !important; 
            text-shadow: none !important; 
            color: #1a1a1a; 
        }}
        """
        return user_css + "\n" + override_css

    def _get_mathjax_script(self) -> str:
        """生成 MathJax 注入脚本"""

        src_url = self.mathjax_path
        print("mathjax_path:", src_url)
        if not os.path.exists(src_url) :
            print("❌ MathJax 不存在 ! 回退默认处理器")
            return ""
        print("mathjax_script:", src_url)
        
        mathjax_url = f"file://{src_url}"
        
        return f"""
        <script type="text/x-mathjax-config">
            MathJax.Hub.Config({{
                tex2jax: {{
                    inlineMath: [['$','$'], ['\\\\(','\\\\)']], 
                    displayMath: [['$$','$$'], ['\\\\[','\\\\]']],
                    processEscapes: true,
                    processClass: "arithmatex"
                }},
                messageStyle: "none"
            }});
            // 渲染完成后通知 wkhtmltopdf
            MathJax.Hub.Queue(function () {{
                window.status = "mathjax_finished";
            }});
        </script>
        <script src="{mathjax_url}?config=TeX-MML-AM_CHTML"></script>
        """
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Markdown转PDF工具")
    parser.add_argument('-i', "--input", help="输入的Markdown文件路径", required=True)
    parser.add_argument("-o", "--output", help="输出的PDF文件路径（默认同输入文件名）")
    parser.add_argument("-c", "--css", default="css/style.css", help="CSS样式文件路径（默认: css/style.css）")
    parser.add_argument("--wkhtmltopdf-path", help="wkhtmltopdf可执行文件路径（覆盖环境变量WKHTMLTOPDF_PATH）")

    args = parser.parse_args()

    output = args.output if args.output else os.path.splitext(args.input)[0] + ".pdf"

    converter = MdPdfConverter()
    
    converter.convert(
        args.input,
        output,
        args.css
    )
   
    