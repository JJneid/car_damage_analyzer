import streamlit as st
import pandas as pd
import io
import base64
from PIL import Image
from openai import OpenAI
import json
from datetime import datetime

# LLaVA configuration
LLAVA_CONFIG = {
    "base_url": "http://3.15.181.146:8000/v1/",
    "model": "llava-v1.6-34b"
}

# Define default car damage assessment prompts
CAR_DAMAGE_PROMPTS = {
    "damage_assessment": """Analyze the car damage in the image and provide:
1. Location of damage (e.g., front bumper, rear door, etc.)
2. Type of damage (e.g., dent, scratch, broken part)
3. Severity (Minor/Moderate/Severe)
4. Estimated repair complexity (Easy/Medium/Complex)
Format as JSON with these fields.""",

    "part_analysis": """List the following for the damaged car:
1. Damaged parts that need repair
2. Parts likely needing replacement
3. Additional areas to check for hidden damage
Format as JSON with these fields.""",

    "repair_recommendations": """Provide repair recommendations:
1. Suggested repair methods
2. Potential repair time
3. Whether specialized tools/skills needed
4. Safety considerations
Format as JSON with these fields."""
}

def encode_image_to_base64(image):
    """Convert PIL Image to base64 string."""
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()

def get_llava_client():
    """Initialize and return the LLaVA client."""
    return OpenAI(base_url=LLAVA_CONFIG["base_url"], api_key='None')

def analyze_car_damage(image, client):
    """Analyze car damage using LLaVA model."""
    base64_image = encode_image_to_base64(image)
    results = {}
    
    for prompt_name, prompt_text in CAR_DAMAGE_PROMPTS.items():
        try:
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt_text
                        },
                        {
                            "type": "image",
                            "image": base64_image
                        }
                    ]
                }
            ]
            
            response = client.chat.completions.create(
                model=LLAVA_CONFIG["model"],
                messages=messages,
                max_tokens=1000,
                temperature=0.2
            )
            
            results[prompt_name] = response.choices[0].message.content
            
        except Exception as e:
            st.error(f"Error in analysis: {str(e)}")
            results[prompt_name] = "Analysis failed"
    
    return results

def display_damage_analysis(results):
    """Display car damage analysis results."""
    
    # Display Damage Assessment
    with st.expander("🔍 Damage Assessment", expanded=True):
        try:
            damage_data = json.loads(results["damage_assessment"])
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Location:**")
                st.info(damage_data.get("location", "N/A"))
                st.markdown("**Type:**")
                st.info(damage_data.get("type", "N/A"))
            with col2:
                st.markdown("**Severity:**")
                severity = damage_data.get("severity", "N/A")
                if severity == "Severe":
                    st.error(severity)
                elif severity == "Moderate":
                    st.warning(severity)
                else:
                    st.success(severity)
                st.markdown("**Repair Complexity:**")
                complexity = damage_data.get("repair_complexity", "N/A")
                if complexity == "Complex":
                    st.error(complexity)
                elif complexity == "Medium":
                    st.warning(complexity)
                else:
                    st.success(complexity)
        except:
            st.write(results["damage_assessment"])
    
    # Display Parts Analysis
    with st.expander("🔧 Parts Analysis", expanded=True):
        try:
            parts_data = json.loads(results["part_analysis"])
            st.markdown("**Parts Needing Repair:**")
            for part in parts_data.get("repair_parts", []):
                st.write(f"- {part}")
            
            st.markdown("**Parts Needing Replacement:**")
            for part in parts_data.get("replacement_parts", []):
                st.write(f"- {part}")
            
            st.markdown("**Areas for Additional Inspection:**")
            for area in parts_data.get("inspection_areas", []):
                st.write(f"- {area}")
        except:
            st.write(results["part_analysis"])
    
    # Display Repair Recommendations
    with st.expander("📋 Repair Recommendations", expanded=True):
        try:
            repair_data = json.loads(results["repair_recommendations"])
            st.markdown("**Repair Methods:**")
            st.info(repair_data.get("repair_methods", "N/A"))
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Estimated Repair Time:**")
                st.info(repair_data.get("repair_time", "N/A"))
            with col2:
                st.markdown("**Specialized Requirements:**")
                if repair_data.get("specialized_requirements", False):
                    st.warning("Requires specialized tools/skills")
                else:
                    st.success("Standard repair")
            
            st.markdown("**Safety Notes:**")
            safety_notes = repair_data.get("safety_considerations", "N/A")
            if "critical" in safety_notes.lower():
                st.error(safety_notes)
            else:
                st.info(safety_notes)
        except:
            st.write(results["repair_recommendations"])

def main():
    st.title("🚗 Car Damage Analyzer")
    st.markdown("""
    Upload photos of vehicle damage for instant AI analysis.
    
    📸 **Tips for best results:**
    - Take clear, well-lit photos
    - Capture multiple angles
    - Include close-ups of damage
    """)
    
    uploaded_files = st.file_uploader(
        "Upload damage photos",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
        help="Upload one or more photos of the damaged areas"
    )
    
    if uploaded_files:
        client = get_llava_client()
        total_files = len(uploaded_files)
        
        st.markdown("---")
        st.subheader(f"Analyzing {total_files} image{'s' if total_files > 1 else ''}")
        
        progress_bar = st.progress(0)
        
        for i, file in enumerate(uploaded_files):
            with st.container():
                st.markdown(f"### Image {i+1}")
                
                # Display image and analysis side by side
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    image = Image.open(file)
                    st.image(image, use_column_width=True)
                
                with col2:
                    with st.spinner("Analyzing damage..."):
                        results = analyze_car_damage(image, client)
                        display_damage_analysis(results)
                
                st.markdown("---")
                
                progress_bar.progress((i + 1) / total_files)
        
        # Create report
        report_data = []
        for i, file in enumerate(uploaded_files):
            image = Image.open(file)
            results = analyze_car_damage(image, client)
            
            try:
                damage_data = json.loads(results["damage_assessment"])
                parts_data = json.loads(results["part_analysis"])
                repair_data = json.loads(results["repair_recommendations"])
                
                report_data.append({
                    "Image": f"Image {i+1}",
                    "Damage Location": damage_data.get("location", "N/A"),
                    "Damage Type": damage_data.get("type", "N/A"),
                    "Severity": damage_data.get("severity", "N/A"),
                    "Repair Complexity": damage_data.get("repair_complexity", "N/A"),
                    "Parts to Replace": ", ".join(parts_data.get("replacement_parts", [])),
                    "Estimated Repair Time": repair_data.get("repair_time", "N/A"),
                    "Special Requirements": repair_data.get("specialized_requirements", "N/A")
                })
            except:
                continue
        
        if report_data:
            df = pd.DataFrame(report_data)
            
            # Create Excel report
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Damage Analysis')
            
            buffer.seek(0)
            
            st.download_button(
                label="📥 Download Analysis Report",
                data=buffer,
                file_name=f"car_damage_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

if __name__ == "__main__":
    main()