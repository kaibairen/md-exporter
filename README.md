# Markdown 转 PDF/DOCX 工具

一个功能强大的 Markdown 转换工具，支持将 Markdown 文件转换为 PDF 和 DOCX 格式，支持 Mermaid 图表、LaTeX 公式、代码高亮等功能。

## 功能特性

### PDF 转换 (md2pdf)
- ✅ LaTeX 公式渲染（KaTeX）
- ✅ Mermaid 图表支持（流程图、序列图、甘特图、象限图等）
- ✅ 代码语法高亮（Pygments）
- ✅ 自定义 CSS 样式
- ✅ 中文字体支持

### DOCX 转换 (md2docx)
- ✅ Mermaid 图表转 PNG 图片
- ✅ 图片尺寸自动控制
- ✅ 可选图片边框
- ✅ 自定义 DOCX 模板
- ✅ 代码语法高亮
- ✅ 自动修复中文引号问题

## 安装

### 1. 克隆项目

```bash
git clone <repository-url>
cd md_exporter
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 安装 Playwright 浏览器（仅 DOCX 转换需要）

```bash
playwright install chromium
```

## 使用方法

### 统一入口（推荐）

项目提供了统一的命令行入口 `main.py`，支持所有 PDF 和 DOCX 转换功能：

```bash
# 转换为 PDF
python main.py pdf -i input.md -o output.pdf

# 转换为 PDF（自定义样式）
python main.py pdf -i input.md -o output.pdf -c custom_style.css

# 转换为 DOCX（默认三线表样式）
python main.py docx -i input.md -o output.docx

# 转换为 DOCX（条纹表样式）
python main.py docx -i input.md -o output.docx --table-style academic_striped

# 转换为 DOCX（高质量 Mermaid + 图片边框）
python main.py docx -i input.md -o output.docx --mermaid-dpi 600 --add-image-border

# 查看完整帮助
python main.py --help
python main.py pdf --help
python main.py docx --help
```

### 直接调用模块

#### PDF 转换

#### 基本用法

```bash
python md2pdf/playwright_md.py -i input.md -o output.pdf
```

#### 使用自定义样式

```bash
python md2pdf/playwright_md.py -i input.md -o output.pdf -c custom_style.css
```

#### 完整参数说明

```bash
python md2pdf/playwright_md.py \
    -i input.md \
    -o output.pdf \
    -c custom_style.css \
    --timeout 60000
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-i, --input` | 输入 Markdown 文件 | 必需 |
| `-o, --output` | 输出 PDF 文件 | 必需 |
| `-c, --css` | 自定义 CSS 样式文件 | `style.css` |
| `--timeout` | 渲染超时时间（毫秒） | 60000 |
| `--init` | 初始化本地资源 | - |

### DOCX 转换

#### 常用用法

```bash
# 基本转换
python md2docx/docx_md.py -i input.md -o output.docx

# 使用默认模板
python md2docx/docx_md.py -i input.md -o output.docx --use-default-template

# 使用自定义模板
python md2docx/docx_md.py -i input.md -o output.docx -t my_template.docx

# 控制图片尺寸（默认：宽16cm，高25cm）
python md2docx/docx_md.py -i input.md -o output.docx \
    --max-image-width-cm 15 \
    --max-image-height-cm 20

# 添加图片边框
python md2docx/docx_md.py -i input.md -o output.docx --add-image-border

# 禁用 Mermaid 图表处理
python md2docx/docx_md.py -i input.md -o output.docx --no-mermaid

# 禁用表格样式化
python md2docx/docx_md.py -i input.md -o output.docx --no-table-enhance

