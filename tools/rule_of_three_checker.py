#!/usr/bin/env python3
"""
Rule of Three Duplicate Code Checker

Detects code duplication patterns and suggests refactoring opportunities
based on the "Rule of Three" principle - when similar code appears three times,
it should be refactored into a reusable component.

Features:
- AST-based code similarity detection
- Function, class, and statement pattern matching
- Configurable similarity thresholds
- CI/CD integration with exit codes
- JSON and text output formats
- Exclusion patterns for generated/vendor code
"""

import ast
import argparse
import hashlib
import json
import os
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import defaultdict
import difflib


@dataclass
class CodeFragment:
    """Represents a fragment of code for similarity analysis"""
    file_path: str
    start_line: int
    end_line: int
    content: str
    ast_hash: str
    normalized_content: str
    fragment_type: str  # 'function', 'class', 'block'
    name: Optional[str] = None


@dataclass
class DuplicationGroup:
    """Represents a group of similar code fragments"""
    fragments: List[CodeFragment]
    similarity_score: float
    fragment_type: str
    suggested_refactoring: str
    impact_score: float


class ASTNormalizer(ast.NodeVisitor):
    """Normalizes AST nodes for similarity comparison"""
    
    def __init__(self):
        self.normalized_parts = []
        self.variable_map = {}
        self.var_counter = 0
    
    def normalize_identifier(self, name: str) -> str:
        """Normalize variable/function names to generic identifiers"""
        if name not in self.variable_map:
            self.variable_map[name] = f"VAR_{self.var_counter}"
            self.var_counter += 1
        return self.variable_map[name]
    
    def visit_Name(self, node):
        # Normalize variable names but keep special names
        if node.id in {'self', 'cls', 'True', 'False', 'None'}:
            self.normalized_parts.append(node.id)
        else:
            self.normalized_parts.append(self.normalize_identifier(node.id))
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        self.normalized_parts.append(f"FUNC_{len(node.args.args)}")
        # Don't normalize function names in some contexts
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        self.normalized_parts.append("CLASS")
        self.generic_visit(node)
    
    def visit_Constant(self, node):
        # Normalize constants by type
        if isinstance(node.value, str):
            self.normalized_parts.append("STRING_CONST")
        elif isinstance(node.value, (int, float)):
            self.normalized_parts.append("NUMBER_CONST")
        else:
            self.normalized_parts.append("CONST")
        
    def visit_Attribute(self, node):
        self.visit(node.value)
        self.normalized_parts.append(f"ATTR_{node.attr}")
    
    def get_normalized_string(self) -> str:
        return "_".join(self.normalized_parts)


