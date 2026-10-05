import json

with open("web/api/mpt_generator.py", "r") as f:
    code = f.read()

notebook = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Modern Portfolio Theory (MPT) - 9 ETF Indian Portfolio\n",
    "This notebook contains the latest source code powering our API. It includes the updated 9-ETF universe (with `SETF10GILT.NS`) and the improved mathematical engine for generating the automated PDF reports."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [line + '\n' for line in code.split('\n')]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.11.0"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}

with open("notebooks/v-02_exploratory_analysis.ipynb", "w") as f:
    json.dump(notebook, f, indent=1)
print("Notebook created successfully.")
