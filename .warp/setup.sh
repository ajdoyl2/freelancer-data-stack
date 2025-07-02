#!/bin/bash
# Setup script for AI Agent Warp workflows

echo "🤖 Setting up AI Agent Warp workflows..."

# Make agent functions executable
chmod +x .warp/agent_functions.sh

# Add to shell profile for persistent access
SHELL_RC=""
if [[ "$SHELL" == *"zsh"* ]]; then
    SHELL_RC="$HOME/.zshrc"
elif [[ "$SHELL" == *"bash"* ]]; then
    SHELL_RC="$HOME/.bashrc"
fi

if [[ -n "$SHELL_RC" ]]; then
    echo ""
    echo "To make these functions available in all terminals, add this line to your $SHELL_RC:"
    echo ""
    echo "source $(pwd)/.warp/agent_functions.sh"
    echo ""
    echo "Or run this command to add it automatically:"
    echo "echo 'source $(pwd)/.warp/agent_functions.sh' >> $SHELL_RC"
fi

# Source the functions for this session
source .warp/agent_functions.sh

echo ""
echo "✅ Setup complete! Agent functions are now available."
echo ""
echo "Quick start:"
echo "  ads    - Start development session"
echo "  atest  - Run test suite"  
echo "  aenv   - Setup environment"
echo "  apr    - Create PR"
echo ""
echo "For help with any function, just run the command without arguments."
