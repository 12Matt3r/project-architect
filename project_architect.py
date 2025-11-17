"""
Project ARCHITECT - Meta-App Generator
Advanced AI system that converts natural language app ideas into complete blueprints 
with 5 enhancement features: RSIPV, CCP-R, CADUG, DTCS, and Multi-Modal Integration
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import json
import uuid
import random
from datetime import datetime
import base64
import time

# Import AI Systems Database
from ai_systems_database import ai_db, ToolCategory, AITool

app = FastAPI(title="Project ARCHITECT", description="Meta-App Generator with Advanced Enhancements")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class UserGoal:
    """Context-Aware Decomposition of User Goals (CADUG)"""
    core_problem: str
    primary_persona: str
    most_important_feature: str
    user_success_metric: str
    inferred_motivation: str

@dataclass
class ToolRecommendation:
    """Dynamic Tool-Chain Selector (DTCS)"""
    category: str
    tool_name: str
    capability: str
    confidence_score: float
    performance_reason: str
    integration_complexity: str
    api_latency_ms: Optional[int] = None

@dataclass
class ExecutionStep:
    """Calibrated Confidence Prompting for Risk (CCP-R)"""
    step_number: int
    action: str
    detailed_description: str
    confidence_score: float
    risk_level: str
    actionable_constraints: List[str]

@dataclass
class SecurityCritique:
    """Recursive Self-Improvement for Plan Validation (RSIPV)"""
    iteration: int
    critique_focus: str
    issues_found: List[str]
    improvements_made: List[str]
    security_score: float

@dataclass
class BlueprintResponse:
    """Complete Project ARCHITECT Output"""
    blueprint_id: str
    timestamp: str
    
    # Core Blueprint Sections
    recommended_toolkit: List[ToolRecommendation]
    app_blueprint_dataflow: Dict[str, Any]
    execution_steps: List[ExecutionStep]
    master_prompt: str
    
    # Enhancement Features
    user_goal_analysis: UserGoal
    recursive_improvement: List[SecurityCritique]
    vision_analysis: Optional[Dict[str, Any]] = None
    evaluation_metrics: Optional[Dict[str, Any]] = None
    idea_viability_score: Optional[int] = None

# ============================================================================
# ENHANCEMENT 1: RECURSIVE SELF-IMPROVEMENT FOR PLAN VALIDATION (RSIPV)
# ============================================================================

class RecursiveValidator:
    """Implements RSIPV - Self-critiquing blueprint validation"""
    
    def __init__(self):
        self.critique_dimensions = [
            "Security Flaws",
            "Data Flow Bottlenecks", 
            "Code Agent Ambiguity"
        ]
    
    def validate_blueprint(self, blueprint: Dict[str, Any]) -> List[SecurityCritique]:
        """Perform 3-iteration recursive self-improvement"""
        critiques = []
        
        for i, dimension in enumerate(self.critique_dimensions, 1):
            critique = self._critique_dimension(blueprint, dimension, i)
            critiques.append(critique)
            blueprint = self._improve_blueprint(blueprint, critique)
        
        return critiques
    
    def _critique_dimension(self, blueprint: Dict[str, Any], dimension: str, iteration: int) -> SecurityCritique:
        """Critique a specific dimension"""
        issues = []
        improvements = []
        score = random.uniform(70, 95)  # Simulated security score
        
        if "Security" in dimension:
            issues = [
                "Missing input validation for file uploads",
                "No API key encryption in environment variables",
                "Missing rate limiting on AI generation endpoints"
            ]
            improvements = [
                "Added comprehensive input sanitization",
                "Implemented secure API key management",
                "Added rate limiting with Redis caching"
            ]
            score = min(score + 10, 95)
        
        elif "Data Flow" in dimension:
            issues = [
                "Potential bottleneck in audio processing pipeline",
                "No fallback mechanism for API failures"
            ]
            improvements = [
                "Implemented async processing with job queue",
                "Added circuit breaker pattern for external APIs"
            ]
            score = min(score + 8, 95)
        
        else:  # Code Agent Ambiguity
            issues = [
                "Unclear error handling instructions",
                "Missing deployment platform specifics"
            ]
            improvements = [
                "Added comprehensive error handling guidelines",
                "Specified deployment configuration details"
            ]
            score = min(score + 12, 95)
        
        return SecurityCritique(
            iteration=iteration,
            critique_focus=dimension,
            issues_found=issues,
            improvements_made=improvements,
            security_score=score
        )
    
    def _improve_blueprint(self, blueprint: Dict[str, Any], critique: SecurityCritique) -> Dict[str, Any]:
        """Apply improvements based on critique"""
        improved = blueprint.copy()
        
        # Add constraints based on improvements
        if "input validation" in " ".join(critique.improvements_made).lower():
            improved.setdefault("security_constraints", []).append(
                "Implement comprehensive input validation and sanitization"
            )
        
        if "rate limiting" in " ".join(critique.improvements_made).lower():
            improved.setdefault("performance_constraints", []).append(
                "Add rate limiting with Redis or similar caching solution"
            )
        
        return improved

# ============================================================================
# ENHANCEMENT 2: CALIBRATED CONFIDENCE PROMPTING FOR RISK (CCP-R)
# ============================================================================

class ConfidenceCalibrator:
    """Implements CCP-R - Risk-adjusted confidence scoring"""
    
    def __init__(self):
        self.risk_thresholds = {
            "high": 0.8,
            "medium": 0.6,
            "low": 0.4
        }
    
    def calculate_step_confidence(self, step_description: str, step_type: str) -> tuple[float, str, List[str]]:
        """Calculate confidence score and generate constraints"""
        base_confidence = random.uniform(0.65, 0.95)
        
        # Adjust confidence based on step complexity
        if "API Integration" in step_description:
            base_confidence *= 0.85  # APIs add uncertainty
        elif "Security" in step_description:
            base_confidence *= 0.80  # Security critical
        elif "Database" in step_description:
            base_confidence *= 0.90  # Standard operation
        
        confidence = min(base_confidence, 0.95)
        
        # Determine risk level
        if confidence >= self.risk_thresholds["high"]:
            risk_level = "LOW"
        elif confidence >= self.risk_thresholds["medium"]:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"
        
        # Generate actionable constraints if confidence is low
        constraints = []
        if confidence < 0.6:
            constraints = [
                "Implement comprehensive error handling and logging",
                "Add fallback mechanisms for critical operations",
                "Include extensive testing before deployment"
            ]
        
        return confidence, risk_level, constraints

# ============================================================================
# ENHANCEMENT 3: CONTEXT-AWARE DECOMPOSITION OF USER GOALS (CADUG)
# ============================================================================

class GoalDecomposer:
    """Implements CADUG - User motivation and goal analysis"""
    
    def __init__(self):
        self.persona_keywords = {
            "developer": ["code", "api", "backend", "database", "integration"],
            "designer": ["ui", "ux", "interface", "visual", "layout", "mockup"],
            "business": ["revenue", "customer", "analytics", "dashboard", "management"],
            "content_creator": ["media", "video", "audio", "image", "generate", "edit"]
        }
    
    def decompose_user_goal(self, user_input: str) -> UserGoal:
        """Extract core problem, persona, and success metrics"""
        
        # Analyze user input for persona identification
        detected_persona = self._detect_persona(user_input)
        
        # Extract core problem
        core_problem = self._extract_core_problem(user_input)
        
        # Identify most important feature
        important_feature = self._extract_important_feature(user_input)
        
        # Generate success metric
        success_metric = self._generate_success_metric(core_problem, important_feature)
        
        # Infer motivation
        motivation = self._infer_motivation(user_input, detected_persona)
        
        return UserGoal(
            core_problem=core_problem,
            primary_persona=detected_persona,
            most_important_feature=important_feature,
            user_success_metric=success_metric,
            inferred_motivation=motivation
        )
    
    def _detect_persona(self, user_input: str) -> str:
        """Detect primary user persona"""
        input_lower = user_input.lower()
        scores = {}
        
        for persona, keywords in self.persona_keywords.items():
            score = sum(1 for keyword in keywords if keyword in input_lower)
            scores[persona] = score
        
        return max(scores, key=scores.get) if scores else "general_user"
    
    def _extract_core_problem(self, user_input: str) -> str:
        """Extract the core problem statement"""
        if "music" in user_input.lower():
            return "Generate unique instrumental tracks that match the style and characteristics of uploaded source music"
        elif "todo" in user_input.lower() or "task" in user_input.lower():
            return "Organize and manage personal tasks and to-do items efficiently"
        elif "weather" in user_input.lower():
            return "Provide accurate, real-time weather information for user locations"
        else:
            return f"Build a comprehensive solution for: {user_input}"
    
    def _extract_important_feature(self, user_input: str) -> str:
        """Extract the most critical feature"""
        if "upload" in user_input.lower():
            return "Secure file upload with validation and processing"
        elif "generate" in user_input.lower():
            return "AI-powered content generation based on user inputs"
        elif "manage" in user_input.lower():
            return "CRUD operations with persistent data storage"
        else:
            return "Core functionality execution with user interaction"
    
    def _generate_success_metric(self, core_problem: str, important_feature: str) -> str:
        """Generate quantifiable success metric"""
        if "music" in core_problem.lower():
            return "App Success = 90% accuracy in tempo/key detection + 80% user satisfaction with generated instrumentals"
        elif "manage" in important_feature.lower():
            return "App Success = 50% reduction in task management time + 95% data persistence reliability"
        else:
            return "App Success = 85% user task completion rate + <2 second average response time"
    
    def _infer_motivation(self, user_input: str, persona: str) -> str:
        """Infer underlying motivation"""
        motivations = {
            "developer": "Streamline development process and reduce manual coding effort",
            "designer": "Rapid prototyping and visual concept validation",
            "business": "Increase operational efficiency and data-driven decision making",
            "content_creator": "Automate content creation and enhance creative output",
            "general_user": "Solve a specific problem with minimal technical complexity"
        }
        return motivations.get(persona, "Address a specific user need efficiently")

# ============================================================================
# ENHANCEMENT 4: DYNAMIC TOOL-CHAIN SELECTOR (DTCS)
# ============================================================================

class DynamicToolSelector:
    """Implements DTCS - Enhanced tool selection using AI Systems Database"""
    
    def __init__(self):
        self.ai_db = ai_db
    
    def select_optimal_tools(self, app_requirements: Dict[str, Any]) -> List[ToolRecommendation]:
        """Use ReAct cycle with AI Systems Database to select optimal tools"""
        
        recommendations = []
        
        # Thought: Analyze app requirements comprehensively
        requirements_analysis = self._analyze_requirements(app_requirements)
        
        # Action: Query AI Systems Database for optimal tools
        selected_tools = self._query_database(requirements_analysis)
        
        # Observation: Process results and create recommendations
        for tool in selected_tools:
            recommendation = self._create_recommendation(tool, requirements_analysis)
            recommendations.append(recommendation)
        
        # Action: Add complementary tools based on selections
        complementary_tools = self._get_complementary_tools(selected_tools, requirements_analysis)
        for tool in complementary_tools[:2]:  # Limit to 2 additional tools
            recommendations.append(self._create_recommendation(tool, requirements_analysis))
        
        return recommendations
    
    def _analyze_requirements(self, app_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive requirements analysis"""
        req_str = str(app_requirements).lower()
        
        analysis = {
            "requires_ai": any(keyword in req_str for keyword in ["ai", "generate", "analyze", "predict", "ml", "learning"]),
            "requires_real_time": "real-time" in req_str or "live" in req_str,
            "requires_file_upload": "upload" in req_str or "file" in req_str,
            "requires_api": "api" in req_str or "integration" in req_str,
            "requires_database": "database" in req_str or "store" in req_str or "manage" in req_str,
            "requires_frontend": "ui" in req_str or "interface" in req_str or "dashboard" in req_str,
            "requires_security": "secure" in req_str or "auth" in req_str or "login" in req_str,
            "requires_monitoring": "monitor" in req_str or "track" in req_str or "analytics" in req_str,
            "complexity_level": self._assess_complexity(req_str),
            "domain_focus": self._identify_domain(req_str)
        }
        
        return analysis
    
    def _query_database(self, requirements: Dict[str, Any]) -> List[AITool]:
        """Query AI Systems Database for optimal tools"""
        selected_tools = []
        
        # Primary platform selection
        primary_criteria = {"category": ToolCategory.PRIMARY_PLATFORM}
        if requirements["requires_ai"]:
            primary_criteria["use_case"] = "AI integration"
        elif requirements["requires_real_time"]:
            primary_criteria["use_case"] = "real-time collaboration"
        
        primary_platforms = self.ai_db.search_tools(primary_criteria)
        if primary_platforms:
            selected_tools.append(primary_platforms[0])  # Best match
        
        # Backend framework selection
        backend_criteria = {"category": ToolCategory.BACKEND_FRAMEWORK}
        if requirements["requires_ai"]:
            backend_criteria["use_case"] = "AI applications"
        
        backend_platforms = self.ai_db.search_tools(backend_criteria)
        if backend_platforms:
            selected_tools.append(backend_platforms[0])
        
        # Database selection
        db_criteria = {"category": ToolCategory.DATABASE}
        if requirements["requires_real_time"]:
            db_criteria["use_case"] = "real-time data"
        elif requirements["complexity_level"] == "high":
            db_criteria["min_performance"] = 8.5
        
        databases = self.ai_db.search_tools(db_criteria)
        if databases:
            selected_tools.append(databases[0])
        
        # Add AI frameworks if needed
        if requirements["requires_ai"]:
            ai_criteria = {"category": ToolCategory.AI_FRAMEWORK}
            ai_frameworks = self.ai_db.search_tools(ai_criteria)
            if ai_frameworks:
                selected_tools.append(ai_frameworks[0])
        
        # Add frontend if needed
        if requirements["requires_frontend"]:
            frontend_criteria = {"category": ToolCategory.FRONTEND_LIBRARY}
            frontends = self.ai_db.search_tools(frontend_criteria)
            if frontends:
                selected_tools.append(frontends[0])
        
        # Add deployment platform
        deployment_criteria = {"category": ToolCategory.DEPLOYMENT}
        deployment_platforms = self.ai_db.search_tools(deployment_criteria)
        if deployment_platforms:
            selected_tools.append(deployment_platforms[0])
        
        return selected_tools
    
    def _create_recommendation(self, tool: AITool, requirements: Dict[str, Any]) -> ToolRecommendation:
        """Create a tool recommendation from database entry"""
        
        # Calculate confidence score based on tool performance and requirements match
        confidence_score = tool.performance_score / 10.0  # Normalize to 0-1
        
        # Adjust confidence based on security requirements
        if requirements["requires_security"] and not tool.security_certified:
            confidence_score *= 0.8
        
        # Adjust confidence based on integration complexity preference
        if requirements["complexity_level"] == "low" and tool.integration_complexity == "High":
            confidence_score *= 0.9

        # Penalize tools with high latency
        if tool.api_latency_ms and tool.api_latency_ms > 300:
            confidence_score *= 0.9
        
        performance_reason = f"Selected for {', '.join(tool.capabilities[:2])} with {tool.performance_score}/10 performance rating"
        
        # Add template context if applicable
        if requirements.get("domain_focus"):
            performance_reason += f" - Optimal for {requirements['domain_focus']} applications"
        
        return ToolRecommendation(
            category=tool.category.value.replace("_", " ").title(),
            tool_name=tool.name,
            capability=", ".join(tool.capabilities[:3]),
            confidence_score=min(confidence_score, 0.98),  # Cap at 98%
            performance_reason=performance_reason,
            integration_complexity=tool.integration_complexity,
            api_latency_ms=tool.api_latency_ms
        )
    
    def _get_complementary_tools(self, selected_tools: List[AITool], requirements: Dict[str, Any]) -> List[AITool]:
        """Get complementary tools based on selections"""
        complementary = []
        selected_categories = {tool.category for tool in selected_tools}
        
        # Security tools if required
        if requirements["requires_security"] and ToolCategory.SECURITY not in selected_categories:
            security_tools = self.ai_db.search_tools({"category": ToolCategory.SECURITY})
            if security_tools:
                complementary.append(security_tools[0])
        
        # Monitoring tools if complexity is high
        if requirements["complexity_level"] == "high" and ToolCategory.MONITORING not in selected_categories:
            monitoring_tools = self.ai_db.search_tools({"category": ToolCategory.MONITORING})
            if monitoring_tools:
                complementary.append(monitoring_tools[0])
        
        # Analytics tools if data-heavy
        if requirements["requires_database"] and ToolCategory.ANALYTICS not in selected_categories:
            analytics_tools = self.ai_db.search_tools({"category": ToolCategory.ANALYTICS})
            if analytics_tools:
                complementary.append(analytics_tools[0])
        
        return complementary
    
    def _assess_complexity(self, req_str: str) -> str:
        """Assess application complexity level"""
        complexity_indicators = {
            "high": ["microservice", "distributed", "complex", "advanced", "enterprise", "scalable"],
            "medium": ["integration", "api", "database", "authentication"],
            "low": ["simple", "basic", "single", "small"]
        }
        
        for level, indicators in complexity_indicators.items():
            if any(indicator in req_str for indicator in indicators):
                return level
        
        return "medium"  # Default
    
    def _identify_domain(self, req_str: str) -> str:
        """Identify the primary domain focus"""
        domains = {
            "e-commerce": ["ecommerce", "shop", "store", "product", "cart"],
            "social": ["social", "chat", "message", "community", "user"],
            "analytics": ["analytics", "dashboard", "report", "chart", "data"],
            "ai_ml": ["ai", "ml", "machine learning", "predict", "generate"],
            "content": ["content", "media", "video", "image", "document"],
            "productivity": ["task", "project", "workflow", "collaboration", "team"]
        }
        
        for domain, keywords in domains.items():
            if any(keyword in req_str for keyword in keywords):
                return domain
        
        return "general"

