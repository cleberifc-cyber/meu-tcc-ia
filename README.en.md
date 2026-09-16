# TCC Kit

An open, local-first toolkit to organize a Brazilian undergraduate thesis (TCC), retrieve DOI metadata, check citation keys, and export an editable DOCX.

The included formatting profile is `preview`, not a verified or current ABNT compliance claim. See the [Portuguese README](README.md), [quick start](docs/quickstart.md), [profile status](docs/abnt/profile-status.md), and [privacy notes](docs/privacy.md).

Quick start: install Python 3.11+ and Git, clone this repository, run `python -m pip install -e .`, create a new project with `tcc-kit init ./my-thesis`, then run `tcc-kit format ./my-thesis --format docx`. DOI lookup is opt-in and sends only the DOI to public metadata registries; thesis text stays local unless you choose to share it elsewhere.

## Support the project

Code, documentation, and issue reports are welcome. If you prefer to contribute financially, an optional USDT address on the TRON network (TRC20) is:

```text
TQCMKPwkQwGCz31se4X4BqbzzFfmj7XK8D
```

Send USDT only over TRON/TRC20. Carefully verify the network, asset, and address in your wallet before sending; crypto transfers may be irreversible and network fees may apply. Support is voluntary and does not include benefits or guarantee a response or outcome. Never share your seed phrase or private key.
