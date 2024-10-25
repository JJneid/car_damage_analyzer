import streamlit as st
import pandas as pd
import io
import base64
from PIL import Image
import json
from datetime import datetime
import requests

# Local LLaVA configuration
LLAVA_CONFIG = {
    "api_url": "http://localhost:11434/api/generate",
    "model": "llava"
}

# Pre-staged results for testing
PRESTAGED_RESULTS = {
    "damage_assessment": """The damage is located on the side and rear of the car. It appears to be a significant impact, as evidenced by the crumpled metal panels and visible structural damage, which indicates that it could have been in a collision.

The type of damage includes a combination of denting and crushing, with some parts of the car's side and rear compartments completely destroyed or heavily deformed. There might also be internal damage to the vehicle not visible from this angle.

The damage is severe, as it has rendered the car essentially inoperable without extensive repairs or replacement of affected components.

The repair is likely to be complex, given the extent of the damage and the fact that multiple parts of the car's bodywork are severely deformed. The structural integrity of the vehicle may have been compromised, which would require careful assessment and potential reinforcement before any cosmetic repairs could be undertaken.""",

    "part_analysis": """The car damage appears to affect several parts of the vehicle, including:

Front bumper and fender, which might be bent or cracked.
Hood, which is visibly damaged and may require replacement or significant repair work.
Windshield area, which could also have been impacted by the collision.
The passenger side doors and possibly the windows might have suffered damage as well.
Side mirrors may need to be checked for any potential damage not visible in this image.

Given the extent of the frontal damage, it is likely that parts of the engine bay or interior components (such as airbags) could also have been damaged during the collision and might require complete replacement or thorough inspection to ensure safety and functionality.

In addition to the visible damage, other areas that should be checked for related damage include:
- Underneath the vehicle, especially around the engine bay, suspension system, and frame for any structural damage.
- The brake lines and hydraulic lines might also have been damaged during the collision and would need to be inspected.
- The vehicle's electrical system, including the battery, alternator, wiring harness, and connectors.
- The fuel tank should be checked for potential damage that could lead to a fuel leak.
- Lastly, the vehicle's tires and wheels should be examined for possible damage or alignment issues caused by the impact.""",

    "repair_recommendations": """Repair methods:
- Assess the structural integrity of the vehicle
- Remove damaged parts
- Assess for hidden damage
- Consider paintless dent removal (PDR)
- Repair or replace body panels
- Replace damaged mechanical components as necessary
- Address safety concerns

The repair time could take several days to several weeks, depending on the complexity and availability of parts.

Specialized tools and professional expertise will be required for frame alignment, dent removal, and mechanical component replacement.

Safety concerns include the integrity of the car's frame and overall structural safety. Professional inspection is crucial before returning the vehicle to service."""
}

# Define default car damage assessment prompts
CAR_DAMAGE_PROMPTS = {
    "damage_assessment": """Look at this car damage image and answer these questions:
1. Where is the damage located? (which part of the car)
2. What type of damage is it? (dent, scratch, etc.)
3. How severe is the damage? (Minor/Moderate/Severe)
4. Is the repair likely to be Easy, Medium, or Complex?""",

    "part_analysis": """For this car damage:
1. Which parts need to be repaired?
2. Which parts might need complete replacement?
3. What other areas should be checked for related damage?""",

    "repair_recommendations": """Based on the visible car damage:
1. What repair methods would you recommend?
2. How long might the repair take?
3. Will this need specialized tools or skills?
4. Are there any safety concerns to consider?"""
}

def encode_image_to_base64(image):
    """Convert PIL Image to base64 string."""
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()

def analyze_with_llava(image, prompt):
    """Analyze image using local LLaVA model with streaming response handling."""
    try:
        # Prepare the request payload
        payload = {
            "model": LLAVA_CONFIG["model"],
            "prompt": prompt,
            "images": [encode_image_to_base64(image)],
            "stream": False  # Disable streaming for simpler response handling
        }

        # Make request to local LLaVA endpoint
        response = requests.post(LLAVA_CONFIG["api_url"], json=payload)
        
        if response.status_code == 200:
            try:
                # Parse the response text
                response_text = ""
                for line in response.text.strip().split('\n'):
                    if line:
                        try:
                            response_json = json.loads(line)
                            if 'response' in response_json:
                                response_text += response_json['response']
                        except json.JSONDecodeError:
                            continue
                
                return response_text.strip()
            except Exception as e:
                st.error(f"Error parsing response: {str(e)}")
                return None
        else:
            st.error(f"Error from LLaVA API: {response.status_code}")
            return None
            
    except Exception as e:
        st.error(f"Error calling LLaVA API: {str(e)}")
        return None

def analyze_car_damage(image, use_prestaged=True):
    """Analyze car damage using LLaVA model or pre-staged results."""
    if use_prestaged:
        return PRESTAGED_RESULTS
    
    results = {}
    for prompt_name, prompt_text in CAR_DAMAGE_PROMPTS.items():
        try:
            response = analyze_with_llava(image, prompt_text)
            if response:
                results[prompt_name] = response
            else:
                results[prompt_name] = "Analysis failed"
        except Exception as e:
            st.error(f"Error in analysis: {str(e)}")
            results[prompt_name] = "Analysis failed"
    
    return results

def display_damage_analysis(results):
    """Display car damage analysis results."""
    
    # Display Damage Assessment
    with st.expander("🔍 Damage Assessment", expanded=True):
        st.write(results["damage_assessment"])
    
    # Display Parts Analysis
    with st.expander("🔧 Parts Analysis", expanded=True):
        st.write(results["part_analysis"])
    
    # Display Repair Recommendations
    with st.expander("📋 Repair Recommendations", expanded=True):
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
    
    # Add toggle for pre-staged results
    use_prestaged = st.checkbox("Use pre-staged results", value=True)
    
    # Add file uploader
    uploaded_files = st.file_uploader(
        "Upload damage photos",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
        help="Upload one or more photos of the damaged areas"
    )
    
    if uploaded_files:
        total_files = len(uploaded_files)
        
        st.markdown("---")
        st.subheader(f"Analyzing {total_files} image{'s' if total_files > 1 else ''}")
        
        progress_bar = st.progress(0)
        
        # Process each uploaded image
        for i, file in enumerate(uploaded_files):
            with st.container():
                st.markdown(f"### Image {i+1}")
                
                # Display image and analysis side by side
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    image = Image.open(file)
                    st.image(image, use_column_width=True)
                
                with col2:
                    with st.spinner("Analyzing damage..." if not use_prestaged else "Loading pre-staged results..."):
                        results = analyze_car_damage(image, use_prestaged)
                        display_damage_analysis(results)
                
                st.markdown("---")
                
                progress_bar.progress((i + 1) / total_files)
        
        # Create report
        report_data = []
        for i, file in enumerate(uploaded_files):
            image = Image.open(file)
            results = analyze_car_damage(image, use_prestaged)
            
            report_data.append({
                "Image": f"Image {i+1}",
                "Damage Assessment": results["damage_assessment"],
                "Parts Analysis": results["part_analysis"],
                "Repair Recommendations": results["repair_recommendations"]
            })
        
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