
# Trustworthy AI Course 2026 Submission

## Setup Instructions

### Creating a Virtual Environment with `uv`

To ensure reproducibility, this project uses `uv` for virtual environment management.

1. Install `uv` if you haven't already:
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2. Create a virtual environment:
    ```bash
    uv venv
    ```

3. Activate the virtual environment:
    ```bash
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

4. Install dependencies:
    ```bash
    uv pip install -r requirements.txt
    ```

### Using `uv` Virtual Environment with Jupyter in VS Code

For detailed instructions on configuring Jupyter notebooks in VS Code with `uv` virtual environments, see this guide:
[Create Virtual Environments with uv to Use Jupyter Notebooks Inside VS Code](https://medium.com/@luismarcelobp/create-virtual-environments-with-uv-to-use-jupyter-notebooks-inside-vs-code-48f336023e7f)