# 转换后自动清理临时图片
python md2docx/docx_md.py -i input.md -o output.docx --cleanup
```

#### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-i, --input` | 输入 Markdown 文件 | 必需 |
| `-o, --output` | 输出 DOCX 文件 | 可选（自动生成） |
| `-t, --template` | 自定义 DOCX 模板路径 | - |
| `--use-default-template` | 使用默认模板 | False |
| `--table-style` | 表格样式（可选值见示例 4） | `academic_three_line` |
| `--no-table-enhance` | 禁用表格样式化 | False |
| `--mermaid-images-dir` | Mermaid 图片保存目录 | `files/temp_mermaid_images` |
| `--mermaid-dpi` | Mermaid 图表 DPI (96-600) | 600 |
| `--max-image-width-cm` | 图片最大宽度（厘米） | 16.0 |
| `--max-image-height-cm` | 图片最大高度（厘米） | 25.0 |
| `--add-image-border` | 添加图片边框 | False |
| `--no-mermaid` | 禁用 Mermaid 处理 | False |
| `--cleanup` | 转换后清理临时文件 | False |
| `-v, --verbose` | 详细日志输出 | False |

## Markdown 语法支持

### Mermaid 图表

支持所有 Mermaid 图表类型：

### LaTeX 公式

#### 行内公式

```
这是一个行内公式 $E = mc^2$ 的示例。
```

#### 块级公式

```
$$
\min_{w \in \mathbb{R}^d} F(w) = \frac{1}{n} \sum_{i=1}^n f_i(w)
$$
```

### 代码高亮

````python
def hello_world():
    print("Hello, World!")
````

## 高级用法

### 作为 Python 模块使用

#### PDF 转换

```python
from md2pdf.playwright_md import PlaywrightMdPdfConverter

# 创建转换器
converter = PlaywrightMdPdfConverter(
    css_path="custom_style.css",
    timeout=60000
)

# 转换文本
converter.convert_to_pdf(
    text="# Hello World\n\n这是测试内容。",
    output_file="output.pdf"
)

# 转换文件
converter.convert_file_to_pdf(
    input_file="input.md",
    output_file="output.pdf"
)
```

#### DOCX 转换

```python
from md2docx.docx_md import PandocMdDocxConverter

# 创建转换器
converter = PandocMdDocxConverter(
    template_path="custom_template.docx",
    max_image_width_cm=16.0,
    max_image_height_cm=25.0,
    add_image_border=True
)

# 转换文件
converter.convert_file_to_docx(
    input_file="input.md",
    output_file="output.docx",
    process_mermaid=True,
    cleanup_temp=False
)
```

### 批量转换

```python
from pathlib import Path
from md2pdf.playwright_md import convert_md_file_to_pdf_playwright
from md2docx.docx_md import PandocMdDocxConverter

# 批量转换为 PDF
md_files = Path("documents").glob("*.md")
for md_file in md_files:
    pdf_file = md_file.with_suffix(".pdf")
    convert_md_file_to_pdf_playwright(str(md_file), str(pdf_file))
    print(f"Converted: {md_file} -> {pdf_file}")

# 批量转换为 DOCX
converter = PandocMdDocxConverter()
for md_file in md_files:
    docx_file = md_file.with_suffix(".docx")
    converter.convert_file_to_docx(str(md_file), str(docx_file))
    print(f"Converted: {md_file} -> {docx_file}")
```

## 常见问题

### 1. Mermaid 图表无法显示

**问题**：转换后的文档中 Mermaid 图表位置显示为空白或原始代码。

**解决方案**：
- 确保已安装 Playwright 浏览器：`playwright install chromium`
- 检查网络连接，首次运行需要下载 Mermaid 库
- 检查 Mermaid 语法是否正确（中文引号会自动转换为英文引号）
- 使用 `--verbose` 参数查看详细日志

### 2. 生成的图片模糊

**解决方案**：
- 提高 `--mermaid-dpi` 参数值（最高 600）
- DOCX: `python md2docx/docx_md.py -i input.md -o output.docx --mermaid-dpi 600`


### 3. 中文字体显示问题

**解决方案**：
- PDF: 在自定义 CSS 中指定中文字体
- DOCX: 在 Word 模板中设置默认中文字体



## 项目结构

