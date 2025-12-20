"""
Specialized metrics for measuring learning effectiveness.

This module provides metrics that go beyond simple accuracy to measure:
- How well systems learn over time
- Whether they forget old knowledge (catastrophic forgetting)
- Whether they transfer learning to new domains
- How quickly they adapt to new patterns
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple, Optional
import statistics


@dataclass
class LearningMetrics:
    """
    Comprehensive learning effectiveness measurement.

    Tracks not just "does it work" but "does it improve and generalize".
    """
    baseline_accuracy: float = 0.0
    final_accuracy: float = 0.0
    improvement_ratio: float = 0.0
    time_to_convergence: Optional[float] = None  # Seconds until 95% of max performance
    sample_efficiency: float = 0.0  # Accuracy per training example

    # Advanced metrics
    catastrophic_forgetting_score: float = 0.0  # 0=perfect retention, 1=total forgetting
    transfer_learning_score: float = 0.0  # How well learning transfers to new domains
    adaptation_speed: float = 0.0  # How quickly system adapts (iterations to threshold)
    robustness_score: float = 0.0  # Performance under noise/outliers

    def compute_overall_score(self) -> float:
        """
        Compute overall learning quality score (0-1, higher is better).

        Weighted combination of all metrics.
        """
        # Weights for different aspects
        weights = {
            'improvement': 0.30,
            'sample_efficiency': 0.15,
            'adaptation_speed': 0.15,
            'transfer': 0.15,
            'forgetting': 0.15,  # Inverted (lower is better)
            'robustness': 0.10
        }

        # Normalize metrics to 0-1 range
        norm_improvement = min(self.improvement_ratio, 1.0)
        norm_sample_eff = min(self.sample_efficiency, 1.0)
        norm_adapt_speed = min(self.adaptation_speed, 1.0)
        norm_transfer = min(self.transfer_learning_score, 1.0)
        norm_forgetting = 1.0 - min(self.catastrophic_forgetting_score, 1.0)  # Invert
        norm_robustness = min(self.robustness_score, 1.0)

        overall = (
            weights['improvement'] * norm_improvement +
            weights['sample_efficiency'] * norm_sample_eff +
            weights['adaptation_speed'] * norm_adapt_speed +
            weights['transfer'] * norm_transfer +
            weights['forgetting'] * norm_forgetting +
            weights['robustness'] * norm_robustness
        )

        return overall

    def to_dict(self) -> Dict[str, Any]:
        """Export metrics as dictionary"""
        return {
            'baseline_accuracy': self.baseline_accuracy,
            'final_accuracy': self.final_accuracy,
            'improvement_ratio': self.improvement_ratio,
            'improvement_percent': self.improvement_ratio * 100,
            'time_to_convergence': self.time_to_convergence,
            'sample_efficiency': self.sample_efficiency,
            'catastrophic_forgetting_score': self.catastrophic_forgetting_score,
            'transfer_learning_score': self.transfer_learning_score,
            'adaptation_speed': self.adaptation_speed,
            'robustness_score': self.robustness_score,
            'overall_score': self.compute_overall_score()
        }


@dataclass
class RoutingTableEvolution:
    """
    Tracks how Meta-Learning routing tables evolve over time.

    Used to verify that routing preferences adapt based on empirical success rates.
    """
    snapshots: List[Dict[str, Dict[str, float]]] = field(default_factory=list)
    # Each snapshot: problem_type -> agent_id -> weight

    def add_snapshot(self, routing_tables: Dict[str, Dict[str, float]]):
        """Record a snapshot of current routing tables"""
        # Deep copy to avoid reference issues
        snapshot = {}
        for problem_type, agents in routing_tables.items():
            snapshot[problem_type] = agents.copy()
        self.snapshots.append(snapshot)

    def compute_stability_score(self) -> float:
        """
        Measure routing table stability (0=chaotic, 1=stable/converged).

        Computes variance in weights over time. Low variance = stable.
        """
        if len(self.snapshots) < 2:
            return 0.0

        # Track weight changes for each (problem_type, agent_id) pair
        weight_histories = {}

        for snapshot in self.snapshots:
            for problem_type, agents in snapshot.items():
                for agent_id, weight in agents.items():
                    key = (problem_type, agent_id)
                    if key not in weight_histories:
                        weight_histories[key] = []
                    weight_histories[key].append(weight)

        # Compute average coefficient of variation across all weight histories
        cvs = []
        for weights in weight_histories.values():
            if len(weights) < 2:
                continue
            try:
                mean = statistics.mean(weights)
                if mean == 0:
                    continue
                stdev = statistics.stdev(weights)
                cv = stdev / abs(mean)
                cvs.append(cv)
            except:
                continue

        if not cvs:
            return 0.0

        avg_cv = statistics.mean(cvs)
        # Convert CV to stability score (lower CV = higher stability)
        stability = 1.0 / (1.0 + avg_cv)
        return stability

    def detect_convergence(self, window_size: int = 10) -> Optional[int]:
        """
        Detect which snapshot iteration routing converged.

        Returns: Snapshot index where convergence detected, or None
        """
        if len(self.snapshots) < window_size:
            return None

        for i in range(window_size, len(self.snapshots)):
            window = self.snapshots[i-window_size:i]

            # Check if weights are stable in this window
            all_stable = True
            for problem_type in window[0].keys():
                for agent_id in window[0][problem_type].keys():
                    weights_in_window = []
                    for snapshot in window:
                        if problem_type in snapshot and agent_id in snapshot[problem_type]:
                            weights_in_window.append(snapshot[problem_type][agent_id])

                    if len(weights_in_window) < window_size:
                        continue

                    try:
                        variance = statistics.variance(weights_in_window)
                        mean_val = statistics.mean(weights_in_window)
                        if mean_val != 0 and (variance ** 0.5) / abs(mean_val) > 0.05:
                            all_stable = False
                            break
                    except:
                        continue

                if not all_stable:
                    break

            if all_stable:
                return i

        return None


@dataclass
class SimilarityMatrixEvolution:
    """
    Tracks how Heuristic Transfer Engine similarity matrix learns.

    Verifies that empirical evidence updates similarity scores appropriately.
    """
    initial_matrix: Dict[Tuple[str, str], float] = field(default_factory=dict)
    current_matrix: Dict[Tuple[str, str], float] = field(default_factory=dict)
    empirical_adjustments: int = 0
    transfer_outcomes: List[Tuple[Tuple[str, str], bool]] = field(default_factory=list)
    # (domain_pair, success)

    def record_initial_matrix(self, matrix: Dict[Tuple[str, str], float]):
        """Record the initial similarity matrix"""
        self.initial_matrix = matrix.copy()
        self.current_matrix = matrix.copy()

    def record_update(self, matrix: Dict[Tuple[str, str], float]):
        """Record an update to the similarity matrix"""
        self.current_matrix = matrix.copy()
        self.empirical_adjustments += 1

    def record_transfer(self, source_domain: str, target_domain: str, success: bool):
        """Record a transfer attempt outcome"""
        pair = tuple(sorted([source_domain, target_domain]))
        self.transfer_outcomes.append((pair, success))

    def compute_prediction_accuracy(self) -> float:
        """
        Measure how well similarity scores predict transfer success.

        Higher similarity should correlate with higher success rate.
        """
        if not self.transfer_outcomes:
            return 0.0

        # Group transfers by domain pair
        pair_results = {}
        for pair, success in self.transfer_outcomes:
            if pair not in pair_results:
                pair_results[pair] = []
            pair_results[pair].append(success)

        # Compute success rate for each pair
        pair_success_rates = {}
        for pair, results in pair_results.items():
            pair_success_rates[pair] = sum(results) / len(results)

        # Compute correlation between similarity and success rate
        pairs_with_both = []
        for pair in pair_success_rates.keys():
            if pair in self.current_matrix:
                similarity = self.current_matrix[pair]
                success_rate = pair_success_rates[pair]
                pairs_with_both.append((similarity, success_rate))

        if len(pairs_with_both) < 2:
            return 0.0

        # Simple correlation: pairs with high similarity should have high success
        # Use Spearman's rank correlation approximation
        sorted_by_sim = sorted(pairs_with_both, key=lambda x: x[0])
        sorted_by_success = sorted(pairs_with_both, key=lambda x: x[1])

        # Count concordant pairs
        concordant = 0
        total_pairs = 0
        for i in range(len(sorted_by_sim)):
            for j in range(i+1, len(sorted_by_sim)):
                total_pairs += 1
                # Check if ranking is concordant
                if ((sorted_by_sim[i][0] < sorted_by_sim[j][0] and
                     sorted_by_sim[i][1] < sorted_by_sim[j][1]) or
                    (sorted_by_sim[i][0] > sorted_by_sim[j][0] and
                     sorted_by_sim[i][1] > sorted_by_sim[j][1])):
                    concordant += 1

        if total_pairs == 0:
            return 0.0

        return concordant / total_pairs

    def compute_learning_magnitude(self) -> float:
        """
        Measure how much the matrix has changed from initial state.

        Returns average absolute change in similarity scores.
        """
        if not self.initial_matrix or not self.current_matrix:
            return 0.0

        total_change = 0.0
        count = 0

        for pair in self.initial_matrix.keys():
            if pair in self.current_matrix:
                change = abs(self.current_matrix[pair] - self.initial_matrix[pair])
                total_change += change
                count += 1

        if count == 0:
            return 0.0

        return total_change / count


@dataclass
class NoveltyDetectionQuality:
    """
    Measures Pattern Recognizer's novelty detection accuracy.

    Tracks precision, recall, and F1 score for identifying novel patterns.
    """
    true_positives: int = 0   # Correctly identified novel patterns
    false_positives: int = 0  # Incorrectly flagged as novel
    true_negatives: int = 0   # Correctly rejected trivial patterns
    false_negatives: int = 0  # Missed novel patterns

    def record_prediction(self, ground_truth_novel: bool, predicted_novel: bool):
        """Record a single prediction"""
        if ground_truth_novel and predicted_novel:
            self.true_positives += 1
        elif not ground_truth_novel and predicted_novel:
            self.false_positives += 1
        elif not ground_truth_novel and not predicted_novel:
            self.true_negatives += 1
        else:  # ground_truth_novel and not predicted_novel
            self.false_negatives += 1

    def compute_precision(self) -> float:
        """Precision = TP / (TP + FP)"""
        denominator = self.true_positives + self.false_positives
        if denominator == 0:
            return 0.0
        return self.true_positives / denominator

    def compute_recall(self) -> float:
        """Recall = TP / (TP + FN)"""
        denominator = self.true_positives + self.false_negatives
        if denominator == 0:
            return 0.0
        return self.true_positives / denominator

    def compute_f1_score(self) -> float:
        """F1 = 2 * (precision * recall) / (precision + recall)"""
        precision = self.compute_precision()
        recall = self.compute_recall()
        denominator = precision + recall
        if denominator == 0:
            return 0.0
        return 2 * (precision * recall) / denominator

    def compute_accuracy(self) -> float:
        """Accuracy = (TP + TN) / (TP + TN + FP + FN)"""
        total = self.true_positives + self.true_negatives + self.false_positives + self.false_negatives
        if total == 0:
            return 0.0
        return (self.true_positives + self.true_negatives) / total

    def to_dict(self) -> Dict[str, Any]:
        """Export metrics as dictionary"""
        return {
            'true_positives': self.true_positives,
            'false_positives': self.false_positives,
            'true_negatives': self.true_negatives,
            'false_negatives': self.false_negatives,
            'precision': self.compute_precision(),
            'recall': self.compute_recall(),
            'f1_score': self.compute_f1_score(),
            'accuracy': self.compute_accuracy()
        }
