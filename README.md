# SEO Command Center

The SEO Command Center is a professional-grade tool for auditing Screaming Frog SEO exports. It transforms raw crawl data into actionable insights, providing deterministic rule-based detection, LLM-powered fixes, and client-ready reports.

## 🚀 Quick Start

### 1. Installation
Ensure you have Python 3.10+ installed. Install the required dependencies:

```bash
pip install mcp python-pptx
```

**Note:** To enable the AI-powered Title Fixer, ensure [Ollama](https://ollama.com/) is running locally with the `gemma4:31b` model:
```bash
ollama pull gemma4:31b
```

### 2. Running the Audit
Run the headless pipeline on any Screaming Frog export directory:

```bash
python run.py path/to/your-export-folder/
```

While the audit is running, you can monitor the progress in real-time via the **Live Dashboard**:
👉 [http://localhost:7700](http://localhost:7700)

## 📊 Generated Outputs
The tool produces a comprehensive set of deliverables in the `outputs/` directory:

| File | Description |
| :--- | :--- |
| `report.json` | Full machine-readable audit data for integration. |
| `report.html` | **Client-Ready Report**: Professional, color-coded HTML dashboard with summary stats and prioritized issues. |
| `report.pptx` | **Executive Presentation**: 5-slide summary including criticality breakdown and top recommendations. |

## 🏗️ Architecture Overview

The system follows a modular pipeline orchestrated by a set of specialized sub-agents:

### 1. Ingest & Auditor Agent
- **Ingest**: Parses `internal_all.csv` and other Screaming Frog exports.
- **Auditor**: Executes deterministic SEO rules (defined in `seo/detector.py`) to identify issues such as missing titles, duplicate H1s, broken links (4xx/5xx), and thin content.

### 2. Fixer Agent
- **Intelligence**: Leverages local LLMs (via Ollama) to analyze problematic pages.
- **Remediation**: Automatically generates optimized, professional SEO titles based on page H1s or URL slugs, ensuring they stay within the 30-60 character sweet spot.

### 3. Reporter Agent
- **Synthesis**: Aggregates findings into a prioritized list based on severity (High $\to$ Medium $\to$ Low).
- **Delivery**: Translates technical data into high-fidelity formats (HTML, JSON, PPTX) suitable for stakeholders and clients.

## 📁 Project Structure
- `seo/detector.py`: The core engine for deterministic issue detection.
- `mcp/server.py`: MCP server that powers the tools and the localhost dashboard.
- `run.py`: Headless entry point for end-to-end audit execution.
- `dashboard/`: Frontend assets for the live monitoring cockpit.
