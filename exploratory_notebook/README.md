# Exploratory Notebook

This repository contains an exploratory Jupyter notebook named `exploratory_notebook.ipynb`. 
This notebook is used to demonstrate, the core concepts of the project.

## Prerequisites
- Python 3.6 or higher
- Jupyter Notebook, Jupiter Lab or any other notebook viewer (VS Code, PyCharm, etc.)

## Installation
Install the required packages using the following command:
```bash
pip install -r requirements.txt
```

## Usage
Run all the cells in the notebook to understand the core concepts of the project.
After the first run, you will have a delta table created in the `data` folder.

If you change the files under "files_examples" and don't clear the delta folder, the notebook will not update the delta table.
I did not implement the logic to update the delta table if the files are changed.

## License
Take it and use it as you want. No restrictions.
