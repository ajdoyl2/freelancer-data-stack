#!/bin/bash
# Rule of Three Duplicate Code Checker - Local Runner
# 
# Convenient wrapper script for running duplicate code analysis locally
# Supports multiple output formats and configuration options

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default configuration
DEFAULT_DIR="."
DEFAULT_SIMILARITY="0.8"
DEFAULT_MIN_LINES="5"
DEFAULT_MAX_IMPACT="5.0"
DEFAULT_FORMAT="text"
DEFAULT_EXCLUDE="test_ __pycache__ .pyc migrations vendor"

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHECKER_SCRIPT="$SCRIPT_DIR/rule_of_three_checker.py"

# Usage function
usage() {
    echo -e "${CYAN}Rule of Three Duplicate Code Checker${NC}"
    echo ""
    echo -e "${BLUE}Usage:${NC}"
    echo "  $0 [OPTIONS] [DIRECTORY]"
    echo ""
    echo -e "${BLUE}Options:${NC}"
    echo "  -s, --similarity FLOAT    Minimum similarity threshold (0.0-1.0, default: $DEFAULT_SIMILARITY)"
    echo "  -l, --min-lines INT       Minimum lines to consider (default: $DEFAULT_MIN_LINES)"
    echo "  -i, --max-impact FLOAT    Maximum impact before failing (default: $DEFAULT_MAX_IMPACT)"
    echo "  -f, --format FORMAT       Output format: text, json (default: $DEFAULT_FORMAT)"
    echo "  -e, --exclude PATTERNS    Space-separated exclude patterns"
    echo "  -o, --output FILE         Output file (default: stdout)"
    echo "  -r, --reports-dir DIR     Reports directory (default: reports/)"
    echo "  -c, --config FILE         Configuration file (YAML)"
    echo "  -q, --quiet               Quiet mode (only show summary)"
    echo "  -v, --verbose             Verbose mode (show debug info)"
    echo "  --fail-on-duplication     Exit with code 1 if duplications found"
    echo "  --strict                  Strict mode (fail on any duplication)"
    echo "  --ci                      CI mode (JSON output + failure on high impact)"
    echo "  -h, --help                Show this help message"
    echo ""
    echo -e "${BLUE}Examples:${NC}"
    echo "  $0                        # Analyze current directory"
    echo "  $0 src/                   # Analyze src/ directory"
    echo "  $0 --similarity 0.9       # Higher similarity threshold"
    echo "  $0 --format json          # JSON output"
    echo "  $0 --ci                   # CI mode"
    echo "  $0 --exclude \"test_ vendor build\"  # Custom exclusions"
    echo ""
    echo -e "${BLUE}Output:${NC}"
    echo "  - Text format: Human-readable analysis report"
    echo "  - JSON format: Machine-readable data for CI/CD"
    echo "  - Reports saved to reports/ directory"
    echo ""
}

# Parse command line arguments
DIRECTORY="$DEFAULT_DIR"
SIMILARITY="$DEFAULT_SIMILARITY"
MIN_LINES="$DEFAULT_MIN_LINES"
MAX_IMPACT="$DEFAULT_MAX_IMPACT"
FORMAT="$DEFAULT_FORMAT"
EXCLUDE="$DEFAULT_EXCLUDE"
OUTPUT=""
REPORTS_DIR="reports"
CONFIG_FILE=""
QUIET=false
VERBOSE=false
FAIL_ON_DUPLICATION=false
STRICT=false
CI_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--similarity)
            SIMILARITY="$2"
            shift 2
            ;;
        -l|--min-lines)
            MIN_LINES="$2"
            shift 2
            ;;
        -i|--max-impact)
            MAX_IMPACT="$2"
            shift 2
            ;;
        -f|--format)
            FORMAT="$2"
            shift 2
            ;;
        -e|--exclude)
            EXCLUDE="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT="$2"
            shift 2
            ;;
        -r|--reports-dir)
            REPORTS_DIR="$2"
            shift 2
            ;;
        -c|--config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        -q|--quiet)
            QUIET=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        --fail-on-duplication)
            FAIL_ON_DUPLICATION=true
            shift
            ;;
        --strict)
            STRICT=true
            FAIL_ON_DUPLICATION=true
            MAX_IMPACT="0.1"
            shift
            ;;
        --ci)
            CI_MODE=true
            FORMAT="json"
            FAIL_ON_DUPLICATION=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        -*)
            echo -e "${RED}Error: Unknown option $1${NC}" >&2
            usage >&2
            exit 1
            ;;
        *)
            DIRECTORY="$1"
            shift
            ;;
    esac
