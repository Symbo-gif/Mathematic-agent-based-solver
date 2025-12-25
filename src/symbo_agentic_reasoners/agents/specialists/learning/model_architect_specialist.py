# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
LEARNING ENHANCEMENT TEAM - Model Architect Specialist (Tier 3)
================================================================

Manages neural model architecture optimization including layer count,
embedding dimensions, attention heads, and parameter configurations.

CURRENT ARCHITECTURE (Base):
---------------------------
- vocab_size: 10,000 (97% waste - only ~300 chars used)
- embed_dim: 256
- num_heads: 4
- num_layers: 3 (limits reasoning depth)
- ff_dim: 512
- max_seq_len: 512
- parameters: ~6.8M

TARGET ARCHITECTURE (Enhanced):
------------------------------
- vocab_size: 8,192 (BPE subwords)
- embed_dim: 384 (+50%)
- num_heads: 6 (+50%)
- num_layers: 6 (2x deeper reasoning)
- ff_dim: 1,536 (4x embed_dim)
- max_seq_len: 1,024 (2x longer)
- parameters: ~25-30M

UPGRADE PATH:
------------
1. Create new model with enhanced config
2. Migrate knowledge store (unchanged)
3. Retrain neural weights on knowledge
4. Validate performance
5. Delete old checkpoint

