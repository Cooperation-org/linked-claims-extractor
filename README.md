# Linked Claims Extractor and PDF Parser

This repository contains two independent projects for extracting and processing claims from text, URLs, and PDFs using AI-powered language models (LLMs). Both projects will be published to PyPI, currently the extractor is published.

## Projects

1. **[Linked Claims Extractor](./claim_extractor/README.md)**: Extracts structured claims from unstructured text, URLs, or PDFs using AI models like Anthropic and OpenAI.
2. **[PDF Parser](./pdf_parser/README.md)**: Processes PDF files into structured chunks of text and images, making it easier to analyze and verify claims.

---

## Installation

Each project will be installed independently via PyPI:

### Linked Claims Extractor
```bash
pip install linked-claims-extractor
```

### PDF Parser
PyPI tbd

For now install manually by following the instructions in the readme

---

## Production Deployment

The PDF Parser includes comprehensive deployment documentation for production environments:

### Deployment Guides
- **[Production Deployment Guide](./pdf_parser_DEPLOYMENT_GUIDE.MD)**: Complete guide for deploying the PDF Parser to production servers, including server setup, SSL configuration, and domain management.
- **[Maintenance & Updates Guide](./pdf_parser_MAINTAINANCE_GUIDE.md)**: Step-by-step instructions for maintaining the production deployment, updating code from GitHub, monitoring logs, and troubleshooting common issues.

### Quick Production Setup
The PDF Parser can be deployed as a production web service with:
- ✅ **Systemd service management** for auto-restart and process monitoring
- ✅ **Nginx reverse proxy** with SSL/TLS encryption
- ✅ **Let's Encrypt SSL certificates** with automatic renewal
- ✅ **Comprehensive logging** and monitoring setup
- ✅ **GitHub integration** for seamless code updates

**Live Demo**: [https://extract.linkedtrust.us](https://extract.linkedtrust.us)

---

## Contributing

Contributions are welcome! Please refer to the individual project READMEs for contribution guidelines.

For production deployments, see the deployment guides in the `docs/` directory for server access and maintenance procedures.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.