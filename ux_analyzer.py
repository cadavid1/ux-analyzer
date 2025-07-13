"""
UX Heuristics Analyzer - Core Analysis Engine
Analyzes images, videos, and websites against comprehensive UX principles
"""

import json
import base64
import os
from typing import Dict, List, Any, Optional
from openai import OpenAI
import streamlit as st
from langchain_openai import ChatOpenAI # type: ignore
from PIL import Image
import cv2 # type: ignore
import tempfile
import requests
from io import BytesIO
import copy

class UXAnalyzer:
    def __init__(self):
        """Initialize the UX Analyzer with heuristics data and OpenAI client"""
        openai_api_key = os.getenv("OPENAI_API_KEY") or st.secrets["OPENAI_API_KEY"]
        self.client = OpenAI(api_key=openai_api_key)
        self.llm = ChatOpenAI(
            temperature=1, model_name="gpt-4.1", openai_api_key=openai_api_key
        )
        with open("ux_heuristics_structured.json", "r", encoding="utf-8") as f:
            self.heuristics = json.load(f)

    def merge_with_all_heuristics(self, ai_result):
        """Ensure all heuristics/checkpoints are present in the result."""
        # Use deep copy to avoid mutating the original
        merged = copy.deepcopy(ai_result)
        
        # Ensure categories exists and is a dict
        if "categories" not in merged or not isinstance(merged["categories"], dict):
            merged["categories"] = {}
        
        # Fix malformed categories if they're in a list
        if isinstance(merged["categories"], list):
            categories_dict = {}
            for idx, cat in enumerate(merged["categories"], 1):
                if isinstance(cat, dict):
                    cat_id = cat.get("id", str(idx).zfill(2))
                    categories_dict[cat_id] = cat
            merged["categories"] = categories_dict
        
        # Ensure all categories from heuristics are present
        for cat_id, cat_data in self.heuristics.items():
            if cat_id not in merged["categories"]:
                # Add missing category
                merged["categories"][cat_id] = {
                    "title": cat_data["title"],
                    "score": 0,
                    "checkpoints": {}
                }
            
            # Ensure checkpoints exists and is a dict
            if "checkpoints" not in merged["categories"][cat_id]:
                merged["categories"][cat_id]["checkpoints"] = {}
            elif isinstance(merged["categories"][cat_id]["checkpoints"], list):
                # Convert list of checkpoints to dict
                checkpoints_dict = {}
                for cp in merged["categories"][cat_id]["checkpoints"]:
                    if isinstance(cp, dict):
                        cp_id = cp.get("id")
                        if cp_id:
                            checkpoints_dict[cp_id] = cp
                merged["categories"][cat_id]["checkpoints"] = checkpoints_dict
            
            # Add all checkpoints from heuristics
            for checkpoint in cat_data["checkpoints"]:
                cp_id = checkpoint["id"]
                if cp_id not in merged["categories"][cat_id]["checkpoints"]:
                    merged["categories"][cat_id]["checkpoints"][cp_id] = {
                        "text": checkpoint["text"],
                        "status": "NOT_EVALUATED",
                        "confidence": 0,
                        "reasoning": "",
                        "recommendation": ""
                    }
        
        return merged

    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64 for OpenAI API"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def _create_analysis_prompt(self) -> str:
        """Create the comprehensive analysis prompt for AI evaluation"""
        prompt = """You are a UX expert analyzing digital interfaces against proven usability heuristics. 

Analyze the provided content against these 10 UX heuristic categories:

"""
        
        for category_id, category in self.heuristics.items():
            prompt += f"\n{category_id}. {category['title']}\n"
            for checkpoint in category['checkpoints']:
                prompt += f"  - {checkpoint['id']}: {checkpoint['text']}\n"
                if checkpoint['description']:
                    prompt += f"    Context: {checkpoint['description']}\n"
        
        prompt += """

For each checkpoint, evaluate the content and provide:
1. Status: "PASS", "FAIL", or "NEEDS_ATTENTION"
2. Confidence: 1-5 (how certain you are about this evaluation)
3. Reasoning: Brief explanation of your assessment
4. Recommendation: Specific actionable advice (if issues found)

Return your analysis in this JSON format:
{
  "overall_score": 85,
  "summary": "Brief overall assessment",
  "categories": {
    "01": {
      "title": "People Don't Want to Work or Think More Than They Have To",
      "score": 80,
      "checkpoints": {
        "01.01": {
          "status": "PASS",
          "confidence": 4,
          "reasoning": "Interface minimizes user effort effectively",
          "recommendation": ""
        },
        "01.02": {
          "status": "FAIL", 
          "confidence": 5,
          "reasoning": "Too much information displayed at once",
          "recommendation": "Implement progressive disclosure with tabs or accordions"
        }
      }
    }
  },
  "priority_issues": [
    "Progressive disclosure needed for complex information",
    "Visual hierarchy could be improved"
  ],
  "strengths": [
    "Clear navigation structure",
    "Good use of whitespace"
  ]
}

Focus on practical, actionable insights that would help improve the user experience."""
        
        return prompt
    
    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """Analyze an image against UX heuristics"""
        try:
            # Encode image for API
            base64_image = self._encode_image(image_path)
            
            # Create analysis prompt
            prompt = self._create_analysis_prompt()
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=4000,
                temperature=0.1
            )
            
            # Parse response
            analysis_text = response.choices[0].message.content
            
            # Try to extract JSON from response
            try:
                if analysis_text is not None:
                    # Find JSON in the response
                    start_idx = analysis_text.find('{')
                    end_idx = analysis_text.rfind('}') + 1
                    json_str = analysis_text[start_idx:end_idx]
                    analysis_result = json.loads(json_str)
                else:
                    raise ValueError("No content returned from OpenAI API.")
            except (json.JSONDecodeError, ValueError, AttributeError):
                # Fallback if JSON parsing fails
                analysis_result = {
                    "overall_score": 75,
                    "summary": "Analysis completed but formatting issue occurred",
                    "raw_response": analysis_text,
                    "categories": {},
                    "priority_issues": ["Unable to parse detailed analysis"],
                    "strengths": []
                }
            
            merged_result = self.merge_with_all_heuristics(analysis_result)
            return merged_result
            
        except Exception as e:
            return {
                "error": f"Analysis failed: {str(e)}",
                "overall_score": 0,
                "summary": "Analysis could not be completed",
                "categories": {},
                "priority_issues": [],
                "strengths": []
            }
    
    def analyze_video(self, video_path: str, num_frames: int = 5) -> Dict[str, Any]:
        """Analyze a video by extracting key frames and analyzing them"""
        try:
            # Extract frames from video
            frames = self._extract_video_frames(video_path, num_frames)
            
            if not frames:
                return {
                    "error": "Could not extract frames from video",
                    "overall_score": 0,
                    "summary": "Video analysis failed",
                    "categories": {},
                    "priority_issues": [],
                    "strengths": []
                }
            
            # Analyze each frame and aggregate results
            frame_analyses = []
            for i, frame_path in enumerate(frames):
                analysis = self.analyze_image(frame_path)
                if 'error' not in analysis:
                    frame_analyses.append(analysis)
                # Clean up temporary frame file
                os.unlink(frame_path)
            
            if not frame_analyses:
                return {
                    "error": "No frames could be analyzed",
                    "overall_score": 0,
                    "summary": "Video analysis failed",
                    "categories": {},
                    "priority_issues": [],
                    "strengths": []
                }
            
            # Aggregate results from all frames
            aggregated_result = self._aggregate_video_analysis(frame_analyses)
            aggregated_result["frames_analyzed"] = len(frame_analyses)
            
            return aggregated_result
            
        except Exception as e:
            return {
                "error": f"Video analysis failed: {str(e)}",
                "overall_score": 0,
                "summary": "Video analysis could not be completed",
                "categories": {},
                "priority_issues": [],
                "strengths": []
            }
    
    def _extract_video_frames(self, video_path: str, num_frames: int) -> List[str]:
        """Extract evenly spaced frames from video"""
        frames = []
        try:
            cap = cv2.VideoCapture(video_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            if total_frames == 0:
                return frames
            
            # Calculate frame indices to extract
            frame_indices = [int(i * total_frames / num_frames) for i in range(num_frames)]
            
            for i, frame_idx in enumerate(frame_indices):
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if ret:
                    # Save frame as temporary image
                    temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
                    cv2.imwrite(temp_file.name, frame)
                    frames.append(temp_file.name)
            
            cap.release()
            return frames
            
        except Exception as e:
            print(f"Error extracting video frames: {e}")
            return frames
    
    def _aggregate_video_analysis(self, frame_analyses: List[Dict]) -> Dict[str, Any]:
        """Aggregate analysis results from multiple video frames"""
        if not frame_analyses:
            return {}
        
        # Calculate average overall score
        avg_score = sum(analysis.get('overall_score', 0) for analysis in frame_analyses) / len(frame_analyses)
        
        # Collect all priority issues and strengths
        all_issues = []
        all_strengths = []
        
        for analysis in frame_analyses:
            all_issues.extend(analysis.get('priority_issues', []))
            all_strengths.extend(analysis.get('strengths', []))
        
        # Remove duplicates while preserving order
        unique_issues = list(dict.fromkeys(all_issues))
        unique_strengths = list(dict.fromkeys(all_strengths))
        
        # Aggregate category scores (simplified approach)
        aggregated_categories = {}
        if frame_analyses and 'categories' in frame_analyses[0]:
            for category_id in frame_analyses[0]['categories'].keys():
                category_scores = []
                for analysis in frame_analyses:
                    if category_id in analysis.get('categories', {}):
                        category_scores.append(analysis['categories'][category_id].get('score', 0))
                
                if category_scores:
                    avg_category_score = sum(category_scores) / len(category_scores)
                    aggregated_categories[category_id] = {
                        "title": frame_analyses[0]['categories'][category_id].get('title', ''),
                        "score": round(avg_category_score),
                        "checkpoints": frame_analyses[0]['categories'][category_id].get('checkpoints', {})
                    }
        
        return {
            "overall_score": round(avg_score),
            "summary": f"Video analysis based on {len(frame_analyses)} frames. Average UX score: {round(avg_score)}%",
            "categories": aggregated_categories,
            "priority_issues": unique_issues[:10],  # Limit to top 10
            "strengths": unique_strengths[:10]  # Limit to top 10
        }
    
    def analyze_website(self, url: str, screenshot_path: Optional[str] = None) -> Dict[str, Any]:
        """Analyze a website by taking a screenshot and analyzing it"""
        try:
            if screenshot_path and os.path.exists(screenshot_path):
                # Use provided screenshot
                return self.analyze_image(screenshot_path)
            else:
                # Capture website screenshot
                from website_capture import WebsiteCapture
                
                capture = WebsiteCapture()
                screenshot_path = capture.capture_website(url)
                
                if screenshot_path:
                    # Analyze the captured screenshot
                    result = self.analyze_image(screenshot_path)
                    
                    # Add website-specific information
                    result["analyzed_url"] = url
                    result["screenshot_path"] = screenshot_path
                    
                    # Clean up screenshot after analysis
                    capture.cleanup_screenshot(screenshot_path)
                    
                    return result
                else:
                    return {
                        "error": "Failed to capture website screenshot",
                        "analyzed_url": url,
                        "overall_score": 0,
                        "summary": "Website screenshot capture failed",
                        "categories": {},
                        "priority_issues": ["Screenshot capture failed"],
                        "strengths": []
                    }
                
        except Exception as e:
            return {
                "error": f"Website analysis failed: {str(e)}",
                "analyzed_url": url,
                "overall_score": 0,
                "summary": "Website analysis could not be completed",
                "categories": {},
                "priority_issues": [],
                "strengths": []
            }

# Test function
def test_analyzer():
    """Test the UX analyzer with a sample analysis"""
    analyzer = UXAnalyzer()
    print("UX Analyzer initialized successfully!")
    print(f"Loaded {len(analyzer.heuristics)} heuristic categories")
    
    total_checkpoints = sum(len(cat['checkpoints']) for cat in analyzer.heuristics.values())
    print(f"Total checkpoints: {total_checkpoints}")
    
    return analyzer

if __name__ == "__main__":
    test_analyzer()
