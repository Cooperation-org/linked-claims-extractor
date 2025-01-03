# Parse PDF Files into Verifiable Claims

This project processes PDF files into structured chunks of text and images, making it easier to analyze and verify claims. It is designed to work alongside the **Linked Claims Extractor** for extracting and visualizing claims from PDFs.

---

## Local Development and Testing

### Quick Setup
From the root directory of this repo, run the setup script:

```bash
./setup_local_dev.sh
```

Alternatively, you can set up the environment manually:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

---

## Running the Code

### Start a REPL (Read-Eval-Print Loop)
To interact with the code in a Python REPL:

```bash
python src/main.py
```

### Visualize Claims from a PDF
To process a PDF and generate an HTML file visualizing all the claims:

```bash
python src/claim_viz.py
```

---

## Local Development with `claim_extractor`

If you are modifying both this project and the `claim_extractor` package simultaneously, you can force the use of the local `claim_extractor` as follows:

1. Make changes to the `claim_extractor` files, including updating the version in `setup.py`.
2. Uninstall the existing `linked-claims-extractor` package:

   ```bash
   pip uninstall linked-claims-extractor
   ```
3. Install the local version of `claim_extractor`:

   ```bash
   pip install -e ../claim_extractor
   ```
4. Verify that the new version is installed:

   ```bash
   pip list | grep linked-claims-extractor
   ```

---

## Contributing

Contributions are welcome! If you'd like to contribute, please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with a detailed description of your changes.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
