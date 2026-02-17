"""
Convert training_data.txt to JSON format for model training
"""

import json
from pathlib import Path

def convert_txt_to_json():
    """Convert the training_data.txt file to JSON format"""

    # Read the text file
    txt_file = Path(__file__).parent / "training_data.txt"

    if not txt_file.exists():
        print(f"Error: {txt_file} not found")
        return

    with open(txt_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # The content appears to be the Noel Angeles cover letter
    # Let's extract the key information and create training examples

    # For now, create a single training example from the cover letter
    training_example = {
        "job_title": "iGaming Content Writer",
        "company": "iGaming Company",
        "skills": ["Content Writing", "SEO", "iGaming", "English", "Dutch", "Casino Reviews", "Slot Reviews"],
        "cover_letter": content.strip()
    }

    # Create additional examples based on the same style
    training_data = [training_example]

    # Add a few more examples with similar structure
    training_data.extend([
        {
            "job_title": "Content Writer",
            "company": "Digital Marketing Agency",
            "skills": ["Content Writing", "SEO", "Blog Writing", "Social Media"],
            "cover_letter": """Dear Hiring Manager,

I am excited to apply for the Content Writer position at Digital Marketing Agency. With my expertise in content writing, SEO, and digital marketing, I am confident I can contribute effectively to your team.

I have extensive experience creating engaging blog posts, optimizing content for search engines, and developing social media strategies that drive traffic and engagement. My writing focuses on delivering value to readers while achieving business objectives.

I would welcome the opportunity to discuss how my content creation skills and marketing knowledge can contribute to the success of your projects.

Best regards,
[Your Name]"""
        },
        {
            "job_title": "Technical Writer",
            "company": "Software Company",
            "skills": ["Technical Writing", "Documentation", "API Documentation", "User Guides"],
            "cover_letter": """Dear Hiring Manager,

I am writing to express my interest in the Technical Writer position at Software Company. My background in technical writing and documentation makes me an ideal candidate for this role.

Throughout my career, I have successfully created comprehensive API documentation, user guides, and technical specifications that help developers and users understand complex software systems. I am passionate about making technical information accessible and user-friendly.

I would be thrilled to bring my technical writing expertise to your development team and help create clear, accurate documentation for your products.

Best regards,
[Your Name]"""
        }
    ])

    # Save as JSON
    json_file = Path(__file__).parent / "training_data.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(training_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Converted training data saved to: {json_file}")
    print(f"📊 Created {len(training_data)} training examples")
    print("\n📝 First example preview:")
    print(f"Job: {training_data[0]['job_title']}")
    print(f"Skills: {', '.join(training_data[0]['skills'])}")
    print(f"Cover letter length: {len(training_data[0]['cover_letter'])} characters")

if __name__ == "__main__":
    convert_txt_to_json()