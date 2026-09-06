# Contributing to EdgeShield Mesh

Thank you for your interest in contributing to **EdgeShield Mesh**! We welcome contributions from IoT security researchers, backend developers, frontend designers, and agricultural engineers.

---

## Development Setup

1. **Fork and Clone the Repository**:
   ```bash
   git clone https://github.com/vijaymahes9080/EdgeShield-Mesh.git
   cd EdgeShield-Mesh
   ```

2. **Backend Setup**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Frontend Setup**:
   ```bash
   cd apps/web
   npm install
   npm run dev
   ```

4. **Running Tests**:
   ```bash
   pytest tests/ -v
   python tests/evaluation/benchmark_runner.py
   npm run build --prefix apps/web
   ```

---

## Code Style & Guidelines

- **Python**: Follow PEP 8 guidelines. Use strict type annotations with Pydantic v2.
- **TypeScript**: Strict types with interfaces in `apps/web/src/types.ts`.
- **Security**: Never commit real production credentials or secrets. Ensure all new MCP tools have strict Pydantic input/output schemas.