```
md_exporter/
├── main.py              # 统一命令行入口（推荐使用）
├── requirements.txt     # 项目依赖
│
├── md2pdf/              # PDF 转换模块
│   ├── playwright_md.py # Playwright PDF 转换器（支持 LaTeX/Mermaid）
│   ├── style.css        # 默认样式
│   └── assets/          # 本地资源（KaTeX, Mermaid）
│
├── md2docx/             # DOCX 转换模块
│   ├── docx_md.py       # DOCX 转换器（支持 Mermaid/表格样式）
│   └── templates/       # DOCX 模板和样式配置
│       ├── docx_template.docx    # 默认 Word 模板
│       └── table_styles.py       # 表格样式配置（4 种学术样式）
│
├── md2common/           # 共享模块
│   └── async_utils.py   # 异步工具函数
│
└── files/               # 测试文件和输出目录
    ├── md_test_files/   # 测试 Markdown 文件
    ├── pdf/             # PDF 输出目录
    ├── docx/            # DOCX 输出目录
    └── temp_mermaid_images/ # Mermaid 图片缓存目录
```

## 示例

### 示例 1: 基本报告转换

```bash
# 转换为 PDF
python md2pdf/playwright_md.py \
    -i files/md_test_files/test_report.md \
    -o files/pdf/test_report.pdf

# 转换为 DOCX
python md2docx/docx_md.py \
    -i files/md_test_files/test_report.md \
    -o files/docx/test_report.docx
```

### 示例 2: 技术文档（带模板）

```bash
# 使用自定义 Word 模板
python md2docx/docx_md.py \
    -i technical_doc.md \
    -o technical_doc.docx \
    -t company_template.docx
```

### 示例 3: 大量图表的文档

```bash
# 高质量图片 + 图片边框
python md2docx/docx_md.py \
    -i diagrams_doc.md \
    -o diagrams_doc.docx \
    --mermaid-dpi 600 \
    --max-image-width-cm 18 \
    --max-image-height-cm 25 \
    --add-image-border
```

### 示例 4: 学术论文表格样式

本项目提供 **4 种学术表格样式**，通过 `--table-style` 参数选择：

| 样式名称 | 说明 | 适用场景 |
|---------|------|---------|
| `academic_three_line` | 三线表（默认） | 学术论文、毕业设计 |
| `academic_striped` | 条纹表 | 数据密集型报告 |
| `simple_grid` | 简单网格 | 通用文档 |
| `minimal` | 极简表格 | 现代简洁风格 |

```bash
# 使用三线表样式（默认）
python md2docx/docx_md.py \
    -i academic_paper.md \
    -o paper.docx

# 使用条纹表样式
python md2docx/docx_md.py \
    -i data_report.md \
    -o report.docx \
    --table-style academic_striped

# 禁用表格样式化（保持 Pandoc 默认样式）
python md2docx/docx_md.py \
    -i simple_doc.md \
    -o output.docx \
    --no-table-enhance
```

## 技术细节

### PDF 转换流程

1. Markdown → HTML（Python-Markdown）
2. 插入 KaTeX 和 Mermaid 脚本
3. Playwright 渲染 HTML
4. 等待 Mermaid 图表完成渲染
5. 生成 PDF（打印背景）

### DOCX 转换流程

1. Markdown → Pandoc HTML（保留 Mermaid 代码块）
2. Playwright 渲染 Mermaid → PNG（高 DPI）
3. PNG 图片尺寸调整（按厘米计算）
4. Pandoc 转换为 DOCX
5. **应用学术表格样式**（python-docx 后处理）
   - 读取生成的 DOCX
   - 应用选定样式（边框、背景、字体）
   - 保存优化后的文档

### DPI 和尺寸计算

- DPI = 600（最高质量）
- 1 英寸 = 2.54 厘米
- 像素转厘米：`cm = pixels * 2.54 / DPI`
- 例如：6000 像素 ÷ 600 DPI × 2.54 = 25.4 厘米

## 许可证

本项目遵循 MIT 许可证。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 更新日志

### v1.0.0 (2024-02-10)
- ✅ 支持 PDF 和 DOCX 转换
- ✅ Mermaid 图表完整支持
- ✅ LaTeX 公式渲染
- ✅ 代码语法高亮
- ✅ 图片尺寸自动控制
- ✅ 浏览器后台关闭优化
- ✅ 中文引号自动修复
- ✅ **4种学术表格样式**（三线表、条纹表、简单网格、极简表格）
- ✅ 表格样式配置文件（可自定义）