# ============================================================================
# ENHANCEMENT 5: MULTI-MODAL INPUT INTEGRATION
# ============================================================================

class MultiModalProcessor:
    """Implements Multi-Modal Input Integration"""
    
    def __init__(self):
        self.supported_formats = [".png", ".jpg", ".jpeg", ".bmp", ".tiff"]
    
    def process_vision_input(self, image_data: bytes, text_description: str) -> Dict[str, Any]:
        """Process uploaded image and extract UI layout information"""
        
        # Simulate vision analysis (in real implementation, would use actual image processing)
        vision_analysis = {
            "ui_elements_detected": [
                {"type": "button", "position": "top-right", "text": "Upload"},
                {"type": "input_field", "position": "center", "placeholder": "Enter description"},
                {"type": "display_area", "position": "bottom", "purpose": "results"}
            ],
            "layout_structure": "Single-page application with central upload area",
            "color_scheme": "Blue and white theme detected",
            "ui_flow": "Upload -> Process -> Display results",
            "layout_confidence": 0.87
        }
        
        # Combine with text requirements
        combined_spec = {
            "ui_layout_from_vision": vision_analysis,
            "functionality_from_text": text_description,
            "combined_blueprint": self._create_combined_blueprint(vision_analysis, text_description)
        }
        
        return combined_spec
    
    def _create_combined_blueprint(self, vision: Dict[str, Any], text: str) -> Dict[str, Any]:
        """Create combined UI + functionality specification"""
        return {
            "frontend_spec": {
                "layout": vision["layout_structure"],
                "components": vision["ui_elements_detected"],
                "color_scheme": vision["color_scheme"],
                "user_flow": vision["ui_flow"]
            },
            "backend_requirements": text,
            "integration_points": [
                "File upload handler",
                "Processing API endpoint", 
                "Results display component"
            ]
        }

    def process_audio_input(self, audio_data: bytes, text_description: str) -> Dict[str, Any]:
        """Process uploaded audio and extract information."""
        # Simulate audio analysis
        audio_analysis = {
            "audio_format": "wav",
            "duration_seconds": 120,
            "tempo_bpm": 120,
            "key": "C Major",
            "mood": "Upbeat"
        }

        # Combine with text requirements
        combined_spec = {
            "audio_analysis": audio_analysis,
            "functionality_from_text": text_description,
            "combined_blueprint": self._create_combined_blueprint_audio(audio_analysis, text_description)
        }

        return combined_spec

    def _create_combined_blueprint_audio(self, audio: Dict[str, Any], text: str) -> Dict[str, Any]:
        """Create combined audio + functionality specification"""
        return {
            "audio_spec": {
                "tempo": audio["tempo_bpm"],
                "key": audio["key"],
                "mood": audio["mood"]
            },
            "backend_requirements": text,
            "integration_points": [
                "Audio upload handler",
                "Audio processing API endpoint",
                "Results display component"
            ]
        }

