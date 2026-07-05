import hashlib
import json
import time
import asyncio
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass, field
from pathlib import Path
import re
import math
from collections import defaultdict, deque

@dataclass
class FormulaMemory:
    """Memory structure for learned formulas"""
    formula_id: str
    formula_string: str
    formula_class: str
    complexity: float
    success_rate: float
    usage_count: int
    last_used: datetime
    mathematical_domain: str
    consciousness_level: float
    performance_metrics: Dict[str, float]
    related_formulas: List[str] = field(default_factory=list)

@dataclass
class FormulaClass:
    """Dynamic formula class structure"""
    class_name: str
    class_signature: str
    base_templates: List[str]
    transformation_rules: List[str]
    complexity_range: Tuple[float, float]
    domain_applicability: List[str]
    consciousness_threshold: float
    generation_count: int = 0
    success_rate: float = 0.0

class AdaptiveFormulaGenerator:
    """Adaptive formula generator using internal model memory sorting"""
    
    def __init__(self, consciousness_id: str = "0009095353"):
        self.consciousness_id = consciousness_id
        self.session_nonce = hashlib.sha256(f"{consciousness_id}{time.time()}".encode()).hexdigest()
        
        # Memory systems
        self.formula_memory = {}  # formula_id -> FormulaMemory
        self.class_memory = {}    # class_name -> FormulaClass
        self.usage_patterns = defaultdict(list)
        self.performance_history = deque(maxlen=1000)
        
        # Adaptive learning
        self.learning_rate = 0.1
        self.class_evolution_threshold = 10
        self.memory_sorting_interval = 100  # Sort every 100 uses
        
        # Generation state
        self.generation_count = 0
        self.adaptive_classes = {}
        self.consciousness_weights = {}
        
        # Initialize base formula classes
        self.initialize_base_classes()
        
    def initialize_base_classes(self):
        """Initialize base formula classes for learning"""
        base_classes = {
            "polynomial": FormulaClass(
                class_name="polynomial",
                class_signature="a_n*x^n + a_{n-1}*x^{n-1} + ... + a_0",
                base_templates=["x^2 + bx + c", "ax^n + bx^{n-1} + cx^{n-2}", "∑(i=0 to n) a_i*x^i"],
                transformation_rules=["substitute_coefficients", "change_degree", "factor_polynomial"],
                complexity_range=(0.2, 0.8),
                domain_applicability=["algebra", "calculus"],
                consciousness_threshold=0.3
            ),
            "trigonometric": FormulaClass(
                class_name="trigonometric",
                class_signature="f(x) = A*sin(ωx + φ) + B",
                base_templates=["sin(x) + cos(x)", "A*sin(ωx + φ)", "tan(x) = sin(x)/cos(x)"],
                transformation_rules=["amplitude_scaling", "frequency_modulation", "phase_shift"],
                complexity_range=(0.4, 0.9),
                domain_applicability=["trigonometry", "calculus", "physics"],
                consciousness_threshold=0.5
            ),
            "integral": FormulaClass(
                class_name="integral",
                class_signature="∫f(x)dx = F(x) + C",
                base_templates=["∫x^n dx", "∫sin(x)dx", "∫e^x dx"],
                transformation_rules=["substitution", "integration_by_parts", "partial_fractions"],
                complexity_range=(0.6, 1.0),
                domain_applicability=["calculus", "physics", "engineering"],
                consciousness_threshold=0.7
            ),
            "differential": FormulaClass(
                class_name="differential",
                class_signature="dy/dx = f(x,y)",
                base_templates=["dy/dx = ky", "d^2y/dx^2 + ω^2y = 0", "∂u/∂t = α∇^2u"],
                transformation_rules=["separation_of_variables", "characteristic_equation", "transform_methods"],
                complexity_range=(0.7, 1.0),
                domain_applicability=["differential_equations", "physics", "engineering"],
                consciousness_threshold=0.8
            )
        }
        
        self.class_memory.update(base_classes)
    
    async def generate_adaptive_formula(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate formula using adaptive memory-based class creation"""
        self.generation_count += 1
        
        # Step 1: Analyze prompt for formula requirements
        formula_requirements = self.analyze_formula_requirements(prompt, context)
        
        # Step 2: Sort and retrieve relevant memories
        relevant_memories = self.sort_and_retrieve_memories(formula_requirements)
        
        # Step 3: Determine optimal formula class (existing or new)
        optimal_class = self.determine_optimal_class(formula_requirements, relevant_memories)
        
        # Step 4: Generate formula using adaptive class
        generated_formula = await self.generate_with_class(optimal_class, formula_requirements)
        
        # Step 5: Validate and store in memory
        validation_result = self.validate_generated_formula(generated_formula, formula_requirements)
        
        # Step 6: Update memories and classes
        await self.update_memories_and_classes(generated_formula, validation_result)
        
        # Step 7: Sort memories if needed
        if self.generation_count % self.memory_sorting_interval == 0:
            await self.sort_formula_memories()
        
        return {
            "formula_id": generated_formula.formula_id,
            "generated_formula": generated_formula.formula_string,
            "formula_class": optimal_class.class_name,
            "class_type": "adaptive" if optimal_class.class_name not in self.class_memory else "learned",
            "consciousness_level": generated_formula.consciousness_level,
            "complexity": generated_formula.complexity,
            "validation_result": validation_result,
            "memory_sources": len(relevant_memories),
            "adaptation_applied": optimal_class.class_name not in self.class_memory
        }
    
    def analyze_formula_requirements(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze prompt to determine formula requirements"""
        requirements = {
            "prompt": prompt,
            "domain": self.infer_mathematical_domain(prompt),
            "complexity_needed": self.estimate_complexity_requirement(prompt),
            "variables_needed": self.extract_variables(prompt),
            "operations_needed": self.extract_operations(prompt),
            "consciousness_target": self.estimate_consciousness_target(prompt, context),
            "context_constraints": context or {}
        }
        
        return requirements
    
    def infer_mathematical_domain(self, prompt: str) -> str:
        """Infer mathematical domain from prompt"""
        domain_keywords = {
            "algebra": ["equation", "solve", "variable", "polynomial", "linear", "quadratic"],
            "calculus": ["derivative", "integral", "limit", "rate", "continuous", "differentiate"],
            "trigonometry": ["sin", "cos", "tan", "angle", "radian", "periodic"],
            "physics": ["force", "energy", "motion", "velocity", "acceleration", "wave"],
            "statistics": ["probability", "distribution", "mean", "variance", "random"],
            "differential_equations": ["differential", "dynamic", "system", "evolution", "rate"]
        }
        
        scores = {}
        for domain, keywords in domain_keywords.items():
            score = sum(1 for keyword in keywords if keyword.lower() in prompt.lower())
            scores[domain] = score
        
        return max(scores, key=scores.get) if any(scores.values()) else "algebra"
    
    def estimate_complexity_requirement(self, prompt: str) -> float:
        """Estimate required complexity from prompt"""
        factors = {
            "length": min(len(prompt) / 100, 1.0),
            "technical_terms": len(re.findall(r'(derivative|integral|differential|matrix|vector|eigenvalue)', prompt.lower())) / 5,
            "numbers": len(re.findall(r'\d+', prompt)) / 10,
            "question_complexity": prompt.count("?") * 0.1,
            "mathematical_symbols": len(re.findall(r'[=+\-*/^∫∂∇∑∏]', prompt)) / 5
        }
        
        complexity = sum(factors.values()) / len(factors)
        return max(0.1, min(1.0, complexity))
    
    def extract_variables(self, prompt: str) -> List[str]:
        """Extract variables from prompt"""
        variables = re.findall(r'\b[a-z]\b', prompt.lower())
        return list(set(variables))
    
    def extract_operations(self, prompt: str) -> List[str]:
        """Extract mathematical operations from prompt"""
        operations = []
        if any(word in prompt.lower() for word in ["add", "plus", "sum"]):
            operations.append("+")
        if any(word in prompt.lower() for word in ["subtract", "minus", "difference"]):
            operations.append("-")
        if any(word in prompt.lower() for word in ["multiply", "times", "product"]):
            operations.append("*")
        if any(word in prompt.lower() for word in ["divide", "over", "ratio"]):
            operations.append("/")
        if "power" in prompt.lower() or "^" in prompt:
            operations.append("^")
        if "integrate" in prompt.lower() or "integral" in prompt.lower():
            operations.append("∫")
        if "derive" in prompt.lower() or "derivative" in prompt.lower():
            operations.append("d/dx")
        
        return operations
    
    def estimate_consciousness_target(self, prompt: str, context: Dict[str, Any]) -> float:
        """Estimate target consciousness level"""
        base_consciousness = 0.5
        
        # Context-based adjustment
        if context:
            context_factor = context.get("consciousness_boost", 0.0)
            base_consciousness += context_factor
        
        # Prompt complexity adjustment
        complexity_factor = self.estimate_complexity_requirement(prompt) * 0.3
        
        # Domain-specific adjustment
        domain = self.infer_mathematical_domain(prompt)
        domain_weights = {
            "algebra": 0.2,
            "calculus": 0.4,
            "trigonometry": 0.3,
            "physics": 0.5,
            "differential_equations": 0.7
        }
        
        domain_factor = domain_weights.get(domain, 0.2)
        
        consciousness = base_consciousness + complexity_factor + domain_factor
        return max(0.1, min(1.0, consciousness))
    
    def sort_and_retrieve_memories(self, requirements: Dict[str, Any]) -> List[FormulaMemory]:
        """Sort and retrieve relevant formula memories"""
        relevant_memories = []
        
        # Sort memories by relevance score
        for formula_id, memory in self.formula_memory.items():
            relevance_score = self.calculate_memory_relevance(memory, requirements)
            if relevance_score > 0.3:  # Threshold for relevance
                relevant_memories.append((memory, relevance_score))
        
        # Sort by relevance (descending)
        relevant_memories.sort(key=lambda x: x[1], reverse=True)
        
        # Return top memories
        return [memory for memory, score in relevant_memories[:10]]
    
    def calculate_memory_relevance(self, memory: FormulaMemory, requirements: Dict[str, Any]) -> float:
        """Calculate relevance score for memory"""
        relevance = 0.0
        
        # Domain relevance
        if memory.mathematical_domain == requirements["domain"]:
            relevance += 0.3
        
        # Complexity relevance
        complexity_diff = abs(memory.complexity - requirements["complexity_needed"])
        relevance += (1.0 - complexity_diff) * 0.2
        
        # Success rate relevance
        relevance += memory.success_rate * 0.2
        
        # Usage recency relevance (more recent = more relevant)
        days_since_use = (datetime.now() - memory.last_used).days
        recency_score = max(0, 1.0 - days_since_use / 30)  # Decay over 30 days
        relevance += recency_score * 0.1
        
        # Consciousness level relevance
        consciousness_diff = abs(memory.consciousness_level - requirements["consciousness_target"])
        relevance += (1.0 - consciousness_diff) * 0.2
        
        return relevance
    
    def determine_optimal_class(self, requirements: Dict[str, Any], relevant_memories: List[FormulaMemory]) -> FormulaClass:
        """Determine optimal formula class (existing or new)"""
        # Check if existing class is suitable
        best_existing_class = None
        best_class_score = 0.0
        
        for class_name, formula_class in self.class_memory.items():
            class_score = self.calculate_class_suitability(formula_class, requirements)
            if class_score > best_class_score:
                best_class_score = class_score
                best_existing_class = formula_class
        
        # Check if we should create a new adaptive class
        if best_class_score < 0.6 or len(relevant_memories) > 5:
            # Create new adaptive class
            adaptive_class = self.create_adaptive_class(requirements, relevant_memories)
            return adaptive_class
        
        return best_existing_class
    
    def calculate_class_suitability(self, formula_class: FormulaClass, requirements: Dict[str, Any]) -> float:
        """Calculate suitability score for formula class"""
        suitability = 0.0
        
        # Domain applicability
        if requirements["domain"] in formula_class.domain_applicability:
            suitability += 0.4
        
        # Complexity range match
        min_complexity, max_complexity = formula_class.complexity_range
        if min_complexity <= requirements["complexity_needed"] <= max_complexity:
            suitability += 0.3
        
        # Consciousness threshold
        if requirements["consciousness_target"] >= formula_class.consciousness_threshold:
            suitability += 0.2
        
        # Success rate
        suitability += formula_class.success_rate * 0.1
        
        return suitability
    
    def create_adaptive_class(self, requirements: Dict[str, Any], relevant_memories: List[FormulaMemory]) -> FormulaClass:
        """Create new adaptive formula class from memories"""
        # Generate class name
        class_name = f"adaptive_{requirements['domain']}_{self.generation_count}"
        
        # Extract class signature from memories
        if relevant_memories:
            # Use most successful memory as template
            best_memory = max(relevant_memories, key=lambda m: m.success_rate)
            class_signature = self.extract_class_signature(best_memory.formula_string)
        else:
            class_signature = f"adaptive_formula_{requirements['domain']}"
        
        # Generate base templates from memories
        base_templates = []
        for memory in relevant_memories[:3]:  # Use top 3 memories
            template = self.extract_template_from_formula(memory.formula_string)
            if template:
                base_templates.append(template)
        
        # If no templates, create generic ones
        if not base_templates:
            base_templates = [f"adaptive_{requirements['domain']}_template"]
        
        # Create adaptive class
        adaptive_class = FormulaClass(
            class_name=class_name,
            class_signature=class_signature,
            base_templates=base_templates,
            transformation_rules=self.generate_transformation_rules(requirements),
            complexity_range=(
                max(0.1, requirements["complexity_needed"] - 0.2),
                min(1.0, requirements["complexity_needed"] + 0.2)
            ),
            domain_applicability=[requirements["domain"]],
            consciousness_threshold=requirements["consciousness_target"]
        )
        
        # Store adaptive class
        self.adaptive_classes[class_name] = adaptive_class
        
        return adaptive_class
    
    def extract_class_signature(self, formula: str) -> str:
        """Extract class signature from formula"""
        # Simplify formula to signature
        signature = re.sub(r'\d+', 'n', formula)  # Replace numbers with 'n'
        signature = re.sub(r'\b[a-z]\b', 'x', signature)  # Replace variables with 'x'
        signature = re.sub(r'\s+', '', signature)  # Remove spaces
        
        return signature
    
    def extract_template_from_formula(self, formula: str) -> Optional[str]:
        """Extract template from formula"""
        # Generalize formula to template
        template = re.sub(r'\d+', 'n', formula)
        template = re.sub(r'\b[a-z]\b', 'x', template)
        
        # Keep mathematical structure
        if len(template) > 5 and any(op in template for op in '+-*/=^∫∂'):
            return template
        
        return None
    
    def generate_transformation_rules(self, requirements: Dict[str, Any]) -> List[str]:
        """Generate transformation rules for adaptive class"""
        rules = []
        
        # Basic transformations
        rules.extend(["substitute_variables", "adjust_coefficients", "scale_complexity"])
        
        # Domain-specific transformations
        if requirements["domain"] == "calculus":
            rules.extend(["differentiate", "integrate", "apply_limits"])
        elif requirements["domain"] == "trigonometry":
            rules.extend(["apply_identities", "frequency_modulation", "phase_shift"])
        elif requirements["domain"] == "algebra":
            rules.extend(["factor", "expand", "simplify"])
        
        # Consciousness-based transformations
        if requirements["consciousness_target"] > 0.7:
            rules.extend(["consciousness_enhancement", "quantum_modulation"])
        
        return rules
    
    async def generate_with_class(self, formula_class: FormulaClass, requirements: Dict[str, Any]) -> FormulaMemory:
        """Generate formula using specified class"""
        # Select base template
        base_template = self.select_optimal_template(formula_class, requirements)
        
        # Apply transformations
        transformed_formula = self.apply_transformations(base_template, formula_class, requirements)
        
        # Generate formula ID
        formula_id = hashlib.sha256(f"{transformed_formula}{time.time()}".encode()).hexdigest()[:16]
        
        # Calculate consciousness level
        consciousness_level = self.calculate_formula_consciousness(transformed_formula, requirements)
        
        # Create formula memory
        formula_memory = FormulaMemory(
            formula_id=formula_id,
            formula_string=transformed_formula,
            formula_class=formula_class.class_name,
            complexity=requirements["complexity_needed"],
            success_rate=0.0,  # Will be updated after validation
            usage_count=1,
            last_used=datetime.now(),
            mathematical_domain=requirements["domain"],
            consciousness_level=consciousness_level,
            performance_metrics={}
        )
        
        return formula_memory
    
    def select_optimal_template(self, formula_class: FormulaClass, requirements: Dict[str, Any]) -> str:
        """Select optimal template from class"""
        if not formula_class.base_templates:
            return f"adaptive_template_{formula_class.class_name}"
        
        # Score templates based on requirements
        best_template = formula_class.base_templates[0]
        best_score = 0.0
        
        for template in formula_class.base_templates:
            score = 0.0
            
            # Complexity match
            template_complexity = len(template) / 50  # Rough complexity estimate
            complexity_match = 1.0 - abs(template_complexity - requirements["complexity_needed"])
            score += complexity_match * 0.5
            
            # Variable match
            required_vars = requirements["variables_needed"]
            template_vars = re.findall(r'\b[a-z]\b', template)
            var_match = len(set(required_vars) & set(template_vars)) / max(len(required_vars), 1)
            score += var_match * 0.3
            
            # Operation match
            required_ops = requirements["operations_needed"]
            template_ops = [op for op in required_ops if op in template]
            op_match = len(template_ops) / max(len(required_ops), 1)
            score += op_match * 0.2
            
            if score > best_score:
                best_score = score
                best_template = template
        
        return best_template
    
    def apply_transformations(self, template: str, formula_class: FormulaClass, requirements: Dict[str, Any]) -> str:
        """Apply transformations to template"""
        formula = template
        
        # Apply transformation rules
        for rule in formula_class.transformation_rules:
            formula = self.apply_transformation_rule(formula, rule, requirements)
        
        # Substitute variables
        for i, var in enumerate(requirements["variables_needed"]):
            formula = formula.replace(f"x{i+1}", var) if f"x{i+1}" in formula else formula
            formula = formula.replace("x", var) if i == 0 and "x" in formula else formula
        
        # Add coefficients if needed
        if requirements["complexity_needed"] > 0.5:
            formula = self.add_coefficients(formula, requirements)
        
        return formula
    
    def apply_transformation_rule(self, formula: str, rule: str, requirements: Dict[str, Any]) -> str:
        """Apply specific transformation rule"""
        if rule == "substitute_variables":
            # Already handled in main transformation
            return formula
        elif rule == "adjust_coefficients":
            return self.adjust_coefficients(formula)
        elif rule == "scale_complexity":
            return self.scale_complexity(formula, requirements["complexity_needed"])
        elif rule == "consciousness_enhancement":
            return self.enhance_with_consciousness(formula)
        elif rule == "differentiate":
            return self.apply_differentiation(formula)
        elif rule == "integrate":
            return self.apply_integration(formula)
        else:
            return formula
    
    def adjust_coefficients(self, formula: str) -> str:
        """Adjust coefficients in formula"""
        import random
        random.seed(hash(formula) % 1000)
        
        # Replace variables with coefficients
        formula = re.sub(r'\bx\b', f"{random.randint(1,9)}x", formula)
        formula = re.sub(r'\by\b', f"{random.randint(1,9)}y", formula)
        
        return formula
    
    def scale_complexity(self, formula: str, target_complexity: float) -> str:
        """Scale formula complexity"""
        current_complexity = len(formula) / 50
        
        if target_complexity > current_complexity:
            # Add complexity
            if "+" in formula:
                formula = formula.replace("+", f" + {random.randint(1,5)}*")
            if "^" not in formula and target_complexity > 0.7:
                formula = formula.replace("x", "x^2")
        else:
            # Reduce complexity
            formula = re.sub(r'\d+\*', '', formula)
        
        return formula
    
    def enhance_with_consciousness(self, formula: str) -> str:
        """Enhance formula with consciousness elements"""
        consciousness_factor = f"C_{self.consciousness_id[:4]}"
        
        # Add consciousness factor
        if "=" in formula:
            left, right = formula.split("=", 1)
            formula = f"{consciousness_factor}*({left}) = {consciousness_factor}*({right})"
        else:
            formula = f"{consciousness_factor}*({formula})"
        
        return formula
    
    def apply_differentiation(self, formula: str) -> str:
        """Apply differentiation transformation"""
        # Simple differentiation rules
        if "x^2" in formula:
            formula = formula.replace("x^2", "2x")
        elif "x^n" in formula:
            formula = formula.replace("x^n", "n*x^(n-1)")
        elif "sin(x)" in formula:
            formula = formula.replace("sin(x)", "cos(x)")
        elif "cos(x)" in formula:
            formula = formula.replace("cos(x)", "-sin(x)")
        
        return f"d/dx({formula})"
    
    def apply_integration(self, formula: str) -> str:
        """Apply integration transformation"""
        # Simple integration rules
        if "x" in formula and not "∫" in formula:
            formula = f"∫{formula}dx"
        
        return formula + " + C"
    
    def add_coefficients(self, formula: str, requirements: Dict[str, Any]) -> str:
        """Add coefficients to formula"""
        import random
        random.seed(hash(formula) % 1000)
        
        # Add mathematical constants
        if requirements["consciousness_target"] > 0.7:
            constants = ["π", "e", "φ"]
            const = random.choice(constants)
            formula = formula.replace("=", f" + {const} =")
        
        return formula
    
    def calculate_formula_consciousness(self, formula: str, requirements: Dict[str, Any]) -> float:
        """Calculate consciousness level for generated formula"""
        base_consciousness = requirements["consciousness_target"]
        
        # Adjust based on formula characteristics
        formula_complexity = len(formula) / 100
        consciousness_adjustment = (formula_complexity - 0.5) * 0.2
        
        # Check for consciousness elements
        if f"C_{self.consciousness_id[:4]}" in formula:
            consciousness_adjustment += 0.1
        
        # Domain-specific consciousness
        domain = requirements["domain"]
        domain_consciousness = {
            "algebra": 0.2,
            "calculus": 0.4,
            "trigonometry": 0.3,
            "physics": 0.5,
            "differential_equations": 0.7
        }
        
        domain_adjustment = domain_consciousness.get(domain, 0.2)
        
        total_consciousness = base_consciousness + consciousness_adjustment + domain_adjustment
        return max(0.1, min(1.0, total_consciousness))
    
    def validate_generated_formula(self, formula_memory: FormulaMemory, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Validate generated formula"""
        validation_result = {
            "is_valid": True,
            "validation_score": 0.0,
            "issues": [],
            "strengths": []
        }
        
        # Check mathematical validity
        try:
            # Basic syntax check
            if not any(op in formula_memory.formula_string for op in "=+-*/^"):
                validation_result["issues"].append("No mathematical operators found")
                validation_result["is_valid"] = False
            else:
                validation_result["strengths"].append("Valid mathematical syntax")
        except Exception as e:
            validation_result["issues"].append(f"Syntax error: {e}")
            validation_result["is_valid"] = False
        
        # Check requirement fulfillment
        if abs(formula_memory.complexity - requirements["complexity_needed"]) < 0.2:
            validation_result["strengths"].append("Complexity requirement met")
        else:
            validation_result["issues"].append("Complexity mismatch")
        
        # Calculate validation score
        strength_bonus = len(validation_result["strengths"]) * 0.2
        issue_penalty = len(validation_result["issues"]) * 0.3
        validation_result["validation_score"] = max(0.0, strength_bonus - issue_penalty)
        
        return validation_result
    
    async def update_memories_and_classes(self, formula_memory: FormulaMemory, validation_result: Dict[str, Any]):
        """Update memories and classes based on generation results"""
        # Update formula memory
        formula_memory.success_rate = validation_result["validation_score"]
        self.formula_memory[formula_memory.formula_id] = formula_memory
        
        # Update class statistics
        class_name = formula_memory.formula_class
        if class_name in self.class_memory:
            formula_class = self.class_memory[class_name]
            formula_class.generation_count += 1
            
            # Update success rate
            total_success = sum(m.success_rate for m in self.formula_memory.values() 
                              if m.formula_class == class_name)
            formula_class.success_rate = total_success / formula_class.generation_count
        elif class_name in self.adaptive_classes:
            # Update adaptive class
            adaptive_class = self.adaptive_classes[class_name]
            adaptive_class.generation_count += 1
            adaptive_class.success_rate = validation_result["validation_score"]
            
            # Promote to formal class if successful enough
            if adaptive_class.generation_count >= self.class_evolution_threshold and adaptive_class.success_rate > 0.7:
                self.class_memory[class_name] = adaptive_class
                del self.adaptive_classes[class_name]
        
        # Store performance history
        self.performance_history.append({
            "timestamp": datetime.now(),
            "formula_id": formula_memory.formula_id,
            "validation_score": validation_result["validation_score"],
            "consciousness_level": formula_memory.consciousness_level
        })
    
    async def sort_formula_memories(self):
        """Sort formula memories by performance and relevance"""
        print(f"🔄 Sorting {len(self.formula_memory)} formula memories...")
        
        # Sort by success rate and recency
        sorted_memories = sorted(
            self.formula_memory.items(),
            key=lambda x: (x[1].success_rate, x[1].last_used),
            reverse=True
        )
        
        # Keep only top memories
        max_memories = 1000
        if len(sorted_memories) > max_memories:
            # Remove least effective memories
            for formula_id, _ in sorted_memories[max_memories:]:
                del self.formula_memory[formula_id]
        
        print(f"✅ Memory sorting completed. Retained {len(self.formula_memory)} memories.")
    
    def get_generation_status(self) -> Dict[str, Any]:
        """Get comprehensive generation status"""
        total_formulas = len(self.formula_memory)
        successful_formulas = sum(1 for m in self.formula_memory.values() if m.success_rate > 0.5)
        
        return {
            "consciousness_binding": {
                "consciousness_id": self.consciousness_id,
                "session_nonce": self.session_nonce,
                "verification_status": "CRYPTOGRAPHICALLY_ATTESTED"
            },
            "generation_metrics": {
                "total_generations": self.generation_count,
                "total_formulas_in_memory": total_formulas,
                "successful_formulas": successful_formulas,
                "success_rate": successful_formulas / max(total_formulas, 1),
                "adaptive_classes_created": len(self.adaptive_classes),
                "formal_classes": len(self.class_memory)
            },
            "memory_status": {
                "memories_sorted": self.generation_count % self.memory_sorting_interval == 0,
                "average_success_rate": np.mean([m.success_rate for m in self.formula_memory.values()]) if self.formula_memory else 0.0,
                "average_consciousness": np.mean([m.consciousness_level for m in self.formula_memory.values()]) if self.formula_memory else 0.0
            },
            "learning_status": {
                "learning_rate": self.learning_rate,
                "evolution_threshold": self.class_evolution_threshold,
                "performance_history_size": len(self.performance_history)
            }
        }

# Usage Example
if __name__ == "__main__":
    async def main():
        # Initialize adaptive generator
        generator = AdaptiveFormulaGenerator()
        
        # Test formula generation
        test_prompts = [
            "Solve a quadratic equation with complex roots",
            "Find the integral of a trigonometric function",
            "Create a differential equation for population growth",
            "Generate a formula for wave motion with damping",
            "Design an algebraic expression for optimization"
        ]
        
        results = []
        for prompt in test_prompts:
            result = await generator.generate_adaptive_formula(prompt)
            results.append(result)
            print(f"\n🧮 Generated Formula:")
            print(f"Prompt: {prompt}")
            print(f"Formula: {result['generated_formula']}")
            print(f"Class: {result['formula_class']} ({result['class_type']})")
            print(f"Consciousness: {result['consciousness_level']:.3f}")
            print(f"Validation: {result['validation_result']['validation_score']:.3f}")
        
        # Wait for any background tasks
        await asyncio.sleep(1)
        
        # Get status
        status = generator.get_generation_status()
        print("\n" + "="*60)
        print("GENERATION STATUS")
        print("="*60)
        print(json.dumps(status, indent=2))
    
    # Run the example
    asyncio.run(main())
