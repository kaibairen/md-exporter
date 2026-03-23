import argparse
import os
import platform

import markdown
import pdfkit


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


def convert_md_to_pdf(input_file, output_file, css_path="css/style.css", wkhtmltopdf_path=None):
    try:
        # 读取Markdown文件
        with open(input_file, 'r', encoding='utf-8') as f:
            md_text = f.read()

        # 转换为HTML
        html = markdown.markdown(md_text,
                                 # extensions=['tables', ]
                                 extensions=['markdown_tables_extended', ]
                                 )
        html_file = os.path.splitext(output_file)[0] + '.html'

        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html)

        options = {
            'encoding': 'UTF-8',
            'quiet': '',
            # 'enable-local-file-access': None  # 允许加载本地资源
        }

        # 获取wkhtmltopdf路径
        if not wkhtmltopdf_path:
            wkhtmltopdf_path = get_default_wkhtmltopdf_path()
            if not wkhtmltopdf_path:
                raise Exception("无法找到wkhtmltopdf。请安装wkhtmltopdf或设置WKHTMLTOPDF_PATH环境变量")

        # 生成PDF配置
        pdfkit_config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

        # 检查CSS文件是否存在
        if css_path and not os.path.exists(css_path):
            print(f"警告: 未找到CSS文件 '{css_path}'，将使用默认样式")
            css_path = None

        # 设置输出文件名
        css_name = os.path.splitext(os.path.basename(css_path))[0] if css_path else "style"
        output_file = os.path.splitext(output_file)[0] + f"_{css_name}.pdf"

        # 生成PDF
        pdfkit.from_string(html, output_file,
                          configuration=pdfkit_config,
                          options=options,
                          css=css_path)

        print(f"成功生成PDF: {output_file}")
    except Exception as e:
        print(f"转换失败: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Markdown转PDF工具")
    parser.add_argument('-i', "--input", help="输入的Markdown文件路径", required=True)
    parser.add_argument("-o", "--output", help="输出的PDF文件路径（默认同输入文件名）")
    parser.add_argument("-c", "--css", default="css/style.css", help="CSS样式文件路径（默认: css/style.css）")
    parser.add_argument("--wkhtmltopdf-path", help="wkhtmltopdf可执行文件路径（覆盖环境变量WKHTMLTOPDF_PATH）")

    args = parser.parse_args()

    # 设置输出文件路径
    output = args.output if args.output else os.path.splitext(args.input)[0] + ".pdf"

    # 设置wkhtmltopdf路径
    wkhtmltopdf_path = args.wkhtmltopdf_path or os.environ.get('WKHTMLTOPDF_PATH')

    # 执行转换
    convert_md_to_pdf(args.input, output, args.css, wkhtmltopdf_path)