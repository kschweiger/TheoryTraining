# Theory Training


## Setup:

1. Install required packages: `pip install -r requirements.txt`
2. Compile the resources: `cd theorytraining; pyside2-rcc resources.qrc -o resources.py; cd .`

Run the main application with: `python theorytraining/mainWindow.py`

## Packaging

### Pyinstaller (WiP)

Additionally install pyinstaller `pip install pyinstaller`

Run pyinstaller:

```bash
pyinstaller \
  --name "Theory Training" \
  --windowed \
  theorytraining/mainWindow.py
```

