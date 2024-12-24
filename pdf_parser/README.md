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

## Local development including changes to claim_extractor

If you are modifying both packages at once, force the use of the local claim_extractor as follows:

```
# make changes to ../claim_extractor files including the version
pip uninstall linked-claims-extractor
pip install -e ../claim_extractor
pip list | grep linked-claims-extractor
# make sure the new version shows up
```
