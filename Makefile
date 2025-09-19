VENV_DIR := .venv

.PHONY: clean run-pmu-reader

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
	@bash -c "source $(VENV_DIR)/Scripts/activate && python src/temp/pmu-data-reader.py"
