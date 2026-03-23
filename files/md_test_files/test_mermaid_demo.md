# Mermaid 图表测试

这是一个测试文档，用于验证 Mermaid 图表转 DOCX 功能。

## 流程图示例

```mermaid
graph TD
    A[开始] --> B{判断条件}
    B -->|选项1| C[结果1]
    B -->|选项2| D[结果2]
    C --> E[结束]
    D --> E

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style E fill:#9f9,stroke:#333,stroke-width:2px
```

## 时序图示例

```mermaid
sequenceDiagram
    participant 用户
    participant 系统
    participant 数据库

    用户->>系统: 发送请求
    系统->>数据库: 查询数据
    数据库-->>系统: 返回结果
    系统-->>用户: 响应数据
```

## 文本内容

除了图表外，文档还包含普通文本内容，用于验证 Markdown 的基本转换功能。

- 列表项 1
- 列表项 2
- 列表项 3

## 数学公式测试

行内公式：$E = mc^2$

块级公式：
$$
\sum_{i=1}^n i = \frac{n(n+1)}{2}
$$

## 表格测试

| 列1 | 列2 | 列3 |
|-----|-----|-----|
| A   | B   | C   |
| D   | E   | F   |
