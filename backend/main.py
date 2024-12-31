from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yaml
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os
from typing import Dict, Any
from pathlib import Path

# Get the current directory
BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the static directory using absolute path
static_dir = BASE_DIR / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

class YAMLData(BaseModel):
    content: str

def create_pdf_from_yaml(yaml_data: Dict[Any, Any], output_path: str = "output.pdf") -> str:
    c = canvas.Canvas(output_path, pagesize=letter)
    y = 750  # Start from top of page
    
    def write_section(data, x=50, y=750, indent=0):
        if isinstance(data, dict):
            for key, value in data.items():
                c.drawString(x + (indent * 20), y, f"{key}:")
                y -= 20
                if isinstance(value, (dict, list)):
                    y = write_section(value, x, y, indent + 1)
                else:
                    c.drawString(x + ((indent + 1) * 20), y, str(value))
                    y -= 20
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    y = write_section(item, x, y, indent + 1)
                else:
                    c.drawString(x + (indent * 20), y, f"- {str(item)}")
                    y -= 20
        return y

    write_section(yaml_data)
    c.save()
    return output_path

@app.get("/")
async def read_root():
    index_path = static_dir / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Index page not found")
    return FileResponse(str(index_path))

@app.post("/convert")
async def convert_yaml_to_pdf(yaml_data: YAMLData):
    try:
        # Parse YAML content
        parsed_yaml = yaml.safe_load(yaml_data.content)
        
        # Generate PDF
        output_path = BASE_DIR / "output.pdf"
        pdf_path = create_pdf_from_yaml(parsed_yaml, str(output_path))
        
        # Return the PDF file
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename="converted.pdf"
        )
    except yaml.YAMLError as e:
        raise HTTPException(status_code=400, detail=f"Invalid YAML format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
    finally:
        # Clean up the generated PDF file
        if output_path.exists():
            os.remove(str(output_path))

if __name__ == "__main__":
    import uvicorn
    # Use port 8080 instead of 8000
    uvicorn.run(app, host="0.0.0.0", port=8080)