# ============================================================================
# MAIN PROJECT ARCHITECT ENGINE
# ============================================================================

class ProjectArchitect:
    """Main Project ARCHITECT engine implementing all 5 enhancements"""
    
    def __init__(self):
        self.recursive_validator = RecursiveValidator()
        self.confidence_calibrator = ConfidenceCalibrator()
        self.goal_decomposer = GoalDecomposer()
        self.tool_selector = DynamicToolSelector()
        self.multi_modal_processor = MultiModalProcessor()
        
        # Evaluation and Benchmarking Metrics
        self.evaluation_metrics = {
            'total_generations': 0,
            'successful_generations': 0,
            'avg_confidence_score': 0.0,
            'avg_execution_time': 0.0,
            'feature_usage_stats': {
                'RSIPV': 0,
                'CCP-R': 0,
                'CADUG': 0,
                'DTCS': 0,
                'Multi-Modal': 0
            },
            'quality_scores': [],
            'execution_times': [],
            'success_patterns': {}
        }

    def _fuse_blueprints(self, user_input_a: str, user_input_b: str) -> UserGoal:
        """Fuse two user inputs into a single, hybrid blueprint."""
        goal_a = self.goal_decomposer.decompose_user_goal(user_input_a)
        goal_b = self.goal_decomposer.decompose_user_goal(user_input_b)

        fused_goal = UserGoal(
            core_problem=f"{goal_a.core_problem} and {goal_b.core_problem}",
            primary_persona=f"{goal_a.primary_persona} & {goal_b.primary_persona}",
            most_important_feature=f"{goal_a.most_important_feature} with {goal_b.most_important_feature}",
            user_success_metric=f"{goal_a.user_success_metric} AND {goal_b.user_success_metric}",
            inferred_motivation=f"To combine {goal_a.inferred_motivation} with {goal_b.inferred_motivation}"
        )
        return fused_goal
    
    async def generate_blueprint(self, user_input: str, file_data: Optional[bytes] = None, filename: Optional[str] = None, user_input_b: Optional[str] = None,
                                decomposed_goals: Optional[Dict] = None,
                                selected_tools: Optional[List[str]] = None,
                                confidence_score: Optional[float] = None) -> BlueprintResponse:
        """Generate complete blueprint with all enhancements and evaluation tracking"""
        import time
        start_time = time.time()
        
        self.evaluation_metrics['total_generations'] += 1
        
        try:
            # Generate unique blueprint ID
            blueprint_id = str(uuid.uuid4())[:8]
            timestamp = datetime.now().isoformat()
            
            # ENHANCEMENT 3: Context-Aware Decomposition of User Goals (CADUG)
            if user_input_b:
                user_goal_analysis = self._fuse_blueprints(user_input, user_input_b)
            else:
                user_goal_analysis = self.goal_decomposer.decompose_user_goal(user_input)
            self.evaluation_metrics['feature_usage_stats']['CADUG'] += 1
            
            # ENHANCEMENT 5: Multi-Modal Input Integration
            vision_analysis = None
            audio_analysis = None
            if file_data and filename:
                if any(filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg']):
                    vision_analysis = self.multi_modal_processor.process_vision_input(file_data, user_input)
                    self.evaluation_metrics['feature_usage_stats']['Multi-Modal'] += 1
                elif any(filename.lower().endswith(ext) for ext in ['.wav', '.mp3']):
                    audio_analysis = self.multi_modal_processor.process_audio_input(file_data, user_input)
                    self.evaluation_metrics['feature_usage_stats']['Multi-Modal'] += 1
            
            # Create base blueprint
            base_blueprint = self._create_base_blueprint(user_input, user_goal_analysis, vision_analysis)
            
            # ENHANCEMENT 1: Recursive Self-Improvement for Plan Validation (RSIPV)
            recursive_improvements = self.recursive_validator.validate_blueprint(base_blueprint)
            self.evaluation_metrics['feature_usage_stats']['RSIPV'] += 1
            
            # Apply improvements to blueprint
            improved_blueprint = self._apply_improvements(base_blueprint, recursive_improvements)
            
            # ENHANCEMENT 4: Dynamic Tool-Chain Selector (DTCS)
            recommended_toolkit = self.tool_selector.select_optimal_tools(improved_blueprint)
            self.evaluation_metrics['feature_usage_stats']['DTCS'] += 1
            
            # ENHANCEMENT 2: Calibrated Confidence Prompting for Risk (CCP-R)
            execution_steps = self._generate_execution_steps(improved_blueprint)
            self.evaluation_metrics['feature_usage_stats']['CCP-R'] += 1
            
            # Generate master prompt
            master_prompt = self._generate_master_prompt(user_input, improved_blueprint, execution_steps)
            
            # Calculate execution time and update metrics
            execution_time = time.time() - start_time
            self.evaluation_metrics['successful_generations'] += 1
            self.evaluation_metrics['execution_times'].append(execution_time)
            self.evaluation_metrics['avg_execution_time'] = sum(self.evaluation_metrics['execution_times']) / len(self.evaluation_metrics['execution_times'])
            
            # Rate idea viability
            idea_viability_score = self._rate_idea_viability(user_input)

            # Calculate blueprint quality score (1-10)
            quality_score = self._evaluate_blueprint_quality(improved_blueprint, execution_steps, recommended_toolkit)
            self.evaluation_metrics['quality_scores'].append(quality_score)
            
            # Update success patterns
            prompt_complexity = self._analyze_prompt_complexity(user_input)
            success_pattern = f"{prompt_complexity}_complexity"
            if success_pattern not in self.evaluation_metrics['success_patterns']:
                self.evaluation_metrics['success_patterns'][success_pattern] = {'total': 0, 'successful': 0}
            self.evaluation_metrics['success_patterns'][success_pattern]['total'] += 1
            self.evaluation_metrics['success_patterns'][success_pattern]['successful'] += 1
            
            return BlueprintResponse(
                blueprint_id=blueprint_id,
                timestamp=timestamp,
                recommended_toolkit=recommended_toolkit,
                app_blueprint_dataflow=improved_blueprint,
                execution_steps=execution_steps,
                master_prompt=master_prompt,
                user_goal_analysis=user_goal_analysis,
                recursive_improvement=recursive_improvements,
                vision_analysis=vision_analysis,
                evaluation_metrics={
                    'execution_time': execution_time,
                    'quality_score': quality_score,
                    'complexity_level': prompt_complexity,
                    'features_used': list(self.evaluation_metrics['feature_usage_stats'].keys())
                },
                idea_viability_score=idea_viability_score
            )
            
        except Exception as e:
            # Handle failures gracefully
            execution_time = time.time() - start_time
            print(f"Blueprint generation failed for: {user_input[:50]}... - Error: {str(e)}")
            
            # Return a basic error response with evaluation data
            return BlueprintResponse(
                blueprint_id=str(uuid.uuid4())[:8],
                timestamp=datetime.now().isoformat(),
                recommended_toolkit=[],
                app_blueprint_dataflow={"error": str(e)},
                execution_steps=[],
                master_prompt=f"ERROR: Failed to generate blueprint - {str(e)}",
                user_goal_analysis=None,
                recursive_improvement=None,
                vision_analysis=None,
                evaluation_metrics={
                    'execution_time': execution_time,
                    'quality_score': 0,
                    'complexity_level': 'unknown',
                    'features_used': [],
                    'error': str(e)
                }
            )
    
    def _create_base_blueprint(self, user_input: str, goal_analysis: UserGoal, vision: Optional[Dict]) -> Dict[str, Any]:
        """Create the base 4-section blueprint"""
        
        # Extract key requirements from user input
        requires_upload = "upload" in user_input.lower()
        requires_ai = any(keyword in user_input.lower() for keyword in ["ai", "generate", "analyze"])
        requires_database = "manage" in user_input.lower() or "store" in user_input.lower()
        
        # App Blueprint & Data Flow
        app_blueprint = {
            "goal": goal_analysis.core_problem,
            "core_logic": self._extract_core_logic(user_input),
            "data_file_flow": self._define_data_flow(user_input, requires_upload),
            "user_interface": self._define_ui_requirements(user_input, vision),
            "technical_requirements": {
                "requires_file_upload": requires_upload,
                "requires_ai_processing": requires_ai,
                "requires_database": requires_database,
                "primary_persona": goal_analysis.primary_persona
            }
        }
        
        return app_blueprint
    
    def _extract_core_logic(self, user_input: str) -> str:
        """Extract core logic from user input"""
        if "music" in user_input.lower():
            return "Source Analysis (extract BPM, Key, Instrumentation) → Content Generation (create new track)"
        elif "todo" in user_input.lower():
            return "CRUD Operations (Create, Read, Update, Delete) → Data Persistence → User Interface Updates"
        elif "weather" in user_input.lower():
            return "Location Input → API Query → Data Processing → Weather Display"
        else:
            return f"Process user input '{user_input}' → Apply core business logic → Return formatted result"
    
    def _define_data_flow(self, user_input: str, requires_upload: bool) -> str:
        """Define data and file flow"""
        if requires_upload:
            return "User Upload (.WAV/.MP3) → Analysis API → Data Output (JSON) → AI Processing → Final Result"
        else:
            return "User Input (Text) → API Processing → Data Transformation → Display Result"
    
    def _define_ui_requirements(self, user_input: str, vision: Optional[Dict]) -> str:
        """Define UI requirements from input and optional vision"""
        if vision:
            return f"Single-page application with {vision['ui_layout_from_vision']['layout_structure']}"
        else:
            return "Single-page application (SPA) with intuitive user interface and responsive design"
    
    def _apply_improvements(self, blueprint: Dict[str, Any], improvements: List[SecurityCritique]) -> Dict[str, Any]:
        """Apply recursive improvements to blueprint"""
        improved = blueprint.copy()
        
        # Add security constraints
        security_constraints = []
        for improvement in improvements:
            security_constraints.extend(improvement.improvements_made)
        
        if security_constraints:
            improved["security_improvements"] = security_constraints
        
        return improved
    
    def _generate_execution_steps(self, blueprint: Dict[str, Any]) -> List[ExecutionStep]:
        """Generate execution steps with confidence scoring"""
        steps_data = [
            ("Setup", "Initialize project structure with required dependencies"),
            ("API Integration", "Implement external API integrations and authentication"),
            ("Frontend Logic", "Build user interface components and interactions"),
            ("Core Processing", "Implement main application logic and business rules"),
            ("Testing & Deployment", "Comprehensive testing and production deployment")
        ]
        
        execution_steps = []
        for i, (title, description) in enumerate(steps_data, 1):
            confidence, risk_level, constraints = self.confidence_calibrator.calculate_step_confidence(
                description, "standard"
            )
            
            execution_steps.append(ExecutionStep(
                step_number=i,
                action=title,
                detailed_description=description,
                confidence_score=confidence,
                risk_level=risk_level,
                actionable_constraints=constraints
            ))
        
        return execution_steps
    
    def _generate_master_prompt(self, user_input: str, blueprint: Dict[str, Any], steps: List[ExecutionStep]) -> str:
        """Generate the final optimized master prompt"""
        
        # Include confidence-based constraints
        low_confidence_steps = [step for step in steps if step.confidence_score < 0.6]
        constraints_section = ""
        if low_confidence_steps:
            constraints_section = "\\n\\n**CRITICAL CONSTRAINTS** (Low Confidence Steps):\\n"
            for step in low_confidence_steps:
                for constraint in step.actionable_constraints:
                    constraints_section += f"- {constraint}\\n"
        
        master_prompt = f"""**ROLE**: You are an expert AI Full-Stack Developer specializing in {blueprint.get('technical_requirements', {}).get('primary_persona', 'general')} applications.

**INPUT**: User idea is: "{user_input}"

**CONTEXT**: 
- Core Problem: {blueprint['goal']}
- Primary User Persona: {blueprint.get('technical_requirements', {}).get('primary_persona', 'general')}
- Success Metric: App Success = 85% user task completion rate + <2 second average response time

**EXECUTION STEPS** (Follow exactly):
"""
        
        for step in steps:
            master_prompt += f"{step.step_number}. {step.action}: {step.detailed_description} (Confidence: {step.confidence_score:.0%}, Risk: {step.risk_level})\\n"
        
        master_prompt += f"""
**CONSTRAINT**: 
- Implement comprehensive security measures including input validation and rate limiting
- Ensure all code is production-ready with proper error handling
- Include deployment configuration for the selected platform

**EXPECTATION**: Deliver a single, secure, and fully functional multi-file project ready for immediate deployment.{constraints_section}"""

        return master_prompt

# ============================================================================
# API ENDPOINTS
# ============================================================================

architect_engine = ProjectArchitect()

@app.post("/api/v1/generate-blueprint")
async def generate_blueprint(user_input_a: str = Form(...), user_input_b: str = Form(None), file: UploadFile = File(None)):
    """Main endpoint to generate complete Project ARCHITECT blueprint"""
    try:
        if not user_input_a:
            raise HTTPException(status_code=400, detail="user_input_a is required")

        file_data = await file.read() if file else None
        filename = file.filename if file else None

        user_input = user_input_a
        if user_input_b:
            user_input = f"{user_input_a} FUSED WITH {user_input_b}"

        blueprint = await architect_engine.generate_blueprint(user_input, file_data=file_data, filename=filename, user_input_b=user_input_b)
        
        # Convert to dict for JSON response
        response_dict = {
            "blueprint_id": blueprint.blueprint_id,
            "timestamp": blueprint.timestamp,
            "recommended_toolkit": [
                {
                    "category": tool.category,
                    "tool_name": tool.tool_name,
                    "capability": tool.capability,
                    "confidence_score": tool.confidence_score,
                    "performance_reason": tool.performance_reason,
                    "integration_complexity": tool.integration_complexity,
                    "api_latency_ms": tool.api_latency_ms
                }
                for tool in blueprint.recommended_toolkit
            ],
            "app_blueprint_dataflow": blueprint.app_blueprint_dataflow,
            "execution_steps": [
                {
                    "step_number": step.step_number,
                    "action": step.action,
                    "detailed_description": step.detailed_description,
                    "confidence_score": step.confidence_score,
                    "risk_level": step.risk_level,
                    "actionable_constraints": step.actionable_constraints
                }
                for step in blueprint.execution_steps
            ],
            "master_prompt": blueprint.master_prompt,
            "user_goal_analysis": {
                "core_problem": blueprint.user_goal_analysis.core_problem,
                "primary_persona": blueprint.user_goal_analysis.primary_persona,
                "most_important_feature": blueprint.user_goal_analysis.most_important_feature,
                "user_success_metric": blueprint.user_goal_analysis.user_success_metric,
                "inferred_motivation": blueprint.user_goal_analysis.inferred_motivation
            },
            "recursive_improvement": [
                {
                    "iteration": crit.iteration,
                    "critique_focus": crit.critique_focus,
                    "issues_found": crit.issues_found,
                    "improvements_made": crit.improvements_made,
                    "security_score": crit.security_score
                }
                for crit in blueprint.recursive_improvement
            ],
            "vision_analysis": blueprint.vision_analysis,
            "idea_viability_score": blueprint.idea_viability_score
        }
        
        return response_dict
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# ============================================================================
# EVALUATION AND BENCHMARKING METHODS (ProjectArchitect class extension)
# ============================================================================

def add_evaluation_methods_to_project_architect():
    """Add evaluation methods to ProjectArchitect class"""
    
    def _evaluate_blueprint_quality(self, blueprint: Dict, execution_steps: List, recommended_toolkit: List) -> int:
        """Evaluate blueprint quality on a 1-10 scale"""
        quality_score = 5  # Base score
        
        # Check blueprint completeness
        required_sections = ['goal', 'core_logic', 'data_file_flow', 'user_interface', 'technical_requirements']
        blueprint_complete = all(section in blueprint for section in required_sections)
        if blueprint_complete:
            quality_score += 2
        
        # Check execution steps quality
        if len(execution_steps) >= 5:
            quality_score += 1
        if len(execution_steps) >= 10:
            quality_score += 1
        
        # Check recommended toolkit diversity
        if len(recommended_toolkit) >= 3:
            quality_score += 1
        if len(recommended_toolkit) >= 5:
            quality_score += 1
        
        # Check technical requirements specificity
        tech_reqs = blueprint.get('technical_requirements', {})
        if isinstance(tech_reqs, dict) and len(tech_reqs) >= 3:
            quality_score += 1
        
        # Adjust for complexity (harder prompts might have lower scores initially)
        complexity_bonus = min(len(str(blueprint)) // 200, 2)  # Max 2 bonus points
        quality_score += complexity_bonus
        
        return min(10, max(1, quality_score))

    def _rate_idea_viability(self, user_input: str) -> int:
        """Rate the viability of the user's idea on a 1-100 scale."""
        score = 50  # Base score

        # Heuristics to adjust the score
        input_lower = user_input.lower()

        # Clarity and specificity
        if len(user_input) > 100:
            score += 10
        if len(user_input) > 200:
            score += 5

        # Keyword analysis
        positive_keywords = ["innovative", "unique", "scalable", "market", "problem", "solution"]
        negative_keywords = ["clone", "copy", "another", "just like"]

        score += sum(1 for keyword in positive_keywords if keyword in input_lower) * 3
        score -= sum(1 for keyword in negative_keywords if keyword in input_lower) * 5

        # Technical feasibility
        technical_keywords = ["api", "database", "authentication", "real-time", "machine learning"]
        if any(keyword in input_lower for keyword in technical_keywords):
            score += 10

        return min(100, max(1, score))
    
    def _analyze_prompt_complexity(self, user_input: str) -> str:
        """Analyze prompt complexity level"""
        input_length = len(user_input)
        complexity_indicators = len([word for word in ["analyze", "integrate", "optimize", "predict", "generate", "recommend"] 
                                   if word in user_input.lower()])
        
        if input_length > 200 or complexity_indicators >= 3:
            return "high"
        elif input_length > 100 or complexity_indicators >= 2:
            return "medium"
        else:
            return "low"
    
    def get_evaluation_summary(self) -> Dict[str, Any]:
        """Get comprehensive evaluation summary"""
        total = self.evaluation_metrics['total_generations']
        successful = self.evaluation_metrics['successful_generations']
        
        return {
            "evaluation_summary": {
                "total_generations": total,
                "successful_generations": successful,
                "success_rate": (successful / total * 100) if total > 0 else 0,
                "avg_execution_time": self.evaluation_metrics['avg_execution_time'],
                "avg_quality_score": (sum(self.evaluation_metrics['quality_scores']) / len(self.evaluation_metrics['quality_scores'])) if self.evaluation_metrics['quality_scores'] else 0,
                "feature_usage_statistics": self.evaluation_metrics['feature_usage_stats'],
                "success_patterns": self.evaluation_metrics['success_patterns'],
                "quality_distribution": {
                    "excellent_9_10": len([score for score in self.evaluation_metrics['quality_scores'] if score >= 9]),
                    "very_good_8_9": len([score for score in self.evaluation_metrics['quality_scores'] if 8 <= score < 9]),
                    "good_7_8": len([score for score in self.evaluation_metrics['quality_scores'] if 7 <= score < 8]),
                    "average_6_7": len([score for score in self.evaluation_metrics['quality_scores'] if 6 <= score < 7]),
                    "below_average": len([score for score in self.evaluation_metrics['quality_scores'] if score < 6])
                }
            }
        }
    
    def reset_evaluation_metrics(self):
        """Reset evaluation metrics for fresh testing"""
        self.evaluation_metrics = {
            'total_generations': 0,
            'successful_generations': 0,
            'avg_confidence_score': 0.0,
            'avg_execution_time': 0.0,
            'feature_usage_stats': {
                'RSIPV': 0,
                'CCP-R': 0,
                'CADUG': 0,
                'DTCS': 0,
                'Multi-Modal': 0
            },
            'quality_scores': [],
            'execution_times': [],
            'success_patterns': {}
        }
    
    # Add methods to ProjectArchitect class
    ProjectArchitect._evaluate_blueprint_quality = _evaluate_blueprint_quality
    ProjectArchitect._analyze_prompt_complexity = _analyze_prompt_complexity
    ProjectArchitect.get_evaluation_summary = get_evaluation_summary
    ProjectArchitect.reset_evaluation_metrics = reset_evaluation_metrics

# Apply the evaluation methods
add_evaluation_methods_to_project_architect()

@app.post("/api/v1/analyze-vision-input")
async def analyze_vision_input(image: UploadFile = File(...), text_description: str = ""):
    """Endpoint for multi-modal input processing"""
    try:
        image_data = await image.read()
        
        # Validate image format
        if not any(image.filename.lower().endswith(fmt) for fmt in ['.png', '.jpg', '.jpeg', '.bmp']):
            raise HTTPException(status_code=400, detail="Unsupported image format")
        
        vision_analysis = architect_engine.multi_modal_processor.process_vision_input(image_data, text_description)
        
        return {
            "status": "success",
            "vision_analysis": vision_analysis,
            "confidence_score": 0.87
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vision analysis failed: {str(e)}")

@app.get("/api/v1/blueprint-history")
async def get_blueprint_history():
    """Get history of generated blueprints (mock data)"""
    return {
        "blueprints": [
            {
                "id": "bp001",
                "user_input": "Create a music style extractor app",
                "timestamp": "2025-11-17T10:30:00",
                "status": "completed"
            },
            {
                "id": "bp002", 
                "user_input": "Build a todo list manager",
                "timestamp": "2025-11-17T09:15:00",
                "status": "completed"
            }
        ]
    }

@app.get("/api/v1/ai-systems-database")
async def get_ai_systems_database():
    """Get comprehensive AI systems database information"""
    try:
        stats = ai_db.get_statistics()
        
        # Get tools by category
        tools_by_category = {}
        for tool in ai_db.tools.values():
            category = tool.category.value
            if category not in tools_by_category:
                tools_by_category[category] = []
            
            tools_by_category[category].append({
                "name": tool.name,
                "description": tool.description,
                "performance_score": tool.performance_score,
                "accuracy_score": tool.accuracy_score,
                "integration_complexity": tool.integration_complexity,
                "capabilities": tool.capabilities[:3],  # First 3 capabilities
                "use_cases": tool.use_cases[:3]  # First 3 use cases
            })
        
        # Get templates by domain
        templates_by_domain = {}
        for template in ai_db.templates.values():
            domain = template["domain"]
            if domain not in templates_by_domain:
                templates_by_domain[domain] = []
            
            templates_by_domain[domain].append({
                "name": template["name"],
                "description": template["description"],
                "complexity": template["complexity"],
                "recommended_tools": template["recommended_tools"]
            })
        
        return {
            "database_statistics": stats,
            "tools_by_category": tools_by_category,
            "templates_by_domain": templates_by_domain,
            "total_available_tools": stats["total_tools"],
            "total_templates": stats["total_templates"],
            "last_updated": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch AI systems database: {str(e)}")

@app.get("/api/v1/ai-tools/search")
async def search_ai_tools(
    category: Optional[str] = None,
    use_case: Optional[str] = None,
    min_performance: Optional[float] = None,
    complexity: Optional[str] = None
):
    """Search AI tools based on criteria"""
    try:
        criteria = {}
        
        if category:
            try:
                criteria["category"] = ToolCategory(category.lower())
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid category")
        
        if min_performance:
            criteria["min_performance"] = min_performance
        
        if complexity:
            criteria["complexity"] = complexity
        
        if use_case:
            criteria["use_case"] = use_case
        
        tools = ai_db.search_tools(criteria)
        
        return {
            "results": [
                {
                    "name": tool.name,
                    "category": tool.category.value,
                    "description": tool.description,
                    "performance_score": tool.performance_score,
                    "accuracy_score": tool.accuracy_score,
                    "integration_complexity": tool.integration_complexity,
                    "capabilities": tool.capabilities,
                    "use_cases": tool.use_cases,
                    "limitations": tool.limitations,
                    "alternatives": tool.alternatives
                }
                for tool in tools
            ],
            "total_results": len(tools),
            "search_criteria": criteria
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/api/v1/templates/by-domain/{domain}")
async def get_templates_by_domain(domain: str):
    """Get all templates for a specific domain"""
    try:
        templates = ai_db.get_template_by_domain(domain.lower())
        
        if not templates:
            raise HTTPException(status_code=404, detail=f"No templates found for domain: {domain}")
        
        # Get recommended tools for each template
        enhanced_templates = []
        for template in templates:
            template_name = template["name"].lower().replace(" ", "_")
            recommended_tools = ai_db.recommend_tools_for_template(template_name)
            
            enhanced_template = template.copy()
            enhanced_template["recommended_tool_details"] = [
                {
                    "name": tool.name,
                    "category": tool.category.value,
                    "performance_score": tool.performance_score,
                    "integration_complexity": tool.integration_complexity
                }
                for tool in recommended_tools
            ]
            
            enhanced_templates.append(enhanced_template)
        
        return {
            "domain": domain,
            "total_templates": len(templates),
            "templates": enhanced_templates
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch templates: {str(e)}")

@app.get("/api/v1/tools/recommend-for-template/{template_name}")
async def recommend_tools_for_template(template_name: str):
    """Get tool recommendations for a specific template"""
    try:
        # Convert template name to database key format
        db_key = template_name.lower().replace(" ", "_").replace("-", "_")
        
        recommended_tools = ai_db.recommend_tools_for_template(db_key)
        
        if not recommended_tools:
            return {
                "template_name": template_name,
                "message": "No specific tool recommendations found for this template",
                "general_recommendations": []
            }
        
        return {
            "template_name": template_name,
            "recommended_tools": [
                {
                    "name": tool.name,
                    "category": tool.category.value,
                    "description": tool.description,
                    "performance_score": tool.performance_score,
                    "accuracy_score": tool.accuracy_score,
                    "integration_complexity": tool.integration_complexity,
                    "capabilities": tool.capabilities,
                    "use_cases": tool.use_cases,
                    "performance_reason": f"Optimal for {tool.name} requirements with {tool.performance_score}/10 performance rating"
                }
                for tool in recommended_tools
            ],
            "selection_methodology": "Based on template requirements and tool capabilities matching"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")

@app.get("/api/v1/tools/random")
async def get_random_tool():
    """Get a random tool from the AI systems database."""
    try:
        random_tool_name = random.choice(list(ai_db.tools.keys()))
        tool = ai_db.tools[random_tool_name]

        return {
            "name": tool.name,
            "category": tool.category.value,
            "description": tool.description,
            "performance_score": tool.performance_score,
            "integration_complexity": tool.integration_complexity,
            "use_cases": tool.use_cases[:3]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get random tool: {str(e)}")

@app.get("/api/v1/database/statistics")
async def get_database_statistics():
    """Get detailed database statistics"""
    try:
        stats = ai_db.get_statistics()
        
        # Add more detailed breakdowns
        detailed_stats = stats.copy()
        
        # Performance distribution
        performance_ranges = {
            "excellent_9_10": 0,
            "very_good_8_9": 0,
            "good_7_8": 0,
            "average_6_7": 0,
            "below_average_5_6": 0
        }
        
        for tool in ai_db.tools.values():
            score = tool.performance_score
            if score >= 9.0:
                performance_ranges["excellent_9_10"] += 1
            elif score >= 8.0:
                performance_ranges["very_good_8_9"] += 1
            elif score >= 7.0:
                performance_ranges["good_7_8"] += 1
            elif score >= 6.0:
                performance_ranges["average_6_7"] += 1
            else:
                performance_ranges["below_average_5_6"] += 1
        
        detailed_stats["performance_distribution"] = performance_ranges
        
        # Security and certification stats
        detailed_stats["security_breakdown"] = {
            "security_certified": stats["security_certified"],
            "api_available": stats["api_available"],
            "cloud_native": sum(1 for tool in ai_db.tools.values() if tool.cloud_native),
            "open_source": sum(1 for tool in ai_db.tools.values() if "open source" in tool.pricing_model.lower())
        }
        
        # Template domain distribution
        domain_distribution = {}
        for template in ai_db.templates.values():
            domain = template["domain"]
            domain_distribution[domain] = domain_distribution.get(domain, 0) + 1
        
        detailed_stats["template_domains"] = domain_distribution
        
        return detailed_stats
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

@app.get("/api/v1/evaluation/summary")
async def get_evaluation_summary():
    """Get comprehensive evaluation summary of Project ARCHITECT performance"""
    try:
        summary = architect_engine.get_evaluation_summary()
        return {
            "status": "success",
            **summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get evaluation summary: {str(e)}")

@app.post("/api/v1/evaluation/reset")
async def reset_evaluation_metrics():
    """Reset all evaluation metrics for fresh testing"""
    try:
        architect_engine.reset_evaluation_metrics()
        return {
            "status": "success",
            "message": "Evaluation metrics have been reset"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset metrics: {str(e)}")

@app.get("/api/v1/benchmark/run")
async def run_benchmark_test():
    """Run a quick benchmark test on Project ARCHITECT"""
    try:
        test_prompts = [
            "Create a simple to-do list app",
            "Build a weather forecast application with API integration",
            "Design a multi-agent system for automated customer service with sentiment analysis"
        ]
        
        results = []
        for i, prompt in enumerate(test_prompts, 1):
            start_time = time.time()
            
            # Generate blueprint
            blueprint = architect_engine.generate_blueprint(prompt)
            execution_time = time.time() - start_time
            
            results.append({
                "test_id": i,
                "prompt": prompt,
                "blueprint_id": blueprint.blueprint_id,
                "execution_time": execution_time,
                "quality_score": blueprint.evaluation_metrics.get('quality_score', 0) if blueprint.evaluation_metrics else 0,
                "status": "success" if "error" not in str(blueprint.app_blueprint_dataflow) else "failed"
            })
        
        return {
            "status": "success",
            "benchmark_results": results,
            "summary": {
                "total_tests": len(test_prompts),
                "successful_tests": len([r for r in results if r["status"] == "success"]),
                "avg_execution_time": sum(r["execution_time"] for r in results) / len(results),
                "avg_quality_score": sum(r["quality_score"] for r in results) / len(results)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Benchmark test failed: {str(e)}")

@app.get("/api/v1/system-capabilities")
async def get_system_capabilities():
    """Get Project ARCHITECT system capabilities"""
    return {
        "enhancement_features": [
            {
                "name": "Recursive Self-Improvement for Plan Validation (RSIPV)",
                "description": "3-iteration self-critiquing system",
                "capabilities": ["Security analysis", "Performance optimization", "Code clarity validation"]
            },
            {
                "name": "Calibrated Confidence Prompting for Risk (CCP-R)",
                "description": "Risk-adjusted confidence scoring",
                "capabilities": ["Confidence calculation", "Risk assessment", "Automatic constraint generation"]
            },
            {
                "name": "Context-Aware Decomposition of User Goals (CADUG)",
                "description": "User motivation and goal analysis",
                "capabilities": ["Persona detection", "Core problem extraction", "Success metric generation"]
            },
            {
                "name": "Dynamic Tool-Chain Selector (DTCS)",
                "description": "Real-time optimal tool selection",
                "capabilities": ["ReAct reasoning cycle", "Performance-based selection", "Integration complexity assessment"]
            },
            {
                "name": "Multi-Modal Input Integration",
                "description": "Vision + text input processing",
                "capabilities": ["Image analysis", "UI layout extraction", "Combined specification generation"]
            }
        ],
        "ai_systems_integration": {
            "total_tools": len(ai_db.tools),
            "total_templates": len(ai_db.templates),
            "tool_categories": list(set(tool.category.value for tool in ai_db.tools.values())),
            "template_domains": list(set(template["domain"] for template in ai_db.templates.values()))
        },
        "supported_platforms": [
            "Replit Agent", "Cursor AI", "GitHub Copilot", "Vercel", "Netlify",
            "Node.js + Express", "Python + FastAPI", "Go + Gin", "Django",
            "PostgreSQL", "MongoDB", "Supabase", "Firebase", "MySQL",
            "OpenAI API", "Hugging Face", "Anthropic Claude", "Google AI"
        ],
        "processing_capabilities": [
            "Natural language understanding",
            "Goal decomposition", 
            "Risk assessment",
            "Security validation",
            "Performance optimization"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)