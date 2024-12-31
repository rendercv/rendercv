from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
import os
import glob
import subprocess
import shutil
import uuid
import logging
import traceback
from pathlib import Path
from datetime import datetime
from ruamel.yaml import YAML
from io import StringIO
yaml = YAML()
yaml.allow_unicode = True
yaml.default_flow_style = False

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup base directories
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "app" / "static"
TEMP_DIR = BASE_DIR / "temp"
OUTPUT_DIR = BASE_DIR / "rendercv_output"

# Create necessary directories
TEMP_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

app = FastAPI(title="CV Generator API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

class ErrorResponse(BaseModel):
    status: str = "error"
    error_type: str
    error_message: str
    error_details: Optional[Dict[str, Any]] = None
    stack_trace: Optional[str] = None

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    error_details = {
        "status": "error",
        "error_type": exc.__class__.__name__,
        "error_message": str(exc),
        "error_details": None,
        "stack_trace": traceback.format_exc() if isinstance(exc, ValueError) else None
    }
    
    # Log the error
    logger.error(f"Error processing request: {error_details}")
    
    # Customize error details based on exception type
    if isinstance(exc, yaml.YAMLError):
        error_details["error_type"] = "YAML_PARSING_ERROR"
        error_details["error_details"] = {
            "line": getattr(exc, 'problem_mark', {}).get('line', None),
            "column": getattr(exc, 'problem_mark', {}).get('column', None),
            "problem": getattr(exc, 'problem', None),
        }
    elif isinstance(exc, subprocess.CalledProcessError):
        error_details["error_type"] = "CV_GENERATION_ERROR"
        error_details["error_details"] = {
            "command": exc.cmd,
            "return_code": exc.returncode,
            "output": exc.stdout,
            "error": exc.stderr
        }
    elif isinstance(exc, ValueError):
        error_details["error_type"] = "VALIDATION_ERROR"
    
    return JSONResponse(
        status_code=400 if isinstance(exc, (yaml.YAMLError, ValueError)) else 500,
        content=jsonable_encoder(error_details)
    )

class CVValidator:
    @staticmethod
    def validate_and_fix_cv_data(data: dict) -> dict:
        """Validates and fixes CV data structure."""
        try:
            if not isinstance(data, dict):
                raise ValueError("Input must be a dictionary")

            # Ensure root 'cv' key exists
            if 'cv' not in data:
                data = {'cv': data}

            cv_data = data['cv']

            # Required sections
            required_sections = {
                'name': str,
                'location': str,
                'email': str,
                'phone': str,
                'sections': dict
            }

            # Initialize missing required fields
            for field, field_type in required_sections.items():
                if field not in cv_data:
                    cv_data[field] = '' if field_type == str else {}

            # Ensure sections exist
            required_subsections = ['summary', 'skills', 'experience', 'education']
            if 'sections' not in cv_data:
                cv_data['sections'] = {}
            
            for section in required_subsections:
                if section not in cv_data['sections']:
                    cv_data['sections'][section] = []
                if not isinstance(cv_data['sections'][section], list):
                    cv_data['sections'][section] = [cv_data['sections'][section]]

            # Fix skills format
            if 'skills' in cv_data['sections']:
                skills = cv_data['sections']['skills']
                fixed_skills = []
                for skill in skills:
                    if isinstance(skill, str):
                        fixed_skills.append({
                            'label': 'Skill',
                            'details': skill
                        })
                    elif isinstance(skill, dict) and ('label' not in skill or 'details' not in skill):
                        skill['label'] = skill.get('label', 'Skill')
                        skill['details'] = skill.get('details', '')
                        fixed_skills.append(skill)
                    else:
                        fixed_skills.append(skill)
                cv_data['sections']['skills'] = fixed_skills

            # Ensure design section exists with defaults
            if 'design' not in cv_data:
                cv_data['design'] = {
                    'theme': 'sb2nov',
                    'font': 'Latin Modern Serif',
                    'font_size': '10pt',
                    'page_size': 'letterpaper',
                    'color': '#004f90',
                    'margins': {
                        'page': {
                            'top': '2 cm',
                            'bottom': '2 cm',
                            'left': '2 cm',
                            'right': '2 cm'
                        }
                    }
                }

            # Ensure locale catalog exists
            if 'locale_catalog' not in cv_data:
                cv_data['locale_catalog'] = {
                    'phone_number_format': 'national',
                    'date_style': 'MONTH_ABBREVIATION YEAR',
                    'month': 'month',
                    'months': 'months',
                    'year': 'year',
                    'years': 'years',
                    'present': 'present',
                    'to': 'to'
                }

            # Fix experience dates
            if 'experience' in cv_data['sections']:
                for exp in cv_data['sections']['experience']:
                    if isinstance(exp, dict):
                        # Ensure required fields exist
                        exp['company'] = exp.get('company', '')
                        exp['position'] = exp.get('position', '')
                        exp['location'] = exp.get('location', '')
                        exp['start_date'] = exp.get('start_date', '')
                        exp['end_date'] = exp.get('end_date', 'present')
                        
                        # Ensure highlights is a list
                        if 'highlights' not in exp:
                            exp['highlights'] = []
                        elif not isinstance(exp['highlights'], list):
                            exp['highlights'] = [exp['highlights']]

            # Fix education dates and format
            if 'education' in cv_data['sections']:
                for edu in cv_data['sections']['education']:
                    if isinstance(edu, dict):
                        edu['institution'] = edu.get('institution', '')
                        edu['area'] = edu.get('area', '')
                        edu['degree'] = edu.get('degree', '')
                        edu['start_date'] = edu.get('start_date', '')
                        edu['end_date'] = edu.get('end_date', '')
                        
                        if 'highlights' not in edu:
                            edu['highlights'] = []
                        elif not isinstance(edu['highlights'], list):
                            edu['highlights'] = [edu['highlights']]

            return data

        except Exception as e:
            logging.error(f"Error validating CV data: {str(e)}")
            raise ValueError(f"Invalid CV data structure: {str(e)}")

class CVRequest(BaseModel):
    yaml_content: str

@app.get("/", response_class=HTMLResponse)
async def root():
    try:
        html_path = STATIC_DIR / "index.html"
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logging.error(f"Error reading index.html: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-cv/")
async def generate_cv(cv_request: CVRequest, background_tasks: BackgroundTasks):
    """
    Generate a CV from YAML content and return the PDF file
    """
    try:
        # Parse YAML content
        try:
            cv_data = yaml.load(cv_request.yaml_content)
        except yaml.YAMLError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid YAML content: {str(e)}"
            )
        
        # Validate and fix CV data
        try:
            cv_data = CVValidator.validate_and_fix_cv_data(cv_data)
            # Convert back to YAML
            yaml_str = StringIO()
            yaml.dump(cv_data, yaml_str)
            cv_request.yaml_content = yaml_str.getvalue()
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail={
                    "error_type": "VALIDATION_ERROR",
                    "error_message": str(e),
                    "error_details": None
                }
            )

        # Create a unique directory for this request
        request_id = str(uuid.uuid4())
        request_dir = TEMP_DIR / request_id
        request_dir.mkdir(exist_ok=True)
        
        # Write YAML content to a file
        yaml_path = request_dir / "cv.yaml"
        yaml_path.write_text(cv_request.yaml_content, encoding="utf-8")
        
        # Use rendercv CLI command
        try:
            import subprocess
            import glob
            import os
            
            # Ensure we're in the correct directory
            os.chdir(BASE_DIR)
            
            # Run rendercv command with proper environment
            process = subprocess.run(
                ["rendercv", "render", str(yaml_path)],
                capture_output=True,
                text=True,
                env={**os.environ, 'RENDERCV_OUTPUT_DIR': str(BASE_DIR / "rendercv_output")},
                check=False  # Don't raise exception immediately
            )
            
            # Log the output for debugging
            logger.info(f"rendercv stdout: {process.stdout}")
            if process.stderr:
                logger.error(f"rendercv stderr: {process.stderr}")
            
            if process.returncode != 0:
                raise Exception(
                    f"rendercv failed with return code {process.returncode}.\n"
                    f"Output: {process.stdout}\n"
                    f"Error: {process.stderr}"
                )
            
            # Look for the PDF in rendercv_output directory
            output_dir = BASE_DIR / "rendercv_output"
            pdf_files = list(output_dir.glob("*.pdf"))
            
            if not pdf_files:
                raise Exception(
                    f"No PDF files found in {output_dir}.\n"
                    f"Directory contents: {list(output_dir.glob('*'))}\n"
                    f"Process output: {process.stdout}\n"
                    f"Process error: {process.stderr}"
                )
            
            output_path = pdf_files[0]
            
            # Extract applicant name from the YAML file
            with open(str(yaml_path), 'r') as file:
                cv_data = yaml.load(file)
                applicant_name = cv_data.get('cv', {}).get('name', 'Applicant').replace(' ', '_')
            
            # Rename the output PDF file based on the applicant's name
            final_output_path = output_dir / f"{applicant_name}_CV.pdf"
            if output_path != final_output_path:
                import shutil
                shutil.copy2(output_path, final_output_path)
                output_path = final_output_path
            
            # Schedule cleanup for after the response is sent
            background_tasks.add_task(cleanup_files, str(output_dir))
            
            return FileResponse(
                path=output_path,
                filename=f"{applicant_name}_CV.pdf",
                media_type="application/pdf",
                background=background_tasks
            )
            
        except Exception as e:
            logger.error(f"Error generating CV: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=500,
                detail={
                    "error_type": "GENERATION_ERROR",
                    "error_message": str(e),
                    "error_details": None
                }
            )
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail={
                "error_type": "UNEXPECTED_ERROR",
                "error_message": str(e),
                "error_details": None
            }
        )

def cleanup_files(directory: str):
    """Clean up temporary files after response is sent"""
    try:
        import shutil
        shutil.rmtree(directory, ignore_errors=True)
    except Exception as e:
        logger.error(f"Error cleaning up directory {directory}: {str(e)}")

@app.post("/test-connection/")
async def test_connection(request_body: dict):
    """Test endpoint for n8n to verify connection"""
    try:
        return {
            "status": "success",
            "message": "Connection successful",
            "received_data": request_body
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get("/usage/")
async def usage():
    return {
        "message": "Welcome to CV Generator API",
        "usage": {
            "endpoint": "POST /generate-cv/",
            "body": {
                "yaml_content": "Your YAML content here"
            }
        }
    }
