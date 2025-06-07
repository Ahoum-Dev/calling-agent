#!/usr/bin/env python3
"""
Simple API server to trigger outbound calls for Ahoum facilitator onboarding
"""

import subprocess
import logging
import json
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=".env")

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_phone_number(phone_number):
    """Validate phone number format"""
    # Remove any spaces or dashes
    phone_number = phone_number.replace(' ', '').replace('-', '')
    
    # Check if it starts with + and has 10-15 digits after
    pattern = r'^\+[1-9]\d{9,14}$'
    return re.match(pattern, phone_number) is not None

def execute_lk_command(phone_number):
    """Execute the LiveKit dispatch command"""
    try:
        cmd = [
            "lk", "dispatch", "create",
            "--new-room",
            "--agent-name", "ahoum-facilitator-onboarding",
            "--metadata", phone_number
        ]
        
        logger.info(f"Executing command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )
        
        if result.returncode == 0:
            logger.info(f"Successfully dispatched call to {phone_number}")
            return {
                "success": True,
                "output": result.stdout,
                "phone_number": phone_number
            }
        else:
            logger.error(f"Command failed: {result.stderr}")
            return {
                "success": False,
                "error": result.stderr,
                "phone_number": phone_number
            }
            
    except subprocess.TimeoutExpired:
        logger.error("Command timed out")
        return {
            "success": False,
            "error": "Command timed out after 30 seconds",
            "phone_number": phone_number
        }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "phone_number": phone_number
        }

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Ahoum Facilitator Onboarding API"
    })

@app.route('/ping', methods=['GET'])
def ping():
    """Simple ping endpoint for basic connectivity testing"""
    return jsonify({
        "message": "pong",
        "status": "ok"
    })

@app.route('/call', methods=['POST'])
def make_call():
    """
    Trigger an outbound call to a facilitator
    
    Expected JSON payload:
    {
        "phone_number": "+918767763794"
    }
    """
    try:
        # Get JSON data
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        # Extract phone number
        phone_number = data.get('phone_number')
        
        if not phone_number:
            return jsonify({
                "success": False,
                "error": "phone_number is required"
            }), 400
        
        # Validate phone number format
        if not validate_phone_number(phone_number):
            return jsonify({
                "success": False,
                "error": "Invalid phone number format. Use international format like +918767763794"
            }), 400
        
        # Execute the LiveKit command
        result = execute_lk_command(phone_number)
        
        if result["success"]:
            return jsonify({
                "success": True,
                "message": f"Call initiated successfully to {phone_number}",
                "phone_number": phone_number,
                "dispatch_info": result["output"]
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": f"Failed to initiate call: {result['error']}",
                "phone_number": phone_number
            }), 500
            
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500

@app.route('/call/batch', methods=['POST'])
def make_batch_calls():
    """
    Trigger multiple outbound calls
    
    Expected JSON payload:
    {
        "phone_numbers": ["+918767763794", "+919876543210", "+15551234567"]
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        phone_numbers = data.get('phone_numbers')
        
        if not phone_numbers or not isinstance(phone_numbers, list):
            return jsonify({
                "success": False,
                "error": "phone_numbers array is required"
            }), 400
        
        results = []
        
        for phone_number in phone_numbers:
            if not validate_phone_number(phone_number):
                results.append({
                    "phone_number": phone_number,
                    "success": False,
                    "error": "Invalid phone number format"
                })
                continue
            
            result = execute_lk_command(phone_number)
            results.append({
                "phone_number": phone_number,
                "success": result["success"],
                "error": result.get("error"),
                "dispatch_info": result.get("output")
            })
        
        successful_calls = sum(1 for r in results if r["success"])
        
        return jsonify({
            "success": True,
            "message": f"Processed {len(results)} calls, {successful_calls} successful",
            "results": results
        }), 200
        
    except Exception as e:
        logger.error(f"Batch API error: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500

if __name__ == '__main__':
    # Check if LiveKit CLI is available
    try:
        subprocess.run(["lk", "--version"], capture_output=True, check=True)
        logger.info("LiveKit CLI is available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("LiveKit CLI not found. Please install it first.")
        exit(1)
    
    port = int(os.getenv('API_PORT'))
    debug_mode = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Ahoum Facilitator Onboarding API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