class RuleOfThreeChecker:
    """Main duplicate code detection engine"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.min_similarity = config.get('min_similarity', 0.8)
        self.min_lines = config.get('min_lines', 5)
        self.exclude_patterns = config.get('exclude_patterns', [])
        self.fragments = []
        self.duplication_groups = []
    
    def should_exclude_file(self, file_path: str) -> bool:
        """Check if file should be excluded from analysis"""
        for pattern in self.exclude_patterns:
            if pattern in file_path:
                return True
        return False
    
    def extract_functions(self, tree: ast.AST, file_path: str, content: str) -> List[CodeFragment]:
        """Extract function definitions as code fragments"""
        fragments = []
        content_lines = content.split('\n')
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                start_line = node.lineno
                end_line = node.end_lineno or start_line
                
                if end_line - start_line + 1 >= self.min_lines:
                    func_content = '\n'.join(content_lines[start_line-1:end_line])
                    
                    # Normalize the AST for similarity comparison
                    normalizer = ASTNormalizer()
                    normalizer.visit(node)
                    normalized = normalizer.get_normalized_string()
                    
                    ast_hash = hashlib.md5(normalized.encode()).hexdigest()
                    
                    fragment = CodeFragment(
                        file_path=file_path,
                        start_line=start_line,
                        end_line=end_line,
                        content=func_content,
                        ast_hash=ast_hash,
                        normalized_content=normalized,
                        fragment_type='function',
                        name=node.name
                    )
                    fragments.append(fragment)
        
        return fragments
    
    def extract_classes(self, tree: ast.AST, file_path: str, content: str) -> List[CodeFragment]:
        """Extract class definitions as code fragments"""
        fragments = []
        content_lines = content.split('\n')
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                start_line = node.lineno
                end_line = node.end_lineno or start_line
                
                if end_line - start_line + 1 >= self.min_lines:
                    class_content = '\n'.join(content_lines[start_line-1:end_line])
                    
                    normalizer = ASTNormalizer()
                    normalizer.visit(node)
                    normalized = normalizer.get_normalized_string()
                    
                    ast_hash = hashlib.md5(normalized.encode()).hexdigest()
                    
                    fragment = CodeFragment(
                        file_path=file_path,
                        start_line=start_line,
                        end_line=end_line,
                        content=class_content,
                        ast_hash=ast_hash,
                        normalized_content=normalized,
                        fragment_type='class',
                        name=node.name
                    )
                    fragments.append(fragment)
        
        return fragments
    
    def extract_statement_blocks(self, tree: ast.AST, file_path: str, content: str) -> List[CodeFragment]:
        """Extract statement blocks as code fragments"""
        fragments = []
        content_lines = content.split('\n')
        
        # Look for compound statements that might be duplicated
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                start_line = node.lineno
                end_line = node.end_lineno or start_line
                
                if end_line - start_line + 1 >= self.min_lines:
                    block_content = '\n'.join(content_lines[start_line-1:end_line])
                    
                    normalizer = ASTNormalizer()
                    normalizer.visit(node)
                    normalized = normalizer.get_normalized_string()
                    
                    ast_hash = hashlib.md5(normalized.encode()).hexdigest()
                    
                    fragment = CodeFragment(
                        file_path=file_path,
                        start_line=start_line,
                        end_line=end_line,
                        content=block_content,
                        ast_hash=ast_hash,
                        normalized_content=normalized,
                        fragment_type='block'
                    )
                    fragments.append(fragment)
        
        return fragments
    
    def analyze_file(self, file_path: str) -> List[CodeFragment]:
        """Analyze a single Python file for code fragments"""
        if self.should_exclude_file(file_path):
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=file_path)
            fragments = []
            
            # Extract different types of code fragments
            fragments.extend(self.extract_functions(tree, file_path, content))
            fragments.extend(self.extract_classes(tree, file_path, content))
            fragments.extend(self.extract_statement_blocks(tree, file_path, content))
            
            return fragments
            
        except (SyntaxError, UnicodeDecodeError) as e:
            print(f"Warning: Could not parse {file_path}: {e}")
            return []
    
    def calculate_similarity(self, frag1: CodeFragment, frag2: CodeFragment) -> float:
        """Calculate similarity between two code fragments"""
        # First check structural similarity via AST hash
        if frag1.ast_hash == frag2.ast_hash:
            return 1.0
        
        # Use sequence matching on normalized content
        matcher = difflib.SequenceMatcher(None, frag1.normalized_content, frag2.normalized_content)
        return matcher.ratio()
    
    def find_duplication_groups(self) -> List[DuplicationGroup]:
        """Find groups of similar code fragments"""
        groups = []
        processed = set()
        
        # Group fragments by AST hash first (exact structural matches)
        hash_groups = defaultdict(list)
        for fragment in self.fragments:
            hash_groups[fragment.ast_hash].append(fragment)
        
        # Process exact matches
        for ast_hash, fragments in hash_groups.items():
            if len(fragments) >= 3:  # Rule of Three
                group = DuplicationGroup(
                    fragments=fragments,
                    similarity_score=1.0,
                    fragment_type=fragments[0].fragment_type,
                    suggested_refactoring=self._suggest_refactoring(fragments),
                    impact_score=self._calculate_impact_score(fragments)
                )
                groups.append(group)
                processed.update(id(f) for f in fragments)
        
        # Process near-matches with similarity threshold
        remaining_fragments = [f for f in self.fragments if id(f) not in processed]
        
        for i, frag1 in enumerate(remaining_fragments):
            similar_group = [frag1]
            
            for j, frag2 in enumerate(remaining_fragments[i+1:], i+1):
                if id(frag2) in processed:
                    continue
                
                similarity = self.calculate_similarity(frag1, frag2)
                if similarity >= self.min_similarity and frag1.fragment_type == frag2.fragment_type:
                    similar_group.append(frag2)
            
            if len(similar_group) >= 3:  # Rule of Three
                group = DuplicationGroup(
                    fragments=similar_group,
                    similarity_score=min(self.calculate_similarity(similar_group[0], f) for f in similar_group[1:]),
                    fragment_type=similar_group[0].fragment_type,
                    suggested_refactoring=self._suggest_refactoring(similar_group),
                    impact_score=self._calculate_impact_score(similar_group)
                )
                groups.append(group)
                processed.update(id(f) for f in similar_group)
        
        return sorted(groups, key=lambda g: g.impact_score, reverse=True)
    
    def _suggest_refactoring(self, fragments: List[CodeFragment]) -> str:
        """Suggest refactoring strategy for duplicate code"""
        fragment_type = fragments[0].fragment_type
        count = len(fragments)
        
        if fragment_type == 'function':
            return f"Extract common logic into a shared utility function. Found {count} similar functions."
        elif fragment_type == 'class':
            return f"Consider using inheritance or composition to share common behavior. Found {count} similar classes."
        elif fragment_type == 'block':
            return f"Extract repeated logic into a helper function or method. Found {count} similar code blocks."
        else:
            return f"Refactor {count} similar code fragments into a reusable component."
    
    def _calculate_impact_score(self, fragments: List[CodeFragment]) -> float:
        """Calculate impact score based on duplication severity"""
        # Factors: number of duplicates, code size, similarity
        num_duplicates = len(fragments)
        avg_size = sum(f.end_line - f.start_line + 1 for f in fragments) / num_duplicates
        
        # Higher score for more duplicates and larger code blocks
        impact = (num_duplicates * 0.4) + (avg_size * 0.1)
        
        # Boost score for functions and classes (more important to refactor)
        if fragments[0].fragment_type in ['function', 'class']:
            impact *= 1.5
        
        return min(impact, 10.0)  # Cap at 10.0
    
    def analyze_directory(self, directory: str) -> None:
        """Analyze all Python files in a directory"""
        directory_path = Path(directory)
        
        for py_file in directory_path.rglob("*.py"):
            fragments = self.analyze_file(str(py_file))
            self.fragments.extend(fragments)
        
        print(f"Analyzed {len(list(directory_path.rglob('*.py')))} Python files")
        print(f"Found {len(self.fragments)} code fragments")
        
        self.duplication_groups = self.find_duplication_groups()
    
    def generate_report(self, output_format: str = 'text') -> str:
        """Generate a duplication report"""
        if output_format == 'json':
            return self._generate_json_report()
        else:
            return self._generate_text_report()
    
    def _generate_text_report(self) -> str:
        """Generate a human-readable text report"""
        report = []
        report.append("🔍 Rule of Three Duplicate Code Analysis Report")
        report.append("=" * 60)
        report.append("")
        
        if not self.duplication_groups:
            report.append("✅ No significant code duplication found!")
            report.append("All code appears to follow good DRY (Don't Repeat Yourself) principles.")
            return "\n".join(report)
        
        report.append(f"⚠️  Found {len(self.duplication_groups)} duplication groups that violate the Rule of Three")
        report.append("")
        
        for i, group in enumerate(self.duplication_groups, 1):
            report.append(f"## Duplication Group {i} (Impact: {group.impact_score:.1f}/10)")
            report.append(f"**Type**: {group.fragment_type.title()}")
            report.append(f"**Similarity**: {group.similarity_score:.1%}")
            report.append(f"**Instances**: {len(group.fragments)}")
            report.append("")
            report.append(f"**Suggested Refactoring**: {group.suggested_refactoring}")
            report.append("")
            report.append("**Duplicated Code Locations**:")
            
            for j, fragment in enumerate(group.fragments, 1):
                location = f"{fragment.file_path}:{fragment.start_line}-{fragment.end_line}"
                if fragment.name:
                    location += f" ({fragment.name})"
                report.append(f"  {j}. {location}")
            
            report.append("")
            report.append("**Sample Code** (first instance):")
            sample_lines = group.fragments[0].content.split('\n')[:10]
            for line in sample_lines:
                report.append(f"    {line}")
            if len(group.fragments[0].content.split('\n')) > 10:
                report.append("    ... (truncated)")
            report.append("")
            report.append("-" * 60)
            report.append("")
        
        # Summary statistics
        total_fragments = sum(len(g.fragments) for g in self.duplication_groups)
        high_impact = len([g for g in self.duplication_groups if g.impact_score >= 5.0])
        
        report.append("## Summary")
        report.append(f"- Total duplicate code fragments: {total_fragments}")
        report.append(f"- High-impact duplications: {high_impact}")
        report.append(f"- Average impact score: {sum(g.impact_score for g in self.duplication_groups) / len(self.duplication_groups):.1f}")
        
        return "\n".join(report)
    
    def _generate_json_report(self) -> str:
        """Generate a JSON report for CI/CD integration"""
        report_data = {
            "summary": {
                "total_groups": len(self.duplication_groups),
                "total_fragments": sum(len(g.fragments) for g in self.duplication_groups),
                "high_impact_groups": len([g for g in self.duplication_groups if g.impact_score >= 5.0]),
                "average_impact": sum(g.impact_score for g in self.duplication_groups) / len(self.duplication_groups) if self.duplication_groups else 0
            },
            "duplication_groups": [
                {
                    "id": i,
                    "fragment_type": group.fragment_type,
                    "similarity_score": group.similarity_score,
                    "impact_score": group.impact_score,
                    "suggested_refactoring": group.suggested_refactoring,
                    "fragments": [
                        {
                            "file_path": frag.file_path,
                            "start_line": frag.start_line,
                            "end_line": frag.end_line,
                            "name": frag.name
                        }
                        for frag in group.fragments
                    ]
                }
                for i, group in enumerate(self.duplication_groups, 1)
            ]
        }
        
        return json.dumps(report_data, indent=2)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Rule of Three Duplicate Code Checker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python rule_of_three_checker.py .                    # Analyze current directory
  python rule_of_three_checker.py src/ --json         # JSON output for CI
  python rule_of_three_checker.py . --min-similarity 0.9  # Higher threshold
  python rule_of_three_checker.py . --exclude test_,migrations  # Exclude patterns
        """
    )
    
    parser.add_argument(
        'directory',
        help='Directory to analyze for duplicate code'
    )
    
    parser.add_argument(
        '--min-similarity',
        type=float,
        default=0.8,
        help='Minimum similarity threshold (0.0-1.0, default: 0.8)'
    )
    
    parser.add_argument(
        '--min-lines',
        type=int,
        default=5,
        help='Minimum lines of code to consider (default: 5)'
    )
    
    parser.add_argument(
        '--exclude',
        nargs='*',
        default=['test_', '__pycache__', '.pyc', 'migrations', 'vendor'],
        help='Patterns to exclude from analysis'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results in JSON format'
    )
    
    parser.add_argument(
        '--fail-on-duplication',
        action='store_true',
        help='Exit with code 1 if duplications found (for CI)'
    )
    
    parser.add_argument(
        '--max-impact',
        type=float,
        default=5.0,
        help='Maximum allowed impact score before failing (default: 5.0)'
    )
    
    args = parser.parse_args()
    
    # Configuration
    config = {
        'min_similarity': args.min_similarity,
        'min_lines': args.min_lines,
        'exclude_patterns': args.exclude
    }
    
    # Run analysis
    checker = RuleOfThreeChecker(config)
    checker.analyze_directory(args.directory)
    
    # Generate report
    output_format = 'json' if args.json else 'text'
    report = checker.generate_report(output_format)
    print(report)
    
    # Exit with appropriate code for CI
    if args.fail_on_duplication and checker.duplication_groups:
        high_impact_groups = [g for g in checker.duplication_groups if g.impact_score >= args.max_impact]
        if high_impact_groups:
            print(f"\n❌ Found {len(high_impact_groups)} high-impact duplication groups (threshold: {args.max_impact})", file=sys.stderr)
            sys.exit(1)
        else:
            print(f"\n⚠️  Found duplications but all below impact threshold ({args.max_impact})", file=sys.stderr)
    
    print(f"\n✅ Analysis complete. Found {len(checker.duplication_groups)} duplication groups.")


if __name__ == "__main__":
    main()
