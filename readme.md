# Insurance Claim Assistant

A Streamlit application that uses LLaVA (Language-and-Vision Assistant) for automated insurance claim assessment. The app analyzes images of damage along with descriptions to provide structured assessments and recommendations.

## Features

- **Multimodal Analysis**: Process both images and text descriptions
- **Comprehensive Assessment**:
  - Damage analysis and severity assessment
  - Repair requirements estimation
  - Consistency verification
- **Structured Reports**:
  - Detailed analysis for each image
  - Downloadable Excel reports
  - Claim tracking and management

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/insurance-claim-assistant.git
cd insurance-claim-assistant
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install requirements:
```bash
pip install -r requirements.txt
```

### Requirements
- Python 3.10.7
- Dependencies:
  ```
  streamlit==1.31.0
  pandas==2.0.3
  Pillow==10.0.0
  openai==1.12.0
  openpyxl==3.1.2
  ```

## Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Using the interface:
   - Fill in claim information
   - Upload damage images
   - Provide incident description
   - Generate and download analysis report

### Assessment Components

1. **Damage Analysis**
   - Type and extent of damage
   - Severity assessment
   - Affected areas identification
   - Safety concerns

2. **Repair Assessment**
   - Required repairs
   - Replacement parts needed
   - Additional inspection recommendations

3. **Consistency Check**
   - Pattern analysis
   - Pre-existing damage identification
   - Incident consistency verification

## Model Details

The application uses LLaVA (Language-and-Vision Assistant) for image analysis:
```python
LLAVA_CONFIG = {
    "base_url": "http://3.15.181.146:8000/v1/",
    "model": "llava-v1.6-34b"
}
```

## Data Processing

1. **Image Processing**
   - Supports PNG, JPG, JPEG formats
   - Multiple image upload
   - Base64 encoding for API transmission

2. **Analysis Pipeline**
   - Image and description analysis
   - Structured data extraction
   - Report generation

3. **Report Generation**
   - Excel format with multiple sheets
   - Claim information summary
   - Individual image analyses
   - Downloadable format

## Limitations

- Image size and quality affect analysis accuracy
- Processing time increases with number of images
- Session state resets on application restart
- Specific format requirements for optimal results

## Best Practices

1. **Image Quality**
   - Use clear, well-lit images
   - Capture damage from multiple angles
   - Ensure good resolution
   - Avoid blurry or dark images

2. **Description Guidelines**
   - Provide detailed incident description
   - Include relevant context
   - Mention specific concerns
   - Use clear, specific language

3. **Analysis Process**
   - Upload images in logical sequence
   - Review each analysis before proceeding
   - Download reports for record-keeping
   - Verify critical findings

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
