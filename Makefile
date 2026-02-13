VENV_DIR := .venv

.PHONY: clean run-pmu-reader run-harmonics-study run-harmonics-notebook

clean:
	rm -rf $(VENV_DIR) temp/ results/

run-pmu-reader:
	@echo "Checking virtual environment..."
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Creating virtual environment..."; \
		python -m venv $(VENV_DIR); \
	fi
	@echo "Activating virtual environment and installing dependencies..."
	@bash -c "source $(VENV_DIR)/Scripts/activate && python -m pip install --upgrade pip && pip install -r requirements.txt"
	@echo "Running PMU data reader..."
	@bash -c "source $(VENV_DIR)/Scripts/activate && python src/temp/temp-pmu-data-reader.py"

run-harmonics-study:
	@echo "Checking virtual environment..."
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Creating virtual environment..."; \
		python -m venv $(VENV_DIR); \
	fi
	@echo "Activating virtual environment and installing dependencies..."
	@bash -c "source $(VENV_DIR)/Scripts/activate && python -m pip install --upgrade pip && pip install -r requirements.txt"
	@echo "Running harmonics study..."
	@bash -c "source $(VENV_DIR)/Scripts/activate && python src/temp/harmonics-study.py"

run-harmonics-notebook:
	@echo "Checking virtual environment..."
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Creating virtual environment..."; \
		python -m venv $(VENV_DIR); \
	fi
	@echo "Activating virtual environment and installing dependencies..."
	@bash -c "source $(VENV_DIR)/Scripts/activate && python -m pip install --upgrade pip && pip install -r requirements.txt && pip install jupyter nbconvert"
	@echo "Running harmonics study notebook..."
	@bash -c "source $(VENV_DIR)/Scripts/activate && cd src/temp && jupyter nbconvert --to notebook --execute harmonics-study.ipynb --output harmonics-study-executed.ipynb"
