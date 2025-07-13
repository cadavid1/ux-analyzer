# UX Heuristics Analyzer

An interactive Streamlit webapp that analyzes digital interfaces against comprehensive UX principles to identify potential usability issues and provide actionable recommendations.

## Features

### 🎯 Comprehensive Analysis
- **10 UX Heuristic Categories**: Analyzes against proven UX principles including cognitive load, error prevention, attention management, and more
- **53 Detailed Checkpoints**: Each category contains specific evaluation criteria for thorough assessment
- **AI-Powered Evaluation**: Uses advanced AI to provide intelligent analysis and recommendations

### 📊 Multiple Input Methods
- **Image Upload**: Analyze screenshots or images of your interface (PNG, JPG, JPEG)
- **Video Upload**: Analyze video recordings of user interactions (MP4, MOV, AVI)
- **Website URL**: Automatically capture and analyze live websites

### 📈 Rich Results Display
- **Overall UX Score**: Get a comprehensive score out of 100
- **Category Breakdown**: See performance across all 10 UX categories with progress bars
- **Detailed Checkpoints**: Expandable sections showing pass/fail status for each criterion
- **Priority Issues**: Top issues that need immediate attention
- **Strengths**: Areas where your design excels
- **Actionable Recommendations**: Specific suggestions for improvement

## UX Heuristic Categories

1. **People Don't Want to Work** - Minimize user effort and cognitive load
2. **People Have Limitations** - Respect cognitive and physical limitations
3. **People Make Mistakes** - Error prevention and recovery mechanisms
4. **Human Memory Is Complicated** - Don't rely on user memory
5. **People are Social** - Leverage social behaviors and validation
6. **Attention** - Manage focus and attention effectively
7. **People Crave Information** - Provide appropriate feedback and information
8. **Unconscious Processing** - Consider subconscious design factors
9. **People Create Mental Models** - Match user expectations and mental models
10. **Visual System** - Optimize visual design and hierarchy

## Installation

### Prerequisites
- Python 3.11+
- Chrome browser (for website analysis)

### Setup
1. Clone or download the project files
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up OpenAI API key:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   export OPENAI_API_BASE="your-api-base-url"
   ```

### Running the Application
```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

The application will be available at `http://localhost:8501`

## Usage Guide

### Analyzing Images
1. Select "📷 Image Upload" from the sidebar
2. Upload an image file (PNG, JPG, JPEG)
3. Click "Analyze Image"
4. View comprehensive results with scores and recommendations

### Analyzing Videos
1. Select "🎥 Video Upload" from the sidebar
2. Upload a video file (MP4, MOV, AVI)
3. Click "Analyze Video"
4. The system will extract key frames and analyze them

### Analyzing Websites
1. Select "🌐 Website URL" from the sidebar
2. Enter the website URL (e.g., example.com)
3. Click "Analyze Website"
4. The system will capture a screenshot and analyze it

### Understanding Results

#### Overall Score
- **85-100**: Excellent UX design
- **70-84**: Good UX with minor improvements needed
- **50-69**: Fair UX requiring attention
- **Below 50**: Poor UX needing significant improvements

#### Category Scores
Each category shows:
- Percentage score with color coding
- Progress bar visualization
- Expandable checkpoint details

#### Checkpoints
- ✅ **PASS**: Criterion is well implemented
- ❌ **FAIL**: Criterion needs improvement
- ⚠️ **ATTENTION**: Criterion partially meets requirements

#### Recommendations
Each failed or attention checkpoint includes:
- **Reasoning**: Why the issue was identified
- **Recommendation**: Specific actionable advice for improvement

## File Structure

```
ux-heuristics-analyzer/
├── app.py                          # Main Streamlit application
├── ux_analyzer.py                  # Core analysis engine
├── website_capture.py              # Website screenshot functionality
├── ux_heuristics_structured.json   # UX heuristics database
├── requirements.txt                # Python dependencies
├── README.md                       # This documentation
└── UXHEURISTICS.xlsx              # Original heuristics data
```

## Technical Details

### Architecture
- **Frontend**: Streamlit with custom CSS styling
- **Backend**: Python with OpenAI API integration
- **Image Processing**: Pillow and OpenCV
- **Web Automation**: Selenium with Chrome WebDriver
- **AI Analysis**: OpenAI GPT-4.1-mini for intelligent evaluation

### Analysis Process
1. **Input Processing**: Handle uploaded files or capture website screenshots
2. **AI Analysis**: Send content to OpenAI API with structured prompts
3. **Result Processing**: Parse AI response into structured format
4. **Score Calculation**: Calculate category and overall scores
5. **Display**: Present results with rich visualizations

### Data Structure
The analysis results follow this structure:
```json
{
  "overall_score": 72,
  "summary": "Analysis summary...",
  "categories": {
    "01": {
      "title": "Category name",
      "score": 65,
      "checkpoints": {
        "01.01": {
          "text": "Checkpoint description",
          "status": "PASS|FAIL|ATTENTION",
          "reasoning": "AI reasoning",
          "recommendation": "Improvement suggestion"
        }
      }
    }
  },
  "priority_issues": ["Issue 1", "Issue 2"],
  "strengths": ["Strength 1", "Strength 2"]
}
```

## Customization

### Adding New Heuristics
1. Edit `ux_heuristics_structured.json`
2. Add new categories or checkpoints
3. Update the analysis prompts in `ux_analyzer.py`

### Styling
- Modify CSS in `app.py` to change appearance
- Update color schemes and layouts as needed

### AI Model
- Change the model in `ux_analyzer.py` (line 108)
- Adjust prompts for different analysis styles

## Troubleshooting

### Common Issues

**Chrome Driver Issues**
- Ensure Chrome browser is installed
- WebDriver Manager handles driver installation automatically

**OpenAI API Errors**
- Verify API key is set correctly
- Check API quota and billing status
- Ensure model name is supported

**Memory Issues**
- Large video files may cause memory issues
- Consider reducing video resolution or length

**Slow Analysis**
- AI analysis can take 30-60 seconds
- Network speed affects processing time

### Error Messages
- **"Analysis failed: Error code: 400"**: Check OpenAI API configuration
- **"Screenshot capture failed"**: Website may block automated access
- **"File too large"**: Reduce file size or resolution

## Contributing

To contribute to this project:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For support or questions:
- Check the troubleshooting section
- Review error messages carefully
- Ensure all dependencies are installed correctly

## Acknowledgments

- UX heuristics based on established usability principles
- Powered by OpenAI's advanced language models
- Built with Streamlit for rapid prototyping and deployment