done

# Validate inputs
if [[ ! -d "$DIRECTORY" ]]; then
    echo -e "${RED}Error: Directory '$DIRECTORY' does not exist${NC}" >&2
    exit 1
fi

if [[ ! -f "$CHECKER_SCRIPT" ]]; then
    echo -e "${RED}Error: Checker script not found: $CHECKER_SCRIPT${NC}" >&2
    exit 1
fi

# Check Python availability
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 is required but not installed${NC}" >&2
    exit 1
fi

# Create reports directory
mkdir -p "$REPORTS_DIR"

# Build command arguments
ARGS=()
ARGS+=("$DIRECTORY")
ARGS+=("--min-similarity" "$SIMILARITY")
ARGS+=("--min-lines" "$MIN_LINES")
ARGS+=("--max-impact" "$MAX_IMPACT")

# Add exclude patterns
if [[ -n "$EXCLUDE" ]]; then
    ARGS+=("--exclude")
    for pattern in $EXCLUDE; do
        ARGS+=("$pattern")
    done
fi

# Add format
if [[ "$FORMAT" == "json" ]]; then
    ARGS+=("--json")
fi

# Add failure mode
if [[ "$FAIL_ON_DUPLICATION" == true ]]; then
    ARGS+=("--fail-on-duplication")
fi

# Show configuration in verbose mode
if [[ "$VERBOSE" == true ]]; then
    echo -e "${CYAN}🔍 Rule of Three Duplicate Code Checker${NC}"
    echo -e "${BLUE}Configuration:${NC}"
    echo "  Directory: $DIRECTORY"
    echo "  Similarity threshold: $SIMILARITY"
    echo "  Minimum lines: $MIN_LINES"
    echo "  Maximum impact: $MAX_IMPACT"
    echo "  Format: $FORMAT"
    echo "  Exclude patterns: $EXCLUDE"
    echo "  Reports directory: $REPORTS_DIR"
    echo "  Fail on duplication: $FAIL_ON_DUPLICATION"
    echo ""
fi

# Run the checker
if [[ "$QUIET" == false && "$CI_MODE" == false ]]; then
    echo -e "${CYAN}🔍 Analyzing code for duplications...${NC}"
fi

# Determine output destination
if [[ -n "$OUTPUT" ]]; then
    OUTPUT_REDIRECT="> $OUTPUT"
elif [[ "$CI_MODE" == true ]]; then
    OUTPUT_REDIRECT="> $REPORTS_DIR/duplication-report.json"
else
    OUTPUT_REDIRECT=""
fi

# Run the analysis
set +e  # Don't exit on checker failure
if [[ -n "$OUTPUT_REDIRECT" ]]; then
    eval "python3 \"$CHECKER_SCRIPT\" \"${ARGS[@]}\" $OUTPUT_REDIRECT"
else
    python3 "$CHECKER_SCRIPT" "${ARGS[@]}"
fi
EXIT_CODE=$?
set -e

# Save reports in CI mode
if [[ "$CI_MODE" == true ]]; then
    # Also generate text report for artifacts
    python3 "$CHECKER_SCRIPT" "${ARGS[@]//--json/}" > "$REPORTS_DIR/duplication-report.txt" 2>/dev/null || true
    
    if [[ "$QUIET" == false ]]; then
        echo -e "${BLUE}📊 Reports saved to:${NC}"
        echo "  - Text: $REPORTS_DIR/duplication-report.txt"
        echo "  - JSON: $REPORTS_DIR/duplication-report.json"
    fi
fi

# Show result summary
if [[ "$QUIET" == false && "$CI_MODE" == false ]]; then
    echo ""
    if [[ $EXIT_CODE -eq 0 ]]; then
        echo -e "${GREEN}✅ Analysis completed successfully${NC}"
    else
        echo -e "${YELLOW}⚠️  Analysis completed with issues (exit code: $EXIT_CODE)${NC}"
    fi
fi

# Exit with the same code as the checker
exit $EXIT_CODE
