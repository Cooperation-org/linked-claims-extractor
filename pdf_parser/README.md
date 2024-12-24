# Parse PDF files into verifiable claims

## Local development/testing

From the root directory of this repo run

`./setup_local_dev.sh`

or if you prefer, create your virtualenv manually and run

```
pip install -r requirements.txt
pip install -e .
```

Then, to exercise the code, you may run

To start a REPL:

`python src/main.py`


To iterate thru a PDF and output HTML visualizing all the claims:

`python src/claim_viz.py`
