"""
Rule database for storing and managing generated rules with comprehensive metadata.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class RuleMetadata:
    """Metadata for a stored rule."""
    rule_id: str
    site_url: str
    cmp_type: str
    confidence_score: float
    generation_timestamp: str
    sites_covered: List[str]
    pattern_similarities: Dict[str, float]
    test_results: Dict[str, Any]
    rule_version: str
    notes: str
    tags: List[str]
    success_rate: float
    last_tested: Optional[str] = None
    failure_reasons: List[str] = None


class RuleDatabase:
    """Database for storing and managing consent rules with metadata."""
    
    def __init__(self, db_path: str = "data/rules_database"):
        """
        Initialize the rule database.
        
        Args:
            db_path: Path to store the database files
        """
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        # Database file paths
        self.rules_dir = self.db_path / "rules"
        self.metadata_dir = self.db_path / "metadata"
        self.analytics_dir = self.db_path / "analytics"
        
        # Create directories
        for directory in [self.rules_dir, self.metadata_dir, self.analytics_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize database index
        self.index_file = self.db_path / "index.json"
        self.index = self._load_index()
    
    def _load_index(self) -> Dict[str, Any]:
        """Load the database index."""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {"rules": {}, "analytics": {}, "last_updated": None}
        return {"rules": {}, "analytics": {}, "last_updated": None}
    
    def _save_index(self):
        """Save the database index."""
        self.index["last_updated"] = datetime.now().isoformat()
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, indent=2, ensure_ascii=False)
    
    def store_rule(self, rule: Dict[str, Any], metadata: RuleMetadata) -> str:
        """
        Store a rule with comprehensive metadata.
        
        Args:
            rule: The rule JSON to store
            metadata: Metadata about the rule
            
        Returns:
            Rule ID
        """
        rule_id = metadata.rule_id
        
        # Store rule JSON
        rule_file = self.rules_dir / f"{rule_id}.json"
        with open(rule_file, 'w', encoding='utf-8') as f:
            json.dump(rule, f, indent=2, ensure_ascii=False)
        
        # Store metadata
        metadata_file = self.metadata_dir / f"{rule_id}_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(metadata), f, indent=2, ensure_ascii=False)
        
        # Update index
        self.index["rules"][rule_id] = {
            "site_url": metadata.site_url,
            "cmp_type": metadata.cmp_type,
            "confidence_score": metadata.confidence_score,
            "generation_timestamp": metadata.generation_timestamp,
            "sites_covered": metadata.sites_covered,
            "success_rate": metadata.success_rate,
            "tags": metadata.tags
        }
        
        self._save_index()
        return rule_id
    
    def get_rule(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """Get a rule by ID."""
        rule_file = self.rules_dir / f"{rule_id}.json"
        if rule_file.exists():
            with open(rule_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def get_rule_metadata(self, rule_id: str) -> Optional[RuleMetadata]:
        """Get rule metadata by ID."""
        metadata_file = self.metadata_dir / f"{rule_id}_metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return RuleMetadata(**data)
        return None
    
    def get_rules_by_cmp_type(self, cmp_type: str) -> List[Dict[str, Any]]:
        """Get all rules for a specific CMP type."""
        rules = []
        for rule_id, rule_info in self.index["rules"].items():
            if rule_info.get("cmp_type") == cmp_type:
                rule = self.get_rule(rule_id)
                if rule:
                    rules.append({
                        "rule_id": rule_id,
                        "rule": rule,
                        "metadata": rule_info
                    })
        return rules
    
    def get_rules_by_site(self, site_url: str) -> List[Dict[str, Any]]:
        """Get all rules that cover a specific site."""
        rules = []
        for rule_id, rule_info in self.index["rules"].items():
            if site_url in rule_info.get("sites_covered", []):
                rule = self.get_rule(rule_id)
                if rule:
                    rules.append({
                        "rule_id": rule_id,
                        "rule": rule,
                        "metadata": rule_info
                    })
        return rules
    
    def update_rule_metadata(self, rule_id: str, updates: Dict[str, Any]) -> bool:
        """Update rule metadata."""
        metadata = self.get_rule_metadata(rule_id)
        if not metadata:
            return False
        
        # Update metadata fields
        for key, value in updates.items():
            if hasattr(metadata, key):
                setattr(metadata, key, value)
        
        # Save updated metadata
        metadata_file = self.metadata_dir / f"{rule_id}_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(metadata), f, indent=2, ensure_ascii=False)
        
        # Update index
        if rule_id in self.index["rules"]:
            for key, value in updates.items():
                if key in self.index["rules"][rule_id]:
                    self.index["rules"][rule_id][key] = value
        
        self._save_index()
        return True
    
    def add_test_result(self, rule_id: str, test_result: Dict[str, Any]) -> bool:
        """Add test result to a rule."""
        metadata = self.get_rule_metadata(rule_id)
        if not metadata:
            return False
        
        # Update test results
        if not metadata.test_results:
            metadata.test_results = {}
        
        test_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        metadata.test_results[test_id] = test_result
        metadata.last_tested = datetime.now().isoformat()
        
        # Calculate success rate
        total_tests = len(metadata.test_results)
        successful_tests = sum(1 for result in metadata.test_results.values() 
                             if result.get('success', False))
        metadata.success_rate = successful_tests / total_tests if total_tests > 0 else 0
        
        return self.update_rule_metadata(rule_id, {
            "test_results": metadata.test_results,
            "last_tested": metadata.last_tested,
            "success_rate": metadata.success_rate
        })
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get analytics about stored rules."""
        analytics = {
            "total_rules": len(self.index["rules"]),
            "rules_by_cmp_type": {},
            "rules_by_confidence": {"high": 0, "medium": 0, "low": 0},
            "average_success_rate": 0,
            "most_common_cmp_types": [],
            "coverage_statistics": {},
            "recent_activity": []
        }
        
        # Analyze rules
        cmp_type_counts = {}
        confidence_counts = {"high": 0, "medium": 0, "low": 0}
        success_rates = []
        
        for rule_id, rule_info in self.index["rules"].items():
            # CMP type analysis
            cmp_type = rule_info.get("cmp_type", "unknown")
            cmp_type_counts[cmp_type] = cmp_type_counts.get(cmp_type, 0) + 1
            
            # Confidence analysis
            confidence = rule_info.get("confidence_score", 0)
            if confidence >= 0.8:
                confidence_counts["high"] += 1
            elif confidence >= 0.6:
                confidence_counts["medium"] += 1
            else:
                confidence_counts["low"] += 1
            
            # Success rate analysis
            success_rate = rule_info.get("success_rate", 0)
            success_rates.append(success_rate)
        
        analytics["rules_by_cmp_type"] = cmp_type_counts
        analytics["rules_by_confidence"] = confidence_counts
        analytics["average_success_rate"] = sum(success_rates) / len(success_rates) if success_rates else 0
        
        # Most common CMP types
        analytics["most_common_cmp_types"] = sorted(
            cmp_type_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        return analytics
    
    def search_rules(self, query: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Search rules by query and filters."""
        results = []
        
        for rule_id, rule_info in self.index["rules"].items():
            # Apply filters
            if filters:
                if "cmp_type" in filters and rule_info.get("cmp_type") != filters["cmp_type"]:
                    continue
                if "min_confidence" in filters and rule_info.get("confidence_score", 0) < filters["min_confidence"]:
                    continue
                if "min_success_rate" in filters and rule_info.get("success_rate", 0) < filters["min_success_rate"]:
                    continue
            
            # Text search
            if query:
                searchable_text = " ".join([
                    rule_info.get("site_url", ""),
                    rule_info.get("cmp_type", ""),
                    " ".join(rule_info.get("tags", []))
                ]).lower()
                
                if query.lower() not in searchable_text:
                    continue
            
            # Get full rule and metadata
            rule = self.get_rule(rule_id)
            metadata = self.get_rule_metadata(rule_id)
            
            if rule and metadata:
                results.append({
                    "rule_id": rule_id,
                    "rule": rule,
                    "metadata": asdict(metadata)
                })
        
        return results
    
    def delete_rule(self, rule_id: str) -> bool:
        """Delete a rule and its metadata."""
        try:
            # Delete files
            rule_file = self.rules_dir / f"{rule_id}.json"
            metadata_file = self.metadata_dir / f"{rule_id}_metadata.json"
            
            if rule_file.exists():
                rule_file.unlink()
            if metadata_file.exists():
                metadata_file.unlink()
            
            # Remove from index
            if rule_id in self.index["rules"]:
                del self.index["rules"][rule_id]
                self._save_index()
            
            return True
        except Exception:
            return False
    
    def export_rules(self, output_path: str, rule_ids: List[str] = None) -> bool:
        """Export rules to a file."""
        try:
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "rules": {},
                "metadata": {}
            }
            
            # Get rules to export
            if rule_ids:
                rules_to_export = rule_ids
            else:
                rules_to_export = list(self.index["rules"].keys())
            
            for rule_id in rules_to_export:
                rule = self.get_rule(rule_id)
                metadata = self.get_rule_metadata(rule_id)
                
                if rule:
                    export_data["rules"][rule_id] = rule
                if metadata:
                    export_data["metadata"][rule_id] = asdict(metadata)
            
            # Save export file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception:
            return False
    
    def import_rules(self, import_path: str) -> int:
        """Import rules from a file."""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            imported_count = 0
            
            for rule_id, rule in import_data.get("rules", {}).items():
                metadata_dict = import_data.get("metadata", {}).get(rule_id, {})
                
                # Create metadata object
                metadata = RuleMetadata(
                    rule_id=rule_id,
                    site_url=metadata_dict.get("site_url", ""),
                    cmp_type=metadata_dict.get("cmp_type", "unknown"),
                    confidence_score=metadata_dict.get("confidence_score", 0.0),
                    generation_timestamp=metadata_dict.get("generation_timestamp", datetime.now().isoformat()),
                    sites_covered=metadata_dict.get("sites_covered", []),
                    pattern_similarities=metadata_dict.get("pattern_similarities", {}),
                    test_results=metadata_dict.get("test_results", {}),
                    rule_version=metadata_dict.get("rule_version", "1.0"),
                    notes=metadata_dict.get("notes", ""),
                    tags=metadata_dict.get("tags", []),
                    success_rate=metadata_dict.get("success_rate", 0.0)
                )
                
                # Store rule
                self.store_rule(rule, metadata)
                imported_count += 1
            
            return imported_count
        except Exception:
            return 0
    
    def get_rule_coverage(self) -> Dict[str, Any]:
        """Get rule coverage statistics."""
        coverage = {
            "total_sites_covered": set(),
            "rules_per_site": {},
            "coverage_gaps": [],
            "overlapping_rules": []
        }
        
        # Collect all covered sites
        for rule_id, rule_info in self.index["rules"].items():
            sites_covered = rule_info.get("sites_covered", [])
            coverage["total_sites_covered"].update(sites_covered)
            
            for site in sites_covered:
                if site not in coverage["rules_per_site"]:
                    coverage["rules_per_site"][site] = []
                coverage["rules_per_site"][site].append(rule_id)
        
        # Convert set to list for JSON serialization
        coverage["total_sites_covered"] = list(coverage["total_sites_covered"])
        
        # Find overlapping rules (sites covered by multiple rules)
        for site, rule_ids in coverage["rules_per_site"].items():
            if len(rule_ids) > 1:
                coverage["overlapping_rules"].append({
                    "site": site,
                    "rule_ids": rule_ids
                })
        
        return coverage
