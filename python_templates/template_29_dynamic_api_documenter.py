"""
Template #29: Dynamic API Documenter
Advanced AI application for analyzing OpenAPI specifications and generating enhanced v2.0 documentation

Author: MiniMax Agent
Date: 2025-11-17
"""

import json
import yaml
import sqlite3
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import jwt
import os
import re
from pathlib import Path

# Configuration
SECRET_KEY = "dynamic_api_documenter_secret_2025"
ALGORITHM = "HS256"

# Initialize FastAPI app
app = FastAPI(
    title="Dynamic API Documenter",
    description="AI-powered OpenAPI specification analysis and v2.0 enhancement generation",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Database setup
def init_database():
    conn = sqlite3.connect('dynamic_api_documenter.db')
    cursor = conn.cursor()
    
    # Create API specifications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_specifications (
            id TEXT PRIMARY KEY,
            original_spec TEXT NOT NULL,
            enhanced_spec TEXT NOT NULL,
            weaknesses TEXT NOT NULL,
            enhancements TEXT NOT NULL,
            analysis_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            api_title TEXT,
            api_version TEXT,
            file_name TEXT
        )
    ''')
    
    # Create endpoint analysis table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS endpoint_analysis (
            id TEXT PRIMARY KEY,
            spec_id TEXT,
            endpoint_path TEXT,
            method TEXT,
            analysis_data TEXT,
            improvement_suggestions TEXT,
            FOREIGN KEY (spec_id) REFERENCES api_specifications (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_database()

# Models
class AnalysisRequest(BaseModel):
    user_input: str
    context_file: Optional[str] = None

class APISpecRequest(BaseModel):
    spec_content: str
    spec_format: str  # "json" or "yaml"
    target_version: str = "2.0"

class EnhancedSpec(BaseModel):
    spec_id: str
    enhanced_openapi: Dict[str, Any]
    weaknesses_identified: List[Dict[str, str]]
    enhancements_made: List[Dict[str, str]]
    improvements_by_endpoint: List[Dict[str, Any]]
    timestamp: str

class EndpointAnalysis(BaseModel):
    endpoint_path: str
    method: str
    current_spec: Dict[str, Any]
    weaknesses: List[str]
    suggested_improvements: List[Dict[str, str]]
    priority: str

# Authentication dependency
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

# Core AI Logic Classes
class OpenAPIAnalyzer:
    """Advanced OpenAPI specification analysis and weakness detection"""
    
    def __init__(self):
        self.common_weaknesses = {
            "incomplete_schemas": [
                "Missing required properties in request bodies",
                "Undefined response schemas",
                "Inconsistent property types across endpoints",
                "Missing example values for complex schemas"
            ],
            "poor_documentation": [
                "Ambiguous endpoint descriptions",
                "Missing parameter descriptions",
                "Unclear error response meanings",
                "Insufficient usage examples"
            ],
            "security_issues": [
                "Missing authentication requirements",
                "Inadequate authorization scopes",
                "Missing rate limiting information",
                "Insufficient security scheme definitions"
            ],
            "design_inconsistencies": [
                "Inconsistent naming conventions",
                "Varying response formats across similar endpoints",
                "Inconsistent error handling patterns",
                "Mixed URL structure patterns"
            ],
            "performance_concerns": [
                "Missing pagination parameters",
                "Inefficient query parameter combinations",
                "Missing caching headers",
                "Large response payloads without filtering"
            ]
        }
    
    def analyze_spec(self, spec_content: str, spec_format: str) -> Dict[str, Any]:
        """Comprehensive OpenAPI specification analysis"""
        try:
            # Parse specification
            spec = self._parse_spec(spec_content, spec_format)
            
            # Perform various analyses
            analysis = {
                "basic_info": self._extract_basic_info(spec),
                "endpoint_analysis": self._analyze_endpoints(spec),
                "schema_analysis": self._analyze_schemas(spec),
                "security_analysis": self._analyze_security(spec),
                "documentation_analysis": self._analyze_documentation(spec),
                "consistency_analysis": self._analyze_consistency(spec),
                "weaknesses": self._identify_weaknesses(spec)
            }
            
            return analysis
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Specification analysis failed: {str(e)}")
    
    def _parse_spec(self, spec_content: str, spec_format: str) -> Dict[str, Any]:
        """Parse OpenAPI specification from JSON or YAML"""
        try:
            if spec_format.lower() == "json":
                return json.loads(spec_content)
            elif spec_format.lower() in ["yaml", "yml"]:
                return yaml.safe_load(spec_content)
            else:
                raise HTTPException(status_code=400, detail="Unsupported specification format")
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            raise HTTPException(status_code=400, detail=f"Invalid specification format: {str(e)}")
    
    def _extract_basic_info(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Extract basic API information"""
        info = spec.get("info", {})
        
        return {
            "title": info.get("title", "Unknown API"),
            "version": info.get("version", "1.0.0"),
            "description": info.get("description", ""),
            "terms_of_service": info.get("termsOfService", ""),
            "contact": info.get("contact", {}),
            "license": info.get("license", {}),
            "openapi_version": spec.get("openapi", ""),
            "servers": spec.get("servers", []),
            "tags": spec.get("tags", [])
        }
    
    def _analyze_endpoints(self, spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze all API endpoints"""
        endpoints = []
        paths = spec.get("paths", {})
        
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method.lower() in ["get", "post", "put", "patch", "delete"]:
                    endpoint = {
                        "path": path,
                        "method": method.upper(),
                        "summary": operation.get("summary", ""),
                        "description": operation.get("description", ""),
                        "operation_id": operation.get("operationId", ""),
                        "tags": operation.get("tags", []),
                        "parameters": operation.get("parameters", []),
                        "request_body": operation.get("requestBody", {}),
                        "responses": operation.get("responses", {}),
                        "security": operation.get("security", []),
                        "deprecated": operation.get("deprecated", False),
                        "deprecated_reason": operation.get("deprecatedReason", "")
                    }
                    endpoints.append(endpoint)
        
        return endpoints
    
    def _analyze_schemas(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze API schemas and data models"""
        schemas = spec.get("components", {}).get("schemas", {})
        
        analysis = {
            "total_schemas": len(schemas),
            "schema_details": [],
            "unused_schemas": [],
            "circular_references": [],
            "complexity_score": 0
        }
        
        for schema_name, schema in schemas.items():
            schema_info = {
                "name": schema_name,
                "type": schema.get("type", "object"),
                "properties": list(schema.get("properties", {}).keys()) if schema.get("properties") else [],
                "required": schema.get("required", []),
                "description": schema.get("description", ""),
                "has_examples": "example" in schema or "examples" in schema,
                "complexity_level": self._calculate_schema_complexity(schema)
            }
            analysis["schema_details"].append(schema_info)
            
            # Calculate overall complexity score
            analysis["complexity_score"] += schema_info["complexity_level"]
        
        # Normalize complexity score
        if analysis["total_schemas"] > 0:
            analysis["complexity_score"] /= analysis["total_schemas"]
        
        return analysis
    
    def _calculate_schema_complexity(self, schema: Dict[str, Any]) -> int:
        """Calculate complexity score for a schema"""
        complexity = 0
        
        # Property count
        properties = schema.get("properties", {})
        complexity += len(properties) * 2
        
        # Nested objects
        for prop_schema in properties.values():
            if isinstance(prop_schema, dict):
                if prop_schema.get("type") == "object":
                    nested_props = prop_schema.get("properties", {})
                    complexity += len(nested_props)
                elif prop_schema.get("type") == "array":
                    complexity += 3  # Array complexity
                elif prop_schema.get("type") == "string" and prop_schema.get("format"):
                    complexity += 2  # Formatted strings
        
        # Required properties
        complexity += len(schema.get("required", []))
        
        # Additional properties
        if schema.get("additionalProperties"):
            complexity += 2
        
        # AllOf/anyOf/oneOf
        if schema.get("allOf"):
            complexity += len(schema["allOf"]) * 2
        if schema.get("anyOf"):
            complexity += len(schema["anyOf"]) * 3
        if schema.get("oneOf"):
            complexity += len(schema["oneOf"]) * 3
        
        return complexity
    
    def _analyze_security(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze API security configuration"""
        security_schemes = spec.get("components", {}).get("securitySchemes", {})
        
        analysis = {
            "security_schemes": security_schemes,
            "global_security": spec.get("security", []),
            "endpoint_security": [],
            "security_score": 0,
            "recommendations": []
        }
        
        # Analyze endpoint security
        endpoints = self._analyze_endpoints(spec)
        for endpoint in endpoints:
            if endpoint["security"]:
                analysis["endpoint_security"].append({
                    "path": endpoint["path"],
                    "method": endpoint["method"],
                    "security": endpoint["security"]
                })
        
        # Calculate security score
        score = 0
        if security_schemes:
            score += 30  # Has security schemes
        if analysis["global_security"]:
            score += 20  # Global security defined
        if len(security_schemes) > 1:
            score += 10  # Multiple schemes
        if any(scheme.get("type") == "oauth2" for scheme in security_schemes.values()):
            score += 20  # OAuth2 support
        if any(scheme.get("type") == "http" for scheme in security_schemes.values()):
            score += 10  # HTTP auth
        if any(scheme.get("type") == "apiKey" for scheme in security_schemes.values()):
            score += 15  # API key auth
        
        analysis["security_score"] = min(score, 100)
        
        # Generate recommendations
        if not security_schemes:
            analysis["recommendations"].append("Define security schemes for authentication")
        if not analysis["global_security"]:
            analysis["recommendations"].append("Consider global security requirements")
        if analysis["security_score"] < 50:
            analysis["recommendations"].append("Enhance security configuration with proper authentication methods")
        
        return analysis
    
    def _analyze_documentation(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze API documentation quality"""
        endpoints = self._analyze_endpoints(spec)
        
        analysis = {
            "documentation_score": 0,
            "endpoint_documentation": [],
            "missing_descriptions": [],
            "missing_examples": [],
            "missing_parameters": [],
            "recommendations": []
        }
        
        total_endpoints = len(endpoints)
        documented_endpoints = 0
        endpoints_with_examples = 0
        well_documented_params = 0
        
        for endpoint in endpoints:
            endpoint_doc = {
                "path": endpoint["path"],
                "method": endpoint["method"],
                "has_summary": bool(endpoint["summary"]),
                "has_description": bool(endpoint["description"]),
                "description_quality": self._assess_description_quality(endpoint.get("description", "")),
                "parameter_documentation": self._assess_parameter_documentation(endpoint.get("parameters", [])),
                "response_documentation": self._assess_response_documentation(endpoint.get("responses", {}))
            }
            
            # Check if well documented
            if endpoint["summary"] and endpoint["description"]:
                documented_endpoints += 1
            
            # Check examples
            if self._has_examples(endpoint):
                endpoints_with_examples += 1
            
            # Parameter documentation quality
            if endpoint_doc["parameter_documentation"]["score"] > 0.7:
                well_documented_params += 1
            
            # Identify missing elements
            if not endpoint["summary"]:
                analysis["missing_descriptions"].append(f"{endpoint['method']} {endpoint['path']}: Missing summary")
            if not endpoint["description"]:
                analysis["missing_descriptions"].append(f"{endpoint['method']} {endpoint['path']}: Missing description")
            if not self._has_examples(endpoint):
                analysis["missing_examples"].append(f"{endpoint['method']} {endpoint['path']}")
            
            analysis["endpoint_documentation"].append(endpoint_doc)
        
        # Calculate documentation score
        if total_endpoints > 0:
            doc_score = (documented_endpoints / total_endpoints) * 40  # 40% for basic docs
            example_score = (endpoints_with_examples / total_endpoints) * 30  # 30% for examples
            param_score = (well_documented_params / total_endpoints) * 30  # 30% for params
            
            analysis["documentation_score"] = doc_score + example_score + param_score
        
        # Generate recommendations
        if analysis["documentation_score"] < 50:
            analysis["recommendations"].append("Improve endpoint descriptions and summaries")
        if len(analysis["missing_examples"]) > total_endpoints * 0.5:
            analysis["recommendations"].append("Add request/response examples for better clarity")
        if analysis["missing_descriptions"]:
            analysis["recommendations"].append("Complete missing parameter and endpoint descriptions")
        
        return analysis
    
    def _assess_description_quality(self, description: str) -> float:
        """Assess quality of description text"""
        if not description:
            return 0.0
        
        score = 0.0
        
        # Length check (minimum 20 characters, bonus for 50+)
        if len(description) >= 20:
            score += 0.3
        if len(description) >= 50:
            score += 0.2
        
        # Contains action words
        action_words = ["retrieve", "get", "create", "update", "delete", "fetch", "list", "search", "filter"]
        if any(word in description.lower() for word in action_words):
            score += 0.2
        
        # Contains technical terms
        tech_terms = ["parameter", "response", "request", "body", "header", "query", "path"]
        if any(term in description.lower() for term in tech_terms):
            score += 0.15
        
        # Contains usage context
        context_words = ["use", "when", "for", "to", "in order", "intended"]
        if any(word in description.lower() for word in context_words):
            score += 0.15
        
        return min(score, 1.0)
    
    def _assess_parameter_documentation(self, parameters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess quality of parameter documentation"""
        if not parameters:
            return {"score": 0.0, "missing_descriptions": []}
        
        total_params = len(parameters)
        well_documented = 0
        missing_descriptions = []
        
        for param in parameters:
            has_name = bool(param.get("name"))
            has_description = bool(param.get("description"))
            has_type = bool(param.get("schema") or param.get("type"))
            has_required = param.get("required", False) is not None
            
            if has_name and has_description and has_type:
                well_documented += 1
            else:
                missing_descriptions.append(param.get("name", "Unknown parameter"))
        
        score = well_documented / total_params if total_params > 0 else 0.0
        
        return {
            "score": score,
            "total_parameters": total_params,
            "well_documented": well_documented,
            "missing_descriptions": missing_descriptions
        }
    
    def _assess_response_documentation(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """Assess quality of response documentation"""
        if not responses:
            return {"score": 0.0, "missing_schemas": []}
        
        total_responses = len(responses)
        well_documented = 0
        missing_schemas = []
        
        for status_code, response in responses.items():
            has_description = bool(response.get("description"))
            has_content = bool(response.get("content"))
            has_schema = False
            
            if has_content:
                content = response["content"]
                for media_type, media_info in content.items():
                    if "schema" in media_info:
                        has_schema = True
                        break
            
            if has_description and has_content and has_schema:
                well_documented += 1
            else:
                if not has_description:
                    missing_schemas.append(f"{status_code}: Missing description")
                elif not has_content:
                    missing_schemas.append(f"{status_code}: Missing content type")
                elif not has_schema:
                    missing_schemas.append(f"{status_code}: Missing response schema")
        
        score = well_documented / total_responses if total_responses > 0 else 0.0
        
        return {
            "score": score,
            "total_responses": total_responses,
            "well_documented": well_documented,
            "missing_schemas": missing_schemas
        }
    
    def _has_examples(self, endpoint: Dict[str, Any]) -> bool:
        """Check if endpoint has examples"""
        # Check request body examples
        request_body = endpoint.get("requestBody", {})
        if request_body:
            content = request_body.get("content", {})
            for media_type, media_info in content.items():
                if "example" in media_info or "examples" in media_info:
                    return True
        
        # Check response examples
        responses = endpoint.get("responses", {})
        for response in responses.values():
            content = response.get("content", {})
            for media_type, media_info in content.items():
                if "example" in media_info or "examples" in media_info:
                    return True
        
        return False
    
    def _analyze_consistency(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze API consistency patterns"""
        endpoints = self._analyze_endpoints(spec)
        
        analysis = {
            "consistency_score": 0,
            "naming_patterns": {},
            "response_patterns": {},
            "parameter_patterns": {},
            "inconsistencies": []
        }
        
        # Analyze naming patterns
        paths = [endpoint["path"] for endpoint in endpoints]
        path_patterns = self._identify_path_patterns(paths)
        
        methods = [endpoint["method"] for endpoint in endpoints]
        method_consistency = self._assess_method_consistency(methods)
        
        # Analyze response patterns
        response_patterns = {}
        for endpoint in endpoints:
            response_codes = list(endpoint["responses"].keys())
            for code in response_codes:
                if code not in response_patterns:
                    response_patterns[code] = []
                response_patterns[code].append(f"{endpoint['method']} {endpoint['path']}")
        
        # Calculate consistency score
        score = 0
        
        # Path naming consistency
        if path_patterns["consistency_ratio"] > 0.8:
            score += 30
        elif path_patterns["consistency_ratio"] > 0.6:
            score += 20
        else:
            analysis["inconsistencies"].append("Inconsistent URL path naming patterns")
        
        # Response code consistency
        expected_codes = ["200", "400", "404", "500"]
        documented_codes = set(response_patterns.keys())
        coverage = len(expected_codes & documented_codes) / len(expected_codes)
        score += coverage * 25
        
        # Method usage consistency
        score += method_consistency * 20
        
        # Parameter naming consistency
        param_consistency = self._assess_parameter_consistency(endpoints)
        score += param_consistency * 25
        
        analysis["consistency_score"] = score
        
        analysis["naming_patterns"] = path_patterns
        analysis["response_patterns"] = response_patterns
        
        return analysis
    
    def _identify_path_patterns(self, paths: List[str]) -> Dict[str, Any]:
        """Identify URL path naming patterns"""
        patterns = {
            "plural_resources": 0,
            "singular_resources": 0,
            "underscore_patterns": 0,
            "camelcase_patterns": 0,
            "kebab_patterns": 0
        }
        
        for path in paths:
            # Resource naming
            if "/users" in path or "/items" in path or "/products" in path:
                patterns["plural_resources"] += 1
            elif "/user" in path or "/item" in path or "/product" in path:
                patterns["singular_resources"] += 1
            
            # Naming conventions
            if "_" in path:
                patterns["underscore_patterns"] += 1
            elif re.search(r'[a-z][A-Z]', path):
                patterns["camelcase_patterns"] += 1
            elif "-" in path:
                patterns["kebab_patterns"] += 1
        
        total = len(paths)
        consistency_ratio = max(patterns.values()) / total if total > 0 else 0
        
        return {
            **patterns,
            "total_paths": total,
            "consistency_ratio": consistency_ratio,
            "dominant_pattern": max(patterns, key=patterns.get)
        }
    
    def _assess_method_consistency(self, methods: List[str]) -> float:
        """Assess HTTP method usage consistency"""
        method_counts = {}
        for method in methods:
            method_counts[method] = method_counts.get(method, 0) + 1
        
        # Expected method patterns
        expected_patterns = {
            "GET": 0.4,  # Most endpoints should be GET
            "POST": 0.25,  # Creation endpoints
            "PUT": 0.15,   # Update endpoints
            "DELETE": 0.1, # Deletion endpoints
            "PATCH": 0.1   # Partial update endpoints
        }
        
        total_endpoints = len(methods)
        if total_endpoints == 0:
            return 0.0
        
        # Calculate deviation from expected patterns
        score = 1.0
        for method, expected_ratio in expected_patterns.items():
            actual_ratio = method_counts.get(method, 0) / total_endpoints
            deviation = abs(actual_ratio - expected_ratio)
            score -= deviation * 0.2
        
        return max(score, 0.0)
    
    def _assess_parameter_consistency(self, endpoints: List[Dict[str, Any]]) -> float:
        """Assess parameter naming and usage consistency"""
        all_params = []
        
        for endpoint in endpoints:
            params = endpoint.get("parameters", [])
            for param in params:
                all_params.append({
                    "name": param.get("name", ""),
                    "in": param.get("in", ""),
                    "type": param.get("schema", {}).get("type", param.get("type", ""))
                })
        
        if not all_params:
            return 1.0
        
        # Check naming consistency
        param_names = [param["name"] for param in all_params if param["name"]]
        name_consistency = len(set(param_names)) / len(param_names) if param_names else 0
        
        # Check location consistency (query, path, header)
        param_locations = [param["in"] for param in all_params if param["in"]]
        location_consistency = len(set(param_locations)) / len(param_locations) if param_locations else 0
        
        # Overall parameter consistency score
        return (name_consistency + location_consistency) / 2
    
    def _identify_weaknesses(self, spec: Dict[str, Any]) -> List[Dict[str, str]]:
        """Identify top weaknesses in the API specification"""
        weaknesses = []
        
        # Perform all analyses
        endpoint_analysis = self._analyze_endpoints(spec)
        schema_analysis = self._analyze_schemas(spec)
        security_analysis = self._analyze_security(spec)
        documentation_analysis = self._analyze_documentation(spec)
        consistency_analysis = self._analyze_consistency(spec)
        
        # Documentation weaknesses
        if documentation_analysis["documentation_score"] < 70:
            weaknesses.append({
                "category": "Documentation",
                "severity": "High" if documentation_analysis["documentation_score"] < 50 else "Medium",
                "description": f"Low documentation quality score ({documentation_analysis['documentation_score']:.1f}%)",
                "impact": "Developers will struggle to understand and use the API effectively",
                "recommendation": "Improve endpoint descriptions, add examples, and document parameters clearly"
            })
        
        # Security weaknesses
        if security_analysis["security_score"] < 70:
            weaknesses.append({
                "category": "Security",
                "severity": "High" if security_analysis["security_score"] < 50 else "Medium",
                "description": f"Insufficient security configuration (score: {security_analysis['security_score']}%)",
                "impact": "API may be vulnerable to unauthorized access and security breaches",
                "recommendation": "Implement proper authentication, authorization, and security schemes"
            })
        
        # Schema weaknesses
        if schema_analysis["complexity_score"] > 7:
            weaknesses.append({
                "category": "Schema Design",
                "severity": "Medium",
                "description": f"High schema complexity (score: {schema_analysis['complexity_score']:.1f})",
                "impact": "Complex schemas make API difficult to understand and maintain",
                "recommendation": "Simplify schemas, break down complex objects, add clear examples"
            })
        
        if schema_analysis["total_schemas"] > 0:
            schemas_with_examples = sum(1 for schema in schema_analysis["schema_details"] if schema["has_examples"])
            if schemas_with_examples / schema_analysis["total_schemas"] < 0.5:
                weaknesses.append({
                    "category": "Schema Documentation",
                    "severity": "Medium",
                    "description": f"Only {schemas_with_examples}/{schema_analysis['total_schemas']} schemas have examples",
                    "impact": "Without examples, developers struggle to understand data structures",
                    "recommendation": "Add example values for all schema properties and complex types"
                })
        
        # Consistency weaknesses
        if consistency_analysis["consistency_score"] < 70:
            weaknesses.append({
                "category": "Design Consistency",
                "severity": "Medium" if consistency_analysis["consistency_score"] > 50 else "High",
                "description": f"Low consistency score ({consistency_analysis['consistency_score']:.1f}%)",
                "impact": "Inconsistent patterns confuse developers and increase learning curve",
                "recommendation": "Standardize naming conventions, response formats, and error handling"
            })
        
        # Endpoint-specific weaknesses
        poorly_documented_endpoints = [
            ep for ep in documentation_analysis["endpoint_documentation"]
            if ep["description_quality"] < 0.5
        ]
        if poorly_documented_endpoints:
            weaknesses.append({
                "category": "Endpoint Documentation",
                "severity": "High" if len(poorly_documented_endpoints) > len(endpoint_analysis) * 0.3 else "Medium",
                "description": f"{len(poorly_documented_endpoints)}/{len(endpoint_analysis)} endpoints have poor descriptions",
                "impact": "Unclear endpoint purposes and usage instructions",
                "recommendation": "Improve endpoint descriptions with clear purpose, parameters, and examples"
            })
        
        # Missing pagination for list endpoints
        list_endpoints = [ep for ep in endpoint_analysis if "list" in ep.get("summary", "").lower() or "get" in ep["method"].lower()]
        endpoints_without_pagination = []
        for endpoint in list_endpoints:
            has_pagination = any(
                param.get("name", "").lower() in ["limit", "offset", "page", "page_size"] 
                for param in endpoint.get("parameters", [])
            )
            if not has_pagination:
                endpoints_without_pagination.append(f"{endpoint['method']} {endpoint['path']}")
        
        if endpoints_without_pagination:
            weaknesses.append({
                "category": "Performance",
                "severity": "Medium",
                "description": f"List endpoints missing pagination: {', '.join(endpoints_without_pagination[:3])}{'...' if len(endpoints_without_pagination) > 3 else ''}",
                "impact": "Large datasets will cause performance issues and timeout errors",
                "recommendation": "Implement pagination parameters (limit/offset or cursor-based) for all list endpoints"
            })
        
        return sorted(weaknesses, key=lambda x: {"High": 3, "Medium": 2, "Low": 1}[x["severity"]], reverse=True)

class APISpecGenerator:
    """Generate enhanced v2.0 API specifications"""
    
    def __init__(self):
        self.enhancement_strategies = {
            "documentation": self._enhance_documentation,
            "security": self._enhance_security,
            "pagination": self._add_pagination,
            "error_handling": self._improve_error_handling,
            "consistency": self._improve_consistency,
            "examples": self._add_examples,
            "performance": self._add_performance_features,
            "monitoring": self._add_monitoring_features
        }
    
    def generate_enhanced_spec(self, original_spec: Dict[str, Any], weaknesses: List[Dict[str, str]]) -> Dict[str, Any]:
        """Generate enhanced v2.0 specification"""
        # Create deep copy of original spec
        enhanced_spec = json.loads(json.dumps(original_spec))
        
        # Update version and metadata
        enhanced_spec = self._update_metadata(enhanced_spec)
        
        # Apply enhancements based on identified weaknesses
        enhancements_applied = []
        
        for weakness in weaknesses[:3]:  # Focus on top 3 weaknesses
            category = weakness["category"]
            
            if category == "Documentation":
                enhanced_spec = self.enhancement_strategies["documentation"](enhanced_spec)
                enhancements_applied.append({
                    "type": "Documentation Enhancement",
                    "description": "Improved endpoint descriptions and parameter documentation",
                    "files_affected": "All endpoints"
                })
            
            elif category == "Security":
                enhanced_spec = self.enhancement_strategies["security"](enhanced_spec)
                enhancements_applied.append({
                    "type": "Security Enhancement",
                    "description": "Added comprehensive security schemes and requirements",
                    "files_affected": "Global security configuration"
                })
            
            elif category == "Performance":
                enhanced_spec = self.enhancement_strategies["pagination"](enhanced_spec)
                enhancements_applied.append({
                    "type": "Performance Enhancement",
                    "description": "Added pagination support for list endpoints",
                    "files_affected": "List endpoints"
                })
            
            elif category == "Schema Documentation":
                enhanced_spec = self.enhancement_strategies["examples"](enhanced_spec)
                enhancements_applied.append({
                    "type": "Schema Enhancement",
                    "description": "Added examples to all schemas and endpoints",
                    "files_affected": "All schemas and endpoints"
                })
            
            elif category == "Design Consistency":
                enhanced_spec = self.enhancement_strategies["consistency"](enhanced_spec)
                enhancements_applied.append({
                    "type": "Consistency Enhancement",
                    "description": "Standardized naming conventions and patterns",
                    "files_affected": "URL patterns and naming"
                })
            
            elif category == "Error Handling":
                enhanced_spec = self.enhancement_strategies["error_handling"](enhanced_spec)
                enhancements_applied.append({
                    "type": "Error Handling Enhancement",
                    "description": "Standardized error responses and schemas",
                    "files_affected": "All error responses"
                })
        
        # Always add performance and monitoring features
        enhanced_spec = self.enhancement_strategies["performance"](enhanced_spec)
        enhancements_applied.append({
            "type": "Performance Features",
            "description": "Added caching headers and optimization parameters",
            "files_affected": "All endpoints"
        })
        
        enhanced_spec = self.enhancement_strategies["monitoring"](enhanced_spec)
        enhancements_applied.append({
            "type": "Monitoring Features",
            "description": "Added request/response metadata and observability",
            "files_affected": "All endpoints"
        })
        
        return enhanced_spec, enhancements_applied
    
    def _update_metadata(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Update API metadata for v2.0"""
        info = spec.get("info", {})
        
        # Update version
        info["version"] = "2.0.0"
        
        # Enhance description
        current_description = info.get("description", "")
        enhanced_description = current_description + "\n\n## Version 2.0 Enhancements\n\nThis version includes improved documentation, security, performance optimizations, and better developer experience."
        info["description"] = enhanced_description
        
        # Add new metadata
        info["termsOfService"] = info.get("termsOfService", "https://api.example.com/terms")
        info["contact"] = {
            "name": "API Support",
            "url": "https://api.example.com/support",
            "email": "support@example.com"
        }
        info["license"] = {
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT"
        }
        
        spec["info"] = info
        
        # Update OpenAPI version
        spec["openapi"] = "3.0.3"
        
        # Add new servers
        spec["servers"] = [
            {
                "url": "https://api.example.com/v2",
                "description": "Production server (v2.0)"
            },
            {
                "url": "https://staging-api.example.com/v2",
                "description": "Staging server"
            }
        ]
        
        # Add new tags
        spec["tags"] = [
            {
                "name": "authentication",
                "description": "Authentication and authorization endpoints"
            },
            {
                "name": "users",
                "description": "User management operations"
            },
            {
                "name": "analytics",
                "description": "Analytics and reporting endpoints"
            }
        ]
        
        return spec
    
    def _enhance_documentation(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance endpoint documentation"""
        paths = spec.get("paths", {})
        
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method.lower() in ["get", "post", "put", "patch", "delete"]:
                    # Enhance summary
                    if not operation.get("summary"):
                        operation["summary"] = self._generate_summary(path, method.upper())
                    
                    # Enhance description
                    if not operation.get("description") or len(operation.get("description", "")) < 50:
                        operation["description"] = self._generate_description(path, method.upper(), operation.get("summary", ""))
                    
                    # Add tags if missing
                    if not operation.get("tags"):
                        operation["tags"] = self._infer_tags(path, method.upper())
                    
                    # Document parameters better
                    if operation.get("parameters"):
                        for param in operation["parameters"]:
                            if not param.get("description"):
                                param["description"] = self._generate_parameter_description(param.get("name", ""), param.get("in", ""))
                    
                    # Enhance responses
                    if operation.get("responses"):
                        for status_code, response in operation["responses"].items():
                            if not response.get("description") or len(response.get("description", "")) < 20:
                                response["description"] = self._generate_response_description(status_code)
        
        return spec
    
    def _generate_summary(self, path: str, method: str) -> str:
        """Generate endpoint summary"""
        resource = self._extract_resource_name(path)
        action = self._get_action_for_method(method)
        return f"{action} {resource}"
    
    def _generate_description(self, path: str, method: str, summary: str) -> str:
        """Generate endpoint description"""
        resource = self._extract_resource_name(path)
        action = self._get_action_for_method(method)
        
        descriptions = {
            "GET": f"Retrieves {resource} information. Use this endpoint to fetch data with optional filtering and pagination.",
            "POST": f"Creates a new {resource}. Include all required properties in the request body.",
            "PUT": f"Updates an existing {resource} completely. All properties must be provided.",
            "PATCH": f"Partially updates an existing {resource}. Only changed properties need to be included.",
            "DELETE": f"Removes the specified {resource}. This operation cannot be undone."
        }
        
        return descriptions.get(method, f"{action} {resource} with the specified parameters.")
    
    def _generate_parameter_description(self, name: str, location: str) -> str:
        """Generate parameter description"""
        descriptions = {
            "id": "Unique identifier of the resource",
            "name": "Name of the resource or item",
            "limit": "Maximum number of results to return (default: 20, max: 100)",
            "offset": "Number of results to skip for pagination",
            "page": "Page number for pagination (1-based)",
            "sort": "Field to sort results by",
            "filter": "Filter criteria for results"
        }
        
        return descriptions.get(name, f"The {name} parameter for filtering and controlling the request")
    
    def _generate_response_description(self, status_code: str) -> str:
        """Generate response description"""
        descriptions = {
            "200": "Successful operation",
            "201": "Resource created successfully",
            "400": "Bad request - invalid parameters or request body",
            "401": "Unauthorized - valid authentication required",
            "403": "Forbidden - insufficient permissions",
            "404": "Resource not found",
            "409": "Conflict - resource already exists",
            "422": "Validation error - request data is invalid",
            "429": "Too many requests - rate limit exceeded",
            "500": "Internal server error",
            "503": "Service unavailable"
        }
        
        return descriptions.get(status_code, f"Response with status code {status_code}")
    
    def _extract_resource_name(self, path: str) -> str:
        """Extract resource name from URL path"""
        # Remove path parameters and common patterns
        path = re.sub(r'/\{[^}]+\}', '', path)
        
        # Get the main resource from path
        parts = [p for p in path.split('/') if p and not p.startswith('{')]
        if parts:
            # Prefer plural form for resources
            resource = parts[-1]
            if not resource.endswith('s') and resource not in ['auth', 'login', 'logout']:
                resource += 's'
            return resource
        
        return "resource"
    
    def _get_action_for_method(self, method: str) -> str:
        """Get action word for HTTP method"""
        actions = {
            "GET": "Retrieve",
            "POST": "Create",
            "PUT": "Update",
            "PATCH": "Modify",
            "DELETE": "Delete"
        }
        return actions.get(method, method.capitalize())
    
    def _infer_tags(self, path: str, method: str) -> List[str]:
        """Infer appropriate tags for endpoint"""
        tags = []
        
        # Auth endpoints
        if "auth" in path or "login" in path:
            tags.append("authentication")
        elif "user" in path:
            tags.append("users")
        elif "analytics" in path or "report" in path:
            tags.append("analytics")
        else:
            tags.append("general")
        
        return tags
    
    def _enhance_security(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance API security configuration"""
        # Initialize components if missing
        if "components" not in spec:
            spec["components"] = {}
        
        if "securitySchemes" not in spec["components"]:
            spec["components"]["securitySchemes"] = {}
        
        # Add comprehensive security schemes
        spec["components"]["securitySchemes"].update({
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "JWT token obtained from authentication endpoint"
            },
            "apiKey": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key",
                "description": "API key for server-to-server authentication"
            },
            "oauth2": {
                "type": "oauth2",
                "description": "OAuth2 authentication flow",
                "flows": {
                    "clientCredentials": {
                        "tokenUrl": "https://api.example.com/oauth/token",
                        "scopes": {
                            "read": "Read access to resources",
                            "write": "Write access to resources",
                            "admin": "Administrative access"
                        }
                    },
                    "authorizationCode": {
                        "authorizationUrl": "https://api.example.com/oauth/authorize",
                        "tokenUrl": "https://api.example.com/oauth/token",
                        "scopes": {
                            "read": "Read access to resources",
                            "write": "Write access to resources",
                            "admin": "Administrative access"
                        }
                    }
                }
            }
        })
        
        # Add global security requirement
        spec["security"] = [{"bearerAuth": []}]
        
        return spec
    
    def _add_pagination(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Add pagination parameters to list endpoints"""
        paths = spec.get("paths", {})
        
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method.lower() == "get":
                    # Check if this looks like a list endpoint
                    summary = operation.get("summary", "").lower()
                    if any(keyword in summary for keyword in ["list", "get", "search", "retrieve"]):
                        # Add pagination parameters
                        pagination_params = [
                            {
                                "name": "limit",
                                "in": "query",
                                "description": "Maximum number of results to return",
                                "required": False,
                                "schema": {
                                    "type": "integer",
                                    "minimum": 1,
                                    "maximum": 100,
                                    "default": 20
                                }
                            },
                            {
                                "name": "offset",
                                "in": "query",
                                "description": "Number of results to skip for pagination",
                                "required": False,
                                "schema": {
                                    "type": "integer",
                                    "minimum": 0,
                                    "default": 0
                                }
                            }
                        ]
                        
                        # Add cursor-based pagination as alternative
                        cursor_params = [
                            {
                                "name": "cursor",
                                "in": "query",
                                "description": "Pagination cursor for efficient navigation",
                                "required": False,
                                "schema": {
                                    "type": "string"
                                }
                            }
                        ]
                        
                        # Merge with existing parameters
                        existing_params = operation.get("parameters", [])
                        param_names = {p.get("name") for p in existing_params}
                        
                        for param in pagination_params + cursor_params:
                            if param["name"] not in param_names:
                                existing_params.append(param)
                        
                        operation["parameters"] = existing_params
        
        return spec
    
    def _improve_error_handling(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize error responses"""
        # Add error schema to components
        if "components" not in spec:
            spec["components"] = {}
        
        if "schemas" not in spec["components"]:
            spec["components"]["schemas"] = {}
        
        # Define standard error schema
        spec["components"]["schemas"]["Error"] = {
            "type": "object",
            "properties": {
                "error": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "Error code"},
                        "message": {"type": "string", "description": "Human-readable error message"},
                        "details": {"type": "object", "description": "Additional error details"},
                        "timestamp": {"type": "string", "format": "date-time", "description": "When the error occurred"},
                        "request_id": {"type": "string", "description": "Unique identifier for the request"}
                    },
                    "required": ["code", "message"]
                }
            },
            "required": ["error"]
        }
        
        # Add error responses to all endpoints
        paths = spec.get("paths", {})
        
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method.lower() in ["get", "post", "put", "patch", "delete"]:
                    responses = operation.get("responses", {})
                    
                    # Add standard error responses if missing
                    error_responses = {
                        "400": {
                            "description": "Bad request - invalid parameters or request body",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        },
                        "401": {
                            "description": "Unauthorized - valid authentication required",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        },
                        "403": {
                            "description": "Forbidden - insufficient permissions",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        },
                        "404": {
                            "description": "Resource not found",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        },
                        "429": {
                            "description": "Too many requests - rate limit exceeded",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        },
                        "500": {
                            "description": "Internal server error",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                    
                    # Merge with existing responses
                    for status_code, response in error_responses.items():
                        if status_code not in responses:
                            responses[status_code] = response
                    
                    operation["responses"] = responses
        
        return spec
    
    def _improve_consistency(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Improve API consistency patterns"""
        paths = spec.get("paths", {})
        
        # Analyze current patterns and suggest improvements
        path_patterns = {}
        method_patterns = {}
        
        for path, path_item in paths.items():
            # Normalize path (remove parameters for pattern analysis)
            base_path = re.sub(r'/\{[^}]+\}', '/{param}', path)
            if base_path not in path_patterns:
                path_patterns[base_path] = []
            path_patterns[base_path].append(path)
            
            for method in path_item:
                if method.lower() in ["get", "post", "put", "patch", "delete"]:
                    if method not in method_patterns:
                        method_patterns[method] = 0
                    method_patterns[method] += 1
        
        # Add consistency improvements
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method.lower() in ["get", "post", "put", "patch", "delete"]:
                    # Ensure operationId follows consistent pattern
                    if not operation.get("operationId"):
                        resource = self._extract_resource_name(path)
                        action = self._get_action_for_method(method)
                        operation["operationId"] = f"{action.lower()}{resource.capitalize()}"
                    
                    # Add tags for consistency
                    if not operation.get("tags"):
                        operation["tags"] = self._infer_tags(path, method.upper())
        
        return spec
    
    def _add_examples(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Add examples to schemas and endpoints"""
        # Add examples to schemas
        schemas = spec.get("components", {}).get("schemas", {})
        
        for schema_name, schema in schemas.items():
            if "example" not in schema and "examples" not in schema:
                schema["example"] = self._generate_schema_example(schema)
        
        # Add examples to endpoints
        paths = spec.get("paths", {})
        
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method.lower() in ["get", "post", "put", "patch", "delete"]:
                    # Add request body examples
                    if operation.get("requestBody"):
                        content = operation["requestBody"].get("content", {})
                        for media_type, media_info in content.items():
                            if "schema" in media_info and "example" not in media_info:
                                schema_ref = media_info["schema"]
                                if "$ref" in schema_ref:
                                    # Resolve schema reference and add example
                                    example = self._generate_request_example(schema_ref)
                                    if example:
                                        media_info["example"] = example
                    
                    # Add response examples
                    for status_code, response in operation.get("responses", {}).items():
                        content = response.get("content", {})
                        for media_type, media_info in content.items():
                            if "schema" in media_info and "example" not in media_info:
                                schema_ref = media_info["schema"]
                                if "$ref" in schema_ref:
                                    example = self._generate_response_example(schema_ref)
                                    if example:
                                        media_info["example"] = example
        
        return spec
    
    def _generate_schema_example(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate example for a schema"""
        schema_type = schema.get("type", "object")
        
        if schema_type == "object":
            example = {}
            properties = schema.get("properties", {})
            required = schema.get("required", [])
            
            for prop_name, prop_schema in properties.items():
                example[prop_name] = self._generate_property_example(prop_schema, prop_name in required)
            
            return example
        elif schema_type == "array":
            item_schema = schema.get("items", {})
            return [self._generate_property_example(item_schema, True)]
        else:
            return self._generate_primitive_example(schema)
    
    def _generate_property_example(self, prop_schema: Dict[str, Any], required: bool = False) -> Any:
        """Generate example for a property"""
        prop_type = prop_schema.get("type")
        prop_format = prop_schema.get("format")
        enum_values = prop_schema.get("enum", [])
        
        if enum_values:
            return enum_values[0]
        
        examples = {
            "string": {
                "format": {
                    "uuid": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "user@example.com",
                    "date-time": "2025-11-17T11:03:26Z",
                    "date": "2025-11-17",
                    "time": "11:03:26"
                },
                "default": "example_string"
            },
            "integer": {
                "format": {
                    "int32": 42,
                    "int64": 42
                },
                "default": 42
            },
            "number": {
                "format": {
                    "float": 42.5,
                    "double": 42.5
                },
                "default": 42.5
            },
            "boolean": True,
            "array": [1, 2, 3],
            "object": {"example": "object"}
        }
        
        if prop_format and prop_format in examples.get(prop_type, {}).get("format", {}):
            return examples[prop_type]["format"][prop_format]
        elif prop_type in examples:
            return examples[prop_type]
        else:
            return "example"
    
    def _generate_primitive_example(self, schema: Dict[str, Any]) -> Any:
        """Generate example for primitive types"""
        return self._generate_property_example(schema)
    
    def _generate_request_example(self, schema_ref: str) -> Dict[str, Any]:
        """Generate request example based on schema reference"""
        # This would resolve the schema reference and generate an example
        # For simplicity, return a generic example
        return {
            "example": "Request body example would be generated here based on the schema reference"
        }
    
    def _generate_response_example(self, schema_ref: str) -> Dict[str, Any]:
        """Generate response example based on schema reference"""
        # This would resolve the schema reference and generate an example
        # For simplicity, return a generic example
        return {
            "example": "Response body example would be generated here based on the schema reference"
        }
    
    def _add_performance_features(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Add performance optimization features"""
        paths = spec.get("paths", {})
        
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method.lower() in ["get", "post", "put", "patch", "delete"]:
                    responses = operation.get("responses", {})
                    
                    # Add cache headers to successful responses
                    for status_code in ["200", "201"]:
                        if status_code in responses:
                            content = responses[status_code].get("content", {})
                            for media_type, media_info in content.items():
                                headers = media_info.get("headers", {})
                                
                                # Add cache control headers
                                headers["Cache-Control"] = {
                                    "description": "Cache control directive",
                                    "schema": {"type": "string", "example": "public, max-age=3600"}
                                }
                                
                                # Add rate limit headers
                                headers["X-RateLimit-Limit"] = {
                                    "description": "Request rate limit per hour",
                                    "schema": {"type": "integer", "example": 1000}
                                }
                                
                                headers["X-RateLimit-Remaining"] = {
                                    "description": "Remaining requests in current window",
                                    "schema": {"type": "integer", "example": 999}
                                }
                                
                                media_info["headers"] = headers
                    
                    # Add performance parameters
                    params = operation.get("parameters", [])
                    param_names = {p.get("name") for p in params}
                    
                    # Add fields parameter for response filtering
                    if method.lower() == "get" and "fields" not in param_names:
                        params.append({
                            "name": "fields",
                            "in": "query",
                            "description": "Comma-separated list of fields to include in response",
                            "required": False,
                            "schema": {
                                "type": "string",
                                "example": "id,name,email"
                            }
                        })
                    
                    operation["parameters"] = params
        
        return spec
    
    def _add_monitoring_features(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Add monitoring and observability features"""
        paths = spec.get("paths", {})
        
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method.lower() in ["get", "post", "put", "patch", "delete"]:
                    responses = operation.get("responses", {})
                    
                    # Add request ID to successful responses
                    for status_code in ["200", "201"]:
                        if status_code in responses:
                            content = responses[status_code].get("content", {})
                            for media_type, media_info in content.items():
                                headers = media_info.get("headers", {})
                                
                                headers["X-Request-ID"] = {
                                    "description": "Unique identifier for the request",
                                    "schema": {"type": "string"}
                                }
                                
                                headers["X-Response-Time"] = {
                                    "description": "Time taken to process the request in milliseconds",
                                    "schema": {"type": "integer"}
                                }
                                
                                media_info["headers"] = headers
        
        return spec

class DatabaseManager:
    """Database operations for storing API analysis results"""
    
    def __init__(self):
        self.db_path = "dynamic_api_documenter.db"
    
    def save_analysis(self, original_spec: str, enhanced_spec: Dict[str, Any], 
                     weaknesses: List[Dict[str, str]], enhancements: List[Dict[str, str]], 
                     file_name: str = "") -> str:
        """Save analysis result to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            spec_id = str(uuid.uuid4())
            
            cursor.execute('''
                INSERT INTO api_specifications 
                (id, original_spec, enhanced_spec, weaknesses, enhancements, api_title, api_version, file_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                spec_id,
                original_spec,
                json.dumps(enhanced_spec),
                json.dumps(weaknesses),
                json.dumps(enhancements),
                enhanced_spec.get("info", {}).get("title", ""),
                enhanced_spec.get("info", {}).get("version", "2.0.0"),
                file_name
            ))
            
            conn.commit()
            return spec_id
            
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        finally:
            conn.close()
    
    def get_analysis(self, spec_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve analysis result from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, enhanced_spec, weaknesses, enhancements, api_title, api_version, analysis_timestamp
                FROM api_specifications
                WHERE id = ?
            ''', (spec_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return {
                "spec_id": row[0],
                "enhanced_spec": json.loads(row[1]),
                "weaknesses": json.loads(row[2]),
                "enhancements": json.loads(row[3]),
                "api_title": row[4],
                "api_version": row[5],
                "timestamp": row[6]
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        finally:
            conn.close()

# Initialize components
openapi_analyzer = OpenAPIAnalyzer()
api_spec_generator = APISpecGenerator()
db_manager = DatabaseManager()

# API Endpoints
@app.post("/api/v1/process", response_model=EnhancedSpec)
async def process_api_specification(request: AnalysisRequest, user: dict = Depends(verify_token)):
    """
    Main endpoint for API specification analysis and enhancement
    
    Args:
        request: Contains user_input (spec content) and optional context_file
        user: Authenticated user object
    
    Returns:
        EnhancedSpec with enhanced OpenAPI specification and analysis
    """
    try:
        # Generate analysis ID
        spec_id = str(uuid.uuid4())
        
        # For this template, we expect the spec content in user_input
        # In a real implementation, this would process uploaded files
        spec_content = request.user_input
        
        # Determine format (assume JSON for this demo)
        spec_format = "json"
        
        # Analyze specification
        analysis = openapi_analyzer.analyze_spec(spec_content, spec_format)
        
        # Generate enhanced specification
        enhanced_spec, enhancements_applied = api_spec_generator.generate_enhanced_spec(
            analysis, analysis["weaknesses"]
        )
        
        # Create result
        result = EnhancedSpec(
            spec_id=spec_id,
            enhanced_openapi=enhanced_spec,
            weaknesses_identified=analysis["weaknesses"],
            enhancements_made=enhancements_applied,
            improvements_by_endpoint=[],  # Could be populated with endpoint-specific improvements
            timestamp=datetime.now().isoformat()
        )
        
        # Save to database
        db_manager.save_analysis(
            spec_content, enhanced_spec, 
            analysis["weaknesses"], enhancements_applied,
            request.context_file or ""
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/v1/upload-spec")
async def upload_api_spec(file: UploadFile = File(...), user: dict = Depends(verify_token)):
    """
    Upload and analyze API specification file
    
    Args:
        file: OpenAPI specification file (JSON or YAML)
        user: Authenticated user object
    
    Returns:
        EnhancedSpec with enhanced specification
    """
    try:
        # Read file content
        content = await file.read()
        spec_content = content.decode('utf-8')
        
        # Determine file format
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension in ['yaml', 'yml']:
            spec_format = 'yaml'
        else:
            spec_format = 'json'
        
        # Generate analysis ID
        spec_id = str(uuid.uuid4())
        
        # Analyze specification
        analysis = openapi_analyzer.analyze_spec(spec_content, spec_format)
        
        # Generate enhanced specification
        enhanced_spec, enhancements_applied = api_spec_generator.generate_enhanced_spec(
            analysis, analysis["weaknesses"]
        )
        
        # Create result
        result = EnhancedSpec(
            spec_id=spec_id,
            enhanced_openapi=enhanced_spec,
            weaknesses_identified=analysis["weaknesses"],
            enhancements_made=enhancements_applied,
            improvements_by_endpoint=[],
            timestamp=datetime.now().isoformat()
        )
        
        # Save to database
        db_manager.save_analysis(
            spec_content, enhanced_spec,
            analysis["weaknesses"], enhancements_applied,
            file.filename
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Specification analysis failed: {str(e)}")

@app.get("/api/v1/analysis/{spec_id}", response_model=EnhancedSpec)
async def get_analysis(spec_id: str, user: dict = Depends(verify_token)):
    """
    Retrieve stored analysis result
    
    Args:
        spec_id: Unique specification identifier
        user: Authenticated user object
    
    Returns:
        EnhancedSpec
    """
    result = db_manager.get_analysis(spec_id)
    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return EnhancedSpec(
        spec_id=result["spec_id"],
        enhanced_spec=result["enhanced_spec"],
        weaknesses_identified=result["weaknesses"],
        enhancements_made=result["enhancements"],
        improvements_by_endpoint=[],
        timestamp=result["timestamp"]
    )

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Dynamic API Documenter", "version": "1.0.0"}

@app.post("/api/v1/generate-token")
async def generate_token():
    """Generate a demo JWT token for testing"""
    payload = {
        "user_id": "demo_user",
        "username": "demo_user",
        "exp": datetime.utcnow().timestamp() + 3600  # 1 hour expiration
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "timestamp": datetime.now().isoformat()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "timestamp": datetime.now().isoformat()}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