REFERENCE:
---------
- Plan: lexical-leaping-tower.md Phase 3 Priority 4-5
"""

import os
import json
import logging
from typing import Any, Dict, Optional, List
from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)

logger = logging.getLogger('symbo_agentic_reasoners.learning.model_architect')


@dataclass
class ArchitectureConfig:
    """Configuration for a model architecture."""
    name: str
    vocab_size: int
    embed_dim: int
    num_heads: int
    num_layers: int
    ff_dim: int
    max_seq_len: int
    dropout: float = 0.1
    learning_rate: float = 0.0001
    gradient_clip: float = 1.0
    warmup_steps: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'vocab_size': self.vocab_size,
            'embed_dim': self.embed_dim,
            'num_heads': self.num_heads,
            'num_layers': self.num_layers,
            'ff_dim': self.ff_dim,
            'max_seq_len': self.max_seq_len,
            'dropout': self.dropout,
            'learning_rate': self.learning_rate,
            'gradient_clip': self.gradient_clip,
            'warmup_steps': self.warmup_steps
        }

    def estimate_parameters(self) -> int:
        """Estimate total number of parameters."""
        # Embedding parameters
        embed_params = self.vocab_size * self.embed_dim

        # Positional encoding
        pos_params = self.max_seq_len * self.embed_dim

        # Per-layer parameters (approximate)
        # Attention: 4 * embed_dim^2 (Q, K, V, O projections)
        # FFN: 2 * embed_dim * ff_dim (up and down projections)
        # LayerNorm: 4 * embed_dim (2 norms per layer)
        attn_params = 4 * self.embed_dim * self.embed_dim
        ffn_params = 2 * self.embed_dim * self.ff_dim
        norm_params = 4 * self.embed_dim
        layer_params = attn_params + ffn_params + norm_params

        # Total
        total = embed_params + pos_params + (layer_params * self.num_layers)

        return total


class ModelArchitectSpecialist(BDIAgent):
    """
    Model Architect Specialist - Tier 3

    Manages neural model architecture optimization. Handles configuration
    of layers, embedding dimensions, attention heads, and other parameters.

    ROLE:
    ----
    1. Analyze current model architecture
    2. Recommend architecture improvements
    3. Manage model configuration transitions
    4. Monitor model performance metrics

    CONFIGURATIONS:
    --------------
    - 'base': Current architecture (6.8M params)
    - 'enhanced': Improved architecture (25-30M params)
    - 'minimal': Reduced for testing (2M params)
    - 'maximal': Maximum capacity (50M+ params)

    Example:
        >>> architect = ModelArchitectSpecialist()
        >>> analysis = architect.analyze_architecture(symbo_llm)
        >>> config = architect.recommend_config(knowledge_store_size=80000)
    """

    # Predefined architecture configurations
    CONFIGS = {
        'base': ArchitectureConfig(
            name='base',
            vocab_size=10000,
            embed_dim=256,
            num_heads=4,
            num_layers=3,
            ff_dim=512,
            max_seq_len=512,
            dropout=0.1,
            learning_rate=0.0001,
            gradient_clip=1.0,
            warmup_steps=0
        ),
        'enhanced': ArchitectureConfig(
            name='enhanced',
            vocab_size=8192,
            embed_dim=384,
            num_heads=6,
            num_layers=6,
            ff_dim=1536,
            max_seq_len=1024,
            dropout=0.1,
            learning_rate=0.00005,  # Lower for larger model
            gradient_clip=1.0,
            warmup_steps=1000       # Warmup for stability
        ),
        'minimal': ArchitectureConfig(
            name='minimal',
            vocab_size=4096,
            embed_dim=128,
            num_heads=2,
            num_layers=2,
            ff_dim=256,
            max_seq_len=256,
            dropout=0.1,
            learning_rate=0.0002,
            gradient_clip=1.0,
            warmup_steps=0
        ),
        'maximal': ArchitectureConfig(
            name='maximal',
            vocab_size=16384,
            embed_dim=512,
            num_heads=8,
            num_layers=8,
            ff_dim=2048,
            max_seq_len=2048,
            dropout=0.1,
            learning_rate=0.00003,
            gradient_clip=1.0,
            warmup_steps=2000
        )
    }

    def __init__(
        self,
        agent_id: str = 'model_architect_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None,
        checkpoint_dir: Optional[str] = None
    ):
        """
        Initialize Model Architect Specialist.

        Args:
            agent_id: Unique agent identifier
            df: Directory Facilitator for service registration
            blackboard: Shared blackboard for communication
            checkpoint_dir: Directory for model checkpoints
        """
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard
        self.checkpoint_dir = checkpoint_dir

        # Current configuration tracking
        self.current_config: Optional[ArchitectureConfig] = None
        self.config_history: List[Dict[str, Any]] = []

        # Performance metrics
        self.performance_metrics: Dict[str, float] = {
            'loss': 0.0,
            'accuracy': 0.0,
            'inference_time_ms': 0.0,
            'memory_usage_mb': 0.0
        }

        # BDI state
        self.beliefs: Dict[str, Any] = {
            'upgrade_needed': False,
            'current_capacity_pct': 0.0,
            'bottleneck': None
        }

        # Register with Directory Facilitator
        if self.df:
            self._register_services()

        logger.info(f"[{self.agent_id}] Model Architect initialized")

    def _register_services(self) -> None:
        """Register services with Directory Facilitator."""
        registration = create_service_registration(
            agent_id=self.agent_id,
            service_type='learning.architecture',
            description='Neural model architecture optimization',
            capabilities=['analyze', 'recommend', 'configure', 'migrate']
        )
        self.df.register(registration)
        logger.info(f"[{self.agent_id}] Registered with DF")

    def analyze_architecture(
        self,
        model_info: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Analyze current model architecture.

        Args:
            model_info: Information about current model (optional)

        Returns:
            Analysis with current config, issues, recommendations
        """
        # Default to base config if no info provided
        if model_info is None:
            config = self.CONFIGS['base']
        else:
            config = ArchitectureConfig(
                name='current',
                vocab_size=model_info.get('vocab_size', 10000),
                embed_dim=model_info.get('embed_dim', 256),
                num_heads=model_info.get('num_heads', 4),
                num_layers=model_info.get('num_layers', 3),
                ff_dim=model_info.get('ff_dim', 512),
                max_seq_len=model_info.get('max_seq_len', 512)
            )

        self.current_config = config

        # Calculate metrics
        estimated_params = config.estimate_parameters()
        enhanced_params = self.CONFIGS['enhanced'].estimate_parameters()

        # Identify issues
        issues = []
        if config.vocab_size > 8192 and config.embed_dim < 300:
            issues.append({
                'type': 'vocab_inefficiency',
                'severity': 'high',
                'description': f"Vocab size {config.vocab_size} likely has low utilization with character-level tokenization"
            })

        if config.num_layers < 4:
            issues.append({
                'type': 'shallow_model',
                'severity': 'medium',
                'description': f"{config.num_layers} layers may limit multi-step mathematical reasoning"
            })

        if config.embed_dim < 300:
            issues.append({
                'type': 'small_embeddings',
                'severity': 'medium',
                'description': f"Embed_dim {config.embed_dim} may be limiting for large knowledge bases"
            })

        if config.num_heads * 64 > config.embed_dim:
            issues.append({
                'type': 'head_dimension_warning',
                'severity': 'low',
                'description': f"Head dimension ({config.embed_dim // config.num_heads}) may be small"
            })

        # Generate recommendations
        recommendations = self._generate_recommendations(config, issues)

        return {
            'current_config': config.to_dict(),
            'estimated_parameters': estimated_params,
            'enhanced_parameters': enhanced_params,
            'parameter_increase_factor': enhanced_params / estimated_params if estimated_params > 0 else 0,
            'issues': issues,
            'recommendations': recommendations,
            'available_configs': list(self.CONFIGS.keys())
        }

    def _generate_recommendations(
        self,
        current: ArchitectureConfig,
        issues: List[Dict]
    ) -> List[str]:
        """Generate architecture recommendations."""
        recommendations = []

        # Check each issue
        for issue in issues:
            if issue['type'] == 'vocab_inefficiency':
                recommendations.append(
                    "Implement BPE tokenization to reduce vocab_size to 8192 with near-100% utilization"
                )
            elif issue['type'] == 'shallow_model':
                recommendations.append(
                    f"Increase num_layers from {current.num_layers} to 6 for deeper reasoning"
                )
            elif issue['type'] == 'small_embeddings':
                recommendations.append(
                    f"Increase embed_dim from {current.embed_dim} to 384 for richer representations"
                )

        # General recommendations
        if current.max_seq_len < 1024:
            recommendations.append(
                "Consider increasing max_seq_len to 1024 for longer mathematical expressions"
            )

        if current.ff_dim < 4 * current.embed_dim:
            recommendations.append(
                f"Increase ff_dim to {4 * current.embed_dim} (4x embed_dim) for better capacity"
            )

        return recommendations

    def get_config(self, config_name: str) -> Optional[ArchitectureConfig]:
        """
        Get a predefined configuration.

        Args:
            config_name: Name of configuration ('base', 'enhanced', etc.)

        Returns:
            ArchitectureConfig or None if not found
        """
        return self.CONFIGS.get(config_name)

    def recommend_config(
        self,
        knowledge_store_size: int = 0,
        target_inference_ms: float = 10.0,
        memory_limit_mb: float = 1000.0
    ) -> Dict[str, Any]:
        """
        Recommend optimal configuration based on constraints.

        Args:
            knowledge_store_size: Number of entries in knowledge store
            target_inference_ms: Maximum acceptable inference time
            memory_limit_mb: Maximum memory usage

        Returns:
            Recommended configuration with rationale
        """
        recommendations = []
        selected_config = 'enhanced'  # Default recommendation

        # Knowledge store size considerations
        if knowledge_store_size < 10000:
            recommendations.append("Small knowledge store - 'base' config sufficient")
            selected_config = 'base'
        elif knowledge_store_size < 50000:
            recommendations.append("Medium knowledge store - 'enhanced' config recommended")
            selected_config = 'enhanced'
        else:
            recommendations.append("Large knowledge store - 'enhanced' or 'maximal' config recommended")
            selected_config = 'enhanced'

        # Inference time considerations
        if target_inference_ms < 5:
            recommendations.append(f"Tight inference target ({target_inference_ms}ms) - prefer smaller model")
            if selected_config == 'maximal':
                selected_config = 'enhanced'
        elif target_inference_ms < 10:
            recommendations.append("Moderate inference target - 'enhanced' should meet requirements")

        # Memory considerations (rough estimates)
        config = self.CONFIGS[selected_config]
        estimated_memory = config.estimate_parameters() * 4 / (1024 * 1024)  # ~4 bytes per param

        if estimated_memory > memory_limit_mb:
            recommendations.append(f"Estimated {estimated_memory:.0f}MB exceeds limit - reducing config")
            if selected_config == 'maximal':
                selected_config = 'enhanced'
            elif selected_config == 'enhanced':
                selected_config = 'base'

        return {
            'recommended_config': selected_config,
            'config_details': self.CONFIGS[selected_config].to_dict(),
            'estimated_parameters': self.CONFIGS[selected_config].estimate_parameters(),
            'rationale': recommendations
        }

    def create_custom_config(
        self,
        name: str,
        **kwargs
    ) -> ArchitectureConfig:
        """
        Create a custom configuration.

        Args:
            name: Name for the configuration
            **kwargs: Architecture parameters

        Returns:
            New ArchitectureConfig
        """
        # Start with base config
        base = self.CONFIGS['base']

        config = ArchitectureConfig(
            name=name,
            vocab_size=kwargs.get('vocab_size', base.vocab_size),
            embed_dim=kwargs.get('embed_dim', base.embed_dim),
            num_heads=kwargs.get('num_heads', base.num_heads),
            num_layers=kwargs.get('num_layers', base.num_layers),
            ff_dim=kwargs.get('ff_dim', base.ff_dim),
            max_seq_len=kwargs.get('max_seq_len', base.max_seq_len),
            dropout=kwargs.get('dropout', base.dropout),
            learning_rate=kwargs.get('learning_rate', base.learning_rate),
            gradient_clip=kwargs.get('gradient_clip', base.gradient_clip),
            warmup_steps=kwargs.get('warmup_steps', base.warmup_steps)
        )

        # Validate constraints
        if config.embed_dim % config.num_heads != 0:
            raise ValueError(f"embed_dim ({config.embed_dim}) must be divisible by num_heads ({config.num_heads})")

        return config

    def compare_configs(
        self,
        config1: str,
        config2: str
    ) -> Dict[str, Any]:
        """
        Compare two configurations.

        Args:
            config1: First config name
            config2: Second config name

        Returns:
            Comparison with differences
        """
        c1 = self.CONFIGS.get(config1)
        c2 = self.CONFIGS.get(config2)

        if not c1 or not c2:
            return {'error': f'Config not found: {config1 if not c1 else config2}'}

        differences = []
        params = ['vocab_size', 'embed_dim', 'num_heads', 'num_layers', 'ff_dim', 'max_seq_len']

        for param in params:
            v1 = getattr(c1, param)
            v2 = getattr(c2, param)
            if v1 != v2:
                change = ((v2 - v1) / v1) * 100 if v1 != 0 else 0
                differences.append({
                    'parameter': param,
                    config1: v1,
                    config2: v2,
                    'change_pct': change
                })

        return {
            'config1': c1.to_dict(),
            'config2': c2.to_dict(),
            'differences': differences,
            'params1': c1.estimate_parameters(),
            'params2': c2.estimate_parameters(),
            'param_increase_factor': c2.estimate_parameters() / c1.estimate_parameters()
        }

    def get_migration_plan(
        self,
        from_config: str,
        to_config: str
    ) -> Dict[str, Any]:
        """
        Get a migration plan between configurations.

        Args:
            from_config: Source configuration
            to_config: Target configuration

        Returns:
            Migration plan with steps
        """
        comparison = self.compare_configs(from_config, to_config)

        if 'error' in comparison:
            return comparison

        steps = [
            {
                'step': 1,
                'action': 'backup_knowledge_store',
                'description': 'Backup current knowledge store to JSON'
            },
            {
                'step': 2,
                'action': 'create_new_model',
                'description': f'Initialize new model with {to_config} configuration',
                'config': self.CONFIGS[to_config].to_dict()
            },
            {
                'step': 3,
                'action': 'migrate_knowledge',
                'description': 'Transfer knowledge store entries (unchanged)'
            },
            {
                'step': 4,
                'action': 'retrain_embeddings',
                'description': 'Retrain neural weights on migrated knowledge',
                'estimated_time': 'Varies by knowledge store size'
            },
            {
                'step': 5,
                'action': 'validate_performance',
                'description': 'Test inference on sample problems'
            },
            {
                'step': 6,
                'action': 'save_checkpoint',
                'description': 'Save new checkpoint, archive old'
            }
        ]

        return {
            'from_config': from_config,
            'to_config': to_config,
            'comparison': comparison,
            'migration_steps': steps,
            'estimated_parameter_change': comparison['param_increase_factor'],
            'risk_level': 'medium' if comparison['param_increase_factor'] > 2 else 'low'
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get architecture statistics."""
        return {
            'current_config': self.current_config.to_dict() if self.current_config else None,
            'available_configs': list(self.CONFIGS.keys()),
            'performance_metrics': self.performance_metrics,
            'config_history': self.config_history[-5:]
        }

    # BDI Agent methods
    def update_beliefs(self, percept: Dict[str, Any] = None) -> None:
        """Update beliefs based on current state and percepts."""
        if percept:
            # Update performance metrics if provided
            for key in ['loss', 'accuracy', 'inference_time_ms', 'memory_usage_mb']:
                if key in percept:
                    self.performance_metrics[key] = percept[key]

        # Determine if upgrade is needed
        if self.current_config:
            enhanced = self.CONFIGS['enhanced']
            self.beliefs['upgrade_needed'] = (
                self.current_config.num_layers < enhanced.num_layers or
                self.current_config.embed_dim < enhanced.embed_dim
            )

        # Identify bottleneck
        if self.performance_metrics['inference_time_ms'] > 50:
            self.beliefs['bottleneck'] = 'inference_speed'
        elif self.performance_metrics['accuracy'] < 0.8:
            self.beliefs['bottleneck'] = 'model_capacity'
        else:
            self.beliefs['bottleneck'] = None

    def deliberate(self) -> Optional[Intention]:
        """Deliberate on current beliefs."""
        if self.beliefs.get('upgrade_needed', False):
            return Intention(
                plan_id='upgrade_architecture',
                steps=['analyze', 'recommend', 'plan_migration', 'execute'],
                target_desire='optimal_architecture'
            )
        return None

    def execute_step(self) -> bool:
        """Execute one step of agent processing."""
        if self.blackboard:
            # Would check for pending architecture tasks
            pass
        return False

    def process(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task from the supervisor.

        Args:
            task_entry: Task with 'action' and relevant data

        Returns:
            Processing result
        """
        action = task_entry.get('action', 'analyze')

        if action == 'analyze':
            return self.analyze_architecture(task_entry.get('model_info'))

        elif action == 'recommend':
            return self.recommend_config(
                knowledge_store_size=task_entry.get('knowledge_store_size', 0),
                target_inference_ms=task_entry.get('target_inference_ms', 10.0),
                memory_limit_mb=task_entry.get('memory_limit_mb', 1000.0)
            )

        elif action == 'get_config':
            config = self.get_config(task_entry.get('config_name', 'enhanced'))
            return config.to_dict() if config else {'error': 'Config not found'}

        elif action == 'compare':
            return self.compare_configs(
                task_entry.get('config1', 'base'),
                task_entry.get('config2', 'enhanced')
            )

        elif action == 'migration_plan':
            return self.get_migration_plan(
                from_config=task_entry.get('from_config', 'base'),
                to_config=task_entry.get('to_config', 'enhanced')
            )

        elif action == 'get_stats':
            return self.get_stats()

        else:
            return {'error': f'Unknown action: {action}'}
