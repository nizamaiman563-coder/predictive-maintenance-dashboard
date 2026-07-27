# ReliabilityIQ — Modern Streamlit Predictive Maintenance Dashboard

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Community Cloud

1. Upload every file and folder in this package to the same GitHub repository.
2. In Streamlit Community Cloud, select `app.py` as the main file.
3. Keep `.streamlit/config.toml` in the repository so the light theme and readable text colours are applied.

## Main improvements

- Clear, modern login page with visible labels and strong contrast.
- Custom industrial equipment logo and equipment-type symbols.
- Live system status, Malaysia time, data-file timestamp, and 15-second status refresh.
- Modern sidebar navigation and authenticated-user indicator.
- Improved KPI cards, priority equipment cards, charts, maintenance due status, filters, and export controls.
- Safer file path handling using the folder containing `app.py`.

## Prototype login accounts

The original prototype credentials remain in `app.py`. Replace the hard-coded `USERS` dictionary with Streamlit Secrets or another secure authentication service before production use.
