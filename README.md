
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
    uv sync
    ```
### Main notebook for submission
The `ulaanbaatar_mn_realestate_salary_nb.ipynb` file is the submission file. In this notebook, I've downloaded statistical data about realestate prices and average household income from the Mongolian statistical office website (1212.mn) and visualized the aspects of price/income ratio as chart. 


### Using `uv` Virtual Environment with Jupyter in VS Code

For detailed instructions on configuring Jupyter notebooks in VS Code with `uv` virtual environments, see this guide:
[Create Virtual Environments with uv to Use Jupyter Notebooks Inside VS Code](https://medium.com/@luismarcelobp/create-virtual-environments-with-uv-to-use-jupyter-notebooks-inside-vs-code-48f336023e7f)
