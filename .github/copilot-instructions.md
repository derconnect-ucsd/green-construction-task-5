# Copilot Instructions for Green Construction Task 5

## Project Overview
This project focuses on analyzing PMU (Phasor Measurement Unit) data, meter data, and load profiles for green construction initiatives. The workspace contains utilities for processing electrical grid data and energy consumption patterns.

## Code Organization Guidelines

### Directory Structure
- `src/utils/` - Reusable utility functions (keep these clean and well-documented)
- `src/temp/` - Temporary development files, test scripts, and experimental code
- `src/visualizers/` - Data visualization and plotting utilities
- `data/raw/` - Raw data files (do not modify)
- `data/results/` - Processed data and analysis outputs
- `data/temp/` - Temporary data files and intermediate processing results

### File Management Best Practices

#### Temporary Files Cleanup
When creating temporary files during development or testing:

1. **Test and Demo Scripts**: Files like `test_*.py`, `demo_*.py`, or `example_*.py` in `src/temp/` should be cleaned up after successful integration into main utilities.

2. **Temporary Data Files**: 
   - Files in `data/temp/` should be cleaned up regularly
   - CSV exports from testing should be moved to `data/results/` if needed for future reference
   - Binary test files should be removed after validation

3. **Development Artifacts**:
   - Remove debugging print statements from final code
   - Clean up commented-out experimental code
   - Remove unused imports and variables

4. **Before Committing**:
   - Review `src/temp/` directory and remove files that are no longer needed
   - Ensure only essential temporary files remain for ongoing development
   - Move any valuable code from temp files into proper utility modules

#### Specific Cleanup Actions
- Remove `demo_pmu_utils.py` and `test_pmu_utils.py` after PMU utilities are validated and integrated
- Clean up any temporary `.signal` files created during testing
- Remove intermediate CSV files unless they contain valuable analysis results
- Clear out any temporary notebooks or scratch files

### PMU Data Processing Guidelines

#### File Naming Conventions
PMU signal files must follow the format: `YYYYMMDD,HHMMSS.microseconds,frequency,datatype.signal`

#### Utility Usage
- Use functions from `src/utils/utils-pmu.py` for all PMU data processing
- Prefer `read_pmu_signal_file()` for standard processing
- Use `get_pmu_file_info()` for metadata without loading large datasets
- Use `read_pmu_signal_file_safe()` when error handling is critical

#### Error Handling
- Always handle `PMUDataError` exceptions when processing PMU files
- Validate file existence and format before processing
- Log processing steps for debugging and monitoring

### Code Quality Standards

#### Documentation
- Add docstrings to all functions in utility modules
- Include usage examples in complex utility functions
- Document expected file formats and data structures

#### Error Handling
- Use custom exceptions for domain-specific errors
- Provide clear error messages that help with debugging
- Log errors appropriately for production use

#### Testing
- Create test scripts in `src/temp/` during development
- Validate utilities with real data files before integration
- Clean up test files after successful validation

### Data Processing Workflow

1. **Development Phase**: Create experimental scripts in `src/temp/`
2. **Testing Phase**: Validate with sample data, create test scripts
3. **Integration Phase**: Move proven code to appropriate utility modules
4. **Cleanup Phase**: Remove temporary files and clean up code
5. **Documentation Phase**: Update documentation and examples

## Maintenance Tasks

### Regular Cleanup Checklist
- [ ] Review and clean `src/temp/` directory
- [ ] Remove unnecessary files from `data/temp/`
- [ ] Update utility documentation
- [ ] Validate that all imports are used
- [ ] Check for and remove debugging code
- [ ] Ensure proper error handling in all utilities

### Before Major Commits
- [ ] Run cleanup checklist
- [ ] Test all utility functions
- [ ] Update project documentation
- [ ] Verify directory structure is maintained

## Notes for AI Assistant
- Always consider the temporary nature of files in `src/temp/` and `data/temp/`
- Suggest cleanup actions when appropriate
- Prioritize code organization and maintainability
- Focus on creating reusable, well-documented utilities
- Consider file management as part of the development workflow
